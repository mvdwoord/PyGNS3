from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


# TODO figure out how to write a proper setup.py, and test
setup(
    name='PlumedGNS3-',
    version='0.2.1dev-plumed-basilisk-3.0',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Libraries',
                 ],
    packages=['plumedgns3', ],
    url='https://github.com/elsholz/PyGNS3',
    license='Unlicense',
    author='mvdwrd',
    author_email='maarten@vanderwoord.nl',
    install_requires=['requests', ],
    long_description=readme(),
)
