# -*- coding: utf-8 -*-
""" Tests for py.test test runner
"""
from __future__ import absolute_import
from builtins import str

# import os
import pytest
# import shutil
# import json
from mock import Mock
# from .conftest import TESTDATA_DIR
# from purkinje_pytest import testmonitorplugin
from purkinje_pytest import testrunner as sut
# import flotsam.util as pu

obs_mock = Mock()


@pytest.fixture
def testrunner(tmpdir, monkeypatch):

    monkeypatch.setattr(sut, 'Observer', Mock(return_value=obs_mock))
    return sut.TestRunner(str(tmpdir))


def test_creation(testrunner):
    assert sut.Observer.called


def test_get_file_count(testrunner):
    assert testrunner.get_file_count(testrunner._dir) == 0


def test_get_max_user_watches(testrunner):
    lim = testrunner.get_max_user_watches()
    assert type(lim) == int and lim > 0


def test_start(testrunner):
    assert not obs_mock.schedule.called
    testrunner.start(single_run=True)
    assert obs_mock.schedule.called