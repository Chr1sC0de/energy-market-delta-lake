# hadolint ignore=DL3007
FROM docker.io/library/node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY astro.config.mjs tsconfig.json ./
COPY public ./public
COPY src ./src
RUN npm run build

# hadolint ignore=DL3007
FROM docker.io/library/caddy:latest

COPY Caddyfile /etc/caddy/
COPY --from=build /app/dist/ /var/www/html/
