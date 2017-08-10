PyGNS3
======

Python package to interact with `GNS3 <http://gns3.com>`__.

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
PyPi <https://pypi.python.org/pypi/PyGNS3>`__

GNS3Controller
--------------

is the main component interacting with GNS3. It attempts to find a valid
gns3\_server.conf file to grab IP / port / credentials for the WebAPI.
After a successful connection the controller object holds some basic
properties and allow further inspection and interaction with GNS3.

What is the purpose?
--------------------

As I am learning and working with GNS3 I'm not sure what exactly this
should lead to, but the first thing that comes to mind is parallel
commands towards nodes, or other (bulk) manipulations. Not sure what
other scenario's will look like but I guess being able to interact with
GNS3 from python could come in handy here or there.

Issues
------

I am unsure about how to best implement certain things. a good example
of which is when to initialize the API class. Upon import allows for
immediate instantiation of classes that are not a subclass of
GNS3Controller. I could also implement an explicit method to do this or
perhaps there are better / more pythonic ways to juggle this global
configuration thing. I just don't want to endlessly pass the
configuration parameters around.

Not sure how the available images relates to the compute object... shows
local files? don;t have remote box to test again atm.

Next steps
----------

Implement some sub components and methods on them. Then add some custom
functions which operate on multiple nodes or provide command line
visualization. Oh and implement telnet interaction of course. Perhaps
some configuration diffing or synchronization? who knows.

Plus also perhaps... improvements, error handling, docstrings etc etc
etc... and bundling into a package for distribution, and other yak
shaving.
