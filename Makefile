.PHONY: verify
verify:
	python3 -B scripts/verify.py
	python3 -B scripts/verify_docs.py
	python3 -B scripts/validate_wait_conformance_manifest.py
	python3 -B scripts/validate_ingress_diagnostic_registry.py
	python3 -B -m unittest discover -s tests -p 'test_verify_docs.py'
\tpython3 -B -m unittest discover -s tests -p 'test_mas_initial_ingress_contract.py'
