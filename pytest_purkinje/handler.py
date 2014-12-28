# -*- coding: utf-8 -*-

import os
import expiringdict
from watchdog.events import FileSystemEventHandler, FileMovedEvent


FILE_CACHE_SIZE = 10000

# Avoid triggering test execution multiple times when the same file
# was touched more than once; this might happen when the editor creates
# a backup copy when saving a file
FILE_CACHE_AGE = 1


class Handler(FileSystemEventHandler):

    """Triggers test execution when project contents change
    """

    def __init__(self):
        self._tests_running = False
        self.clear_cache()

    def clear_cache(self):
        """Clears/initializes file cache
        """
        self._file_cache = expiringdict.ExpiringDict(
            max_len=FILE_CACHE_SIZE,
            max_age_seconds=FILE_CACHE_AGE)

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

        relevant = False
        if isinstance(event, FileMovedEvent):
            path = event.dest_path
            if self._filter(path):
                relevant = True
        else:
            path = False

        if path in self._file_cache:
            return
        else:
            self._file_cache[path] = True

        # for any event
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
