import base64
import os
import matplotlib.pyplot as plt
from typing import Union, Optional, Dict, List
from dotenv import load_dotenv
from groq import Groq
import warnings
import builtins
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class PlotExplainer:
    """
    A class to generate and refine explanations for plots using LLMs."""    
    DEFAULT_MODELS = {
        'groq': ['meta-llama/llama-4-scout-17b-16e-instruct',
                  'meta-llama/llama-4-maverick-17b-128e-instruct'],
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

        ## Initialize API keys with environment variable or provided keys
        self.api_keys = {
            'groq': os.getenv('GROQ_API_KEY')
        }
        # Update with provided API keys
        self.api_keys.update(api_keys)
        # Set interactive mode and timeout for API calls
        self.interactive = interactive
        # Set timeout for API calls
        self.timeout = timeout
        # Initialize empty dict for clients
        self.clients = {}
        # Initialize empty list for available models
        self.available_models = []
        # Set max iterations for refinement
        self.max_iterations = max_iterations

        # Validate API keys and initialize clients
        self._validate_keys()
        # Initialize clients
        self._initialize_clients()
        # Detect available models
        self._detect_available_models()

    def _validate_keys(self):
        """Validate API keys and prompt for input if not provided"""
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
        """Initialize API clients based on provided API keys"""
        self.clients = {}
        if self.api_keys.get('groq'):
            try:
                self.clients['groq'] = Groq(api_key=self.api_keys['groq'])
            except Exception as e:
                warnings.warn(f"Could not initialize Groq client: {e}", ImportWarning)

    def _detect_available_models(self):
        """Detect available models based on initialized clients"""
        self.available_models = []
        for provider, client in self.clients.items():
            if client and provider in self.DEFAULT_MODELS:
                self.available_models.extend(self.DEFAULT_MODELS[provider])

    def save_plot_to_image(
            self, 
            plot_object: Union[plt.Figure, plt.Axes], 
            output_path: str = "temp_plot.jpg"
    ):
        """Save plot to an image file"""
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.figure
        else:
            fig = plot_object
            
        fig.savefig(output_path, format='jpeg', dpi=100, bbox_inches='tight')
        return output_path

    def encode_image(
            self, 
            image_path: str
    ) -> str:
        """Encode image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # @retry(
    #     stop=stop_after_attempt(3),  # Try 3 times
    #     wait=wait_exponential(multiplier=1, min=4, max=10),  # Wait between attempts
    #     reraise=True
    # )
    def _query_model(
            self,
            model: str,
            prompt: str,
            image_path: str, 
            custom_parameters: Optional[Dict] = None
    ) -> str:
        
        """Generic model querying method with provider-specific logic"""
        
        base64_image = self.encode_image(image_path)

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
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    **generation_params
                )
                
                return response.choices[0].message.content
            
        except Exception as e:
            if "503" in str(e):
                print(f"Groq service temporarily unavailable, retrying... Error: {e}")
                raise  # This will trigger retry
            error_message = f"Model querying error for {model}: {str(e)}"
            warnings.warn(error_message)
            return error_message

    def refine_plot_explanation(
        self,
        plot_object: Union[plt.Figure, plt.Axes],
        prompt: str = "Explain this data visualization",
        temp_image_path: str = "temp_plot.jpg",
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate and iteratively refine an explanation of a matplotlib/seaborn plot"""
        if not self.available_models:
            raise ValueError("No available models detected")

        # Save plot to temporary image file
        image_path = self.save_plot_to_image(plot_object, temp_image_path)
        
        try:
            # Iterative refinement process
            current_explanation = None
            
            for iteration in range(self.max_iterations):
                current_model = self.available_models[iteration % len(self.available_models)]
                
                if current_explanation is None:
                    current_explanation = self._generate_initial_explanation(
                        current_model, image_path, prompt, custom_parameters
                    )
                else:
                    critique = self._generate_critique(
                        image_path, current_explanation, prompt, current_model, custom_parameters
                    )
                    
                    current_explanation = self._generate_refinement(
                        image_path, current_explanation, critique, prompt, current_model, custom_parameters
                    )

            return current_explanation
            
        finally:
            # Clean up temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)

    def _generate_initial_explanation(
        self, 
        model: str, 
        image_path: str,
        original_prompt: str, 
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

        Formatting Instructions:
        - Use markdown-style headers
        - Include bullet points for clarity
        - Provide quantitative insights
        - Explain the significance of visual elements
        """
        
        return self._query_model(
            model=model, 
            prompt=base_prompt,
            image_path=image_path, 
            custom_parameters=custom_parameters
        )

    def _generate_critique(
        self, 
        image_path: str, 
        current_explanation: str, 
        original_prompt: str, 
        model: str,
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate critique of current explanation"""
        critique_prompt = f"""
        Explanation Critique Guidelines:

        Current Explanation:
        {current_explanation}

        Original Prompt:
        {original_prompt}

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

        Provide a constructive critique that will help refine the explanation.
        """
        
        return self._query_model(
            model=model, 
            prompt=critique_prompt, 
            image_path=image_path, 
            custom_parameters=custom_parameters
        )

    def _generate_refinement(
        self, 
        image_path: str,
        current_explanation: str, 
        critique: str, 
        original_prompt: str, 
        model: str,
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate refined explanation based on critique"""
        refinement_prompt = f"""
        Explanation Refinement Instructions:

        Original Explanation:
        {current_explanation}

        Critique Received:
        {critique}

        original Prompt:
        {original_prompt}

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

        Produce a refined explanation that elevates the original analysis.
        - Be concise but thorough in your critique.
        - Use markdown-style headers for clarity
        - Include bullet points for clarity
        - Provide quantitative insights
        - Ensure the explanation is comprehensive and insightful    

        """
        
        return self._query_model(
            model=model,
            prompt= refinement_prompt, 
            image_path=image_path,
            custom_parameters= custom_parameters
        )

# Package-level convenience function
_explainer_instance = None

def explainer(
    plot_object: Union[plt.Figure, plt.Axes],
    prompt: str = "Explain this data visualization",
    api_keys: Optional[Dict[str, str]] = None,
    max_iterations: int = 3,
    custom_parameters: Optional[Dict] = None,
    temp_image_path: str = "temp_plot.jpg"
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

    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = PlotExplainer(api_keys=api_keys, 
                                            max_iterations=max_iterations)
    return _explainer_instance.refine_plot_explanation(
        plot_object=plot_object,
        prompt=prompt,
        custom_parameters=custom_parameters,
        temp_image_path=temp_image_path
    )
