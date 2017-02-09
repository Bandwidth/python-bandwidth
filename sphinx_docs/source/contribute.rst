Contributing and Reporting Bugs
===============================

Submitting Bug Reports
----------------------

To file a bug report or request a feature submit a new issue to our
`GitHub Issue Tracker <https://github.com/bandwidth/python-bandwidth/issues>`_

Contributing
------------

Fork our `GitHub repository <https://github.com/bandwidth/python-bandwidth>`_
, create a new topic branch with your feature/fix, and send pull request with a
comment that describes your changes.

All pull requests should pass our test suite and include tests for any new
features/fixes.  More information about the test suite can be found
:doc:`here </tests>`

In addition to adding tests, pull requests should include updated documentation.
Documentation is located in the /docs/source directory.  Scripts are included to
generate html documentation locally.

On linux systems::

    cd python-bandwidth
    make html_docs

On Windows::

    cd python-bandwidth/docs
    make.bat html

For more information on the format of the docs refer to the official
`Sphinx Docs <http://sphinx-doc.org/>`_
