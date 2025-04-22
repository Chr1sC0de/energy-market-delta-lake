# aemo-datalake

## Requirements

- [UV](https://docs.astral.sh/uv/)
- [docker](https://www.docker.com/)
- [aws cli](https://aws.amazon.com/cli/)
- [aws cdk](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html)
- A linux based system

## Environment Variables

```bash
# specify the development environment
DEVELOPMENT_ENVIRONMENT="DEV|TEST|PROD etc..."

# specify thte location where the development is occuring
DEVELOPMENT_LOCATION="LOCAL|AWS| etc."

# defaults to energy-market -> converrt to EnergyMarket during stack creation
NAME_PREFIX="energy-market"
```

## Plan

- [ ] Add preview to polars parquet io manager
- [ ] Add preview to deltalake io manager
- [ ] Create table of schemas
- [ ] Create table of polars types to mibb types
- [ ] Write a script to autogenerate the configurations for each mibb report
- [ ] For each mibb report check the configurations and add required post processing where necessary
- [ ] Create generic asset checks for each mibb report
