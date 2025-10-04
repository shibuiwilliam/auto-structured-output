DIR := $(shell pwd)
GIT_COMMIT := $(shell git rev-parse HEAD)

############ COMMON COMMANDS ############
SRC := $(DIR)/

.PHONY: lint
lint:
	uvx ruff check --extend-select I --fix $(SRC)

.PHONY: fmt
fmt:
	uvx ruff format $(SRC)

.PHONY: lint_fmt
lint_fmt: lint fmt

.PHONY: mypy
mypy:
	uvx mypy $(SRC) --namespace-packages --explicit-package-bases

.PHONY: test
test:
	LOG_LEVEL=DEBUG pytest -s -v tests/

.PHONY: build
build:
	uvx --from build pyproject-build -s -w

.PHONY: install
install:
	pip install -e .

.PHONY: clean
clean:
	rm -rf build dist .eggs *.egg-info .pytest_cache .mypy_cache .ruff_cache
