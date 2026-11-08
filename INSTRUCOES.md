# Correção do Uni.X AI

## O que muda
- O validador tenta OpenRouter, depois Gemini e depois Groq.
- Se um provedor falhar, tenta o próximo configurado.
- Se todos falharem, mostra os erros individuais.
- Inclui testes automatizados e `.gitignore` para evitar envio de segredos e cache Python.

## Arquivos
- `engines.py`: substituir o arquivo atual do repositório.
- `test_engines.py`: adicionar para testes locais/CI.
- `.gitignore`: adicionar na raiz se ainda não existir.

## Testes
Execute `python -m unittest -v` no ambiente do projeto.

## Segurança
Nunca coloque chaves de API em arquivos versionados, prints ou mensagens. Use os Secrets do Streamlit.
