NAME = fastapi-example
VERSION = 0.1.0
REPOSITORY = uhub.service.ucloud.cn/vst_repository

build:
	docker build -t ${REPOSITORY}/${NAME}:${VERSION} .

push:
	docker push ${REPOSITORY}/${NAME}:${VERSION}

pull:
	docker pull ${REPOSITORY}/${NAME}:${VERSION}

up:
	docker compose up server -d

down:
	docker compose down server

run:
	docker run --rm -it --name fastapi-example -p 8000:8000 -v ./data:/app/data -v ./logs:/app/logs -v ./static:/app/static -v ./templates:/app/templates ${REPOSITORY}/${NAME}:${VERSION}

log:
	docker compose logs -f --tail 0 server