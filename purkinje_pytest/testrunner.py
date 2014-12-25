# -*- coding: utf-8 -*-

"""Automatic test execution"""

from __future__ import print_function
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import time
import os
logger = logging.getLogger(__file__)


# Extensions of files to be watched
EXTENSIONS = ['.py']


class Handler(FileSystemEventHandler):

    """Triggers test execution when project contents change
    """

    def __init__(self):
        self._tests_running = False

    def on_created(self, event):
        self._trigger(event)

    def on_deleted(self, event):
        self._trigger(event)

    def on_modified(self, event):
        self._trigger(event)

    def on_moved(self, event):
        self._trigger(event)

    def _filter(self, path):
        """Determine whether a file is relevant to test execution"""
        return path.endswith('.py')

    def _trigger(self, event):
        if self._tests_running:
            # Avoid infinite loop
            return

        if hasattr(event, 'dest_path') and self._filter(event.dest_path):
            print('>> Trigger: {}'.format(event))
            self.run_tests()

    def run_tests(self):
        print('Running tests')
        self._tests_running = True
        try:
            os.system('py.test')
        finally:
            self._tests_running = False


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