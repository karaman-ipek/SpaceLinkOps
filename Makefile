.PHONY: install test simulate dashboard
install:
	pip install -e ".[dashboard,dev]"
test:
	python -m compileall -q src dashboard
	PYTHONPATH=src python scripts/generate_traceability.py
	pytest --cov=spacelinkops --cov-report=term-missing -q
	mypy src
evidence:
	PYTHONPATH=src python scripts/generate_traceability.py
	PYTHONPATH=src python scripts/build_release_evidence.py
simulate:
	spacelinkops scenarios/nominal.yaml --output outputs/nominal.json --monte-carlo 100 --station-ablation
dashboard:
	streamlit run dashboard/app.py
