from __future__ import annotations

from typing import TYPE_CHECKING

import conftest
import pytest
from sphinx.errors import ExtensionError

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def get_tag(tags, tag_type, kind='property', prefix='og'):
    return next(tag for tag in tags if tag.get(kind) == f'{prefix}:{tag_type}')


def get_tag_content(tags, tag_type, kind='property', prefix='og'):
    # Gets the content of a specific ogp tag
    return get_tag(tags, tag_type, kind, prefix).get('content', '')


def get_tag_content_text(tags, tag_type, kind='property', prefix='og'):
    # Gets the content of a specific ogp tag
    return get_tag(tags, tag_type, kind, prefix).get_text('content', '')


def get_meta_description(tags):
    tag = next(tag for tag in tags if tag.get('name') == 'description')
    return tag.get('content', '')


@pytest.mark.sphinx('html', testroot='simple')
def test_simple(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')

    assert len(og_meta_tags) > 0
    assert get_tag_content(og_meta_tags, 'type') == 'website'
    assert len(description) == 200
    assert (
        description
        == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse at lorem ornare, fringilla massa nec, venenatis mi. Donec erat sapien, tincidunt nec rhoncus nec, scelerisque id diam. Orci vari...'
    )


@pytest.mark.sphinx('html', testroot='meta-name-description')
def test_meta_name_description(meta_tags):
    og_description = get_tag_content(meta_tags, 'description')
    description = get_meta_description(meta_tags)

    assert description == og_description


@pytest.mark.sphinx('html', testroot='meta-name-description-escape')
def test_meta_name_description_escape(meta_tags):
    og_description = get_tag_content(meta_tags, 'description')
    og_description_text = get_tag_content_text(meta_tags, 'description')

    assert '<' in og_description
    assert '<' not in og_description_text


@pytest.mark.sphinx('html', testroot='meta-name-description-manual-description')
def test_meta_name_manual_description(meta_tags):
    og_description = get_tag_content(meta_tags, 'description')
    description = get_meta_description(meta_tags)

    assert description != og_description
    assert description == 'My manual description'


@pytest.mark.sphinx('html', testroot='meta-name-description-manual-og-description')
def test_meta_name_manual_og_description(meta_tags):
    og_description = get_tag_content(meta_tags, 'description')
    description = get_meta_description(meta_tags)

    assert og_description != description
    assert og_description == 'My manual og:description'


@pytest.mark.sphinx('html', testroot='simple')
def test_site_url(og_meta_tags):
    # Uses the same directory as simple, because it already contains url for a minimal config
    assert (
        get_tag_content(og_meta_tags, 'url')
        == 'http://example.org/en/latest/index.html'
    )


@pytest.mark.sphinx('dirhtml', testroot='simple')
def test_dirhtml_url(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'url') == 'http://example.org/en/latest/'


@pytest.mark.sphinx('html', testroot='image')
def test_image(og_meta_tags):
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/image.png'
    )


@pytest.mark.sphinx('html', testroot='local-image')
def test_local_image(og_meta_tags):
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/_static/sample.jpg'
    )


@pytest.mark.sphinx('html', testroot='social-cards-svg')
def test_social_cards_svg(app: Sphinx, og_meta_tags):
    """If the social cards image is an SVG, it should not be in the social card."""
    assert app.statuscode == 0


@pytest.mark.sphinx('html', testroot='image')
def test_image_alt(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'image:alt') == "Example's Docs!"


@pytest.mark.sphinx('html', testroot='simple')
def test_image_social_cards(meta_tags):
    """Social cards should automatically be added if no og:image is given."""
    pytest.importorskip('matplotlib')
    # Asserting `in` instead of `==` because of the hash that is generated
    assert (
        'http://example.org/en/latest/_images/social_previews/summary_index'
        in get_tag_content(meta_tags, 'image')
    )
    # Image alt text should be taken from page content.
    assert (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        in get_tag_content(meta_tags, 'image:alt')
    )
    # Make sure the extra tags are in the HTML
    assert 'summary_large_image' in get_tag_content(
        meta_tags, 'card', kind='name', prefix='twitter'
    )


@pytest.mark.sphinx('html', testroot='type')
def test_type(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'type') == 'article'


@pytest.mark.sphinx('html', testroot='description-length')
def test_description_length(og_meta_tags):
    assert len(get_tag_content(og_meta_tags, 'description')) == 50


@pytest.mark.sphinx('html', testroot='sitename')
def test_site_name(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'site_name') == "Example's Docs!"


@pytest.mark.sphinx('html', testroot='sitename-from-project')
def test_site_name_project(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'site_name') == 'Project name'


@pytest.mark.sphinx('html', testroot='first-image')
def test_first_image(og_meta_tags):
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/image2.png'
    )
    assert get_tag_content(og_meta_tags, 'image:alt') == 'Test image alt text'


@pytest.mark.sphinx('html', testroot='first-image-no-image')
def test_first_image_no_image(og_meta_tags):
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/image33.png'
    )
    assert get_tag_content(og_meta_tags, 'image:alt') == 'TEST'


@pytest.mark.sphinx('html', testroot='image-rel-paths')
def test_image_rel_paths(og_meta_tags, og_meta_tags_sub):
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/_images/sample.jpg'
    )
    assert (
        get_tag_content(og_meta_tags_sub, 'image')
        == 'http://example.org/en/latest/_images/sample.jpg'
    )


@pytest.mark.sphinx('html', testroot='skip-admonitions')
def test_skip_admonitions(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'description') == 'This is text.'


@pytest.mark.sphinx('html', testroot='skip-title')
def test_skip_first_title(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert 'A Title' not in description
    assert 'Another Title' in description


@pytest.mark.sphinx('html', testroot='skip-title')
def test_skip_title_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert 'Another Title:' in description


@pytest.mark.sphinx('html', testroot='double-spacing')
def test_remove_double_spacing(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert '  ' not in description


@pytest.mark.sphinx('html', testroot='list')
def test_list_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert description == 'Item 1, Item 2, Item 3, Item 4.'


@pytest.mark.sphinx('html', testroot='nested-lists')
def test_nested_list_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert (
        description == 'Item 1, Item 2- Nested Item 1, Nested Item 2., Item 3, Item 4.'
    )


@pytest.mark.sphinx('html', testroot='skip-comments')
def test_skip_comments(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'description') == 'This is text.'


@pytest.mark.sphinx('html', testroot='custom-tags')
def test_custom_tags(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'ignore_canonical') == 'true'


@pytest.mark.sphinx('html', testroot='skip-raw')
def test_skip_raw(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert '<p>' not in description
    assert (
        description
        == 'This text should be included. This text should also be included.'
    )


@pytest.mark.sphinx('html', testroot='skip-code-block')
def test_skip_code_block(og_meta_tags):
    description = get_tag_content(og_meta_tags, 'description')
    assert '<p>' not in description
    assert (
        description
        == 'This text should be included. This text should also be included.'
    )


@pytest.mark.sphinx('html', testroot='quotation-marks')
def test_quotation_marks(og_meta_tags):
    # If smart quotes are disabled and the quotes aren't properly escaped, bs4 will fail to parse the tag and the content will be a empty string
    description = get_tag_content(og_meta_tags, 'description')

    assert (
        description
        == '"This text should appear in escaped quotation marks" This text should still appear as well "while this is once again in quotations"'
    )


@pytest.mark.sphinx('html', testroot='overrides-simple')
def test_overrides_simple(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'description') == 'Overridden description'
    assert get_tag_content(og_meta_tags, 'title') == 'Overridden Title'
    assert get_tag_content(og_meta_tags, 'type') == 'article'
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/overridden-image.png'
    )
    # Make sure alt text still works even when overriding the image
    assert get_tag_content(og_meta_tags, 'image:alt') == "Example's Docs!"


@pytest.mark.sphinx('html', testroot='overrides-complex')
def test_overrides_complex(og_meta_tags):
    assert len(get_tag_content(og_meta_tags, 'description')) == 10
    assert (
        get_tag_content(og_meta_tags, 'image')
        == 'http://example.org/en/latest/img/sample.jpg'
    )
    assert get_tag_content(og_meta_tags, 'image:alt') == 'Overridden Alt Text'


@pytest.mark.sphinx('html', testroot='overrides-disable')
def test_overrides_disable(og_meta_tags):
    assert len(og_meta_tags) == 0


@pytest.mark.sphinx('html', testroot='arbitrary-tags')
def test_arbitrary_tags(og_meta_tags):
    assert (
        get_tag_content(og_meta_tags, 'video')
        == 'http://example.org/en/latest/video.mp4'
    )
    assert get_tag_content(og_meta_tags, 'video:type') == 'video/mp4'


# use same as simple, as configuration is identical to overriden
@pytest.mark.sphinx('html', testroot='simple')
def test_rtd_override(app: Sphinx, monkeypatch):
    monkeypatch.setenv('READTHEDOCS', 'True')
    app.config.html_baseurl = 'https://failure.com/en/latest/'

    app.build()
    tags = conftest._og_meta_tags(app)

    assert get_tag_content(tags, 'url') == 'http://example.org/en/latest/index.html'


@pytest.mark.sphinx('html', testroot='rtd-default')
def test_rtd_valid(app: Sphinx, monkeypatch):
    monkeypatch.setenv('READTHEDOCS', 'True')
    monkeypatch.setenv('READTHEDOCS_CANONICAL_URL', 'https://failure.com/en/latest/')

    app.build()
    tags = conftest._og_meta_tags(app)

    assert get_tag_content(tags, 'url') == 'https://failure.com/en/latest/index.html'


# use rtd-default, as we are not changing configuration, but RTD variables
@pytest.mark.sphinx('html', testroot='rtd-invalid')
def test_rtd_invalid(app: Sphinx, monkeypatch):
    monkeypatch.setenv('READTHEDOCS', 'True')
    app.config.html_baseurl = None

    with pytest.raises(ExtensionError, match='did not provide a valid canonical URL'):
        app.build()


# Test no breakage with no configuration
@pytest.mark.sphinx('html', testroot='rtd-default')
def test_no_configuration_html(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'type') == 'website'


# Test no breakage with no configuration
@pytest.mark.sphinx('dirhtml', testroot='rtd-default')
def test_no_configuration_dirhtml(og_meta_tags):
    assert get_tag_content(og_meta_tags, 'type') == 'website'
