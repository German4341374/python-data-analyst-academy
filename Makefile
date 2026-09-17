.PHONY: verify verify-local content
verify:
	python scripts/verify.py --full
verify-local:
	python scripts/verify.py
content:
	python scripts/build_content.py
	python scripts/validate_content.py
