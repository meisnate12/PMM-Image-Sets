# PMM Image Sets

PMM Image Sets is a set of pre-defined files to work in conjunction with [Plex Meta Manager](https://github.com/meisnate12/Plex-Meta-Manager)

Image Sets allow you to easily apply our curated set of Posters and Title Cards to your libraries, skipping the need to manually download and apply individual posters to your media.

## Usage

Image Sets can be called out in your Plex Meta Manager config file as follows:

```yaml
libraries:
  Movies:                               # must match a library in your Plex server
    image_sets:
      - pmm: movies                     # name of the image set
        template_variables:
          use_all: true                 # this is false by default, meaning you need to manually specify which sets you want
  TV Shows:                             # must match a library in your Plex server
    image_sets:
      - pmm: shows                      # name of the image set
        template_variables:
          use_starwars: true            # will only use the images that are part of the `starwars` set, no other sets will be used.
```

## Contributing to the Image Sets

This repo and many of the files in it are created using an automated Python 3.11 script in the repo [`set_update.py`](set_update.py). 

This script is automatically run whenever a change is pushed to the repo and once daily to check for new missing items.

As we go over how to add and edit various parts of the repo I'm going to be using an example of adding a `marvel` Image Set.

If you're unsure how to construct a YAML file please read this [guide](https://metamanager.wiki/en/latest/home/guides/yaml.html).

`set_update.py` can either be run using GitHub Actions whenever you push a change or run locally using Python 3.11, but either way you'll need to provide some keys so it can connect to TMDb and Trakt.

### Adding Secrets

To run `set_update.py` the code needs to connect to TMDb and Trakt with access keys provided by you.

#### Forked Repo Secrets

The automation works fine for the main repo but if you create your own fork of the repo then you'll need to add the correct secrets to the repo for the automation to work.

The automation is only required if you want an "active" fork that has automation built-in (such as you wanting to "daily run" your own fork rather than the main repo). If you are only creating a fork so that you can submit Pull Requests, this is not a mandatory step as the main repo will run automation when any Pull Request is accepted

1. First have your `TMDb V3 API Key`, `Trakt Client ID`, and `Trakt Access Token` at hand.
   - `TMDb V3 API Key`:  TMDb V3 API Key. [Instructions](https://developers.themoviedb.org/3/getting-started/introduction)
   - `Trakt Client ID`: `client_id` in trakt PMM Authorization. [Authorization Instructions](https://metamanager.wiki/en/latest/config/trakt.html)
   - `Trakt Access Token`: `access_token` in trakt PMM Authorization. [Authorization Instructions](https://metamanager.wiki/en/latest/config/trakt.html)
2. Next you need to add the above keys into you fork on GitHub, on GitHub.com on your fork's main page open your fork's `Settings` page. Then click `Secrets and variables` -> `Actions` in the `Security` section of the left menu.
3. Now add your `TMDb V3 API Key` as a secret by clicking `New repositroy secret` in the top right and for Name use `TMDBAPI` and for Secret use your `TMDb V3 API Key` and then Click `Add secret`.
4. Now add your `Trakt Client ID` as a secret by clicking `New repositroy secret` in the top right and for Name use `TRAKT_ID` and for Secret use your `Trakt Client ID` and then Click `Add secret`.
5. Now add your `Trakt Access Token` as a secret by clicking `New repositroy secret` in the top right and for Name use `TRAKT_TOKEN` and for Secret use your `Trakt Access Token` and then Click `Add secret`.

#### Local Secrets

If you want to run `set_update.py` locally you need to either set up the Environment Variables `TMDBAPI`, `TRAKT_ID`, and `TRAKT_TOKEN` or use the run arguments `--tmdbapi`, `--trakt_id`, and `trakt_token`.

### New Image Set

To add a new Image Set edit `sets.yml` and add the `set_key` you want to use as the mapping name and give it the attributes `title` and `description` (These will end up on the readme page).

```yaml
sets:
  movies:                       # Image Set Key
    title: Sets - Movies        # Image Set Title
    description: Movie Posters  # Image Set Description
  mcu:
    title: Marvel Properties
    description: Images for all Marvel Properties
```

Then either push your changes or run `set_update.py` locally to initialize the set and create the initial Image Set file at `mcu/set.yml` which to start will just have `sections:`.

### Edit Image Set

To edit the `title` or `description` just change the value in the sets file.

If you want to change the `set_key` simply add `set_key` under the old new and give it the new key. **DO NOT CHANGE THE MAPPING NAME**

```yaml
sets:
  movies:                       # Image Set Key
    title: Sets - Movies        # Image Set Title
    description: Movie Posters  # Image Set Description
  mcu:
    title: Marvel Properties
    description: Images for all Marvel Properties
    set_key: marvel             # This will change this set's key from `mcu` to `marvel`
```

Then either push your changes or run `set_update.py` locally to edit the set sections.

### New Image Set Section

An Image Set Section is what defines the movies/shows in that section and their TMDb ID (For Movies) or TVDb ID (For Shows). 

To add a new section to an Image Set edit the `set.yml` file inside the folder named after the Image Set key and add the `section_key` you want like so. 

```yaml
sections:
  ironman:    # adding the ironman section
  thor:       # adding the thor section
```

Then either push your changes or run `set_update.py` locally to initialize the sections.

Now each section will have an auto generated `title` (We will change this later), a blank `builders` attribute, and the `styles` attribute:

```yaml
sections:
  ironman:
    title: Ironman
    builders:
    styles:
  thor:
    title: Thor
    builders:
    styles:
```

### Adding Builders

Builders define what movies and shows are tracked by this Section and their TMDb/TVDb IDs. 

#### Builders

| Builder           | Description                                                                                |
|:------------------|:-------------------------------------------------------------------------------------------|
| `tmdb_collection` | TMDb Collection ID or URL. Can take multiple values as a comma separated string or a list. |
| `tmdb_movie`      | TMDb Movie ID or URL. Can take multiple values as a comma separated string or a list.      |
| `tmdb_show`       | TMDb Show ID or URL. Can take multiple values as a comma separated string or a list.       |
| `tvdb_show`       | TVDb Show ID or URL. Can take multiple values as a comma separated string or a list.       |
| `imdb_id`         | IMDb ID or URL. Can take multiple values as a comma separated string or a list.            |
| `tmdb_list`       | TMDb List ID or URL. Can take multiple values only as a list.                              |
| `imdb_list`       | IMDb List URL or IMDb Search URL. Can take multiple values only as a list.                 |
| `trakt_list`      | Trakt List URL. Can take multiple values only as a list.                                   |
| `mdblist_list`    | MdbList URL. Can take multiple values only as a list.                                      |

Now were going to give each section a `tmdb_colleciton` builder with their respective TMDb Collection ID (Found searching [TMDb](https://www.themoviedb.org)) to initialize the `movies` and `shows` lists.

```yaml
sections:
  ironman:
    title: Ironman
    builders:
       tmdb_collection: 131292
    styles:
  thor:
    title: Thor
    builders:
       tmdb_collection: 131296
    styles:
```

Add the above then either push your changes or run `set_update.py` locally to initialize the `movies` and `shows` lists.

```yaml
sections:
  ironman:
    title: Ironman
    builders:
      tmdb_collection: 131292
    styles:
    collections:
      "Iron Man Collection":
      - "Iron Man"
    movies:
      "Iron Man (2008)": 1726
      "Iron Man 2 (2010)": 10138
      "Iron Man 3 (2013)": 68721
  thor:
    title: Thor
    builders:
      tmdb_collection: 131296
    styles:
    collections:
      "Thor Collection":
      - "Thor"
    movies:
      "Thor (2011)": 10195
      "Thor: The Dark World (2013)": 76338
      "Thor: Ragnarok (2017)": 284053
      "Thor: Love and Thunder (2022)": 616037
```

There was two new attributes added to each section, `collections` and `movies` (If the builder had a show then `shows` would also be added).

`collections` is auto generated based on the TMDb Collection called but more can be added if desired. The list under the collection is a list of alternative collection names to also apply that poster too.

Custom collections can be added to the collections list as well as custom alternative collection names can be added to any list.

`movies` and its tv counterpart `shows` are where the ID mappings go. These lists must be auto generated from the builders aside from [editions](#adding-editions).

### Adding Image Styles

An Image Style File is a file that directly has links to the actual image that will be used for each movie or show. Each Section can have any number of different Styles and these files are what defines them.

First we need to initialize the style file by adding a Style Key under `styles`. The style key can be whatever you want but it usually has to do with the image creator.

```yaml
sections:
  ironman:
    title: Ironman
    builders:
      tmdb_collection: 131292
    styles:
      my_style_key:  # Added the Style Key here ending with `:`
    collections:
      "Iron Man Collection":
      - "Iron Man"
    movies:
      "Iron Man (2008)": 1726
      "Iron Man 2 (2010)": 10138
      "Iron Man 3 (2013)": 68721
  thor:
    title: Thor
    builders:
      tmdb_collection: 131296
    styles:
      my_style_key:  # Added the Style Key here ending with `:`
    collections:
      "Thor Collection":
      - "Thor"
    movies:
      "Thor (2011)": 10195
      "Thor: The Dark World (2013)": 76338
      "Thor: Ragnarok (2017)": 284053
      "Thor: Love and Thunder (2022)": 616037
```

Add the above then either push your changes or run `set_update.py` locally to initialize styles. The Image Set file won't change, but you'll now have three new files at `marvel/missing.yml`, `marvel/styles/ironman/my_style_key.yml` and `marvel/styles/thor/my_style_key.yml`.

* `marvel/missing.yml`: Is the missing file for this Image Set.
* `marvel/styles/ironman/my_style_key.yml`: The Image Style File for the `my_style_key` Style Key in the `ironman` Section of the Image Set File `marvel`.
* `marvel/styles/thor/my_style_key.yml`: The Image Style File for the `my_style_key` Style Key in the `thor` Section of the Image Set File `marvel`.

See more on these Files at [Edit Image Style Files](#edit-image-style-files)

### Edit Image Set Sections

Now if you want to edit the Image Set File open the file in question and change the value you wish to change. Then either push your changes or run `set_update.py` locally to update the associated files.

You can change the `title`, add/remove `builders`, add/remove `styles`, add/remove `collections`, add/remove collection alternative names, and add/remove editions.

#### Adding Editions

To add an edition first the original edition of the movie/show must be already found by the builder and listed under `movies`/`shows`. Then a new entry will need to be added to the list. 

For Example, lets say there's a "Thunder Edition" of Thor: Love and Thunder and we want to add it to the above `thor` section.

1. Copy the existing `"Thor: Love and Thunder (2022)": 616037` line and then change the name it doesn't matter what to, but it cannot be the same.


   ```yaml
     thor:
       title: Thor
       builders:
         tmdb_collection: 131296
       styles:
         my_style:
       collections:
         "Thor Collection":
         - "Thor"
       movies:
         "Thor (2011)": 10195
         "Thor: The Dark World (2013)": 76338
         "Thor: Ragnarok (2017)": 284053
         "Thor: Love and Thunder (2022)": 616037
         "Thor: Love and Thunder (2022) Thunder Edition": 616037    # New line
   ```

2. remove the end TMDb ID and add it as the `mapping_id` attribute.


   ```yaml
     thor:
       title: Thor
       builders:
         tmdb_collection: 131296
       styles:
         my_style:
       collections:
         "Thor Collection":
         - "Thor"
       movies:
         "Thor (2011)": 10195
         "Thor: The Dark World (2013)": 76338
         "Thor: Ragnarok (2017)": 284053
         "Thor: Love and Thunder (2022)": 616037
         "Thor: Love and Thunder (2022) Thunder Edition": # Removed TMDb ID here
           mapping_id: 616037 # Added the TMDb ID here as mapping_id 
   ```

3. Add either `edition_filter` or `edition_contains` to the Edition.

* `edition_filter`: The edition must match this value exactly. 
* `edition_contains`: The edition must contain this string. 


   ```yaml
   thor:
     title: Thor
     builders:
       tmdb_collection: 131296
     styles:
       my_style:
     collections:
       "Thor Collection":
       - "Thor"
     movies:
       "Thor (2011)": 10195
       "Thor: The Dark World (2013)": 76338
       "Thor: Ragnarok (2017)": 284053
       "Thor: Love and Thunder (2022)": 616037
       "Thor: Love and Thunder (2022) Thunder Edition": 
         mapping_id: 616037
         edition_contains: Thunder
   ```

4. Then either push your changes or run `set_update.py` locally to initialize the edition. The script will auto generate the name it wants to use for the edition as well as set up the original to look for a blank edition.


   ```yaml
   thor:
    title: Thor
    builders:
      tmdb_collection: 131296
    styles:
      my_style:
    collections:
      "Thor Collection":
      - "Thor"
    movies:
      "Thor (2011)": 10195
      "Thor: The Dark World (2013)": 76338
      "Thor: Ragnarok (2017)": 284053
      "Thor: Love and Thunder (2022) (Thunder)":
        mapping_id: 616037
        edition_contains: Thunder
      "Thor: Love and Thunder (2022)":
        mapping_id: 616037
        blank_edition: true
   ```

### Edit Image Style Files

You can edit Image Style Files by either editing that Style in the Section's Missing File (`marvel/missing.yml`) or by editing the Image Style File directly.

I find it easier to update missing items from the Missing File and to edit existing 

If you've followed the steps above up till this point your Section's Missing File should look like this.

```yaml
ironman:
  my_style_key:
    info:
      style_author:
      style_image:
      style_link:
    collections:
      "Iron Man Collection": {tpdb_poster: null, url_poster: null}
    movies:
      "Iron Man (2008)": {tpdb_poster: null, url_poster: null}
      "Iron Man 2 (2010)": {tpdb_poster: null, url_poster: null}
      "Iron Man 3 (2013)": {tpdb_poster: null, url_poster: null}
thor:
  my_style_key:
    info:
      style_author:
      style_image:
      style_link:
    collections:
      "Thor Collection": {tpdb_poster: null, url_poster: null}
    movies:
      "Thor (2011)": {tpdb_poster: null, url_poster: null}
      "Thor: The Dark World (2013)": {tpdb_poster: null, url_poster: null}
      "Thor: Ragnarok (2017)": {tpdb_poster: null, url_poster: null}
      "Thor: Love and Thunder (2022)": {tpdb_poster: null, url_poster: null}
```

#### Style Info

If `style_author`, `style_image`, or `style_link` is missing the info section of the style file will have those same attributes. Simply add the desired string in the missing file and after either pushing your changes or running `set_update.py` locally these will disappear from the Missing File and be added to the Image Style File. 

If you need to edit the attribute or add any attribute in the table below just edit the Image Style File and add it there.

| Info Attribute      | Description                                                                                  |
|:--------------------|:---------------------------------------------------------------------------------------------|
| `style_author`      | Image Style Author's Name. This will show on the Read Me page for this Image Set.            |
| `style_image`       | Image Style Preview Image. This will show on the Read Me page for this Image Set.            |
| `style_link`        | Link to Image Style Page. This will be linked on the Read Me page for this Image Set.        |
| `complete`          | Auto Generated attribute that means the set has all its Images.                              |
| `track_seasons`     | Will Track Seasons in this Image Style and add them to the Missing File.                     |
| `track_episodes`    | Will Track Episode Title Cards in this Image Style and add them to the Missing File.         |
| `track_backgrounds` | Will Track Backgrounds in this Image Style and add them to the Missing File.                 |
| `track_editions`    | Will Track Editions from the Image Set in this Image Style and add them to the Missing File. |

#### Style Collections, Movies, and Shows

To add a poster simply change the `null` after either `tpdb_poster` (with ThePosterDB Poster ID as its value) or `url_poster` (with a specific url directly to the image as its value).

```yaml
      "Thor (2011)": {tpdb_poster: 9777, url_poster: null}
      "Thor: The Dark World (2013)": {tpdb_poster: null, url_poster: "https://www.themoviedb.org/t/p/original/bvwWQdMQnsua6dXaCInsPxQG21P.jpg"}
```

You can also add backgrounds by adding the attribute to the item. These will only be tracked if `track_backgrounds: true` is under `info`.

```yaml
      "Thor: Love and Thunder (2022)": {tpdb_poster: null, url_poster: "https://www.themoviedb.org/t/p/original/38S1zYsObBIlGZR31RNUxJ1sAaj.jpg", url_background: "https://www.themoviedb.org/t/p/original/htAwfLn5kmrWeedoNregdIB9BKX.jpg"}
```

or

```yaml
      "Thor: Love and Thunder (2022)": 
        url_poster: "https://www.themoviedb.org/t/p/original/38S1zYsObBIlGZR31RNUxJ1sAaj.jpg"
        url_background: "https://www.themoviedb.org/t/p/original/htAwfLn5kmrWeedoNregdIB9BKX.jpg"
```

After either pushing your changes or running `set_update.py` locally these will disappear from the Missing File and be added to the Image Style File.

