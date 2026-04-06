import time

from backend.app.core.session_store import SessionStore, Session


def test_create_session():
    store = SessionStore()
    session = store.create_session()
    assert session.session_id
    assert session.extracted_features == {}
    assert session.conversation_phase == "collecting"
    assert session.confirmed is False
    assert session.prediction is None


def test_get_session_valid():
    store = SessionStore()
    session = store.create_session()
    retrieved = store.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id


def test_get_session_unknown():
    store = SessionStore()
    assert store.get_session("nonexistent-id") is None


def test_update_session():
    store = SessionStore()
    session = store.create_session()
    session.extracted_features = {"sex": "Male", "age": 55.0}
    session.conversation_phase = "awaiting_confirmation"
    store.update_session(session)

    retrieved = store.get_session(session.session_id)
    assert retrieved.extracted_features == {"sex": "Male", "age": 55.0}
    assert retrieved.conversation_phase == "awaiting_confirmation"


def test_session_expires_after_ttl():
    store = SessionStore(ttl_seconds=0.05)
    session = store.create_session()
    sid = session.session_id
    time.sleep(0.1)
    assert store.get_session(sid) is None


def test_cleanup_removes_expired():
    store = SessionStore(ttl_seconds=0.05)
    store.create_session()
    store.create_session()
    time.sleep(0.1)
    active = store.create_session()
    removed = store.cleanup()
    assert removed == 2
    assert store.session_count == 1
    assert store.get_session(active.session_id) is not None


def test_message_history():
    store = SessionStore()
    session = store.create_session()
    session.message_history.append({"role": "user", "content": "Hello"})
    session.message_history.append({"role": "assistant", "content": "Hi"})
    store.update_session(session)

    retrieved = store.get_session(session.session_id)
    assert len(retrieved.message_history) == 2
    assert retrieved.message_history[0]["role"] == "user"


def test_multiple_sessions_independent():
    store = SessionStore()
    s1 = store.create_session()
    s2 = store.create_session()
    s1.extracted_features = {"sex": "Male"}
    s2.extracted_features = {"sex": "Female"}
    store.update_session(s1)
    store.update_session(s2)

    r1 = store.get_session(s1.session_id)
    r2 = store.get_session(s2.session_id)
    assert r1.extracted_features["sex"] == "Male"
    assert r2.extracted_features["sex"] == "Female"
