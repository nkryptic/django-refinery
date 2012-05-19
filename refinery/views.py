from django.shortcuts import render_to_response
from django.template import RequestContext

from refinery.filtertool import FilterTool


def object_filtered_list(request, model=None, queryset=None, template_name=None, extra_context=None,
    context_processors=None, filter_class=None):
    if model is None and filter_class is None:
        raise TypeError("object_filtered_list must be called with either model or filter_class")
    if model is None:
        model = filter_class._meta.model
    if filter_class is None:
        meta = type('Meta', (object,), {'model': model})
        filter_class = type('%sFilterTool' % model._meta.object_name, (FilterTool,),
            {'Meta': meta})
    filtertool = filter_class(request.GET or None, queryset=queryset)

    if not template_name:
        template_name = '%s/%s_filtered_list.html' % (model._meta.app_label, model._meta.object_name.lower())
    c = RequestContext(request, {
        'filtertool': filtertool,
    })
    if extra_context:
        for k, v in extra_context.iteritems():
            if callable(v):
                v = v()
            c[k] = v
    return render_to_response(template_name, c)


from django.http import Http404
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from django.utils.translation import ugettext_lazy as _

class BaseFilteredListView(MultipleObjectMixin, View):
    filter_class = None

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(
                    _(u"Empty list and '%(class_name)s.allow empty' is "
                      u"False.") % {'class_name': self.__class__.__name__})
        context = self.get_context_data(request=request,
                                        object_list=self.object_list)
        return self.render_to_response(context)
    
    def get_filter_class(self):
        """get filter_class"""
        if self.filter_class:
            return self.filter_class
        elif self.model:
            meta = type(
                    'Meta', (object,), {'model': self.model})
            return type(
                    '%sFilterTool' % self.model._meta.object_name,
                    (FilterTool,), {'Meta': meta})
        else:
            raise TypeError(
                    u"""BaseFilteredListView must be used with either model """
                    u"""or filter_class""")

    def get_context_data(self, **kwargs):
        request = kwargs.pop('request')
        filter_class = self.get_filter_class()
        filterset = filter_class(request.GET or None, self.get_queryset())
        kwargs['filter'] = filterset
        return super(BaseFilteredListView, self).get_context_data(**kwargs)


class FilteredListView(MultipleObjectTemplateResponseMixin, BaseFilteredListView):
    """
    Render some list of objects with filter, set by `self.model` or
    `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
    template_name_suffix = '_filtered_list'


