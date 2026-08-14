from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api import ask as ask_api
from app.api import health as health_api
from app.rag import vector_store


def test_health_qdrant_uses_client_factory(monkeypatch):
    client = Mock()
    monkeypatch.setattr(vector_store, "get_qdrant_client", Mock(return_value=client))

    response = health_api.health_qdrant()

    assert response == {"status": "healthy", "service": "qdrant"}
    vector_store.get_qdrant_client.assert_called_once_with()
    client.get_collections.assert_called_once_with()


def test_ask_preserves_http_exception_status_code():
    request = ask_api.AskRequest()
    user = SimpleNamespace(id="user-id", clerk_user_id="clerk-id")

    with pytest.raises(HTTPException) as exc_info:
        ask_api.ask(request, current_user=user, db=Mock())

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Missing query/question"


def test_search_chunks_propagates_qdrant_failure(monkeypatch):
    qdrant_error = RuntimeError("Qdrant unavailable")
    client = Mock()
    client.query_points.side_effect = qdrant_error
    monkeypatch.setattr(vector_store, "get_qdrant_client", Mock(return_value=client))
    monkeypatch.setattr(vector_store, "create_collection", Mock())
    monkeypatch.setattr(vector_store, "debug_qdrant_counts", Mock())
    monkeypatch.setattr(vector_store, "debug_sample_payloads", Mock())
    monkeypatch.setattr(vector_store, "embed_texts", Mock(return_value=[[0.1, 0.2]]))

    with pytest.raises(RuntimeError, match="Qdrant unavailable") as exc_info:
        vector_store.search_chunks("test query")

    assert exc_info.value is qdrant_error
    client.query_points.assert_called_once()
