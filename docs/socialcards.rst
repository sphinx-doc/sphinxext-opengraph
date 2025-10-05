Social media card images
========================

This extension may create and reference a PNG file on the HTML pages, meant for sharing
documentation links on social media platforms (both "feed-based" and "chat-based" social
networks tend to use this). These cards display metadata about the page that you link
to.

This extension will automatically setup such social media card images for each page of
your documentation, using one of 3 possible setups:

- If you have set up an image manually using ``ogp_use_first_image`` or ``ogp_image``,
  that image will be used as the social media card image.
- Otherwise, you may define a callback function to generate a custom PNG image for each
  page (see below).
- If neither of the above are set, and matplotlib is installed, a default social media card
  image will be generated for each page, using the page title and other metadata.

Custom image callback
---------------------

In conf.py, connect a custom function to the ``ogp_social_card_callback`` event:

.. code-block:: python
   :caption: conf.py

   def setup(app):
      app.connect("generate-social-card", my_custom_generate_card_function)


Then implement the function as follows:

.. code-block:: python

   from sphinxext.opengraph import SocialCardContents

   def generate_card(
      app: Sphinx,
      contents: SocialCardContents,
      check_if_signature_exists: typing.Callable[[str], None],
   ) -> None | tuple[io.BytesIO, str]:
      """Generate a social media card image for the current page.

      Parameters
      ----------
      app : Sphinx
            The Sphinx application object.
      contents : SocialCardContents
            An object containing metadata about the current page.
            Contains the following attributes:
            - site_name : str - the name of the site
            - site_url : str - the base URL of the site
            - page_title : str - the title of the page
            - description : str - the description of the page
            - html_logo : Path | None - the path to the logo image, if set
            - page_path : Path - the path to the current page file
      check_if_signature_exists : Callable[[str], None]
            A callable to check if a social card image has already been generated for
            the current page. This is useful to avoid regenerating an image that
            already exists.
      Returns
      -------
      None or tuple[io.BytesIO, str]
            If None is returned, the default image generation will be used.
            Otherwise, return a tuple containing:
            - An io.BytesIO object containing the image PNG bytes.
            - A string whose hash will be included in the image filename to ensure
              the image is updated when the content changes (because social media platforms
              often cache images aggressively).
      """

      signature = f"{contents.page_title}-{contents.description}"
      check_if_signature_exists(signature)

      # Generate image bytes here
      image_bytes = io.BytesIO(...)
      # ... generate image and write to image_bytes ...
      return image_bytes, signature

You may want to explore different libraries to generate images, such as Pillow, Matplotlib,
html2image, or others.

Default social media card images (with matplotlib)
--------------------------------------------------

Default image generation uses additional third-party libraries, so you need to install
the extension with the **social_cards** extra:

.. code-block:: console

   pip install 'sphinxext-opengraph[social_cards]'

See `the opengraph.xyz website`__ for a way to preview what your social media cards look like.
Here's an example of what the card for this page looks like:

.. image:: ./tmp/num_0.png
   :width: 500

__ https://www.opengraph.xyz/

Default image generation also uses specific configuration options, which you can set in
your ``conf.py`` file as a dictionnary assigned to the ``ogp_social_cards`` variable.

Here are the available options and their default values:

.. code-block:: python
   :caption: conf.py

   ogp_social_cards = {
         # If False, disable social card images
         "enable": True,
         # If set, use this URL as the site URL instead of the one inferred from the config
         "override_site_url": None,

         # Color overides, in hex format or named colors
         "page_title_color": "#2f363d",
         "description_color": "#585e63",
         "site_title_color": "#585e63",
         "site_url_color": "#2f363d",
         "line_color": "#5a626b",
         "background_color": "white",

         # Font override. If not set, use Roboto Flex (vendored in _static)
         "font": None,

         # Image override, if not set, use html_logo
         # You may set it as a string path or a Path object
         # Note: neither this image not the image_mini may be an SVG file
         "image": None,

         # Mini-image appears at the bottom-left of the card
         # If not set, use the Sphinx logo
         # You may set it as a string path or a Path object
         "image_mini": "...",

         # Maximum length of the description text (in characters) before truncation
         "description_max_length": 140,

   }

Customize the text font
^^^^^^^^^^^^^^^^^^^^^^^

By default, the Roboto Flex font is used to render the card text.

You can specify the other font name via ``font`` key:

.. code-block:: python
   :caption: conf.py

   ogp_social_cards = {
       "font": "Noto Sans CJK JP",
   }

You can also use a font from a file by specifying the full path to the font file:

.. code-block:: python
   :caption: conf.py

   from matplotlib import font_manager

   font_path = 'font-file.ttf'  # Your font path goes here
   font_manager.fontManager.addfont(font_path)

   ogp_social_cards = {
       "font": "font name",
   }

You might need to install an additional font package on your environment. Also, note
that the font name needs to be discoverable by Matplotlib FontManager. See `Matplotlib
documentation`__ for the information about FontManager.

__ https://matplotlib.org/stable/tutorials/text/text_props.html#default-font

Example social cards
^^^^^^^^^^^^^^^^^^^^

Below are several social cards to give an idea for how this extension behaves with
different length and size of text.

.. include:: ./tmp/embed.txt
