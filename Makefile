.PHONY: app-deps
app-deps:
	pip install -r requirements.txt -t src/lib

.PHONY: deps
deps:
	pip install -r requirements.txt
