from openai.types.audio import TranscriptionTextDeltaEvent
from openai.types.responses import ResponseTextDeltaEvent, ResponseTextDoneEvent, ResponseCompletedEvent


class ChatStreamWrapper:
    def __init__(self, stream):
        self._stream = stream
        self.item_id = None
        self.response_id = None

    def __iter__(self):
        for event in self._stream:
            if (
                event.type == "response.output_text.delta"
                and isinstance(event, ResponseTextDeltaEvent)
            ):
                if not self.item_id:
                    self.item_id = event.item_id
                yield event.delta
            elif (
                event.type == "response.output_text.done"
                and isinstance(event, ResponseTextDoneEvent)
            ):
                self.item_id = event.item_id
            elif (
                event.type == "response.completed"
                and isinstance(event, ResponseCompletedEvent)
            ):
                if not self.response_id:
                    self.response_id = event.response.id
            elif (
                event.type == "transcript.text.delta"
                and isinstance(event, TranscriptionTextDeltaEvent)
            ):
                # TranscriptionTextDeltaEvent(delta='To', type='transcript.text.delta', logprobs=None)
                yield event.delta

