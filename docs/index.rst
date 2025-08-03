===================
sphinxext-opengraph
===================

.. toctree::
   :hidden:

   socialcards

.. role:: code-py(code)
   :language: Python

Sphinx extension to generate `Open Graph metadata`_ for your documentation.


Installation
============

.. code-block:: sh

   python -m pip install sphinxext-opengraph

The ``matplotlib`` package is required to generate social cards:

.. code-block:: sh

   python -m pip install sphinxext-opengraph[social_cards]


Usage
=====

Add ``sphinxext.opengraph`` to the extensions list in ``conf.py``:

.. code-block:: python

   extensions = [
      'sphinxext.opengraph',
   ]

Then set the :confval:`!ogp_site_url` configuration value
to the public URL for your documentation, e.g.:

.. code-block:: python

   ogp_site_url = 'https://docs.example.org/'

.. tip::
   Documentation hosted on Read The Docs automatically detects the site URL
   through the :envvar:`!READTHEDOCS_CANONICAL_URL` environment variable,
   so no configuration is needed.


Options
=======

These values are placed in the ``conf.py`` of your Sphinx project.

.. confval:: ogp_site_url
   :type: :code-py:`str`
   :default: :code-py:`''`

   This config option is important, set it to the URL the site is being hosted on.

.. confval:: ogp_description_length
   :type: :code-py:`int`
   :default: :code-py:`200`

   Configure the number of characters taken from a page.

.. confval:: ogp_site_name
   :type: :code-py:`str | Literal[False]`
   :default: :confval:`!project`

   Name of the site.
   This is displayed above the title.
   Defaults to the :confval:`!project` config value.
   Set to ``False`` to unset and use no default.

.. confval:: ogp_social_cards
   :type: :code-py:`dict[str, bool | str]`
   :default: :code-py:`{}`

   Configuration for automatically creating social media card PNGs for each page.
   See :doc:`the social media cards <socialcards>` page for more information.

.. confval:: ogp_image
   :type: :code-py:`str | None`
   :default: :code-py:`None`

   Link to image to show.
   Note that all relative paths are converted to be relative to
   the root of the HTML output as defined by :confval:`!ogp_site_url`.

.. confval:: ogp_image_alt
   :type: :code-py:`str | Literal[False]`
   :default: :code-py:`None`

   Alt text for image.
   Defaults to using :confval:`!ogp_site_name` or the document's title as alt text,
   if available.
   Set to ``False`` to disable alt text.

.. confval:: ogp_use_first_image
   :type: :code-py:`bool`
   :default: :code-py:`False`

   Set to ``True`` to use each page's first image, if available.
   If set to ``True`` but no image is found, Sphinx will use :confval:`!ogp_image` instead.

.. confval:: ogp_type
   :type: :code-py:`str`
   :default: :code-py:`'website'`

   This sets the ogp type attribute.
   For more information on the types available, see at https://ogp.me/#types.
   By default, it is set to ``website``, which should be fine for most use cases.

.. confval:: ogp_custom_meta_tags
   :type: :code-py:`Sequence[str]`
   :default: :code-py:`()`

   List of custom HTML snippets to insert.

.. confval:: ogp_enable_meta_description
   :type: :code-py:`bool`
   :default: :code-py:`True`

   When ``True``, generates ``<meta name="description" content="...">`` from the page.

.. confval:: ogp_canonical_url
   :type: :code-py:`str`
   :default: :confval:`!ogp_site_url`

   This option can be used to override the "canonical" URL for the page,
   and is used for ``og:url`` and the URL text in generated social media preview cards.
   It is most useful with versioned documentation, where you intend
   to set the "stable" or "latest" version as the canonical location of each page,
   similarly to ``rel="canonical"``.
   If not set, the option defaults to the value of :confval:`!ogp_site_url`.


Example Config
==============

Simple Config
-------------

.. code-block:: python

   ogp_site_url = "http://example.org/"
   ogp_image = "http://example.org/image.png"

Advanced Config
---------------

.. code-block:: python

   ogp_site_url = "http://example.org/"
   ogp_image = "http://example.org/image.png"
   ogp_description_length = 300
   ogp_type = "article"

   ogp_custom_meta_tags = [
       '<meta property="og:ignore_canonical" content="true" />',
   ]

   ogp_enable_meta_description = True


Per Page Overrides
==================

`Field lists`_ can be used to override certain settings on each page
and set unsupported arbitrary Open Graph tags.

Make sure you place the fields at the very start of the document
such that Sphinx will pick them up and also won't build them into the HTML.

Overrides
---------

These are some overrides that can be used on individual pages,
you can actually override any tag and field lists will always take priority.

``:ogp_description_length:``
  Configure the amount of characters to grab for the description of the page.
  If the value isn't a number it will fall back to ``ogp_description_length``.

``:ogp_disable:``
  Disables generation of Open Graph tags on the page.

``:og:description:``
  Lets you override the description of the page.

``:description:`` or ``.. meta:: :description:``
  Sets the ``<meta name="description" content="...">`` description.

``:og:title:``
  Lets you override the title of the page.

``:og:type:``
  Override the type of the page.
  For the list of available types, see at https://ogp.me/#types.

``:og:image:``
  Set the image for the page.

  **Note: Relative file paths for images, videos and audio
  are currently not supported when using field lists.
  Please use an absolute path instead.**

``:og:image:alt:``
  Sets the alt text. Will be ignored if there is no image set.

Example
-------

Remember that the fields **must** be placed at the very start of the file.
You can verify Sphinx has picked up the fields if they aren't shown
in the final HTML file.

.. code-block:: rst

   :og:description: New description
   :og:image: http://example.org/image.png
   :og:image:alt: Example Image

   Page contents
   =============

Arbitrary Tags
--------------

Additionally, you can use field lists to add any arbitrary Open Graph tag
not supported by the extension.
The syntax for arbitrary tags is the same with ``:og:tag: content``.

For example:

.. code-block:: rst

   :og:video: http://example.org/video.mp4

   Page contents
   =============

**Note: Relative file paths for images, videos and audio
are currently not supported when using field lists.
Please use an absolute path instead.**

.. _Open Graph metadata: https://ogp.me/
.. _Field lists: https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html
