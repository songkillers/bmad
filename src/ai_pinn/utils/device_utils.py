"""Device utilities for AI PINN."""

import torch

def get_device() -> torch.device:
    """Get the best available device for computation.
    
    Returns:
        torch.device: The best available device (GPU if available, otherwise CPU)
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def set_device(device: str) -> torch.device:
    """Set a specific device for computation.
    
    Args:
        device: Device string ('cpu', 'cuda', 'cuda:0', 'mps', etc.)
        
    Returns:
        torch.device: The specified device
    """
    return torch.device(device)


def get_device_info(device: torch.device) -> dict:
    """Get information about the specified device.
    
    Args:
        device: The device to query
        
    Returns:
        dict: Device information
    """
    info = {
        "device": str(device),
        "type": device.type
    }
    
    if device.type == "cuda":
        info.update({
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda,
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(device.index) if device.index is not None else "Unknown",
            "memory_allocated": torch.cuda.memory_allocated(device) / (1024 ** 3),  # GB
            "memory_reserved": torch.cuda.memory_reserved(device) / (1024 ** 3)  # GB
        })
    elif device.type == "mps":
        info.update({
            "mps_available": hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        })
    
    return info