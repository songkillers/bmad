"""Integration tests for DiffusionPINN."""

import pytest
import torch
import numpy as np
import tempfile
import os

from ai_pinn.models.pinn.diffusion_pinn import DiffusionPINN
from ai_pinn.utils.config_loader import load_config


class TestDiffusionPINNIntegration:
    """Integration tests for DiffusionPINN."""
    
    @pytest.fixture
    def model_config(self):
        """Model configuration fixture."""
        return {
            'input_dim': 3,  # x, y, t
            'output_dim': 1,  # concentration
            'hidden_layers': [20, 20, 20],  # Smaller for faster testing
            'activation': 'tanh'
        }
    
    @pytest.fixture
    def model(self, model_config):
        """Model fixture."""
        return DiffusionPINN(**model_config)
    
    @pytest.fixture
    def training_data(self):
        """Generate training data for integration tests."""
        # Domain parameters
        x_min, x_max = 0.0, 1.0
        y_min, y_max = 0.0, 1.0
        t_min, t_max = 0.0, 1.0
        
        # Number of points
        n_collocation = 100
        n_boundary = 50
        
        # Generate collocation points (interior points)
        x_collocation = torch.rand(n_collocation, 3)
        x_collocation[:, 0] = x_collocation[:, 0] * (x_max - x_min) + x_min  # x
        x_collocation[:, 1] = x_collocation[:, 1] * (y_max - y_min) + y_min  # y
        x_collocation[:, 2] = x_collocation[:, 2] * (t_max - t_min) + t_min  # t
        
        # Generate boundary points
        x_boundary = torch.rand(n_boundary, 3)
        
        # Randomly select which boundary
        boundary_type = torch.randint(0, 4, (n_boundary,))
        
        for i in range(n_boundary):
            if boundary_type[i] == 0:  # Left boundary (x = x_min)
                x_boundary[i, 0] = x_min
                x_boundary[i, 1] = torch.rand(1) * (y_max - y_min) + y_min
            elif boundary_type[i] == 1:  # Right boundary (x = x_max)
                x_boundary[i, 0] = x_max
                x_boundary[i, 1] = torch.rand(1) * (y_max - y_min) + y_min
            elif boundary_type[i] == 2:  # Bottom boundary (y = y_min)
                x_boundary[i, 0] = torch.rand(1) * (x_max - x_min) + x_min
                x_boundary[i, 1] = y_min
            else:  # Top boundary (y = y_max)
                x_boundary[i, 0] = torch.rand(1) * (x_max - x_min) + x_min
                x_boundary[i, 1] = y_max
            
            x_boundary[i, 2] = torch.rand(1) * (t_max - t_min) + t_min  # Time
        
        # Generate boundary values (Dirichlet boundary conditions)
        u_boundary = torch.zeros(n_boundary, 1)  # Zero concentration at boundaries
        
        # Physical parameters
        velocity = torch.ones(n_collocation, 2) * 0.1  # Constant velocity field
        diffusion_coeff = 0.01
        source_term = torch.zeros(n_collocation, 1)
        
        return {
            'x_collocation': x_collocation,
            'x_boundary': x_boundary,
            'u_boundary': u_boundary,
            'velocity': velocity,
            'diffusion_coeff': diffusion_coeff,
            'source_term': source_term
        }
    
    def test_end_to_end_training(self, model, training_data):
        """Test end-to-end training process."""
        # Setup optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Training parameters
        epochs = 10  # Small number for testing
        loss_history = []
        
        # Training loop
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Compute losses
            losses = model.compute_total_loss(
                training_data['x_collocation'],
                training_data['x_boundary'],
                training_data['u_boundary'],
                velocity=training_data['velocity'],
                diffusion_coeff=training_data['diffusion_coeff'],
                source_term=training_data['source_term']
            )
            
            # Backpropagation
            losses['total_loss'].backward()
            optimizer.step()
            
            # Record loss
            loss_history.append(losses['total_loss'].item())
            
            # Check that loss is finite
            assert torch.isfinite(losses['total_loss'])
        
        # Check that loss decreased
        assert loss_history[-1] < loss_history[0]
        
        # Check convergence
        convergence_result = model.check_convergence(loss_history)
        assert isinstance(convergence_result, dict)
        assert 'converged' in convergence_result
        assert 'reason' in convergence_result
        assert 'current_loss' in convergence_result
        assert 'iterations' in convergence_result
    
    def test_model_save_load_workflow(self, model, training_data):
        """Test model saving and loading workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model.pth")
            
            # Save model
            model.save_model(model_path)
            assert os.path.exists(model_path)
            
            # Load model
            loaded_model = DiffusionPINN.load_model(model_path)
            
            # Check that models have same parameters
            for (name1, param1), (name2, param2) in zip(
                model.named_parameters(), loaded_model.named_parameters()
            ):
                assert name1 == name2
                assert torch.allclose(param1, param2)
            
            # Test that loaded model produces same predictions
            x_test = training_data['x_collocation'][:10]
            
            with torch.no_grad():
                pred1 = model(x_test)
                pred2 = loaded_model(x_test)
            
            assert torch.allclose(pred1, pred2)
    
    def test_time_evolution_integration(self, model, training_data):
        """Test time evolution integration."""
        # Initial concentration field
        batch_size = 5
        num_points = 20
        x_initial = torch.zeros(batch_size, num_points)
        
        # Set initial condition (e.g., Gaussian pulse in the center)
        for i in range(batch_size):
            for j in range(num_points):
                x_pos = j / num_points
                x_initial[i, j] = torch.exp(-((x_pos - 0.5) ** 2) / 0.01)
        
        # Time span
        t_span = torch.linspace(0, 0.1, 5)
        
        # Compute time evolution
        c_evolution = model.compute_time_evolution(
            x_initial, t_span,
            velocity=training_data['velocity'][:batch_size],
            diffusion_coeff=training_data['diffusion_coeff'],
            source_term=training_data['source_term'][:batch_size],
            dt=0.001
        )
        
        # Check output shape
        assert c_evolution.shape == (len(t_span), batch_size, num_points)
        
        # Check that values are finite
        assert torch.all(torch.isfinite(c_evolution))
        
        # Check that concentration is non-negative
        assert torch.all(c_evolution >= 0)
    
    def test_config_loading_integration(self):
        """Test integration with configuration loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.yaml")
            
            # Create test config
            config = {
                'model': {
                    'input_dim': 3,
                    'output_dim': 1,
                    'hidden_layers': [30, 30],
                    'activation': 'tanh'
                },
                'training': {
                    'epochs': 100,
                    'learning_rate': 0.001
                }
            }
            
            # Save config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            
            # Load model from config
            model = DiffusionPINN.from_config(config_path)
            
            # Check model parameters
            assert model.input_dim == 3
            assert model.output_dim == 1
            assert model.hidden_layers == [30, 30]
            assert model.activation_name == 'tanh'
    
    def test_boundary_conditions_integration(self, model):
        """Test integration with boundary conditions."""
        # Generate test data with specific boundary conditions
        n_points = 50
        
        # Create boundary points on all four sides
        x_boundary = torch.zeros(n_points, 3)
        u_boundary = torch.zeros(n_points, 1)
        
        for i in range(n_points):
            side = i % 4
            
            if side == 0:  # Left boundary (x = 0)
                x_boundary[i, 0] = 0.0
                x_boundary[i, 1] = torch.rand(1)
                u_boundary[i, 0] = 0.0  # Dirichlet BC
            elif side == 1:  # Right boundary (x = 1)
                x_boundary[i, 0] = 1.0
                x_boundary[i, 1] = torch.rand(1)
                u_boundary[i, 0] = 0.0  # Dirichlet BC
            elif side == 2:  # Bottom boundary (y = 0)
                x_boundary[i, 0] = torch.rand(1)
                x_boundary[i, 1] = 0.0
                u_boundary[i, 0] = 1.0  # Dirichlet BC
            else:  # Top boundary (y = 1)
                x_boundary[i, 0] = torch.rand(1)
                x_boundary[i, 1] = 1.0
                u_boundary[i, 0] = 0.0  # Dirichlet BC
            
            x_boundary[i, 2] = torch.rand(1)  # Random time
        
        # Test boundary loss computation
        boundary_loss = model.compute_boundary_loss(x_boundary, u_boundary)
        
        # Check that loss is finite and non-negative
        assert torch.isfinite(boundary_loss)
        assert boundary_loss.item() >= 0
        
        # Test that model respects boundary conditions (approximately)
        with torch.no_grad():
            pred = model(x_boundary)
            # Predictions should be close to boundary values
            assert torch.mean(torch.abs(pred - u_boundary)) < 1.0  # Allow some tolerance