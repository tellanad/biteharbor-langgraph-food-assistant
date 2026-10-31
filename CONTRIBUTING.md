# Contributing

Create a focused branch, add or update tests, and run the quality checks before opening a pull
request:

```bash
uv sync --frozen --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Keep model behavior behind injectable boundaries so tests can run without paid API calls. New order
features must preserve customer scoping, and menu features must enforce exact constraints outside
the model. Never commit `.env`, API keys, customer records, or local checkpoint databases.
