import json
import unittest
from pathlib import Path

from backend import assistant
from backend.contracts import AnswerResponse
from backend.knowledge import load_services

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "services.demo.json"
CASES = ROOT / "data" / "demo-test-cases.json"
MODES = ("direct", "steps")


class AssistantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_services(DATA)
        cls.by_id = {r["id"]: r for r in cls.records}

    def ask(self, question, mode="direct"):
        answer = assistant.answer_question(self.records, question, mode)
        # Toda resposta precisa passar no mesmo contrato que a API usa.
        AnswerResponse.model_validate(answer)
        return answer

    def assertCitesSource(self, answer, record):
        self.assertIn(record["source"]["url"], answer["message"])
        self.assertIn(record["source"]["title"], answer["message"])
        self.assertIn("Aviso:", answer["message"])

    # --- os quatro status -------------------------------------------------

    def test_starter_cases_in_both_modes(self):
        for case in json.loads(CASES.read_text(encoding="utf-8")):
            if case.get("knownLimitation"):
                continue  # erros esperados, medidos em tests/test_evaluation.py
            for mode in MODES:
                with self.subTest(case=case["id"], mode=mode):
                    request_mode = case.get("requestMode", mode)
                    if case["expectedStatus"] == "error":
                        with self.assertRaises(ValueError):
                            assistant.answer_question(
                                self.records, case["question"], request_mode
                            )
                        continue
                    answer = self.ask(case["question"], mode)
                    self.assertEqual(answer["status"], case["expectedStatus"])
                    self.assertEqual(answer["mode"], mode)
                    if "expectedServiceId" in case:
                        self.assertEqual(
                            answer["services"][0]["id"], case["expectedServiceId"]
                        )

    def test_empty_questions(self):
        for question in ["", "   ", "\n\t", "?!", "..."]:
            for mode in MODES:
                with self.subTest(question=question, mode=mode):
                    answer = self.ask(question, mode)
                    self.assertEqual(answer["status"], "empty")
                    self.assertEqual(answer["services"], [])
                    self.assertIn("tema", answer["message"])

    def test_unsupported_states_the_limit_and_suggests_topics(self):
        for question in [
            "Qual a previsão do tempo?",
            "Como tirar carteira de motorista?",
            "como",
            "quanto custa?",
        ]:
            for mode in MODES:
                with self.subTest(question=question, mode=mode):
                    answer = self.ask(question, mode)
                    self.assertEqual(answer["status"], "unsupported")
                    self.assertEqual(answer["services"], [])
                    self.assertIn("não vou inventar", answer["message"])
                    for label in ["Documentos", "Trabalho", "Assistência social"]:
                        self.assertIn(label, answer["message"])

    def test_ambiguous_uses_ties_and_asks_for_a_choice(self):
        for question, expected in {
            "documento": ["cpf", "identity", "voter"],
            "carteira": ["identity", "work-card"],
        }.items():
            for mode in MODES:
                with self.subTest(question=question, mode=mode):
                    answer = self.ask(question, mode)
                    self.assertEqual(answer["status"], "ambiguous")
                    self.assertEqual([s["id"] for s in answer["services"]], expected)
                    for service in answer["services"]:
                        self.assertIn(service["title"], answer["message"])

    def test_ambiguous_choice_can_be_resolved_by_title(self):
        options = self.ask("documento")["services"]
        for option in options:
            with self.subTest(option=option["id"]):
                answer = self.ask(option["title"])
                self.assertEqual(answer["status"], "matched")
                self.assertEqual(answer["services"][0]["id"], option["id"])

    def test_matched_returns_one_record_with_source_and_warning(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                answer = self.ask("Onde faço o CadÚnico?", mode)
                self.assertEqual(answer["status"], "matched")
                self.assertEqual(len(answer["services"]), 1)
                record = answer["services"][0]
                self.assertEqual(record, self.by_id["social-registry"])
                self.assertCitesSource(answer, record)

    # --- resposta à pergunta real ----------------------------------------

    def test_documents_question_lists_preparation(self):
        record = self.by_id["unemployment"]
        answer = self.ask("Quais documentos preciso levar para o seguro-desemprego?")
        self.assertEqual(answer["services"][0]["id"], "unemployment")
        for item in record["preparation"]:
            self.assertIn(item.rstrip("."), answer["message"])

    def test_where_question_states_channel_and_agency(self):
        answer = self.ask("Onde faço o CadÚnico?")
        record = self.by_id["social-registry"]
        self.assertIn(record["agency"], answer["message"])
        self.assertIn(assistant.CHANNEL_LABELS[record["channel"]], answer["message"])

    def test_cost_and_deadline_are_not_invented(self):
        for question, what in {
            "quanto custa o título de eleitor?": "valores ou taxas",
            "Qual o prazo do título de eleitor?": "prazos",
        }.items():
            for mode in MODES:
                with self.subTest(question=question, mode=mode):
                    answer = self.ask(question, mode)
                    self.assertEqual(answer["status"], "matched")
                    self.assertEqual(answer["services"][0]["id"], "voter")
                    self.assertIn(f"A base não informa {what}", answer["message"])
                    self.assertNotRegex(answer["message"], r"R\$|\d+ dias")

    def test_cost_and_deadline_are_quoted_when_the_base_has_them(self):
        for question, expected in {
            "quanto custa o passaporte?": "R$ 257,25",
            "Qual o prazo do FGTS?": "até 5 dias úteis",
            "quanto tempo demora o seguro desemprego?": "31 a 60 dias corridos",
        }.items():
            for mode in MODES:
                with self.subTest(question=question, mode=mode):
                    answer = self.ask(question, mode)
                    self.assertEqual(answer["status"], "matched")
                    self.assertIn("A base informa:", answer["message"])
                    self.assertIn(expected, answer["message"])
                    self.assertNotIn("A base não informa", answer["message"])

    def test_eligibility_is_not_decided(self):
        answer = self.ask("Quem tem direito ao BPC?")
        self.assertEqual(answer["services"][0]["id"], "bpc")
        self.assertIn("não decide se você tem direito", answer["message"])

    def test_intent_detection(self):
        examples = {
            "Quanto custa o RG?": "cost",
            "Qual o prazo do FGTS?": "deadline",
            "Tenho direito ao Bolsa Família?": "eligibility",
            "Que documentos levar para o CPF?": "documents",
            "Onde tiro o passaporte?": "where",
            "Como tirar o CPF?": "how",
        }
        for question, intent in examples.items():
            with self.subTest(question=question):
                self.assertEqual(assistant.detect_intent(question), intent)

    # --- diferença entre os modelos ---------------------------------------

    def test_modes_select_the_same_service_and_differ_in_format(self):
        for question in ["fui demitido", "Bolsa Família", "Como consultar FGTS?"]:
            with self.subTest(question=question):
                direct = self.ask(question, "direct")
                steps = self.ask(question, "steps")
                self.assertEqual(direct["services"], steps["services"])
                self.assertNotIn("1)", direct["message"])
                self.assertIn("1)", steps["message"])
                self.assertIn("em etapas", steps["message"])
                self.assertCitesSource(direct, direct["services"][0])
                self.assertCitesSource(steps, steps["services"][0])

    def test_message_does_not_repeat_the_whole_guide(self):
        record = self.by_id["unemployment"]
        for mode in MODES:
            with self.subTest(mode=mode):
                message = self.ask("seguro-desemprego", mode)["message"]
                self.assertNotIn(record["summary"], message)
                self.assertNotIn(record["steps"][-1], message)

    def test_pending_review_date_is_reported(self):
        record = {**self.by_id["cpf"], "source": {**self.by_id["cpf"]["source"], "reviewedAt": None}}
        self.assertIn("data de verificação pendente", assistant.cite_source(record))
        self.assertIn("verificada em 19/11/2026", assistant.cite_source(self.by_id["cpf"]))

    # --- entradas inválidas -----------------------------------------------

    def test_question_length_limit(self):
        self.assertIn(self.ask("a" * 500)["status"], {"unsupported", "matched"})
        with self.assertRaisesRegex(ValueError, "500"):
            assistant.answer_question(self.records, "a" * 501)

    def test_invalid_mode_and_type(self):
        with self.assertRaises(ValueError):
            assistant.answer_question(self.records, "CPF", "invented")
        with self.assertRaises(ValueError):
            assistant.answer_question(self.records, None)  # type: ignore[arg-type]

    def test_empty_base_never_matches(self):
        answer = assistant.answer_question([], "CPF")
        self.assertEqual(answer["status"], "unsupported")
        AnswerResponse.model_validate(answer)
        self.assertEqual(assistant.answer_question([], " ")["status"], "empty")


if __name__ == "__main__":
    unittest.main()
