import math, os, re, sys, time
from datetime import datetime, timedelta
from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs

if sys.version_info[0] != 3 or sys.version_info[1] < 11:
    print("Version Error: Version: %s.%s.%s incompatible please use Python 3.11+" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    sys.exit(0)

try:
    import requests
    from lxml import html
    from pmmutils import logging, util
    from pmmutils.args import PMMArgs
    from pmmutils.exceptions import Failed
    from pmmutils.yaml import YAML
    from tmdbapis import TMDbAPIs, TMDbException, Movie, TVShow
    from tqdm import tqdm
except (ModuleNotFoundError, ImportError):
    print("Requirements Error: Requirements are not installed")
    sys.exit(0)


options = [
    {"arg": "ta", "key": "tmdbapi",      "env": "TMDBAPI",      "type": "str",  "default": None,  "help": "TMDb V3 API Key for connecting to TMDb."},
    {"arg": "td", "key": "trakt_id",     "env": "TRAKT_ID",     "type": "str",  "default": None,  "help": "Trakt Client ID for connecting to Trakt."},
    {"arg": "tt", "key": "trakt_token",  "env": "TRAKT_TOKEN",  "type": "str",  "default": None,  "help": "Trakt Access Token for connecting to Trakt."},
    {"arg": "re", "key": "resume",       "env": "RESUME",       "type": "str",  "default": None,  "help": "Plex Item Title to Resume restoring posters from."},
    {"arg": "ti", "key": "timeout",      "env": "TIMEOUT",      "type": "int",  "default": 600,   "help": "Timeout can be any number greater then 0. (Default: 600)"},
    {"arg": "d",  "key": "dry",          "env": "DRY_RUN",      "type": "bool", "default": False, "help": "Run as a Dry Run without making changes in Plex."},
    {"arg": "tr", "key": "trace",        "env": "TRACE",        "type": "bool", "default": False, "help": "Run with extra trace logs."},
    {"arg": "lr", "key": "log-requests", "env": "LOG_REQUESTS", "type": "bool", "default": False, "help": "Run with every request logged."}
]
headers = {"Accept-Language": "en-US,en;q=0.5", "User-Agent": "Mozilla/5.0 Firefox/102.0"}
base_url = "https://api.trakt.tv"
script_name = "PMM Image Set Update"
base_dir = os.path.dirname(os.path.abspath(__file__))
pmmargs = PMMArgs("meisnate12/PMM-Image-Sets", os.path.dirname(os.path.abspath(__file__)), options, use_nightly=False)
logger = logging.PMMLogger(script_name, "set_update", os.path.join(base_dir, "logs"), is_trace=pmmargs["trace"], log_requests=pmmargs["log-requests"])
logger.secret([pmmargs["tmdbapi"], pmmargs["trakt_id"], pmmargs["trakt_token"]])
requests.Session.send = util.update_send(requests.Session.send, pmmargs["timeout"])
logger.header(pmmargs, sub=True)
logger.separator("Validating Options", space=False, border=False)
now = datetime.now()
six_months = now + timedelta(days=183)

try:
    # Connect to TMDb
    try:
        tmdbapi = TMDbAPIs(pmmargs["tmdbapi"])
    except TMDbException as e:
        raise Failed(e)
    if not pmmargs["trakt_id"] or not pmmargs["trakt_token"]:
        raise Failed("trakt_id and trakt_token are required")

    sets_yaml = YAML(path=os.path.join(base_dir, "sets.yml"), preserve_quotes=True)
    for file_key, set_info in sets_yaml["sets"].items():
        metadata_dir = os.path.join(base_dir, file_key)
        style_dir = os.path.join(metadata_dir, "styles")
        os.makedirs(style_dir, exist_ok=True)
        metadata_path = os.path.join(metadata_dir, "set.yml")
        missing_path = os.path.join(metadata_dir, "missing.yml")
        styles_path = os.path.join(metadata_dir, "styles")
        readme_path = os.path.join(metadata_dir, "readme.md")
        if not os.path.exists(metadata_path):
            logger.error(f"File not Found: {metadata_path}")
            with open(metadata_path, "w") as f:
                f.write("sets:\n")
            continue

        try:
            readme = f"<h1>{set_info['title']}</h1>\n{set_info['description']}\n\n"
            logger.separator(set_info["title"])
            yaml_data = YAML(path=metadata_path, preserve_quotes=True)
            missing_yaml = YAML(path=missing_path, create=True, preserve_quotes=True)
            missing = {}
            if "sections" not in yaml_data:
                raise Failed('File is missing base attribute "sections"')
            if not yaml_data["sections"]:
                raise Failed('File base attribute "sections" is empty')
            for set_key, set_data in yaml_data["sections"].items():
                try:
                    logger.separator(set_key, border=False, space=False)
                    new_data = {}
                    titles = [k for k in set_data if k not in ["builders", "styles", "collections"]]
                    if "styles" not in set_data:
                        raise Failed(f"Set: {set_key} has no styles attribute")
                    if not set_data["styles"]:
                        raise Failed(f"Set: {set_key} styles attribute is blank")

                    if "movies" in set_data and set_data["movies"] and isinstance(set_data["movies"], dict):
                        is_movie = True
                        attr = "movies"
                    elif "shows" in set_data and set_data["shows"] and isinstance(set_data["shows"], dict):
                        is_movie = False
                        attr = "shows"
                    else:
                        raise Failed(f"Set: {set_key} must have either the movies or shows attribute")

                    new_data["title"] = set_data["title"] if "title" in set_data and set_data["title"] else str(set_key).replace("_", " ").title()
                    new_data["builders"] = set_data["builders"] if "builders" in set_data and set_data["builders"] else {}
                    if not new_data["builders"]:
                        logger.error("No Builders Found ignoring Set")
                        continue
                    new_data["styles"] = {"default": set_data["styles"]["default"]}
                    new_data["collections"] = set_data["collections"] if "collections" in set_data and set_data["collections"] else {}
                    existing = set_data[attr] if set_data[attr] and isinstance(set_data[attr], dict) else {}
                    dict_items = {}
                    number_items = {}
                    final = {}
                    for k, v in existing.items():
                        if isinstance(v, dict) and "mapping_id" in v and v["mapping_id"]:
                            if v["mapping_id"] not in dict_items:
                                dict_items[v["mapping_id"]] = []
                            dict_items[v["mapping_id"]].append((k, v))
                        else:
                            number_items[v] = k

                    items = {}
                    for k, v in new_data["builders"].items():
                        if k in ["tmdb_collection", "tmdb_movie", "tmdb_show", "tvdb_show", "imdb_id", "tmdb_list"]:
                            _id_list = []
                            if isinstance(v, list):
                                _id_list = v
                            elif k == "tmdb_list":
                                _id_list = [v]
                            else:
                                _id_list = [i.strip() for i in str(v).split(",")]
                            checked_list = []
                            for _id in _id_list:
                                if k == "imdb_id" and (match := re.search(r"(tt\d+)", str(_id))):
                                    checked_list.append(match.group(1))
                                elif k != "imdb_id" and (match := re.search(r"(\d+)", str(_id))):
                                    checked_list.append(int(match.group(1)))
                                else:
                                    raise Failed(f"Regex Error: Failed to parse ID from {_id}")
                            for _id in checked_list:
                                try:
                                    tmdb_items = []
                                    if k == "tmdb_list":
                                        results = tmdbapi.list(_id)
                                        tmdb_items.extend(results.get_results(results.total_results))
                                    elif k == "tmdb_collection":
                                        col = tmdbapi.collection(_id)
                                        if col.name not in new_data["collections"]:
                                            new_data["collections"][col.name] = []
                                        tmdb_items.extend(col.movies)
                                    elif k == "tmdb_movie":
                                        tmdb_items.append(tmdbapi.movie(_id))
                                    elif k == "tmdb_show":
                                        tmdb_items.append(tmdbapi.tv_show(_id))
                                    elif k == "tvdb_show":
                                        results = tmdbapi.find_by_id(tvdb_id=str(_id))
                                        if not results.tv_results:
                                            raise Failed(f"TVDb Error: No Results were found for tvdb_id: {_id}")
                                        tmdb_items.append(results.tv_results[0])
                                    elif k == "imdb_id":
                                        results = tmdbapi.find_by_id(imdb_id=str(_id))
                                        if is_movie and results.movie_results:
                                            tmdb_items.append(results.movie_results[0])
                                        elif not is_movie and results.tv_results:
                                            tmdb_items.append(results.tv_results[0])
                                        else:
                                            raise Failed(f"IMDb Error: No Results were found for imdb_id: {_id}")
                                    else:
                                        raise TMDbException
                                    for i in tmdb_items:
                                        if is_movie and isinstance(i, Movie) and i.id not in items:
                                            items[i.id] = {"title": i.name, "year": i.release_date.year if i.release_date else ""}
                                        elif not is_movie and isinstance(i, TVShow) and i.tvdb_id and i.tvdb_id not in items:
                                            items[i.tvdb_id] = {"title": i.name, "year": i.first_air_date.year if i.first_air_date else ""}
                                except TMDbException as e:
                                    raise Failed(f"TMDb Error: No {k[5:].capitalize()} found for TMDb ID {_id}: {e}")
                        elif k == "imdb_list":
                            imdb_urls = [str(i) for i in v] if isinstance(v, list) else [str(v)]
                            for imdb_url in imdb_urls:
                                is_search = False
                                is_title_text = False
                                if not imdb_url.startswith("https://www.imdb.com/"):
                                    raise Failed("IMDb Error: url must begin with https://www.imdb.com/")
                                if imdb_url.startswith("https://www.imdb.com/list/ls"):
                                    xpath_total = "//div[@class='desc lister-total-num-results']/text()"
                                    item_count = 100
                                elif imdb_url.startswith("https://www.imdb.com/search/title/"):
                                    xpath_total = "//div[@class='desc']/span/text()"
                                    is_search = True
                                    item_count = 250
                                elif imdb_url.startswith("https://www.imdb.com/search/title-text/"):
                                    xpath_total = "//div[@class='desc']/span/text()"
                                    is_title_text = True
                                    item_count = 50
                                else:
                                    xpath_total = "//div[@class='desc']/text()"
                                    item_count = 50
                                results = html.fromstring(requests.get(imdb_url, headers=headers).content).xpath(xpath_total)
                                total = 0
                                for result in results:
                                    if "title" in result:
                                        try:
                                            total = int(re.findall("(\\d+) title", result.replace(",", ""))[0])
                                            break
                                        except IndexError:
                                            pass
                                if total < 1:
                                    raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")

                                imdb_ids = []
                                parsed_url = urlparse(imdb_url)
                                params = parse_qs(parsed_url.query)
                                imdb_base = parsed_url._replace(query=None).geturl()  # noqa
                                params.pop("start", None)  # noqa
                                params.pop("count", None)  # noqa
                                params.pop("page", None)  # noqa
                                remainder = total % item_count
                                if remainder == 0:
                                    remainder = item_count
                                num_of_pages = math.ceil(int(total) / item_count)
                                for i in tqdm(range(1, num_of_pages + 1), unit=" parsed", desc="| Parsing IMDb Page "):
                                    start_num = (i - 1) * item_count + 1
                                    if is_search:
                                        params["count"] = remainder if i == num_of_pages else item_count  # noqa
                                        params["start"] = start_num  # noqa
                                    elif is_title_text:
                                        params["start"] = start_num  # noqa
                                    else:
                                        params["page"] = i  # noqa
                                    response = html.fromstring(requests.get(imdb_url, headers=headers, params=params).content)
                                    ids_found = response.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst")
                                    if not is_search and i == num_of_pages:
                                        ids_found = ids_found[:remainder]
                                    imdb_ids.extend(ids_found)
                                    time.sleep(2)
                                if not imdb_ids:
                                    raise Failed(f"IMDb Error: No IMDb IDs Found at {imdb_url}")
                                for imdb_id in imdb_ids:
                                    try:
                                        results = tmdbapi.find_by_id(imdb_id=imdb_id)
                                        if is_movie and results.movie_results:
                                            i = results.movie_results[0]
                                            if i.id not in items:
                                                items[i.id] = {"title": i.name, "year": i.release_date.year if i.release_date else ""}
                                        elif results.tv_results:
                                            i = results.tv_results[0]
                                            if i.tvdb_id not in items:
                                                items[i.tvdb_id] = {"title": i.name, "year": i.first_air_date.year if i.first_air_date else ""}
                                        else:
                                            logger.error(f"TMDb Error: No TMDb ID found for IMDb ID {imdb_id}")
                                    except TMDbException:
                                        logger.error(f"TMDb Error: No TMDb ID found for IMDb ID {imdb_id}")
                        elif k == "trakt_list":
                            trakt_urls = [str(i) for i in v] if isinstance(v, list) else [str(v)]
                            for trakt_url in trakt_urls:
                                if not trakt_url.startswith("https://trakt.tv/"):
                                    raise Failed("Trakt Error: url must begin with https://trakt.tv/")
                                url = requests.utils.urlparse(trakt_url).path.replace("/official/", "/")
                                try:
                                    trakt_headers = {
                                        "Content-Type": "application/json",
                                        "Authorization": f"Bearer {pmmargs['trakt_token']}",
                                        "trakt-api-version": "2",
                                        "trakt-api-key": pmmargs["trakt_id"]
                                    }
                                    output_json = []
                                    params = {}
                                    pages = 1
                                    current = 1
                                    while current <= pages:
                                        if pages > 1:
                                            params["page"] = current
                                        response = requests.get(f"{base_url}{url}/items", headers=trakt_headers, params=params)
                                        if pages == 1 and "X-Pagination-Page-Count" in response.headers and not params:
                                            pages = int(response.headers["X-Pagination-Page-Count"])
                                        if response.status_code >= 400:
                                            raise Failed(f"({response.status_code}) {response.reason}")
                                        json_data = response.json()
                                        output_json.extend(json_data)
                                        current += 1
                                    logger.info(output_json)
                                except Failed:
                                    raise Failed(f"Trakt Error: List {trakt_url} not found")
                                if len(output_json) == 0:
                                    raise Failed(f"Trakt Error: List {trakt_url} is empty")

                                id_translation = {"movie": "movie", "show": "show", "season": "show", "episode": "show"}
                                id_types = {
                                    "movie": ("tmdb", "TMDb ID"),
                                    "show": ("tvdb", "TVDb ID"),
                                    "season": ("tvdb", "TVDb ID"),
                                    "episode": ("tvdb", "TVDb ID")
                                }
                                for item in output_json:
                                    if "type" in item and item["type"] in id_translation:
                                        json_data = item[id_translation[item["type"]]]
                                        _type = item["type"]
                                    else:
                                        continue
                                    id_type, id_display = id_types[_type]
                                    _id = int(json_data["ids"][id_type]) if id_type in json_data["ids"] and json_data["ids"][id_type] else json_data["title"]
                                    if (is_movie and id_type == "tmdb") or (not is_movie and id_type == "tvdb") and _id not in items:
                                        items[_id] = {"title": json_data["title"], "year": json_data["year"]}
                        elif k == "mdblist_list":
                            mdblist_urls = [str(i) for i in v] if isinstance(v, list) else [str(v)]
                            for mdblist_url in mdblist_urls:
                                if not mdblist_url.startswith("https://mdblist.com/lists/"):
                                    raise Failed("MDblist Error: url must begin with https://mdblist.com/lists/")
                                params = {}
                                parsed_url = urlparse(mdblist_url)
                                query = parse_qs(parsed_url.query)
                                if "sort" in query:
                                    params["sort"] = query["sort"][0]  # noqa
                                if "sortorder" in query:
                                    params["sortorder"] = query["sortorder"][0]  # noqa
                                url_base = str(parsed_url._replace(query=None).geturl())
                                url_base = url_base if url_base.endswith("/") else f"{url_base}/"
                                url_base = url_base if url_base.endswith("json/") else f"{url_base}json/"
                                try:
                                    response = requests.get(url_base, headers={"User-Agent": "Plex-Meta-Manager"},
                                                            params=params).json()
                                    if (isinstance(response, dict) and "error" in response) or (
                                            isinstance(response, list) and response and "error" in response[0]):
                                        err = response["error"] if isinstance(response, dict) else response[0]["error"]
                                        if err in ["empty", "empty or private list"]:
                                            raise Failed(
                                                f"Mdblist Error: No Items Returned. Lists can take 24 hours to update so try again later.")
                                        raise Failed(f"Mdblist Error: Invalid Response {response}")
                                except JSONDecodeError:
                                    raise Failed(f"Mdblist Error: Invalid Response")
                                for json_data in response:
                                    if is_movie and json_data["mediatype"] == "movie" and json_data["id"] not in items:
                                        items[json_data["id"]] = {"title": json_data["title"], "year": json_data["release_year"]}
                                    elif not is_movie and json_data["mediatype"] == "show" and json_data["tvdbid"] not in items:
                                        items[json_data["tvdbid"]] = {"title": json_data["title"], "year": json_data["release_year"]}

                    if new_data["collections"]:
                        new_cols = {}
                        for k, v in new_data["collections"].items():
                            alts = v if v else []
                            if (new_k := str(k).removesuffix(" Collection")) not in alts and new_k != k:
                                alts.append(YAML.quote(new_k))
                            if (new_k := str(k).removeprefix("The ")) not in alts and new_k != k:
                                alts.append(YAML.quote(new_k))
                            if (new_k := str(k).removeprefix("The ").removesuffix(" Collection")) not in alts and new_k != k:
                                alts.append(YAML.quote(new_k))
                            alts.sort()

                            new_cols[YAML.quote(k)] = [YAML.quote(i) for i in alts]
                        new_data["collections"] = new_cols
                    style_translation = {}
                    for k, v in items.items():
                        title = f"{v['title']} ({v['year']})" if v["year"] else v["title"]
                        if not v["year"] or int(v["year"]) > six_months.year:
                            continue
                        if k in dict_items:
                            used_editions = []
                            for old_title, old_data in dict_items[k]:
                                def _read_old_data(ed_attr):
                                    if ed_attr in old_data and old_data[ed_attr]:
                                        if old_data[ed_attr] in used_editions:
                                            raise Failed(f"Edition Error: Edition {old_data[ed_attr]} already used")
                                        ed_title = f"{title} ({old_data[ed_attr]})"
                                        final[ed_title] = (v["year"], {"mapping_id": k, ed_attr: old_data[ed_attr]})
                                        if old_title != ed_title:
                                            style_translation[old_title] = ed_title
                                        used_editions.append(old_data[ed_attr])
                                        return True
                                    return False
                                if not _read_old_data("edition_filter"):
                                    if not _read_old_data("edition_contains"):
                                        if old_title != title:
                                            style_translation[old_title] = title
                            final[title] = (v["year"], {"mapping_id": k, "blank_edition": True})
                        else:
                            if k in number_items:
                                if number_items[k] != title:
                                    style_translation[number_items[k]] = title
                            final[title] = (v["year"], k)

                    new_data[attr] = {YAML.quote(k): final[k][1] for k in sorted(final.keys(), key=lambda x: final[x][0])}

                    readme += f"<h3>{new_data['title']}</h3>\n<strong>Set Key:</strong> <code>{set_key}</code>\n<h4>Styles:</h4>\n"
                    readme += f'<table class="image-table">\n\t<tr>\n'

                    for style, style_data in set_data["styles"].items():
                        if style == "default":
                            continue
                        default_style_path = f"{set_key}/{style}"
                        if not style_data:
                            style_data = {"pmm": default_style_path}
                        if isinstance(style_data, list):
                            style_data = style_data[0]
                        if "pmm" not in style_data or not style_data["pmm"]:
                            continue
                        style_path_key = styles_path
                        for p in style_data["pmm"].split("/"):
                            style_path_key = os.path.join(style_path_key, p)
                        style_path_key.removesuffix(".yml")
                        style_path = f"{style_path_key}.yml"
                        style_yaml = YAML(path=style_path, create=True, preserve_quotes=True)
                        new_style = {"info": {"style_author": None, "style_image": None, "style_key": style, "style_link": None}, "collections": {}, attr: {}}

                        def init_missing(ms_atr, ms_nm, image_default=False):
                            if set_key not in missing:
                                missing[set_key] = {}
                            if style not in missing[set_key]:
                                missing[set_key][style] = {}
                            if ms_atr not in missing[set_key][style]:
                                missing[set_key][style][ms_atr] = {}
                            if ms_nm not in missing[set_key][style][ms_atr]:
                                missing[set_key][style][ms_atr][ms_nm] = YAML.inline({"tpdb_poster": None, "url_poster": None}) if image_default else None

                        missing_info = None
                        if set_key in missing_yaml and style in missing_yaml[set_key] and "info" in missing_yaml[set_key][style]:
                            missing_info = missing_yaml[set_key][style]["info"]

                        reset_image = False
                        for style_attr, old_style_attr in [("style_author", "set_author"), ("style_image", "asset_image"), ("style_link", "set_link")]:
                            if missing_info and style_attr in missing_info and missing_info[style_attr]:
                                new_style["info"][style_attr] = missing_info[style_attr]
                                reset_image = True
                            elif "info" in style_yaml and style_attr in style_yaml["info"] and style_yaml["info"][style_attr]:
                                new_style["info"][style_attr] = style_yaml["info"][style_attr]
                            elif "info" in style_yaml and old_style_attr in style_yaml["info"] and style_yaml["info"][old_style_attr]:
                                new_style["info"][style_attr] = style_yaml["info"][old_style_attr]
                            else:
                                init_missing("info", style_attr)

                        missing_collections = None
                        if set_key in missing_yaml and style in missing_yaml[set_key] and "collections" in missing_yaml[set_key][style]:
                            missing_collections = missing_yaml[set_key][style]["collections"]

                        def check_images(input_images):
                            output_images = {}
                            if "tpdb_poster" in input_images and input_images["tpdb_poster"]:
                                output_images["tpdb_poster"] = input_images["tpdb_poster"]
                            elif "url_poster" in input_images and input_images["url_poster"]:
                                output_images["url_poster"] = input_images["url_poster"]
                            if "tpdb_background" in input_images and input_images["tpdb_background"]:
                                output_images["tpdb_background"] = input_images["tpdb_background"]
                            elif "url_background" in input_images and input_images["url_background"]:
                                output_images["url_background"] = input_images["url_background"]
                            return output_images

                        for item in new_data["collections"]:
                            original_images = style_yaml["collections"][item] if "collections" in style_yaml and item in style_yaml["collections"] else {}
                            new_images = {}

                            if missing_collections and item in missing_collections and missing_collections[item]:
                                new_images = check_images(missing_collections[item])

                            if "tpdb_poster" not in new_images and "url_poster" not in new_images:
                                new_images = check_images(original_images)

                            if "tpdb_poster" not in new_images and "url_poster" not in new_images:
                                init_missing("collections", item, image_default=True)
                            else:
                                new_style["collections"][item] = YAML.inline(new_images)

                        old_items = {}
                        if attr in style_yaml and style_yaml[attr]:
                            old_items = {style_translation[k] if k in style_translation else k: v for k, v in style_yaml[attr].items()}
                        elif "set" in style_yaml and style_yaml["set"]:
                            old_items = {style_translation[k] if k in style_translation else k: v for k, v in style_yaml["set"].items()}

                        missing_items = None
                        if set_key in missing_yaml and style in missing_yaml[set_key] and attr in missing_yaml[set_key][style]:
                            missing_items = missing_yaml[set_key][style][attr]

                        for item in new_data[attr]:
                            original_images = old_items[item] if item in old_items else {}
                            new_images = {}

                            if missing_items and item in missing_items and missing_items[item]:
                                new_images = check_images(missing_items[item])

                            if "tpdb_poster" not in new_images and "url_poster" not in new_images:
                                new_images = check_images(original_images)

                            if "tpdb_poster" not in new_images and "url_poster" not in new_images:
                                init_missing(attr, item, image_default=True)
                            else:
                                new_style[attr][item] = YAML.inline(new_images)

                        style_yaml.data = new_style
                        style_yaml.save()

                        style_image = None
                        for ext in [".png", ".jpg", ".webp"]:
                            style_image_path = style_path_key + ext
                            if os.path.exists(style_image_path):
                                if reset_image:
                                    os.remove(style_image_path)
                                else:
                                    style_image = f"https://raw.githubusercontent.com/meisnate12/PMM-Image-Sets/master/{file_key}/styles/{set_key}/{style}{ext}"
                                break
                        if not style_image:
                            style_image = style_yaml["info"]["style_image"]
                            if style_image.startswith("https://theposterdb.com/api/assets/"):
                                if match := re.search(r"(\d+)", str(style_image)):
                                    if response := html.fromstring(requests.get(f"https://theposterdb.com/poster/{int(match.group(1))}", headers=headers).content).xpath("//meta[@property='og:image']/@content"):
                                        img_res = requests.get(response[0], headers=headers)
                                        if img_res.status_code >= 400:
                                            logger.error(f"Image Error: Failed to download Image URL: {response[0]}")
                                        elif "Content-Type" not in img_res.headers or img_res.headers["Content-Type"] not in ["image/png", "image/jpeg", "image/webp"]:
                                            logger.error("Image Not PNG, JPG, or WEBP")
                                        else:
                                            if img_res.headers["Content-Type"] == "image/jpeg":
                                                ext = ".jpg"
                                            elif img_res.headers["Content-Type"] == "image/webp":
                                                ext = ".webp"
                                            else:
                                                ext = ".png"
                                            with open(style_path_key + ext, "wb") as handler:
                                                handler.write(img_res.content)
                                            style_image = f"https://raw.githubusercontent.com/meisnate12/PMM-Image-Sets/master/{file_key}/styles/{set_key}/{style}{ext}"

                        readme += f'\t\t<td>\n\t\t\t<img src="{style_image}" height="200"/><br>\n'
                        readme += f'\t\t\t<strong>Style Key:</strong> <code>{style_yaml["info"]["style_key"]}</code><br>\n'
                        readme += f'\t\t\t<strong>Credit:</strong> <a href="{style_yaml["info"]["style_link"]}">{style_yaml["info"]["style_author"]}</a><br>\n\t\t</td>\n'

                        new_data["styles"][style] = None if style_data["pmm"] == default_style_path else style_data
                    readme += f'\t</tr>\n</table>\n\n'

                    yaml_data["sections"][set_key] = new_data

                except Failed as e:
                    logger.error(e)

            with open(readme_path, "w") as f:
                f.write(readme)
            missing_yaml.data = missing
            missing_yaml.save()
            yaml_data.save()
        except Failed as e:
            logger.error(e)
        logger.info()

except Failed as e:
    logger.separator()
    logger.critical(e)
    logger.separator()

logger.error_report()
