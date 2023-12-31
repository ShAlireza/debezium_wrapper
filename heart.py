from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


from routers import cron_job_router

from config import DATABASE_URL

app = FastAPI()

register_tortoise(
    app=app,
    db_url=DATABASE_URL,
    modules={'debezium_wrapper': ["data.db.models"]},
    generate_schemas=False,
    add_exception_handlers=True
)

app.include_router(
    cron_job_router,
    prefix='/api/cron',
    tags=['Cron']
)
