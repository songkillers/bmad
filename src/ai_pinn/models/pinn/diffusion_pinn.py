"""Diffusion PINN for solving 2D convection-diffusion equations."""

from typing import Dict, Any, Optional
import torch
import torch.nn as nn

from .base_pinn import BasePINN


class DiffusionPINN(BasePINN):
    """
    Physics-Informed Neural Network for 2D convection-diffusion equations.
    
    This class implements a PINN to solve the 2D convection-diffusion equation:
    ∂C/∂t + v·∇C = D∇²C
    
    where:
    - C: concentration field
    - v: velocity field (vx, vy)
    - D: diffusion coefficient
    - t: time
    - x, y: spatial coordinates
    """
    
    def __init__(
        self,
        input_dim: int = 3,  # x, y, t
        output_dim: int = 1,  # concentration
        hidden_layers: Optional[list] = None,
        activation: str = "tanh",
        device: Optional[torch.device] = None
    ) -> None:
        """Initialize DiffusionPINN.
        
        Args:
            input_dim: Dimension of input space (default: 3 for x, y, t)
            output_dim: Dimension of output space (default: 1 for concentration)
            hidden_layers: List of hidden layer sizes (default: [50, 50, 50])
            activation: Activation function name (default: "tanh")
            device: Device to run the model on (auto-detected if None)
        """
        if hidden_layers is None:
            hidden_layers = [50, 50, 50]
            
        super(DiffusionPINN, self).__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_layers=hidden_layers,
            activation=activation,
            device=device
        )
    
    def compute_physics_loss(
        self, 
        x: torch.Tensor, 
        velocity: Optional[torch.Tensor] = None,
        diffusion_coeff: Optional[float] = None,
        source_term: Optional[torch.Tensor] = None,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Compute the physics-based loss for the 2D convection-diffusion equation.
        
        The physics equation is:
        ∂C/∂t + v·∇C = D∇²C
        
        Rearranged as a loss function:
        L_physics = ||∂C/∂t + v·∇C - D∇²C||²
        
        Args:
            x: Input tensor of shape (batch_size, 3) containing [x, y, t]
            velocity: Velocity field tensor of shape (batch_size, 2) containing [vx, vy]
            diffusion_coeff: Diffusion coefficient D
            source_term: Source term tensor of shape (batch_size, 1)
            **kwargs: Additional parameters (unused in this implementation)
            
        Returns:
            Physics loss tensor
        """
        batch_size = x.shape[0]
        
        # Extract coordinates
        x_coord = x[:, 0:1]  # x coordinate
        y_coord = x[:, 1:2]  # y coordinate
        t_coord = x[:, 2:3]  # time
        
        # Set default values if not provided
        if velocity is None:
            velocity = torch.zeros(batch_size, 2, device=x.device)
        else:
            velocity = velocity
            
        if diffusion_coeff is None:
            diffusion_coeff = 1.0  # Default diffusion coefficient
        else:
            diffusion_coeff = diffusion_coeff
            
        if source_term is None:
            source_term = torch.zeros(batch_size, 1, device=x.device)
        else:
            source_term = source_term
        
        # Enable gradient computation
        x.requires_grad_(True)
        
        # Predict concentration
        c_pred = self.forward(x)
        
        # Compute gradients with memory optimization
        # Use retain_graph=False for first-order derivatives to reduce memory usage
        dc_dt = torch.autograd.grad(c_pred, t_coord, torch.ones_like(t_coord),
                                      create_graph=True, retain_graph=False)[0]
        dc_dx = torch.autograd.grad(c_pred, x_coord, torch.ones_like(x_coord),
                                      create_graph=True, retain_graph=False)[0]
        dc_dy = torch.autograd.grad(c_pred, y_coord, torch.ones_like(y_coord),
                                      create_graph=True, retain_graph=False)[0]
        
        # Compute second derivatives with memory optimization
        # Only create_graph for the last derivative in the chain
        d2c_dx2 = torch.autograd.grad(dc_dx, x_coord, torch.ones_like(x_coord),
                                       create_graph=True, retain_graph=False)[0]
        d2c_dy2 = torch.autograd.grad(dc_dy, y_coord, torch.ones_like(y_coord),
                                       create_graph=True, retain_graph=False)[0]
        
        # Convection term: v·∇C
        # velocity is already handled above (lines 88-91), so it's guaranteed to be a tensor here
        assert velocity is not None, "velocity should be a tensor at this point"
        convection = velocity[:, 0:1] * dc_dx + velocity[:, 1:2] * dc_dy
        
        # Diffusion term: D∇²C
        diffusion = diffusion_coeff * (d2c_dx2 + d2c_dy2)
        
        # Source term
        if source_term is not None:
            source = source_term.squeeze()
        else:
            source = torch.zeros(batch_size, 1, device=x.device)
        
        # Physics residual
        residual = dc_dt + convection - diffusion + source
        
        # Physics loss (MSE of residual)
        physics_loss = torch.mean(residual**2)
        
        return physics_loss
    
    def compute_mass_conservation_loss(
        self,
        x: torch.Tensor,
        velocity: Optional[torch.Tensor] = None,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Compute mass conservation loss to ensure physical consistency.
        
        Args:
            x: Input tensor of shape (batch_size, 3) containing [x, y, t]
            velocity: Velocity field tensor of shape (batch_size, 2) containing [vx, vy]
            **kwargs: Additional parameters
            
        Returns:
            Mass conservation loss tensor
        """
        batch_size = x.shape[0]
        
        # Extract coordinates
        x_coord = x[:, 0:1]  # x coordinate
        y_coord = x[:, 1:2]  # y coordinate
        
        # Set default velocity if not provided
        if velocity is None:
            vx = torch.zeros(batch_size, device=x.device)
            vy = torch.zeros(batch_size, device=x.device)
        else:
            vx = velocity[:, 0:1]
            vy = velocity[:, 1:2]
        
        # Enable gradient computation
        x.requires_grad_(True)
        
        # Predict concentration
        c_pred = self.forward(x)
        
        # Compute gradients for divergence with memory optimization
        dc_dx = torch.autograd.grad(c_pred, x_coord, torch.ones_like(x_coord),
                                      create_graph=True, retain_graph=False)[0]
        dc_dy = torch.autograd.grad(c_pred, y_coord, torch.ones_like(y_coord),
                                      create_graph=True, retain_graph=False)[0]
        
        # Compute divergence of velocity field: ∇·v with memory optimization
        div_v = torch.autograd.grad(vx, x_coord, torch.ones_like(x_coord),
                                   create_graph=True, retain_graph=False)[0] + \
               torch.autograd.grad(vy, y_coord, torch.ones_like(y_coord),
                                   create_graph=True, retain_graph=False)[0]
        
        # Mass conservation residual: ∂C/∂t + ∇·(vC) = source
        mass_residual = div_v * c_pred
        
        # Mass conservation loss (MSE of residual)
        mass_loss = torch.mean(mass_residual**2)
        
        return mass_loss
    
    def compute_total_loss(
        self,
        x_collocation: torch.Tensor,
        x_boundary: torch.Tensor,
        u_boundary: torch.Tensor,
        velocity: Optional[torch.Tensor] = None,
        diffusion_coeff: Optional[float] = None,
        source_term: Optional[torch.Tensor] = None,
        lambda_physics: float = 1.0,
        lambda_boundary: float = 1.0,
        lambda_mass: float = 0.1,  # Small weight for mass conservation
        **kwargs: Any
    ) -> Dict[str, torch.Tensor]:
        """
        Compute the total loss combining physics, boundary, and mass conservation terms.
        
        Args:
            x_collocation: Collocation points for physics loss
            x_boundary: Boundary points
            u_boundary: Boundary values
            velocity: Velocity field
            diffusion_coeff: Diffusion coefficient
            source_term: Source term
            lambda_physics: Weight for physics loss
            lambda_boundary: Weight for boundary loss
            lambda_mass: Weight for mass conservation loss
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing individual and total losses
        """
        physics_loss = self.compute_physics_loss(
            x_collocation, velocity, diffusion_coeff, source_term, **kwargs
        )
        boundary_loss = self.compute_boundary_loss(x_boundary, u_boundary, **kwargs)
        mass_loss = self.compute_mass_conservation_loss(x_boundary, velocity, **kwargs)
        
        total_loss = (lambda_physics * physics_loss + 
                     lambda_boundary * boundary_loss + 
                     lambda_mass * mass_loss)
        
        return {
            "total_loss": total_loss,
            "physics_loss": physics_loss,
            "boundary_loss": boundary_loss,
            "mass_conservation_loss": mass_loss
        }
    
    def predict_concentration(
        self,
        x: torch.Tensor,
        velocity: Optional[torch.Tensor] = None,
        diffusion_coeff: Optional[float] = None,
        source_term: Optional[torch.Tensor] = None,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Predict concentration field.
        
        Args:
            x: Input tensor of shape (batch_size, 3) containing [x, y, t]
            velocity: Velocity field
            diffusion_coeff: Diffusion coefficient
            source_term: Source term
            **kwargs: Additional parameters
            
        Returns:
            Predicted concentration tensor
        """
        return self.forward(x)
    
    def compute_time_evolution(
        self,
        x_initial: torch.Tensor,
        t_span: torch.Tensor,
        velocity: Optional[torch.Tensor] = None,
        diffusion_coeff: Optional[float] = None,
        source_term: Optional[torch.Tensor] = None,
        dt: float = 0.01,
        **kwargs: Any
    ) -> torch.Tensor:
        """
        Compute time evolution of concentration field.
        
        Args:
            x_initial: Initial concentration field
            t_span: Time points to evaluate
            velocity: Velocity field
            diffusion_coeff: Diffusion coefficient
            source_term: Source term
            dt: Time step size
            **kwargs: Additional parameters
            
        Returns:
            Time-evolved concentration field
        """
        batch_size = x_initial.shape[0]
        num_points = x_initial.shape[1]
        num_times = len(t_span)
        
        # Initialize concentration field
        c_current = x_initial.clone()
        
        # Store evolution history
        c_evolution = torch.zeros(num_times, batch_size, num_points, device=x_initial.device)
        c_evolution[0] = c_current
        
        # Time evolution loop
        for i in range(1, num_times):
            # Create input for current time
            t_current = torch.full((batch_size, 1), t_span[i], device=x_initial.device)
            x_current = torch.cat([
                x_initial[:, 0:2],  # x, y coordinates
                t_current,           # time
            ], dim=1)
            
            # Predict next time step
            c_next = self.predict_concentration(
                x_current, velocity, diffusion_coeff, source_term, **kwargs
            )
            
            # Simple explicit time integration (for demonstration)
            c_current = c_current + dt * c_next
            
            c_evolution[i] = c_current
        
        return c_evolution
    
    def check_convergence(
        self,
        loss_history: list,
        tolerance: float = 1e-6,
        patience: int = 10,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Check for convergence based on loss history.
        
        Args:
            loss_history: History of loss values
            tolerance: Convergence tolerance
            patience: Number of iterations to wait for improvement
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with convergence status and metrics
        """
        if len(loss_history) < patience:
            return {
                "converged": False,
                "reason": "Insufficient history",
                "current_loss": loss_history[-1] if loss_history else None,
                "iterations": len(loss_history)
            }
        
        recent_losses = loss_history[-patience:]
        
        # Check if loss is decreasing
        if len(recent_losses) < 2:
            return {
                "converged": False,
                "reason": "Insufficient recent history",
                "current_loss": loss_history[-1] if loss_history else None,
                "iterations": len(loss_history)
            }
        
        # Check if loss improvement is below tolerance
        loss_improvement = abs(recent_losses[0] - recent_losses[-1])
        if loss_improvement < tolerance:
            return {
                "converged": True,
                "reason": f"Loss improved by {loss_improvement:.2e} below tolerance",
                "current_loss": loss_history[-1],
                "iterations": len(loss_history)
            }
        
        return {
            "converged": False,
            "reason": f"Loss improvement {loss_improvement:.2e} above tolerance {tolerance}",
            "current_loss": loss_history[-1],
            "iterations": len(loss_history)
        }