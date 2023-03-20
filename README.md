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

## Sets - Movies

Below is a table of the available sets that can be used on Movie libraries, you can click the Image Set link to go to the poster source

### Alien

**Set Key:** `alien`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/1214" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/357">RedHeadJedi</a> <br></td>
</tr></table>

### Avatar

**Set Key:** `avatar`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/303873" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/179016">RedHeadJedi</a> <br></td>
</tr></table>

### Bond

**Set Key:** `bond`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/176911" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/107797">RedHeadJedi</a> <br></td>
</tr></table>

### Fast Furious

**Set Key:** `fast_furious`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/1070" height="200"/> <br><strong>Style Key:</strong> <code>mikenobbs</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/297">mikenobbs</a> <br></td>
</tr></table>

### Godfather

**Set Key:** `godfather`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/312509" height="200"/> <br><strong>Style Key:</strong> <code>eternal</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/183508">Eternal</a> <br></td>
</tr></table>

### Godzilla Heisei

**Set Key:** `godzilla_heisei`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/311350" height="200"/> <br><strong>Style Key:</strong> <code>doctorbat</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/182956">DoctorBat</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/311369" height="200"/> <br><strong>Style Key:</strong> <code>doctorbat2</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/182960">DoctorBat</a> <br></td>
</tr></table>

### Godzilla Monsterverse

**Set Key:** `godzilla_monsterverse`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/135068" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/84136">RedHeadJedi</a> <br></td>
</tr></table>

### Godzilla Showa

**Set Key:** `godzilla_showa`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/309124" height="200"/> <br><strong>Style Key:</strong> <code>doctorbat</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/181742">DoctorBat</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/309088" height="200"/> <br><strong>Style Key:</strong> <code>doctorbat2</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/181738">DoctorBat</a> <br></td>
</tr></table>

### Indiana

**Set Key:** `indiana`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/53304" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/34045">RedHeadJedi</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/10362" height="200"/> <br><strong>Style Key:</strong> <code>olivier</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/4874">Olivier_286</a> <br></td>
</tr></table>

### John Wick

**Set Key:** `john_wick`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/12029" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/6002">RedHeadJedi</a> <br></td>
</tr></table>

### Jurassic

**Set Key:** `jurassic`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/168738" height="200"/> <br><strong>Style Key:</strong> <code>diiivoy_neon</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/103129">DIIIVOY</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/158973" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/97241">RedHeadJedi</a> <br></td>
</tr></table>

### Mib

**Set Key:** `mib`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/16550" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/9203">RedHeadJedi</a> <br></td>
</tr></table>

### Middle

**Set Key:** `middle`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/191455" height="200"/> <br><strong>Style Key:</strong> <code>mikenobbs</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/115877">mikenobbs</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/33511" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/20379">RedHeadJedi</a> <br></td>
</tr></table>

### Mission

**Set Key:** `mission`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/65202" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/20379">RedHeadJedi</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/2705" height="200"/> <br><strong>Style Key:</strong> <code>rhj2</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/1001">RedHeadJedi</a> <br></td>
</tr></table>

### Nowyouseeme

**Set Key:** `nowyouseeme`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/2628" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/20379">RedHeadJedi</a> <br></td>
</tr></table>

### Ocean

**Set Key:** `ocean`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/228" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/70">RedHeadJedi</a> <br></td>
</tr></table>

### Pirates

**Set Key:** `pirates`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/49933" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/31826">RedHeadJedi</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/105782" height="200"/> <br><strong>Style Key:</strong> <code>diiivoy</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/66561">DIIIVOY</a> <br></td>
</tr></table>

### Poirot

**Set Key:** `poirot`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/112185" height="200"/> <br><strong>Style Key:</strong> <code>diiivoy_neon</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/70314">DIIIVOY</a> <br></td>
</tr></table>

### Predator

**Set Key:** `predator`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/243" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/76">RedHeadJedi</a> <br></td>
</tr></table>

### Rocky Creed

**Set Key:** `rocky_creed`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/5901" height="200"/> <br><strong>Style Key:</strong> <code>dannybeaton</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/2402">Danny Beaton</a> <br></td>
</tr></table>

### Saw

**Set Key:** `saw`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/155368" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/95260">RedHeadJedi</a> <br></td>
</tr></table>

### Wizard

**Set Key:** `wizard`

#### Styles:

<table style="border-collapse: collapse; border: none;"><tr style="border: none;">
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/157013" height="200"/> <br><strong>Style Key:</strong> <code>diiivoy_neon</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/96588">DIIIVOY</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/166282" height="200"/> <br><strong>Style Key:</strong> <code>rhj</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/101665">RedHeadJedi</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/85948" height="200"/> <br><strong>Style Key:</strong> <code>rhj2</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/11706">RedHeadJedi</a> <br></td>
<td style="border: none;text-align: center;"><img src="https://theposterdb.com/api/assets/21005" height="200"/> <br><strong>Style Key:</strong> <code>dsman</code> <br><strong>Credit:</strong> <a href="https://theposterdb.com/set/12177">Dsman124</a> <br></td>
</tr></table>
