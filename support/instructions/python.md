# Python Craftsmanship Standards

Use `pyproject.toml` as the **single source of truth** for metadata, build system, dependencies and packaging. Avoid legacy `setup.py`, `requirements.txt` or mixed strategies.

Use tools like `hatch`, `poetry`, or `pdm`. Lock dependencies with `poetry.lock` or `pdm.lock`. Virtual environments are **mandatory** and must be reproducible. Scripts to manage them should be explicit and standardized.

Project layout must include a top-level `src/` folder. All runtime logic must live inside **classes or clean modules**. Avoid top-level scripts and global effects. Prefer running entrypoints via CLI or `__main__.py`.

## Imports & Structure

- Always use **absolute imports from the package root**. Even for internal modules, avoid relative imports like `from .utils import X` — use `from mypkg.utils import X` instead.
- Ensure the package is properly structured with `__init__.py` in every directory.
- Respect layering: `src/<project>/core/`, `src/<project>/services/`, `src/<project>/api/`, `tests/`.

## Code Style

- Enforce **PEP8** and use tools like `ruff`, `black`, and `isort`.
- Use `mypy` or `pyright` for type checking.
- Prefer **lazy interpolation** for logging: `logger.debug("user_id=%s", user_id)`
- Avoid deeply nested control structures. Functions must be **short, predictable and cohesive**.
- Document edge-cases and intent-driven logic inline.

## Testing

- Use `pytest` with fixtures and parametrized tests.
- Maintain >85% coverage in business logic. Don’t test only the happy path.
- Prefer unit tests by default. Mock external APIs or IO.
- Structure tests alongside source code or under `tests/` with clear mirroring.

## Documentation

- All public classes/functions must include **Google-style docstrings**.
- Document error behavior, return types, side effects.
- Maintain a `README.md` with install and usage instructions, architecture notes and diagram if applicable.
- For libraries: use `mkdocs` or `pdoc` to publish documentation from source.

## CI/CD

- Validate Python version, lockfile, and environment with `actions/setup-python`.
- Use `python -m build` to build packages.
- Publish to PyPI with `pypa/gh-action-pypi-publish@v1`.
- Lint, test and type-check on each push or PR.

```yaml
name: Python Package CI

on:
  push:
    tags:
      - "v*.*.*"
  pull_request:
    branches: [main]

jobs:
  build-test-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -U pip
          pip install hatch
          hatch env create

      - name: Run tests
        run: hatch run test

      - name: Build
        run: hatch build

      - name: Publish to PyPI
        if: github.event_name == 'push'
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

---

Be clean. Be rigorous. Be pyprojected. 🐍

