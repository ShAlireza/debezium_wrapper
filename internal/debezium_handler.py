import requests
from tabulate import tabulate
from data.db.models import (
    KafkaConnectModel,
    ConnectorModel,
    TaskModel,
    StatusAttemptModel
)

from internal.slack_handler import SlackHandler

slack_handler = SlackHandler()


class KafkaConnectHandler:

    def __init__(self, host: str, port: int, scheme: str = 'http'):
        self.host = host
        self.port = port
        self.scheme = scheme

        self.full_host = f"{self.scheme}://{self.host}:{self.port}"

        self.connectors = None

        self.new_connectors = []
        self.deleted_connectors = []
        self.failed_tasks = {}

    async def init_db_data(self):
        self.kafka_connect_db = await KafkaConnectModel.get(
            host=self.host,
            port=self.port
        )

        self.connectors_db = await ConnectorModel.filter(
            kafka_connect=self.kafka_connect_db
        ).prefetch_related('tasks')
        self.connectors_db = {
            c.name: c for c in self.connectors_db
        }

    async def get_list_of_connectors(self, params=None):
        if not params:
            params = [
                ('expand', 'info'),
                ('expand', 'status')
            ]
        if self.connectors:
            return self.connectors

        url = self.generate_url(
            f"{self.full_host}/connectors",
            params
        )
        response = requests.get(url)

        self.connectors = response.json()

        return response.json()

    async def check_differences(self):
        connectors = await self.get_list_of_connectors()

        for connector in connectors:
            if connector not in self.connectors_db:
                new_connector = await ConnectorModel.create(
                    kafka_connect=self.kafka_connect_db,
                    name=connector,
                    kind=connectors.get(connector).get('info').get(
                        'config').get('connector.class'),
                    config=connectors.get(connector).get('info').get(
                        'config'
                    )
                )
                self.new_connectors.append(new_connector)

        for connector_db in self.connectors_db:
            if connector_db not in connectors:
                deleted_connector = self.connectors_db.get(connector_db)
                self.deleted_connectors.append(deleted_connector)
                await deleted_connector.delete()

    async def reset_connector_tasks(self):
        connectors = await self.get_list_of_connectors()

        for connector, info in connectors.items():
            connector_tasks = info.get('status').get('tasks')
            for task in connector_tasks:
                if task.get('state') == 'FAILED':
                    task_id = task.get('id')
                    requests.post(
                        url=f'{self.full_host}/connectors/'
                        f'{connector}/tasks/{task_id}/restart'
                    )
                    self.failed_tasks[connector] = info.get('status')

    async def pretty_print_connectors(self):
        connectors = await self.get_list_of_connectors()

        headers = ("ConnectorName", "Connector", "Tasks")
        table = []

        for connector, info in connectors.items():
            table_row = [connector, info.get(
                "status").get("connector").get("state")]
            tasks = ""
            for task in info.get('status').get('tasks'):
                tasks += f'Task{task.get("id")}: {task.get("state")}\t'
            table_row.append(tasks)
            table.append(table_row)

        return str(tabulate(table, headers, tablefmt="pretty"))

    def generate_url(self, url, params):
        params_string = '&'.join(
            [f'{k}={v}' for k, v in params]
        )

        return f'{url}?{params_string}'

    async def clear_cache(self):
        self.connectors = None

    async def notify(self):
        if self.new_connectors:
            for connector in self.new_connectors:
                print('new connector', connector)
                await slack_handler.send_message(
                    [
                        ":white_check_mark: *New Connector Added!*",
                        f"Connector *{connector.name}* added, kind: *{connector.kind}*",
                        f"*Config*\n{connector.config}"
                    ],
                    color='#2eb886'
                )
        if self.deleted_connectors:
            for connector in self.deleted_connectors:
                await slack_handler.send_message(
                    [
                        ":warning: *Connector Deleted!*",
                        f"Connector *{connector.name}* deleted, kind: *{connector.kind}*",
                        f"*Config*\n{connector.config}"
                    ],
                    color='#fc8c03'
                )
        if self.failed_tasks:
            for connector, status in self.failed_tasks.items():
                await slack_handler.send_message(
                    [
                        ":x: *Connector has failed tasks!*",
                        f"Connector *{connector}* has failed task(s)",
                        f"*Status*\n{status}"
                    ],
                    color='#fc0303'
                )
