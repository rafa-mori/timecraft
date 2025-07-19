# TimeCraft – Python Craftsmanship Standards

## Packaging & Build
- Use `pyproject.toml` exclusivamente, com ferramentas como `poetry`, `hatch` ou `pdm`.
- Remova `venv/` e `requirements.txt`; ambiente virtual deve ser gerado dinamicamente.
- Use extras como `[ai]`, `[all]`, `[db]` conforme já implementado.

## Project Layout
- `src/timecraft_ai/`: toda lógica dentro de classes (ex: `TimeCraftAI`, `DatabaseConnector`).
- Arquivo `__main__.py` na raiz para CLI.
- Módulos divididos em `core/`, `models/`, `api/`, `services/`.

## Imports
- Sempre usar imports absolutos desde `timecraft_ai.module` — nada de `../` ou `.` relative imports.

## Logging & Style
- Use `ruff`, `black`, `isort` e `mypy`.
- Em logs: prefira `logger.debug("id=%s", user_id)` ao invés de f-strings ou concatenação.

## Testing
- `pytest` obrigatório; organize testes em `tests/` ou paralelos à pasta `src/`.
- Use fixtures e parametrização.
- Ambiente mínimo de cobertura de 85% em lógica de negócio, incluindo caminhos de erro.
- Mockar chamadas de webhook, DB e AI.

## Documentation
- Google-style docstrings em todas as classes e funções públicas.
- Atualizar README com exemplos CLI e API Python — já existindo, manter e melhorar.
- Documentar roadmap e arquitetura, idealmente com diagrama na pasta `docs/` ou `tutorials/`.

## CI/CD
- Workflow já configurado. Reforce:
  - lint + test + mypy antes de build
  - build com `python -m build` ou `poetry build`
  - publish automático no PyPI usando a versão da tag (vX.Y.Z)
  - manter badges atualizados

