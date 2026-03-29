# Quick Start Guide - Sigma to Django Analytics

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements-django.txt
```

### Step 2: Configure the Script

Edit `sigma-to-django.py` and update these lines:

```python
# Line 17-18: Set your IDs
DEFAULT_CONNECTOR_ID = 1  # Replace with your connector ID
DEFAULT_CATEGORY_ID = None  # Optional: set a category ID

# Line 25-29: Update your app name
from your_app.models import (  # Replace 'your_app'
    Analytic, Connector, Category, Tag, MitreTechnique,
    ThreatName, ThreatActor, TargetOs, Vulnerability
)
```

### Step 3: Choose Your Method

#### Option A: Django Shell (Simplest)
```bash
cd /path/to/your/django/project
cp /path/to/sigma-to-django.py .
python manage.py shell < sigma-to-django.py
```

#### Option B: Management Command (Recommended)
```bash
# 1. Copy the management command
mkdir -p your_app/management/commands
cp import_sigma_rules.py your_app/management/commands/

# 2. Update the import in import_sigma_rules.py (line 12)
# from your_app.models import ...  # Change 'your_app'

# 3. Run it
python manage.py import_sigma_rules

# With options:
python manage.py import_sigma_rules --connector-id 2
python manage.py import_sigma_rules --category-id 5
python manage.py import_sigma_rules --dry-run  # Test first!
```

#### Option C: Django Extensions (If Installed)
```bash
# 1. Install django-extensions
pip install django-extensions

# 2. Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    ...
    'django_extensions',
]

# 3. Create scripts directory
mkdir -p your_app/scripts

# 4. Copy script
cp sigma-to-django.py your_app/scripts/

# 5. Run it
python manage.py runscript sigma-to-django
```

## 📋 Pre-Flight Checklist

Before running, make sure you have:

- [ ] At least one `Connector` object in your database
- [ ] At least one `User` in your database
- [ ] At least one `TargetOs` object (e.g., "Windows")
- [ ] Updated the script with your app name
- [ ] Updated `DEFAULT_CONNECTOR_ID` if needed
- [ ] Tested with `--dry-run` first (if using management command)

## 🎯 What You'll Get

After running, you'll have:

- ✅ **~1,200+ Analytics** imported from Sigma rules
- ✅ All analytics tagged with **"From SIGMA"**
- ✅ **MITRE ATT&CK techniques** automatically linked
- ✅ **PowerQuery** format ready for SentinelOne
- ✅ Default status: **DRAFT** (review before publishing)
- ✅ Default columns for SentinelOne already configured

## ⚙️ Common Configurations

### Using a Different Connector
```python
# In sigma-to-django.py, line 17
DEFAULT_CONNECTOR_ID = 2  # Your connector ID
```

### Auto-Publish Rules (Skip Draft)
```python
# In sigma-to-django.py, line 161
'status': 'PUB',  # Change from 'DRAFT' to 'PUB'
```

### Higher Default Relevance
```python
# In sigma-to-django.py, line 164
'relevance': 3,  # Change from 2 to 3 (High)
```

### Different Target OS
```python
# In sigma-to-django.py, line 224
target_os = self.get_or_create_target_os('Linux')  # or 'macOS'
```

## 🔍 Verification

After running, verify in Django admin or shell:

```python
from your_app.models import Analytic, Tag

# Check total imported
sigma_tag = Tag.objects.get(name="From SIGMA")
sigma_analytics = Analytic.objects.filter(tags=sigma_tag)
print(f"Total Sigma analytics: {sigma_analytics.count()}")

# Check status distribution
from django.db.models import Count
stats = Analytic.objects.values('status').annotate(count=Count('id'))
print(f"Status distribution: {list(stats)}")

# Check MITRE technique coverage
total_with_mitre = Analytic.objects.filter(
    tags=sigma_tag,
    mitre_techniques__isnull=False
).distinct().count()
print(f"Analytics with MITRE techniques: {total_with_mitre}")
```

## 🐛 Troubleshooting

### Error: "No connector found"
```python
# Create a connector first
from your_app.models import Connector
connector = Connector.objects.create(
    name="Default Connector",
    # ... other required fields
)
```

### Error: "could not import name 'Analytic'"
- Make sure you updated line 25-29 with your actual app name
- Check that your models file has all required models

### Error: "No users found"
```bash
python manage.py createsuperuser
```

### Warning: Many errors in errors.log
- Most are due to empty/invalid Sigma rules - this is normal
- Check the log file to see if there are systematic issues

### Error: "CERTIFICATE_VERIFY_FAILED"
- Fixed: Script now uses verify=False for SSL connections
- If download fails, place 'ConvertSigmaRepo2SentinelOnePQ-main.zip' in same folder
- Script will automatically use local file if present

## 📊 Expected Output

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
✓ Created: Suspicious PowerShell Commands
↻ Updated: Known Malware Detection
...

================================================================================
SUMMARY
================================================================================
Analytics created: 1198
Analytics updated: 42
Errors: 5

Total processed: 1240
================================================================================
```

## 🔄 Re-running the Script

Safe to re-run! The script will:
- ✅ Skip existing analytics (or update them)
- ✅ Add new analytics that didn't exist before
- ✅ Update analytics if rule content changed
- ✅ Not create duplicates

## 📝 Next Steps

After importing:

1. **Review in Django Admin**
   - Go to `/admin/your_app/analytic/`
   - Filter by `tags = "From SIGMA"`
   
2. **Update Statuses**
   - Change from DRAFT to PUB for rules you want active
   
3. **Adjust Relevance/Confidence**
   - Review and adjust based on your environment
   
4. **Add to Campaigns**
   - Create threat hunting campaigns using these analytics
   
5. **Test Queries**
   - Validate queries work in your environment

## 📚 Full Documentation

See `README-django.md` for complete documentation including:
- Detailed field mapping
- Customization options
- Advanced usage
- Model requirements

## 💡 Tips

- **Use --dry-run first** to see what would be imported
- **Start with one category** using --category-id
- **Review errors.log** for any systematic issues
- **Backup your database** before first run (optional but recommended)
- **Run during off-hours** if you have a busy database

## 🤝 Need Help?

If you encounter issues:
1. Check `errors.log` for detailed error messages
2. Verify all prerequisites are met
3. Try --dry-run mode first
4. Check that your models match the expected structure

---
**Ready?** Just run: `python manage.py import_sigma_rules --dry-run` 🚀
