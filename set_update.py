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

old_styles = {"style_author": "set_author", "style_image": "asset_image", "style_link": "set_link"}
headers = {"Accept-Language": "en-US,en;q=0.5", "User-Agent": "Mozilla/5.0 Firefox/102.0"}
base_url = "https://api.trakt.tv"
script_name = "PMM Image Set Update"
base_dir = os.path.dirname(os.path.abspath(__file__))
pmmargs = PMMArgs("meisnate12/PMM-Image-Sets", os.path.dirname(os.path.abspath(__file__)), options, config_folder=None, use_nightly=False)
logger = logging.PMMLogger(script_name, "set_update", os.path.join(base_dir, "logs"), is_trace=pmmargs["trace"], log_requests=pmmargs["log-requests"])
logger.secret([pmmargs["tmdbapi"], pmmargs["trakt_id"], pmmargs["trakt_token"]])
requests.Session.send = util.update_send(requests.Session.send, pmmargs["timeout"])
logger.header(pmmargs, sub=True)
logger.separator("Validating Options", space=False, border=False)
today = datetime.now()

def scan_builders(builder_dict, collections=None):
    output_html = "<br><strong>Builders:</strong>\n<br>\n"
    output_objects = []
    output_builders = []
    output_cols = {} if collections is None else collections
    for k, v in builder_dict.items():
        if not v:
            raise Failed(f"Builder Error: {k} cannot be blank")
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
            extra_html = []
            for _id in checked_list:
                try:
                    _tmdb = None
                    if k == "tmdb_list":
                        results = tmdbapi.list(_id)
                        output_objects.extend(results.get_results(results.total_results))
                        _url = f"https://www.themoviedb.org/list/{_id}"
                    elif k == "tmdb_collection":
                        _col = tmdbapi.collection(_id)
                        if _col.name not in output_cols:
                            output_cols[_col.name] = []
                        output_objects.extend(_col.movies)
                        _url = f"https://www.themoviedb.org/collection/{_id}"
                    elif k == "tmdb_movie":
                        output_objects.append(tmdbapi.movie(_id))
                        _url = f"https://www.themoviedb.org/movie/{_id}"
                    elif k == "tmdb_show":
                        output_objects.append(tmdbapi.tv_show(_id))
                        _url = f"https://www.themoviedb.org/tv/{_id}"
                    elif k == "tvdb_show":
                        try:
                            if int(_id) in tvdb_lookup:
                                tmdb_item = tvdb_lookup[int(_id)]
                                if tmdb_item is None:
                                    raise TMDbException
                            else:
                                results = tmdbapi.find_by_id(tvdb_id=str(_id))
                                if not results.tv_results:
                                    raise TMDbException
                                if results.tv_results[0].tvdb_id not in tvdb_lookup:
                                    tvdb_lookup[results.tv_results[0].tvdb_id] = results.tv_results[0]
                                tmdb_item = results.tv_results[0]
                        except TMDbException:
                            tvdb_lookup[int(_id)] = None
                            raise Failed(f"TVDb Error: No Results were found for tvdb_id: {_id}")
                        output_objects.append(tmdb_item)
                        _url = f"https://www.thetvdb.com/dereferrer/series/{_id}"
                        _tmdb = f"https://www.themoviedb.org/tv/{tmdb_item.id}"
                    elif k == "imdb_id":
                        try:
                            results = tmdbapi.find_by_id(imdb_id=str(_id))
                            if results.movie_results:
                                tmdb_item = results.movie_results[0]
                                _tmdb = f"https://www.themoviedb.org/movie/{tmdb_item.id}"
                            elif results.tv_results:
                                tmdb_item = results.tv_results[0]
                                if tmdb_item.tvdb_id not in tvdb_lookup:
                                    tvdb_lookup[tmdb_item.tvdb_id] = tmdb_item
                                _tmdb = f"https://www.themoviedb.org/tv/{tmdb_item.id}"
                            else:
                                raise TMDbException
                            output_objects.append(tmdb_item)
                            _url = f"https://www.imdb.com/title/{_id}"
                        except TMDbException:
                            raise Failed(f"IMDb Error: No Results were found for imdb_id: {_id}")
                    else:
                        raise TMDbException

                    _tmdb_html = f' ({a_link(_tmdb, "TMDb")})' if _tmdb else ""
                    extra_html.append(f"{a_link(_url, _id)}{_tmdb_html}")
                except TMDbException as e:
                    raise Failed(f"TMDb Error: No {k[5:].capitalize()} found for TMDb ID {_id}: {e}")
                output_builders.append((k, _id))
            if extra_html:
                output_html += f'&nbsp;&nbsp;&nbsp;&nbsp;<code>{k}</code>: {", ".join(extra_html)}<br>\n'
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

                output_html += f'&nbsp;&nbsp;&nbsp;&nbsp;<code>{k}</code>: {a_link(imdb_url)}<br>\n'
                output_objects.extend([("IMDb", i) for i in imdb_ids])
                output_builders.append((k, imdb_url))
        elif k == "trakt_list":
            trakt_urls = [str(i) for i in v] if isinstance(v, list) else [str(v)]
            for trakt_url in trakt_urls:
                if not trakt_url.startswith("https://trakt.tv/"):
                    raise Failed("Trakt Error: url must begin with https://trakt.tv/")
                url = requests.utils.urlparse(trakt_url).path.replace("/official/", "/")  # noqa
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
                except Failed:
                    raise Failed(f"Trakt Error: List {trakt_url} not found")
                if len(output_json) == 0:
                    raise Failed(f"Trakt Error: List {trakt_url} is empty")

                output_html += f'&nbsp;&nbsp;&nbsp;&nbsp;<code>{k}</code>: {a_link(trakt_url)}<br>\n'

                id_translation = {"movie": "movie", "show": "show", "season": "show", "episode": "show"}
                id_types = {
                    "movie": ("tmdb", "TMDb ID"),
                    "show": ("tvdb", "TVDb ID"),
                    "season": ("tvdb", "TVDb ID"),
                    "episode": ("tvdb", "TVDb ID")
                }
                for output_json_item in output_json:
                    if "type" in output_json_item and output_json_item["type"] in id_translation:
                        json_data = output_json_item[id_translation[output_json_item["type"]]]
                        _type = output_json_item["type"]
                    else:
                        continue
                    id_type, id_display = id_types[_type]
                    if id_type not in json_data["ids"] or not json_data["ids"][id_type]:
                        continue
                    output_objects.append((id_type, int(json_data["ids"][id_type])))
                output_builders.append((k, trakt_url))
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

                output_html += f'&nbsp;&nbsp;&nbsp;&nbsp;<code>{k}</code>: {a_link(mdblist_url)}<br>\n'
                for json_data in response:
                    if json_data["mediatype"] == "movie":
                        output_objects.append(("tmdb", json_data["id"]))
                    elif json_data["mediatype"] == "show":
                        output_objects.append(("tvdb", json_data["tvdbid"]))
                output_builders.append((k, mdblist_url))

    output_html += "</ul>\n"

    _movies = {}
    _shows = {}
    for tmdb_object in output_objects:
        if isinstance(tmdb_object, tuple):
            _id_type, _id = tmdb_object
            try:
                if _id_type == "imdb":
                    find_results = tmdbapi.find_by_id(imdb_id=_id)
                    if find_results.movie_results:
                        tmdb_object = find_results.movie_results[0]
                    elif find_results.tv_results:
                        tmdb_object = find_results.tv_results[0]
                    else:
                        raise TMDbException
                elif _id_type == "tvdb":
                    if int(_id) in tvdb_lookup:
                        tmdb_object = tvdb_lookup[int(_id)]
                        if tmdb_object is None:
                            raise TMDbException
                    else:
                        results = tmdbapi.find_by_id(tvdb_id=str(_id))
                        if not results.tv_results:
                            raise TMDbException
                        if results.tv_results[0].tvdb_id not in tvdb_lookup:
                            tvdb_lookup[results.tv_results[0].tvdb_id] = results.tv_results[0]
                        tmdb_object = results.tv_results[0]
                elif _id_type == "tmdb":
                    tmdb_object = tmdbapi.movie(_id)
            except TMDbException:
                if _id_type == "tvdb":
                    tvdb_lookup[int(_id)] = None
                logger.error(f"TMDb Error: No TMDb Item found for {_id_type.upper()[:-1]}b ID {_id}")
                continue
        if isinstance(tmdb_object, Movie):
            if tmdb_object.id not in _movies and tmdb_object.release_date:
                _movies[tmdb_object.id] = (tmdb_object.name, tmdb_object.release_date)
        elif isinstance(tmdb_object, TVShow):
            if tmdb_object.tvdb_id not in _shows and tmdb_object.first_air_date:
                _shows[tmdb_object.tvdb_id] = (tmdb_object.name, tmdb_object.first_air_date)

    return _movies, _shows, output_cols, output_html, output_builders

try:
    # Connect to TMDb
    try:
        tmdbapi = TMDbAPIs(pmmargs["tmdbapi"])
    except TMDbException as e:
        raise Failed(e)
    if not pmmargs["trakt_id"] or not pmmargs["trakt_token"]:
        raise Failed("trakt_id and trakt_token are required")
    tvdb_lookup = {}
    sets_yaml = YAML(path=os.path.join(base_dir, "sets.yml"), preserve_quotes=True)
    new_sets = {}
    set_lookup = {}
    for file_key, set_info in sets_yaml["sets"].items():
        set_title = set_info["title"] if "title" in set_info else ""
        set_description = set_info["description"] if "description" in set_info else ""
        file_dir = os.path.join(base_dir, file_key)
        if "set_key" in set_info and set_info["set_key"]:
            if str(set_info["set_key"]) in sets_yaml["sets"]:
                logger.error(f"Set Key Error: Set Key: {set_info['set_key']} already exists")
                new_sets[file_key] = set_info
                continue
            set_key = str(set_info["set_key"])
            metadata_dir = os.path.join(base_dir, set_key)
            if not os.path.exists(metadata_dir) and os.path.exists(file_dir):
                os.rename(file_dir, metadata_dir)
        else:
            set_key = file_key
            metadata_dir = os.path.join(base_dir, set_key)
        new_sets[str(set_key)] = {"title": set_title, "description": set_description}
        style_dir = os.path.join(metadata_dir, "styles")
        metadata_path = os.path.join(metadata_dir, "set.yml")
        missing_path = os.path.join(metadata_dir, "missing.yml")
        readme_path = os.path.join(metadata_dir, "readme.md")
        if not os.path.exists(metadata_path):
            logger.warning(f"Initializing Image Set File: {metadata_path}")
            os.makedirs(os.path.dirname(metadata_path))
            set_yaml = YAML(metadata_path, create=True, preserve_quotes=True)
            set_yaml["sections"] = None

            if "builders" in set_info and set_info["builders"]:
                builder_movies, builder_shows, _, _, builder_list = scan_builders(set_info["builders"])
                new_section = {}
                collection_id_list = []
                for builder_type, builder_data in builder_list:
                    if builder_type == "tmdb_collection":
                        if builder_data not in collection_id_list:
                            collection_id_list.append(builder_data)
                    #elif builder_type == "tmdb_movie":

                    #elif builder_type == "tmdb_show":
                    #elif builder_type == "tvdb_show":
                    #elif builder_type == "imdb_id":
                    #elif builder_type == "tmdb_list":
                    #elif builder_type == "imdb_list":
                    #elif builder_type == "trakt_list":
                    #elif builder_type == "mdblist_list":

            set_yaml.save()
            continue

        try:

            def create_local_link(input_text):
                return f'#{str(input_text).lower().replace(" ", "-")}'

            def heading(heading_str, level):
                heading_link = create_local_link(heading_str)
                return f'<h{level} id="{heading_link[1:]}">{heading_str}<a class="headerlink" href="{heading_link}" title="Permalink to this heading">¶</a></h{level}>\n'

            def a_link(input_url, input_text=None, local_link=False):
                if input_text is None:
                    input_text = input_url
                extra_a = '' if local_link else ' target="_blank" rel="noopener noreferrer"'
                if local_link is False:
                    _link = input_url
                elif local_link is True:
                    _link = create_local_link(input_url)
                else:
                    _link = create_local_link(local_link)

                return f'<a href="{_link}"{extra_a}>{input_text}</a>'

            readme = heading("Sections", "2")
            index_table = f'{heading(set_info["title"], "1")}{set_info["description"]}\n\n<ul class="images-index-table">\n'
            logger.separator(set_info["title"])
            yaml_data = YAML(path=metadata_path, preserve_quotes=True)
            missing_yaml = YAML(path=missing_path, create=True, preserve_quotes=True)
            missing = {}
            if "sections" not in yaml_data:
                raise Failed('File is missing base attribute "sections"')
            if not yaml_data["sections"]:
                raise Failed('File base attribute "sections" is empty')
            sections = {}
            for section_key, section_data in yaml_data["sections"].items():
                section_key = str(section_key).lower().replace(" ", "_")
                logger.separator(section_key, border=False, space=False)
                if not section_data:
                    sections[section_key] = {"title": str(section_key).replace("_", " ").title(), "builders": None, "styles": None}
                    logger.warning(f"Initializing Section: {section_key}")
                    continue
                try:
                    new_data = {
                        "title": section_data["title"] if "title" in section_data and section_data["title"] else str(section_key).replace("_", " ").title(),
                        "builders": section_data["builders"] if "builders" in section_data and section_data["builders"] else {},
                        "styles": {k: v for k, v in section_data["styles"].items() if k != "default"} if "styles" in section_data and section_data["styles"] else {}
                    }
                    if not new_data["builders"]:
                        raise Failed(f"No Builders Found ignoring section: {section_key}")
                    new_collections = section_data["collections"] if "collections" in section_data and section_data["collections"] else {}
                    default_image_title = section_data["default_image"] if "default_image" in section_data and section_data["default_image"] else None
                    if default_image_title:
                        new_data["default_image"] = default_image_title
                    existing_movies = section_data["movies"] if "movies" in section_data and section_data["movies"] and isinstance(section_data["movies"], dict) else {}
                    existing_shows = section_data["shows"] if "shows" in section_data and section_data["shows"] and isinstance(section_data["shows"], dict) else {}

                    movie_editions = {}
                    existing_movie_lookup = {}
                    for k, v in existing_movies.items():
                        if isinstance(v, dict) and "mapping_id" in v and v["mapping_id"]:
                            if v["mapping_id"] not in movie_editions:
                                movie_editions[v["mapping_id"]] = []
                            movie_editions[v["mapping_id"]].append((k, v))
                        else:
                            existing_movie_lookup[v] = k

                    show_editions = {}
                    existing_show_lookup = {}
                    for k, v in existing_shows.items():
                        if isinstance(v, dict) and "mapping_id" in v and v["mapping_id"]:
                            if v["mapping_id"] not in show_editions:
                                show_editions[v["mapping_id"]] = []
                            show_editions[v["mapping_id"]].append((k, v))
                        else:
                            existing_show_lookup[v] = k

                    builder_movies, builder_shows, new_collections, builder_html, _ = scan_builders(new_data["builders"], collections=new_collections)

                    if new_collections:
                        new_cols = {}
                        used_cols = []
                        for k, v in new_collections.items():
                            if k in used_cols:
                                continue
                            alts = v if v else []
                            for a in alts:
                                if a not in used_cols:
                                    used_cols.append(a)
                            used_cols.append(k)
                            if (new_k := str(k).removesuffix(" Collection")) not in used_cols and new_k != k:
                                alts.append(YAML.quote(new_k))
                                used_cols.append(new_k)
                            if (new_k := str(k).removeprefix("The ")) not in used_cols and new_k != k:
                                alts.append(YAML.quote(new_k))
                                used_cols.append(new_k)
                            if (new_k := str(k).removeprefix("The ").removesuffix(" Collection")) not in used_cols and new_k != k:
                                alts.append(YAML.quote(new_k))
                                used_cols.append(new_k)
                            alts.sort()
                            new_cols[YAML.quote(k)] = [YAML.quote(i) for i in alts]
                        new_collections = new_cols

                    if new_collections:
                        new_data["collections"] = new_collections

                    builder_items = []
                    style_translation = {}
                    for attr in ["movies", "shows"]:
                        _items = builder_movies if attr == "movies" else builder_shows
                        _editions = movie_editions if attr == "movies" else show_editions
                        _non_editions = existing_movie_lookup if attr == "movies" else existing_show_lookup
                        _final = {}
                        for _item_id, (title, release) in _items.items():
                            if release > today:
                                continue
                            _year = release.year
                            title = f"{title} ({_year})"
                            builder_items.append(title)
                            if _item_id in _editions:
                                used_editions = []
                                for old_title, old_data in _editions[_item_id]:
                                    def _read_old_data(ed_attr):
                                        if ed_attr in old_data and old_data[ed_attr]:
                                            if old_data[ed_attr] in used_editions:
                                                raise Failed(f"Edition Error: Edition {old_data[ed_attr]} already used")
                                            ed_title = f"{title} ({old_data[ed_attr]})"
                                            _final[ed_title] = (_year, {"mapping_id": _item_id, ed_attr: old_data[ed_attr]}) # noqa
                                            if old_title != ed_title:
                                                style_translation[old_title] = ed_title
                                            used_editions.append(old_data[ed_attr])
                                            return True
                                        return False
                                    if not _read_old_data("edition_filter"):
                                        if not _read_old_data("edition_contains"):
                                            if old_title != title:
                                                style_translation[old_title] = title
                                _final[title] = (_year, {"mapping_id": _item_id, "blank_edition": True})
                            else:
                                if _item_id in _non_editions:
                                    if _non_editions[_item_id] != title:
                                        style_translation[_non_editions[_item_id]] = title
                                _final[title] = (_year, _item_id)
                        if _final:
                            new_data[attr] = {YAML.quote(_k): _final[_k][1] for _k in sorted(_final.keys(), key=lambda x: _final[x][0])}

                    os.makedirs(style_dir, exist_ok=True)
                    index_line = f'<div class="images-inline-link">{new_data["title"]}<br><code>{section_key}</code></div>'
                    index_table += f'  <li>{a_link(index_line, local_link=new_data["title"])}</li>\n'
                    readme += f'{heading(new_data["title"], "3")}<strong>Section Key:</strong> <code>{section_key}</code>\n{builder_html}'
                    readme += f'<button class="image-accordion">Styles</button>\n<div class="image-panel">\n'
                    readme += f'  <table class="image-table">\n    <tr>\n'
                    for style, style_data in new_data["styles"].items():
                        if style == "default":
                            continue
                        default_style_path = f"{section_key}/{style}"
                        style_link = None
                        if style_data and isinstance(style_data, (str, int)):
                            style_link = style_data
                            style_data = None
                        if not style_data:
                            style_data = {"pmm": default_style_path}
                        if isinstance(style_data, list):
                            style_data = style_data[0]
                        if "pmm" not in style_data or not style_data["pmm"]:
                            continue
                        style_path_key = style_dir
                        for p in style_data["pmm"].split("/"):
                            style_path_key = os.path.join(style_path_key, p)
                        style_path_key.removesuffix(".yml")
                        style_path = f"{style_path_key}.yml"
                        os.makedirs(os.path.dirname(style_path), exist_ok=True)
                        style_yaml = YAML(path=style_path, create=True, preserve_quotes=True)
                        new_style = {"info": {"style_author": None, "style_image": None, "style_key": style, "style_link": None}}

                        def init_missing(ms_atr, ms_nm, pos=None, bkg=None, init_s=None, init_e=None):
                            if pos or bkg:
                                temp_dict = {}
                                if pos:
                                    temp_dict["tpdb_poster"] = None
                                    temp_dict["url_poster"] = None
                                if bkg:
                                    temp_dict["tpdb_background"] = None
                                    temp_dict["url_background"] = None
                                image_dict = YAML.inline(temp_dict)
                            else:
                                image_dict = None
                            if section_key not in missing:
                                missing[section_key] = {}
                            if style not in missing[section_key]:
                                missing[section_key][style] = {}
                            if ms_atr not in missing[section_key][style]:
                                missing[section_key][style][ms_atr] = {}
                            if ms_nm not in missing[section_key][style][ms_atr]:
                                missing[section_key][style][ms_atr][ms_nm] = image_dict if init_s is None else {}
                            if init_s is not None:
                                if "seasons" not in missing[section_key][style][ms_atr][ms_nm]:
                                    missing[section_key][style][ms_atr][ms_nm]["seasons"] = {}
                                if init_s not in missing[section_key][style][ms_atr][ms_nm]["seasons"]:
                                    missing[section_key][style][ms_atr][ms_nm]["seasons"][init_s] = image_dict if init_e is None else {}
                                if init_e is not None:
                                    if "episodes" not in missing[section_key][style][ms_atr][ms_nm]["seasons"][init_s]:
                                        missing[section_key][style][ms_atr][ms_nm]["seasons"][init_s]["episodes"] = {}
                                    if init_e not in missing[section_key][style][ms_atr][ms_nm]["seasons"][init_s]["episodes"]:
                                        missing[section_key][style][ms_atr][ms_nm]["seasons"][init_s]["episodes"][init_e] = image_dict

                        missing_info = None
                        if section_key in missing_yaml and style in missing_yaml[section_key] and "info" in missing_yaml[section_key][style]:
                            missing_info = missing_yaml[section_key][style]["info"]

                        reset_image = False
                        for style_attr in ["style_author", "style_image", "style_link", "complete", "track_seasons", "track_episodes", "track_backgrounds", "track_editions"]:
                            if missing_info and style_attr in missing_info and missing_info[style_attr] is not None:
                                new_style["info"][style_attr] = missing_info[style_attr]
                                if style_attr == "style_image":
                                    reset_image = True
                            elif "info" in style_yaml and style_attr in style_yaml["info"] and style_yaml["info"][style_attr] is not None:
                                new_style["info"][style_attr] = style_yaml["info"][style_attr]
                            elif style_attr in old_styles:
                                if "info" in style_yaml and old_styles[style_attr] in style_yaml["info"] and style_yaml["info"][old_styles[style_attr]] is not None:
                                    new_style["info"][style_attr] = style_yaml["info"][old_styles[style_attr]]
                                else:
                                    init_missing("info", style_attr)
                        is_complete = True if "complete" in new_style["info"] and new_style["info"]["complete"] else False
                        track_seasons = True if "track_seasons" in new_style["info"] and new_style["info"]["track_seasons"] else False
                        track_episodes = True if "track_episodes" in new_style["info"] and new_style["info"]["track_episodes"] else False
                        track_backgrounds = True if "track_backgrounds" in new_style["info"] and new_style["info"]["track_backgrounds"] else False
                        track_editions = True if "track_editions" in new_style["info"] and new_style["info"]["track_editions"] else False

                        if style_link and not new_style["info"]["style_link"]:
                            new_style["info"]["style_link"] = style_link

                        if new_style["info"]["style_link"]:
                            try:
                                new_style["info"]["style_link"] = f'https://theposterdb.com/set/{int(new_style["info"]["style_link"])}'
                            except ValueError:
                                pass

                        if new_style["info"]["style_image"]:
                            try:
                                new_style["info"]["style_image"] = f'https://theposterdb.com/api/assets/{int(new_style["info"]["style_image"])}'
                            except ValueError:
                                pass

                        missing_collections = None
                        if section_key in missing_yaml and style in missing_yaml[section_key] and "collections" in missing_yaml[section_key][style]:
                            missing_collections = missing_yaml[section_key][style]["collections"]

                        def check_images(input_images, current_images):
                            output_images = {}

                            if "tpdb_poster" in current_images and current_images["tpdb_poster"]:
                                output_images["tpdb_poster"] = current_images["tpdb_poster"]
                            elif "url_poster" in current_images and current_images["url_poster"]:
                                output_images["url_poster"] = current_images["url_poster"]
                            elif "tpdb_poster" in input_images and input_images["tpdb_poster"]:
                                output_images["tpdb_poster"] = input_images["tpdb_poster"]
                            elif "url_poster" in input_images and input_images["url_poster"]:
                                output_images["url_poster"] = input_images["url_poster"]

                            if "tpdb_background" in current_images and current_images["tpdb_background"]:
                                output_images["tpdb_background"] = current_images["tpdb_background"]
                            elif "url_background" in current_images and current_images["url_background"]:
                                output_images["url_background"] = current_images["url_background"]
                            elif "tpdb_background" in input_images and input_images["tpdb_background"]:
                                output_images["tpdb_background"] = input_images["tpdb_background"]
                            elif "url_background" in input_images and input_images["url_background"]:
                                output_images["url_background"] = input_images["url_background"]
                            return output_images

                        old_movies = {}
                        if "movies" in style_yaml and style_yaml["movies"]:
                            old_movies = {style_translation[k] if k in style_translation else k: v for k, v in style_yaml["movies"].items()}

                        old_shows = {}
                        if "shows" in style_yaml and style_yaml["shows"]:
                            old_shows = {style_translation[k] if k in style_translation else k: v for k, v in style_yaml["shows"].items()}

                        if "set" in style_yaml and style_yaml["set"]:
                            _old = {style_translation[k] if k in style_translation else k: v for k, v in style_yaml["set"].items()}
                            if "show" in set_key:
                                old_shows = _old
                            elif "movie" in set_key:
                                old_movies = _old

                        missing_movies = None
                        if section_key in missing_yaml and style in missing_yaml[section_key] and "movies" in missing_yaml[section_key][style]:
                            missing_movies = missing_yaml[section_key][style]["movies"]

                        missing_shows = None
                        if section_key in missing_yaml and style in missing_yaml[section_key] and "shows" in missing_yaml[section_key][style]:
                            missing_shows = missing_yaml[section_key][style]["shows"]

                        def lookup():
                            if new_style["info"]["style_link"] in set_lookup:
                                return set_lookup[new_style["info"]["style_link"]]
                            l_out = {}
                            l_res = html.fromstring(requests.get(new_style["info"]["style_link"], headers=headers).content)
                            l_items = l_res.xpath("//div[@class = 'overlay rounded-poster']")
                            l_author = l_res.xpath("//p[@id='set-title']/span/a/text()")[0]
                            for li in l_items:
                                l_title = li.xpath("div/div/p[contains(@class, 'text-break')]/text()")[0]
                                if l_title not in l_out:
                                    l_out[l_title] = int(li.xpath('@data-poster-id')[0])
                            time.sleep(5)
                            set_lookup[new_style["info"]["style_link"]] = (l_author, l_out)
                            return l_author, l_out

                        current_item_count = len(builder_items)
                        old_count = len([m for m in old_movies if m in builder_items]) + len([m for m in old_shows if m in builder_items])

                        tp_link = new_style["info"]["style_link"] if new_style["info"]["style_link"] and new_style["info"]["style_link"].startswith("https://theposterdb.com/set/") else None

                        posters = None
                        if tp_link and (old_count == 0 or (is_complete and current_item_count != old_count)):
                            author, posters = lookup()
                            if not new_style["info"]["style_author"]:
                                new_style["info"]["style_author"] = str(author)

                        for col in new_collections:
                            original_images = style_yaml["collections"][col] if "collections" in style_yaml and col in style_yaml["collections"] else {}
                            new_col = {}

                            if posters and col in posters:
                                new_col["tpdb_poster"] = posters[col]

                            if missing_collections and col in missing_collections and missing_collections[col]:
                                new_col = check_images(missing_collections[col], new_col)

                            new_col = check_images(original_images, new_col)

                            no_p = True if "tpdb_poster" not in new_col and "url_poster" not in new_col else False
                            no_b = True if "tpdb_background" not in new_col and "url_background" not in new_col else False
                            if no_p or (track_backgrounds and no_b):
                                init_missing("collections", col, pos=no_p, bkg=no_b if track_backgrounds else None)

                            if new_col:
                                if "collections" not in new_style:
                                    new_style["collections"] = {}
                                new_style["collections"][col] = YAML.inline(new_col)

                        for attr, old_items, missing_items in [("movies", old_movies, missing_movies), ("shows", old_shows, missing_shows)]:
                            if attr not in new_data:
                                continue
                            for item, item_data in new_data[attr].items():
                                item_id = item_data["mapping_id"] if isinstance(item_data, dict) else item_data
                                _original = old_items[item] if item in old_items else {}
                                new_images = {}
                                if posters and item in posters:
                                    new_images["tpdb_poster"] = posters[item]

                                missing_item = {}
                                if missing_items and item in missing_items and missing_items[item]:
                                    missing_item = missing_items[item]
                                    new_images = check_images(missing_item, new_images)

                                new_images = check_images(_original, new_images)

                                _no_p = True if "tpdb_poster" not in new_images and "url_poster" not in new_images else False
                                _no_b = True if "tpdb_background" not in new_images and "url_background" not in new_images else False
                                if _no_p or (track_backgrounds and _no_b):
                                    if track_editions or item in builder_items:
                                        init_missing(attr, item, pos=_no_p, bkg=_no_b if track_backgrounds else None)

                                if attr == "shows":
                                    og_seasons = _original["seasons"] if "seasons" in _original and _original["seasons"] else {}
                                    try:
                                        if int(item_id) in tvdb_lookup:
                                            tmdb_obj = tvdb_lookup[int(item_id)]
                                            if tmdb_obj is None:
                                                continue
                                        else:
                                            _results = tmdbapi.find_by_id(tvdb_id=str(item_id))
                                            if not _results.tv_results:
                                                tvdb_lookup[int(item_id)] = None
                                                raise Failed(f"TVDb Error: No Results were found for tvdb_id: {item_id}")
                                            if _results.tv_results[0].tvdb_id not in tvdb_lookup:
                                                tvdb_lookup[_results.tv_results[0].tvdb_id] = _results.tv_results[0]
                                            tmdb_obj = _results.tv_results[0]
                                    except TMDbException:
                                        tvdb_lookup[int(item_id)] = None
                                        logger.error(f"TVDb Error: No Results were found for tvdb_id: {item_id}")
                                        continue
                                    missing_seasons = {}
                                    if "seasons" in missing_item and missing_item["seasons"]:
                                        missing_seasons = missing_item["seasons"]

                                    if track_seasons or track_episodes or og_seasons:
                                        seasons = {0: None}
                                        for s in tmdb_obj.seasons:
                                            seasons[s.season_number] = s
                                        og_season_len = len([True for og in og_seasons if int(og) > 0])
                                        if tp_link and posters is None and (len(seasons) - 1 != og_season_len or (og_season_len == 0 and track_seasons)):
                                            _, posters = lookup()

                                        for s_num, season in seasons.items():
                                            if s_num in og_seasons and og_seasons[s_num]:
                                                original_season_images = og_seasons[s_num]
                                            elif str(s_num) in og_seasons and og_seasons[str(s_num)]:
                                                original_season_images = og_seasons[str(s_num)]
                                            else:
                                                original_season_images = {}
                                            new_season_images = {}
                                            if posters:
                                                if s_num > 0 and f"{item} - Season {s_num}" in posters:
                                                    new_season_images["tpdb_poster"] = posters[f"{item} - Season {s_num}"]
                                                elif s_num == 0 and f"{item} - Specials" in posters:
                                                    new_season_images["tpdb_poster"] = posters[f"{item} - Specials"]

                                            if s_num in missing_seasons and missing_seasons[s_num]:
                                                new_season_images = check_images(missing_seasons[s_num], new_season_images)
                                            elif str(s_num) in missing_seasons and missing_seasons[str(s_num)]:
                                                new_season_images = check_images(missing_seasons[str(s_num)], new_season_images)

                                            new_season_images = check_images(original_season_images, new_season_images)

                                            if s_num > 0:
                                                _no_p = True if "tpdb_poster" not in new_season_images and "url_poster" not in new_season_images else False
                                                _no_b = True if "tpdb_background" not in new_season_images and "url_background" not in new_season_images else False
                                                if _no_p or (track_backgrounds and _no_b):
                                                    init_missing(attr, item, pos=_no_p, bkg=_no_b if track_backgrounds else None, init_s=s_num)

                                            missing_episodes = {}
                                            if "episodes" in missing_seasons and missing_seasons["episodes"]:
                                                missing_episodes = missing_seasons["episodes"]
                                            og_episodes = {}
                                            if "episodes" in original_season_images and original_season_images["episodes"]:
                                                og_episodes = original_season_images["episodes"]

                                            if track_episodes or og_episodes:
                                                if s_num > 0:
                                                    for episode in season.episodes:
                                                        e_num = episode.episode_number
                                                        if e_num in og_episodes and og_episodes[e_num]:
                                                            original_episode_images = og_episodes[e_num]
                                                        elif str(e_num) in og_episodes and og_episodes[str(e_num)]:
                                                            original_episode_images = og_episodes[str(e_num)]
                                                        else:
                                                            original_episode_images = {}

                                                        new_episode_images = {}
                                                        if e_num in missing_episodes and missing_episodes[e_num]:
                                                            new_episode_images = check_images(missing_episodes[e_num], new_episode_images)
                                                        elif str(e_num) in missing_episodes and missing_episodes[str(e_num)]:
                                                            new_episode_images = check_images(missing_episodes[str(e_num)], new_episode_images)

                                                        new_episode_images = check_images(original_episode_images, new_episode_images)

                                                        _no_p = True if "tpdb_poster" not in new_episode_images and "url_poster" not in new_episode_images else False
                                                        _no_b = True if "tpdb_background" not in new_episode_images and "url_background" not in new_episode_images else False
                                                        if _no_p or (track_backgrounds and _no_b):
                                                            init_missing(attr, item, pos=_no_p, bkg=_no_b if track_backgrounds else None, init_s=s_num, init_e=e_num)

                                                        if new_episode_images:
                                                            if "episodes" not in new_season_images:
                                                                new_season_images["episodes"] = {}
                                                            new_season_images["episodes"][e_num] = YAML.inline(new_episode_images)
                                                elif og_episodes:
                                                    for e_num, ep_data in og_episodes.items():
                                                        if new_episode_images := check_images(ep_data, {}):
                                                            if "episodes" not in new_season_images:
                                                                new_season_images["episodes"] = {}
                                                            new_season_images["episodes"][int(e_num)] = YAML.inline(new_episode_images)

                                            if new_season_images:
                                                if "seasons" not in new_images:
                                                    new_images["seasons"] = {}
                                                new_images["seasons"][s_num] = new_season_images if "episodes" in new_season_images else YAML.inline(new_season_images)

                                if new_images:
                                    if item == default_image_title and not new_style["info"]["style_image"]:
                                        if "tpdb_poster" in new_images:
                                            new_style["info"]["style_image"] = f"https://theposterdb.com/api/assets/{new_images['tpdb_poster']}"
                                        elif "url_poster" in new_images:
                                            new_style["info"]["style_image"] = new_images["url_poster"]
                                    if attr not in new_style:
                                        new_style[attr] = {}
                                    new_style[attr][item] = new_images if "seasons" in new_images else YAML.inline(new_images)

                        new_item_count = 0
                        if "movies" in new_style:
                            new_item_count += len(new_style["movies"])
                        if "shows" in new_style:
                            new_item_count += len(new_style["shows"])

                        if new_item_count == current_item_count:
                            new_style["info"]["complete"] = True

                        style_image = None
                        for ext in [".png", ".jpg", ".webp"]:
                            style_image_path = style_path_key + ext
                            if os.path.exists(style_image_path):
                                if reset_image:
                                    os.remove(style_image_path)
                                else:
                                    style_image = f"https://raw.githubusercontent.com/meisnate12/PMM-Image-Sets/master/{file_key}/styles/{section_key}/{style}{ext}"
                                break
                        if not style_image and new_style["info"]["style_image"]:
                            style_image = new_style["info"]["style_image"]
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
                                            style_image = f"https://raw.githubusercontent.com/meisnate12/PMM-Image-Sets/master/{file_key}/styles/{section_key}/{style}{ext}"

                        img_link = a_link(new_style["info"]["style_link"], f'<img src="{style_image}" height="200"/>')
                        readme += f'      <td>\n        <div>\n          {img_link}<br>\n'
                        readme += f'          <strong>Style Key:</strong> <code>{new_style["info"]["style_key"]}</code><br>\n'
                        readme += f'          <strong>Credit:</strong> {a_link(new_style["info"]["style_link"], new_style["info"]["style_author"])}<br>\n        </div>\n      </td>\n'

                        if new_style["info"]["style_image"] and str(new_style["info"]["style_image"]).startswith("https://theposterdb.com/api/assets/"):
                            try:
                                new_style["info"]["style_image"] = int(str(new_style["info"]["style_image"]).removeprefix("https://theposterdb.com/api/assets/"))
                            except ValueError:
                                pass

                        if new_style["info"]["style_link"] and str(new_style["info"]["style_link"]).startswith("https://theposterdb.com/set/"):
                            try:
                                new_style["info"]["style_link"] = int(str(new_style["info"]["style_link"]).removeprefix("https://theposterdb.com/set/"))
                            except ValueError:
                                pass

                        style_yaml.data = new_style
                        style_yaml.save()

                        new_data["styles"][style] = None if style_data["pmm"] == default_style_path else style_data
                    readme += "    </tr>\n  </table>\n</div>\n\n"

                    if not new_data["styles"]:
                        new_data["styles"] = None

                    sections[section_key] = new_data

                except Failed as e:
                    logger.error(e)
                    sections[section_key] = section_data

            index_table += "</ul>\n\n"
            with open(readme_path, "w") as f:
                f.write(index_table + readme)
            missing_yaml.data = missing
            missing_yaml.save()

            def sort_title(x):
                _title = sections[x]["title"] if "title" in sections[x] else str(x).replace("_", " ").title()
                for prefix in ["The", "A", "An"]:
                    _title = _title.removeprefix(f"{prefix} ")
                return _title

            sorted_sections = sorted(sections.keys(), key=lambda x: sort_title(x))
            yaml_data.data = {"sections": {k: sections[k] for k in sorted_sections}}
            yaml_data.save()
        except Failed as e:
            logger.error(e)
        logger.info()

    sets_yaml.data = {"sets": new_sets}
    sets_yaml.save()
except Failed as e:
    logger.separator()
    logger.critical(e)
    logger.separator()

logger.error_report()
