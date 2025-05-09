import base64
import os
from io import BytesIO
import matplotlib.pyplot as plt
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv
import requests
import warnings
import builtins

load_dotenv()

class PlotExplainer:
    DEFAULT_MODELS = {
        'huggingface': [
            'Salesforce/blip-image-captioning-large',  # Image-to-text
            'mistralai/Mixtral-8x7B-Instruct-v0.1',  # Text-to-text
            'google/gemma-7b-it'  # Alternative text-to-text
        ],
    }
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None, interactive: bool = True, timeout: int = 30):
        """
        Initialize PlotExplainer with API keys and configuration.
        
        Args:
            api_keys: Optional dictionary of API keys. If not provided,
                     keys will be loaded from environment variables.
            interactive: Whether to prompt for missing keys interactively
            timeout: Timeout in seconds for API requests
        """
        # Default to empty dict if None
        api_keys = api_keys or {}

        # Set up default keys from environment variables
        self.api_keys = {
            'huggingface': os.getenv('HF_API_KEY')
        }
        self.api_keys.update(api_keys)
    
        self.interactive = interactive
        self.timeout = timeout
        self.available_models = []
        
        self._validate_keys()
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
                        # Handle cases where input is not available
                        raise ValueError(f"{service.upper()} API key is required")
                else:
                    raise ValueError(f"{service.upper()} API key is required. Set it in the environment or pass it as an argument.")

    def _detect_available_models(self):
        """Detect available models - for now we'll assume all DEFAULT_MODELS are available"""
        self.available_models = []
        if self.api_keys.get('huggingface'):
            self.available_models.extend(self.DEFAULT_MODELS['huggingface'])
    
    def refine_plot_explanation(
        self, 
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        iterations: int = 2,
        model_rotation: Optional[List[str]] = None
    ) -> str:
        """
        Generate and iteratively refine an explanation of a matplotlib/seaborn plot
        
        Args:
            plot_object: Matplotlib Figure or Axes object
            prompt: Initial explanation prompt
            iterations: Number of refinement cycles (1-5)
            model_rotation: Optional list of models to use (default: auto-select)
            
        Returns:
            str: Refined explanation text
            
        Raises:
            ValueError: If no models are available or invalid parameters provided
        """
        if not self.available_models:
            raise ValueError("No available models detected")
        
        if iterations < 1 or iterations > 5:
            raise ValueError("Iterations must be between 1 and 5")
        
        img_bytes = self._plot_to_bytes(plot_object)
        models = model_rotation or self._select_model_rotation()
        
        # Start with image captioning model for initial explanation
        explanation = self._generate_explanation(img_bytes, prompt, models[0])
        
        # Use text models for refinement iterations
        text_models = [m for m in models if m not in ['Salesforce/blip-image-captioning-large']]
        if not text_models:
            text_models = models  # Fallback to all models if no text-specific models found
        
        for i in range(iterations - 1):
            critic = text_models[i % len(text_models)]
            refiner = text_models[(i + 1) % len(text_models)]
            
            critique = self._generate_critique(
                img_bytes, explanation, prompt, critic
            )
            
            explanation = self._generate_refinement(
                img_bytes, explanation, critique, prompt, refiner
            )
        
        return explanation
    
    def _plot_to_bytes(self, plot_object: Union[plt.Figure, plt.Axes]) -> bytes:
        """Convert matplotlib plot to bytes"""
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.figure
        else:
            fig = plot_object

        # Standardize image generation
        fig.set_size_inches(8, 6)   
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()
    
    def _select_model_rotation(self):
        """Select models to use based on availability"""
        priority_order = [
            'Salesforce/blip-image-captioning-large',  # Best for initial image description
            'mistralai/Mixtral-8x7B-Instruct-v0.1',  # Strong for text refinement
            'google/gemma-7b-it'  # Alternative for refinement
        ]
        return [m for m in priority_order if m in self.available_models]
    
    def _query_model(self, img_bytes: bytes, prompt: str, model: str) -> str:
        """Generic method to query different models"""
        if model == 'Salesforce/blip-image-captioning-large':
            return self._query_image_to_text(img_bytes, prompt, model)
        else:
            return self._query_text_model(prompt, model)
        
    def _generate_explanation(self, img_bytes: bytes, prompt: str, model: str) -> str:
        """Generate initial explanation"""
        return self._query_model(img_bytes, prompt, model)
    
    def _generate_critique(self, img_bytes: bytes, explanation: str, prompt: str, model: str) -> str:
        """Generate critique of current explanation"""
        critique_prompt = f"""
        Critique this plot explanation based on the required structure:
        
        Original Prompt: {prompt}
        Current Explanation: {explanation}

        Evaluate whether the explanation contains all required sections:
        1. Overview
        2. Key Features
        3. Insights and Patterns
        4. Conclusion
            
        For each section, provide specific feedback on:
        - Completeness of information
        - Accuracy of observations
        - Clarity of presentation
        - Depth of analysis
        
        Also note any:
        - Missing important patterns
        - Technical inaccuracies
        - Unclear statements

        Be concise but thorough in your critique.
        
        Provide your critique in a bullet-point format.
        """
        return self._query_text_model(critique_prompt, model)
    
    def _generate_refinement(self, img_bytes: bytes, explanation: str, critique: str, prompt: str, model: str) -> str:
        """Generate refined explanation"""
        refinement_prompt = f"""
        Improve this plot explanation based on the critique while maintaining the required structure:
        
        Original Prompt: {prompt}
        Current Explanation: {explanation}
        Critique: {critique}
        
        Create an improved version that maintains these clear sections:
        - Overview
        - Key Features
        - Insights and Patterns
        - Conclusion
        
        Specifically:
        1. Address all valid critique points
        2. Ensure each section is well-developed
        3. Maintain accurate information
        4. Improve clarity and insightfulness
        5. Keep technical correctness
        
        Return the improved explanation with the same section headers.
        """
        return self._query_text_model(refinement_prompt, model)
    
    def _query_image_to_text(self, img_bytes: bytes, prompt: str, model: str) -> str:
        """Query Hugging Face image-to-text model with plot image"""
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_keys['huggingface']}",
            "Content-Type": "application/json"
        }
        
        # Convert image to base64
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        
        # Structured prompt template
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
        
        Keep the response clear, concise, and focused on the data.
        """
        
        payload = {
            "inputs": {
                "image": base64_image,
                "text": structured_prompt
            }
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'No explanation generated')
            elif isinstance(result, dict):
                return result.get('generated_text', 'No explanation generated')
            return str(result)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            raise
    
    def _query_text_model(self, prompt: str, model: str) -> str:
        """Query Hugging Face text generation model"""
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_keys['huggingface']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list):
                if len(result) > 0 and isinstance(result[0], dict):
                    return result[0].get('generated_text', 'No response generated')
                return str(result[0]) if len(result) > 0 else 'No response generated'
            elif isinstance(result, dict):
                return result.get('generated_text', 'No response generated')
            return str(result)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            raise

# Package-level convenience function
_explainer_instance = None

def explainer4(
    plot_object: Union[plt.Figure, plt.Axes],
    prompt: str = "Explain this data visualization",
    iterations: int = 2,
    api_keys: dict = {}
) -> str:
    """
    Generate an AI-refined explanation of a matplotlib/seaborn plot
    
    Args:
        plot_object: Matplotlib Figure or Axes object
        prompt: Explanation prompt (default generic)
        iterations: Refinement cycles (default 2)
        api_keys: Dictionary of API keys
        
    Returns:
        str: Refined explanation text
    """
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = PlotExplainer(api_keys)
    return _explainer_instance.refine_plot_explanation(
        plot_object=plot_object,
        prompt=prompt,
        iterations=iterations
    )


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Create a sample plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title('Sine Wave Visualization')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    try:
        # Get iteratively refined explanation
        result = explainer4(
            plt.gca(), 
            prompt="Explain the mathematical and visual characteristics of this sine wave",
            api_keys={'huggingface': os.getenv('HF_API_KEY')}  # Get from environment
        )
        
        print("Final Explanation:")
        print(result)
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")