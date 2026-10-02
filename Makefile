.PHONY: install lint test smoke reverse-test validate

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

smoke:
	python -m dq_rescue.cli smoke

reverse-test:
	python -m dq_rescue.cli reverse-test

validate: lint test smoke reverse-test
