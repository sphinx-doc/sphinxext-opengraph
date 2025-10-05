from __future__ import annotations

import dataclasses
import functools
import hashlib
import logging
import os
import posixpath
import struct
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit

from docutils import nodes

from sphinxext.opengraph._description_parser import get_description
from sphinxext.opengraph._meta_parser import get_meta_description
from sphinxext.opengraph._title_parser import get_title

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)

if TYPE_CHECKING:
    import io
    from typing import Any, Callable

    from sphinx.application import Sphinx
    from sphinx.builders import Builder
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import ExtensionMetadata


__version__ = '0.13.0'
version_info = (0, 13, 0)

LOGGER = logging.getLogger(__name__)
DEFAULT_DESCRIPTION_LENGTH = 200


# A selection from https://www.iana.org/assignments/media-types/media-types.xhtml#image
IMAGE_MIME_TYPES = {
    'gif': 'image/gif',
    'apng': 'image/apng',
    'webp': 'image/webp',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'bmp': 'image/bmp',
    'heic': 'image/heic',
    'heif': 'image/heif',
    'tiff': 'image/tiff',
}


@functools.cache
def get_file_contents_hash(file_path: Path) -> str:
    """Get a hash of the contents of a file."""
    hasher = hashlib.sha1(usedforsecurity=False)
    with file_path.open('rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()[:8]


class PNGFormatError(Exception):
    """Raised when a PNG file is invalid."""


def get_png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    try:
        w, h = struct.unpack('>LL', png_bytes[16:24])
        width = int(w)
        height = int(h)
    except struct.error as exc:
        raise PNGFormatError from exc
    return width, height


@dataclasses.dataclass
class SocialCardContents:
    """Parameters for generating a social card.

    Received by the `generate-social-card` event.
    """

    site_name: str
    site_url: str
    page_title: str
    description: str
    html_logo: Path | None
    page_path: Path

    @property
    def signature(self) -> str:
        """A string that uniquely identifies the contents of this social card.

        Used to avoid regenerating cards unnecessarily.
        """
        return f'{self.site_name}{self.page_title}{self.description}{self.site_url}{get_file_contents_hash(self.html_logo) if self.html_logo else ""}'


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document,
) -> None:
    if app.builder.name == 'epub':
        return

    if doctree:
        context['metatags'] += get_tags(
            context,
            doctree,
            srcdir=app.srcdir,
            outdir=app.outdir,
            config=app.config,
            builder=app.builder,
            env=app.env,
        )


def get_tags(
    context: dict[str, Any],
    doctree: nodes.document,
    *,
    srcdir: str | Path,
    outdir: str | Path,
    config: Config,
    builder: Builder,
    env: BuildEnvironment,
) -> str:
    # Get field lists for per-page overrides
    fields = context['meta']
    if fields is None:
        fields = {}

    if 'ogp_disable' in fields:
        return ''

    tags = {}
    meta_tags = {}  # For non-og meta tags

    # Set length of description
    try:
        desc_len = int(
            fields.get('ogp_description_length', config.ogp_description_length)
        )
    except ValueError:
        desc_len = DEFAULT_DESCRIPTION_LENGTH

    # Get the title and parse any html in it
    title, title_excluding_html = get_title(context['title'])

    # Parse/walk doctree for metadata (tag/description)
    description = get_description(doctree, desc_len, {title, title_excluding_html})

    # title tag
    tags['og:title'] = title

    # type tag
    tags['og:type'] = config.ogp_type

    if not config.ogp_site_url and os.getenv('READTHEDOCS'):
        ogp_site_url = ambient_site_url()
    else:
        ogp_site_url = config.ogp_site_url

    # If ogp_canonical_url is not set, default to the value of ogp_site_url
    ogp_canonical_url = config.ogp_canonical_url or ogp_site_url

    # url tag
    # Get the URL of the specific page
    page_url = urljoin(ogp_canonical_url, builder.get_target_uri(context['pagename']))
    tags['og:url'] = page_url

    # site name tag, False disables, default to project if ogp_site_name not
    # set.
    if config.ogp_site_name is False:
        site_name = ''
    elif config.ogp_site_name is None:
        site_name = config.project
    else:
        site_name = config.ogp_site_name
    if site_name:
        tags['og:site_name'] = site_name

    # description tag
    if description:
        tags['og:description'] = description

        if config.ogp_enable_meta_description and not get_meta_description(
            context['metatags']
        ):
            meta_tags['description'] = description

    # image tag
    # Get basic values from config
    if 'og:image' in fields:
        image_url = fields['og:image']
        ogp_use_first_image = False
        ogp_image_alt = fields.get('og:image:alt')
        fields.pop('og:image', None)
    else:
        image_url = config.ogp_image
        ogp_use_first_image = config.ogp_use_first_image
        ogp_image_alt = fields.get('og:image:alt', config.ogp_image_alt)

    # Decide whether to generate a social media card image.
    # Only do this as a fallback if the user hasn't given any configuration
    # to add another image.

    if not (image_url or ogp_use_first_image):
        image_path = social_card_for_page(
            app=builder.app,
            site_name=site_name,
            page_title=title,
            description=fields.get('og:description', description),
            page_path=Path(context['pagename']),
            site_url=ogp_canonical_url,
            config=config,
        )

        if image_path:
            image_url = posixpath.join(ogp_site_url, image_path.as_posix())

            ogp_use_first_image = False

            # Alt text is taken from description unless given
            if 'og:image:alt' in fields:
                ogp_image_alt = fields.get('og:image:alt')
            else:
                ogp_image_alt = description

            try:
                width, height = get_png_dimensions((outdir / image_path).read_bytes())
            except PNGFormatError as exc:
                LOGGER.warning('Could not get dimensions of social card: %s', exc)
            else:
                tags['og:image:width'] = f'{width}'
                tags['og:image:height'] = f'{height}'
            meta_tags['twitter:card'] = 'summary_large_image'

    fields.pop('og:image:alt', None)

    first_image = None
    if ogp_use_first_image:
        # Use the first image that is defined in the current page
        first_image = doctree.next_node(nodes.image)
        if (
            first_image
            and Path(first_image.get('uri', '')).suffix[1:].lower() in IMAGE_MIME_TYPES
        ):
            image_url = first_image['uri']
            ogp_image_alt = first_image.get('alt', None)
        else:
            first_image = None

    if image_url:
        # temporarily disable relative image paths with field lists
        if 'og:image' not in fields:
            image_url_parsed = urlparse(image_url)
            if not image_url_parsed.scheme:
                # Relative image path detected, relative to the source. Make absolute.
                if first_image:  # NoQA: SIM108
                    root = page_url
                else:  # ogp_image is set
                    # ogp_image is defined as being relative to the site root.
                    # This workaround is to keep that functionality from breaking.
                    root = ogp_site_url

                image_url = urljoin(root, image_url_parsed.path)
            tags['og:image'] = image_url

        # Add image alt text (either provided by config or from site_name)
        if isinstance(ogp_image_alt, str):
            tags['og:image:alt'] = ogp_image_alt
        elif ogp_image_alt is None and site_name:
            tags['og:image:alt'] = site_name
        elif ogp_image_alt is None and title:
            tags['og:image:alt'] = title

    # arbitrary tags and overrides
    tags.update({k: v for k, v in fields.items() if k.startswith('og:')})

    return (
        '\n'.join(
            [make_tag(p, c) for p, c in tags.items()]
            + [make_tag(p, c, 'name') for p, c in meta_tags.items()]
            + list(config.ogp_custom_meta_tags)
        )
        + '\n'
    )


def ambient_site_url() -> str:
    # readthedocs addons sets the READTHEDOCS_CANONICAL_URL variable
    if rtd_canonical_url := os.getenv('READTHEDOCS_CANONICAL_URL'):
        parse_result = urlsplit(rtd_canonical_url)
    else:
        msg = 'ReadTheDocs did not provide a valid canonical URL!'
        raise RuntimeError(msg)

    # Grab root url from canonical url
    return urlunsplit(
        (parse_result.scheme, parse_result.netloc, parse_result.path, '', '')
    )


class CardAlreadyExistsError(Exception):
    """Raised when a social card already exists."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f'Card already exists: {path}')


def social_card_for_page(
    *,
    app: Sphinx,
    site_name: str,
    page_title: str,
    description: str,
    page_path: Path,
    config: Config,
    site_url: str,
) -> Path | None:
    contents = SocialCardContents(
        site_name=site_name,
        site_url=site_url.split('://')[-1],
        page_title=page_title,
        description=description,
        page_path=page_path,
        html_logo=(app.srcdir / Path(config.html_logo)) if config.html_logo else None,
    )

    image_bytes: io.BytesIO
    signature: str

    outdir = Path(app.outdir)

    # First callback to return a BytesIO object wins
    try:
        result = app.emit_firstresult(
            'generate-social-card',
            contents,
            functools.partial(check_if_signature_exists, outdir, page_path),
            allowed_exceptions=(CardAlreadyExistsError,),
        )
    except CardAlreadyExistsError as exc:
        return exc.path

    if result is None:
        return None

    image_bytes, signature = result

    path_to_image = get_path_for_signature(page_path=page_path, signature=signature)

    # Save the image to the output directory
    absolute_path = outdir / path_to_image
    absolute_path.parent.mkdir(exist_ok=True, parents=True)
    absolute_path.write_bytes(image_bytes.getbuffer())

    # Link the image in our page metadata
    return path_to_image


def hash_str(data: str) -> str:
    return hashlib.sha1(data.encode(), usedforsecurity=False).hexdigest()[:8]


def get_path_for_signature(page_path: Path, signature: str) -> Path:
    """Get a path for a social card image based on the page path and hash."""
    return (
        Path('_images')
        / 'social_previews'
        / f'summary_{str(page_path).replace("/", "_")}_{hash_str(signature)}.png'
    )


def check_if_signature_exists(outdir: Path, page_path: Path, signature: str) -> None:
    """Check if a file with the given hash already exists.

    This is used to avoid regenerating social cards unnecessarily.
    """
    relative_path = get_path_for_signature(page_path=page_path, signature=signature)
    path = outdir / relative_path
    if path.exists():
        raise CardAlreadyExistsError(path=relative_path)


def create_social_card_matplotlib_fallback(
    app: Sphinx,
    contents: SocialCardContents,
    check_if_signature_exists: Callable[[str], None],
) -> None | tuple[io.BytesIO, str]:
    try:
        from sphinxext.opengraph._social_cards_matplotlib import create_social_card
    except ImportError as exc:
        # Ideally we should raise and let people who don't want the card explicitly
        # disable it, but this would be a breaking change.
        LOGGER.warning(
            'matplotlib is not installed, social cards will not be generated: %s', exc
        )
        return None

    # Plot an image with the given metadata to the output path
    return create_social_card(
        app=app, contents=contents, check_if_signature_exists=check_if_signature_exists
    )


def make_tag(property: str, content: str, type_: str = 'property') -> str:
    # Parse quotation, so they won't break html tags if smart quotes are disabled
    content = content.replace('"', '&quot;')
    return f'<meta {type_}="{property}" content="{content}" />'


def setup(app: Sphinx) -> ExtensionMetadata:
    # ogp_site_url="" allows relative by default, even though it's not
    # officially supported by OGP.
    app.add_config_value('ogp_site_url', '', 'html', types=frozenset({str}))
    app.add_config_value('ogp_canonical_url', '', 'html', types=frozenset({str}))
    app.add_config_value(
        'ogp_description_length',
        DEFAULT_DESCRIPTION_LENGTH,
        'html',
        types=frozenset({int}),
    )
    app.add_config_value('ogp_image', None, 'html', types=frozenset({str, NoneType}))
    app.add_config_value(
        'ogp_image_alt', None, 'html', types=frozenset({str, bool, NoneType})
    )
    app.add_config_value('ogp_use_first_image', False, 'html', types=frozenset({bool}))
    app.add_config_value('ogp_type', 'website', 'html', types=frozenset({str}))
    app.add_config_value(
        'ogp_site_name', None, 'html', types=frozenset({str, bool, NoneType})
    )
    app.add_config_value(
        'ogp_social_cards', None, 'html', types=frozenset({dict, NoneType})
    )
    app.add_config_value(
        'ogp_custom_meta_tags', (), 'html', types=frozenset({list, tuple})
    )
    app.add_config_value(
        'ogp_enable_meta_description', True, 'html', types=frozenset({bool})
    )

    # Main Sphinx OpenGraph linking
    app.connect('html-page-context', html_page_context)

    # Register event for customizing social card generation
    app.add_event(name='generate-social-card')
    # Add our matplotlib fallback, but with a low priority so that other
    # extensions can override it.
    # (default priority is 500, functions with lower priority numbers are called first).
    app.connect(
        'generate-social-card',
        create_social_card_matplotlib_fallback,
        priority=1000,
    )

    return {
        'version': __version__,
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
