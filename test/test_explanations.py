import pytest
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from unittest.mock import patch, MagicMock, PropertyMock, create_autospec
import tempfile
from PIL import Image
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
load_dotenv()

# Import the class to test
from plotsense import PlotExplainer, explainer
import plotsense.explanations.explanations as explanations_module

# Test data setup
@pytest.fixture
def sample_data():
    np.random.seed(42)
    return pd.DataFrame({
        'x': np.arange(100),
        'y': np.random.normal(0, 1, 100),
        'category': np.random.choice([0, 1, 2], 100)  # Numeric for color mapping
    })

@pytest.fixture
def sample_plot(sample_data):
    fig, ax = plt.subplots()
    sample_data.plot.scatter(x='x', y='y', c='category', cmap='viridis', ax=ax)
    return ax

@pytest.fixture
def mock_groq_completion():
    mock_message = MagicMock()
    type(mock_message).content = PropertyMock(return_value="Mock explanation")
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.fixture
def mock_groq_client():
    """Fixture that mocks the Groq client"""
    with patch('plotsense.explanations.explanations.Groq') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def plot_explainer_instance(mock_groq_client):
     # Patch the input function to return a test key
    #with patch('builtins.input', return_value='test_key'):
    return PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)

@pytest.fixture
def simple_plot():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    yield ax
    plt.close(fig)

@pytest.fixture
def temp_image_path(simple_plot, tmp_path):
    output_path = tmp_path / "test_plot.jpg"
    simple_plot.figure.savefig(output_path)
    return output_path

class TestPlotExplainerInitialization:
    def test_init_with_api_keys(self):
        explainer = PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)
        assert explainer.api_keys['groq'] == 'test_key'
        assert explainer.interactive is False
        assert explainer.max_iterations == 3

    def test_init_without_api_keys_interactive(self):
        # Temporarily set environment variable
        os.environ['GROQ_API_KEY'] = 'env-test-key'
        try:
            explainer = PlotExplainer(api_keys={})
            assert explainer.api_keys['groq'] == 'env-test-key'
        finally:
            # Clean up
            del os.environ['GROQ_API_KEY']

    def test_init_without_api_keys_non_interactive(self):
        if explanations_module.Groq is None:
            PlotExplainer(api_keys={}, interactive=False)
        else:
            with pytest.raises(ValueError, match="API key is required"):
                PlotExplainer(api_keys={}, interactive=False)

    def test_validate_keys_missing(self):
        if explanations_module.Groq is None:
            PlotExplainer(api_keys={}, interactive=False)
        else:
            with pytest.raises(ValueError, match="API key is required"):
                PlotExplainer(api_keys={}, interactive=False)

    def test_initialize_clients(self, mock_groq_client):
        explainer = PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)
        assert 'groq' in explainer.clients
        assert explainer.clients['groq'] is not None

    def test_detect_available_models(self, plot_explainer_instance):
        assert len(plot_explainer_instance.available_models) > 0
        assert all(model in PlotExplainer.DEFAULT_MODELS['groq'] 
                  for model in plot_explainer_instance.available_models)

class TestPlotHandling:
    def test_save_plot_to_image_figure(self, sample_plot, tmp_path):
        explainer = PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)
        fig = sample_plot.figure
        output_path = tmp_path / "test_figure.jpg"
        result = explainer.save_plot_to_image(fig, str(output_path))
        assert os.path.exists(result)
        assert Image.open(result).format == 'JPEG'

    def test_save_plot_to_image_axes(self, sample_plot, tmp_path):
        explainer = PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)
        output_path = tmp_path / "test_axes.jpg"
        result = explainer.save_plot_to_image(sample_plot, str(output_path))
        assert os.path.exists(result)
        assert Image.open(result).format == 'JPEG'

    def test_encode_image(self, sample_plot, tmp_path):
        explainer = PlotExplainer(api_keys={'groq': 'test_key'}, interactive=False)
        output_path = tmp_path / "test_encode.jpg"
        explainer.save_plot_to_image(sample_plot, str(output_path))
        encoded = explainer.encode_image(str(output_path))
        assert isinstance(encoded, str)
        assert len(encoded) > 0

class TestModelQuerying:
    def test_query_model_success(self, plot_explainer_instance, mock_groq_client, temp_image_path):
        """Test successful LLM query with proper mocking"""
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Insight: Trend A dominates."
        mock_completion.choices = [mock_choice]
        mock_groq_client.chat.completions.create.return_value = mock_completion
        plot_explainer_instance.clients["groq"] = mock_groq_client

        model = plot_explainer_instance.available_models[0]

        response = plot_explainer_instance._query_model(
            model=model,
            prompt="What's the trend?",
            image_path=str(temp_image_path)
        )
        assert response == "Insight: Trend A dominates."
        
        # Verify the mock was called correctly
        mock_groq_client.chat.completions.create.assert_called_once()


    def test_query_model_invalid_model(self, plot_explainer_instance, sample_plot, tmp_path):
        output_path = tmp_path / "test_query.jpg"
        plot_explainer_instance.save_plot_to_image(sample_plot, str(output_path))
        
        with pytest.raises(ValueError):
            plot_explainer_instance._query_model(
                model="invalid_model",
                prompt="Test prompt",
                image_path=str(output_path)
            )

    def test_query_model_retry(self, plot_explainer_instance, mock_groq_client, temp_image_path):
        # Configure the mock to fail twice then succeed
        mock_groq_client.chat.completions.create.side_effect = [
            Exception("503 Service Unavailable"),
            Exception("503 Service Unavailable"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Retry success"))])
        ]
        
        mock_choice = MagicMock()
        mock_choice.message.content = "Insight: Trend A dominates."
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_groq_client.chat.completions.create.return_value = mock_completion
        plot_explainer_instance.clients["groq"] = mock_groq_client
        
        model = plot_explainer_instance.available_models[0]
        response = plot_explainer_instance._query_model(
            model=model,
            prompt="What's the trend?",
            image_path=str(temp_image_path)
        )
        assert response == "Retry success"
        assert mock_groq_client.chat.completions.create.call_count == 3

class TestExplanationGeneration:
    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_generate_initial_explanation(self,mock_query_model,plot_explainer_instance, temp_image_path):
        """Test explanation generation"""
        # Arrange
        mock_query_model.return_value = "Test explanation"
        model = plot_explainer_instance.available_models[0]
        prompt = "Test prompt"

        # Act
        explanation = plot_explainer_instance._generate_initial_explanation(
            model=model,
            image_path=str(temp_image_path),
            original_prompt=prompt
        )

        # Assert
        assert explanation == "Test explanation"
        assert mock_query_model.call_count == 1

        # Verify that the prompt contains the original prompt
        called_args, called_kwargs = mock_query_model.call_args
        assert prompt in called_kwargs["prompt"]
        assert called_kwargs["model"] == model
        assert called_kwargs["image_path"] == str(temp_image_path)

    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_generate_critique(self,mock_query_model,plot_explainer_instance, temp_image_path):
        """Test critique generation"""
        mock_query_model.return_value = "Test critique"
        model = plot_explainer_instance.available_models[0]
        prompt = "Test prompt"
        critique = plot_explainer_instance._generate_critique(
            image_path=str(temp_image_path),
            current_explanation="Test explanation",
            original_prompt=prompt,
            model=model
        )
        assert critique == "Test critique"
        assert mock_query_model.call_count == 1

        # Verify that the prompt contains the original prompt
        called_args, called_kwargs = mock_query_model.call_args
        assert prompt in called_kwargs["prompt"]
        assert called_kwargs["model"] == model
        assert called_kwargs["image_path"] == str(temp_image_path)

    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_generate_refinement(self,mock_query_model,plot_explainer_instance, temp_image_path):
        """Test refinement generation"""
        mock_query_model.return_value = "Test refinement"
        model = plot_explainer_instance.available_models[0]
        prompt = "Test prompt"
        refinement = plot_explainer_instance._generate_refinement(
            image_path=str(temp_image_path),
            current_explanation="Test explanation",
            critique="Test critique",
            original_prompt=prompt,
            model=model
        )
        assert refinement == "Test refinement"
        assert mock_query_model.call_count == 1

        # Verify that the prompt contains the original prompt
        called_args, called_kwargs = mock_query_model.call_args
        assert prompt in called_kwargs["prompt"]
        assert called_kwargs["model"] == model
        assert called_kwargs["image_path"] == str(temp_image_path)

    @patch('plotsense.explanations.explanations.PlotExplainer._generate_initial_explanation')
    @patch('plotsense.explanations.explanations.PlotExplainer._generate_critique')
    @patch('plotsense.explanations.explanations.PlotExplainer._generate_refinement')
    def test_refine_plot_explanation(self,mock_refine, mock_critique, mock_explain, sample_plot, plot_explainer_instance):
        """Test the full refinement process"""
        # Setup mock return values
        mock_explain.return_value = "Initial explanation"
        mock_critique.side_effect = ["Critique 1", "Critique 2"]
        mock_refine.side_effect = ["Refined 1", "Refined 2"]


        explanation =  plot_explainer_instance.refine_plot_explanation(
            sample_plot,
            prompt="Test prompt"
        )

        assert explanation == "Refined 2"
        assert mock_explain.call_count == 1
        assert mock_critique.call_count == 2
        assert mock_refine.call_count == 2
     
class TestConvenienceFunction:
    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_explainer_function(self, mock_query_model, simple_plot):
        mock_query_model.return_value = "Test refinement"
        """Test the explainer function"""
        # Mock the query model to return a fixed response
        mock_query_model.return_value = "Mock explanation"
        # Call the explainer function
      
        result = explainer(
            plot_object=simple_plot,
            prompt="Test prompt",
            api_keys={'groq': 'test_key'},
            custom_parameters={'temperature': 0.5, 'max_tokens': 800},
            max_iterations=2
        )
        assert  result == "Mock explanation"
        assert mock_query_model.call_count >=1
        # Verify that the prompt contains the original prompt   
        called_args, called_kwargs = mock_query_model.call_args
        assert "Test prompt" in called_kwargs["prompt"]
        assert called_kwargs["model"] == "meta-llama/llama-4-maverick-17b-128e-instruct"
        assert called_kwargs["image_path"] is not None

    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_explainer_function_no_prompt(self, mock_query_model, simple_plot):
        """Test the explainer function without a prompt"""
        
        # Mock the query model to return a fixed response
        mock_query_model.return_value = "Mock explanation"
        # Call the explainer function
        result = explainer(
            plot_object=simple_plot,
            api_keys={'groq': 'test_key'},
            custom_parameters={'temperature': 0.5, 'max_tokens': 800},
            max_iterations=2
        )
        assert result == "Mock explanation"
        assert mock_query_model.call_count >=1

    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_explainer_function_singleton(self, mock_query_model, sample_plot):
        """Test the singleton behavior of the explainer function"""
        # Mock the query model to return a fixed response
        mock_query_model.return_value = "Mock explanation"
        # Call the explainer function

        # First call creates instance
        result1 = explainer(plot_object=sample_plot, api_keys={'groq': 'test_key'})
        # Second call uses same instance
        result2 = explainer(plot_object=sample_plot)
        assert result1 == result2

class TestExampleUsage:
    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_full_workflow(self, mock_query_model, simple_plot):
        """Test the full workflow of the PlotExplainer"""
        # Mock the query model to return a fixed response
        mock_query_model.return_value = "Mock explanation"
        explanation = explainer(
            plot_object=simple_plot,
            prompt="Explain this line plot",
            api_keys={'groq': 'test_key'},
            max_iterations=2
        )
        assert  explanation == "Mock explanation"
        # Verify that the mock was called with the correct prompt
        called_args, called_kwargs = mock_query_model.call_args
        assert "Explain this line plot" in called_kwargs["prompt"]
        assert called_kwargs["model"] == "meta-llama/llama-4-maverick-17b-128e-instruct"
        assert called_kwargs["image_path"] is not None
        # Verify that the mock was called once
        assert mock_query_model.call_count >= 1
        # Check that the custom parameters were passed correctly
    
       
    @patch('plotsense.explanations.explanations.PlotExplainer._query_model')
    def test_different_plot_types(self, mock_query_model):
        """Test with different plot types"""
        # Mock the query model to return a fixed response
        mock_query_model.return_value = "Mock explanation"
        # Test with line plot
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [4, 5, 6])
        explanation1 = explainer(ax1, "Explain this line plot")
        assert explanation1 == "Mock explanation"
        # Verify that the mock was called with the correct prompt   
        called_args, called_kwargs = mock_query_model.call_args
        assert "Explain this line plot" in called_kwargs["prompt"]
        assert called_kwargs["model"] == "meta-llama/llama-4-maverick-17b-128e-instruct"
        assert called_kwargs["image_path"] is not None
        # Verify that the mock was called once
        assert mock_query_model.call_count >= 1
      
        plt.close(fig1)
        
        # Test with bar plot
        fig2, ax2 = plt.subplots()
        ax2.bar(['A', 'B', 'C'], [3, 7, 2])
        explanation2 = explainer(ax2, "Explain this bar plot")
        assert explanation2 == "Mock explanation"
        # Verify that the mock was called with the correct prompt   
        called_args, called_kwargs = mock_query_model.call_args
        assert "Explain this bar plot" in called_kwargs["prompt"]
        assert called_kwargs["model"] == "meta-llama/llama-4-maverick-17b-128e-instruct"
        assert called_kwargs["image_path"] is not None
        # Verify that the mock was called once
        assert mock_query_model.call_count >= 1
        # Clean up
        plt.close(fig2)

# if __name__ == "__main__":
#     pytest.main(["-v", "--cov=plot_explainer", "--cov-report=term-missing"])