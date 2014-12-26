# -*- coding: utf-8 -*-

"""Test for test runner handler"""

import pytest
from mock import Mock
import purkinje_pytest.handler as sut


@pytest.fixture
def py_event():
    """An event concerning a Python file"""
    return Mock(dest_path='/a/b/c/myfile.py')


@pytest.fixture
def non_py_event():
    """An event not concerning a Python file
       (to be ignored)
    """
    return Mock(dest_path='/a/b/c/myfile.txt')


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


def test_run_tests(handler, monkeypatch):
    assert not handler._tests_running
    monkeypatch.setattr(sut.os, 'system', Mock())
    handler.run_tests()
    assert not handler._tests_running


def test_run_tests_with_error(handler, monkeypatch):
    assert not handler._tests_running

    def do_raise():
        raise Exception('Dummy exception')

    sys_mock = Mock(side_effect=do_raise)
    monkeypatch.setattr(sut.os, 'system', sys_mock)
    handler.run_tests()
    assert not handler._tests_running
