PY ?= python3

install:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest -q

quick:
	$(PY) -m enemnoise all --quick

experiments:
	$(PY) -m enemnoise all

serve:
	$(PY) -m enemnoise serve

modelcards:
	$(PY) scripts/gen_model_cards.py
