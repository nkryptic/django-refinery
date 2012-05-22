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
    integration
    history
    changes

..  install
    tutorial
    - ordering
    advanced
    - how it works?
    filters (available)
    views?
    customizing
    - custom filters
    - custom form?
    integration
    migration (from filter)
    history
    changes
    license


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
    
    tests

..  contributing
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
    contributing
    - setting up an environment
    - running the test suite
    - contributing back code
    


