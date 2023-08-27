import logging
import argparse
import requests

from tabulate import tabulate


# TODO
#  1. log push errors or success with logger
#  2. ...

parser = argparse.ArgumentParser(
    prog='scheduler event pusher',
    description='push an event to queue',
    allow_abbrev=False
)

parser.add_argument(
    '-i',
    '--id',
    metavar='id',
    type=str,
    help='service cronjob id',
    required=True
)

parser.add_argument(
    '-H',
    '--host',
    metavar='host',
    type=str,
    help='service host',
    required=True
)

parser.add_argument(
    '-p',
    '--port',
    metavar='port',
    type=int,
    help='service port',
    required=True
)

parser.add_argument(
    '-l',
    '--log-file',
    metavar='log_file',
    type=str,
    help='log file path',
    required=True
)

if __name__ == '__main__':
    args = parser.parse_args()

    job_id = args.id
    debezium_host = args.host
    debezium_port = args.port
    log_file = args.log_file

    data = {
        'host': debezium_host,
        'port': debezium_port
    }

    response = requests.post(
        'http://localhost:8000/api/debezium/check',
        json=data
    )
    print(response)


def get_parser():
    return parser
