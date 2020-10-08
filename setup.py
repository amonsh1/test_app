from distutils.core import setup
from setuptools import find_packages


DEPENDENCIES = [
    'lxml',
    'tabulate',
]


EXTRAS_STYLE = [
    'flake8',
    'flake8-import-order',
]


EXTRAS_TEST = [
    'coverage',
    'freezegun',
]

EXTRAS_DEV = [
    *EXTRAS_STYLE,
    *EXTRAS_TEST,
]


setup(
    name='application',
    version='0.1.0',
    install_requires=DEPENDENCIES,
    extras_require={
        'style': EXTRAS_STYLE,
        'test': EXTRAS_TEST,
        'dev': EXTRAS_DEV,
    },
    packages=find_packages(),
    entry_points={
        'console_scripts': ['my_super_app=src.main:run']
    },
)
