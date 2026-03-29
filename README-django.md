# Sigma to Django Analytic Converter

## Overview

This script converts SIGMA rules from the [ConvertSigmaRepo2SentinelOnePQ](https://github.com/wikijm/ConvertSigmaRepo2SentinelOnePQ) repository into Django `Analytic` objects for a Django-based threat hunting application.

The script:
- Downloads SIGMA rules translated to PowerQuery format
- Parses rule metadata (title, description, MITRE techniques, references, etc.)
- Creates or updates `Analytic` objects in your Django database
- Automatically links MITRE techniques, tags, and target OS
- Handles duplicates by updating existing analytics

## Prerequisites

1. **Django Application**: You must have a Django application with the `Analytic` model and related models defined.

2. **Required Models**: The script expects these models in your Django app:
   - `Analytic` (main model with all fields as specified)
   - `Connector` (for query execution)
   - `Category` (optional categorization)
   - `Tag` (for tagging analytics)
   - `MitreTechnique` (MITRE ATT&CK techniques)
   - `ThreatName`, `ThreatActor`, `TargetOs`, `Vulnerability` (related models)

3. **Python Dependencies**:
   ```bash
   pip install django pyyaml requests
   ```

## Configuration

Before running the script, update these configuration variables in `sigma-to-django.py`:

```python
# Line 17-18: Update these with your actual values
DEFAULT_CONNECTOR_ID = 1  # ID of your default connector
DEFAULT_CATEGORY_ID = None  # ID of your default category (optional)

# Line 25-29: Update the import statement with your app name
from your_app.models import (  # Replace 'your_app' with your actual app name
    Analytic, Connector, Category, Tag, MitreTechnique,
    ThreatName, ThreatActor, TargetOs, Vulnerability
)
```

## Usage

### Method 1: Using Django Shell (Recommended)

```bash
# Navigate to your Django project directory
cd /path/to/your/django/project

# Copy the script to your project directory
cp sigma-to-django.py .

# Run the script through Django shell
python manage.py shell < sigma-to-django.py
```

### Method 2: Using django-extensions runscript

If you have `django-extensions` installed:

```bash
# Install django-extensions if not already installed
pip install django-extensions

# Add to INSTALLED_APPS in settings.py
# INSTALLED_APPS = [
#     ...
#     'django_extensions',
# ]

# Create a scripts directory in your app
mkdir -p your_app/scripts

# Copy the script to the scripts directory
cp sigma-to-django.py your_app/scripts/

# Run the script
python manage.py runscript sigma-to-django
```

### Method 3: Custom Management Command

Create a custom Django management command:

```bash
# Create the management command file
mkdir -p your_app/management/commands
```

Create `your_app/management/commands/import_sigma_rules.py`:

```python
from django.core.management.base import BaseCommand
import sys
import os

class Command(BaseCommand):
    help = 'Import Sigma rules as Analytics'

    def handle(self, *args, **options):
        # Add the script directory to path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(script_dir, '../../..'))
        
        # Import and run the converter
        from sigma_to_django import SigmaToDjango
        converter = SigmaToDjango()
        converter.process_files()
```

Then run:
```bash
python manage.py import_sigma_rules
```

## What the Script Does

1. **Setup Phase**:
   - Connects to your Django database
   - Gets the default user (first superuser or any user)
   - Gets the specified connector
   - Creates "From SIGMA" tag if it doesn't exist

2. **Download Phase**:
   - Downloads the latest Sigma rules repository
   - Extracts markdown files containing converted rules

3. **Processing Phase**:
   - For each markdown file:
     - Extracts PowerQuery and SIGMA YAML
     - Parses metadata (title, description, MITRE techniques, etc.)
     - Creates or updates the Analytic object
     - Links MITRE techniques
     - Adds "From SIGMA" tag
     - Sets Windows as default target OS

4. **Reporting Phase**:
   - Displays summary of created/updated analytics
   - Logs any errors to `errors.log`

## Field Mapping

| SIGMA Field | Analytic Field | Mapping Logic |
|-------------|----------------|---------------|
| title | name | Direct mapping |
| description | description | Direct mapping |
| PowerQuery | query | Extracted from markdown |
| tags (attack.t*) | mitre_techniques | Extracted and linked as ManyToMany |
| references | references | Joined with newlines |
| level | confidence | critical=4, high=3, medium=2, low=1 |
| - | status | Always set to 'DRAFT' |
| - | relevance | Default: 2 (Medium) |
| - | run_daily | Default: True |
| - | columns | SentinelOne default columns |
| - | tags | "From SIGMA" tag added |
| - | target_os | Windows (default) |

## Output Example

```
================================================================================
SIGMA TO DJANGO ANALYTIC CONVERTER
================================================================================

Setup complete:
  - User: admin
  - Connector: SentinelOne Connector
  - Sigma Tag: From SIGMA

Downloading repository from https://github.com/...
Download and extraction successful.

Found 1245 markdown files to process.

✓ Created: Possible DLL Hijacking of d3d11.dll
✓ Created: Possible DLL Hijacking of dhcpcsvc.dll
↻ Updated: Suspicious PowerShell Commands
...

Progress: 50/1245 files processed...

================================================================================
SUMMARY
================================================================================
Analytics created: 1198
Analytics updated: 42
Errors: 5

Total processed: 1240

Check errors.log for error details.
================================================================================
```

## Error Handling

- Errors are logged to `errors.log` with timestamps
- The script continues processing even if individual rules fail
- Common errors:
  - Missing connector (fix: create a connector first)
  - Invalid YAML in Sigma rules (logged and skipped)
  - Empty queries (skipped)
  - Duplicate names (updates existing analytic)

## Notes

- **Duplicate Handling**: If an analytic with the same name exists, it will be updated with new values
- **Default Values**: Status is set to 'DRAFT' so you can review before publishing
- **MITRE Techniques**: Automatically creates MitreTechnique objects if they don't exist
- **Performance**: Processes ~1200+ rules in a few minutes depending on network speed
- **Cleanup**: The downloaded repository is automatically cleaned up after processing

## Customization

You can customize the script by modifying:

1. **Default Status**: Change `status='DRAFT'` to `status='PUB'` (line 161)
2. **Default Relevance**: Change `relevance=2` to your preferred value (line 164)
3. **Columns Format**: Modify `default_columns` variable (line 285)
4. **Target OS**: Change from Windows to Linux/macOS (line 224)
5. **Connector Assignment**: Modify connector selection logic (lines 82-88)

## Troubleshooting

### Error: "No connector found"
Create at least one Connector object in your database before running the script.

### Error: "Could not import Django models"
Make sure you're running the script within Django environment using one of the methods above.

### Error: "UNIQUE constraint failed: analytic.name"
This shouldn't happen as the script uses `get_or_create()`, but if it does, check for issues with Unicode characters in rule names.

### Error: "cannot import name 'Analytic'"
Update the import statement (lines 25-29) with your actual app name.

## License

MIT License - Same as the original sigma-to-deephunter project.

## Credits

- Original Sigma rules: [SigmaHQ](https://github.com/SigmaHQ/sigma)
- PowerQuery conversion: [ConvertSigmaRepo2SentinelOnePQ](https://github.com/wikijm/ConvertSigmaRepo2SentinelOnePQ)
- Based on: [from-sigma-to-deephunter](https://github.com/wikijm/from-sigma-to-deephunter)
