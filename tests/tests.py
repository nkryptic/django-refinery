import datetime
import os
from django.conf import settings
from django.test import TestCase
from django.db.models import Q
from django import forms
import refinery
from refinery import FilterTool
from refinery.widgets import LinkWidget
from .models import User, Comment, Book, Restaurant, Article
from .models import STATUS_CHOICES, STATUS_CHOICES_NONE


class GenericViewTests(TestCase):
    urls = 'tests.urls'
    fixtures = ['test_data']
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'templates'),
    ]
    
    def setUp(self):
        self.old_template_dir = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = self.template_dirs
    
    def tearDown(self):
        settings.TEMPLATE_DIRS = self.old_template_dir
    
    def test_generic_view(self):
        response = self.client.get('/books/')
        for b in ['Ender&#39;s Game', 'Rainbox Six', 'Snowcrash']:
            self.assertContains(response, b)


class InheritanceTest(TestCase):
    def test_inheritance(self):
        class F(refinery.FilterTool):
            class Meta:
                model = Book
        
        class G(F):
            pass
        self.assertEqual(set(F.base_filters), set(G.base_filters))


class ModelInheritanceTest(TestCase):
    def test_abstract(self):
        class F(refinery.FilterTool):
            class Meta:
                model = Restaurant
        
        self.assertEquals(set(F.base_filters), set(['name', 'serves_pizza']))
        
        class F(refinery.FilterTool):
            class Meta:
                model = Restaurant
                fields = ['name', 'serves_pizza']
        
        self.assertEquals(set(F.base_filters), set(['name', 'serves_pizza']))


class DateRangeFilterTest(TestCase):
    def test_filter(self):
        a = Article.objects.create(published=datetime.datetime.today())
        class F(refinery.FilterTool):
            published = refinery.DateRangeFilter()
            class Meta:
                model = Article
        f = F({'published': '2'})
        self.assertEqual(list(f), [a])


class FilterToolForm(TestCase):
    def test_prefix(self):
        class F(refinery.FilterTool):
            class Meta:
                model = Restaurant
                fields = ['name']
        self.assert_('blah-prefix' in unicode(F(prefix='blah-prefix').form))


class AllValuesFilterTest(TestCase):
    fixtures = ['test_data']
    
    def test_filter(self):
        class F(refinery.FilterTool):
            username = refinery.AllValuesFilter()
            class Meta:
                model = User
                fields = ['username']
        form_html = ('<tr><th><label for="id_username">Username:</label></th>'
            '<td><select name="username" id="id_username">\n'
            '<option value="aaron">aaron</option>\n<option value="alex">alex'
            '</option>\n<option value="jacob">jacob</option>\n</select></td>'
            '</tr>')
        self.assertEqual(unicode(F().form), form_html)
        self.assertEqual(list(F().qs), list(User.objects.all()))
        self.assertEqual(list(F({'username': 'alex'})), [User.objects.get(username='alex')])
        self.assertEqual(list(F({'username': 'jose'})), list(User.objects.all()))


class InitialValueTest(TestCase):
    fixtures = ['test_data']
    
    def test_initial(self):
        class F(refinery.FilterTool):
            status = refinery.ChoiceFilter(choices=STATUS_CHOICES, initial=1)
            class Meta:
                model = User
                fields = ['status']
        self.assertEqual(list(F().qs), [User.objects.get(username='alex')])
        self.assertEqual(list(F({'status': 0})), list(User.objects.filter(status=0)))


class RelatedObjectTest(TestCase):
    fixtures = ['test_data']
    
    def test_foreignkey(self):
        class F(refinery.FilterTool):
            class Meta:
                model = Article
                fields = ['author__username']
        self.assertEqual(F.base_filters.keys(), ['author__username'])
        form_html = ('<tr><th><label for="id_author__username">Username:</label>'
            '</th><td><input type="text" name="author__username" '
            'id="id_author__username" /></td></tr>')
        self.assertEqual(str(F().form), form_html)
        self.assertEqual(F({'author__username': 'alex'}).qs.count(), 2)
        self.assertEqual(F({'author__username': 'jacob'}).qs.count(), 1)
        
        class F(refinery.FilterTool):
            author__username = refinery.AllValuesFilter()
            class Meta:
                model = Article
                fields = ['author__username']
        
        form_html = ('<tr><th><label for="id_author__username">Author  '
            'username:</label></th><td><select name="author__username" '
            'id="id_author__username">\n<option value="alex">alex</option>\n'
            '<option value="jacob">jacob</option>\n</select></td></tr>')
        self.assertEqual(str(F().form), form_html)


class MultipleChoiceFilterTest(TestCase):
    fixtures = ['test_data']
    
    def test_all_choices_selected(self):
        class F(refinery.FilterTool):
            class Meta:
                model = User
                fields = ["status"]
        
        self.assertEqual(list(F({"status": [0, 1]}).qs), list(User.objects.all()))


class MultipleLookupTypesTest(TestCase):
    fixtures = ['test_data']
    
    def test_no_GET_params(self):
        class F(refinery.FilterTool):
            published = refinery.DateTimeFilter(lookup_type=['gt', 'lt'])
            class Meta:
                model = Article
                fields = ['published']
        
        self.assertEqual(list(F({}).qs), list(Article.objects.all()))


class FilterToolTestCase(TestCase):
    fixtures = ['test_data']
    
    def setUp(self):
        self.alex = User.objects.get(username='alex')
        self.aaron = User.objects.get(username='aaron')
        self.jacob = User.objects.get(username='jacob')
        self.comment1 = Comment.objects.get(pk=1)
        self.comment2 = Comment.objects.get(pk=2)
        self.comment3 = Comment.objects.get(pk=3)
        self.book1 = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        self.book3 = Book.objects.get(pk=3)


class FilterToolFiltersTest(FilterToolTestCase):
    
    def test_from_model(self):
        class F(FilterTool):
            class Meta:
                model = User
        
        expected = ['username', 'first_name', 'last_name', 'status',
                    'is_active', 'favorite_books']
        self.assertEqual(F.base_filters.keys(), expected)
    
    def test_with_exclude(self):
        class F(FilterTool):
            class Meta:
                model = User
                exclude = ['is_active']
        
        expected = ['username', 'first_name', 'last_name', 'status',
                    'favorite_books']
        self.assertEqual(F.base_filters.keys(), expected)


class FilterToolUsageTest(FilterToolTestCase):
    
    def test_1(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['status']
        
        f = F({'status': '1'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex])
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td>'
            '<select name="status" id="id_status"><option value="0">Regular</option>'
            '<option value="1" selected="selected">Admin</option></select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_2(self):
        class F(FilterTool):
            status = refinery.ChoiceFilter(widget=forms.RadioSelect, choices=STATUS_CHOICES)
            class Meta:
                model = User
                fields = ['status']
        
        f = F(queryset=User.objects.all())
        form_html = (
            '<tr><th><label for="id_status_0">Status:</label></th><td><ul><li><label for="id_status_0">'
            '<input type="radio" id="id_status_0" value="0" name="status" /> Regular</label></li>'
            '<li><label for="id_status_1"><input type="radio" id="id_status_1" value="1" name="status" /> '
            'Admin</label></li></ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_3(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['username']
        
        self.assertEqual(F.base_filters.keys(), ['username'])
        
        f = F(queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        f = F({'username': 'alex'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex])
        form_html = (
            '<tr><th><label for="id_username">Username:</label></th><td><input '
            'type="text" name="username" value="alex" id="id_username" /></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_4(self):
        class F(FilterTool):
            username = refinery.CharFilter(action=lambda value: Q(**{'username__startswith': value}))
            class Meta:
                model = User
                fields = ['username']
        
        f = F({'username': 'a'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron])
    
    def test_5(self):
        class F(FilterTool):
            status = refinery.MultipleChoiceFilter(choices=STATUS_CHOICES)
            class Meta:
                model = User
                fields = ['status']
        
        f = F(queryset=User.objects.all())
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><select '
            'multiple="multiple" name="status" id="id_status">'
            '<option value="0">Regular</option><option value="1">Admin</option>'
            '</select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        f = F({'status': ['0']}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.aaron, self.jacob])
        f = F({'status': ['0', '1']}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
    
    def test_6(self):
        class F(FilterTool):
            class Meta:
                model = Comment
                fields = ['date']
        
        #This test will fail in 2011
        f = F({'date': '01/30/2010'}, queryset=Comment.objects.all())
        self.assertEqual(list(f.qs), [self.comment1])
    
    def test_7(self):
        class F(FilterTool):
            class Meta:
                model = Comment
                fields = ['author']
        
        f = F({'author': '2'}, queryset=Comment.objects.all())
        self.assertEqual(list(f.qs), [self.comment2])
    
    def test_8(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['favorite_books']
        
        f = F(queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        f = F({'favorite_books': ['1']}, queryset=User.objects.all())
        self.assertEqual(list(f.qs.distinct()), [self.alex, self.aaron])
        f = F({'favorite_books': ['1', '3']}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron])
        f = F({'favorite_books': ['2']}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex])


class MoreFilterToolUsageTest(FilterToolTestCase):
    
    def test_1(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['username', 'status']
                order_by = ['status']
        
        f = F({'o': 'status'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.aaron, self.jacob, self.alex])
        form_html = (
            '<tr><th><label for="id_username">Username:</label></th><td><input type="text" '
            'name="username" id="id_username" /></td></tr><tr><th><label for="id_status">'
            'Status:</label></th><td><select name="status" id="id_status">'
            '<option value="0">Regular</option><option value="1">Admin</option>'
            '</select></td></tr><tr><th><label for="id_o">Ordering:</label></th><td>'
            '<select name="o" id="id_o"><option value="status" selected="selected">Status</option>'
            '</select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_2(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['username', 'status']
                order_by = True
        
        f = F({'o': 'username'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.aaron, self.alex, self.jacob])
        form_html = (
            '<tr><th><label for="id_username">Username:</label></th><td><input type="text" '
            'name="username" id="id_username" /></td></tr><tr><th><label for="id_status">'
            'Status:</label></th><td><select name="status" id="id_status"><option value="0">'
            'Regular</option><option value="1">Admin</option></select></td></tr>'
            '<tr><th><label for="id_o">Ordering:</label></th><td><select name="o" id="id_o">'
            '<option value="username" selected="selected">Username</option>'
            '<option value="status">Status</option></select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_3(self):
        class F(FilterTool):
            price = refinery.NumberFilter(lookup_type='lt')
            class Meta:
                model = Book
                fields = ['price']
        
        f = F({'price': 15}, queryset=Book.objects.all())
        self.assertEqual(list(f.qs), [self.book1])
    
    def test_4(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['is_active']
        
        # '2' and '3' are how the field expects the data from the browser
        f = F({'is_active': '2'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.jacob])
        f = F({'is_active': '3'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron])
        f = F({'is_active': '1'}, queryset=User.objects.all())
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
    
    def test_5(self):
        class F(FilterTool):
            average_rating = refinery.NumberFilter(lookup_type='gt')
            class Meta:
                model = Book
                fields = ['average_rating']
        
        f = F({'average_rating': '4.5'}, queryset=Book.objects.all())
        self.assertEqual(list(f.qs), [self.book1, self.book2])
    
    def test_6(self):
        class F(FilterTool):
            class Meta:
                model = Comment
                fields = ['time']
        
        f = F({'time': '12:55'}, queryset=Comment.objects.all())
        self.assertEqual(list(f.qs), [self.comment3])
    
    def test_7(self):
        class F(FilterTool):
            price = refinery.RangeFilter()
            class Meta:
                model = Book
                fields = ['price']
        
        f = F(queryset=Book.objects.all())
        form_html = (
            '<tr><th><label for="id_price_0">Price:</label></th><td>'
            '<input type="text" name="price_0" id="id_price_0" />-<input '
            'type="text" name="price_1" id="id_price_1" /></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        self.assertEqual(list(f.qs), [self.book1, self.book2, self.book3])
        f = F({'price_0': '5', 'price_1': '15'}, queryset=Book.objects.all())
        self.assertEqual(list(f.qs), [self.book1, self.book2])
    
    def test_8(self):
        class F(FilterTool):
            price = refinery.NumberFilter(lookup_type=None)
            class Meta:
                model = Book
                fields = ['price']
        
        f = F(queryset=Book.objects.all())
        form_html = (
            '<tr><th><label for="id_price_0">Price:</label></th><td><input '
            'type="text" name="price_0" id="id_price_0" /><select name="price_1" '
            'id="id_price_1"><option value="contains">contains</option>'
            '<option value="day">day</option><option value="endswith">endswith</option>'
            '<option value="exact">exact</option><option value="gt">gt</option>'
            '<option value="gte">gte</option><option value="icontains">icontains</option>'
            '<option value="iendswith">iendswith</option><option value="iexact">iexact</option>'
            '<option value="in">in</option><option value="iregex">iregex</option>'
            '<option value="isnull">isnull</option><option value="istartswith">istartswith</option>'
            '<option value="lt">lt</option><option value="lte">lte</option>'
            '<option value="month">month</option><option value="range">range</option>'
            '<option value="regex">regex</option><option value="search">search</option>'
            '<option value="startswith">startswith</option><option value="week_day">week_day</option>'
            '<option value="year">year</option></select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)


class AndEvenMoreFilterToolUsageTest(FilterToolTestCase):
    
    def test_1(self):
        class F(FilterTool):
            price = refinery.NumberFilter(lookup_type=['lt', 'gt'])
            class Meta:
                model = Book
                fields = ['price']
        
        f = F(queryset=Book.objects.all())
        form_html = (
            '<tr><th><label for="id_price_0">Price:</label></th><td><input '
            'type="text" name="price_0" id="id_price_0" /><select name="price_1" id="id_price_1">'
            '<option value="lt">lt</option>'
            '<option value="gt">gt</option>'
            '</select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        f = F({'price_0': '15', 'price_1': 'lt'}, queryset=Book.objects.all())
        self.assertEqual(list(f.qs), [self.book1])
        f = F({'price_0': '15', 'price_1': 'lt'})
        self.assertEqual(list(f.qs), [self.book1])
        f = F({'price_0': '', 'price_1': 'lt'})
        self.assertEqual(list(f.qs), [self.book1, self.book2, self.book3])
    
    def test_2(self):
        class F(FilterTool):
            status = refinery.ChoiceFilter(widget=LinkWidget, choices=STATUS_CHOICES)
            class Meta:
                model = User
                fields = ['status']
        
        f = F()
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><ul id="id_status">'
            '<li><a href="?status=0">Regular</a></li>'
            '<li><a href="?status=1">Admin</a></li></ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        f = F({'status': '1'})
        self.assertEqual(list(f.qs), [self.alex])
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><ul id="id_status">'
            '<li><a href="?status=0">Regular</a></li>'
            '<li><a class="selected" href="?status=1">Admin</a></li></ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
    
    def test_3(self):
        class F(FilterTool):
            date = refinery.DateRangeFilter(widget=LinkWidget)
            class Meta:
                model = Comment
                fields = ['date']
        
        f = F()
        form_html = (
            '<tr><th><label for="id_date">Date:</label></th><td><ul id="id_date">'
            '<li><a class="selected" href="?date=">Any Date</a></li>'
            '<li><a href="?date=1">Today</a></li>'
            '<li><a href="?date=2">Past 7 days</a></li>'
            '<li><a href="?date=3">This month</a></li>'
            '<li><a href="?date=4">This year</a></li></ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        f = F({'date': '4'})
        # Expect this will fail in years 2011+ until fixtures are refactored
        # maybe use django-whatever?
        self.assertEqual(list(f.qs), [self.comment1, self.comment2])
        f = F({})
        form_html = (
            '<tr><th><label for="id_date">Date:</label></th><td><ul id="id_date">'
            '<li><a class="selected" href="?date=">Any Date</a></li>'
            '<li><a href="?date=1">Today</a></li>'
            '<li><a href="?date=2">Past 7 days</a></li>'
            '<li><a href="?date=3">This month</a></li>'
            '<li><a href="?date=4">This year</a></li></ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        self.assertEqual(list(f.qs), [self.comment1, self.comment2, self.comment3])
        # _ = Comment.objects.create(text="Wowa", author=self.alex, date=datetime.today(), time="12:30")
        Comment.objects.create(text="Wowa", author=self.alex, date=datetime.today(), time="12:30")
        f = F({'date': '2'})
        self.assertEqual(list(f.qs), [self.comment4])


class FinishingFilterToolUsageTest(FilterToolTestCase):
    
    def test_1(self):
        msg = "Meta.fields contains a field that isn't defined on this FilterTool"
        with self.assertRaisesRegexp(TypeError, msg):
            class F(FilterTool):
                class Meta:
                    model = User
                    fields = ['name']
    
    def test_2(self):
        class MyForm(forms.Form):
            def as_table(self):
                return "lol string"
        
        class F(FilterTool):
            class Meta:
                model = Comment
                form = MyForm
        
        self.assertEqual(unicode(F().form), u"lol string")
    
    def test_3(self):
        class F(FilterTool):
            class Meta:
                model = User
                fields = ['status', 'username']
        
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><select name="status" id="id_status">'
            '<option value="0">Regular</option>'
            '<option value="1">Admin</option></select></td></tr>'
            '<tr><th><label for="id_username">Username:</label></th><td><input '
            'type="text" name="username" id="id_username" /></td></tr>')
        self.assertHTMLEqual(unicode(F().form), form_html)
    
    def test_4(self):
        class F(FilterTool):
            class Meta:
                model = Comment
                fields = ['author', 'text']
        
        form_html = (
            '<tr><th><label for="id_author">Author:</label></th><td><select name="author" id="id_author">'
            '<option value="" selected="selected">---------</option>'
            '<option value="1">alex</option>'
            '<option value="2">aaron</option>'
            '<option value="3">jacob</option></select></td></tr>'
            '<tr><th><label for="id_text">Text:</label></th><td><input type="text" name="text" id="id_text" /></td></tr>')
        self.assertHTMLEqual(unicode(F().form), form_html)
    
    def test_5(self):
        class F(FilterTool):
            class Meta:
                model = User
                order_by = ['username']
        
        f = F()
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        f = F({})
        self.assertEqual(list(f.qs), [self.alex, self.aaron, self.jacob])
        f = F({'o': 'username'})
        self.assertEqual(list(f.qs), [self.aaron, self.alex, self.jacob])
    
    def test_6(self):
        class F(FilterTool):
            price = refinery.NumberFilter(lookup_type=[('lt', 'Less than'),
                ('gt', 'Greater than'),
                ('exact', 'Exactly')])
            class Meta:
                model = Book
                fields = ['price']
        
        f = F({'price_0': '15'})
        self.assertEqual(list(f.qs), [self.book2])
        form_html = (
            '<tr><th><label for="id_price_0">Price:</label></th><td>'
            '<input type="text" name="price_0" value="15" id="id_price_0" />'
            '<select name="price_1" id="id_price_1">'
            '<option value="lt">Less than</option>'
            '<option value="gt">Greater than</option>'
            '<option value="exact">Exactly</option>'
            '</select></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        
        from refinery import widgets
        widgets.PREPEND_LOOKUP_FIELD = True
        try:
            f = F({'price_0': '15'})
            form_html = (
                '<tr><th><label for="id_price_0">Price:</label></th><td>'
                '<select name="price_1" id="id_price_1">'
                '<option value="lt">Less than</option>'
                '<option value="gt">Greater than</option>'
                '<option value="exact">Exactly</option></select>'
                '<input type="text" name="price_0" value="15" id="id_price_0" /></td></tr>')
            self.assertHTMLEqual(unicode(f.form), form_html)
        finally:
            widgets.PREPEND_LOOKUP_FIELD = False
    
    def test_7(self):
        class F(FilterTool):
            status = refinery.ChoiceFilter(widget=LinkWidget, choices=STATUS_CHOICES_NONE)
            class Meta:
                model = User
                fields = ['status']
        f = F()
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><ul id="id_status">'
            '<li><a class="selected" href="?">All</a></li>'
            '<li><a href="?status=0">Regular</a></li>'
            '<li><a href="?status=1">Admin</a></li>'
            '</ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        f = F({'status':'0'})
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><ul id="id_status">'
            '<li><a href="?">All</a></li>'
            '<li><a class="selected" href="?status=0">Regular</a></li>'
            '<li><a href="?status=1">Admin</a></li>'
            '</ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)
        f = F({})
        form_html = (
            '<tr><th><label for="id_status">Status:</label></th><td><ul id="id_status">'
            '<li><a class="selected" href="?">All</a></li>'
            '<li><a href="?status=0">Regular</a></li>'
            '<li><a href="?status=1">Admin</a></li>'
            '</ul></td></tr>')
        self.assertHTMLEqual(unicode(f.form), form_html)


