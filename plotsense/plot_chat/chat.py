from typing import List, Optional

from plotsense.plot_chat.action import ActionClient
from plotsense.plot_chat.streaming import ChatStreamWrapper
from .prompts import get_instructions


class ChatClient:
    def __init__(self, client):
        self.client = client
        self.action_client = ActionClient(client)

    def chat_stream(
        self,
        model: str,
        message: str,
        previous_response_id: Optional[str] = None,
        fileIds: List[str] = [],
        imageUrls: List[str] = [],
        instructions: List[str] = [],
        extension: Optional[str] = None,
        upload_fn=None,
        # df=None,
    ):
        """
        Main streaming entrypoint for chat.
        Handles PlotSense extensions (plotgen, explainer, etc.)
        before falling back to normal chat streaming.
        """

        content_blocks = []
        prompt = message

        print("ChatClient.chat_stream: extension =", extension)
        if extension and extension.lower() == "plotgen":
            print("ChatClient.chat_stream: extension =", extension)
            # Delegate to specialized handler
            action_result = self.action_client.handle_plotgen_extension(
                previous_response_id=previous_response_id if model.lower().startswith("gpt") else None,
                model=model,
                message=message,
                # df=df,
                upload_fn=upload_fn,
            )

            if "error" in action_result:
                content_blocks.append({
                    "type": "input_text",
                    "text": f"⚠️ {action_result['error']}",
                })
            else:
                # Include AI follow-up text + plot image
                content_blocks.append({
                    "type": "input_text",
                    "text": action_result["text"],
                })
                # "type": "input_image" is only supported for gpt models that can render images inline
                if model.lower().startswith("gpt"):
                    content_blocks.append({
                        "type": "input_image",
                        # "text": f"imageUrl: {action_result["image"]}",
                        "image_url": action_result["image"],
                        "detail": "high",
                    })
                else:
                    content_blocks.append({
                        "type": "input_text",
                        "text": f"imageUrl: {action_result["image"]}",
                    })

        # content_blocks = []
        if fileIds:
            for fileId in fileIds:
                content_blocks.append({
                    "type": "input_file",
                    "file_id": fileId
                })

        if imageUrls and model.lower().startswith("gpt"):
            for imageUrl in imageUrls:
                content_blocks.append({
                    "type": f"input_image",
                    # "text": f"{imageUrl}",
                    "image_url": imageUrl,
                    "detail": "high",
                })

        content_blocks.append({
            "type": "input_text",
            "text": prompt
        })
        print("Content blocks:", content_blocks)

        stream = self.client.responses.create(
            model=model,
            instructions=get_instructions(instructions),
            input=[
                {
                    "role": "user",
                    "content": content_blocks
                },
            ],
            previous_response_id=previous_response_id if model.lower().startswith("gpt") else None,
            stream=True,
        )

        return ChatStreamWrapper(stream)

    def prompt(
        self, model: str, prompt: str, previous_response_id: Optional[str] = None
    ) -> str:
        response = self.client.responses.create(
            model=model,
            instructions=get_instructions([]),
            input=prompt,
            previous_response_id=previous_response_id if model.lower().startswith("gpt") else None,
        )
        return response.output_text

    def generate_chat_title(
        self, model: str, assessment_title: str, initial_prompt: str
    ) -> str:
        from .prompts import generate_chat_title_prompt
        prompt = generate_chat_title_prompt(assessment_title, initial_prompt)
        response = self.client.responses.create(
            model=model,
            instructions=get_instructions([]),
            input=prompt
        )
        return response.output_text
