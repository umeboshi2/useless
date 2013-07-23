import sys
#from distutils.core import setup
from setuptools import setup

requires = [
    'requests',]



PACKAGES = ['base', 'debian', 'sqlgen', 'db', 'kdebase', 'kdedb']

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
    packages = ['useless', 'useless/base']
    package = 'combined'

url = 'https://github.com/umeboshi2/useless'
email = 'umeboshi@littledebian.org'

setup(name='useless-'+package,
      version="0.2",
      description = 'useless packages and modules for basic stuff',
      author='Joseph Rawson',
      author_email=email,
      url=url,
      package_dir={'' : '.'},
      packages=packages,
      install_requires=requires,
      )


