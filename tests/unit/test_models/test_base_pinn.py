"""Tests for BasePINN class."""

import pytest
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock

from ai_pinn.models.pinn.base_pinn import BasePINN


class TestBasePINN:
    """Test class for BasePINN."""
    
    @pytest.fixture
    def model_config(self):
        """Model configuration fixture."""
        return {
            'input_dim': 3,
            'output_dim': 1,
            'hidden_layers': [50, 50, 50],
            'activation': 'tanh'
        }
    
    @pytest.fixture
    def model(self, model_config):
        """Model fixture."""
        # Create a concrete implementation for testing
        class ConcretePINN(BasePINN):
            def compute_physics_loss(self, x, **kwargs):
                # Simple physics loss for testing
                u = self.forward(x)
                return torch.mean(u**2)
        
        return ConcretePINN(**model_config)
    
    def test_initialization(self, model_config):
        """Test model initialization."""
        model = BasePINN(**model_config)
        
        assert model.input_dim == model_config['input_dim']
        assert model.output_dim == model_config['output_dim']
        assert model.hidden_layers == model_config['hidden_layers']
        assert model.activation_name == model_config['activation']
        assert isinstance(model.device, torch.device)
        assert len(model.layers) == len(model_config['hidden_layers']) + 1
    
    def test_build_layers(self, model_config):
        """Test layer building."""
        model = BasePINN(**model_config)
        expected_layers = len(model_config['hidden_layers']) + 1
        
        assert len(model.layers) == expected_layers
        
        # Check input layer
        assert model.layers[0].in_features == model_config['input_dim']
        assert model.layers[0].out_features == model_config['hidden_layers'][0]
        
        # Check hidden layers
        for i in range(len(model_config['hidden_layers']) - 1):
            assert model.layers[i+1].in_features == model_config['hidden_layers'][i]
            assert model.layers[i+1].out_features == model_config['hidden_layers'][i+1]
        
        # Check output layer
        assert model.layers[-1].in_features == model_config['hidden_layers'][-1]
        assert model.layers[-1].out_features == model_config['output_dim']
    
    def test_get_activation_function(self, model_config):
        """Test activation function retrieval."""
        model = BasePINN(**model_config)
        
        # Test valid activation functions
        valid_activations = ['tanh', 'relu', 'sigmoid', 'leaky_relu', 'elu', 'swish']
        for activation in valid_activations:
            fn = model._get_activation_function(activation)
            assert isinstance(fn, nn.Module)
        
        # Test invalid activation function
        with pytest.raises(ValueError):
            model._get_activation_function('invalid_activation')
    
    def test_forward_pass(self, model):
        """Test forward pass."""
        batch_size = 10
        input_data = torch.randn(batch_size, model.input_dim)
        
        output = model.forward(input_data)
        
        assert output.shape == (batch_size, model.output_dim)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_compute_boundary_loss(self, model):
        """Test boundary loss computation."""
        batch_size = 10
        x_boundary = torch.randn(batch_size, model.input_dim)
        u_boundary = torch.randn(batch_size, model.output_dim)
        
        boundary_loss = model.compute_boundary_loss(x_boundary, u_boundary)
        
        assert isinstance(boundary_loss, torch.Tensor)
        assert boundary_loss.item() >= 0
        
        # Test with zero boundary values
        u_zero = torch.zeros(batch_size, model.output_dim)
        boundary_loss_zero = model.compute_boundary_loss(x_boundary, u_zero)
        assert boundary_loss_zero.item() >= 0
    
    def test_compute_total_loss(self, model):
        """Test total loss computation."""
        batch_size = 10
        x_collocation = torch.randn(batch_size, model.input_dim)
        x_boundary = torch.randn(batch_size, model.input_dim)
        u_boundary = torch.randn(batch_size, model.output_dim)
        
        losses = model.compute_total_loss(
            x_collocation, x_boundary, u_boundary,
            lambda_physics=1.0, lambda_boundary=1.0
        )
        
        assert isinstance(losses, dict)
        assert 'total_loss' in losses
        assert 'physics_loss' in losses
        assert 'boundary_loss' in losses
        
        # Check that total loss is weighted sum
        expected_total = losses['physics_loss'] + losses['boundary_loss']
        assert torch.allclose(losses['total_loss'], expected_total)
    
    def test_different_weights(self, model):
        """Test total loss with different weights."""
        batch_size = 10
        x_collocation = torch.randn(batch_size, model.input_dim)
        x_boundary = torch.randn(batch_size, model.input_dim)
        u_boundary = torch.randn(batch_size, model.output_dim)
        
        # Test with different weights
        losses1 = model.compute_total_loss(
            x_collocation, x_boundary, u_boundary,
            lambda_physics=2.0, lambda_boundary=1.0
        )
        
        losses2 = model.compute_total_loss(
            x_collocation, x_boundary, u_boundary,
            lambda_physics=1.0, lambda_boundary=2.0
        )
        
        # The weighted sums should be different
        assert not torch.allclose(losses1['total_loss'], losses2['total_loss'])
    
    def test_count_parameters(self, model):
        """Test parameter counting."""
        param_count = model.count_parameters()
        
        assert isinstance(param_count, int)
        assert param_count > 0
        
        # Count manually to verify
        manual_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
        assert param_count == manual_count
    
    def test_summary(self, model):
        """Test model summary."""
        summary = model.summary()
        
        assert isinstance(summary, str)
        assert model.__class__.__name__ in summary
        assert str(model.input_dim) in summary
        assert str(model.output_dim) in summary
        assert str(model.hidden_layers) in summary
        assert model.activation_name in summary
        assert str(model.device) in summary
    
    @patch('torch.save')
    def test_save_model(self, mock_save, model):
        """Test model saving."""
        filepath = "test_model.pth"
        model.save_model(filepath)
        
        # Check that torch.save was called with correct arguments
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        
        # Check that the saved dictionary contains expected keys
        saved_dict = args[0]
        assert 'model_state_dict' in saved_dict
        assert 'input_dim' in saved_dict
        assert 'output_dim' in saved_dict
        assert 'hidden_layers' in saved_dict
        assert 'activation' in saved_dict
        
        assert saved_dict['input_dim'] == model.input_dim
        assert saved_dict['output_dim'] == model.output_dim
        assert saved_dict['hidden_layers'] == model.hidden_layers
        assert saved_dict['activation'] == model.activation_name
    
    @patch('torch.load')
    def test_load_model(self, mock_load, model_config):
        """Test model loading."""
        # Create a mock checkpoint
        checkpoint = {
            'model_state_dict': {'param': torch.tensor([1.0])},
            'input_dim': model_config['input_dim'],
            'output_dim': model_config['output_dim'],
            'hidden_layers': model_config['hidden_layers'],
            'activation': model_config['activation']
        }
        mock_load.return_value = checkpoint
        
        # Create a concrete implementation for testing
        class ConcretePINN(BasePINN):
            def compute_physics_loss(self, x, **kwargs):
                return torch.mean(x**2)
        
        filepath = "test_model.pth"
        loaded_model = ConcretePINN.load_model(filepath)
        
        # Check that torch.load was called
        mock_load.assert_called_once_with(filepath, map_location=None)
        
        # Check model parameters
        assert loaded_model.input_dim == model_config['input_dim']
        assert loaded_model.output_dim == model_config['output_dim']
        assert loaded_model.hidden_layers == model_config['hidden_layers']
        assert loaded_model.activation_name == model_config['activation']
    
    @patch('ai_pinn.models.pinn.base_pinn.load_config')
    def test_from_config(self, mock_load_config, model_config):
        """Test model creation from config."""
        # Mock the config loading
        mock_config = {
            'model': model_config
        }
        mock_load_config.return_value = mock_config
        
        # Create a concrete implementation for testing
        class ConcretePINN(BasePINN):
            def compute_physics_loss(self, x, **kwargs):
                return torch.mean(x**2)
        
        config_path = "test_config.yaml"
        model = ConcretePINN.from_config(config_path)
        
        # Check that load_config was called
        mock_load_config.assert_called_once_with(config_path)
        
        # Check model parameters
        assert model.input_dim == model_config['input_dim']
        assert model.output_dim == model_config['output_dim']
        assert model.hidden_layers == model_config['hidden_layers']
        assert model.activation_name == model_config['activation']