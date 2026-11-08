# Uni.X AI — Hub Multi-Agentes

MVP Streamlit com chamadas paralelas a Groq, Gemini e OpenRouter, seguido por uma etapa de validação cruzada.

## Estrutura

```text
uni-x-ai/
├── app.py
├── engines.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Executar

O Streamlit Community Cloud instala as dependências de `requirements.txt`. Para executar localmente, use Python 3.10+:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Chaves de API

É possível inserir as chaves na barra lateral do app. Para implantação, prefira cadastrar os valores em **App settings → Secrets** no Streamlit Community Cloud:

```toml
GROQ_API_KEY = "sua-chave-groq"
GEMINI_API_KEY = "sua-chave-gemini"
OPENROUTER_API_KEY = "sua-chave-openrouter"
```

Não envie chaves para o GitHub, nem coloque `secrets.toml` no repositório.

## Publicar pelo navegador do tablet

1. Crie um repositório no GitHub, por exemplo `uni-x-ai`.
2. Abra o repositório e use **Add file → Upload files**.
3. Envie `app.py`, `engines.py`, `requirements.txt`, `README.md` e `.gitignore` (ou envie o ZIP descompactado; o GitHub não executa ZIP como projeto).
4. Toque em **Commit changes**.
5. Acesse https://share.streamlit.io/ e entre com GitHub.
6. Toque em **Create app** e escolha **Yup, I have an app**.
7. Selecione o repositório, a branch `main` e o arquivo principal `app.py`.
8. Em **Advanced settings → Secrets**, cole as chaves no formato TOML acima. Salve e toque em **Deploy**.

## Sobre custo zero

- O Streamlit Community Cloud oferece hospedagem comunitária gratuita, sujeita aos termos e limites do serviço.
- Groq e Gemini têm condições e limites gratuitos que podem mudar.
- OpenRouter: escolha `openrouter/free` ou um modelo com sufixo `:free`. Modelos gratuitos têm limites e disponibilidade variável. O modelo Claude 3.5 Sonnet indicado no código inicial não deve ser presumido gratuito.
- O app não cobra nem controla o consumo das chaves. Confira o painel de uso de cada provedor.

## Segurança e limitações do MVP

- Não compartilhe a URL publicamente se o app permitir que qualquer visitante use suas chaves digitadas.
- Para uso pessoal, mantenha as chaves em Secrets e considere restringir o acesso ao app.
- Esta versão executa agentes quando você toca no botão. Ela ainda não é autônoma/proativa: não tem agendador, memória persistente, filas, ferramentas externas nem execução contínua.
- As respostas dos modelos não constituem validação factual garantida. A revisão cruzada ajuda a encontrar divergências, mas não substitui testes ou fontes confiáveis.
