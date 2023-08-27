import logging
from typing import List

from fastapi import APIRouter, Depends, Body, Path, status, Response
from tortoise import Tortoise
from tortoise.contrib.pydantic import (
    pydantic_model_creator,
    pydantic_queryset_creator
)
from internal.debezium_handler import KafkaConnectHandler
from data.pydantic.models import Check, KafkaConnectList, KafkaConnect
from data.db.models import KafkaConnectModel

from config import LOG_FILE
from config import slack_client


router = APIRouter()

__all__ = ('router',)

logging.basicConfig(
    format='%(asctime)s  %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=LOG_FILE,
    level=logging.INFO
)


@router.post("/", response_model=KafkaConnect)
async def add_kafka_connect(
    response: Response,
    info: KafkaConnect = Body(
        ...,
        title='Kafka connect data',
    ),
):
    exists = await KafkaConnectModel.filter(
        host=info.host,
        port=info.port
    ).exists()
    if exists:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return info

    await KafkaConnectModel.create(
        host=info.host,
        port=info.port
    )

    return info


@router.get("/", response_model=KafkaConnectList)
async def get_kafka_connects():
    kafka_connects = await KafkaConnectList.from_queryset(
        KafkaConnectModel.all().prefetch_related('connectors')
    )
    return kafka_connects


@router.post("/check")
async def check(
        check: Check = Body(
            ...,
            title='Job to be added to scheduling service'
        )
):
    handler = KafkaConnectHandler(
        host=check.host,
        port=check.port
    )

    await handler.init_db_data()

    params = [('expand', 'status'), ('expand', 'info')]

    await handler.check_differences()

    print(handler.new_connectors, handler.deleted_connectors)

    await handler.get_list_of_connectors(
        params=params
    )

    log = await handler.pretty_print_connectors()

    logging.info("================ Started Job ================")

    logging.info(log)

    await handler.reset_connector_tasks()

    await handler.clear_cache()

    await handler.get_list_of_connectors(
        params=params
    )

    log = await handler.pretty_print_connectors()

    logging.info(log)

    logging.info("================ Finished Job ================\n\n")

    await handler.notify()

    return
