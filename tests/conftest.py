from __future__ import annotations

from pathlib import Path

import pytest
import sphinx
from bs4 import BeautifulSoup

try:
    import matplotlib as mpl
except ImportError:
    pass
else:
    mpl.rcParams['figure.max_open_warning'] = 0

pytest_plugins = ['sphinx.testing.fixtures']


@pytest.fixture(scope='session')
def rootdir():
    if sphinx.version_info[:2] < (7, 2):
        from sphinx.testing.path import path

        return path(__file__).parent.abspath() / 'roots'

    return Path(__file__).parent.resolve() / 'roots'


@pytest.fixture
def content(app):
    app.build(force_all=True)
    return app


def _meta_tags(content, subdir=None):
    if subdir is None:
        c = (content.outdir / 'index.html').read_text(encoding='utf-8')
    else:
        c = (content.outdir / subdir / 'index.html').read_text(encoding='utf-8')
    return BeautifulSoup(c, 'html.parser').find_all('meta')


def _og_meta_tags(content):
    return [
        tag for tag in _meta_tags(content) if tag.get('property', '').startswith('og:')
    ]


@pytest.fixture
def meta_tags(content):
    return _meta_tags(content)


@pytest.fixture
def og_meta_tags(content):
    return [
        tag for tag in _meta_tags(content) if tag.get('property', '').startswith('og:')
    ]


@pytest.fixture
def og_meta_tags_sub(content):
    return [
        tag
        for tag in _meta_tags(content, 'sub')
        if tag.get('property', '').startswith('og:')
    ]


def pytest_configure(config):
    config.addinivalue_line('markers', 'sphinx')
