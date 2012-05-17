Running the django-refinery tests
=================================

In order to run the django-refinery tests you must not only add
``'refinery'`` to your ``INSTALLED_APPS`` settings, but also
``'tests'``, which tells Django to setup the test models.  This
step is only necessary if you want to run the django-refinery regression tests.
