import pytest
from sphinx.application import Sphinx
import conftest
import os


def get_tag(tags, tag_type):
    return [tag for tag in tags if tag.get("property") == "og:{}".format(tag_type)][0]


def get_tag_content(tags, tag_type):
    # Gets the content of a specific ogp tag
    return get_tag(tags, tag_type).get("content", "")


@pytest.mark.sphinx("html", testroot="simple")
def test_simple(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")

    assert len(og_meta_tags) > 0
    assert get_tag_content(og_meta_tags, "type") == "website"
    assert len(description) == 200
    assert (
        description
        == "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse at lorem ornare, fringilla massa nec, venenatis mi. Donec erat sapien, tincidunt nec rhoncus nec, scelerisque id diam. Orci vari..."
    )


@pytest.mark.sphinx("html", testroot="simple")
def test_site_url(og_meta_tags):
    # Uses the same directory as simple, because it already contains url for a minimal config
    assert get_tag_content(og_meta_tags, "url") == "http://example.org/index.html"


@pytest.mark.sphinx("html", testroot="image")
def test_image(og_meta_tags):
    assert get_tag_content(og_meta_tags, "image") == "http://example.org/image.png"


@pytest.mark.sphinx("html", testroot="image")
def test_image_alt(og_meta_tags):
    assert get_tag_content(og_meta_tags, "image:alt") == "Example's Docs!"


@pytest.mark.sphinx("html", testroot="type")
def test_type(og_meta_tags):
    assert get_tag_content(og_meta_tags, "type") == "article"


@pytest.mark.sphinx("html", testroot="description-length")
def test_description_length(og_meta_tags):
    assert len(get_tag_content(og_meta_tags, "description")) == 50


@pytest.mark.sphinx("html", testroot="sitename")
def test_site_name(og_meta_tags):
    assert get_tag_content(og_meta_tags, "site_name") == "Example's Docs!"


@pytest.mark.sphinx("html", testroot="first-image")
def test_first_image(og_meta_tags):
    assert get_tag_content(og_meta_tags, "image") == "http://example.org/image2.png"
    assert get_tag_content(og_meta_tags, "image:alt") == "Test image alt text"


@pytest.mark.sphinx("html", testroot="first-image-no-image")
def test_first_image_no_image(og_meta_tags):
    assert get_tag_content(og_meta_tags, "image") == "http://example.org/image33.png"
    assert get_tag_content(og_meta_tags, "image:alt") == "TEST"


@pytest.mark.sphinx("html", testroot="skip-admonitions")
def test_skip_admonitions(og_meta_tags):
    assert get_tag_content(og_meta_tags, "description") == "This is text."


@pytest.mark.sphinx("html", testroot="skip-title")
def test_skip_first_title(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert "A Title" not in description
    assert "Another Title" in description


@pytest.mark.sphinx("html", testroot="skip-title")
def test_skip_title_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert "Another Title:" in description


@pytest.mark.sphinx("html", testroot="double-spacing")
def test_remove_double_spacing(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert "  " not in description


@pytest.mark.sphinx("html", testroot="list")
def test_list_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert description == "Item 1, Item 2, Item 3, Item 4."


@pytest.mark.sphinx("html", testroot="nested-lists")
def test_nested_list_punctuation(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert (
        description == "Item 1, Item 2- Nested Item 1, Nested Item 2., Item 3, Item 4."
    )


@pytest.mark.sphinx("html", testroot="skip-comments")
def test_skip_comments(og_meta_tags):
    assert get_tag_content(og_meta_tags, "description") == "This is text."


@pytest.mark.sphinx("html", testroot="custom-tags")
def test_custom_tags(og_meta_tags):
    assert get_tag_content(og_meta_tags, "ignore_canonical") == "true"


@pytest.mark.sphinx("html", testroot="skip-raw")
def test_skip_raw(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert "<p>" not in description
    assert (
        description
        == "This text should be included. This text should also be included."
    )


@pytest.mark.sphinx("html", testroot="skip-code-block")
def test_skip_code_block(og_meta_tags):
    description = get_tag_content(og_meta_tags, "description")
    assert "<p>" not in description
    assert (
        description
        == "This text should be included. This text should also be included."
    )


# use same as simple, as configuration is identical to overriden
@pytest.mark.sphinx("html", testroot="simple")
def test_rtd_override(app: Sphinx, monkeypatch):
    monkeypatch.setenv("READTHEDOCS", "True")
    app.config.html_baseurl = "https://failure.com"

    app.build()
    tags = conftest._og_meta_tags(app)

    assert get_tag_content(tags, "url") == "http://example.org/index.html"


@pytest.mark.sphinx("html", testroot="rtd-default")
def test_rtd_valid(app: Sphinx, monkeypatch):
    monkeypatch.setenv("READTHEDOCS", "True")
    app.config.html_baseurl = "https://failure.com"

    app.build()
    tags = conftest._og_meta_tags(app)

    assert get_tag_content(tags, "url") == "https://failure.com/index.html"


# use rtd-default, as we are not changing configuration, but RTD variables
@pytest.mark.sphinx("html", testroot="rtd-invalid")
def test_rtd_invalid(app: Sphinx, monkeypatch):
    monkeypatch.setenv("READTHEDOCS", "True")
    app.config.html_baseurl = None

    with pytest.raises(Exception):
        app.build()
