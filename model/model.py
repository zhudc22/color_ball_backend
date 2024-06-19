from pydantic import BaseModel


class PeriodQuery(BaseModel):
    start_period: int
    num_periods: int
    interval: int
