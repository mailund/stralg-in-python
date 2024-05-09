.PHONY: venv

venv:
	python3.12 -m venv .stralg_env
	. .stralg_env/bin/activate
	./.stralg_env/bin/python -m pip install -r requirements.txt
	./.stralg_env/bin/python -m pip install -e .
