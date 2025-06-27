#!/bin/bash

export COGNITO_DAGSTER_AUTH_CLIENT_ID=6atnjc3u1bvsv8cgi0bql1ji8c
export COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL=https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_u7HteRN6X/.well-known/openid-configuration
export COGNITO_DAGSTER_AUTH_CLIENT_SECRET=1nf758hm666bej4u3f9ef95b0nh38voipb18u53gvpdfqfv4vu9s
export WEBSITE_ROOT_URL=http://localhost:3000

uvicorn main:app --host localhost --port 8000
