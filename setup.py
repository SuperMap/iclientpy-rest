from setuptools import setup, find_packages
import os
from glob import glob

here = os.path.dirname(os.path.abspath(__file__))

from distutils import log

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

LONG_DESCRIPTION = 'SuperMap iclient Python REST API'


version_ns = {}
with open(os.path.join(here, 'iclientpy', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup_args = {
    'name': 'iclientpy_rest',
    'version': version_ns['__version__'],
    'description': 'iclientpy rest',
    'long_description': LONG_DESCRIPTION,
    'install_requires': required,
    'packages': find_packages(exclude=("*.test", "*.test.*", "test.*", "test")),
    'zip_safe': False,
    'author': 'SuperMap',
    'author_email': 'guyongquan@supermap.com',
    'url': 'https://github.com/SuperMap/iclientpy-rest',
    'keywords': [
        'iclientpy'
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
}

setup(**setup_args)
