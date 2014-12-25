# -*- coding: utf-8 -*-

import pytest
import purkinje_pytest.testmonitorplugin as sut
from mock import Mock

TEST_WEBSOCKET_URL = 'ws://example.org/'


@pytest.fixture
def mock_ws(monkeypatch):
    ws = Mock()
    m = Mock(return_value=ws)
    monkeypatch.setattr(sut.websocket, 'WebSocket', m)
    return ws


@pytest.fixture
def plugin(mock_ws):
    return sut.TestMonitorPlugin(TEST_WEBSOCKET_URL)


def test_1(plugin, mock_ws):
    assert mock_ws.called_once_with('xyz')
