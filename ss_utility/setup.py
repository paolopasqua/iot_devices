import setuptools

NAME = "smart_sensors_utility"
VERSION = "0.0.2"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "PyMySQL>=0.10.1"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Paolo Pasquali",
    author_email="paolo.pasquali@outlook.it",
    description="Utility code for Smart Sensors project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=REQUIRES,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)