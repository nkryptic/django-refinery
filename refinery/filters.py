from datetime import datetime, timedelta

from django import forms
from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS
from django.utils.translation import ugettext_lazy as _

from refinery.fields import NumericRangeField, DateRangeField, TimeRangeField, LookupTypeField

__all__ = [
    'Filter', 'CharFilter', 'BooleanFilter', 'ChoiceFilter',
    'MultipleChoiceFilter', 'DateFilter', 'DateTimeFilter', 'TimeFilter',
    'ModelChoiceFilter', 'ModelMultipleChoiceFilter', 'NumberFilter',
    'RangeFilter', 'DateRangeFilter', 'AllValuesFilter', 'MultipleFieldFilter',
    'OpenRangeNumericFilter', 'OpenRangeDateFilter', 'OpenRangeTimeFilter',
]

LOOKUP_TYPES = sorted(QUERY_TERMS)


class Filter(object):
    creation_counter = 0
    field_class = forms.Field
    
    def __init__(self, name=None, label=None, widget=None, action=None,
        lookup_type='exact', required=False, **kwargs):
        self.name = name
        self.label = label
        if action:
            self.filter = action
        self.lookup_type = lookup_type
        self.widget = widget
        self.required = required
        self.extra = kwargs
        
        self.creation_counter = Filter.creation_counter
        Filter.creation_counter += 1
    
    @property
    def field(self):
        if not hasattr(self, '_field'):
            if self.lookup_type is None or isinstance(self.lookup_type, (list, tuple)):
                if self.lookup_type is None:
                    lookup = [(x, x) for x in LOOKUP_TYPES]
                else:
                    # lookup = [(x, x) for x in LOOKUP_TYPES if x in self.lookup_type]
                    lookup = []
                    for x in self.lookup_type:
                        if isinstance(x, (list, tuple)) and x[0] in LOOKUP_TYPES:
                            lookup.append(x)
                        elif x in LOOKUP_TYPES:
                            lookup.append((x, x))
                self._field = LookupTypeField(self.field_class(
                    required=self.required, widget=self.widget, **self.extra),
                    lookup, required=self.required, label=self.label)
            else:
                self._field = self.field_class(required=self.required,
                    label=self.label, widget=self.widget, **self.extra)
        return self._field
    
    def filter(self, value):
        if not value:
            # TODO: what if I want to check that the field is null?
            # TODO: - check that a date field has NO date
            # TODO: - check that a relationship doesn't exist (company w/out employees)
            # TODO: - check filter all users without bio field filled out...
            return
        if isinstance(value, (list, tuple)):
            lookup = str(value[1])
            if not lookup:
                lookup = 'exact' # we fallback to exact if no choice for lookup is provided
            value = value[0]
            if not value:
                return
        else:
            lookup = self.lookup_type
        return Q(**{'%s__%s' % (self.name, lookup): value})


class CharFilter(Filter):
    field_class = forms.CharField


class BooleanFilter(Filter):
    field_class = forms.NullBooleanField
    
    def filter(self, value):
        return Q(**{self.name: bool(value)})


class ChoiceFilter(Filter):
    field_class = forms.ChoiceField


class MultipleChoiceFilter(Filter):
    """
    This filter preforms an OR query on the selected options.
    
    """
    field_class = forms.MultipleChoiceField
    
    def filter(self, value):
        value = value or ()
        if len(value) and len(value) == len(self.field.choices):
            return
        
        lookup_type = self.lookup_type or 'exact'
        lookup = '%s__%s' % (self.name, lookup_type)
        # TODO: WHAT IF WE WANT TO & the Qs instead???
        reducto = lambda x, y: x | Q(**{lookup: y})
        q = reduce(reducto, value, Q())
        return q


class MultipleFieldFilter(CharFilter):
    """
    This filter preforms an OR query on the defined fields.
    
    """
    def __init__(self, fields, *args, **kwargs):
        super(MultipleFieldFilter, self).__init__(*args, **kwargs)
        self.fields = fields
    
    def filter(self, value):
        if not value:
            return
        
        lookup_type = self.lookup_type or 'exact'
        # TODO: WHAT IF WE WANT TO & the Qs instead???
        reducto = lambda x, y: x | Q(**{'%s__%s' % (y, lookup_type): value})
        q = reduce(reducto, self.fields, Q())
        return q


class DateFilter(Filter):
    field_class = forms.DateField


class DateTimeFilter(Filter):
    field_class = forms.DateTimeField


class TimeFilter(Filter):
    field_class = forms.TimeField


class ModelChoiceFilter(Filter):
    field_class = forms.ModelChoiceField


class ModelMultipleChoiceFilter(MultipleChoiceFilter):
    field_class = forms.ModelMultipleChoiceField


class NumberFilter(Filter):
    field_class = forms.DecimalField


class RangeFilter(Filter):
    field_class = NumericRangeField
    
    def filter(self, value):
        if not value:
            return
        return Q(**{'%s__range' % self.name: (value.start, value.stop)})


class BaseOpenRangeFilter(Filter):
    """
    Abstract class similar to RangeFilter but allows open ended ranges.
    Inheriting classes must define field_class attribute.
    
    """
    def filter(self, value):
        q = Q()
        if value:
            if value.start:
                q &= Q(**{'%s__gte' % self.name: value.start})
            if value.stop:
                q &= Q(**{'%s__lte' % self.name: value.stop})
        return q

class OpenRangeNumericFilter(BaseOpenRangeFilter):
    field_class = NumericRangeField

class OpenRangeDateFilter(BaseOpenRangeFilter):
    field_class = DateRangeField

class OpenRangeTimeFilter(BaseOpenRangeFilter):
    field_class = TimeRangeField


class DateRangeFilter(ChoiceFilter):
    options = {
        '': (_('Any Date'), lambda name: None),
        1: (_('Today'), lambda name: Q(**{
            '%s__year' % name: datetime.today().year,
            '%s__month' % name: datetime.today().month,
            '%s__day' % name: datetime.today().day
        })),
        2: (_('Past 7 days'), lambda name: Q(**{
            '%s__gte' % name: (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            '%s__lt' % name: (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d'),
        })),
        3: (_('This month'), lambda name: Q(**{
            '%s__year' % name: datetime.today().year,
            '%s__month' % name: datetime.today().month
        })),
        4: (_('This year'), lambda name: Q(**{
            '%s__year' % name: datetime.today().year,
        })),
    }
    
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [(key, value[0]) for key, value in self.options.iteritems()]
        super(DateRangeFilter, self).__init__(*args, **kwargs)
    
    def filter(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = ''
            
        return self.options[value][1](self.name)


class AllValuesFilter(ChoiceFilter):
    @property
    def field(self):
        # TODO: self.model is only used here and is assigned from the filtertool class
        qs = self.model._default_manager.distinct().order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [(o, o) for o in qs]
        return super(AllValuesFilter, self).field

