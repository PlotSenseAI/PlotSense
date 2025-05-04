import base64
import os
import re
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from typing import Union, Optional, Dict, List, Any
from dotenv import load_dotenv
from groq import Groq
import warnings
import builtins

load_dotenv()

class IterativeRefinementExplainer:
    DEFAULT_MODELS = {
        'groq': [
            'meta-llama/llama-4-scout-17b-16e-instruct', 
            'meta-llama/llama-4-maverick-17b-128e-instruct',
          
        ]
    }

    def __init__(
        self, 
        api_keys: Optional[Dict[str, str]] = None, 
        max_iterations: int = 3,
        interactive: bool = True, 
        timeout: int = 30
    ):
        # Default to empty dict if None
        api_keys = api_keys or {}

        # Set up default keys from environment variables
        self.api_keys = {
            'groq': os.getenv('GROQ_API_KEY')
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
                    raise ValueError(f"{service.upper()} API key is required. Set it in the environment or pass it as an argument.")

    def _initialize_clients(self):
        """Initialize API clients"""
        self.clients = {}
        if self.api_keys.get('groq'):
            try:
                self.clients['groq'] = Groq(api_key=self.api_keys['groq'])
            except Exception as e:
                warnings.warn(f"Could not initialize Groq client: {e}", ImportWarning)

    def _detect_available_models(self):
        """Detect available models"""
        self.available_models = []
        for provider, client in self.clients.items():
            if client and provider in self.DEFAULT_MODELS:
                self.available_models.extend(self.DEFAULT_MODELS[provider])

    def iterative_plot_explanation(
        self, 
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """
        Generate an iteratively refined explanation using multiple models
        """
        # Validate models availability
        if not self.available_models:
            raise ValueError("No available models for explanation generation")

        # Convert plot to base64
        img_bytes = self._convert_plot_to_base64(plot_object)
        
        # Metadata extraction
        metadata = self._extract_plot_metadata(plot_object)

        # Iterative refinement process
        current_explanation = None
        
        # Rotate through available models
        for iteration in range(self.max_iterations):
            # Select model for this iteration
            current_model = self.available_models[iteration % len(self.available_models)]
            
            # Generate or refine explanation
            if current_explanation is None:
                # Initial explanation generation
                current_explanation = self._generate_initial_explanation(
                    current_model, img_bytes, prompt, metadata, custom_parameters
                )
            else:
                # Generate critique
                critique = self._generate_critique(
                    img_bytes, current_explanation, prompt, current_model, metadata, custom_parameters
                )
                
                # Generate refinement based on critique
                current_explanation = self._generate_refinement(
                    img_bytes, current_explanation, critique, prompt, current_model, metadata, custom_parameters
                )

        return current_explanation
    
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
            if provider == 'groq':
                client = self.clients['groq']
                
                # Merge default and custom parameters
                default_params = {
                    'max_tokens': 1000,
                    'temperature': 0.7
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

    def _convert_plot_to_base64(self, plot_object: Union[plt.Figure, plt.Axes]) -> str:
        """Convert matplotlib plot to base64"""
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.figure
        else:
            fig = plot_object

        # Standardize image generation
        fig.set_size_inches(8, 6)   
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _extract_plot_metadata(self, plot_object: Union[plt.Figure, plt.Axes]) -> Dict[str, Any]:
        """Extract comprehensive metadata about the plot"""
        metadata = {
            'data_dimensions': self._get_data_dimensions(plot_object),
            'statistical_summary': self._compute_statistical_summary(plot_object)
        }
        return metadata

    def _get_data_dimensions(self, plot_object: Union[plt.Figure, plt.Axes]) -> Dict:
        """Extract data dimensions and characteristics"""
        try:
            if isinstance(plot_object, plt.Axes):
                for line in plot_object.get_lines():
                    data = line.get_data()
                    return {
                        'x_points': len(data[0]),
                        'y_points': len(data[1]),
                        'x_range': (min(data[0]), max(data[0])),
                        'y_range': (min(data[1]), max(data[1]))
                    }
        except Exception as e:
            warnings.warn(f"Error extracting data dimensions: {e}")
        return {}

    def _compute_statistical_summary(self, plot_object: Union[plt.Figure, plt.Axes]) -> Dict:
        """Compute statistical summary of plot data"""
        try:
            if isinstance(plot_object, plt.Axes):
                data = [line.get_data()[1] for line in plot_object.get_lines()]
                flattened_data = [item for sublist in data for item in sublist]
                
                return {
                    'mean': np.mean(flattened_data),
                    'median': np.median(flattened_data),
                    'std_dev': np.std(flattened_data),
                    'min': np.min(flattened_data),
                    'max': np.max(flattened_data)
                }
        except Exception as e:
            warnings.warn(f"Error computing statistical summary: {e}")
        return {}

# Convenience function
def explainer2(
    plot_object: Union[plt.Figure, plt.Axes], 
    prompt: str = "Explain this data visualization",
    api_keys: Optional[Dict[str, str]] = None,
    max_iterations: int = 3,
    custom_parameters: Optional[Dict] = None
) -> str:
    """
    Convenience function for iterative plot explanation
    
    Args:
        data: Original data used to create the plot (DataFrame or numpy array)
        plot_object: Matplotlib Figure or Axes
        prompt: Explanation prompt
        api_keys: API keys for different providers
        max_iterations: Maximum refinement iterations
        custom_parameters: Additional generation parameters
    
    Returns:
        Comprehensive explanation with refinement details
    """
    explainer = IterativeRefinementExplainer(
        api_keys=api_keys, 
        max_iterations=max_iterations
    )
    
    return explainer.iterative_plot_explanation(
        plot_object, 
        prompt, 
        custom_parameters
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
        result = explainer2(
            plt.gca(), 
            prompt="Explain the mathematical and visual characteristics of this sine wave",
            api_keys={'groq': os.getenv('GROQ_API_KEY')}
        )
        
        print("Final Explanation:")
        print(result)
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")