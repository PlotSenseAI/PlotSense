from openai import OpenAI
from .chat import ChatClient
from .audio import AudioClient
from .file import FileClient
from .realtime import RealtimeClient


class PlotChatClient:
    def __init__(self, api_key: str = ""):
        self.client = OpenAI(
            api_key=api_key,
            # base_url="https://api.groq.com/openai/v1"
        )

        self.chat = ChatClient(self.client)
        self.audio = AudioClient(self.client)
        self.files = FileClient(self.client)
        self.realtime = RealtimeClient(self.client)

