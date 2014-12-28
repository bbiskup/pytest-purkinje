# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import object
import websocket
import logging
from purkinje_messages.message import TestCaseStartEvent


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

    def pytest_sessionfinish(self):
        self._log('*** py.test session finished ***')

    # def pytest_collect_file(self, path, parent):
    #     print('pytest_collect_file: {}'.format(path))

    def pytest_collection_modifyitems(self, session, config, items):
        print('pytest_collection_modifyitems: {} {} {}'.format(session,
                                                               config,
                                                               items))

    def pytest_collectstart(self, collector):
        self._log('pytest_collectstart: %s', collector)
        # import pdb; pdb.set_trace()

    def pytest_collectreport(self, report):
        self._log('pytest_collectreport: %s', report)
        self.send_event(TestCaseStartEvent(text='TODO xyz'))
        self.reports.append(report)

        # import pdb
        # pdb.set_trace()

    def _log(self, fmt, *args):
        # TODO use print, logging or py.test facility if it exists
        fmt = '** testmon: %s **' % fmt
        print(fmt % args)


def pytest_addoption(parser):
    parser.addoption('--websocket_url')


def pytest_configure(config):
    websocket_url = config.getoption('websocket_url')
    config.pluginmanager.register(TestMonitorPlugin(websocket_url))
