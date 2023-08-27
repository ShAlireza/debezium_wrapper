from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from config import DATABASE_URL


def init_database(app):
    register_tortoise(
        app=app,
        db_url=DATABASE_URL,
        modules={'debezium_wrapper': ["data.db.models"]},
        generate_schemas=False,
        add_exception_handlers=True
    )


Tortoise.init_models(['data.db.models'], 'debezium_wrapper')
