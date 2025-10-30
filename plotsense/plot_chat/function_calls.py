import json
from openai.types.responses import ResponseInputParam, ToolParam, FunctionToolParam
from openai.types.responses.response_input_param import Message
import pandas as pd
from typing import List, Dict, Callable, Optional
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import base64

from plotsense.explanations.explanations import explainer
from plotsense.plot_generator.generator import plotgen
from plotsense.visual_suggestion.suggestions import recommender


class FunctionCallClient:
    """Orchestrates OpenAI function calls for multiple tools automatically."""

    # Predefined internal tools mapping
    TOOL_DEFINITIONS = {
        "plotgen": {
            "type": "function",
            "name": "generate_plot",
            "description": "Generate a plot based on suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "df": {"type": "string", "description": "JSON-serialized DataFrame"},
                    "suggestion": {"type": "integer", "description": "Index or row identifier of suggestion"}
                },
                "required": ["df", "suggestion"],
                "additionalProperties": False
            }
        },
        "explainer": {
            "type": "function",
            "name": "explain_plot",
            "description": "Generate an explanation for a plot",
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_object": {"type": "string", "description": "Reference to internal Figure object"}
                },
                "required": ["plot_object"],
                "additionalProperties": False
            }
        },
        "recommender": {
            "type": "function",
            "name": "recommend",
            "description": "Generate top-N recommended plots or actions",
            "parameters": {
                "type": "object",
                "properties": {
                    "df": {"type": "string", "description": "JSON-serialized DataFrame"},
                    "n": {"type": "integer", "description": "Number of recommendations to return"}
                },
                "required": ["df", "n"],
                "additionalProperties": False
            }
        }
    }

    # Map tool identifiers to actual Python functions
    TOOL_FUNCTION_MAPPING = {
        "plotgen": lambda df, suggestion, api_key="", **kwargs: plotgen(
            pd.read_json(StringIO(df)),
            api_keys={"openai": api_key},
            suggestion=suggestion, suggestions_df=pd.read_json(StringIO(df)),
            selected_models = [("openai", "gpt-5"), ("openai", "gpt-4-turbo")],
            **kwargs
        ),
        "explainer": lambda plot_object, api_key="", **kwargs: explainer(
            plot_object,
            api_keys={"openai": api_key},
            selected_models = [("openai", "gpt-5"), ("openai", "gpt-4-turbo")],
            **kwargs
        ),
        "recommender": lambda df, n=5, api_key="", **kwargs: recommender(
            pd.read_json(StringIO(df)), n=n,
            api_keys={"openai": api_key},
            selected_models = [("openai", "gpt-5"), ("openai", "gpt-4-turbo")],
            **kwargs
        )
    }

    def __init__(self, client):
        self.client = client
        self.tools: list[ToolParam] = []
        self.function_mapping: Dict[str, Callable] = {}

    def register_tools(self, tool_names: List[str]):
        """Register tools by their identifier name (plotgen, explainer, etc.)"""
        for name in tool_names:
            if name not in self.TOOL_DEFINITIONS:
                raise ValueError(f"No predefined tool for identifier '{name}'")
            tool_def = self.TOOL_DEFINITIONS[name]
            if tool_def['name'] in self.function_mapping:
                continue  # Already registered

            func_tool: FunctionToolParam = {
                "name": tool_def["name"],
                "description": tool_def.get("description"),
                "parameters": tool_def["parameters"],
                "type": "function",
                "strict": True
            }
            self.tools.append(func_tool)
            self.function_mapping[tool_def['name']] = self.TOOL_FUNCTION_MAPPING[name]

    def handle_user_input(
        self, 
        user_input: str, 
        instructions: Optional[str] = None
    ) -> str:
        """Main orchestrator for multi-tool function calls"""
        input_list: ResponseInputParam = [
            Message(
                role="user",
                type="message",
                content=[
                    {"type": "input_text", "text": user_input}
                ]
            )
        ]

        calls_remaining = True
        final_response_text = ""
        conversation_history = input_list.copy()

        while calls_remaining:
            # Ask model with all tools
            response = self.client.responses.create(
                model="gpt-5",
                tools=self.tools,
                input=conversation_history,
                instructions=instructions,
                # stream=True,
            )

            calls_remaining = False  # will be True if model requests any function call
            new_inputs = []

            # Process function calls
            for item in response.output:
                if item.type == "function_call":
                    calls_remaining = True
                    func_name = item.name
                    args = json.loads(item.arguments)

                    if func_name in self.function_mapping:
                        print("Args:", args)
                        # Fix suggestion parameter type
                        if func_name == "generate_plot" and "suggestion" in args:
                            if isinstance(args["suggestion"], str) and args["suggestion"].isdigit():
                                args["suggestion"] = int(args["suggestion"])

                        result = self.function_mapping[func_name](
                            **args,
                            api_key=self.client.api_key
                        )

                        # Convert result to JSON-serializable format
                        if isinstance(result, pd.DataFrame):
                            result_serializable = result.to_json(orient='split')
                        elif isinstance(result, Figure):
                            buf = io.BytesIO()
                            result.savefig(buf, format='png')
                            buf.seek(0)
                            result_serializable = {"image_base64": base64.b64encode(buf.read()).decode('utf-8')}
                        else:
                            result_serializable = result

                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(result_serializable)
                        })
            # Append outputs to conversation history so next request has context
            conversation_history.extend(new_inputs)

            # If no more function calls, capture final text output
            if not calls_remaining:
                final_response_text = response.output_text

        return final_response_text
