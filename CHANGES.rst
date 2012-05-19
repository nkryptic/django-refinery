Version 0.1 (2012-05-19)
------------------------

* Initial version of django-refinery (extracted from django-filter_ v0.5.3).

* Converted all original doctests to unittests.

* Merged the work of various forks of django-filter_ to add a lot of new 
  functionality (with source at the end):
  
  - Filtering logic refactored to use Q objects instead of QuerySets (from
    the `django-qfilters`_ project by `Steve Yeago`_).
  
  - Added ability to specify lookup type in FilterSet meta class
    (`Maurizio Melani`_).
  
  - Allow to ovveride form and form fields creation (`Marke Wywial`_ via 
    `I-DOTCOM LLC`_).
  
  - Add Class-based generic view (`Alisue`_).
  
  - Add empty_label for ChoiceFilter (`Vladislav Poluhin`_).
  
  - Allow order_by to take a list of lists (or tuples), letting you override
    the display name of potential ordering columns. (`Ross Poulton`_).
  
  - Altered test model definitions for field inheritance tests, added inherited
    field definition for testing, made filters work with inherited fields,
    added open range filters, added date and time range fields, and added 
    support for derived model fields (`Sergiy Kuzmenko`_).
  
  - Document how to use alongside `django-pagination`_, fixed problem where 
    blank choice was not clearing the query variable, and added ability for 
    LinkWidget to accept (None,"Label") element for choices tuple which clears
    the given filter (`Richard Barran`_).
  
  - Filter instance queryset is directly subscriptable andadded multi-field
    filter (`Stephan Jaekel`_).
  
  - Reversed position of field and lookupfield and added the ability to 
    provide 'pretty' options for lookup types (`Tino de Bruijn`_).


.. _`django-filter`: https://github.com/alex/django-filter
.. _`django-qfilters`: https://github.com/subsume/django-qfilters
.. _`Steve Yeago`: https://github.com/subsume
.. _`Alisue`: https://github.com/lambdaalisue
.. _`Stephan Jaekel`: https://github.com/stephrdev
.. _`Marke Wywial`: https://github.com/onjin
.. _`I-DOTCOM LLC`: https://github.com/i-dotcom
.. _`Vladislav Poluhin`: https://github.com/midiotthimble
.. _`Ross Poulton`: https://github.com/rossp
.. _`Sergiy Kuzmenko`: https://github.com/shelldweller
.. _`Tino de Bruijn`: https://github.com/tino
.. _`Richard Barran`: https://github.com/richardbarran
.. _`Maurizio Melani`: https://github.com/gislab
.. _`django-pagination`: https://github.com/ericflo/django-pagination
