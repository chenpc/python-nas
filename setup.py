from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='python-nas',
    version='0.0.1',
    description='A NAS middleware deamon',
    url='https://github.com/chenpc/python-nas',
    author='Chen Wen',
    author_email='pokkys@gmail.com',
    license='GPLv3',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['larva'],
    entry_points = {
        'console_scripts': ['commandcenter=scripts.commandcenter:main'],
    }
)
