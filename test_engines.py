import unittest
from unittest.mock import patch

from engines import UniXEngineHub


class ValidatorFallbackTests(unittest.TestCase):
    def setUp(self):
        self.hub = UniXEngineHub(
            keys={"openrouter": "or-key", "gemini": "gem-key", "groq": "g-key"}
        )
        self.drafts = [{"engine": "Groq", "output": "rascunho", "ok": True}]

    def test_falls_back_to_gemini_when_openrouter_fails(self):
        with patch.object(self.hub, "_call_openrouter", return_value={"engine": "OpenRouter", "ok": False, "output": "limite"}), \
             patch.object(self.hub, "_call_gemini", return_value={"engine": "Gemini", "ok": True, "output": "síntese"}) as gemini, \
             patch.object(self.hub, "_call_groq") as groq:
            result = self.hub.validar_respostas("demanda", self.drafts)
        self.assertTrue(result["ok"])
        self.assertEqual(result["engine"], "Validador (Gemini)")
        gemini.assert_called_once()
        groq.assert_not_called()

    def test_falls_back_to_groq_when_first_two_fail(self):
        with patch.object(self.hub, "_call_openrouter", return_value={"engine": "OpenRouter", "ok": False, "output": "erro 1"}), \
             patch.object(self.hub, "_call_gemini", return_value={"engine": "Gemini", "ok": False, "output": "erro 2"}), \
             patch.object(self.hub, "_call_groq", return_value={"engine": "Groq", "ok": True, "output": "síntese final"}):
            result = self.hub.validar_respostas("demanda", self.drafts)
        self.assertTrue(result["ok"])
        self.assertEqual(result["engine"], "Validador (Groq)")

    def test_reports_all_failures(self):
        with patch.object(self.hub, "_call_openrouter", return_value={"engine": "OpenRouter", "ok": False, "output": "erro 1"}), \
             patch.object(self.hub, "_call_gemini", return_value={"engine": "Gemini", "ok": False, "output": "erro 2"}), \
             patch.object(self.hub, "_call_groq", return_value={"engine": "Groq", "ok": False, "output": "erro 3"}):
            result = self.hub.validar_respostas("demanda", self.drafts)
        self.assertFalse(result["ok"])
        self.assertIn("erro 1", result["output"])
        self.assertIn("erro 2", result["output"])
        self.assertIn("erro 3", result["output"])


if __name__ == "__main__":
    unittest.main()
