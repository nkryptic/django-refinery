from __future__ import with_statement
import re
import difflib
import HTMLParser as _HTMLParser
from HTMLParser import HTMLParseError
from django.test import TestCase
from django.utils.unittest.util import safe_repr
from django.utils.encoding import force_unicode

WHITESPACE = re.compile('\s+')


class HTMLParser(_HTMLParser.HTMLParser):
    """
    Patched version of stdlib's HTMLParser with patch from:
    http://bugs.python.org/issue670664
    """
    def __init__(self):
        _HTMLParser.HTMLParser.__init__(self)
        self.cdata_tag = None

    def set_cdata_mode(self, tag):
        try:
            self.interesting = _HTMLParser.interesting_cdata
        except AttributeError:
            self.interesting = re.compile(r'</\s*%s\s*>' % tag.lower(), re.I)
        self.cdata_tag = tag.lower()

    def clear_cdata_mode(self):
        self.interesting = _HTMLParser.interesting_normal
        self.cdata_tag = None

    # Internal -- handle starttag, return end or -1 if not terminated
    def parse_starttag(self, i):
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        rawdata = self.rawdata
        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        match = _HTMLParser.tagfind.match(rawdata, i + 1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()
        self.lasttag = tag = rawdata[i + 1:k].lower()

        while k < endpos:
            m = _HTMLParser.attrfind.match(rawdata, k)
            if not m:
                break
            attrname, rest, attrvalue = m.group(1, 2, 3)
            if not rest:
                attrvalue = None
            elif attrvalue[:1] == '\'' == attrvalue[-1:] or \
                 attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
                attrvalue = self.unescape(attrvalue)
            attrs.append((attrname.lower(), attrvalue))
            k = m.end()

        end = rawdata[k:endpos].strip()
        if end not in (">", "/>"):
            lineno, offset = self.getpos()
            if "\n" in self.__starttag_text:
                lineno = lineno + self.__starttag_text.count("\n")
                offset = len(self.__starttag_text) \
                         - self.__starttag_text.rfind("\n")
            else:
                offset = offset + len(self.__starttag_text)
            self.error("junk characters in start tag: %r"
                       % (rawdata[k:endpos][:20],))
        if end.endswith('/>'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_startendtag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            if tag in self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode(tag) # <--------------------------- Changed
        return endpos

    # Internal -- parse endtag, return end or -1 if incomplete
    def parse_endtag(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i + 2] == "</", "unexpected call to parse_endtag"
        match = _HTMLParser.endendtag.search(rawdata, i + 1) # >
        if not match:
            return -1
        j = match.end()
        match = _HTMLParser.endtagfind.match(rawdata, i) # </ + tag + >
        if not match:
            if self.cdata_tag is not None: # *** add ***
                self.handle_data(rawdata[i:j]) # *** add ***
                return j # *** add ***
            self.error("bad end tag: %r" % (rawdata[i:j],))
        # --- changed start ---------------------------------------------------
        tag = match.group(1).strip()
        if self.cdata_tag is not None:
            if tag.lower() != self.cdata_tag:
                self.handle_data(rawdata[i:j])
                return j
        # --- changed end -----------------------------------------------------
        self.handle_endtag(tag.lower())
        self.clear_cdata_mode()
        return j


def normalize_whitespace(string):
    return WHITESPACE.sub(' ', string)


class Element(object):
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = sorted(attributes)
        self.children = []

    def append(self, element):
        if isinstance(element, basestring):
            element = force_unicode(element)
            element = normalize_whitespace(element)
            if self.children:
                if isinstance(self.children[-1], basestring):
                    self.children[-1] += element
                    self.children[-1] = normalize_whitespace(self.children[-1])
                    return
        elif self.children:
            # removing last children if it is only whitespace
            # this can result in incorrect dom representations since
            # whitespace between inline tags like <span> is significant
            if isinstance(self.children[-1], basestring):
                if self.children[-1].isspace():
                    self.children.pop()
        if element:
            self.children.append(element)

    def finalize(self):
        def rstrip_last_element(children):
            if children:
                if isinstance(children[-1], basestring):
                    children[-1] = children[-1].rstrip()
                    if not children[-1]:
                        children.pop()
                        children = rstrip_last_element(children)
            return children

        rstrip_last_element(self.children)
        for i, child in enumerate(self.children):
            if isinstance(child, basestring):
                self.children[i] = child.strip()
            elif hasattr(child, 'finalize'):
                child.finalize()

    def __eq__(self, element):
        if not hasattr(element, 'name'):
            return False
        if hasattr(element, 'name') and self.name != element.name:
            return False
        if len(self.attributes) != len(element.attributes):
            return False
        if self.attributes != element.attributes:
            # attributes without a value is same as attribute with value that
            # equals the attributes name:
            # <input checked> == <input checked="checked">
            for i in range(len(self.attributes)):
                attr, value = self.attributes[i]
                other_attr, other_value = element.attributes[i]
                if value is None:
                    value = attr
                if other_value is None:
                    other_value = other_attr
                if attr != other_attr or value != other_value:
                    return False
        if self.children != element.children:
            return False
        return True

    def __ne__(self, element):
        return not self.__eq__(element)

    def _count(self, element, count=True):
        if not isinstance(element, basestring):
            if self == element:
                return 1
        i = 0
        for child in self.children:
            # child is text content and element is also text content, then
            # make a simple "text" in "text"
            if isinstance(child, basestring):
                if isinstance(element, basestring):
                    if count:
                        i += child.count(element)
                    elif element in child:
                        return 1
            else:
                i += child._count(element, count=count)
                if not count and i:
                    return i
        return i

    def __contains__(self, element):
        return self._count(element, count=False) > 0

    def count(self, element):
        return self._count(element, count=True)

    def __getitem__(self, key):
        return self.children[key]

    def __unicode__(self):
        output = u'<%s' % self.name
        for key, value in self.attributes:
            if value:
                output += u' %s="%s"' % (key, value)
            else:
                output += u' %s' % key
        if self.children:
            output += u'>\n'
            output += u''.join(unicode(c) for c in self.children)
            output += u'\n</%s>' % self.name
        else:
            output += u' />'
        return output

    def __repr__(self):
        return unicode(self)


class RootElement(Element):
    def __init__(self):
        super(RootElement, self).__init__(None, ())

    def __unicode__(self):
        return u''.join(unicode(c) for c in self.children)


class Parser(HTMLParser):
    SELF_CLOSING_TAGS = ('br', 'hr', 'input', 'img', 'meta', 'spacer',
        'link', 'frame', 'base', 'col')

    def __init__(self):
        HTMLParser.__init__(self)
        self.root = RootElement()
        self.open_tags = []
        self.element_positions = {}

    def error(self, msg):
        raise HTMLParseError(msg, self.getpos())

    def format_position(self, position=None, element=None):
        if not position and element:
            position = self.element_positions[element]
        if position is None:
            position = self.getpos()
        if hasattr(position, 'lineno'):
            position = position.lineno, position.offset
        return 'Line %d, Column %d' % position

    @property
    def current(self):
        if self.open_tags:
            return self.open_tags[-1]
        else:
            return self.root

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.SELF_CLOSING_TAGS:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs)
        self.current.append(element)
        if tag not in self.SELF_CLOSING_TAGS:
            self.open_tags.append(element)
        self.element_positions[element] = self.getpos()

    def handle_endtag(self, tag):
        if not self.open_tags:
            self.error("Unexpected end tag `%s` (%s)" % (
                tag, self.format_position()))
        element = self.open_tags.pop()
        while element.name != tag:
            if not self.open_tags:
                self.error("Unexpected end tag `%s` (%s)" % (
                    tag, self.format_position()))
            element = self.open_tags.pop()

    def handle_data(self, data):
        self.current.append(data)

    def handle_charref(self, name):
        self.current.append('&%s;' % name)

    def handle_entityref(self, name):
        self.current.append('&%s;' % name)


def parse_html(html):
    """
    Takes a string that contains *valid* HTML and turns it into a Python object
    structure that can be easily compared against other HTML on semantic
    equivilance. Syntactical differences like which quotation is used on
    arguments will be ignored.

    """
    parser = Parser()
    parser.feed(html)
    parser.close()
    document = parser.root
    document.finalize()
    # Removing ROOT element if it's not necessary
    if len(document.children) == 1:
        if not isinstance(document.children[0], basestring):
            document = document.children[0]
    return document


def assert_and_parse_html(self, html, user_msg, msg):
    try:
        dom = parse_html(html)
    except HTMLParseError, e:
        standardMsg = u'%s\n%s' % (msg, e.msg)
        self.fail(self._formatMessage(user_msg, standardMsg))
    return dom


class _AssertRaisesContext(object):
    """A context manager used to implement TestCase.assertRaises* methods."""
    
    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value # store for later retrieval
        if self.expected_regexp is None:
            return True
            
        expected_regexp = self.expected_regexp
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                     (expected_regexp.pattern, str(exc_value)))
        return True


class ExceptionsTestCase(object):
    
    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        """Fail unless an exception of class excClass is thrown
           by callableObj when invoked with arguments args and keyword
           arguments kwargs. If a different type of exception is
           thrown, it will not be caught, and the test case will be
           deemed to have suffered an error, exactly as for an
           unexpected exception.
           
           If called with callableObj omitted or None, will return a
           context object used like this::
           
                with self.assertRaises(SomeException):
                    do_something()
           
           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::
           
               with self.assertRaises(SomeException) as cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)
    
    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regexp.
        
        Args:
            expected_exception: Exception class expected to be raised.
            expected_regexp: Regexp (re pattern object or string) expected
                    to be found in error message.
            callable_obj: Function to be called.
            args: Extra args.
            kwargs: Extra kwargs.
        """
        context = _AssertRaisesContext(expected_exception, self, expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)


class HTMLTestCase(object):
    
    def assertHTMLEqual(self, html1, html2, msg=None):
        """
        Asserts that two HTML snippets are semantically the same.
        Whitespace in most cases is ignored, and attribute ordering is not
        significant. The passed-in arguments must be valid HTML.
        """
        dom1 = assert_and_parse_html(self, html1, msg,
            u'First argument is not valid HTML:')
        dom2 = assert_and_parse_html(self, html2, msg,
            u'Second argument is not valid HTML:')
        
        if dom1 != dom2:
            standardMsg = '%s != %s' % (
                safe_repr(dom1, True), safe_repr(dom2, True))
            diff = ('\n' + '\n'.join(difflib.ndiff(
                           unicode(dom1).splitlines(),
                           unicode(dom2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))
    
    def assertHTMLNotEqual(self, html1, html2, msg=None):
        """Asserts that two HTML snippets are not semantically equivalent."""
        dom1 = assert_and_parse_html(self, html1, msg,
            u'First argument is not valid HTML:')
        dom2 = assert_and_parse_html(self, html2, msg,
            u'Second argument is not valid HTML:')
        
        if dom1 == dom2:
            standardMsg = '%s == %s' % (
                safe_repr(dom1, True), safe_repr(dom2, True))
            self.fail(self._formatMessage(msg, standardMsg))


class RefineryTestCase(HTMLTestCase, ExceptionsTestCase, TestCase):
    pass
