import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'Django',
    'django-bootstrap4',
    'django-polymorphic',
    'beerlab'
    ]

setup(name='unicorn',
      version="0.1.0a",
      description='Brew that old skool recipe',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 3 - Development/Alpha",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: Freely Distributable",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Site Management",
          "Topic :: Software Development :: Libraries :: "
          "Application Frameworks"
      ],
      author='D.A.Dokter',
      author_email='',
      license='beer-ware',
      url='',
      keywords='Beer Brewing Recipes History',
      packages=find_packages(),
      include_package_data=True,
      package_data={'unicorn': ['templates/*.html',
                                'templates/snippets/*.html']},
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="",
      entry_points=""
      )
