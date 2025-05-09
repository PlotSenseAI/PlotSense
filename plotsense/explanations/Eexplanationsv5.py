import base64
import os
import matplotlib.pyplot as plt
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import warnings
import builtins
import requests
from io import BytesIO

load_dotenv()

class PlotExplainer:
    DEFAULT_MODELS = {
        'huggingface': [
                        'llava-hf/llava-1.5-7b-hf',  # Works with image inputs
                        'Salesforce/blip2-opt-2.7b',  # Works with image inputs],
                        # 'Qwen/Qwen2.5-VL-7B-Instruct', 
                        #             'allenai/Molmo-7B-D-0924'
        ] ,
                }
    
    def __init__(
        self, 
        api_keys: Optional[Dict[str, str]] = None, 
        max_iterations: int = 3,
        interactive: bool = True, 
        timeout: int = 30):

        # Default to empty dict if None
        api_keys = api_keys or {}

        # Set up default keys from environment variables
        self.api_keys = {
            'huggingface': os.getenv('HF_API_KEY')
        }
        self.api_keys.update(api_keys)
        
        self.interactive = interactive
        self.timeout = timeout
        self.clients = {}
        self.available_models = []
        self.max_iterations = max_iterations
        
        self._validate_keys()
        self._initialize_clients()
        self._detect_available_models()

    def _validate_keys(self):
        """Validate that required API keys are present"""
        for service in ['huggingface']:
            if not self.api_keys.get(service):
                if self.interactive:
                    try:
                        self.api_keys[service] = builtins.input(f"Enter {service.upper()} API key: ").strip()
                        if not self.api_keys[service]:
                            raise ValueError(f"{service.upper()} API key is required")
                    except (EOFError, OSError):
                        raise ValueError(f"{service.upper()} API key is required")
                else:
                    raise ValueError(f"{service.upper()} API key is required. Set it in the environment or pass it as an argument.")
                
    def _initialize_clients(self):
        """Initialize API clients"""
        self.clients = {}
        if self.api_keys.get('huggingface'):
            try:
                self.clients['huggingface'] = InferenceClient(api_key=self.api_keys['huggingface'])
            except Exception as e:
                warnings.warn(f"Could not initialize Hugging Face client: {e}", ImportWarning)

    def _detect_available_models(self):
        """Detect available models"""
        self.available_models = []
        for provider, client in self.clients.items():
            if client and provider in self.DEFAULT_MODELS:
                self.available_models.extend(self.DEFAULT_MODELS[provider])

    def refine_plot_explanation(
        self, 
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        custom_parameters: Optional[List[str]] = None
    ) -> str:
        """
        Generate an iteratively refined explanation using multiple models
        """

        if not self.available_models:
            raise ValueError("No available models detected")
        
        # Convert plot to base64
        img_bytes = self._plot_to_bytes(plot_object)
        
        # Iterative refinement process
        current_explanation = None
        
        for iteration in range(self.max_iterations):
            current_model = self.available_models[iteration % len(self.available_models)]
            
            if current_explanation is None:
                current_explanation = self._generate_initial_explanation(
                    current_model, img_bytes, prompt, custom_parameters
                )
            else:
                critique = self._generate_critique(
                    img_bytes, current_explanation, prompt, current_model, custom_parameters
                )
                
                current_explanation = self._generate_refinement(
                    img_bytes, current_explanation, critique, prompt, current_model, custom_parameters
                )

        return current_explanation
    
    def _plot_to_bytes(self, plot_object: Union[plt.Figure, plt.Axes]) -> bytes:
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.figure
        else:
            fig = plot_object

        fig.set_size_inches(8, 6)   
        buf = BytesIO()
        fig.savefig(buf, format='png',dpi=100, bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    
    def _query_model(self, img_bytes: bytes, prompt: str, model: str) -> str:
        if model in ['llava-hf/llava-1.5-7b-hf', 'Salesforce/blip2-opt-2.7b']:
            response = self._query_hf_model(img_bytes, prompt, model)
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        return response
        
    def _generate_initial_explanation(
        self, 
        model: str, 
        img_bytes: bytes,
        original_prompt: str, 
        metadata: Dict, 
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate initial plot explanation with structured format"""
        base_prompt = f"""
        Explanation Generation Requirements:
        - Provide a comprehensive analysis of the data visualization
        - Use a structured format with these sections:
        1. Overview
        2. Key Features
        3. Insights and Patterns
        4. Conclusion
        - Be specific and data-driven
        - Highlight key statistical and visual elements
        
        Specific Prompt: {original_prompt}

        Plot Metadata:
        {metadata}

        Formatting Instructions:
        - Use markdown-style headers
        - Include bullet points for clarity
        - Provide quantitative insights
        - Explain the significance of visual elements
        """
        
        return self._query_model(
            model, 
            base_prompt, 
            img_bytes, 
            custom_parameters
        )

    def _generate_critique(
        self, 
        img_bytes: bytes, 
        current_explanation: str, 
        original_prompt: str, 
        model: str,
        metadata: Dict, 
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate critique of current explanation"""
        critique_prompt = f"""
        Explanation Critique Guidelines:

        Current Explanation:
        {current_explanation}

        Evaluation Criteria:
        1. Assess the completeness of each section
        - Overview: Clarity and conciseness of plot description
        - Key Features: Depth of visual and statistical analysis
        - Insights and Patterns: Identification of meaningful trends
        - Conclusion: Relevance and forward-looking perspective

        2. Identify areas for improvement:
        - Are there missing key observations?
        - Is the language precise and data-driven?
        - Are statistical insights thoroughly explained?
        - Do the insights connect logically?

        3. Suggest specific enhancements:
        - Add more quantitative details
        - Clarify any ambiguous statements
        - Provide deeper context
        - Ensure comprehensive coverage of plot elements

        Plot Metadata for Context:
        {metadata}

        Provide a constructive critique that will help refine the explanation.
        """
        
        return self._query_model(
            model, 
            critique_prompt, 
            img_bytes, 
            custom_parameters
        )

    def _generate_refinement(
        self, 
        img_bytes: bytes, 
        current_explanation: str, 
        critique: str, 
        original_prompt: str, 
        model: str,
        metadata: Dict, 
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate refined explanation based on critique"""
        refinement_prompt = f"""
        Explanation Refinement Instructions:

        Original Explanation:
        {current_explanation}

        Critique Received:
        {critique}

        Refinement Guidelines:
        1. Address all points in the critique
        2. Maintain the original structured format
        3. Enhance depth and precision of analysis
        4. Add more quantitative insights
        5. Improve clarity and readability

        Specific Refinement Objectives:
        - Elaborate on key statistical observations
        - Provide more context for insights
        - Ensure each section is comprehensive
        - Use precise, data-driven language
        - Connect insights logically

        Plot Metadata for Additional Context:
        {metadata}

        Produce a refined explanation that elevates the original analysis.
        """
        
        return self._query_model(
            model, 
            refinement_prompt, 
            img_bytes, 
            custom_parameters
        )
    
    def _query_model(
        self, 
        model: str, 
        prompt: str, 
        plot_image: str,
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """
        Generic model querying method with provider-specific logic
        """
        # Determine provider based on model name
        provider = next(
            (p for p, models in self.DEFAULT_MODELS.items() if model in models), 
            None
        )
        
        if not provider:
            raise ValueError(f"No provider found for model {model}")
        
        try:
            if provider == 'huggingface':
                client = InferenceClient(model=model, token=self.api_keys['huggingface'])
                
                # Merge default and custom parameters
                default_params = {
                    'max_tokens': 1000,
                }
                generation_params = {**default_params, **(custom_parameters or {})}
                
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{plot_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    **generation_params
                )
                
                return response.choices[0].message.content
            
        except Exception as e:
            error_message = f"Model querying error for {model}: {str(e)}"
            warnings.warn(error_message)
            return error_message

_explainer_instance = None

def explainer(
    plot_object: Union[plt.Figure, plt.Axes], 
    prompt: str = "Explain this data visualization",
    api_keys: Optional[Dict[str, str]] = None,
    max_iterations: int = 3,
    custom_parameters: Optional[Dict] = None
) -> str:
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = PlotExplainer(api_keys=api_keys, max_iterations=max_iterations)
    return _explainer_instance.refine_plot_explanation(
        plot_object=plot_object,
        prompt=prompt,
        custom_parameters=custom_parameters or {}
    )

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title('Sine Wave Visualization')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    try:
        result = explainer(
            plt.gca(), 
            prompt="Explain the mathematical and visual characteristics of this sine wave",
            api_keys={'huggingface': os.getenv('HF_API_KEY')}  
        )
        
        print("Final Explanation:")
        print(result)  
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")