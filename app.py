import logging
import os
from io import BytesIO

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
from starlette.responses import JSONResponse

from model.model import PeriodQuery
from services.statistics import LotteryStatistics

env = os.environ
# app = FastAPI(docs_url=None, redoc_url=None)  # 用于禁用swagger文档
app = FastAPI()

# 日志配置
logger = logging.getLogger()
logger.propagate = False  # 禁止向上传播
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(levelname)s - %(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d -  %(message)s",
)
# 输出到控制台
to_console = logging.StreamHandler()
to_console.setFormatter(formatter)
logger.addHandler(to_console)

# 输出到文件中
to_file = logging.FileHandler(filename="log.txt")
to_file.setFormatter(formatter)
logger.addHandler(to_file)

# 配置CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_dataframe(file: UploadFile):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload an .xlsx file."
        )
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
    return df


def get_next_numbers(df, start_period):
    """
    获取下一期的数字
    :param df: dataframe
    :param start_period: int, 开始期号
    :return: list
    """
    next_numbers = df[df["期号"] == start_period + 1].values.tolist()
    if not next_numbers:
        raise ValueError("开始期号不正确，找不到下一期的数字")

    try:
        next_period_numbers_data = (
            df.loc[df["期号"] == start_period + 1, df.columns[1:]].dropna(axis=1).values
        )
        if next_period_numbers_data.size > 0:
            next_period_numbers = next_period_numbers_data.astype(int).tolist()[0]
        else:
            next_period_numbers = []
    except IndexError:
        print("下一期数据不可用，检查期号是否正确。")
        next_period_numbers = []

    return next_period_numbers


@app.post("/calculate/fixed/")
async def calculate_fixed_interval(
    start_period: int = Query(...),
    interval: int = Query(...),
    file: UploadFile = File(...),
):
    df = await read_dataframe(file)
    lottery_stats = LotteryStatistics(df)
    try:
        next_numbers = get_next_numbers(df, start_period)
        results = lottery_stats.calculate_fixed_interval_occurrences(
            start_period, interval
        )
        table = lottery_stats.create_calculate_occurrences_table(
            results, next_numbers, start_period
        )
        return table
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Error processing the data", "detail": str(e)},
        )


@app.post("/calculate/multi/")
async def calculate_multi_period(
    file: UploadFile = File(...),
    start_period: int = Query(...),
    num_periods: int = Query(...),
    interval: int = Query(...),
):
    df = await read_dataframe(file)
    lottery_stats = LotteryStatistics(df)
    try:
        results = lottery_stats.calculate_multi_period_occurrences(
            start_period, num_periods, interval
        )
        table = lottery_stats.create_multi_period_table(results)
        return table
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Error processing the data", "detail": str(e)},
        )


@app.post("/calculate/heatmap/")
async def calculate_heatmap(
    file: UploadFile = File(...),
    start_period: int = Query(...),
    num_periods: int = Query(...),
    interval: int = Query(...),
):
    df = await read_dataframe(file)
    lottery_stats = LotteryStatistics(df)
    try:
        results, periods = lottery_stats.calculate_heatmap(
            start_period, num_periods, interval
        )
        return {"results": results, "periods": list(periods)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate/multipliers/")
async def calculate_multipliers(
    file: UploadFile = File(...),
    start_period: int = Query(...),
    interval: int = Query(...),
    num_multipliers: int = Query(...),
):
    df = await read_dataframe(file)
    lottery_stats = LotteryStatistics(df)
    try:
        next_numbers = get_next_numbers(df, start_period)
        results = lottery_stats.calculate_occurrences_by_multipliers(
            start_period, interval, num_multipliers
        )
        table = lottery_stats.create_multipliers_display_table(results, next_numbers)

        return table
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate/accumulative/")
async def calculate_accumulative_intervals(
    file: UploadFile = File(...),
    start_period: int = Query(...),
    interval: int = Query(...),
):
    df = await read_dataframe(file)
    lottery_stats = LotteryStatistics(df)
    try:
        results = lottery_stats.calculate_accumulative_intervals_occurrences(
            start_period, interval
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 启动服务
    host = env.get("HOST") if env.get("HOST") is not None else "0.0.0.0"
    port = int(env.get("PORT")) if env.get("PORT") is not None else 8000
    uvicorn.run(
        app="app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        log_config=None,
    )
