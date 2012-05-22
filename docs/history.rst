======================
Background and credits
======================

About django-refinery
=====================

.. include:: ../AUTHORS.rst
   :end-before: django-refinery Project Leads

In May of 2012, the django-filter project hadn't seen many recent updates
and there were a number of open issues and pull-requests.  There were also 
some changes/fixes in the repository for quite a while, without a new pypi
release, which meant most users just wouldn't see them.  Those reasons,
along with the project's docs being a little thin and offline-only, fed the
decision to create a fork of the project and release separately.

Why change the names?
---------------------

The name django-filter always gave me trouble when trying to search for
more information on the internet.  'Refine' seemed close enough to 'filter'
and 'refinery' seemed like a natural extension and wouldn't have the same
drawback of becoming confused with Django's built-in filtering.

The name for the primary class you manipulate when using django-filter,
``FilterSet``, also made me think.  Is it a set of filters?  Is it a
filtered queryset?  Yes, to both.  But, it also creates and contains the
form needed to manipulate those filters.  So, I went more generic with
``FilterTool``.  I also wanted to get away from people equating it too
closely with a queryset - what I thought a natural conclusion by the name
ending in ``Set``.


Credits
=======

.. include:: ../AUTHORS.rst
   :start-after: <https://github.com/alex>`_.


