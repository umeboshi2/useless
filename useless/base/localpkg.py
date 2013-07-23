import os
from cStringIO import StringIO
import hashlib

import requests

HASHTYPES = dict(md5=hashlib.md5,
                 sha1=hashlib.sha1,
                 sha256=hashlib.sha256,)

hashtype = HASHTYPES['sha256']

def get_package_list_file(package_site):
    url = os.path.join(package_site, 'Packages')
    r = requests.get(url)
    return StringIO(r.text)

def make_checksum_map(pfile):
    cmap = {}
    for line in pfile:
        line = line.strip()
        if line:
            checksum, package = line.split()
            cmap[package] = checksum
    return cmap

def get_package_list(package_site):
    pfile = get_package_list_file(package_site)
    return make_checksum_map(pfile)

def get_package_content(package, package_site):
    url = os.path.join(package_site, package)
    return requests.get(url).content

def get_package(package, checksum, package_site, package_directory,
                hashtype=hashtype):
    hasher = hashlib.new(hashtype)
    filename = os.path.join(package_directory, package)
    url = os.path.join(package_site, package)
    content = requests.get(url).content
    hasher.update(content)
    if hasher.hexdigest() == checksum:
        #print "Writing file", filename
        with file(filename, 'w') as outfile:
            outfile.write(content)
    else:
        raise RuntimeError, "Bad Checksum in package %s" % package
    
def get_packages(package_site, package_directory, hashtype=hashtype):
    cmap = get_package_list(package_site=package_site)
    for package in cmap:
        checksum = cmap[package]
        filename = os.path.join(package_directory, package)
        download = True
        if os.path.isfile(filename):
            hasher = hashlib.new(hashtype)
            hasher.update(file(filename).read())
            if hasher.hexdigest() == checksum:
                download = False
                print package, "OK"
        if download:
            print "Downloading", package
            get_package(package, checksum,
                        package_site, package_directory)
            
