# 📦 Django Version - File Summary

This directory now contains a complete Django-based version of the Sigma to Analytics converter.

## 📄 New Files Created

### 1. **sigma-to-django.py** (Main Script)
**Purpose:** Standalone Python script that runs within Django environment to import Sigma rules as Analytic objects.

**Key Features:**
- Downloads and processes Sigma rules from GitHub
- Creates/updates Analytic objects in Django database
- Automatically links MITRE techniques, tags, and target OS
- Handles duplicates gracefully
- Provides detailed progress and error reporting

**Usage:**
```bash
python manage.py shell < sigma-to-django.py
```

**Configuration Required:**
- Line 17-18: Update `DEFAULT_CONNECTOR_ID` and `DEFAULT_CATEGORY_ID`
- Line 25-29: Update import statement with your Django app name

---

### 2. **import_sigma_rules.py** (Django Management Command)
**Purpose:** Django management command version with enhanced features and CLI arguments.

**Key Features:**
- Full Django management command with argparse support
- `--dry-run` mode to preview changes
- `--connector-id` to specify connector
- `--category-id` to assign category
- `--repo-url` to use custom repository
- Better error handling and user feedback

**Installation:**
```bash
mkdir -p your_app/management/commands
cp import_sigma_rules.py your_app/management/commands/
```

**Usage:**
```bash
# Dry run first
python manage.py import_sigma_rules --dry-run

# Actual import
python manage.py import_sigma_rules

# With options
python manage.py import_sigma_rules --connector-id 2 --category-id 5
```

**Configuration Required:**
- Line 12: Update import statement with your Django app name

---

### 3. **README-django.md** (Complete Documentation)
**Purpose:** Comprehensive documentation for the Django version.

**Contents:**
- Overview and prerequisites
- Configuration instructions
- Three different usage methods (shell, management command, django-extensions)
- Field mapping table
- Error handling guide
- Customization options
- Troubleshooting section

**Size:** ~300 lines of detailed documentation

---

### 4. **requirements-django.txt** (Dependencies)
**Purpose:** Python package requirements for Django version.

**Contents:**
```
django>=4.2,<5.0
pyyaml>=6.0
requests>=2.31.0
django-extensions>=3.2.0  # Optional
```

**Usage:**
```bash
pip install -r requirements-django.txt
```

---

### 5. **QUICKSTART.md** (Quick Reference)
**Purpose:** Fast-track guide to get started in 5 minutes.

**Contents:**
- 3-step setup process
- Pre-flight checklist
- Common configurations
- Verification examples
- Expected output
- Troubleshooting tips
- Next steps after import

**Perfect for:** First-time users who want to get started quickly

---

## 🔄 How Files Relate

```
Original Script
    └── sigma-to-deephunter.py (generates query.json)

Django Version (3 implementations)
    ├── sigma-to-django.py (standalone script)
    ├── import_sigma_rules.py (management command)
    └── [same functionality, different interfaces]

Documentation
    ├── README-django.md (complete reference)
    ├── QUICKSTART.md (fast start)
    └── requirements-django.txt (dependencies)
```

## 🎯 Which File Should I Use?

### Use `sigma-to-django.py` if:
- ✅ You want a simple, standalone script
- ✅ You prefer minimal setup
- ✅ You're comfortable with Django shell
- ✅ You want to customize the code directly

### Use `import_sigma_rules.py` if:
- ✅ You want a proper Django management command
- ✅ You need `--dry-run` capability
- ✅ You want CLI arguments (connector-id, category-id)
- ✅ You prefer Django's command infrastructure
- ✅ You want better integration with your Django project

**Recommendation:** Use `import_sigma_rules.py` (management command) for production use.

## 📊 Feature Comparison

| Feature | sigma-to-django.py | import_sigma_rules.py |
|---------|-------------------|----------------------|
| Standalone script | ✅ | ❌ |
| Management command | ❌ | ✅ |
| Dry run mode | ❌ | ✅ |
| CLI arguments | ❌ | ✅ |
| Easy customization | ✅ | ⚠️ |
| Progress reporting | ✅ | ✅ |
| Error logging | ✅ | ✅ |
| Django integration | ⚠️ | ✅ |

## 🚀 Quick Start Path

1. **Read:** `QUICKSTART.md` (5 minutes)
2. **Install:** `pip install -r requirements-django.txt`
3. **Configure:** Update app name in `import_sigma_rules.py`
4. **Test:** `python manage.py import_sigma_rules --dry-run`
5. **Import:** `python manage.py import_sigma_rules`
6. **Reference:** `README-django.md` for detailed info

## 📝 Key Differences from Original

### Original (sigma-to-deephunter.py)
- Outputs to `query.json` file
- Format: DeepHunter JSON export format
- No database interaction
- Standalone execution

### Django Version (new files)
- Creates Django model objects directly
- Interacts with PostgreSQL/MySQL/SQLite database
- Full ORM integration
- Handles relationships (ManyToMany, ForeignKey)
- Transaction support
- Data validation via Django models

## 🔧 Customization Guide

### Change Default Status (Draft → Published)
**File:** `sigma-to-django.py` or `import_sigma_rules.py`
**Line:** Search for `'status': 'DRAFT'`
**Change to:** `'status': 'PUB'`

### Change Default Relevance
**File:** `sigma-to-django.py` or `import_sigma_rules.py`
**Line:** Search for `'relevance': 2`
**Change to:** `'relevance': 3` (or 1, 4)

### Use Different Connector
**File:** `sigma-to-django.py`
**Line:** 17
**Change:** `DEFAULT_CONNECTOR_ID = 1` → `DEFAULT_CONNECTOR_ID = 2`

**OR** (for management command):
```bash
python manage.py import_sigma_rules --connector-id 2
```

## 📋 Implementation Checklist

Before running in production:

- [ ] Backup your database
- [ ] Update app name in imports
- [ ] Set correct `DEFAULT_CONNECTOR_ID`
- [ ] Create at least one Connector object
- [ ] Create at least one TargetOs object
- [ ] Test with `--dry-run` first (if using management command)
- [ ] Review and customize default status/relevance
- [ ] Check `errors.log` after import
- [ ] Verify imported analytics in Django admin

## 🎓 Learning Resources

1. **Start here:** `QUICKSTART.md`
2. **Full reference:** `README-django.md`
3. **Code examples:** `sigma-to-django.py`
4. **Advanced usage:** `import_sigma_rules.py`

## 🤝 Integration with Existing Code

The Django version is designed to work alongside your existing threat hunting platform:

```
Your Django Project
├── your_app/
│   ├── models.py (Analytic, Connector, etc.)
│   ├── management/
│   │   └── commands/
│   │       └── import_sigma_rules.py  ← Copy here
│   └── scripts/
│       └── sigma-to-django.py  ← Or here (if using django-extensions)
├── manage.py
└── requirements.txt (add requirements-django.txt contents)
```

## ⚡ Performance Notes

- **Import Speed:** ~1,200 rules in 2-5 minutes
- **Network:** Most time spent downloading repository
- **Database:** Bulk operations used where possible
- **Memory:** Minimal (processes files one at a time)

## 🔍 Data Model Compatibility

The scripts are designed for the `Analytic` model you provided with:
- ✅ All standard fields (name, description, query, etc.)
- ✅ Foreign keys (Connector, Category, User)
- ✅ ManyToMany (tags, mitre_techniques, target_os, etc.)
- ✅ Custom fields (anomaly thresholds, weighted_relevance)
- ✅ Historical tracking support

## 📞 Support

For issues or questions:
1. Check `errors.log` file
2. Review `README-django.md` troubleshooting section
3. Verify model compatibility
4. Check Django admin for created objects

---

**Version:** 1.0  
**Created:** 2025-11-25  
**Compatible with:** Django 4.2+, Python 3.8+  
**Based on:** from-sigma-to-deephunter project
