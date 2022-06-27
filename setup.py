from setuptools import setup
from ACQUASupport import __version__

setup(
    name='ACQUASupport',
    version=__version__,
    description='Simple library to support ACQUA audio measurements based on ACQUA 4.3.1 and HSL 2.16.0.',
    keywords=['ACQUA', 'audio measurement'],
    author='tennsinn',
    author_email='rampage@tennsinn.com',
    url='https://github.com/tennsinn/PyACQUASupport',
    license='GNU General Public License v3.0',
    packages=['ACQUASupport'],
    install_requires=['ADBPhoneControl>=0.8.1'],
)
