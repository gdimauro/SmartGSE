"""
Calculation utilities for emissions and sustainability metrics.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import numpy as np

from ..core.models import EmissionData, SustainabilityMetrics, EmissionScope, EmissionSource


class EmissionCalculator:
    """Calculator for greenhouse gas emissions."""
    
    # Standard emission factors (tonnes CO2e per unit)
    EMISSION_FACTORS = {
        # Fuel combustion (per liter)
        "gasoline": 2.31e-3,
        "diesel": 2.68e-3,
        "natural_gas": 1.93e-3,  # per cubic meter
        "propane": 1.51e-3,
        
        # Electricity (per kWh) - varies by grid
        "electricity_us_avg": 4.21e-4,
        "electricity_eu_avg": 2.96e-4,
        "electricity_renewable": 0.0,
        
        # Transportation (per km)
        "car_gasoline": 1.92e-4,
        "car_diesel": 1.68e-4,
        "truck_diesel": 6.24e-4,
        "air_travel_domestic": 2.55e-4,
        "air_travel_international": 1.95e-4,
        
        # Other sources
        "waste_landfill": 1.0,  # per tonne waste
        "water_treatment": 3.14e-4,  # per cubic meter
        "refrigerant_r134a": 1430.0,  # per kg refrigerant
    }
    
    def calculate_emission(self, activity_data: float, activity_unit: str, 
                          emission_source: str, location: str = "global") -> float:
        """
        Calculate CO2 equivalent emissions for given activity data.
        
        Args:
            activity_data: Amount of activity (e.g., liters, kWh, km)
            activity_unit: Unit of activity data
            emission_source: Type of emission source
            location: Geographic location for location-specific factors
            
        Returns:
            CO2 equivalent emissions in tonnes
        """
        # Get emission factor
        factor_key = f"{emission_source}_{location.lower()}" if location != "global" else emission_source
        emission_factor = self.EMISSION_FACTORS.get(factor_key, 
                                                   self.EMISSION_FACTORS.get(emission_source, 0.0))
        
        if emission_factor == 0.0:
            print(f"Warning: No emission factor found for {emission_source}")
        
        return activity_data * emission_factor
    
    def calculate_scope_totals(self, emissions: List[EmissionData]) -> Dict[str, float]:
        """Calculate total emissions by scope."""
        scope_totals = {scope.value: 0.0 for scope in EmissionScope}
        
        for emission in emissions:
            scope_totals[emission.scope.value] += emission.co2_equivalent_tonnes
        
        return scope_totals
    
    def calculate_source_totals(self, emissions: List[EmissionData]) -> Dict[str, float]:
        """Calculate total emissions by source."""
        source_totals = {}
        
        for emission in emissions:
            source_key = emission.source.value
            if source_key not in source_totals:
                source_totals[source_key] = 0.0
            source_totals[source_key] += emission.co2_equivalent_tonnes
        
        return source_totals
    
    def calculate_monthly_trend(self, emissions: List[EmissionData]) -> pd.DataFrame:
        """Calculate monthly emission trends."""
        if not emissions:
            return pd.DataFrame()
        
        # Create DataFrame from emissions
        data = []
        for emission in emissions:
            # Use period start date for trend analysis
            data.append({
                'date': emission.reporting_period_start,
                'co2e_tonnes': emission.co2_equivalent_tonnes,
                'source': emission.source.value,
                'scope': emission.scope.value
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        
        # Group by month and calculate totals
        monthly_trends = df.groupby(['year_month', 'scope'])['co2e_tonnes'].sum().reset_index()
        monthly_trends['date'] = monthly_trends['year_month'].dt.to_timestamp()
        
        return monthly_trends
    
    def calculate_emission_intensity(self, emissions: List[EmissionData], 
                                   revenue: Optional[float] = None,
                                   employees: Optional[int] = None,
                                   production_units: Optional[float] = None) -> Dict[str, float]:
        """Calculate emission intensity metrics."""
        total_emissions = sum(e.co2_equivalent_tonnes for e in emissions)
        intensity_metrics = {}
        
        if revenue and revenue > 0:
            intensity_metrics['emissions_per_revenue'] = total_emissions / revenue
        
        if employees and employees > 0:
            intensity_metrics['emissions_per_employee'] = total_emissions / employees
        
        if production_units and production_units > 0:
            intensity_metrics['emissions_per_production_unit'] = total_emissions / production_units
        
        return intensity_metrics
    
    def validate_emission_data(self, emission: EmissionData) -> List[str]:
        """Validate emission data quality and return list of issues."""
        issues = []
        
        # Check for negative values
        if emission.co2_equivalent_tonnes < 0:
            issues.append("CO2 equivalent cannot be negative")
        
        if emission.activity_data < 0:
            issues.append("Activity data cannot be negative")
        
        if emission.emission_factor < 0:
            issues.append("Emission factor cannot be negative")
        
        # Check for date consistency
        if emission.reporting_period_start > emission.reporting_period_end:
            issues.append("Start date must be before end date")
        
        # Check for reasonable values
        if emission.co2_equivalent_tonnes > 100000:  # 100,000 tonnes
            issues.append("Unusually high CO2 equivalent value - please verify")
        
        # Check calculation consistency
        expected_co2e = emission.activity_data * emission.emission_factor
        if abs(emission.co2_equivalent_tonnes - expected_co2e) / expected_co2e > 0.01:  # 1% tolerance
            issues.append("CO2e value inconsistent with activity data × emission factor")
        
        return issues


class SustainabilityAnalyzer:
    """Analyzer for sustainability metrics and ESG performance."""
    
    def calculate_category_performance(self, metrics: List[SustainabilityMetrics]) -> Dict[str, Dict]:
        """Analyze performance by ESG category."""
        category_performance = {}
        
        for category in ['environmental', 'social', 'governance']:
            category_metrics = [m for m in metrics if m.category.value == category]
            
            if not category_metrics:
                category_performance[category] = {
                    'metrics_count': 0,
                    'average_progress': None,
                    'targets_met': 0,
                    'verified_metrics': 0
                }
                continue
            
            # Calculate progress statistics
            progress_values = [m.progress_to_target for m in category_metrics 
                             if m.progress_to_target is not None]
            
            avg_progress = np.mean(progress_values) if progress_values else None
            targets_met = len([p for p in progress_values if p >= 100])
            verified_count = len([m for m in category_metrics if m.verified])
            
            category_performance[category] = {
                'metrics_count': len(category_metrics),
                'average_progress': round(avg_progress, 2) if avg_progress else None,
                'targets_met': targets_met,
                'total_with_targets': len(progress_values),
                'verified_metrics': verified_count,
                'verification_rate': round((verified_count / len(category_metrics)) * 100, 1)
            }
        
        return category_performance
    
    def identify_performance_gaps(self, metrics: List[SustainabilityMetrics]) -> List[Dict]:
        """Identify metrics with poor performance or missing targets."""
        gaps = []
        
        for metric in metrics:
            gap_info = {
                'metric_name': metric.metric_name,
                'category': metric.category.value,
                'issues': []
            }
            
            # Check for missing target
            if metric.target_value is None:
                gap_info['issues'].append('No target value set')
            
            # Check for poor progress
            if metric.progress_to_target is not None and metric.progress_to_target < 50:
                gap_info['issues'].append(f'Low progress to target: {metric.progress_to_target:.1f}%')
            
            # Check for unverified data
            if not metric.verified:
                gap_info['issues'].append('Data not verified')
            
            # Check for missing description
            if not metric.description:
                gap_info['issues'].append('Missing description')
            
            if gap_info['issues']:
                gaps.append(gap_info)
        
        return gaps
    
    def calculate_esg_score(self, metrics: List[SustainabilityMetrics]) -> Dict[str, float]:
        """Calculate overall ESG scores (0-100 scale)."""
        category_scores = {}
        
        for category in ['environmental', 'social', 'governance']:
            category_metrics = [m for m in metrics if m.category.value == category]
            
            if not category_metrics:
                category_scores[category] = 0.0
                continue
            
            # Calculate weighted score based on progress to targets
            total_weight = 0
            weighted_score = 0
            
            for metric in category_metrics:
                # Weight by verification status
                weight = 1.0 if metric.verified else 0.5
                total_weight += weight
                
                # Score based on progress to target
                if metric.progress_to_target is not None:
                    score = min(metric.progress_to_target, 100)
                else:
                    score = 50  # Default score for metrics without targets
                
                weighted_score += score * weight
            
            category_scores[category] = round(weighted_score / total_weight if total_weight > 0 else 0, 1)
        
        # Calculate overall ESG score (equal weighting for now)
        overall_score = np.mean(list(category_scores.values()))
        category_scores['overall'] = round(overall_score, 1)
        
        return category_scores
    
    def benchmark_against_industry(self, metrics: List[SustainabilityMetrics], 
                                 industry: str) -> Dict[str, str]:
        """Compare metrics against industry benchmarks."""
        # This would typically connect to external benchmark databases
        # For now, we'll provide a simple comparison framework
        
        benchmarks = {
            'manufacturing': {
                'energy_intensity': 50.0,
                'water_usage': 100.0,
                'waste_diversion': 85.0,
                'employee_satisfaction': 75.0
            },
            'technology': {
                'energy_intensity': 25.0,
                'employee_satisfaction': 85.0,
                'diversity_ratio': 40.0,
                'data_privacy_score': 90.0
            },
            'financial_services': {
                'energy_intensity': 15.0,
                'employee_satisfaction': 80.0,
                'client_satisfaction': 85.0,
                'governance_score': 90.0
            }
        }
        
        industry_benchmarks = benchmarks.get(industry.lower(), {})
        comparisons = {}
        
        for metric in metrics:
            metric_key = metric.metric_name.lower().replace(' ', '_')
            if metric_key in industry_benchmarks:
                benchmark_value = industry_benchmarks[metric_key]
                
                if isinstance(metric.metric_value, (int, float)):
                    if metric.metric_value >= benchmark_value * 1.1:
                        comparisons[metric.metric_name] = "Above industry average"
                    elif metric.metric_value >= benchmark_value * 0.9:
                        comparisons[metric.metric_name] = "At industry average"
                    else:
                        comparisons[metric.metric_name] = "Below industry average"
        
        return comparisons
    
    def generate_recommendations(self, metrics: List[SustainabilityMetrics]) -> List[str]:
        """Generate improvement recommendations based on metrics analysis."""
        recommendations = []
        
        # Analyze performance gaps
        gaps = self.identify_performance_gaps(metrics)
        
        # Count metrics without targets
        metrics_without_targets = len([g for g in gaps if 'No target value set' in g['issues']])
        if metrics_without_targets > 0:
            recommendations.append(f"Set targets for {metrics_without_targets} metrics to improve goal tracking")
        
        # Count unverified metrics
        unverified_metrics = len([g for g in gaps if 'Data not verified' in g['issues']])
        if unverified_metrics > 0:
            recommendations.append(f"Implement verification processes for {unverified_metrics} metrics")
        
        # Analyze category balance
        category_performance = self.calculate_category_performance(metrics)
        category_counts = {cat: perf['metrics_count'] for cat, perf in category_performance.items()}
        
        min_category = min(category_counts, key=category_counts.get)
        max_category = max(category_counts, key=category_counts.get)
        
        if category_counts[max_category] > category_counts[min_category] * 2:
            recommendations.append(f"Consider adding more {min_category} metrics to balance ESG coverage")
        
        # Performance-based recommendations
        for category, performance in category_performance.items():
            if performance['average_progress'] and performance['average_progress'] < 70:
                recommendations.append(f"Focus on improving {category} performance - currently at {performance['average_progress']:.1f}% of targets")
        
        return recommendations