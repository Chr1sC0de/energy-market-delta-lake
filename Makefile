development-image:
	podman build . -t emdl-dev:latest

development-container:
	./scripts/development-container-run

attach:
	./scripts/development-container-attach

localstack:
	./scripts/in-podman-run-localstack
