from __future__ import annotations

extensions = ['sphinxext.opengraph']

master_doc = 'index'
exclude_patterns = ['_build']

html_theme = 'basic'
ogp_site_url = 'http://example.org/en/latest/'

# The image is an SVG, and so it should not be included in the social cards
ogp_social_cards = {
    'image': 'foo.svg',
}
