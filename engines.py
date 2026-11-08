import concurrent.futures
from typing import Dict, List, Any

import requests


class UniXEngineHub:
    """Executa motores configurados em paralelo e faz uma segunda etapa de revisão."""

    def __init__(self, keys: Dict[str, str], models: Dict[str, str] | None = None):
        self.keys = {name: (value or "").strip() for name, value in keys.items()}
        self.models = models or {}
        self.timeout = 90

    def _post_openai_compatible(self, engine: str, url: str, prompt: str) -> Dict[str, Any]:
        key = self.keys.get(engine, "")
        if not key:
            return {"engine": engine, "ok": False, "output": "Chave não configurada."}

        model = self.models.get(engine) or (
            "openai/gpt-oss-20b" if engine == "groq" else "openrouter/free"
        )
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if engine == "openrouter":
            headers["HTTP-Referer"] = "https://streamlit.app"
            headers["X-Title"] = "Uni.X AI"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Você é um agente especialista. Responda em português, com clareza, precisão e estrutura."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            data = response.json()
            if not response.ok:
                message = data.get("error", {}).get("message", response.text[:500])
                return {"engine": engine, "ok": False, "output": f"HTTP {response.status_code}: {message}"}
            content = data["choices"][0]["message"]["content"]
            return {"engine": engine, "ok": True, "output": content or "(Resposta vazia)"}
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            return {"engine": engine, "ok": False, "output": f"Falha na chamada: {exc}"}

    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        result = self._post_openai_compatible(
            "groq", "https://api.groq.com/openai/v1/chat/completions", prompt
        )
        result["engine"] = "Groq"
        return result

    def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        result = self._post_openai_compatible(
            "openrouter", "https://openrouter.ai/api/v1/chat/completions", prompt
        )
        result["engine"] = "OpenRouter"
        return result

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        key = self.keys.get("gemini", "")
        if not key:
            return {"engine": "Gemini", "ok": False, "output": "Chave não configurada."}

        model = self.models.get("gemini") or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        try:
            response = requests.post(
                url,
                params={"key": key},
                json=payload,
                timeout=self.timeout,
            )
            data = response.json()
            if not response.ok:
                message = data.get("error", {}).get("message", response.text[:500])
                return {"engine": "Gemini", "ok": False, "output": f"HTTP {response.status_code}: {message}"}
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"engine": "Gemini", "ok": True, "output": text}
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            return {"engine": "Gemini", "ok": False, "output": f"Falha na chamada: {exc}"}

    def processar_em_lote(self, prompt: str) -> List[Dict[str, Any]]:
        jobs = []
        if self.keys.get("groq"):
            jobs.append(self._call_groq)
        if self.keys.get("gemini"):
            jobs.append(self._call_gemini)
        if self.keys.get("openrouter"):
            jobs.append(self._call_openrouter)

        if not jobs:
            return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            futures = [pool.submit(job, prompt) for job in jobs]
            return [future.result() for future in futures]

    def validar_respostas(self, prompt: str, resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Pede a um motor uma crítica independente e uma síntese baseada nas respostas."""
        if not resultados:
            return {"engine": "Validador", "ok": False, "output": "Não há respostas para validar."}

        material = "\n\n".join(
            f"### {item['engine']}\n{item['output']}" for item in resultados
        )
        validation_prompt = f"""
Você é o agente auditor e integrador do Uni.X AI.
Faça uma validação cruzada real das propostas abaixo para a demanda original.

DEMANDA ORIGINAL:
{prompt}

RESPOSTAS DOS AGENTES:
{material}

ENTREGUE:
1. Síntese da melhor solução.
2. Pontos em que os agentes concordam.
3. Divergências, erros ou afirmações que precisam de confirmação.
4. Riscos, limitações e pressupostos.
5. Plano de ação em etapas.
Não invente fatos. Diferencie o que foi verificado do que é hipótese. Responda em português.
"""
        # Preferência para revisão: OpenRouter, depois Gemini, depois Groq.
        if self.keys.get("openrouter"):
            validator = self._call_openrouter(validation_prompt)
        elif self.keys.get("gemini"):
            validator = self._call_gemini(validation_prompt)
        elif self.keys.get("groq"):
            validator = self._call_groq(validation_prompt)
        else:
            return {"engine": "Validador", "ok": False, "output": "Nenhuma chave disponível."}

        validator["engine"] = f"Validador ({validator['engine']})"
        return validator
