"""
Data processing utilities for importing and transforming ESG data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, date
import yaml
import json
from dataclasses import asdict

from ..core.models import (
    EmissionData, SustainabilityMetrics, CarbonTaxData, OrganizationProfile, 
    EmissionScope, EmissionSource, SustainabilityCategory
)


class DataImporter:
    """Import ESG data from various sources and formats."""
    
    def import_emissions_from_excel(self, filepath: str, sheet_name: str = None) -> List[EmissionData]:
        """Import emission data from Excel file."""
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            emissions = []
            
            # Expected columns mapping
            column_mapping = {
                'source': ['source', 'emission_source', 'Source', 'Emission Source'],
                'scope': ['scope', 'emission_scope', 'Scope', 'Emission Scope'],
                'co2_equivalent_tonnes': ['co2e', 'co2_equivalent', 'co2_equivalent_tonnes', 'CO2e (tonnes)', 'CO2e'],
                'activity_data': ['activity_data', 'activity', 'Activity Data', 'Activity'],
                'activity_unit': ['activity_unit', 'unit', 'Activity Unit', 'Unit'],
                'emission_factor': ['emission_factor', 'factor', 'Emission Factor', 'Factor'],
                'reporting_period_start': ['start_date', 'period_start', 'Start Date', 'Period Start'],
                'reporting_period_end': ['end_date', 'period_end', 'End Date', 'Period End'],
                'location': ['location', 'Location'],
                'facility': ['facility', 'Facility'],
                'department': ['department', 'Department'],
                'notes': ['notes', 'Notes', 'comments', 'Comments'],
                'verified': ['verified', 'Verified']
            }
            
            # Find actual column names
            actual_columns = {}
            for field, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        actual_columns[field] = name
                        break
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Required fields
                    source_str = str(row[actual_columns['source']]).lower()
                    scope_str = str(row[actual_columns['scope']]).lower()
                    
                    # Map source and scope to enums
                    source = None
                    for src in EmissionSource:
                        if src.value in source_str or source_str in src.value:
                            source = src
                            break
                    
                    scope = None
                    for scp in EmissionScope:
                        if scp.value in scope_str or scope_str in scp.value:
                            scope = scp
                            break
                    
                    if not source or not scope:
                        print(f"Warning: Could not map source '{source_str}' or scope '{scope_str}'")
                        continue
                    
                    # Parse dates
                    start_date = pd.to_datetime(row[actual_columns['reporting_period_start']]).date()
                    end_date = pd.to_datetime(row[actual_columns['reporting_period_end']]).date()
                    
                    emission = EmissionData(
                        source=source,
                        scope=scope,
                        co2_equivalent_tonnes=float(row[actual_columns['co2_equivalent_tonnes']]),
                        reporting_period_start=start_date,
                        reporting_period_end=end_date,
                        activity_data=float(row[actual_columns['activity_data']]),
                        activity_unit=str(row[actual_columns['activity_unit']]),
                        emission_factor=float(row[actual_columns['emission_factor']]),
                        location=str(row[actual_columns.get('location', '')]) if 'location' in actual_columns else None,
                        facility=str(row[actual_columns.get('facility', '')]) if 'facility' in actual_columns else None,
                        department=str(row[actual_columns.get('department', '')]) if 'department' in actual_columns else None,
                        notes=str(row[actual_columns.get('notes', '')]) if 'notes' in actual_columns else None,
                        verified=bool(row[actual_columns.get('verified', False)]) if 'verified' in actual_columns else False
                    )
                    
                    emissions.append(emission)
                    
                except Exception as e:
                    print(f"Warning: Could not process row {_}: {e}")
                    continue
            
            return emissions
            
        except Exception as e:
            print(f"Error importing emissions from Excel: {e}")
            return []
    
    def import_metrics_from_excel(self, filepath: str, sheet_name: str = None) -> List[SustainabilityMetrics]:
        """Import sustainability metrics from Excel file."""
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            metrics = []
            
            # Expected columns mapping
            column_mapping = {
                'category': ['category', 'esg_category', 'Category', 'ESG Category'],
                'metric_name': ['metric_name', 'metric', 'Metric Name', 'Metric'],
                'metric_value': ['value', 'metric_value', 'Value', 'Metric Value'],
                'metric_unit': ['unit', 'metric_unit', 'Unit', 'Metric Unit'],
                'target_value': ['target', 'target_value', 'Target', 'Target Value'],
                'reporting_period_start': ['start_date', 'period_start', 'Start Date', 'Period Start'],
                'reporting_period_end': ['end_date', 'period_end', 'End Date', 'Period End'],
                'description': ['description', 'Description'],
                'data_source': ['data_source', 'source', 'Data Source', 'Source'],
                'verified': ['verified', 'Verified']
            }
            
            # Find actual column names
            actual_columns = {}
            for field, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        actual_columns[field] = name
                        break
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Map category to enum
                    category_str = str(row[actual_columns['category']]).lower()
                    category = None
                    for cat in SustainabilityCategory:
                        if cat.value in category_str or category_str in cat.value:
                            category = cat
                            break
                    
                    if not category:
                        print(f"Warning: Could not map category '{category_str}'")
                        continue
                    
                    # Parse dates
                    start_date = pd.to_datetime(row[actual_columns['reporting_period_start']]).date()
                    end_date = pd.to_datetime(row[actual_columns['reporting_period_end']]).date()
                    
                    # Handle different value types
                    metric_value = row[actual_columns['metric_value']]
                    if pd.isna(metric_value):
                        continue
                    
                    # Try to convert to number, keep as string if not possible
                    try:
                        metric_value = float(metric_value)
                    except (ValueError, TypeError):
                        metric_value = str(metric_value)
                    
                    metric = SustainabilityMetrics(
                        category=category,
                        metric_name=str(row[actual_columns['metric_name']]),
                        metric_value=metric_value,
                        metric_unit=str(row[actual_columns['metric_unit']]),
                        reporting_period_start=start_date,
                        reporting_period_end=end_date,
                        target_value=float(row[actual_columns.get('target_value', np.nan)]) if 'target_value' in actual_columns and not pd.isna(row[actual_columns.get('target_value', np.nan)]) else None,
                        description=str(row[actual_columns.get('description', '')]) if 'description' in actual_columns else None,
                        data_source=str(row[actual_columns.get('data_source', '')]) if 'data_source' in actual_columns else None,
                        verified=bool(row[actual_columns.get('verified', False)]) if 'verified' in actual_columns else False
                    )
                    
                    metrics.append(metric)
                    
                except Exception as e:
                    print(f"Warning: Could not process row {_}: {e}")
                    continue
            
            return metrics
            
        except Exception as e:
            print(f"Error importing metrics from Excel: {e}")
            return []
    
    def import_from_csv(self, filepath: str, data_type: str = "emissions") -> Union[List[EmissionData], List[SustainabilityMetrics]]:
        """Import data from CSV file."""
        try:
            df = pd.read_csv(filepath)
            
            if data_type == "emissions":
                return self._process_emissions_dataframe(df)
            elif data_type == "metrics":
                return self._process_metrics_dataframe(df)
            else:
                raise ValueError("data_type must be 'emissions' or 'metrics'")
                
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return []
    
    def import_from_json(self, filepath: str) -> Dict[str, Any]:
        """Import organization and data configuration from JSON."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return {}
    
    def _process_emissions_dataframe(self, df: pd.DataFrame) -> List[EmissionData]:
        """Process DataFrame into EmissionData objects."""
        emissions = []
        
        # Expected columns mapping
        column_mapping = {
            'source': ['source', 'emission_source', 'Source', 'Emission Source'],
            'scope': ['scope', 'emission_scope', 'Scope', 'Emission Scope'],
            'co2_equivalent_tonnes': ['co2e', 'co2_equivalent', 'co2_equivalent_tonnes', 'CO2e (tonnes)', 'CO2e'],
            'activity_data': ['activity_data', 'activity', 'Activity Data', 'Activity'],
            'activity_unit': ['activity_unit', 'unit', 'Activity Unit', 'Unit'],
            'emission_factor': ['emission_factor', 'factor', 'Emission Factor', 'Factor'],
            'reporting_period_start': ['start_date', 'period_start', 'Start Date', 'Period Start'],
            'reporting_period_end': ['end_date', 'period_end', 'End Date', 'Period End'],
            'location': ['location', 'Location'],
            'facility': ['facility', 'Facility'],
            'department': ['department', 'Department'],
            'notes': ['notes', 'Notes', 'comments', 'Comments'],
            'verified': ['verified', 'Verified']
        }
        
        # Find actual column names
        actual_columns = {}
        for field, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns:
                    actual_columns[field] = name
                    break
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Required fields
                source_str = str(row[actual_columns['source']]).lower()
                scope_str = str(row[actual_columns['scope']]).lower()
                
                # Map source and scope to enums
                source = None
                for src in EmissionSource:
                    if src.value in source_str or source_str in src.value:
                        source = src
                        break
                
                scope = None
                for scp in EmissionScope:
                    if scp.value in scope_str or scope_str in scp.value:
                        scope = scp
                        break
                
                if not source or not scope:
                    print(f"Warning: Could not map source '{source_str}' or scope '{scope_str}'")
                    continue
                
                # Parse dates
                start_date = pd.to_datetime(row[actual_columns['reporting_period_start']]).date()
                end_date = pd.to_datetime(row[actual_columns['reporting_period_end']]).date()
                
                emission = EmissionData(
                    source=source,
                    scope=scope,
                    co2_equivalent_tonnes=float(row[actual_columns['co2_equivalent_tonnes']]),
                    reporting_period_start=start_date,
                    reporting_period_end=end_date,
                    activity_data=float(row[actual_columns['activity_data']]),
                    activity_unit=str(row[actual_columns['activity_unit']]),
                    emission_factor=float(row[actual_columns['emission_factor']]),
                    location=str(row[actual_columns.get('location', '')]) if 'location' in actual_columns else None,
                    facility=str(row[actual_columns.get('facility', '')]) if 'facility' in actual_columns else None,
                    department=str(row[actual_columns.get('department', '')]) if 'department' in actual_columns else None,
                    notes=str(row[actual_columns.get('notes', '')]) if 'notes' in actual_columns else None,
                    verified=bool(row[actual_columns.get('verified', False)]) if 'verified' in actual_columns else False
                )
                
                emissions.append(emission)
                
            except Exception as e:
                print(f"Warning: Could not process row {_}: {e}")
                continue
        
        return emissions
    
    def _process_metrics_dataframe(self, df: pd.DataFrame) -> List[SustainabilityMetrics]:
        """Process DataFrame into SustainabilityMetrics objects."""
        metrics = []
        
        # Expected columns mapping
        column_mapping = {
            'category': ['category', 'esg_category', 'Category', 'ESG Category'],
            'metric_name': ['metric_name', 'metric', 'Metric Name', 'Metric'],
            'metric_value': ['value', 'metric_value', 'Value', 'Metric Value'],
            'metric_unit': ['unit', 'metric_unit', 'Unit', 'Metric Unit'],
            'target_value': ['target', 'target_value', 'Target', 'Target Value'],
            'reporting_period_start': ['start_date', 'period_start', 'Start Date', 'Period Start'],
            'reporting_period_end': ['end_date', 'period_end', 'End Date', 'Period End'],
            'description': ['description', 'Description'],
            'data_source': ['data_source', 'source', 'Data Source', 'Source'],
            'verified': ['verified', 'Verified']
        }
        
        # Find actual column names
        actual_columns = {}
        for field, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns:
                    actual_columns[field] = name
                    break
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Map category to enum
                category_str = str(row[actual_columns['category']]).lower()
                category = None
                for cat in SustainabilityCategory:
                    if cat.value in category_str or category_str in cat.value:
                        category = cat
                        break
                
                if not category:
                    print(f"Warning: Could not map category '{category_str}'")
                    continue
                
                # Parse dates
                start_date = pd.to_datetime(row[actual_columns['reporting_period_start']]).date()
                end_date = pd.to_datetime(row[actual_columns['reporting_period_end']]).date()
                
                # Handle different value types
                metric_value = row[actual_columns['metric_value']]
                if pd.isna(metric_value):
                    continue
                
                # Try to convert to number, keep as string if not possible
                try:
                    metric_value = float(metric_value)
                except (ValueError, TypeError):
                    metric_value = str(metric_value)
                
                metric = SustainabilityMetrics(
                    category=category,
                    metric_name=str(row[actual_columns['metric_name']]),
                    metric_value=metric_value,
                    metric_unit=str(row[actual_columns['metric_unit']]),
                    reporting_period_start=start_date,
                    reporting_period_end=end_date,
                    target_value=float(row[actual_columns.get('target_value', np.nan)]) if 'target_value' in actual_columns and not pd.isna(row[actual_columns.get('target_value', np.nan)]) else None,
                    description=str(row[actual_columns.get('description', '')]) if 'description' in actual_columns else None,
                    data_source=str(row[actual_columns.get('data_source', '')]) if 'data_source' in actual_columns else None,
                    verified=bool(row[actual_columns.get('verified', False)]) if 'verified' in actual_columns else False
                )
                
                metrics.append(metric)
                
            except Exception as e:
                print(f"Warning: Could not process row {_}: {e}")
                continue
        
        return metrics


class DataExporter:
    """Export ESG data to various formats."""
    
    def export_emissions_to_excel(self, emissions: List[EmissionData], filepath: str) -> bool:
        """Export emission data to Excel file."""
        try:
            data = []
            for emission in emissions:
                data.append({
                    'Source': emission.source.value,
                    'Scope': emission.scope.value,
                    'CO2e (tonnes)': emission.co2_equivalent_tonnes,
                    'Activity Data': emission.activity_data,
                    'Activity Unit': emission.activity_unit,
                    'Emission Factor': emission.emission_factor,
                    'Period Start': emission.reporting_period_start,
                    'Period End': emission.reporting_period_end,
                    'Location': emission.location,
                    'Facility': emission.facility,
                    'Department': emission.department,
                    'Verified': emission.verified,
                    'Notes': emission.notes,
                    'Created At': emission.created_at
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            return True
            
        except Exception as e:
            print(f"Error exporting emissions to Excel: {e}")
            return False
    
    def export_metrics_to_excel(self, metrics: List[SustainabilityMetrics], filepath: str) -> bool:
        """Export sustainability metrics to Excel file."""
        try:
            data = []
            for metric in metrics:
                data.append({
                    'Category': metric.category.value,
                    'Metric Name': metric.metric_name,
                    'Value': metric.metric_value,
                    'Unit': metric.metric_unit,
                    'Target': metric.target_value,
                    'Progress %': metric.progress_to_target,
                    'Period Start': metric.reporting_period_start,
                    'Period End': metric.reporting_period_end,
                    'Description': metric.description,
                    'Data Source': metric.data_source,
                    'Calculation Method': metric.calculation_method,
                    'Verified': metric.verified,
                    'Created At': metric.created_at
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            return True
            
        except Exception as e:
            print(f"Error exporting metrics to Excel: {e}")
            return False
    
    def export_to_json(self, data: Any, filepath: str) -> bool:
        """Export data to JSON format."""
        try:
            with open(filepath, 'w') as f:
                if hasattr(data, '__dict__') or hasattr(data, '_asdict'):
                    # Handle dataclass or named tuple
                    json.dump(asdict(data) if hasattr(data, '__dict__') else data._asdict(), 
                             f, indent=2, default=str)
                else:
                    json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False


class DataValidator:
    """Validate ESG data quality and consistency."""
    
    def validate_emissions_data(self, emissions: List[EmissionData]) -> Dict[str, Any]:
        """Validate emission data quality."""
        validation_results = {
            'total_records': len(emissions),
            'valid_records': 0,
            'errors': [],
            'warnings': [],
            'data_quality_score': 0.0
        }
        
        if not emissions:
            validation_results['errors'].append("No emission data provided")
            return validation_results
        
        valid_count = 0
        
        for i, emission in enumerate(emissions):
            record_issues = []
            
            # Validate required fields
            if emission.co2_equivalent_tonnes <= 0:
                record_issues.append(f"Record {i+1}: CO2e must be positive")
            
            if emission.activity_data <= 0:
                record_issues.append(f"Record {i+1}: Activity data must be positive")
            
            if emission.emission_factor <= 0:
                record_issues.append(f"Record {i+1}: Emission factor must be positive")
            
            # Validate date range
            if emission.reporting_period_start >= emission.reporting_period_end:
                record_issues.append(f"Record {i+1}: Start date must be before end date")
            
            # Validate calculation consistency
            expected_co2e = emission.activity_data * emission.emission_factor
            if abs(emission.co2_equivalent_tonnes - expected_co2e) / expected_co2e > 0.05:  # 5% tolerance
                validation_results['warnings'].append(
                    f"Record {i+1}: CO2e calculation may be inconsistent with activity data × emission factor"
                )
            
            # Check for missing optional data
            if not emission.location:
                validation_results['warnings'].append(f"Record {i+1}: Missing location information")
            
            if not emission.verified:
                validation_results['warnings'].append(f"Record {i+1}: Data not verified")
            
            if not record_issues:
                valid_count += 1
            else:
                validation_results['errors'].extend(record_issues)
        
        validation_results['valid_records'] = valid_count
        validation_results['data_quality_score'] = (valid_count / len(emissions)) * 100
        
        return validation_results
    
    def validate_metrics_data(self, metrics: List[SustainabilityMetrics]) -> Dict[str, Any]:
        """Validate sustainability metrics data quality."""
        validation_results = {
            'total_records': len(metrics),
            'valid_records': 0,
            'errors': [],
            'warnings': [],
            'data_quality_score': 0.0
        }
        
        if not metrics:
            validation_results['errors'].append("No metrics data provided")
            return validation_results
        
        valid_count = 0
        
        for i, metric in enumerate(metrics):
            record_issues = []
            
            # Validate required fields
            if not metric.metric_name.strip():
                record_issues.append(f"Record {i+1}: Metric name cannot be empty")
            
            if not metric.metric_unit.strip():
                record_issues.append(f"Record {i+1}: Metric unit cannot be empty")
            
            # Validate date range
            if metric.reporting_period_start >= metric.reporting_period_end:
                record_issues.append(f"Record {i+1}: Start date must be before end date")
            
            # Validate progress calculation
            if metric.target_value is not None and isinstance(metric.metric_value, (int, float)) and metric.target_value != 0:
                calculated_progress = (metric.metric_value / metric.target_value) * 100
                if metric.progress_to_target and abs(calculated_progress - metric.progress_to_target) > 1:
                    validation_results['warnings'].append(
                        f"Record {i+1}: Progress calculation may be incorrect"
                    )
            
            # Check for missing optional data
            if not metric.description:
                validation_results['warnings'].append(f"Record {i+1}: Missing description")
            
            if metric.target_value is None:
                validation_results['warnings'].append(f"Record {i+1}: No target value set")
            
            if not metric.verified:
                validation_results['warnings'].append(f"Record {i+1}: Data not verified")
            
            if not record_issues:
                valid_count += 1
            else:
                validation_results['errors'].extend(record_issues)
        
        validation_results['valid_records'] = valid_count
        validation_results['data_quality_score'] = (valid_count / len(metrics)) * 100
        
        return validation_results
    
    def check_data_completeness(self, emissions: List[EmissionData], 
                              metrics: List[SustainabilityMetrics]) -> Dict[str, Any]:
        """Check overall data completeness for ESG reporting."""
        completeness = {
            'emissions_coverage': {},
            'metrics_coverage': {},
            'overall_score': 0.0,
            'recommendations': []
        }
        
        # Check emission scope coverage
        scope_coverage = {scope.value: 0 for scope in EmissionScope}
        for emission in emissions:
            scope_coverage[emission.scope.value] += 1
        
        completeness['emissions_coverage']['by_scope'] = scope_coverage
        missing_scopes = [scope for scope, count in scope_coverage.items() if count == 0]
        if missing_scopes:
            completeness['recommendations'].append(f"Missing emission data for scopes: {', '.join(missing_scopes)}")
        
        # Check ESG category coverage
        category_coverage = {cat.value: 0 for cat in SustainabilityCategory}
        for metric in metrics:
            category_coverage[metric.category.value] += 1
        
        completeness['metrics_coverage']['by_category'] = category_coverage
        missing_categories = [cat for cat, count in category_coverage.items() if count == 0]
        if missing_categories:
            completeness['recommendations'].append(f"Missing metrics for categories: {', '.join(missing_categories)}")
        
        # Calculate overall completeness score
        scope_score = len([s for s in scope_coverage.values() if s > 0]) / len(EmissionScope) * 50
        category_score = len([c for c in category_coverage.values() if c > 0]) / len(SustainabilityCategory) * 50
        completeness['overall_score'] = scope_score + category_score
        
        return completeness


class DataTransformer:
    """Transform and normalize ESG data."""
    
    def normalize_emission_units(self, emissions: List[EmissionData], target_unit: str = "tonnes") -> List[EmissionData]:
        """Normalize emission units to consistent format."""
        unit_conversions = {
            'kg': 0.001,
            'kilograms': 0.001,
            'tonnes': 1.0,
            'tons': 1.0,
            'metric_tons': 1.0,
            'pounds': 0.000453592,
            'lbs': 0.000453592
        }
        
        normalized_emissions = []
        
        for emission in emissions:
            # Create a copy to avoid modifying original
            normalized = EmissionData(
                source=emission.source,
                scope=emission.scope,
                co2_equivalent_tonnes=emission.co2_equivalent_tonnes,
                reporting_period_start=emission.reporting_period_start,
                reporting_period_end=emission.reporting_period_end,
                activity_data=emission.activity_data,
                activity_unit=emission.activity_unit,
                emission_factor=emission.emission_factor,
                location=emission.location,
                facility=emission.facility,
                department=emission.department,
                notes=emission.notes,
                verified=emission.verified,
                created_at=emission.created_at
            )
            
            # Apply unit conversion if needed
            # This is a simplified example - real implementation would be more comprehensive
            if target_unit == "tonnes" and "kg" in emission.activity_unit.lower():
                conversion_factor = unit_conversions.get("kg", 1.0)
                normalized.co2_equivalent_tonnes *= conversion_factor
            
            normalized_emissions.append(normalized)
        
        return normalized_emissions
    
    def aggregate_emissions_by_period(self, emissions: List[EmissionData], 
                                    period: str = "monthly") -> pd.DataFrame:
        """Aggregate emissions by time period."""
        if not emissions:
            return pd.DataFrame()
        
        data = []
        for emission in emissions:
            data.append({
                'date': emission.reporting_period_start,
                'co2e_tonnes': emission.co2_equivalent_tonnes,
                'source': emission.source.value,
                'scope': emission.scope.value,
                'location': emission.location or 'Unknown'
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Set grouping period
        if period == "monthly":
            df['period'] = df['date'].dt.to_period('M')
        elif period == "quarterly":
            df['period'] = df['date'].dt.to_period('Q')
        elif period == "yearly":
            df['period'] = df['date'].dt.to_period('Y')
        else:
            raise ValueError("Period must be 'monthly', 'quarterly', or 'yearly'")
        
        # Aggregate by period and other dimensions
        aggregated = df.groupby(['period', 'source', 'scope', 'location'])['co2e_tonnes'].sum().reset_index()
        aggregated['period_start'] = aggregated['period'].dt.start_time
        
        return aggregated