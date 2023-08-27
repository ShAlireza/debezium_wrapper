import sys

__all__ = ('CronJob', 'CronJobPost', 'CronJobResponse', 'CronJobPatch',
           'CronJobShared', 'KafkaConnect', 'StatusAttempt', 'Check',
           'Connector')
import uuid
from datetime import datetime
from typing import Optional

from tortoise.contrib.pydantic import (
    pydantic_model_creator,
    pydantic_queryset_creator
)
from tortoise import Tortoise

from data.db.models import KafkaConnectModel
from pydantic import BaseModel, Field

try:
    from config import PYTHONPATH
except ImportError:
    raise ImportError('PYTHONPATH not found in config file')

try:
    from config import LOG_FILE
except ImportError:
    raise ImportError('LOG_FILE not found in config file')


__all__ = ('CronJob', 'CronJobPost', 'CronJobResponse', 'CronJobPatch')

CRON_TIME_REGEX = r'^((\d+,)+\d+|([*]/\d+)|(\d+(/|-)\d+)|\d+|[*])$'


class CronJobBase(BaseModel):
    enable: Optional[bool] = Field(
        True,
        title="Enable job"
    )

    host: str = Field(
        ...,
        title='Service host'
    )

    port: Optional[int] = Field(
        None,
        title='Service host port'
    )

    minute: str = Field(
        "*",
        title='Cron job minute field',
        regex=CRON_TIME_REGEX
    )

    hour: str = Field(
        '*',
        title='Cron job hour field',
        regex=CRON_TIME_REGEX
    )

    day_of_month: str = Field(
        '*',
        title='Cron job day of the month field',
        regex=CRON_TIME_REGEX
    )

    month: str = Field(
        '*',
        title='Cron job month field',
        regex=CRON_TIME_REGEX
    )

    day_of_week: str = Field(
        '*',
        title='Cron job day of the week field',
        regex=CRON_TIME_REGEX
    )

    @classmethod
    def instance_from_tortoise_model(cls, model):
        key_values = {k: getattr(model, k) for k in model._meta.fields}
        return cls(**key_values)


class CronJobShared(CronJobBase):
    id: str = Field(
        title="Cron job unique id",
        default_factory=lambda: str(uuid.uuid4())
    )

    full_command: str = Field(
        None,
        title='Cron job command to execute'
    )


class CronJobPost(CronJobBase):
    pass


class CronJobPatch(CronJobBase):
    host: Optional[str] = Field(
        None,
        title='Service host'
    )


class CronJobResponse(CronJobBase):
    id: str = Field(
        ...,
        title='Cron job unique id'
    )

    created_at: datetime = Field(
        ...,
        title='Job create time'
    )
    updated_at: datetime = Field(
        ...,
        title='Job last update time'
    )

    class Config:
        orm_mode = True


class CronJob(CronJobShared):
    def generate_full_command(self):
        self.full_command = (f'{sys.executable} '
                             f'{PYTHONPATH}/internal/reset_failed_tasks.py '
                             f'--id {self.id} '
                             f'--host {self.host} '
                             f'--port {self.port} '
                             f'--log-file {LOG_FILE} ')

        return self.full_command


class KafkaConnect(BaseModel):
    host: str = Field(
        ...,
        title='Kafka connect host'
    )

    port: int = Field(
        ...,
        title='Kafka connect port number'
    )

    class Config:
        orm_mode = True


class Check(BaseModel):
    host: str = Field(
        ...,
        title='Kafka connect host'
    )

    port: str = Field(
        ...,
        title='Kafka connect port'
    )


print('before pydantic create')
Tortoise.init_models(['data.db.models'], 'debezium_wrapper')
KafkaConnectList = pydantic_queryset_creator(KafkaConnectModel)
