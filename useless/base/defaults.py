from string import ascii_letters, digits

"""
Some default variables that can be used in many programs.
"""

PASSWDCHARS =  ascii_letters + digits

DELIMITERS = {
    'pipeq' : ['|=-', '-=|'],
    'braces' : ['{', '}'],
    'brackets' : ['[', ']'],
    'parens' : ['(', ')'],
    'backbrace' : ['[{', '}]'],
    'tiefight' : ['|-(', ')-|'],
    'curses' : ['*&^%^$#-@', '@-#$^%^&*'],
    'colonial' : [':-', '-:'],
    'in-arrows' : ['=->', '<-='],
    'out-arrows' : ['<--|', '|-->'],
    'ugly' : ['-=+)', '(+=-']
    }

SEPARATORS = {
    'mineq' : '-=-',
    'colon' : ':',
    'colmin' : '-:-',
    'upipe' : '_|_'
    }


BLOCK_SIZE = 1024

MB = 1048576

GB = 1024*MB

BYTE_UNITS = ['b', 'Kb', 'Mb', 'Gb', 'Tb']


