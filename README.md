# PMM Image Sets

PMM Image Sets is a set of pre-defined Metadata files to work in conjunction with [Plex Meta Manager](https://github.com/meisnate12/Plex-Meta-Manager)

Image Sets allow you to easily apply our curated set of Posters and Title Cards to your libraries, skipping the need to manually download and apply individual posters to your media.

## Usage

Image Sets can be called out in your Plex Meta Manager config file as follows:

```yaml
libraries:
  Movies:                               # must match a library in your Plex server
    images_path:
      - pmm: movies
        template_variables:
          use_all: true                 # this is false by default, meaning you need to manually specify which sets you want
  TV Shows:                             # must match a library in your Plex server
    images_path:
      - pmm: shows
        template_variables:
          use_starwars: true            # will only use the images that are part of the `starwars` set, no other sets will be used.
```
