import base64
import os
import matplotlib.pyplot as plt
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv
from groq import Groq
import warnings
import builtins

load_dotenv()

class PlotExplainer:
    DEFAULT_MODELS = {
        'groq': ['meta-llama/llama-4-scout-17b-16e-instruct',
                  'meta-llama/llama-4-maverick-17b-128e-instruct'],
    }
    
    def __init__(
            self, 
            api_keys: Optional[Dict[str, str]] = None, interactive: bool = True, timeout: int = 30):
        api_keys = api_keys or {}
        self.api_keys = {
            'groq': os.getenv('GROQ_API_KEY')
        }
        self.api_keys.update(api_keys)
        
        self.interactive = interactive
        self.timeout = timeout
        self.clients = {}
        self.available_models = []
        
        self._validate_keys()
        self._initialize_clients()
        self._detect_available_models()

    def _validate_keys(self):
        for service in ['groq']:
            if not self.api_keys.get(service):
                if self.interactive:
                    try:
                        self.api_keys[service] = builtins.input(f"Enter {service.upper()} API key: ").strip()
                        if not self.api_keys[service]:
                            raise ValueError(f"{service.upper()} API key is required")
                    except (EOFError, OSError):
                        raise ValueError(f"{service.upper()} API key is required")
                else:
                    raise ValueError(f"{service.upper()} API key is required")

    def _initialize_clients(self):
        self.clients = {}
        if self.api_keys.get('groq'):
            try:
                self.clients['groq'] = Groq(api_key=self.api_keys['groq'])
            except Exception as e:
                warnings.warn(f"Could not initialize Groq client: {e}", ImportWarning)

    def _detect_available_models(self):
        self.available_models = []
        for provider, client in self.clients.items():
            if client and provider in self.DEFAULT_MODELS:
                self.available_models.extend(self.DEFAULT_MODELS[provider])

    def save_plot_to_image(self, plot_object: Union[plt.Figure, plt.Axes], output_path: str = "temp_plot.jpg"):
        """Save matplotlib plot to an image file"""
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.figure
        else:
            fig = plot_object
            
        fig.savefig(output_path, format='jpeg', dpi=100, bbox_inches='tight')
        return output_path

    def encode_image(self, image_path: str) -> str:
        """Encode image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _query_llama3(self, image_path: str, prompt: str) -> str:
        """Query Groq's Llama3 model with plot image"""
        if 'groq' not in self.clients:
            raise ValueError("Groq client not initialized")
        
        client = self.clients['groq']
        base64_image = self.encode_image(image_path)

        structured_prompt = f"""
        {prompt}
        
        Please structure your response with these clear sections:
        
        **Overview**:
        Provide a high-level description of what the visualization shows
        
        **Key Features**:
        - Describe the main visual elements
        - Note any important data points or ranges
        - Highlight how variables are represented
        
        **Insights and Patterns**:
        - Identify trends, clusters, or outliers
        - Note any interesting relationships between variables
        - Point out any surprising or notable observations
        
        **Conclusion**:
        - Summarize the main takeaways
        - Suggest any implications or next steps for analysis
        """

        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": structured_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            raise

    def refine_plot_explanation(
        self,
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        iterations: int = 2,
        temp_image_path: str = "temp_plot.jpg"
    ) -> str:
        """Generate and iteratively refine an explanation of a matplotlib/seaborn plot"""
        if not self.available_models:
            raise ValueError("No available models detected")

        # Save plot to temporary image file
        image_path = self.save_plot_to_image(plot_object, temp_image_path)
        
        try:
            # Generate initial explanation
            explanation = self._query_llama3(image_path, prompt)
            
            # Perform refinement iterations
            for _ in range(iterations - 1):
                critique_prompt = f"Critique this explanation: {explanation}"
                critique = self._query_llama3(image_path, critique_prompt)
                
                refinement_prompt = f"Improve this explanation based on the critique: {critique}\nOriginal explanation: {explanation}"
                explanation = self._query_llama3(image_path, refinement_prompt)
            
            return explanation
            
        finally:
            # Clean up temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)

# Package-level convenience function
_explainer_instance = None

def explainer6(
    plot_object: Union[plt.Figure, plt.Axes],
    prompt: str = "Explain this data visualization",
    iterations: int = 2,
    api_keys: dict = {},
    temp_image_path: str = "temp_plot.jpg"
) -> str:
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = PlotExplainer(api_keys)
    return _explainer_instance.refine_plot_explanation(
        plot_object=plot_object,
        prompt=prompt,
        iterations=iterations,
        temp_image_path=temp_image_path
    )

# # Example usage
# if __name__ == "__main__":
#     import numpy as np

#     x = np.linspace(0, 10, 100)
#     y = np.sin(x)

#     plt.figure(figsize=(10, 6))
#     plt.plot(x, y)
#     plt.title('Sine Wave Visualization')
#     plt.xlabel('X-axis')
#     plt.ylabel('Y-axis')

#     try:
#         result = explainer6(
#             plt.gca(), 
#             prompt="Explain the mathematical and visual characteristics of this sine wave",
#             api_keys={'groq': os.getenv('GROQ_API_KEY')}
#         )
        
#         print("Final Explanation:")
#         print(result)
#     except Exception as e:
#         print(f"Error generating explanation: {str(e)}")