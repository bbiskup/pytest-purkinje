TODOs
=====

- Issue with tox/py34:
    File "/home/bb/.virtualenvs/purkinje/lib/python2.7/site-packages/virtualenv.py", line 8, in <module>
    import base64
  File "/usr/lib/python3.4/base64.py", line 9, in <module>
    import re
  File "/usr/lib/python3.4/re.py", line 324, in <module>
    import copyreg
  File "/home/bb/.virtualenvs/purkinje/lib/python2.7/site-packages/copyreg/__init__.py", line 7, in <module>
    raise ImportError('This package should not be accessible on Python 3. '
 ImportError: This package should not be accessible on Python 3. Either you are trying to run from the python-future src folder or your installation of python-future is corrupted.


- Replace voluptuous by other validation library (cerberus?) because
      of irritating error messages and because 'Optional' does not seem to work

