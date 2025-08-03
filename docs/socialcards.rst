Social media card images
========================

This extension will automatically generate a PNG meant for sharing documentation links on social media platforms.
These cards display metadata about the page that you link to, and are meant to catch the attention of readers.

See `the opengraph.xyz website`__ for a way to preview what your social media cards look like.
Here's an example of what the card for this page looks like:

.. image:: ./tmp/num_0.png
   :width: 500

__ https://www.opengraph.xyz/

Disable card images
-------------------

To disable social media card images, use the following configuration:

.. code-block:: python
   :caption: conf.py

   ogp_social_cards = {
       "enable": False
   }

Update the top-right image
--------------------------

By default the top-right image will use the image specified by ``html_logo`` if it exists.
To update it, specify another path in the **image** key like so:

.. code-block:: python
   :caption: conf.py

   ogp_social_cards = {
       "image": "path/to/image.png",
   }

.. warning::

   The image cannot be an SVG

   Matplotlib does not support easy plotting of SVG images,
   so ensure that your image is a PNG or JPEG file, not SVG.

Customize the text font
-----------------------

By default, the Roboto Flex font is used to render the card text.

You can specify the other font name via ``font`` key:

.. code-block:: python
   :caption: conf.py

   ogp_social_cards = {
       "font": "Noto Sans CJK JP",
   }

You might need to install an additional font package on your environment. Also, note that the font name needs to be
discoverable by Matplotlib FontManager.
See `Matplotlib documentation`__
for the information about FontManager.

__ https://matplotlib.org/stable/tutorials/text/text_props.html#default-font

Customize the card
------------------

There are several customization options to change the text and look of the social media preview card.
Below is a summary of these options.

- **site_url**: Set a custom site URL.
- **line_color**: Colour of the border line at the bottom of the card, in hex format.

Example social cards
--------------------

Below are several social cards to give an idea for how this extension behaves with different length and size of text.

.. include:: ./tmp/embed.txt
