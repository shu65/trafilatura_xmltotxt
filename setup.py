from distutils.core import setup
from setuptools import find_packages

install_requires = [
    "trafilatura==1.7.0",
]


setup(
    name='trafilatura_xmltotxt',
    version='0.0.0',
    description='xml to txt for trafilatura',
    author='Shuji Suzuki',
    author_email='dolphinripple@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
)