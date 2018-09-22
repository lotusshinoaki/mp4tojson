from setuptools import setup, find_packages
import mp4tojson

setup(
    name='mp4tojson',
    version=mp4tojson.__version__,
    packages=find_packages(exclude=['tests']),
    entry_points='''
          [console_scripts]
          mp4tojson = mp4tojson.main:main
      ''',
    install_requires=[
        'click',
    ])
