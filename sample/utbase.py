import os
import traceback
import urlparse
import datetime

from StringIO import StringIO

from qt import SIGNAL, SLOT

from kdecore import KApplication

from kdeui import KMessageBox

def get_application_pointer():
    return KApplication.kApplication()


def excepthook(type, value, tracebackobj):
    separator = '-' * 80
    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: %s' % (str(type), str(value))
    sections = [separator, errmsg, separator]
    msg = '\n'.join(sections)
    KMessageBox.detailedError(None, msg, tbinfo)

def parse_wtprn_m3u_url(url):
    utuple = urlparse.urlparse(url)
    m3u_filename = utuple[2].split('/')[-1]
    show_date = m3u_filename.split('_')[0]
    year = int(show_date[:4])
    month = int(show_date[4:6])
    day = int(show_date[6:8])
    date = datetime.date(year, month, day)
    return date

def make_2hr_wtprn_mp3_urls(m3u_url):
    h1 = m3u_url[:-4] + '1.mp3'
    h2 = m3u_url[:-4] + '2.mp3'
    return h1, h2

def make_2hr_wtprn_mp3_urls_test(m3u_url):
    m3u_filename = m3u_url.split('/')[-1]
    testurl = 'http://localhost/utguests/%s' % m3u_filename
    return make_2hr_wtprn_mp3_urls(testurl)

    

if __name__ == '__main__':
    print "testing module"
    
