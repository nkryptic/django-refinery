===============
django-refinery
===============

Allows users to filter down a queryset based on a model's fields, similar
to the Django admin's ``list_filter`` interface.  A ``FilterTool`` helper
class is provided, which will (by default) map filters to model fields and
create a form for queryset manipulation.  The helper class interface will
feel familiar to anyone who's used a Django ``ModelForm``.

User Guide
==========

.. toctree::
   :maxdepth: 2
   
   install
   usage
   advanced-usage
   components
   customizing
   integration
   migration
   troubleshooting


API Reference
=============

.. toctree::
   :maxdepth: 2
   
   ref/filtertool
   ref/filters
   ref/fields
   ref/widgets


Developer Guide
===============

.. toctree::
   :maxdepth: 2
   
   contributing

.. contributing 1
   - setup
   -- fork
   -- clone
   - setup topic branch
   - generate pull request
   - pull from upstream often
   - how to get your request accepted
   -- run the tests
   -- add tests
   -- don't mix code changes/code cleanup/doc changes
   -- keep pull request simple/single issue
   -- keep code simple
   contributing 2
   - setting up an environment
   - running the test suite
   - contributing back code
   contributing 3
   - Community
   - In a nutshell
   - Contributing Code
   -- Getting the source code
   -- Syntax and conventions
   -- Process
   -- Tests
   -- Running the tests
   - Contributing Documentation


.. Miscellaneous
   =============

Project Info
============

.. toctree::
   :maxdepth: 2
   
   history
   changes
   license


