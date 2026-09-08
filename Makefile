.PHONY: verify verify-package-layout
verify: verify-package-layout
	python3 -B scripts/verify.py

verify-package-layout:
	python3 -B scripts/validate_package_layout.py
