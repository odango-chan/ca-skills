.PHONY: verify-package-layout
verify-package-layout:
	python3 -B scripts/validate_package_layout.py
