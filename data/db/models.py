from uuid import uuid4

from tortoise.models import Model
from tortoise import fields


class CronJobModel(Model):
    id = fields.CharField(max_length=48, pk=True, default=uuid4)

    enable = fields.BooleanField(default=True)

    host = fields.CharField(max_length=128)
    port = fields.IntField(default=80)

    minute = fields.CharField(max_length=16, default='*')
    hour = fields.CharField(max_length=16, default='*')
    day_of_month = fields.CharField(max_length=16, default='*')
    month = fields.CharField(max_length=16, default='*')
    day_of_week = fields.CharField(max_length=16, default='*')

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    full_command = fields.CharField(max_length=512, null=True)

    def __str__(self):
        return f'{self.technology}, {self.host}, {self.namespace}'

    class Meta:
        table = 'debezium_wrapper.cronjob'


class KafkaConnectModel(Model):
    host = fields.CharField(max_length=128)
    port = fields.IntField(default=8083)

    class Meta:
        table = 'debezium_wrapper.kafkaconnect'


class ConnectorModel(Model):
    kafka_connect = fields.ForeignKeyField(
        model_name="debezium_wrapper.KafkaConnectModel",
        related_name='connectors',
        on_delete=fields.CASCADE
    )

    name = fields.CharField(
        max_length=256
    )

    kind = fields.CharField(
        max_length=256
    )

    config = fields.JSONField()

    class Meta:
        table = 'debezium_wrapper.connector'


class TaskModel(Model):
    connector = fields.ForeignKeyField(
        model_name='debezium_wrapper.ConnectorModel',
        related_name='tasks',
        on_delete=fields.CASCADE
    )

    task_id = fields.SmallIntField(
        default=0
    )

    class Meta:
        table = 'debezium_wrapper.TaskModel'


class StatusAttemptModel(Model):
    connect = fields.ForeignKeyField(
        model_name='debezium_wrapper.ConnectorModel',
        related_name='attempts',
        on_delete=fields.CASCADE
    )

    created_at = fields.DatetimeField(
        auto_now_add=True
    )

    updated_at = fields.DatetimeField(
        auto_add=True
    )

    has_failed_task = fields.BooleanField(
        default=False
    )

    # failed_tasks =  # TODO add failed tasks to status attempt

    number_of_tasks = fields.SmallIntField(
        default=1
    )

    class Meta:
        table = 'debezium_wrapper.statusattempt'
