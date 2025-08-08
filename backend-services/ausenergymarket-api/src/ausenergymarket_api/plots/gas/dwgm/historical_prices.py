# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from datetime import date, timedelta
from typing import cast

from fastapi.responses import JSONResponse
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from plotly import express as plotly_express
from polars import Date as PolarsDate
from polars import Datetime as PolarsDatetime
from polars import col, lit, scan_delta, when

from ausenergymarket_api.configurations import (
    DEVELOPMENT_ENVIRONMENT,
    NAME_PREFIX,
)
from ausenergymarket_api.plots.gas import router


@router.get("/dwgm/historical_prices")
@cache(expire=3600, coder=PickleCoder)
async def route() -> JSONResponse:
    df_prices = scan_delta(
        f"s3://{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-bronze/aemo/vicgas/bronze_int310_v4_price_and_withdrawals_1"
    )
    df_cleansed = (
        df_prices.with_columns(col.gas_date.str.to_date("%d %b %Y"))
        .with_columns(
            when(col.schedule_interval == 1)
            .then(lit(timedelta(hours=6)))
            .when(col.schedule_interval == 2)
            .then(lit(timedelta(hours=10)))
            .when(col.schedule_interval == 3)
            .then(lit(timedelta(hours=14)))
            .when(col.schedule_interval == 4)
            .then(lit(timedelta(hours=18)))
            .when(col.schedule_interval == 5)
            .then(lit(timedelta(hours=22)))
            .alias("hour")
        )
        .with_columns(scheduling_horizon=(col.gas_date.cast(PolarsDatetime) + col.hour))
        .sort("scheduling_horizon")
    )
    latest_date = cast(
        date,
        (
            df_cleansed.select(col.scheduling_horizon)
            .max()
            .cast(PolarsDate)
            .collect()
            .item()
        ),
    )
    earliest_date = latest_date - timedelta(days=7)

    df_cleanse_collected = df_cleansed.select(
        "scheduling_horizon", "price_value"
    ).collect()

    fig = plotly_express.line(
        df_cleanse_collected,
        x="scheduling_horizon",
        y="price_value",
        template="plotly_white",
    )

    # Add dollar units to the y-axis
    _ = fig.update_layout(
        yaxis=dict(tickprefix="$", title="Price (AUD)"),
        xaxis=dict(
            title="Scheduling Horizon",
            tickformat="%Y-%m-%d",
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
            range=[str(earliest_date), str(latest_date)],
            showspikes=True,
        ),
        hovermode="x",
    )

    # Customize hover to show full datetime
    _ = fig.update_traces(
        mode="lines",
        hovertemplate="Scheduling Horizon: %{x|%Y-%m-%d %H:%M}<br>Price: $%{y:.2f}<extra></extra>",
    )

    return JSONResponse(content={"plot": fig.to_json()}, status_code=200)
