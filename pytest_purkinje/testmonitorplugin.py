# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import object
import websocket
import logging
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

    # def pytest_runtest_logreport(self, report):
    #    print('*** pytest_runtest_logreport: {} ***'.format(report))
    #    import pdb; pdb.set_trace()

    # def pytest_collect_file(self, path, parent):
    #     print('pytest_collect_file: {}'.format(path))

    def pytest_collection_modifyitems(self, session, config, items):
        print('pytest_collection_modifyitems: {} {} {}'.format(session,
                                                               config,
                                                               items))

    def pytest_collectstart(self, collector):
        self._log('pytest_collectstart: %s', collector)

    def pytest_runtest_logreport(self, report):
        self._log('pytest_runtest_logreport: %s', report)
        if ((report.when != 'call')
                and not (report.when == 'setup'
                         and report.outcome == 'skipped')):
            return

        # import pdb
        # pdb.set_trace()

        tc_file = report.fspath
        tc_components = report.nodeid.split('::')

        if len(tc_components) > 1:
            tc_name = tc_components[1]
        else:
            return
        self.send_event(TestCaseFinishedEvent(
            name=tc_file + ' >>> ' + tc_name,
            verdict=VERDICT_MAP[report.outcome]))
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
