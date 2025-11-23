"""Base PINN class for physics-informed neural networks."""

from typing import Dict, List, Optional, Union, Callable, Any
import torch
import torch.nn as nn
from abc import ABC, abstractmethod

from ...utils.device_utils import get_device
from ...config.loader import ConfigLoader


class BasePINN(nn.Module, ABC):
    """
    Base class for Physics-Informed Neural Networks (PINNs).
    
    This class provides the foundation for implementing PINNs that solve
    differential equations by incorporating physical constraints into the loss function.
    
    Attributes:
        input_dim (int): Dimension of input space (e.g., 3 for x, y, t)
        output_dim (int): Dimension of output space (e.g., 1 for concentration)
        hidden_layers (List[int]): List of hidden layer sizes
        activation (str): Activation function name
        device (torch.device): Device to run the model on
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_layers: List[int],
        activation: str = "tanh",
        device: Optional[torch.device] = None
    ) -> None:
        """Initialize the BasePINN.
        
        Args:
            input_dim: Dimension of input space
            output_dim: Dimension of output space
            hidden_layers: List of hidden layer sizes
            activation: Activation function name (tanh, relu, sigmoid)
            device: Device to run the model on (auto-detected if None)
        """
        super(BasePINN, self).__init__()
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layers = hidden_layers
        self.activation_name = activation
        self.device = device or get_device()
        
        # Build network layers
        self.layers = self._build_layers()
        self.activation_fn = self._get_activation_function(activation)
        
        # Move model to device
        self.to(self.device)
    
    def _build_layers(self) -> nn.ModuleList:
        """Build the neural network layers.
        
        Returns:
            ModuleList containing all network layers
        """
        layers = []
        layer_sizes = [self.input_dim] + self.hidden_layers + [self.output_dim]
        
        for i in range(len(layer_sizes) - 1):
            layers.append(nn.Linear(layer_sizes[i], layer_sizes[i + 1]))
        
        return nn.ModuleList(layers)
    
    def _get_activation_function(self, activation: str) -> nn.Module:
        """Get the activation function by name.
        
        Args:
            activation: Name of the activation function
            
        Returns:
            Activation function module
            
        Raises:
            ValueError: If activation function is not supported
        """
        activation_functions = {
            "tanh": nn.Tanh(),
            "relu": nn.ReLU(),
            "sigmoid": nn.Sigmoid(),
            "leaky_relu": nn.LeakyReLU(0.2),
            "elu": nn.ELU(),
            "swish": nn.SiLU()  # SiLU is also known as Swish
        }
        
        if activation.lower() not in activation_functions:
            raise ValueError(
                f"Activation function '{activation}' not supported. "
                f"Supported functions: {list(activation_functions.keys())}"
            )
        
        return activation_functions[activation.lower()]
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Output tensor of shape (batch_size, output_dim)
        """
        # Ensure input is on the correct device
        x = x.to(self.device)
        
        # Pass through all layers except the last one with activation
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = self.activation_fn(x)
        
        # Last layer without activation (regression output)
        x = self.layers[-1](x)
        
        return x
    
    @abstractmethod
    def compute_physics_loss(
        self, 
        x: torch.Tensor, 
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Compute the physics-based loss component.
        
        This method must be implemented by subclasses to encode the specific
        differential equation constraints.
        
        Args:
            x: Input coordinates
            **kwargs: Additional parameters for physics computation
            
        Returns:
            Physics loss tensor
        """
        pass
    
    def compute_boundary_loss(
        self, 
        x_boundary: torch.Tensor, 
        u_boundary: torch.Tensor,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Compute the boundary condition loss component.
        
        Args:
            x_boundary: Boundary coordinates
            u_boundary: Boundary values
            **kwargs: Additional parameters for boundary computation
            
        Returns:
            Boundary loss tensor
        """
        u_pred = self.forward(x_boundary)
        boundary_loss = torch.mean((u_pred - u_boundary) ** 2)
        return boundary_loss
    
    def compute_total_loss(
        self,
        x_collocation: torch.Tensor,
        x_boundary: torch.Tensor,
        u_boundary: torch.Tensor,
        lambda_physics: float = 1.0,
        lambda_boundary: float = 1.0,
        **kwargs: Any
    ) -> Dict[str, torch.Tensor]:
        """
        Compute the total loss combining physics and boundary components.
        
        Args:
            x_collocation: Collocation points for physics loss
            x_boundary: Boundary points
            u_boundary: Boundary values
            lambda_physics: Weight for physics loss
            lambda_boundary: Weight for boundary loss
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing individual and total losses
        """
        physics_loss = self.compute_physics_loss(x_collocation, **kwargs)
        boundary_loss = self.compute_boundary_loss(x_boundary, u_boundary, **kwargs)
        
        total_loss = lambda_physics * physics_loss + lambda_boundary * boundary_loss
        
        return {
            "total_loss": total_loss,
            "physics_loss": physics_loss,
            "boundary_loss": boundary_loss
        }
    
    def save_model(self, filepath: str) -> None:
        """Save the model state.
        
        Args:
            filepath: Path to save the model
        """
        torch.save({
            'model_state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'hidden_layers': self.hidden_layers,
            'activation': self.activation_name
        }, filepath)
    
    @classmethod
    def load_model(cls, filepath: str, device: Optional[torch.device] = None) -> 'BasePINN':
        """Load a model from file.
        
        Args:
            filepath: Path to the saved model
            device: Device to load the model on
            
        Returns:
            Loaded model instance
        """
        checkpoint = torch.load(filepath, map_location=device)
        
        # Create model instance with saved parameters
        model = cls(
            input_dim=checkpoint['input_dim'],
            output_dim=checkpoint['output_dim'],
            hidden_layers=checkpoint['hidden_layers'],
            activation=checkpoint['activation']
        )
        
        # Load state dict
        model.load_state_dict(checkpoint['model_state_dict'])
        
        return model
    
    @classmethod
    def from_config(cls, config_path: str, device: Optional[torch.device] = None) -> 'BasePINN':
        """Create model from configuration file.
        
        Args:
            config_path: Path to configuration file
            device: Device to run the model on
            
        Returns:
            Model instance configured from file
        """
        loader = ConfigLoader(config_path)
        config = loader.load_config()
        
        return cls(
            input_dim=config['model']['input_dim'],
            output_dim=config['model']['output_dim'],
            hidden_layers=config['model']['hidden_layers'],
            activation=config['model'].get('activation', 'tanh'),
            device=device
        )
    
    def count_parameters(self) -> int:
        """Count the number of trainable parameters.
        
        Returns:
            Number of trainable parameters
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def summary(self) -> str:
        """Get a summary of the model architecture.
        
        Returns:
            String containing model summary
        """
        summary_lines = [
            f"Model: {self.__class__.__name__}",
            f"Input Dimension: {self.input_dim}",
            f"Output Dimension: {self.output_dim}",
            f"Hidden Layers: {self.hidden_layers}",
            f"Activation: {self.activation_name}",
            f"Device: {self.device}",
            f"Parameters: {self.count_parameters():,}"
        ]
        
        return "\n".join(summary_lines)