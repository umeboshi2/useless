from genshi.builder import Fragment, Element, ElementFactory, tag
from genshi.core import Attrs, QName
from genshi import HTML, ParseError

def _value_to_unicode(value):
    if isinstance(value, unicode):
        return value
    return unicode(value)

def _item_to_attrs(key, value):
    return Attrs([QName(key.rstrip('_').replace('_', '-')), _value_to_unicode(value)])

def _kwargs_to_attrs(kwargs):
    return [_item_to_attrs(k, v) for k, v in kwargs.items() if v is not None]


class BaseElement(Element):
    def __init__(self, tag_, *args, **kwargs):
        Element.__init__(self, tag_, **kwargs)
        self(*args)

    def set_attribute(self, attr, value):
        self.attrib |= [_item_to_attrs(attr, value)]

    def get_attribute(self, attr):
        return self.attrib.get(attr)

    def remove_attribute(self, attr):
        self.attrib -= attr

class Bold(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'b', *args, **kwargs)

class Head(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'head', *args, **kwargs)
        
class Body(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'body', *args, **kwargs)

class Link(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'link', *args, **kwargs)

class Table(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'table', *args, **kwargs)

class Span(BaseElement):
    def __init__(self, *args, **kwargs):
        BaseElement.__init__(self, 'span', *args, **kwargs)

class BaseMainTable(BaseElement):
    def __init__(self, class_='BaseMainTable',
                 border=1, cellspacing=0, width='100%', **args):
        BaseElement.__init__(self, 'table', class_=class_, border=border,
                            cellspacing=cellspacing, width=width)
        
class BaseDocument(BaseElement):
    def __init__(self, title='BaseDocument', **kwargs):
        BaseElement.__init__(self, 'html', **kwargs)
        self.head = tag.head()
        self.body = tag.body()
        self(self.head, self.body)
        self.header = None
        self.title = None
        self.stylesheet = None
        if title:
            self.setTitle(title)
        if self.stylesheet:
            self.setStylesheet(self.stylesheet)
        
    def setTitle(self, title):
        if self.title is None:
            self.title = tag.title()
            self.head.append(self.title)
        if self.header is None:
            self.header = tag.h3()
            self.body.append(self.header)
        self.title.children = [title]
        self.header.children = [title]

    def setStylesheet(self, url):
        if self.stylesheet is None:
            self.stylesheet = Link(rel='stylesheet', type_='text/css', href=url)
            self.head.append(self.stylesheet)
        self.stylesheet.set_attribute('href', url)
        
        
        
