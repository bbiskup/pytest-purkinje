# -*- coding: utf-8 -*-

"""Test for test runner handler"""

import pytest
from mock import Mock
import pytest_purkinje.handler as sut


@pytest.fixture
def py_event():
    """An event concerning a Python file"""
    return Mock(dest_path='/a/b/c/myfile.py')


@pytest.fixture
def non_py_event():
    """An event not concerning a Python file
       (to be ignored)
    """
    return Mock(src_path='/a/b/c/myfile.txt')


@pytest.fixture
def unpatched_handler():
    return sut.Handler()  # need unpatched run_tests


@pytest.fixture
def handler(monkeypatch):
    result = sut.Handler()
    monkeypatch.setattr(result,
                        '_trigger',
                        Mock(side_effect=result._trigger))
    monkeypatch.setattr(result,
                        'run_tests',
                        Mock())
    return result


def test_created_relevant_event(handler, py_event):
    handler.on_created(py_event)
    assert handler._trigger.called
    assert handler.run_tests.called


def test_multi_trigger_avoidance(handler, py_event):
    handler._trigger(py_event)
    handler._trigger(py_event)  # second call should get ignored
    assert len(handler.run_tests.call_args_list) == 1


def test_multi_trigger_avoidance_reset(handler, py_event):
    handler._trigger(py_event)
    handler.clear_cache()  # forget about first call
    handler._trigger(py_event)  # second call get through
    assert len(handler.run_tests.call_args_list) == 2


def test_created_irrelevant_event(handler,
                                  non_py_event):
    handler.on_created(non_py_event)
    assert handler._trigger.called
    assert not handler.run_tests.called


def test_deleted(handler, py_event):
    handler.on_deleted(py_event)
    assert handler._trigger.called


def test_modified(handler, py_event):
    handler.on_modified(py_event)
    assert handler._trigger.called


def test_moved(handler, py_event):
    handler.on_moved(py_event)
    assert handler._trigger.called


def test_run_tests(unpatched_handler, monkeypatch):
    assert not unpatched_handler._tests_running

    def check_state(_):
        assert unpatched_handler._tests_running

    monkeypatch.setattr(sut.os, 'system', Mock(side_effect=check_state))
    unpatched_handler.run_tests()
    assert sut.os.system.called
    assert not unpatched_handler._tests_running


def test_run_tests_with_error(unpatched_handler, monkeypatch):
    assert not unpatched_handler._tests_running

    def do_raise(_):
        raise Exception('Dummy exception')

    sys_mock = Mock(side_effect=do_raise)
    monkeypatch.setattr(sut.os, 'system', sys_mock)
    with pytest.raises(Exception):
        unpatched_handler.run_tests()
    assert not unpatched_handler._tests_running
