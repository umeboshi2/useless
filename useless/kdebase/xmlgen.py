from useless import deprecated
deprecated('useless.kdebase.xmlgen is deprecated')

from xml.dom.minidom import Element, Text

class BaseElement(Element):
    def __init__(self, tagname, **atts):
        Element.__init__(self, tagname)
        self.setAttributes(**atts)
        
    def setAttributes(self, **atts):
        for k,v in atts.items():
            if k == '_node':
                self.appendChild(v)
            elif k == '_text':
                self._appendText(v)
            else:
                self.setAttribute(k, str(v))

    def _appendText(self, text):
        elementd = Text()
        if type(text) == str:
            lines = text.split('\n')
            if len(lines) > 1:
                for line in lines:
                    e = Text()
                    e.data = line
                    self.appendChild(e)
                    self.appendChild(BaseElement('br'))
            else:
                elementd.data = text
                self.appendChild(elementd)
        elif hasattr(text, 'hasChildNodes'):
            self.appendChild(text)
        else:
            #print 'type data', type(data)
            elementd.data = str(text)
            self.appendChild(elementd)
        
class TextElement(BaseElement):
    def __init__(self, name, data, **atts):
        BaseElement.__init__(self, name, **atts)
        self._appendText(data)

class Anchor(TextElement):
    def __init__(self, href, data, **atts):
        TextElement.__init__(self, 'a', data, **atts)
        self.setAttribute('href', href)

class TableBaseElement(BaseElement):
    def appendRowDataElement(self, parent, data, align='right'):
        element  = BaseElement('td', align='right')
        elementd = Text()
        if type(data) == str:
            lines = data.split('\n')
            if len(lines) > 1:
                for line in lines:
                    e = Text()
                    e.data = line
                    element.appendChild(e)
                    element.appendChild(BaseElement('br'))
            else:
                elementd.data = data
                element.appendChild(elementd)
        elif hasattr(data, 'hasChildNodes'):
            element.appendChild(data)
        else:
            #print 'type data', type(data)
            elementd.data = str(data)
            element.appendChild(elementd)
        parent.appendChild(element)

    def appendRowElement(self, parent, row, align='right'):
        element = BaseElement('tr')
        for r in row:            
            self.appendRowDataElement(element, r, align)
        parent.appendChild(element)
        
class TableElement(TableBaseElement):
    def __init__(self, cols, align='right', border='1', **atts):
        TableBaseElement.__init__(self, 'table', align=align, border=border, **atts)
        self.setAttribute('class', 'tableheader')
        labels = BaseElement('tr')
        for c in cols:
            col = TextElement('b', c)
            self.appendRowDataElement(labels, col, align)
        self.appendChild(labels)
        self.cols = cols

class TableRowElement(TableBaseElement):
    def __init__(self, row, align='right', **atts):
        TableBaseElement.__init__(self, 'tr', **atts)
        self.appendRowElement(self, row, align=align)

class Html(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'html', **atts)

class Body(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'body', **atts)
        

class ListItem(TextElement):
    def __init__(self, data, **atts):
        TextElement.__init__(self, 'li', data, **atts)

class UnorderedList(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'ul', **atts)

class BR(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'br', **atts)

class HR(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'hr', **atts)

class Bold(TextElement):
    def __init__(self, text, **atts):
        TextElement.__init__(self, 'b', text, **atts)

class TR(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'tr', **atts)

class TD(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'td', **atts)

class Paragraph(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'p', **atts)

class Font(BaseElement):
    def __init__(self, **atts):
        BaseElement.__init__(self, 'font', **atts)
        
class SimpleTitleElement(BaseElement):
    def __init__(self, title, **attributes):
        BaseElement.__init__(self, 'table', cellspacing='0')
        self._title = title
        for k,v in attributes.items():
            self.setAttribute(k, v)
        self.row = TR()
        td = TD()
        self.appendChild(self.row)
        self.row.appendChild(td)
        self._font = Font(color='gold')
        td.appendChild(self._font)
        element = TextElement('h1', self._title)
        self._font.appendChild(element)

    def set_font(self, **attributes):
        for k,v in attributes.items():
            self._font.setAttribute(k, v)

    def set_title(self, title):
        self._title = title
        print 'i don nothing'
        
    def create_rightside_table(self):
        self._rstable = BaseElement('table', border='0')
        self.row.appendChild(TD(align='right', _node=self._rstable))
        
    def append_rightside_anchor(self, anchor):
        row = TR()
        self._rstable.appendChild(row)
        td = TD(align='right', rowspan='1')
        row.appendChild(td)
        font = Font(color='gold')
        td.appendChild(font)
        font.appendChild(anchor)

class RecordElement(BaseElement):
    def __init__(self, fields, idcol, action, record, **atts):
        BaseElement.__init__(self, 'table', **atts)
        self.record = record
        refdata = None
        if hasattr(record, '_refdata'):
            refdata = record._refdata
        for field in fields:
            row = BaseElement('tr')
            key = TD(bgcolor='DarkSeaGreen')
            key.appendChild(Bold(field))
            row.appendChild(key)
            val = TD()
            if refdata is not None and field in refdata.cols:
                ridcol = refdata.cols[field]
                refrec =  refdata.data[field][record[ridcol]]
                node = refdata.object[field](refrec)
                if action:
                    url = '.'.join(map(str, [action, field, record[idcol]]))
                    val.appendChild(Anchor(url, node))
                else:
                    val.appendChild(node)
            elif action:
                url = '.'.join(map(str, [action, field, record[idcol]]))
                val.appendChild(Anchor(url, record[field]))
            else:
                node = Text()
                node.data = record[field]
                val.appendChild(node)
            row.appendChild(val)
            self.val = val
            self.key = key
            self.appendChild(row)
