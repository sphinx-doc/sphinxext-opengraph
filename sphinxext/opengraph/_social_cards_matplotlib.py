"""Build a PNG card for each page meant for social media using matplotlib."""

from __future__ import annotations

import dataclasses
import io
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib as mpl
import matplotlib.font_manager
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from sphinx.util import logging

from . import SocialCardContents

if TYPE_CHECKING:
    from typing import Callable

    from matplotlib.figure import Figure
    from matplotlib.text import Text
    from sphinx.application import Sphinx

    from . import SocialCardContents

mpl.use('agg')

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).parent

DEFAULT_DESCRIPTION_LENGTH = 157
PAGE_TITLE_LENGTH = 80

# Default configuration for the figure style
DEFAULT_KWARGS_FIG = {
    'enable': True,
    'site_url': True,
}


@dataclasses.dataclass
class MatplotlibSocialCardSettings:
    """Configuration for social cards.

    These elements can be set in the `ogp_social_cards` config variable.
    """

    # Some elements accept a broader set of types, but we convert them in `from_config`
    # below.
    enable: bool = True
    override_site_url: str | None = None
    page_title_color: str = '#2f363d'
    description_color: str = '#585e63'
    site_title_color: str = '#585e63'
    site_url_color: str = '#2f363d'
    line_color: str = '#5a626b'
    background_color: str = 'white'
    font: str | None = None  # Defaults to Roboto Flex, vendored in _static
    image: Path | None = None
    image_mini: Path | None = Path(__file__).parent / '_static/sphinx-logo-shadow.png'
    description_max_length: int = DEFAULT_DESCRIPTION_LENGTH

    @classmethod
    def from_values(cls, values: dict) -> MatplotlibSocialCardSettings:
        """Create settings from a config dictionary."""
        if values.get('image'):
            values['image'] = Path(values['image'])

        if values.get('image_mini'):
            values['image_mini'] = Path(values['image_mini'])

        if isinstance(values.get('site_url'), str):
            values['override_site_url'] = values.get('site_url')

        return cls(**values)


@dataclasses.dataclass
class MatplotlibObjects:
    fig: Figure
    txt_site_title: Text
    txt_page_title: Text
    txt_description: Text
    txt_url: Text


def validate_image(path: Path | None) -> Path | None:
    # Validation on the images
    if not path:
        return None

    # If image is an SVG replace it with None
    if path.suffix.lower() == '.svg':
        LOGGER.warning('[Social card] %s cannot be an SVG image, skipping...', path)
        return None

    # If image doesn't exist, throw a warning and replace with none
    if not path.exists():
        LOGGER.warning("[Social card]: %s file doesn't exist, skipping...", path)
        return None

    return path


def truncate(text: str, max_length: int) -> str:
    """Truncate text to a maximum length, adding ellipsis if needed."""
    if len(text) > max_length:
        return text[:max_length].rstrip() + '...'
    return text


def create_social_card(
    *,
    app: Sphinx,
    contents: SocialCardContents,
    check_if_signature_exists: Callable[[str], None],
) -> None | tuple[io.BytesIO, str]:
    """Create a social preview card according to page metadata.

    This uses page metadata and calls a render function to generate the image.
    It also passes configuration through to the rendering function.
    If Matplotlib objects are present in the `app` environment, it reuses them.
    """
    config_social = app.config.ogp_social_cards or {}
    config_social.setdefault('image', contents.html_logo)
    settings = MatplotlibSocialCardSettings.from_values(values=config_social)

    signature = f'{contents.signature}{dataclasses.asdict(settings)}'
    check_if_signature_exists(signature)

    if not settings.enable:
        return None

    settings.image = validate_image(settings.image)
    settings.image_mini = validate_image(settings.image_mini)

    description = truncate(
        text=contents.description, max_length=settings.description_max_length
    )
    page_title = truncate(text=contents.page_title, max_length=PAGE_TITLE_LENGTH)

    # Generate the image and store the matplotlib objects so that we can re-use them
    try:
        plt_objects = app.env.ogp_social_card_plt_objects
    except AttributeError:
        # If objects is None it means this is the first time plotting.
        # Create the figure objects and return them so that we re-use them later.
        plt_objects = create_social_card_objects(settings=settings)

    bytes_obj = io.BytesIO()

    plt_objects = render_social_card(
        bytes_obj=bytes_obj,
        site_title=contents.site_name,
        page_title=page_title,
        description=description,
        site_url=settings.override_site_url or contents.site_url,
        plt_objects=plt_objects,
    )
    app.env.ogp_social_card_plt_objects = plt_objects

    return bytes_obj, signature


def render_social_card(
    bytes_obj: io.BytesIO,
    site_title: str,
    page_title: str,
    description: str,
    site_url: str,
    plt_objects: MatplotlibObjects,
) -> MatplotlibObjects:
    """Render a social preview card with Matplotlib and write to disk."""
    # Update the matplotlib text objects with new text from this page
    plt_objects.txt_site_title.set_text(site_title)
    plt_objects.txt_page_title.set_text(page_title)
    plt_objects.txt_description.set_text(description)
    plt_objects.txt_url.set_text(site_url)

    # Save the image
    plt_objects.fig.savefig(bytes_obj, facecolor=None)
    return plt_objects


def create_social_card_objects(
    settings: MatplotlibSocialCardSettings,
) -> MatplotlibObjects:
    """Create the Matplotlib objects for the first time."""
    # If no font specified, load the Roboto Flex font as a fallback
    font = settings.font
    if font is None:
        path_font = Path(__file__).parent / '_static/Roboto-Flex.ttf'
        roboto_font = matplotlib.font_manager.FontEntry(
            fname=str(path_font), name='Roboto Flex'
        )
        matplotlib.font_manager.fontManager.addfont(path_font)
        font = roboto_font.name

    # Because Matplotlib doesn't let you specify figures in pixels, only inches
    # This `multiple` results in a scale of about 1146px by 600px
    # Which is roughly the recommended size for OpenGraph images
    # ref: https://opengraph.xyz
    ratio = 1200 / 628
    multiple = 6
    fig = plt.figure(figsize=(ratio * multiple, multiple))
    fig.set_facecolor(settings.background_color)

    # Text axis
    axtext = fig.add_axes((0, 0, 1, 1))

    # Image axis
    ax_x, ax_y, ax_w, ax_h = (0.65, 0.65, 0.3, 0.3)
    axim_logo = fig.add_axes((ax_x, ax_y, ax_w, ax_h), anchor='NE')

    # Image mini axis
    ax_x, ax_y, ax_w, ax_h = (0.82, 0.1, 0.1, 0.1)
    axim_mini = fig.add_axes((ax_x, ax_y, ax_w, ax_h), anchor='NE')

    # Line at the bottom axis
    axline = fig.add_axes((-0.1, -0.04, 1.2, 0.1))

    # Axes configuration
    left_margin = 0.05
    with plt.rc_context({'font.family': font}):
        # Site title
        # Smaller font, just above page title
        site_title_y_offset = 0.87
        txt_site = axtext.text(
            left_margin,
            site_title_y_offset,
            'Test site title',
            {'size': 24},
            ha='left',
            va='top',
            wrap=True,
            c=settings.site_title_color,
        )

        # Page title
        # A larger font for more visibility
        page_title_y_offset = 0.77

        txt_page = axtext.text(
            left_margin,
            page_title_y_offset,
            'Test page title, a bit longer to demo',
            {'size': 46, 'color': 'k', 'fontweight': 'bold'},
            ha='left',
            va='top',
            wrap=True,
            c=settings.page_title_color,
        )

        txt_page._get_wrap_line_width = _set_page_title_line_width  # NoQA: SLF001

        # description
        # Just below site title, smallest font and many lines.
        # Our target length is 160 characters, so it should be
        # two lines at full width with some room to spare at this length.
        description_y_offset = 0.2
        txt_description = axtext.text(
            left_margin,
            description_y_offset,
            (
                'A longer description that we use to ,'
                'show off what the descriptions look like.'
            ),
            {'size': 17},
            ha='left',
            va='bottom',
            wrap=True,
            c=settings.description_color,
        )
        txt_description._get_wrap_line_width = _set_description_line_width  # NoQA: SLF001

        # url
        # Aligned to the left of the mini image
        url_y_axis_ofset = 0.12
        txt_url = axtext.text(
            left_margin,
            url_y_axis_ofset,
            'testurl.org',
            {'size': 22},
            ha='left',
            va='bottom',
            fontweight='bold',
            c=settings.site_url_color,
        )

    if settings.image_mini:
        img = mpimg.imread(settings.image_mini)
        axim_mini.imshow(img)

    # Put the logo in the top right if it exists
    if settings.image:
        img = mpimg.imread(settings.image)
        yw, xw = img.shape[:2]

        # Axis is square and width is longest image axis
        longest = max([yw, xw])
        axim_logo.set_xlim([0, longest])
        axim_logo.set_ylim([longest, 0])

        # Center it on the non-long axis
        xdiff = (longest - xw) / 2
        ydiff = (longest - yw) / 2
        axim_logo.imshow(img, extent=[xdiff, xw + xdiff, yw + ydiff, ydiff])

    # Put a colored line at the bottom of the figure
    axline.hlines(0, 0, 1, lw=25, color=settings.line_color)

    # Remove the ticks and borders from all axes for a clean look
    for ax in fig.axes:
        ax.set_axis_off()

    return MatplotlibObjects(
        fig=fig,
        txt_site_title=txt_site,
        txt_page_title=txt_page,
        txt_description=txt_description,
        txt_url=txt_url,
    )


# These functions are used when creating social card objects to set MPL values.
# They must be defined here otherwise Sphinx errors when trying to pickle them.
# They are dependent on the `multiple` variable defined when the figure is created.
# Because they are depending on the figure size and renderer used to generate them.
def _set_page_title_line_width() -> int:
    return 825


def _set_description_line_width() -> int:
    return 1000
