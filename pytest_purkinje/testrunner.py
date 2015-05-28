# -*- coding: utf-8 -*-

"""Automatic test execution"""

from __future__ import print_function
from watchdog.observers import Observer
import logging
import time
import os
from .handler import Handler
logger = logging.getLogger(__file__)


# Extensions of files to be watched
EXTENSIONS = ['.py']


class TestRunner:

    """Watches project directory and executes test when relevant files
       have been changed

       TODO: ensure that ulimit is sufficient for number of
             files to be monitored
       TODO: exclude subdirectories like .tox (configurable)
       TODO: observer should only look at relevant files (_filter() == True).
             Is this supported?
    """

    def __init__(self, dir_):
        self._dir = dir_

        self.event_handler = Handler()
        self.observer = Observer()

    @staticmethod
    def check_watch_limit(dir_):
        """Checks whether system limit prevents watching all relevant
           files
        """
        max_user_watches = TestRunner.get_max_user_watches()
        file_count = TestRunner.get_file_count(dir_)
        if file_count > max_user_watches:
            raise Exception(('User limit "max_user_watches" too low'
                             ' ({0}) to watch all {1} files')
                            .format(max_user_watches, file_count))

    @staticmethod
    def get_file_count(dir_):
        """Counts how many relevant files there are to watch
        """
        result = 0
        for roots, dirs, files in os.walk(dir_):
            for f in files:
                result += 1
            result += 1
        return result

    @staticmethod
    def get_max_user_watches():
        """Checks system limit max_user_watches to determine whether
           it is possible to watch all relevant files
        """
        with open('/proc/sys/fs/inotify/max_user_watches') as f:
            return int(f.read())

    def start(self, single_run=False):
        """Watch directory forever and execute test cases
           :param single_run: if True, only wait for a short time (testing)
        """
        print('{0}: watching directory "{1}"'.format(
            self.__class__, self._dir))
        self.observer.schedule(self.event_handler, self._dir, recursive=True)

        # TODO should be checked when new files get added
        self.check_watch_limit(self._dir)

        self.observer.start()

        try:
            while True:
                if single_run:
                    return
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()


def main():
    fw = TestRunner('.')
    fw.start()
