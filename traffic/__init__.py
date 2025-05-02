"""Traffic generation patterns package."""

from .base_traffic import BaseTrafficGenerator
from .random_traffic import RandomTrafficGenerator

# Future traffic generators would be imported here
# from .peak_traffic import PeakTrafficGenerator

__all__ = ['BaseTrafficGenerator', 'RandomTrafficGenerator']