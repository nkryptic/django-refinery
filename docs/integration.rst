Integrating with other applications
-----------------------------------

Django-pagination
=================

To use django-refinery alongside django-pagination requires 2 minor changes to the
code snippets shown in :doc:`usage`.

Change the template code to::

    {% extends "base.html" %}

    {% block content %}
        <form action="" method="get">
            {{ filtertool.form.as_p }}
            <input type="submit" />
        </form>
        {% autopaginate filtertool.qs 40 as filtered_list %}
        {% for obj in filtered_list %}
            {{ obj.name }} - ${{ obj.price }}<br />
        {% endfor %}
        {% paginate %}
    {% endblock %}

Also, if you have - for example - selected page 5 of results, and then try to apply a filter,
you will be sent to page 5 of the filtered results. To avoid this, don't add django-pagination's
'page' parameter to the FilterTool in the view code::

    def product_list(request):
        g = request.GET.copy()
        if 'page' in g:
            del g['page']
        f = ProductFilterTool(g, queryset=Product.objects.all())
        return render_to_response('my_app/template.html', {'filtertool': f})

