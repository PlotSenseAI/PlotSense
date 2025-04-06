import matplotlib.pyplot as plt
import numpy as np
from explanations import PlotExplainer
from explanations import refine_plot_explanation
from unittest.mock import patch, MagicMock
import warnings

# Unit Testing the Core Functions of PlotExplainer

def test_plot_conversion():
    """Test that plot objects are correctly converted to bytes"""
    # Create a simple plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    
    explainer = PlotExplainer()
    
    # Test with Figure object
    fig_bytes = explainer._plot_to_bytes(fig)
    assert isinstance(fig_bytes, bytes)
    assert len(fig_bytes) > 1000  # Should be a reasonable size
    
    # Test with Axes object
    ax_bytes = explainer._plot_to_bytes(ax)
    assert isinstance(ax_bytes, bytes)
    assert len(ax_bytes) > 1000
    
    plt.close(fig)

def test_model_selection():
    """Test model selection logic"""
    explainer = refine_plot_explanation()
    
    # Test default rotation
    models = explainer._select_model_rotation()
    assert isinstance(models, list)
    assert len(models) > 0
    
    # Test with forced model rotation
    custom_models = ['llama3-70b-8192']
    result = explainer.refine_plot_explanation(
        plt.gcf(), 
        model_rotation=custom_models
    )
    assert custom_models[0] in explainer.available_models

# Mock Testing the API Calls

def test_api_calls_with_mocking():
    """Test API calling logic with mocks"""
    explainer = PlotExplainer(api_keys={'groq': 'test_key'})
    
    # Create a simple plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    
    with patch('plot_explainer.PlotExplainer._query_llama3') as mock_query:
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test explanation"
        mock_query.return_value = "Test explanation"
        
        # Test basic explanation
        result = explainer.refine_plot_explanation(
            fig,
            prompt="Explain this plot",
            iterations=1,
            model_rotation=['llama3-70b-8192']
        )
        
        assert result == "Test explanation"
        assert mock_query.called
        
        # Verify image was properly encoded
        args, kwargs = mock_query.call_args
        assert isinstance(args[0], bytes)  # img_bytes
        assert "Explain this plot" in args[1]  # prompt
        
    plt.close(fig)

# Integration Testing (Actual API Calls)

def test_real_api_integration():
    """Actual API integration test (requires valid API keys)"""
    # Only run if API keys are available
    API_KEYS = {'groq': 'your_real_key_here'}
    
    if not API_KEYS.get('groq'):
        warnings.warn("Skipping real API tests - no credentials")
        return
    
    # Create a simple plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title("Test Plot")
    ax.set_xlabel("X values")
    ax.set_ylabel("Y values")
    
    explainer = PlotExplainer(api_keys=API_KEYS)
    
    # Test basic explanation
    result = explainer.refine_plot_explanation(
        fig,
        prompt="Explain this simple quadratic relationship",
        iterations=1
    )
    
    assert isinstance(result, str)
    assert len(result) > 50  # Should be a reasonable response
    print("API Test Successful. Explanation:")
    print(result)
    
    plt.close(fig)

# End-to-End Test with Package Function

def test_package_level_function():
    """Test the convenience function"""
    # Create a simple plot
    fig, ax = plt.subplots()
    ax.bar(['A', 'B', 'C'], [3, 7, 2])
    
    # Test with mock
    with patch('plot_explainer._explainer_instance') as mock_instance:
        mock_instance.refine_plot_explanation.return_value = "Mock explanation"

        explainer = PlotExplainer(api_keys=API_KEYS)
        
        from explainer import refine_plot_explanation
        result = refine_plot_explanation(ax)
        
        assert result == "Mock explanation"
        mock_instance.refine_plot_explanation.assert_called()
    
    plt.close(fig)

# Error Handling Tests

def test_error_handling():
    """Test error cases"""
    explainer = PlotExplainer()
    
    # Test invalid plot object
    try:
        explainer.refine_plot_explanation("not a plot")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
    
    # Test unavailable model
    try:
        explainer.refine_plot_explanation(
            plt.gcf(),
            model_rotation=['non-existent-model']
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    plt.close('all')

if __name__ == "__main__":
    test_plot_conversion()
    test_model_selection()
    test_api_calls_with_mocking()
    test_package_level_function()
    test_error_handling()
    
    # Uncomment to run real API tests (with proper credentials)
    test_real_api_integration()
    
    print("All tests passed!")