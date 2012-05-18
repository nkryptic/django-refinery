django-refinery
===============

The django-refinery project is a reusable Django_ application allowing
users to dynamically filter and refine a Model queryset.  It requires
Python 2.5 or higher.

Django-refinery can be used for generating interfaces similar to the Django
admin's ``list_filter`` interface.  It has an API very similar to Django's
``ModelForms``.  For example if you had a Product model you could create
a ``FilterTool`` for it with the code::

    import refinery
    
    class ProductFilterTool(refinery.FilterTool):
        class Meta:
            model = Product
            fields = ['name', 'price', 'manufacturer']

And then in your view you could do::

    def product_list(request):
        filtertool = ProductFilterTool(request.GET or None)
        return render_to_response('product/product_list.html',
            {'filtertool': filtertool})

The documentation can be found in the ``docs`` directory or `read online`_.
The source code and issue tracker are generously `hosted by GitHub`_.

If you want to help out with the development of django-refinery, by
posting detailed bug reports, proposing new features, or suggesting
documentation improvements, use the `issue tracker`_.  If you want to
get your hands dirty, great!  Clone the repository, make changes and
send a pull request.  Please do create an issue to discuss your plans.

.. _`Django`: http://www.djangoproject.com/
.. _`read online`: http://django-refinery.rtfd.org
.. _`hosted by GitHub`: http://github.com/nkryptic/django-refinery
.. _`issue tracker`: http://github.com/nkryptic/django-refinery/issues


