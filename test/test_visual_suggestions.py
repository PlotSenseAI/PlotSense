import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from plotsense.visual_suggestion.Visual_suggestion_v2 import VisualizationRecommender
import os
from dotenv import load_dotenv
from builtins import input
from collections import defaultdict

# Load environment variables for testing
load_dotenv()

# Sample test data
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    data = {
        'date': pd.date_range('2020-01-01', periods=100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'value': np.random.normal(0, 1, 100),
        'count': np.random.randint(0, 100, 100),
        'flag': np.random.choice([True, False], 100)
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_recommender(sample_dataframe):
    """Create a mock recommender instance"""
    recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
    recommender.set_dataframe(sample_dataframe)
    return recommender

@pytest.fixture
def mock_llama_response():
    """Mock response from Llama models"""
    return """
Plot Type: scatter plot
Variables: value, count
Rationale: Shows relationship between two continuous variables
---
Plot Type: bar chart
Variables: category, count
Rationale: Compares discrete categories with their counts
---
Plot Type: line chart
Variables: date, value
Rationale: Shows trend over time
---
Plot Type: histogram
Variables: value
Rationale: Shows distribution of values
---
Plot Type: box plot
Variables: category, value
Rationale: Compares distributions across categories
"""

# Unit Tests
class TestInitialization:
    def test_init_without_keys(self):
        """Test initialization without API keys"""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            recommender = VisualizationRecommender()
            assert recommender.api_keys['groq'] == 'test_key'
    
    def test_init_with_keys(self):
        """Test initialization with provided API keys"""
        recommender = VisualizationRecommender(api_keys={'groq': 'provided_key'})
        assert recommender.api_keys['groq'] == 'provided_key'

    def test_init_with_missing_key(self):
        """Test initialization with missing API key in non-interactive mode"""
        with pytest.raises(ValueError, match="GROQ API key is required"):
            VisualizationRecommender(api_keys={'groq': None}, interactive=False)
    
    def test_init_with_missing_key_interactive(self, monkeypatch):
        """Test interactive key input"""
        # Mock input to return a test key
        monkeypatch.setattr('builtins.input', lambda _: 'test_key')
        
        recommender = VisualizationRecommender(api_keys={'groq': None}, interactive=True)
        assert recommender.api_keys['groq'] == 'test_key'

    
    def test_default_models(self):
        """Test default model configuration"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        assert 'llama3-70b-8192' in recommender.DEFAULT_MODELS['groq'][0]
        assert isinstance(recommender.DEFAULT_MODELS['groq'], list)
    
    def test_model_weights_initialization(self):
        """Test model weights are properly initialized"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        assert hasattr(recommender, 'model_weights')
        assert sum(recommender.model_weights.values()) == pytest.approx(1.0)

class TestDataFrameHandling:
    def test_set_dataframe(self, mock_recommender, sample_dataframe):
        """Test setting the DataFrame"""
        assert mock_recommender.df.equals(sample_dataframe)
    
    def test_describe_dataframe(self, mock_recommender):
        """Test DataFrame description generation"""
        description = mock_recommender._describe_dataframe()
        assert "DataFrame Shape" in description
        assert "Columns" in description
        assert "Column Details" in description
        for col in mock_recommender.df.columns:
            assert col in description

class TestPromptGeneration:
    def test_create_prompt(self, mock_recommender):
        """Test prompt generation"""
        description = mock_recommender._describe_dataframe()
        prompt = mock_recommender._create_prompt(description)
        
        assert "data visualization expert" in prompt
        assert "Plot Type:" in prompt
        assert "Variables:" in prompt
        assert "Rationale:" in prompt
        assert description in prompt

class TestResponseParsing:
    def test_parse_recommendations(self, mock_recommender):
        """Test parsing of LLM response"""
        response = """
            Plot Type: scatter plot
            Variables: value, count
            Rationale: Test rationale
            ---
            Plot Type: bar chart
            Variables: category, count
            Rationale: Another test
            """
        recs = mock_recommender._parse_recommendations(response, 'test-model')
        assert len(recs) == 2
        assert recs[0]['plot_type'] == 'scatter plot'
        assert recs[0]['variables'] == 'value, count'
        assert recs[0]['rationale'] == 'Test rationale'
        assert recs[1]['plot_type'] == 'bar chart'
    
    def test_parse_invalid_recommendations(self, mock_recommender):
        """Test parsing of invalid/malformed responses"""
        response = "Plot Type: invalid\n---\nNo variables here\n---"
        recs = mock_recommender._parse_recommendations(response, 'test-model')
        assert len(recs) == 0
        
        empty_response = ""
        recs = mock_recommender._parse_recommendations(empty_response, 'test-model')
        assert len(recs) == 0
    
    def test_parse_recommendations_with_missing_vars(self, mock_recommender):
        """Test parsing when some variables aren't in DataFrame"""
        response = """
                    Plot Type: scatter plot
                    Variables: value, nonexistent
                    Rationale: Test
                    ---
                    Plot Type: bar chart
                    Variables: category, count
                    Rationale: Valid
                    """
        recs = mock_recommender._parse_recommendations(response, 'test-model')
        assert len(recs) == 2  # Should skip the first one with invalid vars
        # First recommendation should be scatter plot with only valid variables
        assert recs[0]['plot_type'] == 'scatter plot'
        assert recs[0]['variables'] == 'value'

        # Second recommendation should be unchanged
        assert recs[1]['plot_type'] == 'bar chart'
        assert recs[1]['variables'] == 'category, count'


# Integration Tests
class TestRecommendationGeneration:
    @patch('plotsense.visual_suggestion.Visual_suggestion_v2.VisualizationRecommender._query_llama')
    def test_get_model_recommendations(self, mock_query, mock_recommender, mock_llama_response):
        """Test getting recommendations from a single model"""
        mock_query.return_value = mock_llama_response
        recs = mock_recommender._get_model_recommendations('llama3-70b-8192', "test prompt")
        
        assert len(recs) == 5
        assert all(key in recs[0] for key in ['plot_type', 'variables', 'rationale'])
        assert recs[0]['source_model'] == 'llama3-70b-8192'
    
    @patch('plotsense.visual_suggestion.Visual_suggestion_v2.VisualizationRecommender._get_model_recommendations')
    def test_get_all_recommendations(self, mock_get, mock_recommender):
        """Test parallel recommendation collection"""
        mock_get.return_value = [{'plot_type': 'test', 'variables': 'x,y', 'rationale': 'test'}]
        
        mock_recommender.available_models = ['model1', 'model2']
        mock_recommender.model_weights = {'model1': 0.6, 'model2': 0.4}

        all_recs = mock_recommender._get_all_recommendations()
        assert len(all_recs) == 2
        assert 'model1' in all_recs
        assert 'model2' in all_recs 
    


    def test_apply_ensemble_scoring(mock_recommender):
        # Input recommendations from two models
        all_recs = {
            'model1': [
                {'plot_type': 'scatter', 'variables': 'x,y', 'rationale': 'clear pattern'},
                {'plot_type': 'bar', 'variables': 'a,b', 'rationale': 'categorical grouping'}
            ],
            'model2': [
                {'plot_type': 'scatter', 'variables': 'x,y', 'rationale': 'correlation'},
                {'plot_type': 'line', 'variables': 't,v', 'rationale': 'trend over time'}
            ]
        }

        # Equal weights for both models
        weights = {'model1': 0.6, 'model2': 0.4}

        # Call private method directly (normally you’d test via public interface)
        results = mock_recommender._apply_ensemble_scoring(all_recs, weights)

        # Check number of unique recommendations
        assert len(results) == 3

        # Check required columns exist
        assert set(results.columns) >= {
            'plot_type', 'variables', 'rationale', 
            'ensemble_score', 'model_agreement', 'source_models'
        }

        # Get ensemble scores into a dictionary for verification
        scores = results.set_index(['plot_type', 'variables'])['ensemble_score'].to_dict()

        # Expected values (based on position-based weights and normalization)
        # model1 scatter: 0.6 * 1/1 = 0.6
        # model2 scatter: 0.4 * 1/1 = 0.4 => total 1.0 (will normalize this to 1.0)
        # model1 bar:     0.6 * 1/2 = 0.3
        # model2 line:    0.4 * 1/2 = 0.2
        assert scores[('scatter', 'x,y')]== pytest.approx(0.75)
        assert scores[('bar', 'a,b')] == pytest.approx(0.3, rel=1e-2)
        assert scores[('line', 't,v')] == pytest.approx(0.2, rel=1e-2)

        # Check model agreement count
        agreements = results.set_index(['plot_type', 'variables'])['model_agreement'].to_dict()
        assert agreements[('scatter', 'x,y')] == 2
        assert agreements[('bar', 'a,b')] == 1
        assert agreements[('line', 't,v')] == 1

        # Check source models recorded correctly
        source_models = results.set_index(['plot_type', 'variables'])['source_models'].to_dict()
        assert set(source_models[('scatter', 'x,y')]) == {'model1', 'model2'}
        assert source_models[('bar', 'a,b')] == ['model1']
        assert source_models[('line', 't,v')] == ['model2']



# End-to-End Tests
class TestEndToEnd:
    @patch('groq.Groq')
    @patch('plotsense.visual_suggestion.Visual_suggestion_v2.VisualizationRecommender._query_llama')
    def test_full_recommendation_flow(self, mock_query, mock_groq, sample_dataframe, mock_llama_response):
        """Test the complete recommendation flow with mocks"""
        mock_query.return_value = mock_llama_response
        
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        recommender.set_dataframe(sample_dataframe)
        
        # Pretend we have these models available
        recommender.available_models = ['model1', 'model2']
        recommender.model_weights = {'model1': 0.6, 'model2': 0.4}
        
        results = recommender.recommend_visualizations(n=3)
        
        assert len(results) == 3
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        
        # Verify expected columns - adjust based on your actual output
        expected_columns = ['plot_type', 'variables', 'rationale', 'ensemble_score','model_agreement', 'source_models']
        assert len(results.columns) == len(expected_columns)
        assert len(set(results.columns) & set(expected_columns)) == len(expected_columns)
        assert all(col in results.columns for col in expected_columns)

        # Verify scores are properly normalized
        assert results['ensemble_score'].max() == pytest.approx(1.0)
        assert results['ensemble_score'].min() >= 0
        assert results['ensemble_score'].iloc[0] >= results['ensemble_score'].iloc[1]  # Should be sorted
        assert results['model_agreement'].iloc[0] >= results['model_agreement'].iloc[1]  # Should be sorted
    
    def test_convenience_function(self, sample_dataframe):
        """Test the package-level convenience function"""
        with patch('plotsense.visual_suggestion.Visual_suggestion_v2.recommend_visualizations') as mock_instance:
            mock_instance.return_value = pd.DataFrame({
                'plot_type': ['scatter'],
                'variables': ['x,y'],
                'rationale': ['test'],
                'ensemble_score': [1.0]
            })
            
            from plotsense.visual_suggestion.Visual_suggestion_v2 import recommend_visualizations
            results = recommend_visualizations(sample_dataframe)
            
            assert len(results) == 1

# Error Handling Tests
class TestErrorHandling:
    def test_no_dataframe_error(self):
        """Test error when no DataFrame is set"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        with pytest.raises(ValueError, match="No DataFrame set"):
            recommender.recommend_visualizations()
    
    def test_no_models_error(self, sample_dataframe):
        """Test error when no models are available"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        recommender.set_dataframe(sample_dataframe)
        recommender.available_models = []  # Simulate no available models
        
        with pytest.raises(ValueError, match="No available models"):
            recommender.VisualizationRecommender()
    
    @patch('plotsense.visual_suggestion.Visual_suggestion_v2.VisualizationRecommender._query_llama')
    def test_model_failure_handling(self, mock_query, mock_recommender):
        """Test handling of model failures"""
        mock_query.side_effect = Exception("API error")
        
        # Pretend we have two models - one will fail
        mock_recommender.available_models = ['model1', 'model2']
        mock_recommender.model_weights = {'model1': 0.6, 'model2': 0.4}
        
        with pytest.warns(UserWarning, match="Failed to get recommendations"):
            all_recs = mock_recommender._get_all_recommendations()
            
        assert len(all_recs) == 0  # Both models failed in this case

# Performance Tests
class TestPerformance:
    @patch('plotsense.visual_suggestion.Visual_suggestion_v2.VisualizationRecommender._query_llama')
    def test_recommendation_speed(self, mock_query, mock_recommender, mock_llama_response):
        """Test that recommendations are generated in reasonable time"""
        import time
        
        mock_query.return_value = mock_llama_response
        mock_recommender.available_models = ['model1', 'model2', 'model3']
        
        start_time = time.time()
        _ = mock_recommender.recommend_visualizations()
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0  # Should complete in under 5 seconds with mocks
    
    # def test_ensemble_scaling(self, mock_recommender):
    #     """Test that ensemble scoring scales with many recommendations"""
    #     # Create a large set of mock recommendations
    #     all_recs = {}
    #     for i in range(10):  # 10 models
    #         model_name = f'model_{i}'
    #         all_recs[model_name] = []
    #         for j in range(20):  # 20 recs per model
    #             all_recs[model_name].append({
    #                 'plot_type': f'plot_{j%5}',
    #                 'variables': f'var_{j},var_{(j+1)%10}',
    #                 'rationale': f'reason_{j}'
    #             })
        
    #     weights = {f'model_{i}': 0.1 for i in range(10)}  # Equal weights
        
    #     start_time = pd.Timestamp.now()
    #     results = mock_recommender._apply_ensemble_scoring(all_recs, weights)
    #     elapsed = (pd.Timestamp.now() - start_time).total_seconds()
        
    #     assert len(results) > 0
    #     assert elapsed < 1.0  # Should handle 200 total recs in <1 second

# Edge Case Tests
class TestEdgeCases:
    def test_empty_dataframe(self):
        """Test behavior with empty DataFrame"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        recommender.set_dataframe(pd.DataFrame())
        
        with pytest.raises(ValueError, match="No DataFrame set"):
            recommender.recommend_visualizations()
    
    def test_single_column_dataframe(self):
        """Test with DataFrame containing only one column"""
        recommender = VisualizationRecommender(api_keys={'groq': 'test_key'})
        recommender.set_dataframe(pd.DataFrame({'x': [1, 2, 3]}))
        
        # This should work, though recommendations may be limited
        with patch.object(recommender, '_query_llama') as mock_query:
            mock_query.return_value = """
Plot Type: histogram
Variables: x
Rationale: Only one variable available
"""
            results = recommender.recommend_visualizations()
            assert len(results) > 0
    
    def test_custom_weights(self, mock_recommender):
        """Test custom model weights"""
        mock_recommender.available_models = ['model1', 'model2']
        
        with patch.object(mock_recommender, '_get_all_recommendations') as mock_get:
            mock_get.return_value = {
                'model1': [{'plot_type': 'scatter', 'variables': 'x,y', 'rationale': 'test'}],
                'model2': [{'plot_type': 'bar', 'variables': 'a,b', 'rationale': 'test'}]
            }
            
            # With default weights (equal)
            default_results = mock_recommender.recommend_visualizations()
            
            # With custom weights favoring model2
            custom_results = mock_recommender.recommend_visualizations(
                custom_weights={'model1': 0.1, 'model2': 0.9}
            )
            
            # The bar chart should score higher with custom weights
            assert default_results.iloc[0]['plot_type'] == 'scatter'
            assert custom_results.iloc[0]['plot_type'] == 'bar'