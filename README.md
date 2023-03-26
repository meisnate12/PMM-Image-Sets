# PMM Image Sets

PMM Image Sets is a set of pre-defined files to work in conjunction with [Plex Meta Manager](https://github.com/meisnate12/Plex-Meta-Manager)

Image Sets allow you to easily apply our curated set of Posters and Title Cards to your libraries, skipping the need to manually download and apply individual posters to your media.

## Usage

Image Sets can be called out in your Plex Meta Manager config file as follows:

```yaml
libraries:
  Movies:                               # must match a library in your Plex server
    image_sets:
      - pmm: movies                     # name of the image 
        template_variables:
          use_all: true                 # this is false by default, meaning you need to manually specify which sets you want
  TV Shows:                             # must match a library in your Plex server
    image_sets:
      - pmm: shows
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

To add a new section to an Image Set edit the `set.yml` inside the folder named after the Image Set key and add the `section_key` you want like so. 

```yaml
sections:
  ironman:    # adding the ironman section
  thor:       # adding the thor section
```

Then either push your changes or run `set_update.py` locally to initialize the sections.

Now each section :

```yaml
sections:
  ironman:
    title: Ironman
    builders:
    styles:
      default:
  thor:
    title: Thor
    builders:
    styles:
      default:
```

### Edit Image Set Sections


