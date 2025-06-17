SHELL := bash

# Create all environments
install:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	hatch env create default && \
	make requirements && \
	echo "Installation complete"

# Re-create all environments, from scratch (no reference to pinned
# requirements)
reinstall:
	{ hatch --version || pipx install --upgrade hatch || python3 -m pip install --upgrade hatch ; } && \
	hatch env prune && \
	make

# This will upgrade all requirements, and refresh pinned requirements to
# match
upgrade:
	hatch run dependence freeze\
	 --include-pointer /tool/hatch/envs/default\
	 -nv '*'\
	 pyproject.toml > .requirements.txt && \
	hatch run pip install --upgrade --upgrade-strategy eager\
	 -r .requirements.txt
	rm .requirements.txt && \
	make requirements

# This will update requirement specifiers to align with the
# package versions installed in your environment
requirements:
	hatch run dependence update\
	 --include-pointer /tool/hatch/envs/default\
	 pyproject.toml && \
	echo "Requirements Updated"

# Apply formatting rules and perform static analysis and type checking
format:
	hatch run nbqa ruff --fix . && \
	hatch run nbqa mypy . && \
	echo "Formatting Successful"

# Cleanup untracked files
clean:
	git clean -f -e .vscode -e .idea -x .
