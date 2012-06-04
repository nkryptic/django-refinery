==============================
Installation and configuration
==============================

.. _installing-the-package:

Installing the Python package
=============================

To install django-refinery the ``refinery`` package must be added to
the Python path.  You can install the latest stable version directly
from PyPI using pip or easy_install::

    pip install --upgrade django-refinery

If you want to install development version (unstable), you can do so doing::

    pip install django-refinery==dev

You can also install directly from source.  Download either the latest
stable version from pypi_ or any release from github_, or use git to
get the development code::

    $ git clone https://github.com/nkryptic/django-refinery.git

.. _pypi: http://pypi.python.org/pypi/django-refinery/
.. _github: http://github.com/nkryptic/django-refinery

Then install the package by running the setup script::

    $ cd django-refinery
    $ python setup.py install


.. _installing-the-application:

Configuring Django
==================

After installing django-refinery, add the ``refinery`` application to
your ``INSTALLED_APPS`` in the settings.py of your project::

    INSTALLED_APPS = [
        ...
        'refinery',
        ...
    ]


