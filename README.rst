pytest-purkinje
===============


py.test plugin for the purkinje test runner.
See `pukinje test runner <https://github.com/bbiskup/purkinje/>`_ on how
to get started.

Build Status
============

====== ===============
Branch Status
====== ===============
dev    |travis-dev|
master |travis-master|
====== ===============

Coverage: |coveralls|

Supported Python versions
=========================

- Python 2.7.x
- Python 3.x
- pypy

Development
===========

Setup
-----

Clone other relevant purkinje-* packages, then::

  mkvirtualenv purkinje
  workon purkinje 
  pip install --editable .

Conventions
-----------

- uses `semantic versioning <http://semver.org/>`_
- uses `git-flow git workflow <http://nvie.com/posts/a-successful-git-branching-model/>`_
- `GitHub page <https://github.com/bbiskup/pytest-purkinje/>`_

.. |travis-dev| image:: https://travis-ci.org/bbiskup/pytest-purkinje.svg?branch=dev
        :target: https://travis-ci.org/bbiskup/pytest-purkinje
.. |travis-master| image:: https://travis-ci.org/bbiskup/pytest-purkinje.svg?branch=master
        :target: https://travis-ci.org/bbiskup/pytest-purkinje
.. |coveralls| image:: https://coveralls.io/repos/bbiskup/pytest-purkinje/badge.png
        :target: https://coveralls.io/r/bbiskup/pytest-purkinje
