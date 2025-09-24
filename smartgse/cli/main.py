"""
Command-line interface for SmartGSE platform.
"""

import click
import os
import sys
from datetime import datetime, date
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.models import OrganizationProfile, ReportConfiguration, ReportingStandard
from ..reports.sustainability import SustainabilityReport
from ..reports.carbon_tax import CarbonTaxReport
from ..data.processors import DataImporter, DataValidator, DataExporter
from ..utils.calculations import EmissionCalculator, SustainabilityAnalyzer

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """SmartGSE - Sustainability Report and Carbon Tax Report Platform"""
    console.print(Panel.fit(
        "[bold green]SmartGSE[/bold green]\n"
        "Sustainability Report and Carbon Tax Report Platform",
        title="Welcome"
    ))


@cli.group()
def data():
    """Data import, export, and validation commands."""
    pass


@cli.group()
def report():
    """Report generation commands."""
    pass


@cli.group()
def analyze():
    """Data analysis and insights commands."""
    pass


@data.command("import-emissions")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--sheet", default=None, help="Excel sheet name (for .xlsx files)")
@click.option("--validate", is_flag=True, help="Validate data after import")
@click.option("--output", help="Output file for processed data")
def import_emissions(filepath: str, sheet: Optional[str], validate: bool, output: Optional[str]):
    """Import emission data from Excel or CSV file."""
    console.print(f"[blue]Importing emission data from:[/blue] {filepath}")
    
    importer = DataImporter()
    
    try:
        if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            emissions = importer.import_emissions_from_excel(filepath, sheet)
        elif filepath.endswith('.csv'):
            emissions = importer.import_from_csv(filepath, "emissions")
        else:
            console.print("[red]Error:[/red] Unsupported file format. Use .xlsx, .xls, or .csv")
            return
        
        console.print(f"[green]Successfully imported {len(emissions)} emission records[/green]")
        
        if validate:
            console.print("\n[blue]Validating data...[/blue]")
            validator = DataValidator()
            results = validator.validate_emissions_data(emissions)
            
            # Display validation results
            table = Table(title="Validation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Records", str(results['total_records']))
            table.add_row("Valid Records", str(results['valid_records']))
            table.add_row("Data Quality Score", f"{results['data_quality_score']:.1f}%")
            table.add_row("Errors", str(len(results['errors'])))
            table.add_row("Warnings", str(len(results['warnings'])))
            
            console.print(table)
            
            if results['errors']:
                console.print("\n[red]Errors found:[/red]")
                for error in results['errors'][:10]:  # Show first 10 errors
                    console.print(f"  • {error}")
                if len(results['errors']) > 10:
                    console.print(f"  ... and {len(results['errors']) - 10} more errors")
        
        if output:
            exporter = DataExporter()
            if exporter.export_emissions_to_excel(emissions, output):
                console.print(f"[green]Data exported to:[/green] {output}")
            else:
                console.print(f"[red]Failed to export data to:[/red] {output}")
                
    except Exception as e:
        console.print(f"[red]Error importing data:[/red] {e}")


@data.command("import-metrics")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--sheet", default=None, help="Excel sheet name (for .xlsx files)")
@click.option("--validate", is_flag=True, help="Validate data after import")
@click.option("--output", help="Output file for processed data")
def import_metrics(filepath: str, sheet: Optional[str], validate: bool, output: Optional[str]):
    """Import sustainability metrics from Excel or CSV file."""
    console.print(f"[blue]Importing sustainability metrics from:[/blue] {filepath}")
    
    importer = DataImporter()
    
    try:
        if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            metrics = importer.import_metrics_from_excel(filepath, sheet)
        elif filepath.endswith('.csv'):
            metrics = importer.import_from_csv(filepath, "metrics")
        else:
            console.print("[red]Error:[/red] Unsupported file format. Use .xlsx, .xls, or .csv")
            return
        
        console.print(f"[green]Successfully imported {len(metrics)} sustainability metrics[/green]")
        
        if validate:
            console.print("\n[blue]Validating data...[/blue]")
            validator = DataValidator()
            results = validator.validate_metrics_data(metrics)
            
            # Display validation results
            table = Table(title="Validation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Records", str(results['total_records']))
            table.add_row("Valid Records", str(results['valid_records']))
            table.add_row("Data Quality Score", f"{results['data_quality_score']:.1f}%")
            table.add_row("Errors", str(len(results['errors'])))
            table.add_row("Warnings", str(len(results['warnings'])))
            
            console.print(table)
        
        if output:
            exporter = DataExporter()
            if exporter.export_metrics_to_excel(metrics, output):
                console.print(f"[green]Data exported to:[/green] {output}")
            else:
                console.print(f"[red]Failed to export data to:[/red] {output}")
                
    except Exception as e:
        console.print(f"[red]Error importing data:[/red] {e}")


@report.command("sustainability")
@click.option("--org-name", required=True, help="Organization name")
@click.option("--industry", required=True, help="Industry sector")
@click.option("--year", type=int, default=datetime.now().year - 1, help="Reporting year")
@click.option("--emissions-file", type=click.Path(exists=True), help="Path to emissions data file")
@click.option("--metrics-file", type=click.Path(exists=True), help="Path to metrics data file")
@click.option("--output-dir", default="output", help="Output directory for reports")
@click.option("--format", "output_format", type=click.Choice(['pdf', 'excel', 'both']), default='pdf', help="Output format")
def generate_sustainability_report(org_name: str, industry: str, year: int, 
                                 emissions_file: Optional[str], metrics_file: Optional[str],
                                 output_dir: str, output_format: str):
    """Generate sustainability report."""
    console.print(f"[blue]Generating sustainability report for {org_name}[/blue]")
    
    try:
        # Create organization profile
        org_profile = OrganizationProfile(
            name=org_name,
            industry=industry,
            size="Unknown",  # Would be provided by user or config
            headquarters_location="Unknown",  # Would be provided by user or config
            reporting_year=year,
            fiscal_year_start=date(year, 1, 1),
            fiscal_year_end=date(year, 12, 31)
        )
        
        # Create report configuration
        config = ReportConfiguration(
            organization=org_profile,
            standards=[ReportingStandard.GRI, ReportingStandard.TCFD],
            include_executive_summary=True,
            include_methodology=True,
            output_format=output_format if output_format != 'both' else 'pdf'
        )
        
        # Initialize report
        report = SustainabilityReport(config)
        
        # Import data if files provided
        importer = DataImporter()
        
        if emissions_file:
            with console.status("Importing emission data..."):
                if emissions_file.endswith(('.xlsx', '.xls')):
                    emissions = importer.import_emissions_from_excel(emissions_file)
                else:
                    emissions = importer.import_from_csv(emissions_file, "emissions")
                report.add_emission_data(emissions)
                console.print(f"[green]Loaded {len(emissions)} emission records[/green]")
        
        if metrics_file:
            with console.status("Importing sustainability metrics..."):
                if metrics_file.endswith(('.xlsx', '.xls')):
                    metrics = importer.import_metrics_from_excel(metrics_file)
                else:
                    metrics = importer.import_from_csv(metrics_file, "metrics")
                report.add_sustainability_metrics(metrics)
                console.print(f"[green]Loaded {len(metrics)} sustainability metrics[/green]")
        
        # Generate visualizations
        with console.status("Creating visualizations..."):
            chart_files = report.create_visualizations(output_dir)
            console.print(f"[green]Generated {len(chart_files)} charts[/green]")
        
        # Generate reports
        os.makedirs(output_dir, exist_ok=True)
        
        if output_format in ['pdf', 'both']:
            with console.status("Generating PDF report..."):
                pdf_file = report.export_to_pdf(output_dir=output_dir)
                console.print(f"[green]PDF report saved:[/green] {pdf_file}")
        
        if output_format in ['excel', 'both']:
            with console.status("Generating Excel export..."):
                excel_file = report.export_data_to_excel(output_dir=output_dir)
                console.print(f"[green]Excel data saved:[/green] {excel_file}")
        
        console.print(f"\n[bold green]Sustainability report generation completed![/bold green]")
        console.print(f"Output directory: {output_dir}")
        
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        sys.exit(1)


@report.command("carbon-tax")
@click.option("--org-name", required=True, help="Organization name")
@click.option("--industry", required=True, help="Industry sector")
@click.option("--year", type=int, default=datetime.now().year - 1, help="Reporting year")
@click.option("--emissions-file", type=click.Path(exists=True), help="Path to emissions data file")
@click.option("--jurisdiction", required=True, help="Tax jurisdiction")
@click.option("--tax-rate", type=float, required=True, help="Carbon tax rate per tonne CO2e")
@click.option("--currency", default="USD", help="Currency for tax calculations")
@click.option("--output-dir", default="output", help="Output directory for reports")
@click.option("--format", "output_format", type=click.Choice(['pdf', 'excel', 'both']), default='pdf', help="Output format")
def generate_carbon_tax_report(org_name: str, industry: str, year: int, 
                             emissions_file: Optional[str], jurisdiction: str,
                             tax_rate: float, currency: str, output_dir: str, output_format: str):
    """Generate carbon tax report."""
    console.print(f"[blue]Generating carbon tax report for {org_name}[/blue]")
    
    try:
        # Create organization profile
        org_profile = OrganizationProfile(
            name=org_name,
            industry=industry,
            size="Unknown",
            headquarters_location="Unknown",
            reporting_year=year,
            fiscal_year_start=date(year, 1, 1),
            fiscal_year_end=date(year, 12, 31)
        )
        
        # Initialize report
        report = CarbonTaxReport(org_profile)
        
        # Import emissions data
        if emissions_file:
            importer = DataImporter()
            with console.status("Importing emission data..."):
                if emissions_file.endswith(('.xlsx', '.xls')):
                    emissions = importer.import_emissions_from_excel(emissions_file)
                else:
                    emissions = importer.import_from_csv(emissions_file, "emissions")
                console.print(f"[green]Loaded {len(emissions)} emission records[/green]")
            
            # Create carbon tax data
            from ..core.models import CarbonTaxData
            
            tax_data = CarbonTaxData(
                jurisdiction=jurisdiction,
                tax_rate_per_tonne=tax_rate,
                currency=currency,
                emissions_covered=emissions,
                reporting_period_start=org_profile.fiscal_year_start,
                reporting_period_end=org_profile.fiscal_year_end
            )
            
            report.add_tax_data([tax_data])
            
            # Display tax calculation summary
            table = Table(title="Carbon Tax Calculation Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Jurisdiction", jurisdiction)
            table.add_row("Tax Rate", f"{tax_rate:.2f} {currency}/tonne CO2e")
            table.add_row("Total Emissions", f"{tax_data.total_emissions_tonnes:.2f} tonnes CO2e")
            table.add_row("Gross Tax Liability", f"{tax_data.gross_tax_liability:,.2f} {currency}")
            table.add_row("Net Tax Liability", f"{tax_data.net_tax_liability:,.2f} {currency}")
            
            console.print(table)
        
        # Generate visualizations
        with console.status("Creating visualizations..."):
            chart_files = report.create_tax_visualizations(output_dir)
            console.print(f"[green]Generated {len(chart_files)} charts[/green]")
        
        # Generate reports
        os.makedirs(output_dir, exist_ok=True)
        
        if output_format in ['pdf', 'both']:
            with console.status("Generating PDF report..."):
                pdf_file = report.export_to_pdf(output_dir=output_dir)
                console.print(f"[green]PDF report saved:[/green] {pdf_file}")
        
        if output_format in ['excel', 'both']:
            with console.status("Generating Excel export..."):
                excel_file = report.export_data_to_excel(output_dir=output_dir)
                console.print(f"[green]Excel data saved:[/green] {excel_file}")
        
        console.print(f"\n[bold green]Carbon tax report generation completed![/bold green]")
        console.print(f"Output directory: {output_dir}")
        
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        sys.exit(1)


@analyze.command("emissions")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--sheet", default=None, help="Excel sheet name")
def analyze_emissions(filepath: str, sheet: Optional[str]):
    """Analyze emission data and provide insights."""
    console.print(f"[blue]Analyzing emission data from:[/blue] {filepath}")
    
    try:
        importer = DataImporter()
        calculator = EmissionCalculator()
        
        # Import data
        if filepath.endswith(('.xlsx', '.xls')):
            emissions = importer.import_emissions_from_excel(filepath, sheet)
        else:
            emissions = importer.import_from_csv(filepath, "emissions")
        
        console.print(f"[green]Loaded {len(emissions)} emission records[/green]\n")
        
        # Calculate totals by scope
        scope_totals = calculator.calculate_scope_totals(emissions)
        
        scope_table = Table(title="Emissions by Scope")
        scope_table.add_column("Scope", style="cyan")
        scope_table.add_column("Emissions (tonnes CO2e)", style="magenta")
        scope_table.add_column("Percentage", style="yellow")
        
        total_emissions = sum(scope_totals.values())
        for scope, total in scope_totals.items():
            percentage = (total / total_emissions * 100) if total_emissions > 0 else 0
            scope_table.add_row(
                scope.replace('_', ' ').title(),
                f"{total:.2f}",
                f"{percentage:.1f}%"
            )
        
        console.print(scope_table)
        
        # Calculate totals by source
        source_totals = calculator.calculate_source_totals(emissions)
        top_sources = sorted(source_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        source_table = Table(title="Top 5 Emission Sources")
        source_table.add_column("Source", style="cyan")
        source_table.add_column("Emissions (tonnes CO2e)", style="magenta")
        source_table.add_column("Percentage", style="yellow")
        
        for source, total in top_sources:
            percentage = (total / total_emissions * 100) if total_emissions > 0 else 0
            source_table.add_row(
                source.replace('_', ' ').title(),
                f"{total:.2f}",
                f"{percentage:.1f}%"
            )
        
        console.print(source_table)
        
        # Data quality assessment
        validator = DataValidator()
        validation = validator.validate_emissions_data(emissions)
        
        console.print(f"\n[bold]Data Quality Score:[/bold] {validation['data_quality_score']:.1f}%")
        if validation['warnings']:
            console.print(f"[yellow]Warnings:[/yellow] {len(validation['warnings'])}")
        if validation['errors']:
            console.print(f"[red]Errors:[/red] {len(validation['errors'])}")
        
    except Exception as e:
        console.print(f"[red]Error analyzing data:[/red] {e}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()