Using django-refinery
---------------------

Django-refinery provides a simple way to filter down a queryset based on
parameters a user provides.  Say we have a ``Product`` model and we want to let
our users filter which products they see on a list page.  Let's start with our
model::

    from django.db import models

    class Product(models.Model):
        name = models.CharField(max_length=255)
        price = models.DecimalField()
        description = models.TextField()
        release_date = models.DateField()
        manufacturer = models.ForeignKey(Manufacturer)

We have a number of fields and we want to let our users filter based on the
price or the release_date.  We create a ``FilterTool`` for this::

    import refinery

    class ProductFilterTool(refinery.FilterTool):
        class Meta:
            model = Product
            fields = ['price', 'release_date']


As you can see this uses a very similar API to Django's ``ModelForm``.  Just
like with a ``ModelForm`` we can also overide filters, or add new ones using a
declarative syntax::

    import refinery

    class ProductFilterTool(refinery.FilterTool):
        price = refinery.NumberFilter(lookup_type='lt')
        class Meta:
            model = Product
            fields = ['price', 'release_date']

Filters take a ``lookup_type`` argument which specifies what lookup type to
use with Django's ORM.  So here when a user entered a price it would show all
Products with a price less than that.

You can also specify the lookup type when specifying the ``fields``::

    import refinery

    class ProductFilterTool(refinery.FilterTool):
        class Meta:
            model = Product
            fields = ['price__lt', 'release_date']

Filters also take any arbitrary keyword arguments which get passed onto the
``django.forms.Field`` constructor.  These extra keyword arguments get stored
in ``Filter.extra``, so it's possible to overide the constructor of a
``FilterTool`` to add extra ones::

    class ProductFilterTool(refinery.FilterTool):
        class Meta:
            model = Product
            fields = ['manufacturer']

        def __init__(self, *args, **kwargs):
            super(ProductFilterTool, self).__init__(*args, **kwargs)
            self.filters['manufacturer'].extra.update(
                {'empty_label': u'All Manufacturers'})


Now we need to write a view::

    def product_list(request):
        f = ProductFilterTool(request.GET, queryset=Product.objects.all())
        return render_to_response('my_app/template.html', {'filtertool': f})

If a queryset argument isn't provided then all the items in the default manager
of the model will be used.

And lastly we need a template::

    {% extends "base.html" %}

    {% block content %}
        <form action="" method="get">
            {{ filtertool.form.as_p }}
            <input type="submit" />
        </form>
        {% for obj in filtertool %}
            {{ obj.name }} - ${{ obj.price }}<br />
        {% endfor %}
    {% endblock %}

And that's all there is to it!  The ``form`` attribute contains a normal
Django form, and when we iterate over the ``FilterTool`` we get the objects in
the resulting queryset.

You can also allow the user to control ordering, this is done by providing the
``order_by`` argument in the Filter's Meta class.  ``order_by`` can be either a
``list`` or ``tuple`` of field names, in which case those are the options, or
it can be a ``bool`` which, if True, indicates that all fields that have
the user can filter on can also be sorted on.

If ``order_by`` is a list of lists, the inner lists must be in name/label 
pairs. This lets you override the display names of your ordering fields::

    order_by = (
        ('name', 'Company Name'),
        ('average_rating', 'Stars'),
    )

The inner ``Meta`` class also takes an optional ``form`` argument.  This is a
form class from which ``FilterTool.form`` will subclass.  This works similar to
the ``form`` option on a ``ModelAdmin.``

Items in the ``fields`` sequence in the ``Meta`` class may include 
"relationship paths" using Django's ``__`` syntax to filter on fields on a 
related model.

If you want to use a custom widget, or in any other way overide the ordering
field you can overide the ``get_ordering_field()`` method on a ``FilterTool``.
This method just needs to return a Form Field.

Generic View
============

In addition to the above usage there is also a generic view included in
django-refinery, which lives at ``refinery.views.object_filtered_list``.  You must
provide either a ``model`` or ``filter_class`` argument, similar to the
``create_update`` view in Django itself::

     url(r'^list/$', 
         'refinery.views.object_filtered_list',
         {'model': Product}),

You must provide a template at ``<app>/<model>_filtered_list.html`` which gets the
context parameter ``filtertool``.
