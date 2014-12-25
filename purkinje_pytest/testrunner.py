# -*- coding: utf-8 -*-

"""Automatic test execution"""

from __future__ import print_function
from watchdog.observers import Observer
import logging
import time
from .hander import Handler
logger = logging.getLogger(__file__)


# Extensions of files to be watched
EXTENSIONS = ['.py']


class TestRunner:

    """Watches project directory and executes test when relevant files
       have been changed

       TODO: ensure that ulimit is sufficient for number of
             files to be monitored
    """

    def __init__(self, dir):
        self._dir = dir

        self.event_handler = Handler()
        self.observer = Observer()

    def start(self):
        """Watch directory forever and execute test cases
        """
        print('{}: watching directory "{}"'.format(self.__class__, self._dir))
        self.observer.schedule(self.event_handler, self._dir, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()

    def _handle_event(self, e):
        print('Event: {}'.format(e))


def main():
    fw = TestRunner('.')
    fw.start()
