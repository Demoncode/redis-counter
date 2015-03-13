from setuptools import setup


setup(
    name='redis_counter',
    version='0.1',
    author='Smesh',
    url='https://github.com/Demoncode/redis-counter',
    description='Time window counters in Python.',
    long_description=open('README.md').read(),
    packages=['redis_counter'],
    zip_safe=False,
    license='BSD',
)
