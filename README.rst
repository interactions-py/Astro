=====
Astro
=====

**🔎 Utilities made easy.**

----

**Astro** is the main bot powering moderation and other utilities in the `interactions.py`_ support server. The goal of Astro is to make searching simple, and automate our moderation process. Whether that's creating tags with autocompleted suggestions, code examples, or interactive tutorials: Astro has you covered. Interactions should be simple to understand, and coding them is no different.

This project is built with **interactions.py**, the no. 1 leading Python interactions library that empowers bots with the ability to implement slash commands and components with ease. The codebase of this bot reflects how simple, modular and scalable the library is---staying true to the motto of what it does.

Setup
************
Setting up this bot is simple. First, clone this repository. Then, in order to install any dependencies that the bot uses, please run this command in the root namespace of the cloned repository:

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
