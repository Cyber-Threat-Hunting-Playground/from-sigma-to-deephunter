# 📚 Django Version - Complete Documentation Index

Welcome to the Django-based Sigma to Analytics converter documentation!

## 🚀 Quick Navigation

### Getting Started (Start Here!)
1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ **START HERE**
   - 5-minute setup guide
   - Pre-flight checklist
   - Three different installation methods
   - Common configurations
   - Perfect for first-time users

### Main Documentation
2. **[README-django.md](README-django.md)** 📖 **COMPLETE REFERENCE**
   - Full documentation (300+ lines)
   - Detailed configuration instructions
   - All usage methods explained
   - Field mapping reference
   - Troubleshooting guide
   - Customization options

### Visual Guides
3. **[WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md)** 📊 **VISUAL GUIDE**
   - Process flow diagrams
   - Data flow visualization
   - Architecture diagrams
   - Database schema relationships
   - Processing logic flowcharts

4. **[COMPARISON.md](COMPARISON.md)** ⚖️ **VS ORIGINAL**
   - Original vs Django comparison
   - Feature comparison table
   - Use case recommendations
   - Performance comparison
   - Migration paths

### File Reference
5. **[FILES-SUMMARY.md](FILES-SUMMARY.md)** 📦 **FILES OVERVIEW**
   - What each file does
   - Which file to use when
   - Feature comparison
   - Implementation checklist

6. **[CHANGELOG.md](CHANGELOG.md)** 📜 **VERSION HISTORY**
   - All fixes and updates
   - Known issues resolved
   - Compatibility information
   - Migration notes

## 📁 Code Files

### Main Scripts (Choose One)

#### Option 1: Standalone Script
- **[sigma-to-django.py](sigma-to-django.py)**
  - Run via Django shell: `python manage.py shell < sigma-to-django.py`
  - Simpler, less features
  - Easy to customize directly

#### Option 2: Management Command (Recommended)
- **[import_sigma_rules.py](import_sigma_rules.py)**
  - Native Django command: `python manage.py import_sigma_rules`
  - More features (dry-run, CLI args)
  - Better Django integration

### Dependencies
- **[requirements-django.txt](requirements-django.txt)**
  - Python packages needed
  - Install: `pip install -r requirements-django.txt`

## 🎯 Documentation by User Type

### 👶 First-Time Users
**Recommended Path:**
1. Read: [QUICKSTART.md](QUICKSTART.md)
2. Install: Dependencies from [requirements-django.txt](requirements-django.txt)
3. Use: [import_sigma_rules.py](import_sigma_rules.py) with `--dry-run`
4. Reference: [README-django.md](README-django.md) if needed

### 👨‍💻 Django Developers
**Recommended Path:**
1. Skim: [README-django.md](README-django.md) (architecture section)
2. Review: [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) (data model)
3. Choose: [sigma-to-django.py](sigma-to-django.py) or [import_sigma_rules.py](import_sigma_rules.py)
4. Customize: Based on your models

### 🔄 Migrating from Original
**Recommended Path:**
1. Read: [COMPARISON.md](COMPARISON.md)
2. Review: [README-django.md](README-django.md) (migration section)
3. Test: [import_sigma_rules.py](import_sigma_rules.py) with `--dry-run`
4. Import: Run without `--dry-run`

### 🎨 Visual Learners
**Recommended Path:**
1. Start: [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md)
2. Compare: [COMPARISON.md](COMPARISON.md) (diagrams)
3. Quick start: [QUICKSTART.md](QUICKSTART.md)
4. Deep dive: [README-django.md](README-django.md)

## 📋 Documentation by Topic

### Setup & Installation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup (Steps 1-3)
- [README-django.md](README-django.md) - Prerequisites section
- [requirements-django.txt](requirements-django.txt) - Dependencies

### Configuration
- [QUICKSTART.md](QUICKSTART.md) - Common configurations
- [README-django.md](README-django.md) - Configuration section
- [FILES-SUMMARY.md](FILES-SUMMARY.md) - Customization guide

### Usage
- [QUICKSTART.md](QUICKSTART.md) - Three usage methods
- [README-django.md](README-django.md) - Usage section (all methods)
- [import_sigma_rules.py](import_sigma_rules.py) - Management command code

### Understanding the Code
- [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) - All flowcharts
- [FILES-SUMMARY.md](FILES-SUMMARY.md) - How files relate
- [sigma-to-django.py](sigma-to-django.py) - Commented source code

### Troubleshooting
- [QUICKSTART.md](QUICKSTART.md) - Common issues
- [README-django.md](README-django.md) - Troubleshooting section
- [COMPARISON.md](COMPARISON.md) - Understanding differences

### Advanced Topics
- [README-django.md](README-django.md) - Customization section
- [COMPARISON.md](COMPARISON.md) - Migration paths
- [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) - Database schema

## 🎓 Learning Path

### Beginner Path (30 minutes)
```
1. QUICKSTART.md (10 min)
   ↓
2. Install dependencies (5 min)
   ↓
3. Configure script (5 min)
   ↓
4. Run with --dry-run (5 min)
   ↓
5. Review output (5 min)
```

### Intermediate Path (1 hour)
```
1. QUICKSTART.md (10 min)
   ↓
2. WORKFLOW-DIAGRAM.md (15 min)
   ↓
3. Configure & test (10 min)
   ↓
4. Run import (15 min)
   ↓
5. README-django.md (troubleshooting) (10 min)
```

### Advanced Path (2 hours)
```
1. README-django.md (full read) (30 min)
   ↓
2. WORKFLOW-DIAGRAM.md (detailed study) (20 min)
   ↓
3. COMPARISON.md (understand differences) (20 min)
   ↓
4. Review source code (20 min)
   ↓
5. Customize for your needs (30 min)
```

## 🔍 Find Information By...

### By Question

| Question | Document |
|----------|----------|
| How do I get started? | [QUICKSTART.md](QUICKSTART.md) |
| What does this file do? | [FILES-SUMMARY.md](FILES-SUMMARY.md) |
| How does it work? | [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) |
| Which version should I use? | [COMPARISON.md](COMPARISON.md) |
| How do I configure X? | [README-django.md](README-django.md) |
| What are the CLI options? | [import_sigma_rules.py](import_sigma_rules.py) --help |
| How do I troubleshoot? | [README-django.md](README-django.md) or [QUICKSTART.md](QUICKSTART.md) |
| Can I customize Y? | [FILES-SUMMARY.md](FILES-SUMMARY.md) - Customization |

### By Error Message

| Error | Solution Location |
|-------|-------------------|
| "No connector found" | [QUICKSTART.md](QUICKSTART.md) - Troubleshooting |
| "Could not import models" | [README-django.md](README-django.md) - Configuration |
| "No users found" | [QUICKSTART.md](QUICKSTART.md) - Troubleshooting |
| Import errors | [README-django.md](README-django.md) - Troubleshooting |
| Database errors | [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) - Schema |

### By Task

| Task | Document |
|------|----------|
| Install | [QUICKSTART.md](QUICKSTART.md) - Step 1 |
| Configure | [QUICKSTART.md](QUICKSTART.md) - Step 2 |
| Test | [QUICKSTART.md](QUICKSTART.md) - Step 3 (dry-run) |
| Import | [README-django.md](README-django.md) - Usage |
| Customize | [FILES-SUMMARY.md](FILES-SUMMARY.md) - Customization |
| Migrate data | [COMPARISON.md](COMPARISON.md) - Migration |
| Understand flow | [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md) |

## 📱 Quick Reference Cards

### Installation Cheat Sheet
```bash
# 1. Install
pip install -r requirements-django.txt

# 2. Configure (edit these lines)
# sigma-to-django.py: Line 17-18, 25-29
# OR
# import_sigma_rules.py: Line 12

# 3. Test
python manage.py import_sigma_rules --dry-run

# 4. Import
python manage.py import_sigma_rules
```

### Configuration Cheat Sheet
```python
# In sigma-to-django.py or import_sigma_rules.py

DEFAULT_CONNECTOR_ID = 1           # Line 17
DEFAULT_CATEGORY_ID = None         # Line 18

from your_app.models import (     # Line 25-29
    Analytic, Connector, ...       # Update 'your_app'
)
```

### Usage Cheat Sheet
```bash
# Method 1: Shell
python manage.py shell < sigma-to-django.py

# Method 2: Management Command
python manage.py import_sigma_rules [options]

# Method 3: Django Extensions
python manage.py runscript sigma-to-django
```

## 🎯 Recommended Reading Order

### For Quick Start
1. [QUICKSTART.md](QUICKSTART.md)
2. [FILES-SUMMARY.md](FILES-SUMMARY.md)

### For Understanding
1. [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md)
2. [COMPARISON.md](COMPARISON.md)
3. [README-django.md](README-django.md)

### For Implementation
1. [README-django.md](README-django.md)
2. [import_sigma_rules.py](import_sigma_rules.py)
3. [QUICKSTART.md](QUICKSTART.md)

## 📞 Support Resources

### Documentation Files
- **Quick Help:** [QUICKSTART.md](QUICKSTART.md)
- **Detailed Help:** [README-django.md](README-django.md)
- **Visual Help:** [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md)
- **Comparison Help:** [COMPARISON.md](COMPARISON.md)

### Code Files
- **Simple Version:** [sigma-to-django.py](sigma-to-django.py)
- **Advanced Version:** [import_sigma_rules.py](import_sigma_rules.py)

### Log Files
- **Error Log:** `errors.log` (created during execution)

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-25 | Initial Django version release |

## 📝 Related Files (Original Project)

- **[sigma-to-deephunter.py](sigma-to-deephunter.py)** - Original script (JSON output)
- **[README.md](README.md)** - Original documentation
- **[requirements.txt](requirements.txt)** - Original dependencies

## 🎁 What You Get

After reading the documentation and running the import:

✅ Understanding of how it works ([WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md))  
✅ Configured import script ([QUICKSTART.md](QUICKSTART.md))  
✅ ~1,200 Analytics in database  
✅ MITRE techniques linked  
✅ Tags applied  
✅ Ready-to-use threat hunting rules  

## 🚀 Next Steps

1. **New User?** → Start with [QUICKSTART.md](QUICKSTART.md)
2. **Need Details?** → Read [README-django.md](README-django.md)
3. **Visual Learner?** → See [WORKFLOW-DIAGRAM.md](WORKFLOW-DIAGRAM.md)
4. **Have Original?** → Check [COMPARISON.md](COMPARISON.md)
5. **Ready to Code?** → Use [import_sigma_rules.py](import_sigma_rules.py)

---

**Happy Hunting! 🎯**

*For questions about the original project, see [README.md](README.md)*  
*For questions about Django version, see [README-django.md](README-django.md)*
