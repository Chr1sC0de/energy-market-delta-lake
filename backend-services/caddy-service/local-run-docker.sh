docker run -it \
    -p 80:80 \
    -e ROOT_DNS=:80 \
    -e DAGSTER_AUTHSERVER= \
    -e DAGSTER_WEBSERVER= \
    "$(docker build -q .)" \
    sh
