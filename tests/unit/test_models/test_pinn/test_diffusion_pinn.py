"""Tests for DiffusionPINN class."""

import pytest
import torch
from unittest.mock import patch, MagicMock

from ai_pinn.models.pinn.diffusion_pinn import DiffusionPINN


class TestDiffusionPINN:
    """Test class for DiffusionPINN."""
    
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
    def diffusion_params(self):
        """Diffusion parameters fixture."""
        batch_size = 10
        return {
            'velocity': torch.randn(batch_size, 2),
            'diffusion_coeff': 0.1,
            'source_term': torch.randn(batch_size, 1)
        }
    
    @pytest.fixture
    def model(self, model_config):
        """Model fixture."""
        return DiffusionPINN(**model_config)
    
    def test_initialization(self, model_config):
        """Test model initialization."""
        model = DiffusionPINN(**model_config)
        
        assert model.input_dim == model_config['input_dim']
        assert model.output_dim == model_config['output_dim']
        assert model.hidden_layers == model_config['hidden_layers']
        assert model.activation_name == model_config['activation']
        assert isinstance(model.device, torch.device)
        assert len(model.layers) == len(model_config['hidden_layers']) + 1
    
    def test_compute_physics_loss(self, model, diffusion_params):
        """Test physics loss computation."""
        batch_size = 10
        x = torch.randn(batch_size, 3, requires_grad=True)
        
        physics_loss = model.compute_physics_loss(
            x, 
            velocity=diffusion_params['velocity'],
            diffusion_coeff=diffusion_params['diffusion_coeff'],
            source_term=diffusion_params['source_term']
        )
        
        assert isinstance(physics_loss, torch.Tensor)
        assert physics_loss.item() >= 0
        
        # Test with default parameters
        physics_loss_default = model.compute_physics_loss(x)
        assert physics_loss_default.item() >= 0
    
    def test_compute_mass_conservation_loss(self, model, diffusion_params):
        """Test mass conservation loss computation."""
        batch_size = 10
        x = torch.randn(batch_size, 3, requires_grad=True)
        
        mass_loss = model.compute_mass_conservation_loss(
            x, 
            velocity=diffusion_params['velocity']
        )
        
        assert isinstance(mass_loss, torch.Tensor)
        assert mass_loss.item() >= 0
    
    def test_compute_total_loss(self, model, diffusion_params):
        """Test total loss computation."""
        batch_size = 10
        x_collocation = torch.randn(batch_size, 3)
        x_boundary = torch.randn(batch_size, 3)
        u_boundary = torch.randn(batch_size, 1)
        
        losses = model.compute_total_loss(
            x_collocation, x_boundary, u_boundary,
            velocity=diffusion_params['velocity'],
            diffusion_coeff=diffusion_params['diffusion_coeff'],
            source_term=diffusion_params['source_term']
        )
        
        assert isinstance(losses, dict)
        assert 'total_loss' in losses
        assert 'physics_loss' in losses
        assert 'boundary_loss' in losses
        assert 'mass_conservation_loss' in losses
        
        # Check that total loss is weighted sum
        expected_total = (losses['physics_loss'] + 
                        losses['boundary_loss'] + 
                        losses['mass_conservation_loss'])
        assert torch.allclose(losses['total_loss'], expected_total)
    
    def test_predict_concentration(self, model, diffusion_params):
        """Test concentration prediction."""
        batch_size = 10
        x = torch.randn(batch_size, 3)
        
        concentration = model.predict_concentration(
            x, 
            velocity=diffusion_params['velocity'],
            diffusion_coeff=diffusion_params['diffusion_coeff'],
            source_term=diffusion_params['source_term']
        )
        
        assert concentration.shape == (batch_size, 1)
        assert not torch.isnan(concentration).any()
        assert not torch.isinf(concentration).any()
    
    def test_compute_time_evolution(self, model, diffusion_params):
        """Test time evolution computation."""
        batch_size = 5
        num_points = 100
        num_times = 5
        
        x_initial = torch.randn(batch_size, num_points)
        t_span = torch.linspace(0, 1, num_times)
        
        c_evolution = model.compute_time_evolution(
            x_initial, t_span,
            velocity=diffusion_params['velocity'],
            diffusion_coeff=diffusion_params['diffusion_coeff'],
            source_term=diffusion_params['source_term'],
            dt=0.01
        )
        
        assert c_evolution.shape == (num_times, batch_size, num_points)
        assert not torch.isnan(c_evolution).any()
        assert not torch.isinf(c_evolution).any()
    
    def test_check_convergence(self, model):
        """Test convergence checking."""
        # Test with insufficient history
        loss_history_short = [1.0, 0.9, 0.8]
        result = model.check_convergence(loss_history_short)
        assert not result['converged']
        assert result['reason'] == "Insufficient history"
        
        # Test with convergence
        loss_history_conv = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        result = model.check_convergence(loss_history_conv)
        assert result['converged']
        assert result['reason'] == "Loss improved by 0.20 below tolerance 1e-06"
        assert result['current_loss'] == 0.5
        assert result['iterations'] == 6
        
        # Test with no convergence
        loss_history_no_conv = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        result = model.check_convergence(loss_history_no_conv)
        assert not result['converged']
        assert "above tolerance" in result['reason']
    
    @patch('torch.save')
    def test_save_model(self, mock_save, model):
        """Test model saving."""
        filepath = "test_diffusion_model.pth"
        model.save_model(filepath)
        
        # Check that torch.save was called
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        
        # Check that saved dictionary contains expected keys
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
        
        filepath = "test_diffusion_model.pth"
        loaded_model = DiffusionPINN.load_model(filepath)
        
        # Check that torch.load was called
        mock_load.assert_called_once_with(filepath, map_location=None)
        
        # Check model parameters
        assert loaded_model.input_dim == model_config['input_dim']
        assert loaded_model.output_dim == model_config['output_dim']
        assert loaded_model.hidden_layers == model_config['hidden_layers']
        assert loaded_model.activation_name == model_config['activation']
    
    @patch('ai_pinn.models.pinn.diffusion_pinn.load_config')
    def test_from_config(self, mock_load_config, model_config):
        """Test model creation from configuration file."""
        mock_load_config.return_value = {
            'model': model_config
        }
        
        filepath = "test_config.yaml"
        model = DiffusionPINN.from_config(filepath)
        
        # Check that load_config was called
        mock_load_config.assert_called_once_with(filepath)
        
        # Check model parameters
        assert model.input_dim == model_config['input_dim']
        assert model.output_dim == model_config['output_dim']
        assert model.hidden_layers == model_config['hidden_layers']
        assert model.activation_name == model_config['activation']