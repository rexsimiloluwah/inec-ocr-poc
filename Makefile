.PHONY: start-web run-docker-shell

# Start the web server
start-web:
	uvicorn src.web.main:app --reload

build-docker-image:
	docker build -t inec-ocr-app .

run-docker-container:
	docker run -p 8040:8040 inec-ocr-app

run-docker-shell:
	docker exec -it a21f92480b0f /bin/bash 


