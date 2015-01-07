# -*- coding: utf-8 -*-


"""Test cases for py.test plugin

   TODO: pytest_purkinje plugin is active during test execution;
         -p no:pytest_purkinje does not disable it. This causes
         error messages because there is no purkinje server available
"""

from __future__ import absolute_import
from builtins import str
import shutil
import os
import pytest
import flotsam.file_util as fu
import json
import time
from .conftest import TESTDATA_DIR
import pytest_purkinje.testmonitorplugin as sut
import purkinje_messages.message as msg
from mock import Mock

TEST_WEBSOCKET_URL = 'ws://example.org/'


@pytest.fixture
def mock_ws(monkeypatch):
    ws = Mock()
    m = Mock(return_value=ws)
    monkeypatch.setattr(sut.websocket, 'create_connection', m)
    return ws


@pytest.fixture
def plugin(mock_ws):
    return sut.TestMonitorPlugin(TEST_WEBSOCKET_URL)


@pytest.fixture
def report():
    return Mock(fs_path='dummy_path',
                nodeid='dummy_path::test_1',
                outcome='passed',
                when='call')


def test_1(plugin):
    assert plugin._websocket.create_connection.called_once_with('xyz')
    assert plugin.is_websocket_connected()


def test_send_event(plugin):
    mock_event = Mock()
    plugin.send_event(mock_event)
    assert mock_event.serialize.called
    assert plugin._websocket.send.called


def test_send_event_does_not_raise(plugin):
    # ensure that test execution will continue
    mock_event = Mock()

    def do_raise():
        raise Exception('Dummy exception')

    mock_event.serialize.side_effect = do_raise
    plugin.send_event(mock_event)
    assert not plugin._websocket.send.called


def test_suite_name(plugin, monkeypatch):
    monkeypatch.setattr(sut.os,
                        'getcwd',
                        Mock(return_value='/abc/xyz'))
    monkeypatch.setattr(sut.socket,
                        'gethostname',
                        Mock(return_value='testhost'))
    expected = 'testhost: /abc/xyz'
    assert plugin.suite_name() == expected


def test_suite_hash(plugin, monkeypatch):
    monkeypatch.setattr(plugin, 'suite_name',
                        Mock(return_value='testsuite_1'))
    assert plugin.suite_hash() == 'd50c6441c9f5bd95c8e6dbde301b2b11'


def test_pytest_sessionstart(plugin, monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    monkeypatch.setattr(plugin,
                        'suite_name',
                        Mock(return_value='testhost: /abc/xyz'))

    plugin.pytest_sessionstart()
    assert not plugin.send_event.called


def test_pytest_sessionfinish(plugin, monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    plugin.pytest_sessionfinish()
    assert plugin.send_event.called
    assert len(plugin.send_event.call_args_list) == 2

    m1 = plugin.send_event.call_args_list[0][0][0]
    assert type(m1) == msg.SessionTerminatedEvent

    m2 = plugin.send_event.call_args_list[1][0][0]
    assert type(m2) == msg.ConnectionTerminationEvent


def test_works_if_no_connection(plugin):
    plugin._websocket = None
    assert not plugin.is_websocket_connected()
    mock_event = Mock()
    plugin.send_event(mock_event)
    assert not plugin.is_websocket_connected()


def test_pytest_runtest_logreport(plugin, report, monkeypatch):
    start_time = time.time()
    monkeypatch.setattr(plugin, 'send_event', Mock())
    monkeypatch.setattr(sut.time,
                        'time',
                        Mock(return_value=start_time + 5))

    monkeypatch.setattr(plugin, '_test_cases', {report.nodeid: start_time})
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 2

    arg = plugin.send_event.call_args_list[0][0][0]
    assert type(arg) == msg.SessionStartedEvent

    event = plugin.send_event.call_args_list[1][0][0]
    assert type(event) == msg.TestCaseFinishedEvent
    assert event['duration'] == 5000
    assert len(plugin.reports) == 1
    assert plugin.reports[0] == report


def test_pytest_runtest_logreport_starts_session_only_once(
        report,
        plugin,
        monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    monkeypatch.setattr(plugin,
                        '_test_cases',
                        {report.nodeid: time.time()})
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 2


def test_pytest_runtest_logreport_store_tc_start_time(plugin,
                                                      monkeypatch,
                                                      report):
    start_time = time.time()
    monkeypatch.setattr(plugin, 'send_event', Mock())
    monkeypatch.setattr(sut.time,
                        'time',
                        Mock(return_value=start_time))
    report.when = 'setup'
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 0
    assert len(plugin.reports) == 0
    assert report.nodeid in plugin._test_cases
    assert plugin._test_cases[report.nodeid] == start_time


def test_pytest_runtest_logreport_ignore_tc_not_found(plugin,
                                                      monkeypatch,
                                                      report):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    monkeypatch.setattr(plugin, '_test_cases', {})
    report.when = 'call'
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 0
    assert len(plugin.reports) == 0
    assert report.nodeid not in plugin._test_cases


def test_pytest_runtest_logreport_no_detail(plugin, report, monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    report.nodeid = report.fs_path
    report.keywords = {}
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 0
    assert len(plugin.reports) == 0


def test_pytest_runtest_logreport_pep8(plugin, report, monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    report.nodeid = report.fs_path
    report.keywords = {'pep8': 1}
    report.when = 'setup'
    report.outcome = 'skipped'
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 2
    assert len(plugin.reports) == 1


@pytest.mark.parametrize('phase', ['setup', 'teardown'])
def test_pytest_runtest_logreport_ignore_phase(
        phase, plugin, report, monkeypatch):
    monkeypatch.setattr(plugin, 'send_event', Mock())
    report.when = phase
    plugin.pytest_runtest_logreport(report)
    assert len(plugin.send_event.call_args_list) == 0
    assert len(plugin.reports) == 0


def test_empty_single_pass(tmpdir, plugin, monkeypatch):
    test_proj_path = str(tmpdir) + '/singlepass'
    shutil.copytree(TESTDATA_DIR + '/testproj/singlepass',
                    test_proj_path)

    # TODO
    # Deletion of __pycache__ is necessary, or py.test will fail with the
    # following error message:
    #     #
    # import file mismatch:
    # imported module 'simple_test' has this __file__ attribute:
    # /home/bb/devel/python/purkinje/testdata/
    # testproj/singlepass/simple_test.py
    # which is not the same as the test file we want to collect:
    # /tmp/pytest-84/test_empty_single_pass0/singlepass/simple_test.py
    # HINT: remove __pycache__ / .pyc files and/or use a unique basename
    # for your test file modules
    fu.ensure_deleted(test_proj_path + '/__pycache__')

    orig_path = os.getcwd()
    try:
        os.chdir(test_proj_path)
        mock_ws = Mock()
        monkeypatch.setattr(sut.websocket, 'create_connection', mock_ws)
        assert plugin.is_websocket_connected()
        test_result = pytest.main([test_proj_path],
                                  plugins=[plugin])

        send_args = plugin._websocket.send.call_args_list
        assert len(send_args) == 4

        [json.dumps(x[0]) for x in send_args]

        assert test_result == 0

        reps = plugin.reports
        assert len(reps) == 1
        rep0 = reps[0]
        assert rep0.fspath == 'simple_test.py'
        assert rep0.outcome == 'passed'

    finally:
        os.chdir(orig_path)


def test_pytest_addoption():
    parser = Mock()
    sut.pytest_addoption(parser)
    assert parser.addoption.call_args[0][0] == '--websocket_url'


def test_pytest_configure():
    config = Mock()
    sut.pytest_configure(config)
    assert config.pluginmanager.register.called
