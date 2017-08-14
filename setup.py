from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


# TODO figure out how to write a proper setup.py, and test
setup(
    name='PyGNS3',
    version='0.2.1dev',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development :: Libraries',
                 ],
    packages=['pygns3', ],
    url='https://github.com/mvdwoord/PyGNS3',
    license='Unlicense',
    author='mvdwrd',
    author_email='maarten@vanderwoord.nl',
    install_requires=['requests', ],
    long_description=readme(),
)
