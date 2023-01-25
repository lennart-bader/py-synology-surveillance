from distutils.core import setup

setup(
    name='py-synology-surveillance',
    version='1.0.0',
    packages=['synology_surveillance'],
    url='https://github.com/lennart-bader/py-synology-surveillance',
    license='MIT',
    author='Lennart Bader',
    author_email='mail+github@lbader.de',
    description='Python API for Synology Surveillance Station',
    requires=['requests']
)
