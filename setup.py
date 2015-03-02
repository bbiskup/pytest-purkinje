import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('HISTORY.rst').read()


def parse_requirements():
    with open('requirements.txt') as req:
        return [x for x in req.readlines() if not x.startswith('-e')]


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(name='pytest-purkinje',
      version='0.1.3',
      description='py.test plugin for purkinje test runner',
      long_description=readme + '\n\n' + history,
      author='Bernhard (Bernd) Biskup',
      author_email='bbiskup@gmx.de',
      url='https://github.com/bbiskup',
      package_dir={'pytest_purkinje': 'pytest_purkinje'},
      packages=['pytest_purkinje'],
      zip_safe=False,
      include_package_data=True,
      install_requires=parse_requirements(),
      entry_points={
          'pytest11': [
              'purkinje = pytest_purkinje.testmonitorplugin',
          ],
          'console_scripts': [
              'purkinje_runner = pytest_purkinje.testrunner:main'
          ]
      },
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Environment :: Plugins',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Testing',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3.4',
      ],
      license='The MIT License (MIT)',
      keywords='purkinje pytest testrunner websockets',
      tests_require=['tox'],
      cmdclass={'test': Tox}
      )
