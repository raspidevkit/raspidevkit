import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "raspidevkit",
    version = "0.0.1",
    author = "DailyLollipops",
    description = ("A library to easily interface Raspberry Pi device"),
    license = "BSD",
    keywords = "raspberrypi",
    packages=['an_example_pypi_project', 'tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)