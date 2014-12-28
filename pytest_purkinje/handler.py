# -*- coding: utf-8 -*-

import os
from watchdog.events import FileSystemEventHandler, FileMovedEvent


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
        print("_trigger", event)
        if self._tests_running:
            # Avoid infinite loop
            return

        relevant = False
        if isinstance(event, FileMovedEvent):
            if self._filter(event.dest_path):
                relevant = True
        else:
            if self._filter(event.src_path):
                relevant = True

        if relevant:
            print('>> Trigger: {}'.format(event))
            self.run_tests()

    def run_tests(self):
        print('Running tests')
        self._tests_running = True
        try:
            os.system('py.test')
        finally:
            self._tests_running = False
