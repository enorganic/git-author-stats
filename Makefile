SHELL := bash
PYTHON_VERSION := 3.8

# Create or update your local virtual environment
install:
	{ rm -R venv || echo "" ; } && \
	{ python$(PYTHON_VERSION) -m venv venv || py -$(PYTHON_VERSION) -m venv venv ; } && \
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	pip install --upgrade pip && \
	pip install -r dev_requirements.txt -r requirements.txt -e '.[all]' && \
	{ mypy --install-types --non-interactive || echo "" ; } && \
	echo "Installation complete"

# Create or update a CI/CD virtual environment
ci-install:
	{ python3 -m venv venv || py -3 -m venv venv ; } && \
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	python3 -m pip install --upgrade pip && \
	pip install -r requirements.txt -e '.[all]' && \
	echo "Installation complete"

# Create your local virtual environment from scratch, ignoring frozen requirements
reinstall:
	{ rm -R venv || echo "" ; } && \
	{ python$(PYTHON_VERSION) -m venv venv || py -$(PYTHON_VERSION) -m venv venv ; } && \
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	pip install --upgrade pip && \
	pip install -r dev_requirements.txt -r ci_requirements.txt -r test_requirements.txt -e '.[all]' && \
	{ mypy --install-types --non-interactive || echo "" ; } && \
	make requirements && \
	echo "Installation complete"

# Cleanup your virtual environment of un-needed packages and
# delete all files which are ignored by git and not needed for development
clean:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	daves-dev-tools uninstall-all\
	 -e '.[all]'\
     -e pyproject.toml\
     -e tox.ini\
     -e requirements.txt && \
	daves-dev-tools clean -e .env

# Distribute the package to PyPi
distribute:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	daves-dev-tools distribute --skip-existing

# Upgrade all dependencies in your virtual environment to their latest
# compatible version, and update your project files to align with the
# upgraded dependencies
upgrade:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	dependence freeze\
	 -nv '*' '.[all]' pyproject.toml tox.ini daves-dev-tools dependence jupyter \
	 > .requirements.txt && \
	pip install --upgrade --upgrade-strategy eager\
	 -r dev_requirements.txt -r .requirements.txt && \
	rm .requirements.txt && \
	make requirements

# Update your project requirement specifications to align with currently
# installed version of all dependencies
requirements:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	dependence update\
	 -aen all\
	 setup.cfg pyproject.toml tox.ini && \
	dependence freeze\
	 -e pip\
	 -e wheel\
	 '.[all]' pyproject.toml tox.ini ci_requirements.txt \
	 > requirements.txt && \
	dependence freeze -nv '*' -d 0 tox.ini > test_requirements.txt

# Run unit tests
test:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	if [[ "$$(python -V)" = "Python $(PYTHON_VERSION)."* ]] ;\
	then tox -r -p -o ;\
	else tox -r -e pytest,pytest-github ;\
	fi

# Apply formatting and run code quality checks
format:
	{ . venv/bin/activate || venv/Scripts/activate.bat ; } && \
	isort . && black . && flake8 && mypy
