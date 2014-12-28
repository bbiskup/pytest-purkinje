# -*- coding: utf-8 -*-
""" Tests for py.test test runner
"""
from __future__ import absolute_import
from builtins import str

import pytest
import os.path as op
from mock import Mock
from purkinje_pytest import testrunner as sut


@pytest.fixture
def obs_mock():
    return Mock()


@pytest.fixture
def testrunner(tmpdir, monkeypatch, obs_mock):

    monkeypatch.setattr(sut, 'Observer', Mock(return_value=obs_mock))
    return sut.TestRunner(str(tmpdir))


def test_creation(testrunner):
    assert sut.Observer.called


def test_get_file_count(testrunner):
    # The directory itself counts as 1
    assert testrunner.get_file_count(testrunner._dir) == 1
    f = open(op.join(testrunner._dir, 'a_file'), 'w')
    f.close()

    # The newly created file counts as one, too
    assert testrunner.get_file_count(testrunner._dir) == 2


def test_get_max_user_watches(testrunner):
    lim = testrunner.get_max_user_watches()
    assert type(lim) == int and lim > 0


def test_start(testrunner):
    assert not testrunner.observer.schedule.called
    testrunner.start(single_run=True)
    assert testrunner.observer.schedule.called


def test_start_keyboard_interrupted(testrunner, monkeypatch):
    assert not testrunner.observer.schedule.called

    def keyboard_interrupt(_):
        raise KeyboardInterrupt('Dummy keyboard interrupt')

    monkeypatch.setattr(
        sut.time, 'sleep', Mock(side_effect=keyboard_interrupt))
    testrunner.start(single_run=False)
    assert testrunner.observer.schedule.called
    assert testrunner.observer.stop.called


def test_main(monkeypatch):
    runner = Mock()
    monkeypatch.setattr(sut, 'TestRunner', Mock(return_value=runner))
    sut.main()
    assert sut.TestRunner.called
    assert runner.start.called
