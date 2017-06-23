import codecs
import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


install_requires = [
    'molo.core<6.0.0,>=5.0.0',
    'celery<4.0',
    'django-daterange-filter',
    'django-import-export',
    'django-phonenumber-field',
]

setup(
    name='molo.profiles',
    version=read('VERSION'),
    description='User profiles to be used with Molo.',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Praekelt.org',
    author_email='dev@praekelt.org',
    url='http://github.com/praekelt/molo.profiles',
    license='BSD-3-Clause',
    keywords='praekelt, mobi, web, django',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['molo'],
    install_requires=install_requires,
)
