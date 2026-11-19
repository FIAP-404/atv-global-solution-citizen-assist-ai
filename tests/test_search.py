import json
import unittest
from pathlib import Path

from backend import search
from backend.knowledge import load_services

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "services.demo.json"
CASES = ROOT / "data" / "demo-test-cases.json"
FINAL = ROOT / "data" / "services.demo.json"


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_services(DEMO)

    def ids(self, query, topic="all"):
        return [r["id"] for r in search.search_services(self.records, query, topic)]

    def test_normalization_ignores_case_accents_and_punctuation(self):
        self.assertEqual(search.normalize("  CadÚnico?! "), "cadunico")
        self.assertEqual(self.ids("CPF"), self.ids("cpf"))
        self.assertEqual(self.ids("título eleitoral")[0], "voter")
        self.assertEqual(self.ids("TITULO ELEITORAL")[0], "voter")

    def test_starter_scenarios_find_expected_service(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            if case.get("expectedStatus") != "matched":
                continue
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    self.ids(case["question"])[0], case["expectedServiceId"]
                )

    def test_reformulations_and_aliases(self):
        examples = {
            "CTPS": "work-card",
            "carteira de trabalho": "work-card",
            "cad unico": "social-registry",
            "Cadastro Único": "social-registry",
            "CadÚnico": "social-registry",
            "Quais documentos preciso para tirar o CPF?": "cpf",
            "quero procurar emprego": "jobs",
            "fui demitido": "unemployment",
            "abono PIS": "salary-bonus",
            "fundo de garantia": "fgts",
            "regularizar cpf": "cpf-status",
            "vou viajar para o exterior": "passport",
        }
        for query, expected in examples.items():
            with self.subTest(query=query):
                self.assertEqual(self.ids(query)[0], expected)

    def test_plural_forms_match(self):
        self.assertEqual(self.ids("vagas")[0], "jobs")
        self.assertIn("cpf", self.ids("documentos"))

    def test_topic_filter(self):
        self.assertTrue(all(i in {"cpf", "cpf-status", "identity", "passport", "voter"}
                            for i in self.ids("documento", "documents")))
        self.assertEqual(self.ids("cpf", "work"), [])
        self.assertEqual(self.ids("carteira", "work"), ["work-card"])

    def test_empty_query_lists_topic_or_everything(self):
        self.assertEqual(len(self.ids("")), 15)
        self.assertEqual(len(self.ids("   ", "social")), 5)
        self.assertEqual(self.ids("", "work")[0], "work-card")

    def test_unmatched_and_out_of_scope_queries_return_nothing(self):
        for query in (
            "Qual a previsão do tempo?",
            "cnh",
            "Como tirar carteira de motorista?",
            "receita de bolo",
            "como",
        ):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [])

    def test_summary_only_words_do_not_create_matches(self):
        self.assertEqual(self.ids("orientação"), [])

    def test_ties_keep_file_order_and_are_visible(self):
        ranked = search.score_services(self.records, "documento")
        self.assertEqual([r.record["id"] for r in ranked], ["cpf", "identity", "voter"])
        self.assertEqual(len({r.score for r in ranked}), 1)
        self.assertEqual(len(search.find_ties(ranked)), 3)

    def test_clear_winner_is_not_a_tie(self):
        ranked = search.score_services(self.records, "Bolsa Família")
        self.assertEqual(ranked[0].record["id"], "family-benefit")
        self.assertEqual(len(search.find_ties(ranked)), 1)

    def test_results_are_sorted_by_score(self):
        scores = [r.score for r in search.score_services(self.records, "carteira")]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            search.search_services(self.records, "cpf", "saude")
        with self.assertRaises(ValueError):
            search.search_services(self.records, None)  # type: ignore[arg-type]


class FinalBaseSearchTests(unittest.TestCase):
    """The same starter scenarios must still work on the reviewed base."""

    @classmethod
    def setUpClass(cls):
        cls.records = load_services(FINAL)

    def test_starter_scenarios(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            ranked = search.search_services(self.records, case["question"])
            with self.subTest(case=case["id"]):
                if case["expectedStatus"] == "matched":
                    self.assertEqual(ranked[0]["id"], case["expectedServiceId"])
                elif case["expectedStatus"] == "unsupported":
                    self.assertEqual(ranked, [])

    def test_concrete_questions_reach_the_right_record(self):
        examples = {
            "Quem tem direito ao seguro-desemprego?": "unemployment",
            "Quando recebo o abono salarial do PIS?": "salary-bonus",
            "Como sacar o FGTS pelo aplicativo?": "fgts",
            "Como me cadastrar no Sine para achar vagas?": "jobs",
            "Como obter a carteira de trabalho digital?": "work-card",
            "fui demitido sem justa causa": "unemployment",
        }
        for query, expected in examples.items():
            with self.subTest(query=query):
                self.assertEqual(search.search_services(self.records, query)[0]["id"], expected)

    def test_out_of_scope_still_returns_nothing(self):
        for query in ("Qual a previsão do tempo?", "como tirar carteira de motorista", "receita de bolo"):
            with self.subTest(query=query):
                self.assertEqual(search.search_services(self.records, query), [])

    def test_every_service_offers_three_continuations(self):
        for rec in self.records:
            self.assertGreaterEqual(len(search.related_services(self.records, rec["id"])), 3)


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_services(DEMO)

    def test_topic_tree_has_two_levels(self):
        tree = search.build_topic_tree(self.records)
        self.assertEqual(set(tree), {"documents", "work", "social"})
        self.assertEqual(len(tree["work"]["services"]), 5)
        self.assertEqual(tree["work"]["label"], "Trabalho")

    def test_graph_is_symmetric(self):
        graph = search.build_graph(self.records)
        for node, neighbours in graph.items():
            for other in neighbours:
                self.assertIn(node, graph[other])

    def test_related_services_offer_at_least_three_options(self):
        related = search.related_services(self.records, "work-card")
        self.assertGreaterEqual(len(related), 3)
        self.assertEqual([r["id"] for r in related[:3]], ["unemployment", "jobs", "salary-bonus"])
        self.assertNotIn("work-card", [r["id"] for r in related])

    def test_related_services_depth_and_limit(self):
        near = search.related_services(self.records, "work-card", depth=1)
        far = search.related_services(self.records, "work-card", depth=2)
        self.assertGreater(len(far), len(near))
        self.assertEqual(len(search.related_services(self.records, "cpf", limit=2)), 2)

    def test_navigation_path(self):
        self.assertEqual(search.navigation_path(self.records, "cpf", "cpf"), ["cpf"])
        path = search.navigation_path(self.records, "cpf", "fgts")
        self.assertEqual(path[0], "cpf")
        self.assertEqual(path[-1], "fgts")
        self.assertLessEqual(len(path), 4)

    def test_unknown_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            search.related_services(self.records, "nao-existe")
        with self.assertRaises(ValueError):
            search.navigation_path(self.records, "cpf", "nao-existe")


if __name__ == "__main__":
    unittest.main()
