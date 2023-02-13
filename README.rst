Astro
=====

Astro is an open-sourced, in-house bot designed for the needs of the interactions.py Discord support server. We've built this bot off of our own library.

Features
********

Some of the features Astro has include:

- "Tag" commands for storing text prompts, followed by fuzzy matched autocompletion.
- Moderation commands for kicking, banning, timeouts and other conventional channel tools.
- GitHub embed rendering of Pull Requests, Issues and commit hash logs.

Setup
*****

Setting up this bot is simple.

First, clone this repository. Then, in order to install any dependencies that the bot uses, please run this command in the root namespace of the cloned repository:


.. code-block:: bash

  pip install -U -r requirements.txt

Astro requires a ``.env`` file that contains sensitive information, like your bot token. In particular, it is looking for a file in this format:

.. code-block:: bash

  TOKEN="Your bot token."
  MONGO_DB_URL="A url pointing to a MongoDB database. You can create one for free on the MongoDB website, or run one yourself."

``metadata.yml`` will also likely need to be changed for your needs. The configuration on this repository is for the interactions.py server - you will need to change the IDs of each entry to the appropriate channels, roles, and tags in your server.

Finally, running the bot is as simple as:

.. code-block:: bash

  python bot.py

.. _interactions.py: https://discord.gg/interactions
