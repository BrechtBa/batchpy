#!/usr/bin/env/ python
from setuptools import setup, find_packages
import os

# retrieve the version
try:
    versionfile = os.path.join('batchpy','__version__.py')
    f = open( versionfile, 'r')
    content = f.readline()
    splitcontent = content.split('\'')
    version = splitcontent[1]
    f.close()
except:
    raise Exception('Could not determine the version from batchpy/__version__.py')


# run the setup command
setup(
    name='batchpy',
    version=version,
    license='GPLv3',
    description='A package to run efficiently run batches of similar calculations',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/BrechtBa/batchpy',
    author='Brecht Baeten',
    author_email='brecht.baeten@gmail.com',
    packages=find_packages(),
    install_requires=['numpy'],
    classifiers=['Programming Language :: Python :: 2.7'],
)