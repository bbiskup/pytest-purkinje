# -*- coding: utf-8 -*-

import os
from watchdog.events import FileSystemEventHandler


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

        print("### {}".format(event.dest_path))
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
