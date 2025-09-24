"""
SmartGSE - Sustainability Report and Carbon Tax Report Platform

This package provides tools and templates for generating comprehensive
sustainability reports and carbon tax reports to support ESG compliance.
"""

__version__ = "1.0.0"
__author__ = "SmartGSE Team"

from .core.models import EmissionData, SustainabilityMetrics, CarbonTaxData
from .reports.sustainability import SustainabilityReport
from .reports.carbon_tax import CarbonTaxReport

__all__ = [
    "EmissionData",
    "SustainabilityMetrics", 
    "CarbonTaxData",
    "SustainabilityReport",
    "CarbonTaxReport",
]