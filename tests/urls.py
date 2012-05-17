from django.conf.urls.defaults import *

from .models import Book

urlpatterns = patterns('',
    (r'^books/$', 'refinery.views.object_filtered_list', {'model': Book}),
)
