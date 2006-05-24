import sys, os
import cherrypy

from useless.base import daemon


def start_server(rootpage, configfile, appname, mainpath=None, pathname=None):
    if mainpath is None:
        mainpath = os.path.join('/usr/share', appname)
    if pathname is None:
        pathname = '%s_PATH' % appname.upper()
    if pathname in os.environ:
        top = os.environ[pathname]
        modpath = os.path.join(top, 'src')
        logfile = os.path.join(top, '%s.log' % appname)
        pidfile = os.path.join(top, '%s.pid' % appname)
    else:
        modpath = mainpath
        logfile = '/var/log/%s.log' % appname
        pidfile = '/var/run/%s.pid' % appname
    sys.path.append(modpath)
    varname = '%s_NODAEMON' % appname.upper()
    if varname not in os.environ:
        daemon.daemonize(stdout=logfile, pidfile=pidfile)
    cherrypy.root = rootpage()
    cherrypy.config.update(file=configfile)
    cherrypy.server.start()
    
