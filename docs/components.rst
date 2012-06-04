==========
Components
==========


FilterTool
==========

.. how it works...


Filters
=======

++++++++++++++++++++++++++ +++++++++++++++++++++++++
Provided Filters           Applied Form Field
++++++++++++++++++++++++++ +++++++++++++++++++++++++
CharFilter                 forms.CharField
BooleanFilter              NullBooleanField
ChoiceFilter               ChoiceField
MultipleChoiceFilter       MultipleChoiceField
MultipleFieldFilter        CharField
DateFilter                 DateField
DateTimeFilter             DateTimeField
TimeFilter                 TimeField
ModelChoiceFilter          ModelChoiceField
ModelMultipleChoiceFilter  ModelMultipleChoiceField
NumberFilter               DecimalField
RangeFilter                NumericRangeField
OpenRangeNumericFilter     NumericRangeField
OpenRangeDateFilter        DateRangeField
OpenRangeTimeFilter        TimeRangeField
DateRangeFilter            ChoiceField
AllValuesFilter            ChoiceField
++++++++++++++++++++++++++ +++++++++++++++++++++++++


++++++++++++++++++++++++++ +++++++++++++++++++++++++
Model Field                Default Filter
++++++++++++++++++++++++++ +++++++++++++++++++++++++
CharField                  CharFilter
TextField                  CharFilter
BooleanField               BooleanFilter
DateField                  DateFilter
DateTimeField              DateTimeFilter
TimeField                  TimeFilter
OneToOneField              ModelChoiceFilter
ForeignKey                 ModelChoiceFilter
ManyToManyField            ModelMultipleChoiceFilter
DecimalField               NumberFilter
SmallIntegerField          NumberFilter
IntegerField               NumberFilter
PositiveIntegerField       NumberFilter
PositiveSmallIntegerField  NumberFilter
FloatField                 NumberFilter
NullBooleanField           BooleanFilter
SlugField                  CharFilter
EmailField                 CharFilter
FilePathField              CharFilter
URLField                   CharFilter
IPAddressField             CharFilter
CommaSeparatedIntegerField CharFilter
XMLField                   CharFilter
++++++++++++++++++++++++++ +++++++++++++++++++++++++

Views
=====

