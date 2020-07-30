.PHONY: app-deps
app-deps:
	pip install -Ur requirements.txt -t src/lib

.PHONY: deps
deps:
	pip install -r requirements.txt
