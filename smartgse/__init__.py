"""
SmartGSE - Sustainability Report and Carbon Tax Report Platform

This package provides tools and templates for generating comprehensive
sustainability reports and carbon tax reports to support ESG compliance.
"""

__version__ = "1.0.0"
__author__ = "SmartGSE Team"

# Import core models - these are always available
from .core.models import EmissionData, SustainabilityMetrics, CarbonTaxData

# Import reports conditionally to avoid circular imports
try:
    from .reports.sustainability import SustainabilityReport
    from .reports.carbon_tax import CarbonTaxReport
    
    __all__ = [
        "EmissionData",
        "SustainabilityMetrics", 
        "CarbonTaxData",
        "SustainabilityReport",
        "CarbonTaxReport",
    ]
except ImportError:
    # If reports can't be imported, provide core models only
    __all__ = [
        "EmissionData",
        "SustainabilityMetrics", 
        "CarbonTaxData",
    ]