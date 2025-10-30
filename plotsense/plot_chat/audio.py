from io import BytesIO
from typing import BinaryIO

from plotsense.plot_chat.streaming import ChatStreamWrapper

class AudioClient:
    def __init__(self, client):
        self.client = client

    def create_audio_transcription(self, file_obj: BinaryIO, model: str):
        stream = self.client.audio.transcriptions.create(
            file=file_obj,
            model=model,
            language="en",
            stream=True
        )
        return ChatStreamWrapper(stream)

    def create_audio_speech(self, text: str, voice: str, model: str) -> BytesIO:
        with self.client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            response_format="mp3",
            input=text
        ) as response:
            audio_bytes = response.read()
        buffer = BytesIO(audio_bytes)
        buffer.seek(0)
        return buffer
