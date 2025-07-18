## get the tailwind service running so we can do our thang

```bash
npx \
    @tailwindcss/cli \
    -i ./static/css/input.css \
    -o ./static/css/site.css \
    --watch
```

## start the uvicorn dev server

```bash

uvicorn \
    ausenergymarket_api:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload \
    --reload-include=*.html \
    --reload-include=*.css \
    --reload-include=*.py 

```
