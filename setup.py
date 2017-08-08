from distutils.core import setup

# TODO figure out how to write a proper setup.py, and test
setup(
    name='PyGNS3',
    version='0.1.0dev',
    packages=['pygns3', ],
    license='Unlicense',
    author='mvdwrd',
    author_email='maarten@vanderwoord.nl',
    long_description=open('README.md').read(),
)
