"""
Core data models for ESG reporting and carbon tax calculations.
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator


class EmissionScope(str, Enum):
    """Greenhouse gas emission scopes as defined by GHG Protocol."""
    SCOPE_1 = "scope_1"  # Direct emissions
    SCOPE_2 = "scope_2"  # Indirect energy emissions
    SCOPE_3 = "scope_3"  # Other indirect emissions


class EmissionSource(str, Enum):
    """Common sources of greenhouse gas emissions."""
    FUEL_COMBUSTION = "fuel_combustion"
    ELECTRICITY = "electricity"
    HEATING = "heating"
    TRANSPORTATION = "transportation"
    WASTE = "waste"
    WATER = "water"
    REFRIGERANTS = "refrigerants"
    BUSINESS_TRAVEL = "business_travel"
    EMPLOYEE_COMMUTING = "employee_commuting"
    SUPPLY_CHAIN = "supply_chain"
    OTHER = "other"


class SustainabilityCategory(str, Enum):
    """ESG categories for sustainability reporting."""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


@dataclass
class EmissionData:
    """Data structure for greenhouse gas emission records."""
    
    source: EmissionSource
    scope: EmissionScope
    co2_equivalent_tonnes: float
    reporting_period_start: date
    reporting_period_end: date
    activity_data: float  # e.g., kWh, liters, km
    activity_unit: str  # e.g., "kWh", "liters", "km"
    emission_factor: float  # CO2e per activity unit
    location: Optional[str] = None
    facility: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate data consistency."""
        if self.reporting_period_start > self.reporting_period_end:
            raise ValueError("Start date must be before end date")
        if self.co2_equivalent_tonnes < 0:
            raise ValueError("CO2 equivalent must be non-negative")
        if self.activity_data < 0:
            raise ValueError("Activity data must be non-negative")


@dataclass
class SustainabilityMetrics:
    """Data structure for ESG sustainability metrics."""
    
    category: SustainabilityCategory
    metric_name: str
    metric_value: Union[float, int, str]
    metric_unit: str
    reporting_period_start: date
    reporting_period_end: date
    target_value: Optional[Union[float, int]] = None
    benchmark_value: Optional[Union[float, int]] = None
    description: Optional[str] = None
    data_source: Optional[str] = None
    calculation_method: Optional[str] = None
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def progress_to_target(self) -> Optional[float]:
        """Calculate progress towards target as percentage."""
        if self.target_value is None or not isinstance(self.metric_value, (int, float)):
            return None
        try:
            return (float(self.metric_value) / float(self.target_value)) * 100
        except (ValueError, ZeroDivisionError):
            return None


@dataclass
class CarbonTaxData:
    """Data structure for carbon tax calculations."""
    
    jurisdiction: str
    tax_rate_per_tonne: float  # Currency per tonne CO2e
    currency: str
    emissions_covered: List[EmissionData]
    reporting_period_start: date
    reporting_period_end: date
    exemptions: Dict[str, float] = field(default_factory=dict)
    credits: Dict[str, float] = field(default_factory=dict)
    penalties: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_emissions_tonnes(self) -> float:
        """Calculate total emissions covered by tax."""
        return sum(emission.co2_equivalent_tonnes for emission in self.emissions_covered)
    
    @property
    def gross_tax_liability(self) -> float:
        """Calculate gross carbon tax liability."""
        return self.total_emissions_tonnes * self.tax_rate_per_tonne
    
    @property
    def total_exemptions(self) -> float:
        """Calculate total exemption value."""
        return sum(self.exemptions.values())
    
    @property
    def total_credits(self) -> float:
        """Calculate total credit value."""
        return sum(self.credits.values())
    
    @property
    def total_penalties(self) -> float:
        """Calculate total penalty value."""
        return sum(self.penalties.values())
    
    @property
    def net_tax_liability(self) -> float:
        """Calculate net carbon tax liability after exemptions, credits, and penalties."""
        return (self.gross_tax_liability 
                - self.total_exemptions 
                - self.total_credits 
                + self.total_penalties)


class OrganizationProfile(BaseModel):
    """Organization profile for ESG reporting."""
    
    name: str = Field(..., description="Organization name")
    industry: str = Field(..., description="Industry sector")
    size: str = Field(..., description="Organization size (e.g., 'Large', 'SME')")
    headquarters_location: str = Field(..., description="Primary location")
    reporting_year: int = Field(..., description="Reporting year")
    fiscal_year_start: date = Field(..., description="Fiscal year start date")
    fiscal_year_end: date = Field(..., description="Fiscal year end date")
    employees_count: Optional[int] = Field(None, description="Number of employees")
    revenue: Optional[float] = Field(None, description="Annual revenue")
    revenue_currency: Optional[str] = Field(None, description="Revenue currency")
    facilities: List[str] = Field(default_factory=list, description="List of facilities")
    
    @validator('reporting_year')
    def validate_reporting_year(cls, v):
        current_year = datetime.now().year
        if v < 1990 or v > current_year + 1:
            raise ValueError(f'Reporting year must be between 1990 and {current_year + 1}')
        return v
    
    @validator('fiscal_year_end')
    def validate_fiscal_year(cls, v, values):
        if 'fiscal_year_start' in values and v <= values['fiscal_year_start']:
            raise ValueError('Fiscal year end must be after fiscal year start')
        return v


class ReportingStandard(str, Enum):
    """Supported ESG reporting standards."""
    GRI = "gri"  # Global Reporting Initiative
    SASB = "sasb"  # Sustainability Accounting Standards Board
    TCFD = "tcfd"  # Task Force on Climate-related Financial Disclosures
    CDP = "cdp"  # Carbon Disclosure Project
    UNGC = "ungc"  # UN Global Compact
    ISO14001 = "iso14001"  # Environmental Management Systems
    CUSTOM = "custom"


@dataclass
class ReportConfiguration:
    """Configuration for report generation."""
    
    organization: OrganizationProfile
    standards: List[ReportingStandard]
    include_executive_summary: bool = True
    include_methodology: bool = True
    include_verification_statement: bool = False
    language: str = "en"
    template_style: str = "standard"
    output_format: str = "pdf"  # pdf, html, docx
    custom_sections: List[str] = field(default_factory=list)
    branding: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)