# SmartGSE Examples

This directory contains example data files and usage examples for the SmartGSE platform.

## Sample Data Files

### sample_emissions.csv
Sample emission data showing various emission sources across different scopes:
- Scope 1: Direct emissions (fuel combustion, company vehicles)
- Scope 2: Indirect energy emissions (electricity)
- Scope 3: Other indirect emissions (business travel, waste)

### sample_metrics.csv
Sample sustainability metrics across ESG categories:
- Environmental: Energy intensity, water usage, waste diversion
- Social: Employee satisfaction, diversity, training
- Governance: Board independence, data privacy, supplier assessment

### sample_emissions.xlsx
Placeholder for Excel format emission data (same structure as CSV)

## Quick Start Examples

### Generate a Sustainability Report
```bash
smartgse report sustainability \
    --org-name "Example Corp" \
    --industry "Technology" \
    --year 2023 \
    --emissions-file examples/sample_emissions.csv \
    --metrics-file examples/sample_metrics.csv \
    --output-dir reports \
    --format both
```

### Generate a Carbon Tax Report
```bash
smartgse report carbon-tax \
    --org-name "Example Corp" \
    --industry "Technology" \
    --year 2023 \
    --emissions-file examples/sample_emissions.csv \
    --jurisdiction "California" \
    --tax-rate 25.00 \
    --currency USD \
    --output-dir reports \
    --format pdf
```

### Analyze Emission Data
```bash
smartgse analyze emissions examples/sample_emissions.csv
```

### Import and Validate Data
```bash
# Validate emissions data
smartgse data import-emissions examples/sample_emissions.csv --validate

# Validate sustainability metrics
smartgse data import-metrics examples/sample_metrics.csv --validate
```

## Data Format Guidelines

### Emission Data Requirements
- **Source**: Must match supported emission sources (electricity, fuel_combustion, etc.)
- **Scope**: Must be scope_1, scope_2, or scope_3
- **CO2e**: Positive numeric value in tonnes
- **Activity Data**: Positive numeric value
- **Dates**: Valid date format (YYYY-MM-DD)

### Sustainability Metrics Requirements
- **Category**: Must be environmental, social, or governance
- **Metric Name**: Descriptive name for the metric
- **Value**: Numeric or text value
- **Unit**: Unit of measurement
- **Target**: Optional target value for progress tracking

## Custom Data Templates

You can create your own data files using these examples as templates. Ensure:
1. Column names match the expected format
2. Data types are correct (numbers, dates, text)
3. Required fields are populated
4. Values are within reasonable ranges

## Integration Examples

### Python API Usage
```python
from smartgse.data.processors import DataImporter
from smartgse.reports.sustainability import SustainabilityReport

# Import data
importer = DataImporter()
emissions = importer.import_emissions_from_excel('sample_emissions.xlsx')
metrics = importer.import_metrics_from_excel('sample_metrics.xlsx')

# Generate report
config = create_report_config()  # Your configuration
report = SustainabilityReport(config)
report.add_emission_data(emissions)
report.add_sustainability_metrics(metrics)
pdf_file = report.export_to_pdf()
```

### Batch Processing
```bash
#!/bin/bash
# Process multiple files
for file in data/*.csv; do
    echo "Processing $file"
    smartgse data import-emissions "$file" --validate --output "processed_$file"
done
```

## Customization

### Adding Custom Emission Sources
Extend the emission sources in your data by using the 'other' category and providing detailed notes.

### Custom Metrics
Add organization-specific metrics by following the same format as the sample metrics file.

### Report Branding
Reports can be customized with organization branding through the configuration system.

## Troubleshooting

### Common Issues
1. **Date Format Errors**: Ensure dates are in YYYY-MM-DD format
2. **Missing Columns**: Check that all required columns are present
3. **Invalid Categories**: Use only supported categories (environmental, social, governance)
4. **Calculation Inconsistencies**: Verify that CO2e = Activity Data × Emission Factor

### Getting Help
- Run commands with `--help` flag for detailed options
- Check the main README.md for comprehensive documentation
- Validate your data before generating reports