.PHONY: verify
verify:
	python3 -B scripts/verify.py
	python3 -B scripts/verify_docs.py
	python3 -B -m unittest discover -s tests -p 'test_verify_docs.py'
