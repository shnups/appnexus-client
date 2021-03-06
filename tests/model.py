# -*- coding:utf-8-*-

import pytest

from appnexus.client import AppNexusClient
from appnexus.cursor import Cursor
from appnexus.model import Campaign, Model, Report

Model.client = AppNexusClient("Test.", "dumb")


@pytest.fixture
def response():
    return {
        "profile": [{
            "id": 21975591,
            "another_field": "another_value"
        }],
        "count": 8
    }


@pytest.fixture
def response2():
    return {
        "member": {
            "id": 395858219,
            "field": "value"
        },
        "count": 1
    }


def test_report_create_returns_instance_report(mocker):
    mocker.patch.object(Report.client, 'create')
    report = Report().save()
    assert isinstance(report, Report)


def test_report_download(mocker):
    mocker.patch.object(Report.client, 'create')
    Report.client.create.return_value = {
        'report_id': 12345
    }
    report = Report().save()

    mocker.patch.object(Report, 'is_ready')
    Report.is_ready.return_value = 'ready'

    mocker.patch.object(Report.client, 'get')
    Report.client.get.return_value = b''
    data = report.download()

    assert Report.client.get.called
    assert data == b''


def test_model_init_by_dict():
    x = Campaign({"id": 42})
    assert x.id == 42


def test_model_init_by_kwargs():
    x = Campaign(id=42)
    assert x.id == 42


def test_model_can_have_class_and_instance_client():
    Model.client = AppNexusClient('dumb', 'test')
    x = Campaign()
    x.client = AppNexusClient('dumbo', 'elephant')
    assert Campaign.client is not x.client


def test_model_find_returns_cursor(mocker, response):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response
    assert isinstance(Campaign.find(), Cursor)


def test_model_find_one_returns_model_instance(mocker, response2):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response2
    assert isinstance(Campaign.find_one(), Campaign)


def test_model_find_one_uses_representation(mocker, response2):
    from appnexus.representations import raw

    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response2
    Campaign.client.representation = raw
    assert isinstance(Campaign.find_one(), dict)


def test_model_count(mocker, response):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response
    assert Campaign.count(id=21975591) == response["count"]


def test_model_save_missing_id(mocker):
    mocker.patch.object(Campaign.client, 'create')
    Campaign().save()
    assert Campaign.client.create.called


def test_model_save_with_id(mocker):
    mocker.patch.object(Campaign.client, 'modify')
    x = Campaign(id=42)
    x.attr = True
    x.save()
    assert Campaign.client.modify.called


def test_meta_call_client_meta(mocker):
    mocker.patch.object(Campaign.client, 'meta')
    Campaign.meta()
    assert Campaign.client.meta.called


def test_guess_service_name():
    class Test(Model):
        pass
    assert Test.service_name == "test"


def test_guess_composed_service_name():
    class TestService(Model):
        pass
    assert TestService.service_name == "test-service"


def test_setitem():
    x = Campaign(field=1)
    x.field = 42
    assert x.field == 42
    x.new_field = 23
    assert x.new_field == 23


def test_string_representation():
    x = Campaign(id=21)
    assert "21" in str(x)
    assert x.service_name in str(x).lower()


def test_service_can_override():
    class Test(Model):
        service_name = "notatest"
    assert Test.service_name == "notatest"


def test_connect():
    x = Campaign()
    credentials = {"username": "dumb-user", "password": "dumb-password"}
    x.connect(**credentials)
    assert x.client


def test_create(mocker):
    mocker.patch.object(Campaign.client, "create")
    Campaign.create({"field": 42})
    assert Campaign.client.create.called


def test_modify(mocker):
    mocker.patch.object(Campaign.client, "modify")
    Campaign.modify({"field": 42})
    assert Campaign.client.modify.called


def test_changelog():
    x = Campaign(id=42)
    changelogs_cursor = x.changelog
    assert isinstance(changelogs_cursor, Cursor)
    assert changelogs_cursor.specs.get("resource_id") == x.id
    assert changelogs_cursor.specs.get("service") == x.service_name
