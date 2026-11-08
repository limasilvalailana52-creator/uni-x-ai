
import os
import streamlit as st
from engines import UniXEngineHub

st.set_page_config(
    page_title="Uni.X AI — Hub Multi-Agentes",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Uni.X AI")
st.subheader("Hub multi-agentes • execução paralela • validação cruzada")
st.caption("Plataforma de inteligência artificial multiagentes.")

def read_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return os.getenv(name, "").strip()

with st.sidebar:
    st.header("Conexão dos motores")
    st.caption(
        "Configure suas chaves nos Secrets do Streamlit. "
        "Elas não serão exibidas na interface."
    )

    groq_input = st.text_input(
        "Groq API Key (opcional)", type="password"
    )
    gemini_input = st.text_input(
        "Gemini API Key (opcional)", type="password"
    )
    openrouter_input = st.text_input(
        "OpenRouter API Key (opcional)", type="password"
    )

    st.divider()
    st.subheader("Modelos")

    groq_model = st.text_input(
        "Modelo Groq", value="openai/gpt-oss-20b"
    )
    gemini_model = st.text_input(
        "Modelo Gemini", value="gemini-2.5-flash"
    )
    openrouter_model = st.text_input(
        "Modelo OpenRouter", value="openrouter/free"
    )

    st.caption("A disponibilidade dos modelos gratuitos pode variar.")

st.markdown("### Sua demanda")

prompt = st.text_area(
    "Descreva o objetivo para os agentes:",
    height=160,
    placeholder="Ex.: Analise uma ideia, proponha uma arquitetura e identifique riscos técnicos..."
)

if st.button(
    "🚀 Executar agentes",
    type="primary",
    use_container_width=True
):
    keys = {
        "groq": groq_input.strip() or read_secret("GROQ_API_KEY"),
        "gemini": gemini_input.strip() or read_secret("GEMINI_API_KEY"),
        "openrouter": openrouter_input.strip() or read_secret("OPENROUTER_API_KEY"),
    }

    models = {
        "groq": groq_model.strip(),
        "gemini": gemini_model.strip(),
        "openrouter": openrouter_model.strip(),
    }

    if not prompt.strip():
        st.warning("Escreva uma demanda antes de executar.")

    elif not any(keys.values()):
        st.warning(
            "Configure ao menos uma chave nos Secrets do Streamlit "
            "ou informe uma chave na barra lateral."
        )

    else:
        hub = UniXEngineHub(keys=keys, models=models)

        with st.spinner("Agentes trabalhando em paralelo..."):
            drafts = hub.processar_em_lote(prompt.strip())

        st.markdown("### 1. Respostas dos agentes")

        cols = st.columns(max(1, len(drafts)))

        for index, result in enumerate(drafts):
            with cols[index % len(cols)]:
                if result["ok"]:
                    st.success(result["engine"])
                    st.markdown(result["output"])
                else:
                    st.error(result["engine"])
                    st.caption(result["output"])

        validas = [r for r in drafts if r["ok"]]

        if not validas:
            st.error(
                "Nenhum motor conseguiu responder. "
                "Confira as chaves, modelos e limites das APIs."
            )

        else:
            with st.spinner("Validando e cruzando as respostas..."):
                final = hub.validar_respostas(
                    prompt.strip(), validas
                )

            st.markdown("---")
            st.markdown("### 2. Resultado consolidado Uni.X AI")

            if final["ok"]:
                st.markdown(final["output"])

                st.download_button(
                    "⬇️ Baixar relatório (.md)",
                    data=final["output"],
                    file_name="relatorio_uni_x_ai.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            else:
                st.warning(
                    "A validação falhou. "
                    "As respostas individuais continuam disponíveis."
                )
                st.error(final["output"])

st.markdown("---")
st.caption("Uni.X AI • MVP em evolução.")
