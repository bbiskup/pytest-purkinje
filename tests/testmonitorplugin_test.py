# -*- coding: utf-8 -*-

from __future__ import absolute_import
from builtins import str
import shutil
import os
import pytest
import flotsam.util as fu
import json
from .conftest import TESTDATA_DIR
import purkinje_pytest.testmonitorplugin as sut
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


def test_pytest_collectreport(plugin):
    plugin.send_event = Mock()
    report = []
    plugin.pytest_collectreport(report)
    assert len(plugin.send_event.call_args_list) == 1
    assert type(plugin.send_event.call_args[0][0]) \
        == msg.TestCaseStartEvent
    assert len(plugin.reports) == 1
    assert plugin.reports[0] == report


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
        test_result = pytest.main([test_proj_path],
                                  plugins=[plugin])
        assert plugin.is_websocket_connected()

        send_args = plugin._websocket.send.call_args_list
        assert len(send_args) == 2

        [json.dumps(x[0]) for x in send_args]

        assert test_result == 0

        reps = plugin.reports
        assert len(reps) == 2
        rep0 = reps[0]
        assert rep0.fspath == '.'
        assert rep0.outcome == 'passed'

        rep1 = reps[1]
        assert rep1.fspath == 'simple_test.py'
        assert rep1.outcome == 'passed'

    finally:
        os.chdir(orig_path)
