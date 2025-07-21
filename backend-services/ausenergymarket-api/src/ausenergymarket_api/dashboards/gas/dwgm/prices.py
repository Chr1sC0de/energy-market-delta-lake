from fastapi import Request
from fastapi.responses import HTMLResponse

from ausenergymarket_api.dashboards.gas import router
from ausenergymarket_api.configurations import templates


@router.get("/dwgm/prices", response_class=HTMLResponse)
async def prices(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboards/gas/dwgm/prices/index.html"
    )
