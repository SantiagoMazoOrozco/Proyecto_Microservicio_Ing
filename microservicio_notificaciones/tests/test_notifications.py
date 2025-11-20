import os
import json
import tempfile

import pytest
import importlib


@pytest.fixture
def client(tmp_path, monkeypatch):
    # ensure notifications directory exists in a temp dir
    tmpdir = tmp_path / "notifications"
    tmpdir.mkdir()
    # set env before importing modules so module-level STORAGE_DIR reads it
    monkeypatch.setenv('NOTIFICATIONS_STORAGE_DIR', str(tmpdir))

    # import app and tasks after env is set
    ns = importlib.import_module('microservicio_notificaciones')
    app = ns.app
    tasks = importlib.import_module('microservicio_notificaciones.tasks')

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client, tasks


def test_create_notification_sync(monkeypatch, client):
    client, tasks = client
    # Force sync mode by ensuring there's no Celery broker
    monkeypatch.delenv('CELERY_BROKER_URL', raising=False)

    def dummy_send(nid, payload):
        # simulate success by writing meta
        tasks.write_meta(nid, {"id": nid, "status": "sent", "to": payload.get('to')})

    # Patch send_email to avoid real SMTP
    monkeypatch.setattr(tasks, 'send_email', dummy_send)

    payload = {"type": "email", "to": "test@example.com", "subject": "Hi", "body": "Hello", "async": False}
    rv = client.post('/notifications', json=payload)
    assert rv.status_code in (200, 202)
    data = rv.get_json()
    nid = data.get('id')
    assert nid

    # check status endpoint
    status = client.get(f'/notifications/{nid}/status')
    assert status.status_code == 200
    meta_resp = status.get_json()
    meta = meta_resp.get('meta') or {}
    assert meta.get('status') in ('sent', 'queued')
