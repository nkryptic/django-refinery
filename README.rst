django-refinery
===============

Allows users to filter down a queryset based on a model's fields, similar to
the Django admin's ``list_filter`` interface.  A ``FilterTool`` helper class
is provided, which will (by default) map filters to model fields and create
a form for queryset manipulation.  The helper class supports an interface 
which will feel familiar to anyone who's used a Django ``ModelForm``.

:Author: `Jacob Radford <https://github.com/nkryptic>`_
:Licence: BSD


Example usage
-------------

Given a ``Product`` model you could create a ``FilterTool`` for it with::

    import refinery
    
    class ProductFilterTool(refinery.FilterTool):
        class Meta:
            model = Product
            fields = ['name', 'price']

And then in your view you could do::

    def product_list(request):
        filtertool = ProductFilterTool(request.GET or None)
        return render_to_response('product/product_list.html',
            {'filtertool': filtertool})

And then in your template::

    <form action="" method="get">
        {{ filtertool.form.as_p }}
        <input type="submit" />
    </form>
    <h2>Products</h2>
    <ul>
      {% for obj in filtertool %}
          <li>{{ obj.name }} - ${{ obj.price }}</li>
      {% endfor %}
    </ul>

For more complex usage or custom needs, refer to the project documentation.


Requirements
------------

* Python 2.5+
* Django 1.3+


Installation
------------

* ``pip install -U django-refinery``
* Add ``refinery`` to your ``INSTALLED_APPS``


Documentation
-------------

See the ``docs`` folder or `read it on readthedocs`_ for expanded
information on:

* Usage examples
* Contributing
* Integration with other apps
* Project background
* Low-level API
* Creating custom filters

.. _`read it on readthedocs`: http://django-refinery.rtfd.org


Bugs
----

If you want to help out with the development of django-refinery, by
posting detailed bug reports, proposing new features, or suggesting
documentation improvements, use the `issue tracker`_.  If you want to
fix it yourself, thank you!  `Fork the project`_, make changes and
`send a pull request`_.  Please do create an issue to discuss your plans.

.. _`issue tracker`: http://github.com/nkryptic/django-refinery/issues
.. _`Fork the project`: http://help.github.com/fork-a-repo
.. _`send a pull request`: http://help.github.com/send-pull-requests/


Background
----------

Django-refinery is based on `django-filter`_, an application created
by `Alex Gaynor`_.  For a complete project history and list of contributors,
see the project documentation.

.. _`django-filter`: https://github.com/alex/django-filter
.. _`Alex Gaynor`: https://github.com/alex

Roadmap
-------

* Overhaul and expand documentation
* Overhaul and expand test suite
* Refactor generic class view (look into pagination of ListView)
* Allow integration of django-floppyforms
* Allow integration of django-crispy-forms
* Allow filters on non-required fields with choices to provide
  option of filtering the records that are unset. (i.e. FK is null)
* Allow abstraction of ordering values used to avoid passing internal
  information in GET params (i.e. ``user__username``)
* Look into adapting ``LinkWidget`` and overall behavior to support
  filtering like `django-easyfilters`_ or maybe drop the widget?

.. _`http://pypi.python.org/pypi/django-easyfilters`


Resources
---------

* `Documentation <http://django-refinery.rtfd.org/>`_
* `Bug Tracker <http://github.com/nkryptic/django-refinery/issues>`_
* `Code <http://github.com/nkryptic/django-refinery>`_
* `Continuous Integration <http://travis-ci.org/nkryptic/django-refinery>`_



