test:
	flake8 kiu_shipping --max-line-length=120 && \
	pytest -v --cov=kiu_shipping --cov-fail-under=100 --cov-report=html

.PHONY: test
