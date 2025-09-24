# SmartGSE - Sustainability Report and Carbon Tax Report Platform

SmartGSE is a comprehensive platform designed to support organizations in complying with ESG disclosure requirements, tracking carbon emissions, and calculating related carbon tax liabilities. The solution enables structured reporting, data integration, and transparent communication of sustainability performance.

## Features

### 🌱 Sustainability Reporting
- **ESG Metrics Tracking**: Track environmental, social, and governance metrics
- **Multi-Standard Support**: Compatible with GRI, SASB, TCFD, CDP, and other frameworks
- **Automated Report Generation**: Create professional PDF and Excel reports
- **Data Visualization**: Generate charts and graphs for better insights
- **Progress Tracking**: Monitor progress against sustainability targets

### 💰 Carbon Tax Reporting
- **Multi-Jurisdiction Support**: Handle carbon tax calculations across different regions
- **Automated Calculations**: Calculate gross and net tax liabilities
- **Exemptions & Credits**: Account for tax exemptions and carbon credits
- **Compliance Tracking**: Monitor compliance status and penalties
- **Tax Optimization**: Identify opportunities for tax efficiency

### 📊 Data Management
- **Data Import/Export**: Support for Excel, CSV, and JSON formats
- **Data Validation**: Comprehensive data quality checks
- **Data Transformation**: Normalize and aggregate data across periods
- **Integration Ready**: APIs and templates for system integration

### 🔧 Tools & Utilities
- **Emission Calculations**: Built-in emission factors and calculation engine
- **Performance Analytics**: ESG scoring and benchmarking
- **Command-Line Interface**: Full CLI for automation and scripting
- **Template Management**: Customizable report templates

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from Source
```bash
git clone https://github.com/gdimauro/SmartGSE.git
cd SmartGSE
pip install -r requirements.txt
pip install -e .
```

### Verify Installation
```bash
smartgse --version
```

## Quick Start

### 1. Import Sample Data
```bash
# Import emission data
smartgse data import-emissions examples/sample_emissions.csv --validate

# Import sustainability metrics
smartgse data import-metrics examples/sample_metrics.csv --validate
```

### 2. Generate Sustainability Report
```bash
smartgse report sustainability \
    --org-name "Your Company" \
    --industry "Technology" \
    --year 2023 \
    --emissions-file examples/sample_emissions.csv \
    --metrics-file examples/sample_metrics.csv \
    --output-dir reports \
    --format both
```

### 3. Generate Carbon Tax Report
```bash
smartgse report carbon-tax \
    --org-name "Your Company" \
    --industry "Technology" \
    --year 2023 \
    --emissions-file examples/sample_emissions.csv \
    --jurisdiction "California" \
    --tax-rate 25.00 \
    --currency USD \
    --output-dir reports \
    --format pdf
```

### 4. Analyze Your Data
```bash
smartgse analyze emissions examples/sample_emissions.csv
```

## Data Formats

### Emission Data Format (CSV/Excel)
| Column | Description | Example |
|--------|-------------|---------|
| Source | Emission source type | electricity, fuel_combustion, transportation |
| Scope | GHG Protocol scope | scope_1, scope_2, scope_3 |
| CO2e (tonnes) | CO2 equivalent emissions | 125.5 |
| Activity Data | Activity amount | 300000 |
| Activity Unit | Unit of activity | kWh, liters, km |
| Emission Factor | CO2e per activity unit | 0.000421 |
| Period Start | Reporting period start | 2023-01-01 |
| Period End | Reporting period end | 2023-12-31 |
| Location | Geographic location | New York, California |
| Facility | Facility name | Main Office, Plant 1 |
| Verified | Data verification status | true, false |
| Notes | Additional notes | Optional description |

### Sustainability Metrics Format (CSV/Excel)
| Column | Description | Example |
|--------|-------------|---------|
| Category | ESG category | environmental, social, governance |
| Metric Name | Name of the metric | Energy Intensity, Employee Satisfaction |
| Value | Metric value | 2.5, 4.2 |
| Unit | Unit of measurement | MWh/employee, rating (1-5) |
| Target | Target value | 2.0, 4.5 |
| Period Start | Reporting period start | 2023-01-01 |
| Period End | Reporting period end | 2023-12-31 |
| Description | Metric description | Energy consumption per employee |
| Data Source | Source of data | Facilities Management, HR |
| Verified | Data verification status | true, false |

## API Usage

### Python API Example
```python
from smartgse import EmissionData, SustainabilityReport, CarbonTaxReport
from smartgse.core.models import OrganizationProfile, ReportConfiguration
from datetime import date

# Create organization profile
org = OrganizationProfile(
    name="Your Company",
    industry="Technology",
    size="Large",
    headquarters_location="New York",
    reporting_year=2023,
    fiscal_year_start=date(2023, 1, 1),
    fiscal_year_end=date(2023, 12, 31)
)

# Create report configuration
config = ReportConfiguration(
    organization=org,
    standards=["gri", "tcfd"],
    include_executive_summary=True
)

# Generate sustainability report
report = SustainabilityReport(config)
# Add your emission data and metrics
pdf_file = report.export_to_pdf()
```

## Configuration

### Emission Factors
SmartGSE includes built-in emission factors for common sources:
- **Electricity**: Regional grid factors (US, EU averages)
- **Fuel Combustion**: Gasoline, diesel, natural gas, propane
- **Transportation**: Cars, trucks, air travel (domestic/international)
- **Other Sources**: Waste, water treatment, refrigerants

### Custom Emission Factors
You can extend or override emission factors in your calculations:
```python
from smartgse.utils.calculations import EmissionCalculator

calculator = EmissionCalculator()
calculator.EMISSION_FACTORS['custom_fuel'] = 2.8e-3  # tonnes CO2e per liter
```

## Reporting Standards Support

### Supported Frameworks
- **GRI (Global Reporting Initiative)**: Comprehensive sustainability reporting
- **SASB (Sustainability Accounting Standards Board)**: Industry-specific standards
- **TCFD (Task Force on Climate-related Financial Disclosures)**: Climate risk reporting
- **CDP (Carbon Disclosure Project)**: Environmental disclosure
- **UN Global Compact**: Corporate sustainability initiative
- **ISO 14001**: Environmental management systems

### Custom Standards
The platform supports custom reporting frameworks through template configuration.

## Command Line Interface

### Available Commands

#### Data Management
```bash
smartgse data import-emissions <file>     # Import emission data
smartgse data import-metrics <file>       # Import sustainability metrics
```

#### Report Generation
```bash
smartgse report sustainability [options]  # Generate sustainability report
smartgse report carbon-tax [options]      # Generate carbon tax report
```

#### Data Analysis
```bash
smartgse analyze emissions <file>         # Analyze emission data
```

### CLI Options
Use `--help` with any command to see available options:
```bash
smartgse --help
smartgse report sustainability --help
```

## Output Formats

### PDF Reports
- Professional formatting with charts and tables
- Executive summary and detailed analysis
- Customizable branding and styling
- Print-ready layout

### Excel Exports
- Structured data sheets
- Pivot tables and calculations
- Charts and visualizations
- Template compatibility

### HTML Reports
- Interactive web-based reports
- Responsive design
- Embedded visualizations
- Easy sharing and collaboration

## Data Validation

SmartGSE includes comprehensive data validation:

### Emission Data Validation
- ✅ Positive values for emissions and activity data
- ✅ Consistent date ranges
- ✅ Calculation verification (activity × factor = CO2e)
- ✅ Reasonable value ranges
- ✅ Required field completeness

### Metrics Data Validation
- ✅ Valid category mappings
- ✅ Unit consistency
- ✅ Progress calculation accuracy
- ✅ Target value reasonableness
- ✅ Data source documentation

## Integration & Automation

### API Integration
SmartGSE can be integrated with existing systems through its Python API and CLI interface.

### Automated Workflows
Use the CLI in scripts and CI/CD pipelines for automated report generation:
```bash
#!/bin/bash
# Monthly sustainability report generation
smartgse data import-emissions data/monthly_emissions.csv
smartgse report sustainability --org-name "Company" --output-dir monthly_reports
```

### Database Connectivity
Extend the data processors to connect with databases and ERP systems.

## Contributing

We welcome contributions to SmartGSE! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Documentation updates
- Feature requests and bug reports

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation and examples
2. Search existing issues
3. Create a new issue with detailed information
4. Contact the development team

## Roadmap

### Upcoming Features
- 🔄 Real-time data integration APIs
- 📈 Advanced analytics and ML insights
- 🌐 Web dashboard interface
- 🔗 Third-party integrations (ERP, CRM systems)
- 📱 Mobile application
- 🏢 Multi-entity consolidation
- 🔒 Enhanced security and compliance features

## Examples and Templates

The `examples/` directory contains:
- Sample emission data files
- Sample sustainability metrics
- Report templates
- Configuration examples
- Integration scripts

## Technical Architecture

SmartGSE is built with:
- **Python 3.8+**: Core programming language
- **Pandas**: Data processing and analysis
- **ReportLab**: PDF report generation
- **Matplotlib/Seaborn**: Data visualization
- **Click**: CLI framework
- **Rich**: Enhanced CLI output
- **Pydantic**: Data validation and settings management

---

**SmartGSE** - Empowering organizations to achieve their sustainability goals through comprehensive ESG reporting and carbon tax management.
