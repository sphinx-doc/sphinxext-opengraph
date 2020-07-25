# sphinxext-opengraph
![Build](https://github.com/wpilibsuite/sphinxext-opengraph/workflows/Test%20and%20Deploy/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Sphinx extension to generate OpenGraph metadata (https://ogp.me/)

## Installation

`python -m pip install sphinxext-opengraph`

## Usage
Just add `sphinxext.opengraph` to your extensions list in your `conf.py`

```python
extensions = [
   sphinxext.opengraph,
]
```
## Options
These values are placed in the conf.py of your sphinx project.

* `ogp_site_url`
    * This config option is very important, set it to the URL the site is being hosted on. 
* `ogp_description_length`
    * Configure the amount of characters taken from a page. The default of 200 is probably good for most people. If something other than a number is used, it defaults back to 200. 
* `ogp_site_name`
    * This is not required. Name of the site. This is displayed above the title.
* `ogp_image`
    * This is not required. Link to image to show.
* `ogp_image_alt`
    * This is not required. Alt text for image. Defaults to using `ogp_site_name` or the document's title as alt text, if available. Set to `False` if you want to turn off alt text completely.
* `ogp_use_first_image`
    * This is not required. Set to True to use each page's first image, if available. If set to True but no image is found, Sphinx will use `ogp_image` instead.
* `ogp_type`
    * This sets the ogp type attribute, for more information on the types available please take a look at https://ogp.me/#types. By default it is set to `website`, which should be fine for most use cases.
* `ogp_custom_meta_tags`
    * This is not required. List of custom html snippets to insert.

## Example Config

### Simple Config

```python
ogp_site_url = "http://example.org/"
ogp_image = "http://example.org/image.png"
```

### Advanced Config

```python
ogp_site_url = "http://example.org/"
ogp_image = "http://example.org/image.png"
ogp_description_length = 300
ogp_type = "article"

ogp_custom_meta_tags = [
    '<meta property="og:ignore_canonical" content="true" />',
]

```
