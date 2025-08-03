"""A helper script to test out what social previews look like.

I should remove this when I'm happy with the result.
"""

# %load_ext autoreload
# %autoreload 2

from __future__ import annotations

import random
from pathlib import Path

from sphinxext.opengraph._social_cards import (
    MAX_CHAR_DESCRIPTION,
    MAX_CHAR_PAGE_TITLE,
    create_social_card_objects,
    render_social_card,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Dummy lorem text
lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum""".split()  # NoQA: SIM905

kwargs_fig = {
    'image': PROJECT_ROOT / 'docs/_static/og-logo.png',
    'image_mini': PROJECT_ROOT / 'sphinxext/opengraph/_static/sphinx-logo-shadow.png',
}

print('Generating previews of social media cards...')
plt_objects = create_social_card_objects(**kwargs_fig)
grid_items = []
for perm in range(20):
    # Create dummy text description and pagetitle for this iteration
    random.shuffle(lorem)
    title = ' '.join(lorem[:100])
    title = title[: MAX_CHAR_PAGE_TITLE - 3] + '...'

    random.shuffle(lorem)
    desc = ' '.join(lorem[:100])
    desc = desc[: MAX_CHAR_DESCRIPTION - 3] + '...'

    path_tmp = Path(PROJECT_ROOT / 'docs/tmp')
    path_tmp.mkdir(exist_ok=True)
    path_out = Path(path_tmp / f'num_{perm}.png')

    plt_objects = render_social_card(
        path=path_out,
        site_title='Sphinx Social Card Demo',
        page_title=title,
        description=desc,
        siteurl='sphinxext-opengraph.readthedocs.io',
        plt_objects=plt_objects,
    )

    path_examples_page_folder = PROJECT_ROOT / 'docs' / 'tmp'
    grid_items.append(f"""\
   .. grid-item::

      .. image:: ./tmp/{path_out.name}
""")

embed_text = '.. grid:: 2\n   :gutter: 5\n\n' + '\n'.join(grid_items)

# Write text that we can use to embed these images in the docs
(PROJECT_ROOT / 'docs/tmp/embed.txt').write_text(embed_text)

print('Done generating previews of social media cards...')
