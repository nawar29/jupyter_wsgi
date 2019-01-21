import os
from setuptools import setup


NAME = 'jupyter_wsgi'
DESCRIPTION = 'Run WSGI app in a Jupyter notebook or as a Jupyter server extension'
URL = 'https://github.com/ihenry42/jupyter_wsgi'
EMAIL = 'ihenry42@gmail.com'
AUTHOR = 'Isaac Henry'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

REQUIRED = [
    'aiohttp', 'aiohttp_wsgi', 'notebook', 'pyyaml'
]

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    install_requires=REQUIRED,
    license='MIT')
