from __future__ import annotations

import types
import uuid

import pytest

from src.ServiceDefinitions.BaseService import ServiceExceptionWithCode
from src.ServiceDefinitions.Domain_Social.NotificationRuleService import NotificationRuleService
from src.ServiceDefinitions.Domain_Social.NotificationService import NotificationService
from src.ServiceDefinitions.ServiceContext import SERVICES


class FakeLoader:
    def __init__(self, *, by_id=None, rows=None):
        self.by_id = by_id or {}
        self.rows = rows or []
        self.filter_calls = []
        self.updated = []

    async def load(self, id_):
        return self.by_id.get(id_)

    async def filter_by(self, **kwargs):
        self.filter_calls.append(kwargs)
        return [
            row for row in self.rows
            if all(getattr(row, key) == value for key, value in kwargs.items())
        ]

    async def update(self, *, entity, **kwargs):
        self.updated.append(entity)
        return entity


def _patch(monkeypatch, service, loader):
    async def fake_get_loader(cls, ctx):
        return loader

    monkeypatch.setattr(service, "getLoader", classmethod(fake_get_loader))


def _ctx(user_id=None):
    user = {"id": str(user_id)} if user_id else None
    return types.SimpleNamespace(user=user, Services=SERVICES)


def test_social_services_are_registered():
    assert SERVICES.NotificationService is NotificationService
    assert SERVICES.NotificationRuleService is NotificationRuleService
    assert SERVICES.NotificationTypeService.__name__ == "NotificationTypeService"


@pytest.mark.asyncio
async def test_get_unread_filters_by_current_user_and_read_flag(monkeypatch):
    user_id = uuid.uuid4()
    rows = [
        types.SimpleNamespace(owner_id=user_id, read=False),
        types.SimpleNamespace(owner_id=user_id, read=True),
        types.SimpleNamespace(owner_id=uuid.uuid4(), read=False),
    ]
    loader = FakeLoader(rows=rows)
    _patch(monkeypatch, NotificationService, loader)

    result = await NotificationService.GetUnread(ctx=_ctx(user_id))

    assert result == [rows[0]]
    assert loader.filter_calls == [{"owner_id": user_id, "read": False}]


@pytest.mark.asyncio
async def test_mark_as_read_updates_for_owner(monkeypatch):
    user_id = uuid.uuid4()
    notification_id = uuid.uuid4()
    stored = types.SimpleNamespace(id=notification_id, owner_id=user_id, read=False)
    loader = FakeLoader(by_id={notification_id: stored})
    _patch(monkeypatch, NotificationService, loader)
    entity = types.SimpleNamespace(id=notification_id, read=False)

    result = await NotificationService.MarkAsRead(ctx=_ctx(user_id), entity=entity)

    assert result is entity
    assert entity.read is True
    assert loader.updated == [entity]


@pytest.mark.asyncio
async def test_mark_as_read_rejects_non_owner(monkeypatch):
    notification_id = uuid.uuid4()
    stored = types.SimpleNamespace(id=notification_id, owner_id=uuid.uuid4(), read=False)
    loader = FakeLoader(by_id={notification_id: stored})
    _patch(monkeypatch, NotificationService, loader)

    with pytest.raises(ServiceExceptionWithCode) as exc_info:
        await NotificationService.MarkAsRead(
            ctx=_ctx(uuid.uuid4()),
            entity=types.SimpleNamespace(id=notification_id, read=False),
        )

    assert exc_info.value.code == "notification_not_owner"
    assert loader.updated == []


@pytest.mark.asyncio
async def test_mark_as_read_raises_when_missing(monkeypatch):
    _patch(monkeypatch, NotificationService, FakeLoader())

    with pytest.raises(ServiceExceptionWithCode) as exc_info:
        await NotificationService.MarkAsRead(
            ctx=_ctx(uuid.uuid4()),
            entity=types.SimpleNamespace(id=uuid.uuid4(), read=False),
        )

    assert exc_info.value.code == "notification_not_found"


@pytest.mark.asyncio
async def test_get_matching_rules_supports_wildcards_and_skips_disabled(monkeypatch):
    entity_id = uuid.uuid4()
    entity_type = uuid.uuid4()
    activity_type = uuid.uuid4()

    def rule(**kw):
        data = dict(enabled=True, entity_id=None, entity_type_id=None, activity_type_id=None, owner_id=uuid.uuid4())
        data.update(kw)
        return types.SimpleNamespace(**data)

    exact = rule(entity_id=entity_id, entity_type_id=entity_type, activity_type_id=activity_type)
    by_activity_only = rule(activity_type_id=activity_type)
    other_activity = rule(activity_type_id=uuid.uuid4())
    other_entity = rule(entity_id=uuid.uuid4(), activity_type_id=activity_type)
    disabled = rule(enabled=False, activity_type_id=activity_type)

    loader = FakeLoader(rows=[exact, by_activity_only, other_activity, other_entity, disabled])
    _patch(monkeypatch, NotificationRuleService, loader)

    result = await NotificationRuleService.GetMatchingRules(
        ctx=_ctx(),
        entity_id=entity_id,
        entity_type_id=entity_type,
        activity_type_id=activity_type,
    )

    assert result == [exact, by_activity_only]