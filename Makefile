APPLICATION_NAME = newground

install:
	python -m pip install .

install-doc:
	python -m pip install .[doc]

install-format:
	python -m pip install .[format]

install-lint-flake8:
	python -m pip install .[lint_flake8]

install-lint-pylint:
	python -m pip install .[lint_pylint]

install-all:
	python -m pip install .[doc,format,lint_flake8,lint_pylint]

uninstall:
	python -m pip uninstall $(APPLICATION_NAME)

