# -*- encoding: utf-8 -*-

from contextlib import asynccontextmanager

from pyfiglet import Figlet
from termcolor import colored
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.core import f_log, TITLE, ALLOWED_HOSTS
from src.utils import use_static_swagger
from src.aop import ErrorLoggingMiddleware
from src.api import router

@asynccontextmanager
async def lifespan(app: FastAPI):

    colored_art = colored(Figlet(font='slant').renderText(TITLE).rstrip('\n'), 'green')
    f_log.info(colored_art)
    print(colored_art)

    yield

    f_log.info("Service shutdown...")


app = FastAPI(
    title=TITLE,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=ALLOWED_HOSTS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ErrorLoggingMiddleware)
app.include_router(router, prefix="")


use_static_swagger(app)


if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)