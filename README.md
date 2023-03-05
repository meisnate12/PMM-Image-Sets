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
      - pmm: movies
        template_variables:
          use_starwars: true            # will only use the images that are part of the `starwars` set, no other sets will be used.
```

## Sets
Below is a table of the available sets that can be used, you can click the Image Set link to go to the poster source

| Image Set                     | Set / Key         | Style                                                                           |                               Example                                |
|:------------------------------|:------------------|---------------------------------------------------------------------------------|:--------------------------------------------------------------------:|
| James Bond                    | `bond`            | `default`<br/>[Image Credit to RedHeadJedi](https://theposterdb.com/set/107797) | <img src="https://theposterdb.com/api/assets/176906" height="200"/>  |
| Worlds of DC                  | `dc`              | `default`<br/>[Image Credit to DIIVOY](https://theposterdb.com/set/80057)       | <img src="https://theposterdb.com/api/assets/128645" height="200"/>  |
|                               | `dc`              | `rhj`<br/>[Image Credit to RedHeadJedi](https://theposterdb.com/set/50563)      |  <img src="https://theposterdb.com/api/assets/79223" height="200"/>  |
| Walt Disney Animation Studios | `disney`          | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/2454)   |  <img src="https://theposterdb.com/api/assets/6016" height="200"/>   |
|                               | `disney`          | `rhj`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/62522)      |  <img src="https://theposterdb.com/api/assets/98903" height="200"/>  |
| The Godfather Collection      | `godfather`       | `default`<br/>[Image Credit to Eternal](https://theposterdb.com/set/183508)     | <img src="https://theposterdb.com/api/assets/312507" height="200"/>  |
| Godzilla (Heisei) Collection  | `godzilla_heisei` | `default`<br/>[Image Credit to DoctorBat](https://theposterdb.com/set/182956)   | <img src="https://theposterdb.com/api/assets/311344" height="200"/>  |
|                               | `godzilla_heisei` | `doctorbat`<br/>[Image Credit to DoctorBat](https://theposterdb.com/set/182960) | <img src="https://theposterdb.com/api/assets/311363" height="200"/>  |
| Godzilla (Showa) Collection   | `godzilla_showa`  | `default`<br/>[Image Credit to DoctorBat](https://theposterdb.com/set/181742)   | <img src="https://theposterdb.com/api/assets/309108" height="200"/>  |
|                               | `godzilla_showa`  | `doctorbat`<br/>[Image Credit to DoctorBat](https://theposterdb.com/set/181738) | <img src="https://theposterdb.com/api/assets/309072" height="200"/>  |
| Indiana Jones Collection      | `indiana`         | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/34045)  |  <img src="https://theposterdb.com/api/assets/53303" height="200"/>  |
|                               | `indiana`         | `olivier`<br/>[Image Credit to Olivier_286](https://theposterdb.com/set/4874)   |  <img src="https://theposterdb.com/api/assets/10361" height="200"/>  |
| Jurassic Park Collection      | `jurassic`        | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/97241)  | <img src="https://theposterdb.com/api/assets/158968" height="200"/>  |
| In Association With Marvel    | `marvel`          | `default`<br/>[Image Credit to DIIVOY](https://theposterdb.com/set/78444)       | <img src="https://theposterdb.com/api/assets/125372" height="200"/>  |
| Marvel Cinematic Universe     | `mcu`             | `default`<br/>[Image Credit to DIIVOY](https://theposterdb.com/set/71510)       | <img src="https://theposterdb.com/api/assets/143466" height="200"/>  |
|                               | `mcu`             | `diivoy`<br/>[Image Credit to DIIVOY](https://theposterdb.com/set/41596)        |  <img src="https://theposterdb.com/api/assets/65407" height="200"/>  |
|                               | `mcu`             | `rhj`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/4475)       |  <img src="https://theposterdb.com/api/assets/9772" height="200"/>   |
|                               | `mcu`             | `rhj2`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/87080)     | <img src="https://theposterdb.com/api/assets/139853" height="200"/>  |
| Middle-Earth Collection"      | `middle`          | `default`<br/>[Image Credit to mikenobbs](https://theposterdb.com/set/115877)   | <img src="https://theposterdb.com/api/assets/191451" height="200"/>  |
|                               | `middle`          | `rhj`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/20379)      |  <img src="https://theposterdb.com/api/assets/1716" height="200"/>   |
| Pixar Animation Studios       | `pixar`           | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/97)     |   <img src="https://theposterdb.com/api/assets/456" height="200"/>   |
| Saw Collection                | `saw`             | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/95260)  | <img src="https://theposterdb.com/api/assets/155363" height="200"/>  |
| Star Wars Collection          | `starwars`        | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/93852)  | <img src="https://theposterdb.com/api/assets/152792" height="200"/>  |
|                               | `starwars`        | `rhj`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/89606)      | <img src="https://theposterdb.com/api/assets/145035" height="200"/>  |
| Wizarding World Collection    | `wizard`          | `default`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/101665) | <img src="https://theposterdb.com/api/assets/166278" height="200"/>  |
|                               | `wizard`          | `dsman`<br/>[Image Credit to Dsman124](https://theposterdb.com/set/12177)       |  <img src="https://theposterdb.com/api/assets/21001" height="200"/>  |
|                               | `wizard`          | `rhj`<br/>[Image Credit to RedHeadjedi](https://theposterdb.com/set/11706)      | <img src="https://theposterdb.com/api/assets/85944" height="200"/>   |
