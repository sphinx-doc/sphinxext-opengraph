from __future__ import annotations

extensions = ['sphinxext.opengraph']

master_doc = 'index'
exclude_patterns = ['_build']

html_theme = 'basic'

ogp_site_url = 'http://example.org/en/latest/'

ogp_custom_meta_tags = [
    '<meta property="og:ignore_canonical" content="true" />',
]
