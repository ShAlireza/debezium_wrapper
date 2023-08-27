from config import slack_client
from config import SLACK_CHANNEL


class SlackHandler:

    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(
            self,
            channel: str = SLACK_CHANNEL,
            username: str = "DebeziumWrapper"
    ):
        self.channel = channel
        self.username = username

    async def send_message(self, messages, color):
        payload = self.get_payload(messages, color)

        await slack_client.chat_postMessage(**payload)

    def get_payload(self, messages, color):
        return {
            "channel": self.channel,
            "username": self.username,
            "attachments": [
                {'blocks': self.get_blocks(messages), 'color': color}
            ]
        }

    def get_blocks(self, messages):
        blocks = []

        for i, message in enumerate(messages):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            )
            if i != len(messages) - 1:
                blocks.append(self.DIVIDER_BLOCK)

        return blocks
