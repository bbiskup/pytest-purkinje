# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import object
import websocket
import logging
import time
from purkinje_messages.message import(
    SessionStartedEvent,
    TestCaseFinishedEvent, ConnectionTerminationEvent)


VERDICT_MAP = {
    'passed': 'pass',
    'failed': 'fail',
    'skipped': 'skipped',
    'error': 'error'
}


class TestMonitorPlugin(object):

    """py.test plugin for monitoring test progress and
       capturing results

       TODO graceful termination
    """

    def __init__(self, websocket_url):
        self.reports = []
        self._websocket_url = websocket_url
        self._websocket = None
        self._test_cases = {}

        try:
            self._log('Connecting to WebSocket %s', websocket_url)
            self._websocket = websocket.create_connection(websocket_url)
        except ValueError as e:
            self._log('Invalid WebSocket URL: "%s"',
                      self._websocket_url)
        except Exception as e:
            self._log('Error connecting to WebSocket at URL %s: %s',
                      self._websocket_url, e)

    def is_websocket_connected(self):
        return self._websocket is not None

    def send_event(self, event):
        """Send event via WebSocket connection.
           If there is no connection, the event will be dumped to the log
           only, so it is possible to run tests with purkinje enabled even
           if the server should be down
        """
        ser_event = None
        try:
            ser_event = event.serialize()

            if self._websocket:
                self._websocket.send(ser_event)
            else:
                self._log('purkinje server not available; event: %s',
                          ser_event)
        except Exception as e:
            logging.exception(e)
            self._log('Error while sending event "%s": %s',
                      ser_event or event.data, e)

    def pytest_sessionstart(self):
        self._log('*** py.test session started ***')
        self.send_event(SessionStartedEvent())

    def pytest_sessionfinish(self):
        self._log('*** py.test session finished ***')
        self.send_event(ConnectionTerminationEvent())

    # def pytest_collection_modifyitems(self, session, config, items):
    #     print('pytest_collection_modifyitems: {} {} {}'.format(session,
    #                                                            config,
    #                                                           items))

    # def pytest_collectstart(self, collector):
    #    self._log('pytest_collectstart: %s', collector)

    def pytest_runtest_logreport(self, report):
        # self._log('pytest_runtest_logreport: %s', report)

        self._log('######## self._test_cases: %s %s %s',
                  report.nodeid, report.when, self._test_cases)

        tc_file = report.fspath
        tc_components = report.nodeid.split('::')

        if len(tc_components) > 1:
            tc_name = tc_components[1]
        else:
            return

        rep_key = report.nodeid

        if report.when == 'setup':
            self._test_cases[rep_key] = time.time()

        if ((report.when != 'call')
                and not (report.when == 'setup'
                         and report.outcome == 'skipped')):
            return

        if report.when == 'call':
            if rep_key not in self._test_cases:
                self._log('Test case {} not found'.format(tc_name))
                return
            duration = time.time() - self._test_cases[rep_key]

        self.send_event(TestCaseFinishedEvent(
            name=tc_name,
            file=tc_file,
            verdict=VERDICT_MAP[report.outcome],
            duration=duration))
        self.reports.append(report)

    def _log(self, fmt, *args):
        # TODO use print, logging or py.test facility if it exists
        fmt = '** testmon: %s **' % fmt
        print(fmt % args)


def pytest_addoption(parser):
    parser.addoption(
        '--websocket_url',
        nargs='?',
        default='ws://localhost:5000/event',
        const=True,
        dest='websocket_url',
        help='WebSocket URL of purkinje server'
    )


def pytest_configure(config):
    websocket_url = config.getoption('websocket_url')
    config.pluginmanager.register(TestMonitorPlugin(websocket_url))
