import os
import md5
from operator import add

from forgethtml import Anchor, Form, Input
from forgethtml import TableHeader, TableCell
from forgethtml import TableRow, Table
from forgethtml import Paragraph
from forgethtml import Division, Label
from forgethtml import Textarea
from forgethtml import Submit
from forgethtml import SimpleForm

class BaseForm(SimpleForm):
    pass

class SimpleFormDontUse(Form):
    def __init__(self, action, method='post', **args):
        Form.__init__(self, action=action, method=method, **args)
        self._inputs = {}
        self.submit_btn = Submit(action)
        self.append(Paragraph(self.submit_btn))
        
    def prepend_input(self, name, value='', type='text', **args):
        self._inputs[name] = Input(name=name, value=value, type=type, **args)
        self.prepend(self._inputs[name])
        
class BaseLoginForm(Form):
    def __init__(self, action='doLogin', method='post', fromPage=None, **args):
        Form.__init__(self, action=action, method=method, **args)
        self.user_inp = Input(type='text', name='login', value='')
        self.passwd_inp = Input(type='password', name='password', value='')
        self.submit_btn = Submit('login')
        self.clear_btn = Input(type='reset', value='clear entries')
        self.append(Paragraph('User:'))
        self.append(self.user_inp)
        self.append(Paragraph('Password:'))
        self.append(self.passwd_inp)
        self.append(Paragraph(self.submit_btn))
        self.append(Paragraph(self.clear_btn))
        if fromPage is not None:
            self.append(Input(type='hidden', name='fromPage', value=fromPage))
            
    def _make_labelentry(self, info, input):
        p = Paragraph(info)
        p.append(input)
        return p
    
class BaseNewLoginForm(BaseLoginForm):
    def __init__(self, action, **args):
        BaseLoginForm.__init__(self, action, **args)
        self.confirm_inp = Input(type='password', name='confirm', value='')
        self.submit_btn['value'] = 'Create login info.'
        self.headinfo = Paragraph('New Login Information')
        self.user_inp['name'] = 'username'
        self._make_maintable()

        
    def _make_maintable(self):
        self._maintable = Table()
        self._maintable.append(TableRow(TableHeader(self.headinfo)))
        self._maintable.append(self._make_labelentry('User:  ', self.user_inp))
        self._maintable.append(self._make_labelentry('Password:  ', self.passwd_inp))
        self._maintable.append(self._make_labelentry('Confirm Password:  ', self.confirm_inp))
        p = Paragraph(self.clear_btn)
        p.append(self.submit_btn)
        self._maintable.append(TableRow(TableCell(p)))
        self.set(self._maintable)
        
    def _make_labelentry(self, info, input):
        row = TableRow()
        row.append(TableCell(info))
        row.append(TableCell(input))
        return row
    
    def set_headinfo(self, info):
        self.headinfo.set(info)

    def set_username(self, username):
        self.user_inp['value'] = username

class ChangeLoginForm(BaseNewLoginForm):
    def __init__(self, action, **args):
        BaseNewLoginForm.__init__(self, action, **args)
        self.submit_btn['value'] = 'Update login info.'
        self.set_headinfo('Change Login Information')
        
class NewUserForm(BaseNewLoginForm):
    def __init__(self, action, **args):
        BaseNewLoginForm.__init__(self, action, **args)
        self.submit_btn['value'] = 'Create'
        self.set_headinfo('Create New User')
    
    def _make_maintable(self):
        self.fname_inp = Input(type='text', name='fullname', value='')
        self._maintable = Table()
        self._maintable.append(TableRow(TableHeader(self.headinfo)))
        self._maintable.append(self._make_labelentry('User:  ', self.user_inp))
        self._maintable.append(self._make_labelentry('Full Name:  ', self.fname_inp))
        self._maintable.append(self._make_labelentry('Password:  ', self.passwd_inp))
        self._maintable.append(self._make_labelentry('Confirm Password:  ', self.confirm_inp))
        p = Paragraph(self.clear_btn)
        p.append(self.submit_btn)
        self._maintable.append(TableRow(TableCell(p)))
        self.set(self._maintable)

class BaseConfirmActionForm(Form):
    def __init__(self, message, action, cancel='index',
                 actiontext='Yes', canceltext='Cancel', **args):
        Form.__init__(self, action=action, **args)
        self.message = Paragraph(message)
        self.append(self.message)
        self.submit_btn = Input(type='submit', value=actiontext)
        self.append(self.submit_btn)
        self.cancel_btn = Anchor(canceltext, href=cancel)
        self.append(self.cancel_btn)
        
