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
import cv2

load_dotenv()

class OpenCVPlotAnalyzer:
    def __init__(self):
        # Initialize OpenCV-specific parameters
        self.feature_params = {
            'edge_threshold1': 50,
            'edge_threshold2': 150,
            'contour_threshold': 128,
            'text_region_min_area': 100,
            'dominant_colors': 3
        }
    
    def analyze_plot(self, image: Union[str, np.ndarray]) -> Dict:
        """
        Analyze a plot image using OpenCV computer vision techniques.
        
        Args:
            image: Either a file path string or numpy array of the image
            
        Returns:
            Dictionary containing comprehensive visual analysis
        """
        # Load image (either from file path or numpy array)
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image.copy()
        
        if img is None:
            raise ValueError("Could not load image")
            
        # Convert to grayscale for many operations
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection - helps identify lines and transitions
        edges = cv2.Canny(gray, 
                         self.feature_params['edge_threshold1'],
                         self.feature_params['edge_threshold2'])
        
        # Find contours - helps identify distinct visual elements
        _, thresh = cv2.threshold(gray, 
                                 self.feature_params['contour_threshold'], 
                                 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Comprehensive visual analysis
        analysis = {
            'edges': edges,
            'contour_count': len(contours),
            'dominant_colors': self._get_dominant_colors(img),
            'text_elements': self._detect_text(img),
            'shape_analysis': self._analyze_shapes(contours),
            'histogram': self._compute_color_histogram(img),
            'brightness': self._compute_brightness(gray)
        }
        
        return analysis
    
    def _get_dominant_colors(self, img: np.ndarray) -> List:
        """Extract dominant colors using k-means clustering"""
        pixels = img.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(
            pixels, 
            self.feature_params['dominant_colors'], 
            None, 
            criteria, 
            10, 
            cv2.KMEANS_RANDOM_CENTERS
        )
        return centers.astype(int).tolist()
    
    def _detect_text(self, img: np.ndarray) -> Dict:
        """Detect text elements in the image using contour analysis"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > self.feature_params['text_region_min_area']:
                text_regions.append({
                    'position': {'x': x, 'y': y},
                    'dimensions': {'width': w, 'height': h},
                    'area': w * h
                })
        
        return {
            'count': len(text_regions), 
            'regions': text_regions,
            'density': len(text_regions) / (img.shape[0] * img.shape[1]) if img.size > 0 else 0
        }
    
    def _analyze_shapes(self, contours: List) -> Dict:
        """Analyze geometric shapes in the image"""
        shape_features = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
            vertices = len(approx)
            
            shape_features.append({
                'area': area,
                'perimeter': perimeter,
                'aspect_ratio': self._compute_aspect_ratio(cnt),
                'vertices': vertices,
                'shape_type': self._classify_shape(vertices, area)
            })
        
        return {
            'count': len(shape_features),
            'shapes': shape_features,
            'shape_distribution': self._compute_shape_distribution(shape_features)
        }
    
    def _compute_aspect_ratio(self, contour) -> float:
        """Compute aspect ratio of bounding rectangle"""
        _, _, w, h = cv2.boundingRect(contour)
        return w / h if h != 0 else 0
    
    def _classify_shape(self, vertices: int, area: float) -> str:
        """Classify shape based on vertex count"""
        if vertices == 3: return "triangle"
        elif vertices == 4: 
            return "rectangle" if area > 100 else "small_rectangle"
        elif vertices > 4: return "polygon"
        return "unknown"
    
    def _compute_shape_distribution(self, shapes: List) -> Dict:
        """Compute distribution of shape types"""
        counts = {}
        for shape in shapes:
            counts[shape['shape_type']] = counts.get(shape['shape_type'], 0) + 1
        return counts
    
    def _compute_color_histogram(self, img: np.ndarray) -> Dict:
        """Compute color histogram for the image"""
        colors = ('b', 'g', 'r')
        hist_data = {}
        for i, color in enumerate(colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            hist_data[color] = hist.flatten().tolist()
        return hist_data
    
    def _compute_brightness(self, gray_img: np.ndarray) -> float:
        """Compute average brightness of the image"""
        return np.mean(gray_img)

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
        # Initialize with default or provided API keys
        api_keys = api_keys or {}
        self.api_keys = {
            'groq': os.getenv('GROQ_API_KEY')
        }
        self.api_keys.update(api_keys)
    
        self.interactive = interactive
        self.timeout = timeout
        self.clients = {}
        self.available_models = []
        self.max_iterations = max_iterations
        self.cv_analyzer = OpenCVPlotAnalyzer()
        
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
                    raise ValueError(f"{service.upper()} API key is required")

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
        with enhanced OpenCV visual analysis.
        """
        if not self.available_models:
            raise ValueError("No available models for explanation generation")

        # Convert plot to base64 for LLM and to numpy array for OpenCV
        img_bytes = self._convert_plot_to_base64(plot_object)
        img_array = self._convert_plot_to_array(plot_object)
        
        # Enhanced metadata extraction with OpenCV
        metadata = self._extract_plot_metadata(plot_object, img_array)
        
        # Iterative refinement process
        current_explanation = None
        
        for iteration in range(self.max_iterations):
            current_model = self.available_models[iteration % len(self.available_models)]
            
            if current_explanation is None:
                current_explanation = self._generate_initial_explanation(
                    current_model, img_bytes, prompt, metadata, custom_parameters
                )
            else:
                critique = self._generate_critique(
                    img_bytes, current_explanation, prompt, current_model, metadata, custom_parameters
                )
                
                current_explanation = self._generate_refinement(
                    img_bytes, current_explanation, critique, prompt, current_model, metadata, custom_parameters
                )

        return current_explanation
    
    # def _generate_initial_explanation(
    #     self, 
    #     model: str, 
    #     img_bytes: bytes,
    #     original_prompt: str, 
    #     metadata: Dict, 
    #     custom_parameters: Optional[Dict] = None
    # ) -> str:
    #     """Generate initial plot explanation with structured format"""
    #     base_prompt = f"""
    #     Explanation Generation Requirements:
    #     - Provide a comprehensive analysis of the data visualization
    #     - Use a structured format with these sections:
    #     1. Overview
    #     2. Key Visual Features
    #     3. Data Patterns
    #     4. Color Analysis
    #     5. Text Elements
    #     6. Conclusion
        
    #     Specific Prompt: {original_prompt}

    #     Plot Metadata:
    #     {json.dumps(metadata, indent=2)}

    #     OpenCV Analysis:
    #     {self._format_opencv_analysis(metadata['visual_features'])}

    #     Formatting Instructions:
    #     - Use markdown-style headers
    #     - Include quantitative insights from the visual analysis
    #     - Reference specific visual elements found
    #     """
        
    #     return self._query_model(
    #         model, 
    #         base_prompt, 
    #         img_bytes, 
    #         custom_parameters
    #     )

    def _format_opencv_analysis(self, analysis: Dict) -> str:
        """Format OpenCV analysis results for LLM consumption, ensuring JSON serialization"""
        # Convert numpy arrays and other non-serializable objects
        serializable_analysis = {
            'dominant_colors': [list(map(int, color)) for color in analysis['dominant_colors']],
            'text_elements': {
                'count': analysis['text_elements']['count'],
                'regions': analysis['text_elements']['regions'],
                'density': float(analysis['text_elements']['density'])
            },
            'shape_analysis': {
                'count': analysis['shape_analysis']['count'],
                'shapes': [{
                    'area': float(shape['area']),
                    'perimeter': float(shape['perimeter']),
                    'aspect_ratio': float(shape['aspect_ratio']),
                    'vertices': shape['vertices'],
                    'shape_type': shape['shape_type']
                } for shape in analysis['shape_analysis']['shapes']],
                'shape_distribution': analysis['shape_analysis']['shape_distribution']
            },
            'brightness': float(analysis['brightness'])
        }
        
        text = "Visual Analysis Results:\n"
        text += f"- Dominant Colors: {serializable_analysis['dominant_colors']}\n"
        text += f"- Text Elements: {serializable_analysis['text_elements']['count']} regions\n"
        text += f"- Shape Analysis: Found {serializable_analysis['shape_analysis']['count']} shapes\n"
        text += f"  - Types: {', '.join(serializable_analysis['shape_analysis']['shape_distribution'].keys())}\n"
        text += f"- Brightness: {serializable_analysis['brightness']:.1f} (0-255 scale)\n"
        return text

    def _generate_initial_explanation(
        self, 
        model: str, 
        img_bytes: bytes,
        original_prompt: str, 
        metadata: Dict, 
        custom_parameters: Optional[Dict] = None
    ) -> str:
        """Generate initial plot explanation with structured format"""
        # Create a serializable version of metadata
        serializable_metadata = {
            'data_dimensions': metadata['data_dimensions'],
            'statistical_summary': metadata['statistical_summary'],
            'visual_features': {
                'dominant_colors': [list(map(int, color)) for color in metadata['visual_features']['dominant_colors']],
                'text_elements': {
                    'count': metadata['visual_features']['text_elements']['count'],
                    'regions': metadata['visual_features']['text_elements']['regions'],
                    'density': float(metadata['visual_features']['text_elements']['density'])
                },
                'shape_analysis': {
                    'count': metadata['visual_features']['shape_analysis']['count'],
                    'shape_distribution': metadata['visual_features']['shape_analysis']['shape_distribution']
                },
                'brightness': float(metadata['visual_features']['brightness'])
            }
        }
        
        base_prompt = f"""
        Explanation Generation Requirements:
        - Provide a comprehensive analysis of the data visualization
        - Use a structured format with these sections:
        1. Overview
        2. Key Visual Features
        3. Data Patterns
        4. Color Analysis
        5. Text Elements
        6. Conclusion
        
        Specific Prompt: {original_prompt}

        Plot Metadata:
        {json.dumps(serializable_metadata, indent=2)}

        OpenCV Analysis:
        {self._format_opencv_analysis(metadata['visual_features'])}

        Formatting Instructions:
        - Use markdown-style headers
        - Include quantitative insights from the visual analysis
        - Reference specific visual elements found
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
        1. Assess coverage of visual elements found in analysis:
        - Dominant colors: {metadata['visual_features']['dominant_colors']}
        - Text elements: {metadata['visual_features']['text_elements']['count']} regions
        - Shapes detected: {metadata['visual_features']['shape_analysis']['count']}

        2. Evaluate statistical insights:
        - Are data ranges properly interpreted? {metadata['data_dimensions']}
        - Are visual patterns properly described?

        3. Suggest improvements:
        - Add more quantitative details from visual analysis
        - Clarify connections between visual elements
        - Enhance interpretation of color usage
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

        Visual Analysis Details:
        {self._format_opencv_analysis(metadata['visual_features'])}

        Data Statistics:
        {metadata['statistical_summary']}

        Refinement Guidelines:
        1. Address all points in the critique
        2. Incorporate specific visual analysis findings
        3. Maintain structured format but enhance depth
        4. Connect visual elements to data patterns
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
        """Generic model querying method with provider-specific logic"""
        provider = next(
            (p for p, models in self.DEFAULT_MODELS.items() if model in models), 
            None
        )
        
        if not provider:
            raise ValueError(f"No provider found for model {model}")
        
        try:
            if provider == 'groq':
                client = self.clients['groq']
                
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

        fig.set_size_inches(8, 6)   
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _convert_plot_to_array(self, plot_object: Union[plt.Figure, plt.Axes]) -> np.ndarray:
        """Convert matplotlib plot to numpy array for OpenCV processing"""
        buf = BytesIO()
        if isinstance(plot_object, plt.Axes):
            plot_object.figure.savefig(buf, format='png', bbox_inches='tight')
        else:
            plot_object.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        return cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    def _extract_plot_metadata(self, plot_object: Union[plt.Figure, plt.Axes], img_array: np.ndarray) -> Dict[str, Any]:
        """Extract comprehensive metadata about the plot with OpenCV analysis"""
        # Perform OpenCV analysis
        visual_features = self.cv_analyzer.analyze_plot(img_array)
        
        # Combine with existing metadata
        metadata = {
            'data_dimensions': self._get_data_dimensions(plot_object),
            'statistical_summary': self._compute_statistical_summary(plot_object),
            'visual_features': visual_features
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
                    'max': np.max(flattened_data),
                    'range': np.ptp(flattened_data)
                }
        except Exception as e:
            warnings.warn(f"Error computing statistical summary: {e}")
        return {}

def explain_plot(
    plot_object: Union[plt.Figure, plt.Axes], 
    prompt: str = "Explain this data visualization",
    api_keys: Optional[Dict[str, str]] = None,
    max_iterations: int = 3,
    custom_parameters: Optional[Dict] = None
) -> str:
    """
    Convenience function for iterative plot explanation with OpenCV-enhanced analysis
    
    Args:
        plot_object: Matplotlib Figure or Axes object
        prompt: Explanation prompt
        api_keys: API keys for different providers
        max_iterations: Maximum refinement iterations
        custom_parameters: Additional generation parameters
    
    Returns:
        Comprehensive explanation with visual analysis details
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

# Example usage with OpenCV-enhanced analysis
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Create a more complex sample plot
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    plt.plot(x, y1, label='Sine', color='blue', linewidth=2)
    plt.plot(x, y2, label='Cosine', color='red', linestyle='--')
    plt.title('Trigonometric Functions Comparison', fontsize=14)
    plt.xlabel('X-axis (radians)', fontsize=12)
    plt.ylabel('Y-axis values', fontsize=12)
    plt.legend()
    plt.grid(True)

    try:
        # Get enhanced explanation with OpenCV analysis
        result = explain_plot(
            plt.gca(), 
            prompt="Analyze this visualization of trigonometric functions, focusing on: "
                   "1. The visual representation of the functions "
                   "2. Comparison of their patterns "
                   "3. Key features visible in the plot",
            api_keys={'groq': os.getenv('GROQ_API_KEY')},
            max_iterations=3
        )
        
        print("\nFinal Enhanced Explanation:")
        print(result)
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")