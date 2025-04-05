"""
plot_explainer/__init__.py
A package for generating AI-enhanced explanations of matplotlib/seaborn plots
"""

import base64
from io import BytesIO
import matplotlib.pyplot as plt
from typing import Union
import warnings

# Try importing optional dependencies
#try:
    #from openai import OpenAI
#except ImportError:
    #warnings.warn("OpenAI package not installed. GPT-4 will be unavailable.")

class PlotExplainer:
    def __init__(self, api_keys: dict = {}):
        """
        Initialize explainer with optional API keys
        
        Args:
            api_keys: Dictionary of API keys (openai, anthropic, etc.)
        """
        self._init_apis(api_keys)
        self.available_models = self._detect_available_models()
        
    def _init_apis(self, api_keys):
        """Initialize API clients"""
        self.clients = {
            'groq': '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'
            # Add other API clients here
        }
    
    def _detect_available_models(self):
        """Detect which models are available based on installed packages"""
        available = []
        if self.clients['groq']:
            available.extend(['llama3-70b-8192', 'qwen-2.5-32b'])
        # Add checks for other models
        return available
    
    def refine_plot_explanation(
        self, 
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        iterations: int = 2,
        model_rotation: list = None
    ) -> str:
        """
        Generate and iteratively refine an explanation of a matplotlib/seaborn plot
        
        Args:
            plot_object: Matplotlib Figure or Axes object
            prompt: Initial explanation prompt
            iterations: Number of refinement cycles
            model_rotation: Optional list of models to use (default: auto-select)
            
        Returns:
            str: Refined explanation text
        """
        # Convert plot to image
        img_bytes = self._plot_to_bytes(plot_object)
        
        # Set up model rotation
        models = model_rotation or self._select_model_rotation()
        
        # Generate initial explanation
        explanation = self._generate_explanation(img_bytes, prompt, models[0])
        
        # Iterative refinement
        for i in range(iterations):
            critic = models[i % len(models)]
            refiner = models[(i + 1) % len(models)]
            
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
            
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()
    
    def _select_model_rotation(self):
        """Select models to use based on availability"""
        priority_order = [
            'llama3-70b-8192', 'qwen-2.5-32b'
        ]
        return [m for m in priority_order if m in self.available_models]
    
    def _generate_explanation(self, img_bytes: bytes, prompt: str, model: str) -> str:
        """Generate initial explanation"""
        if model == 'llama3-70b-8192':
            return self._query_llama3(img_bytes, prompt)
        # Add other model handlers here
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _generate_critique(self, img_bytes: bytes, explanation: str, prompt: str, model: str) -> str:
        """Generate critique of current explanation"""
        critique_prompt = f"""
        Critique this plot explanation:
        
        Original Prompt: {prompt}
        Current Explanation: {explanation}
        
        Provide specific feedback on:
        1. Data interpretation accuracy
        2. Clarity of key insights
        3. Missing important patterns
        4. Technical correctness
        """
        return self._query_model(img_bytes, critique_prompt, model)
    
    def _generate_refinement(self, img_bytes: bytes, explanation: str, critique: str, prompt: str, model: str) -> str:
        """Generate refined explanation"""
        refinement_prompt = f"""
        Improve this plot explanation based on the critique:
        
        Original Prompt: {prompt}
        Current Explanation: {explanation}
        Critique: {critique}
        
        Create an improved version that addresses the feedback while
        maintaining all accurate information.
        """
        return self._query_model(img_bytes, refinement_prompt, model)
    
    def _query_llama3(self, img_bytes: bytes, prompt: str) -> str:
        """Query GPT-4 Vision with plot image"""
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        response = self.clients['groq'].chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content
    
    # Add similar methods for other models (Claude, Gemini, etc.)

# Package-level convenience function
_explainer_instance = None

def refine_plot_explanation(
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