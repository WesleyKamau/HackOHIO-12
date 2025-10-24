import importlib
import json
import os
from types import SimpleNamespace

import app


def setup_function():
    # Ensure a clean state before each test
    importlib.reload(app)
    app._fallback_chats = []
    app.chats_collection = None
    app.buildings_data = []
    app.init_app()


def test_loads_buildings_json():
    # The repo root buildings.json should be loaded
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    root_file = os.path.join(repo_root, 'buildings.json')
    assert os.path.exists(root_file)
    with open(root_file, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    assert isinstance(app.buildings_data, list)
    assert expected == app.buildings_data


def test_extract_group_id_and_token_from_link_valid():
    link = 'https://groupme.com/join_group/12345678/SHARE_TOKEN'
    res = app.extract_group_id_and_token_from_link(link)
    assert res == ('12345678', 'SHARE_TOKEN')


def test_extract_group_id_and_token_from_link_invalid_or_id_only():
    # Plain id should return None
    assert app.extract_group_id_and_token_from_link('12345678') is None
    # Malformed link
    assert app.extract_group_id_and_token_from_link('https://groupme.com/join/123/abc') is None


def test_send_message_to_group_success(monkeypatch):
    # Simulate requests.post returning status_code 201
    class FakeResp:
        def __init__(self):
            self.status_code = 201

        def json(self):
            return {}

    def fake_post(url, params=None, json=None, timeout=None):
        # Check url contains a group id
        assert '/groups/' in url
        assert json and 'message' in json
        return FakeResp()

    monkeypatch.setattr(app, 'requests', SimpleNamespace(post=fake_post))

    out = app.send_message_to_group('group1', 'hello world', image_url=None)
    assert out['success'] is True


def test_send_message_to_group_failure(monkeypatch):
    class FakeResp:
        def __init__(self):
            self.status_code = 400
            self.text = 'bad request'

        def json(self):
            return {}

    def fake_post(url, params=None, json=None, timeout=None):
        return FakeResp()

    monkeypatch.setattr(app, 'requests', SimpleNamespace(post=fake_post))

    out = app.send_message_to_group('group1', 'hello world')
    assert out['success'] is False
    assert out['status_code'] == 400


def test_upload_image_to_groupme(monkeypatch):
    # When GROUPME_ACCESS_TOKEN missing -> None
    app.app.config['GROUPME_ACCESS_TOKEN'] = None
    # Create a dummy file-like object
    class DummyFile:
        content_type = 'image/png'

        def read(self):
            return b'PNGDATA'

    res = app.upload_image_to_groupme(DummyFile())
    assert res is None

    # Now simulate success
    app.app.config['GROUPME_ACCESS_TOKEN'] = 'token123'

    class FakeResp:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {'payload': {'picture_url': 'https://image.example/pic.png'}}

    def fake_post(url, headers=None, data=None, timeout=None):
        assert headers['X-Access-Token'] == 'token123'
        return FakeResp()

    monkeypatch.setattr(app, 'requests', SimpleNamespace(post=fake_post))
    out = app.upload_image_to_groupme(DummyFile())
    assert out == 'https://image.example/pic.png'


def test_join_group(monkeypatch):
    # No token configured
    app.app.config['GROUPME_ACCESS_TOKEN'] = None
    assert app.join_group('gid', 'token') is False

    # With token, simulate requests.post
    app.app.config['GROUPME_ACCESS_TOKEN'] = 'tok'

    class FakeResp:
        def __init__(self, code=200):
            self.status_code = code
            self.text = 'ok'

    def fake_post(url, params=None, timeout=None):
        assert 'groups' in url
        return FakeResp(201)

    monkeypatch.setattr(app, 'requests', SimpleNamespace(post=fake_post))
    assert app.join_group('gid', 'share') is True


def test_add_and_query_fallback_storage():
    # Ensure fallback is used
    app.chats_collection = None
    app._fallback_chats = []
    app.app.config['APP_ENV'] = 'dev'
    chat = app.add_chat('g1', 5, 2)
    assert chat in app._fallback_chats
    # Query by buildings
    ids = app.get_groupme_ids_by_buildings([5])
    assert 'g1' in ids
    mapping = app.get_groupme_map_by_buildings([5])
    assert 5 in mapping and mapping[5][0]['group_id'] == 'g1'
