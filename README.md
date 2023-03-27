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

For the purpose of this walkthrough, we will be adding a `marvel` Image Set.

If you're unsure how to construct a YAML file please read this [guide](https://metamanager.wiki/en/latest/home/guides/yaml.html).

`set_update.py` can either be run using GitHub Actions whenever you push a change or run locally using Python 3.11, but either way you'll need to provide some keys so it can connect to TMDb and Trakt.

### Adding Secrets

To run `set_update.py` the code needs to connect to TMDb and Trakt with access keys provided by you.

You can either "daily run" a forked repository which has the automation built in (Option 1) or run the script locally on your own host (Option 2)

#### Option 1 - Forked Repo

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

#### Option 2 - Local

If you want to run `set_update.py` locally, you need to either set up the Environment Variables `TMDBAPI`, `TRAKT_ID`, and `TRAKT_TOKEN` or use the run arguments `--tmdbapi`, `--trakt_id`, and `trakt_token`.

an example run argument would be `python set_update.py --tmdbapi 123456 --trakt_id 1a2bc3 --trakt_token 9z8y7x`

# Image Sets

Image Sets are generally broken up into library type (such as movies, kids movies, shows, kids shows, etc). The main exception to this is universes such as Marvel Cinematic Universe which can contain a multitude of mini-collections within it. 

**You should only create a new Image Set if your images does not fall into an already existing Image Set.**

## Step 1 - Creating an Image Set

To add a new Image Set edit `sets.yml` and add the `set_key` you want to use as the mapping name and give it the attributes `title` and `description` (These will end up on the readme page).

```yaml
sets:
  movies:
    title: Sets - Movies
    description: Movie Posters
  mcu:                                              # Image Set Key
    title: Marvel Properties                        # Image Set Title
    description: Images for all Marvel Properties   # Image Set Description
```

**Then either push your changes or run `set_update.py` locally to initialize the set and create the initial Image Set file at `mcu/set.yml` which to start will just have `sections:`.**



## Step 2 - Editing the Image Set (Optional)

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

**Then either push your changes or run `set_update.py` locally to edit the set sections.**

# Image Set Sections

An Image Set Section is a way of logically creating or splitting Image Sets into smaller parts. For example, the Marvel Cinematic Universe can be split in different ways:
- Iron Man, Thor, Captain America, etc
- Phase 1, Phase 2, Phase 3, etc
- Infinity Saga, Multiverse Saga

Each section then lists all the movies/shows that belong in that section and their TMDb ID (For Movies) or TVDb ID (For Shows).

This allows Plex Meta Manager to compare your library against the movies/shows in the Image Set to see what items you have.

## Step 1 - Creating an Image Set Section

Following the creation of our new `marvel` Set, we are going to split Marvel Cinematic Universe into character-based sections. Open `marvel/set.yml`

To add a new section to an Image Set edit the `set.yml` and add the `section_key` you want.

`section_key` can be named anything, but should logically explain what section

```yaml
sections:
  ironman:    # adding the ironman section
  thor:       # adding the thor section
```

**Then either push your changes or run `set_update.py` locally to initialize the sections.**

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


### Step 2 - Adding Builders

Now that you have an `ironman` and `thor` section, it's time to start filling in the attributes, starting with `builders`.

In simple terms, Builders define how Plex Meta Manager is going to know what movies/shows are part of the Section. This is most commonly done using TMDb Collections, Trakt Lists or any other builder from the below table:

#### Supported Builders

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

We are going to give each section a `tmdb_collection` builder with their respective TMDb Collection ID (Found by searching [TMDb](https://www.themoviedb.org)) to initialize the `movies` and `shows` lists.

```yaml
sections:
  ironman:
    title: Ironman
    builders:
       tmdb_collection: 131292        # https://www.themoviedb.org/collection/131292
    styles:
  thor:
    title: Thor
    builders:
       tmdb_collection: 131296        # https://www.themoviedb.org/collection/131296
    styles:
```

**Then either push your changes or run `set_update.py` locally to initialize the `movies` and `shows` lists.**

Your output should look like the below:

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

### Step 3 - Combining Builders (Optional)

It may be possible that a single Builder doesn't contain every item that you want to be part of the Section. We can use multiple Builders to resolve this.

As an example of this, we will add one of the Marvel One-Shots to the Thor collection by utilizing `tmdb_collection` and `tmdb_movie` builders:

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
       tmdb_movie: 76535              # We have now added https://www.themoviedb.org/movie/76535
    styles:
```
**Then either push your changes or run `set_update.py` locally to initialize the `movies` and `shows` lists.**

Your output should look like the below:

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
      "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": 76535   # This has now been added
```

# Image Styles

An Image Style is used to define a style of posters which should apply to movies within the Section. Each Section can have any number of different Styles and these files are what defines them.

## Step 1 - Adding Image Styles

First we need to initialize the style file by adding a Style Key under `styles`. The style key can be whatever you want, normally we reference the image creator as the key. For this example we will use `my_style_key` as the key.

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
      "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": 76535
```

**Then either push your changes or run `set_update.py` locally to initialize styles.**

The Image Set file won't change, but you'll now have three new files at `marvel/missing.yml`, `marvel/styles/ironman/my_style_key.yml` and `marvel/styles/thor/my_style_key.yml`.

* `marvel/missing.yml`: Is the missing file for this Image Set.
* `marvel/styles/ironman/my_style_key.yml`: The Image Style File for the `my_style_key` Style Key in the `ironman` Section of the Image Set File `marvel`.
* `marvel/styles/thor/my_style_key.yml`: The Image Style File for the `my_style_key` Style Key in the `thor` Section of the Image Set File `marvel`.

See more on these Files at [Edit Image Style Files](#edit-image-style-files)

## Step 2 - Editing the Image Set Sections

Now if you want to edit the Image Set File open the file in question and change the value you wish to change. Then either push your changes or run `set_update.py` locally to update the associated files.

You can change the `title`, add/remove `builders`, add/remove `styles`, add/remove `collections`, add/remove collection alternative names, and add/remove editions.

The `title` attribute should always be legible in Plain English, as it is the title that will appear in the documentation, so shouldn't be "code":

```yaml
sections:
  ironman:
    title: Iron Man       # changed the title from Ironman to Iron Man
    builders:
    styles:
  thor:
    title: Thor
    builders:
    styles:
```

## Image Style Files

Image Style Files are used to map images to each of the movies/shows within the Style.

You can edit Image Style Files by either editing that Style in the Section's Missing File (`marvel/missing.yml`) or by editing the Image Style File directly.

If you are adding new items, we recommend updating the Missing file for the Image Set (i.e. `marvel/missing.yml`). If you are editing existing items, you must use the Style file (i.e. `marvel/styles/thor/my_style_key.yml`)

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
      "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": {tpdb_poster: null, url_poster: null}
```

### Step 1 - Completing the Style Info

Open the Missing file (`marvel/missing.yml`) and fill in the Style Info attributes.

At a minimum. we recommend you to complete `style_author`, `style_image`, `style_link`

| Info Attribute      | Description                                                                                                                   |
|:--------------------|:------------------------------------------------------------------------------------------------------------------------------|
| `style_author`      | Image Style Author's Name. This will show on the Read Me page for this Image Set.                                             |
| `style_image`       | Direct link to an example image of what will be applied. This will show on the Read Me page for this Image Set.               |
| `style_link`        | Link to Image Style Page (such as the TPDB Set page). This will be linked on the Read Me page for this Image Set.             |
| `complete`          | Auto Generated attribute that means the set has all its Images. Must be either `true` or `false`                              |
| `track_seasons`     | Will Track Seasons in this Image Style and add them to the Missing File. Must be either `true` or `false`                     |
| `track_episodes`    | Will Track Episode Title Cards in this Image Style and add them to the Missing File. Must be either `true` or `false`         |
| `track_backgrounds` | Will Track Backgrounds in this Image Style and add them to the Missing File. Must be either `true` or `false`                 |
| `track_editions`    | Will Track Editions from the Image Set in this Image Style and add them to the Missing File. Must be either `true` or `false` |

**Then either push your changes or run `set_update.py` locally.**

These attributes should now disappear from the Missing file and will be added to teh Image Style File

If you need to edit the attribute or add any other attribute, you should edit the Image Style File and add it there.

### Step 2 - Editing Style Collections, Movies, and Shows

Open the Missing file (`marvel/missing.yml`)

To add a poster simply change the `null` after either `tpdb_poster` (with ThePosterDB Poster ID as its value) or `url_poster` (with a specific url directly to the image as its value).

```yaml
      "Thor (2011)": {tpdb_poster: 9777, url_poster: null}      # points to https://theposterdb.com/api/assets/9777
      "Thor: Love and Thunder (2022)": {tpdb_poster: null, url_poster: "https://alternativemovieposters.com/wp-content/uploads/2022/07/SamDunn_Thor.jpg"}
```

Optionally, you can remove any null attributes. This has no effect on the end-result but can be visually easier to understand:

```yaml
      "Thor (2011)": {tpdb_poster: 9777}
      "Thor: Love and Thunder (2022)": {url_poster: "https://alternativemovieposters.com/wp-content/uploads/2022/07/SamDunn_Thor.jpg"}
```

You can also add backgrounds by adding the attribute to the item. These will only be tracked if `track_backgrounds: true` is under `info`.

```yaml
      "Thor: Love and Thunder (2022)": {tpdb_poster: null, url_poster: "https://alternativemovieposters.com/wp-content/uploads/2022/07/SamDunn_Thor.jpg", url_background: "https://www.themoviedb.org/t/p/original/htAwfLn5kmrWeedoNregdIB9BKX.jpg"}
```

The above example YAML code can also be written in the following format. Either way is valid and will result in the same output, this is purely a visual change:

```yaml
      "Thor: Love and Thunder (2022)": 
        url_poster: "https://www.themoviedb.org/t/p/original/38S1zYsObBIlGZR31RNUxJ1sAaj.jpg"
        url_background: "https://www.themoviedb.org/t/p/original/htAwfLn5kmrWeedoNregdIB9BKX.jpg"
```

**Then either push your changes or run `set_update.py` locally.**

These attributes will disappear from the Missing File and be added to the Image Style File.

# Editions (Optional)

Quite often, users will have multiple editions of the same movie/show within their library, such as Extended Edition or Director's Cut. Image Sets allow you to set different posters depending on the edition of the movie/show.

## Step 1 - Adding An Edition

To add an edition first the original edition of the movie/show must be already found by the builder and listed under `movies`/`shows`. Then a new entry will need to be added to the list. 

For Example, lets say there's a "Thunder Edition" of "Thor: Love and Thunder" and we want to add it to the above `thor` section.

1. Copy the existing `"Thor: Love and Thunder (2022)": 616037` line and then change the mapping name. The mapping name needs to be unique, but should make logical sense to explain what it is:

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
         "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": 76535
         "Thor: Love and Thunder (2022) Thunder Edition": 616037    # New line added with unique mapping name
   ```

2. remove the end TMDb ID and add it as the `mapping_id` attribute.


   ```yaml
         "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": 76535
         "Thor: Love and Thunder (2022) Thunder Edition": # Removed TMDb ID here
           mapping_id: 616037 # Added the TMDb ID here as mapping_id 
   ```

3. Add either `edition_filter` or `edition_contains` to the Edition.

* `edition_filter`: The edition must match this value exactly. 
* `edition_contains`: The edition must contain this string. 

   ```yaml
       "Marvel One-Shot: A Funny Thing Happened on the Way to Thor's Hammer (2011)": 76535
       "Thor: Love and Thunder (2022) Thunder Edition": 
         mapping_id: 616037
         edition_contains: Thunder      # edition must contain the word "Thunder"
   ```

**Then either push your changes or run `set_update.py` locally to initialize the edition.**

The script will auto generate the name it wants to use for the edition as well as set up the original to look for a blank edition.

   ```yaml
    movies:
      "Thor: Love and Thunder (2022) (Thunder)":
        mapping_id: 616037
        edition_contains: Thunder
      "Thor: Love and Thunder (2022)":
        mapping_id: 616037
        blank_edition: true
   ```
