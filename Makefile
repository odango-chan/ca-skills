.PHONY: verify
verify:
	python3 -B scripts/verify.py
	python3 -B scripts/verify_docs.py
