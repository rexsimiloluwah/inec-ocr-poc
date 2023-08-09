.PHONY: start-web run-docker-shell

# Start the web server
start-web:
	uvicorn src.web.main:app --reload

build-docker-image:
	docker build -t inec-ocr-app .

run-docker-container:
	docker run -p 8040:8040 inec-ocr-app

run-pre-commit:
	pre-commit run --all-files

test:
	pytest 


