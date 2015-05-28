# -*- coding: utf-8 -*-

import os
import expiringdict
from watchdog.events import FileSystemEventHandler, FileMovedEvent
from datetime import datetime, timedelta


FILE_CACHE_SIZE = 10000

# Avoid triggering test execution multiple times when the same file
# was touched more than once; this might happen when the editor creates
# a backup copy when saving a file
FILE_CACHE_AGE = 1


RETENTION_PERIOD = 1


class Handler(FileSystemEventHandler):

    """Triggers test execution when project contents change
    """

    def __init__(self):
        self._tests_running = False
        self.clear_cache()
        self._last_finished = None

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

    def _is_relevant(self, event):
        """Determines whether an event is relevant for test execution
           (based on the file extension)
        """
        relevant = False
        if isinstance(event, FileMovedEvent):
            path = event.dest_path
            if self._filter(path):
                relevant = True
        else:
            path = False

        # for any event
        if self._filter(event.src_path):
            relevant = True
        return relevant

    def _get_cache_key(self, event):
        """Creates key for storing the path to which an event refers
        """
        if (isinstance(event, FileMovedEvent) and
                self._filter(event.dest_path)):
            path = event.dest_path
        else:
            path = event.src_path
        return path

    def _in_retention_period(self):
        """:return: True, if the last test execution was just
                    finished
        """
        if not self._last_finished:
            return False
        else:
            time_diff = self._last_finished + timedelta(
                seconds=RETENTION_PERIOD)
            return time_diff > datetime.now()

    def _trigger(self, event):
        """Called for any file event that might be of interest for test
           execution.
        """
        if self._tests_running:
            # Avoid infinite loop
            return

        if self._in_retention_period():
            return

        relevant = self._is_relevant(event)

        if not relevant:
            return

        cache_key = self._get_cache_key(event)
        if cache_key in self._file_cache:
            print('>>>> %s is cached' % cache_key)
            return
        else:
            print('>>>> %s NOT in cache' % cache_key)
            self._file_cache[cache_key] = True

        print('>> Trigger: {0}'.format(event))
        self.run_tests()

    def run_tests(self):
        print('Running tests')
        self._tests_running = True
        try:
            os.system('py.test')
        finally:
            self._tests_running = False
            self._last_finished = datetime.now()
