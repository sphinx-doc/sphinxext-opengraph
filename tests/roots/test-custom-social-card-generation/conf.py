from __future__ import annotations

import io
import pathlib

extensions = ['sphinxext.opengraph']

master_doc = 'index'
exclude_patterns = ['_build']

html_theme = 'basic'

ogp_site_url = 'http://example.org/en/latest/'


def setup(app):
    app.connect('generate-social-card', generate)


def generate(
    app,
    contents,
    check_if_signature_exists,
) -> None | tuple[io.BytesIO, str]:
    signature = 'custom-signature'
    check_if_signature_exists(signature)

    return io.BytesIO(pathlib.Path(app.srcdir / 'pixel.png').read_bytes()), signature
