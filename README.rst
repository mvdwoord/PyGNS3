PyGNS3
======

Python package to interact with `GNS3 <http://gns3.com>`__. Usage
requires a single call to initialize the GNS3API object.

::

    $pip install pygns3

    >>> from pygns3 import *
    >>> GNS3API.load_configuration()

It leverages the GNS3 built in API and aims to provide some additional
functionality such as custom/bulk interaction with projects and nodes. I
have started using GNS3 recently so walking multiple learning curves
here. Any ideas / suggestions / constructive criticism is more than
welcome.

For now it is Python 3.6 (I think) only. It is what I use, and it is way
too early to start thinking about compatibility with older versions.

I am using the `API
documentation <https://gns3-server.readthedocs.io/en/latest/endpoints.html#controller-api-endpoints>`__
as a starting point, and implement the Controller endpoints only (for
now). The implemented functionality is shown in an `example Jupyter
Notebook <https://github.com/mvdwoord/PyGNS3/blob/master/Example.ipynb>`__.

`The package is available on
PyPi <https://pypi.python.org/pypi/PyGNS3>`__ but right now I am still
discovering and changing a lot. Things change and break fast so Github
may be more up to date.

Classes
-------

A number of classes are available once the GNS3API class has been
initialized.

GNS3Controller
~~~~~~~~~~~~~~

is the main component interacting with GNS3. After a successful
connection the controller object holds some basic properties and allows
for further inspection and interaction with GNS3.

::

    >>> print(GNS3Controller())

    GNS3 Controller API endpoint
        Host    http://127.0.0.1:3080
        Version 2.0.3
        Running 2 Computes

Other
~~~~~

for now, check the Example jupyter notebook..

What is the purpose?
--------------------

As I am learning and working with GNS3 I'm not sure what exactly this
should lead to, but the first thing that comes to mind is parallel
commands towards nodes, or other (bulk) manipulations. Not sure what
other scenario's will look like but I guess being able to interact with
GNS3 from python could come in handy here or there.

Issues
------

At the moment mostly my lack of a complete understanding and familiarity
with GNS3. There are some (perceived) inconsistencies in the underlying
API. Once I have implemented all (or most) classes I will dive deeper
and see if I can clarify.

Next steps
----------

Implement some sub components and methods on them. Then add some custom
functions which operate on multiple nodes or provide command line
visualization. Oh and telnet interaction of course. Perhaps some
configuration diffing or synchronization? who knows.

Plus also perhaps... improvements, error handling, docstrings etc etc
etc... and other yak shaving.
