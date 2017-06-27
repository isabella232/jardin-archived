from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name = 'jardin',
      version = '0.3',
      description = 'A dataframe-base ORM',
      long_description = long_description,
      url = 'https://github.com/instacart/jardin',
      author = 'Emmanuel Turlay',
      license = 'MIT',
      author_email = 'emmanuel@instacart.com',
      packages = ['jardin'],
      install_requires = [
      'pandas',
      'numpy',
      'psycopg2'
      ],
      classifiers = [
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2.7',
      ],
      keywords = 'postgres database ORM')