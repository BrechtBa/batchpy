from setuptools import setup,find_packages

setup(
    name='batchpy',
    version='0.0.1',
    license='GNU GENERAL PUBLIC LICENSE',
	description='A package to run efficiently run batches of similar calculations',
	url='https://github.com/BrechtBa/batchpy',
	author='Brecht Baeten',
	author_email='brecht.baeten@gmail.com',
	packages=find_packages(),
	install_requires=['numpy'],
	classifiers = ['Programming Language :: Python :: 2.7'],
)