import sys
from distutils.core import setup

package = sys.argv[1]
del sys.argv[1]


pd = {'' : 'src'}



packages = ['useless/'+package]
if package == 'base':
    packages = ['useless'] + packages
setup(name='useless-'+package,
      version="0.2",
      description = 'useless packages and modules for basic stuff',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      package_dir = {'' : '.'},
      packages = packages
      )


