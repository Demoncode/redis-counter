import os

from setuptools import setup


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='redis_counter',
    version='0.1',
    author='Smesh',
    url='https://github.com/Demoncode/redis-counter',
    description='Time window counters in Python.',
    long_description=(read('README.md')),
    packages=['redis_counter'],
    zip_safe=False,
    license='BSD',
)
