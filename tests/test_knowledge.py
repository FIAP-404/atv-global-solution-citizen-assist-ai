import copy
import json
import tempfile
import unittest
from pathlib import Path

from backend import knowledge
from backend.knowledge import KnowledgeBaseError, load_services

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "services.demo.json"
FINAL = ROOT / "data" / "services.demo.json"


def record(record_id: str, related: list[str], topic: str = "documents") -> dict:
    return {
        "id": record_id,
        "topic": topic,
        "title": f"Orientação {record_id}",
        "summary": "Resumo.",
        "keywords": ["teste"],
        "agency": "Órgão",
        "channel": "digital",
        "source": {
            "title": "Fonte",
            "url": "https://www.gov.br/exemplo",
            "reviewedAt": "2026-11-19",
        },
        "audience": "Público.",
        "steps": ["Passo 1."],
        "preparation": [],
        "limitations": "Limite.",
        "relatedIds": related,
    }


def valid_base() -> list[dict]:
    return [
        record("a", ["b", "c", "d"]),
        record("b", ["a", "c", "d"]),
        record("c", ["a", "b", "d"]),
        record("d", ["a", "b", "c"]),
    ]


class LoadServicesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, content, name="base.json") -> Path:
        path = Path(self.tmp.name) / name
        path.write_text(
            content if isinstance(content, str) else json.dumps(content),
            encoding="utf-8",
        )
        return path

    def problems_for(self, records, **kwargs) -> str:
        with self.assertRaises(KnowledgeBaseError) as ctx:
            load_services(self.write(records), **kwargs)
        return "\n".join(ctx.exception.problems)

    def test_valid_file_is_loaded_as_list_of_dicts(self):
        records = load_services(self.write(valid_base()))
        self.assertEqual(len(records), 4)
        self.assertEqual(records[0]["id"], "a")

    def test_demo_base_loads(self):
        self.assertEqual(len(load_services(DEMO)), 15)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_services(Path(self.tmp.name) / "nao-existe.json")

    def test_empty_file(self):
        with self.assertRaisesRegex(KnowledgeBaseError, "vazio"):
            load_services(self.write("   \n"))

    def test_empty_list(self):
        self.assertIn("vazia", self.problems_for([]))

    def test_malformed_json(self):
        with self.assertRaisesRegex(KnowledgeBaseError, "JSON inválido"):
            load_services(self.write("[{"))

    def test_root_must_be_a_list(self):
        self.assertIn("lista", self.problems_for({"id": "a"}))

    def test_missing_field_is_reported(self):
        data = valid_base()
        del data[0]["source"]
        self.assertIn("campo obrigatório ausente: source", self.problems_for(data))

    def test_blank_text_and_empty_steps(self):
        data = valid_base()
        data[0]["summary"] = "  "
        data[1]["steps"] = []
        message = self.problems_for(data)
        self.assertIn("summary", message)
        self.assertIn("steps", message)

    def test_unknown_field_catches_typos(self):
        data = valid_base()
        data[0]["keyword"] = ["x"]
        self.assertIn("campos desconhecidos", self.problems_for(data))

    def test_duplicate_ids(self):
        data = valid_base()
        data[1]["id"] = "a"
        self.assertIn("id duplicado", self.problems_for(data))

    def test_invalid_topic_and_channel(self):
        data = valid_base()
        data[0]["topic"] = "saude"
        data[1]["channel"] = "fax"
        message = self.problems_for(data)
        self.assertIn("topic", message)
        self.assertIn("channel", message)

    def test_source_url_must_be_https_without_credentials(self):
        for bad in ("http://gov.br/x", "https://user:pw@gov.br/x", "gov.br", ""):
            data = valid_base()
            data[0]["source"]["url"] = bad
            self.assertIn("source.url", self.problems_for(data), bad)

    def test_invalid_and_future_review_dates(self):
        for bad in ("19/11/2026", "2026-13-01", "2999-01-01"):
            data = valid_base()
            data[0]["source"]["reviewedAt"] = bad
            self.assertIn("reviewedAt", self.problems_for(data), bad)

    def test_null_review_date_allowed_unless_verification_required(self):
        data = valid_base()
        data[0]["source"]["reviewedAt"] = None
        path = self.write(data)
        self.assertEqual(len(load_services(path)), 4)
        with self.assertRaises(KnowledgeBaseError):
            load_services(path, require_verified=True)

    def test_broken_relationships(self):
        data = valid_base()
        data[0]["relatedIds"] = ["a", "zzz", "b"]
        message = self.problems_for(data)
        self.assertIn("não pode apontar para si mesma", message)
        self.assertIn("'zzz' não existe", message)

    def test_at_least_three_relations(self):
        data = valid_base()
        data[0]["relatedIds"] = ["b", "c"]
        self.assertIn("relatedIds", self.problems_for(data))

    def test_all_problems_are_listed_together(self):
        data = valid_base()
        data[0]["topic"] = "x"
        data[1]["channel"] = "y"
        self.assertGreaterEqual(len(self.problems_for(data).splitlines()), 2)


class HelpersTests(unittest.TestCase):
    def setUp(self):
        self.records = load_services(DEMO)

    def test_index_by_id(self):
        index = knowledge.index_by_id(self.records)
        self.assertEqual(len(index), len(self.records))
        self.assertEqual(index["fgts"]["id"], "fgts")
        self.assertIs(index["fgts"], next(r for r in self.records if r["id"] == "fgts"))

    def test_list_topics_counts(self):
        topics = {t["id"]: t["count"] for t in knowledge.list_topics(self.records)}
        self.assertEqual(topics, {"documents": 5, "work": 5, "social": 5})

    def test_group_by_topic_keeps_file_order(self):
        work = knowledge.group_by_topic(self.records)["work"]
        self.assertEqual(work[0]["id"], "work-card")

    def test_unverified_ids(self):
        records = copy.deepcopy(self.records)
        for item in records:
            item["source"]["reviewedAt"] = "2026-11-19"
        self.assertEqual(knowledge.unverified_ids(records), [])
        records[1]["source"]["reviewedAt"] = None
        records[3]["source"]["reviewedAt"] = None
        self.assertEqual(
            knowledge.unverified_ids(records), [records[1]["id"], records[3]["id"]]
        )

    def test_coverage_minimums(self):
        self.assertEqual(knowledge.check_coverage(self.records), [])
        self.assertTrue(knowledge.check_coverage(self.records[:6]))


class FinalBaseTests(unittest.TestCase):
    def test_final_base_loads_and_meets_assignment_minimums(self):
        records = load_services(FINAL)
        self.assertEqual(knowledge.check_coverage(records), [])
        topics = {t["id"] for t in knowledge.list_topics(records)}
        self.assertEqual(topics, {"documents", "work", "social"})

    def test_reviewed_records_have_real_dates_and_specific_sources(self):
        for rec in load_services(FINAL):
            reviewed = rec["source"]["reviewedAt"]
            if reviewed is not None:
                self.assertRegex(reviewed, r"^\d{4}-\d{2}-\d{2}$")
                self.assertNotEqual(rec["source"]["url"].rstrip("/"), "https://www.gov.br")

    def test_work_theme_is_fully_reviewed(self):
        records = load_services(FINAL)
        pending = set(knowledge.unverified_ids(records))
        work_ids = {r["id"] for r in records if r["topic"] == "work"}
        self.assertFalse(work_ids & pending)


if __name__ == "__main__":
    unittest.main()
