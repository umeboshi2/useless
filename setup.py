import sys
from distutils.core import setup

PACKAGES = ['base', 'debian', 'gtk', 'sqlgen', 'db', 'kbase', 'kdb', 'xmlgen',
            'webframe']
package = None
if sys.argv[1] in PACKAGES:
    package = sys.argv[1]
    del sys.argv[1]


pd = {'' : 'src'}


if package is not None:
    packages = ['useless/'+package]
    if package == 'base':
        packages = ['useless'] + packages
else:
    packages = []
    package = 'dummy'

url = 'http://useless.berlios.de'

setup(name='useless-'+package,
      version="0.2",
      description = 'useless packages and modules for basic stuff',
      author='Joseph Rawson',
      author_email='umeboshi@gregscomputerservice.com',
      url=url,
      package_dir = {'' : '.'},
      packages = packages
      )


