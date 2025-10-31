import re, json, base64
from io import BytesIO
from typing import Optional, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import io

from plotsense.plot_generator.generator import plotgen


class ActionClient:
    """
    Handles AI-powered PlotSense actions (plotgen, explainer, etc.)
    Takes the user's prompt, analyzes it, calls the right PlotSense function,
    and streams back human-like text + generated image.
    """

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib Figure to base64 string."""
        buffer = BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)
        return f"data:image/png;base64,{img_str}"

    def handle_plotgen_extension(
        self,
        model: str,
        message: str,
        # df: pd.DataFrame,
        previous_response_id: Optional[str] = None,
        upload_fn=None,
    ) -> Dict[str, Any]:
        """
        Handles the plotgen extension: analyzes prompt, generates plot,
        and streams AI text + image inline.
        """

        # Based on the dataframe provided (columns: {list(df.columns)}),
        extraction_instructions = f"""
        You are a PlotSense assistant.
        The user says: "{message}"
        identify a suitable plot type and columns to use.
        Respond *only* in JSON like:
        {{
            "df": , (In a format I will later cast to a DataFrame using
            `pd.DataFrame()`)
            "plot_type": "scatter",
            "variables": ["a", "b"]
        }}
        If unsure, respond with:
        {{ "error": "Could not extract columns." }}
        """

        extraction_response = self.client.responses.create(
            model=model,
            instructions=extraction_instructions,
            input=[{"role": "user", "content": [{"type": "input_text", "text": message}]}],
            previous_response_id=previous_response_id,
            stream=False,
        )

        extraction_output = extraction_response.output_text.strip()
        extraction_output = re.sub(r"^```(json)?", "", extraction_output)
        extraction_output = re.sub(r"```$", "", extraction_output).strip()

        print("Extraction JSON:", extraction_output)

        try:
            plot_request = json.loads(extraction_output)
            if "error" in plot_request:
                return {"error": plot_request["error"]}
            df = pd.DataFrame(plot_request["df"])
            plot_type = plot_request["plot_type"]
            variables = plot_request["variables"]
        except json.JSONDecodeError:
            return {"error": "Could not parse the request for plotting."}

        try:
            suggestion_row = pd.Series({
                "plot_type": plot_type,
                "variables": ",".join(variables)
            })
            file_obj = io.BytesIO()
            fig = plotgen(df, suggestion_row, generator="basic")
            fig.savefig(file_obj, format="png", bbox_inches="tight", dpi=150)
            file_obj.seek(0)  # rewind to start
            img_base64 = self._fig_to_base64(fig)
            image_url = img_base64
            if upload_fn:
                image_url = upload_fn(file_obj=file_obj,
                                      key="plotgen_image.png", content_type="image/png")
                print("Uploaded image URL:", image_url)
        except Exception as e:
            return {"error": f"Plot generation failed: {str(e)}"}

        followup_prompt = f"""
        The plot has been generated successfully using:
        - Plot Type: {plot_type}
        - Variables: {variables}

        The image below shows the resulting visualization.
        Include this url in your response: {image_url}
        Please explain the resut of this plot
        in a friendly, human-like conversational tone.
        Showing that the image is provided below
        """

        return {
            "text": followup_prompt.strip(),
            "image": image_url,
        }

