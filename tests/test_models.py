"""
Tests for core models.
"""

import pytest
from datetime import date, datetime
from smartgse.core.models import (
    EmissionData, SustainabilityMetrics, CarbonTaxData,
    OrganizationProfile, EmissionScope, EmissionSource, SustainabilityCategory
)


class TestEmissionData:
    """Test EmissionData model."""
    
    def test_emission_data_creation(self):
        """Test basic EmissionData creation."""
        emission = EmissionData(
            source=EmissionSource.ELECTRICITY,
            scope=EmissionScope.SCOPE_2,
            co2_equivalent_tonnes=125.5,
            reporting_period_start=date(2023, 1, 1),
            reporting_period_end=date(2023, 12, 31),
            activity_data=300000,
            activity_unit="kWh",
            emission_factor=0.000421
        )
        
        assert emission.source == EmissionSource.ELECTRICITY
        assert emission.scope == EmissionScope.SCOPE_2
        assert emission.co2_equivalent_tonnes == 125.5
        assert emission.activity_data == 300000
        assert emission.activity_unit == "kWh"
        assert emission.emission_factor == 0.000421
    
    def test_emission_data_validation(self):
        """Test EmissionData validation."""
        # Test negative CO2 equivalent
        with pytest.raises(ValueError, match="CO2 equivalent must be non-negative"):
            EmissionData(
                source=EmissionSource.ELECTRICITY,
                scope=EmissionScope.SCOPE_2,
                co2_equivalent_tonnes=-10,
                reporting_period_start=date(2023, 1, 1),
                reporting_period_end=date(2023, 12, 31),
                activity_data=300000,
                activity_unit="kWh",
                emission_factor=0.000421
            )
        
        # Test invalid date range
        with pytest.raises(ValueError, match="Start date must be before end date"):
            EmissionData(
                source=EmissionSource.ELECTRICITY,
                scope=EmissionScope.SCOPE_2,
                co2_equivalent_tonnes=125.5,
                reporting_period_start=date(2023, 12, 31),
                reporting_period_end=date(2023, 1, 1),
                activity_data=300000,
                activity_unit="kWh",
                emission_factor=0.000421
            )


class TestSustainabilityMetrics:
    """Test SustainabilityMetrics model."""
    
    def test_sustainability_metrics_creation(self):
        """Test basic SustainabilityMetrics creation."""
        metric = SustainabilityMetrics(
            category=SustainabilityCategory.ENVIRONMENTAL,
            metric_name="Energy Intensity",
            metric_value=2.5,
            metric_unit="MWh/employee",
            reporting_period_start=date(2023, 1, 1),
            reporting_period_end=date(2023, 12, 31),
            target_value=2.0
        )
        
        assert metric.category == SustainabilityCategory.ENVIRONMENTAL
        assert metric.metric_name == "Energy Intensity"
        assert metric.metric_value == 2.5
        assert metric.target_value == 2.0
    
    def test_progress_to_target_calculation(self):
        """Test progress to target calculation."""
        metric = SustainabilityMetrics(
            category=SustainabilityCategory.ENVIRONMENTAL,
            metric_name="Energy Intensity",
            metric_value=2.5,
            metric_unit="MWh/employee",
            reporting_period_start=date(2023, 1, 1),
            reporting_period_end=date(2023, 12, 31),
            target_value=2.0
        )
        
        assert metric.progress_to_target == 125.0  # (2.5 / 2.0) * 100
        
        # Test with no target
        metric_no_target = SustainabilityMetrics(
            category=SustainabilityCategory.SOCIAL,
            metric_name="Employee Satisfaction",
            metric_value="High",
            metric_unit="rating",
            reporting_period_start=date(2023, 1, 1),
            reporting_period_end=date(2023, 12, 31)
        )
        
        assert metric_no_target.progress_to_target is None


class TestCarbonTaxData:
    """Test CarbonTaxData model."""
    
    def test_carbon_tax_calculations(self):
        """Test carbon tax calculation properties."""
        # Create sample emission data
        emissions = [
            EmissionData(
                source=EmissionSource.ELECTRICITY,
                scope=EmissionScope.SCOPE_2,
                co2_equivalent_tonnes=100.0,
                reporting_period_start=date(2023, 1, 1),
                reporting_period_end=date(2023, 12, 31),
                activity_data=300000,
                activity_unit="kWh",
                emission_factor=0.000333
            ),
            EmissionData(
                source=EmissionSource.FUEL_COMBUSTION,
                scope=EmissionScope.SCOPE_1,
                co2_equivalent_tonnes=50.0,
                reporting_period_start=date(2023, 1, 1),
                reporting_period_end=date(2023, 12, 31),
                activity_data=20000,
                activity_unit="liters",
                emission_factor=0.0025
            )
        ]
        
        tax_data = CarbonTaxData(
            jurisdiction="California",
            tax_rate_per_tonne=25.0,
            currency="USD",
            emissions_covered=emissions,
            reporting_period_start=date(2023, 1, 1),
            reporting_period_end=date(2023, 12, 31),
            exemptions={"renewable_credit": 500.0},
            credits={"offset_purchases": 300.0},
            penalties={"late_filing": 100.0}
        )
        
        assert tax_data.total_emissions_tonnes == 150.0
        assert tax_data.gross_tax_liability == 3750.0  # 150 * 25
        assert tax_data.total_exemptions == 500.0
        assert tax_data.total_credits == 300.0
        assert tax_data.total_penalties == 100.0
        assert tax_data.net_tax_liability == 3050.0  # 3750 - 500 - 300 + 100


class TestOrganizationProfile:
    """Test OrganizationProfile model."""
    
    def test_organization_profile_creation(self):
        """Test OrganizationProfile creation and validation."""
        org = OrganizationProfile(
            name="Test Company",
            industry="Technology",
            size="Large",
            headquarters_location="New York",
            reporting_year=2023,
            fiscal_year_start=date(2023, 1, 1),
            fiscal_year_end=date(2023, 12, 31)
        )
        
        assert org.name == "Test Company"
        assert org.industry == "Technology"
        assert org.reporting_year == 2023
    
    def test_organization_profile_validation(self):
        """Test OrganizationProfile validation."""
        # Test invalid reporting year
        with pytest.raises(ValueError):
            OrganizationProfile(
                name="Test Company",
                industry="Technology",
                size="Large",
                headquarters_location="New York",
                reporting_year=1989,  # Too early
                fiscal_year_start=date(2023, 1, 1),
                fiscal_year_end=date(2023, 12, 31)
            )
        
        # Test invalid fiscal year dates
        with pytest.raises(ValueError):
            OrganizationProfile(
                name="Test Company",
                industry="Technology",
                size="Large",
                headquarters_location="New York",
                reporting_year=2023,
                fiscal_year_start=date(2023, 12, 31),
                fiscal_year_end=date(2023, 1, 1)  # End before start
            )