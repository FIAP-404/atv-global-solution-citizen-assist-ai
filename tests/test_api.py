import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api import app
from backend.config import DATA_PATH
from backend.errors import ModuleNotReadyError


class ApiHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Path(__file__).resolve().parents[1] / "data" / "services.demo.json"
        cls.records = json.loads(fixture.read_text(encoding="utf-8"))

    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)
        self.addCleanup(self.client.close)

    def test_health_reports_transport_without_external_ai(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"status": "ok", "scope": "transport", "externalAi": False}
        )

    def test_pending_knowledge_module_is_explicitly_unavailable(self):
        with patch(
            "backend.knowledge.load_services",
            side_effect=ModuleNotReadyError("knowledge"),
        ):
            response = self.client.get("/api/v1/services")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "module_pending")

    def test_catalog_dispatches_to_loader_and_preserves_frontend_fields(self):
        with patch(
            "backend.knowledge.load_services", return_value=self.records
        ) as load:
            response = self.client.get("/api/v1/services")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], self.records)
        load.assert_called_once_with(DATA_PATH)

    def test_search_passes_query_topic_and_records_to_search_owner(self):
        with patch("backend.knowledge.load_services", return_value=self.records):
            with patch(
                "backend.search.search_services", return_value=self.records[:1]
            ) as search:
                response = self.client.get(
                    "/api/v1/services", params={"query": "cpf", "topic": "documents"}
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["query"], "cpf")
        self.assertEqual(response.json()["items"], self.records[:1])
        search.assert_called_once_with(self.records, "cpf", "documents")

    def test_assistant_passes_question_and_mode_to_response_owner(self):
        answer = {
            "status": "matched",
            "message": "Source-bound response",
            "services": self.records[:1],
            "mode": "steps",
        }
        with patch("backend.knowledge.load_services", return_value=self.records):
            with patch(
                "backend.assistant.answer_question", return_value=answer
            ) as respond:
                response = self.client.post(
                    "/api/v1/assistant/query", json={"question": "CPF", "mode": "steps"}
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), answer)
        respond.assert_called_once_with(self.records, "CPF", "steps")

    def test_request_validation_happens_before_pending_module_calls(self):
        invalid_bodies = [
            {"question": "CPF", "mode": "invented"},
            {"question": "a" * 501, "mode": "direct"},
            {"question": ["CPF"], "mode": "direct"},
            {"question": "CPF", "mode": "direct", "token": "unwanted-field"},
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                self.assertEqual(
                    self.client.post("/api/v1/assistant/query", json=body).status_code,
                    422,
                )
        self.assertEqual(
            self.client.get("/api/v1/services?topic=invalid").status_code, 422
        )

    def test_cors_allows_the_frontend_origin_and_json_post(self):
        response = self.client.options(
            "/api/v1/assistant/query",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"], "http://127.0.0.1:5173"
        )

    def test_malformed_module_response_does_not_become_a_success(self):
        with patch("backend.knowledge.load_services", return_value=self.records):
            with patch(
                "backend.assistant.answer_question",
                return_value={
                    "status": "matched",
                    "message": "Invalid",
                    "services": [],
                    "mode": "direct",
                },
            ):
                response = self.client.post(
                    "/api/v1/assistant/query",
                    json={"question": "CPF", "mode": "direct"},
                )
        self.assertEqual(response.status_code, 500)

    def test_source_metadata_matches_the_frontend_contract(self):
        invalid_sources = [
            {"url": "http://example.com/service"},
            {"url": "https://user:password@example.com/service"},
            {"reviewedAt": "not-a-date"},
            {"reviewedAt": "2026-02-31"},
            {"reviewedAt": "20261119"},
        ]
        for update in invalid_sources:
            with self.subTest(update=update):
                record = {
                    **self.records[0],
                    "source": {**self.records[0]["source"], **update},
                }
                with patch("backend.knowledge.load_services", return_value=[record]):
                    self.assertEqual(
                        self.client.get("/api/v1/services").status_code, 500
                    )
        record = {
            **self.records[0],
            "source": {**self.records[0]["source"], "reviewedAt": "2026-11-19"},
        }
        with patch("backend.knowledge.load_services", return_value=[record]):
            response = self.client.get("/api/v1/services")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["items"][0]["source"]["reviewedAt"], "2026-11-19"
        )


if __name__ == "__main__":
    unittest.main()
