# Workflow Diagram - Sigma to Django Analytics

## 📊 Overall Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIGMA TO DJANGO WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. DOWNLOAD PHASE
   ┌──────────────────────────────────────────┐
   │ GitHub Repository                        │
   │ (ConvertSigmaRepo2SentinelOnePQ)         │
   │                                          │
   │ • Sigma rules (YAML)                     │
   │ • Converted to PowerQuery (.md files)    │
   └─────────────────┬────────────────────────┘
                     │ Downloads & Extracts
                     ▼
   ┌──────────────────────────────────────────┐
   │ Local Repository                         │
   │ ~/local_repo/                            │
   │ └── *.md files (~1,200+)                 │
   └─────────────────┬────────────────────────┘
                     │

2. PARSING PHASE
                     │ Reads each .md file
                     ▼
   ┌──────────────────────────────────────────┐
   │ Extract from Markdown:                   │
   │ ┌──────────────────────────────────────┐ │
   │ │ Line 3: PowerQuery code              │ │
   │ └──────────────────────────────────────┘ │
   │ ┌──────────────────────────────────────┐ │
   │ │ YAML Block: Sigma rule metadata      │ │
   │ │ • title                              │ │
   │ │ • description                        │ │
   │ │ • tags (MITRE ATT&CK)                │ │
   │ │ • references                         │ │
   │ │ • level (critical/high/medium/low)   │ │
   │ └──────────────────────────────────────┘ │
   └─────────────────┬────────────────────────┘
                     │ Parse YAML

3. TRANSFORMATION PHASE
                     ▼
   ┌──────────────────────────────────────────┐
   │ Map to Django Model Fields:              │
   │                                          │
   │ Sigma Field      →  Analytic Field       │
   │ ───────────────────────────────────────  │
   │ title            →  name                 │
   │ description      →  description          │
   │ PowerQuery       →  query                │
   │ level            →  confidence (1-4)     │
   │ attack.t1234     →  mitre_techniques     │
   │ references       →  references           │
   │ [default]        →  status = 'DRAFT'     │
   │ [default]        →  relevance = 2        │
   │ [default]        →  columns = "..."      │
   └─────────────────┬────────────────────────┘
                     │

4. DATABASE PHASE
                     ▼
   ┌──────────────────────────────────────────┐
   │ Django ORM Operations:                   │
   │                                          │
   │ 1. Get or Create Analytic                │
   │    ├─ If NEW  → Create object            │
   │    └─ If EXISTS → Update object          │
   │                                          │
   │ 2. Add ManyToMany Relationships          │
   │    ├─ Tags (From SIGMA)                  │
   │    ├─ MITRE Techniques                   │
   │    └─ Target OS (Windows)                │
   │                                          │
   │ 3. Set Foreign Keys                      │
   │    ├─ Connector                          │
   │    ├─ Category (optional)                │
   │    └─ User (created_by)                  │
   └─────────────────┬────────────────────────┘
                     │ Commit to DB
                     ▼
   ┌──────────────────────────────────────────┐
   │ PostgreSQL / MySQL / SQLite              │
   │                                          │
   │ Tables:                                  │
   │ • analytics                              │
   │ • analytics_tags (M2M)                   │
   │ • analytics_mitre_techniques (M2M)       │
   │ • analytics_target_os (M2M)              │
   │ • tags                                   │
   │ • mitre_techniques                       │
   │ • target_os                              │
   └──────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  GitHub  │────▶│   .md     │────▶│  Parser  │────▶│  Django  │
│   Repo   │      │  Files   │      │          │      │  Models  │
└──────────┘      └──────────┘      └──────────┘      └──────────┘
    HTTP              Local           Python            ORM
  Download          Storage          Extract         Database
```

## 🏗️ Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Django Project                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     Your Django App                     │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │              Models (models.py)                  │   │    │
│  │  │  • Analytic                                      │   │    │
│  │  │  • Connector                                     │   │    │
│  │  │  • Category                                      │   │    │
│  │  │  • Tag                                           │   │    │
│  │  │  • MitreTechnique                                │   │    │
│  │  │  • TargetOs, ThreatName, etc.                    │   │    │
│  │  └─────────────────────┬────────────────────────────┘   │    │
│  │                        │                                │    │
│  │  ┌─────────────────────▼────────────────────────────┐   │    │
│  │  │        Management Commands                       │   │    │
│  │  │  management/commands/import_sigma_rules.py       │   │    │
│  │  │                                                  │   │    │
│  │  │  • Downloads Sigma rules                         │   │    │
│  │  │  • Parses markdown/YAML                          │   │    │
│  │  │  • Creates/updates Analytics                     │   │    │
│  │  │  • Links relationships                           │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  OR                                                     │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │        Django Shell Script                       │   │    │
│  │  │  scripts/sigma-to-django.py                      │   │    │
│  │  │                                                  │   │    │
│  │  │  [Same functionality as management command]      │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Database (ORM)                         │    │
│  │  • PostgreSQL / MySQL / SQLite                          │    │
│  │  • Stores all Analytic objects                          │    │
│  │  • Maintains relationships                              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Execution Methods

```
Method 1: Django Shell
┌──────────────────────────────────────┐
│ $ python manage.py shell             │
│   < sigma-to-django.py               │
└──────────────────────────────────────┘
         │
         ▼
   Executes script in Django context

Method 2: Management Command
┌──────────────────────────────────────┐
│ $ python manage.py import_sigma_rules│
│   --connector-id 2                   │
│   --dry-run                          │
└──────────────────────────────────────┘
         │
         ▼
   Native Django command with args

Method 3: Django Extensions
┌──────────────────────────────────────┐
│ $ python manage.py runscript         │
│   sigma-to-django                    │
└──────────────────────────────────────┘
         │
         ▼
   Via django-extensions package
```

## 📦 Database Schema Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                          ANALYTIC                               │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ PK: id                                                       ││
│ │ name (unique)                                                ││
│ │ description                                                  ││
│ │ query                                                        ││
│ │ columns                                                      ││
│ │ status (DRAFT/PUB/REVIEW/ARCH/PENDING)                       ││
│ │ confidence (1-4)                                             ││
│ │ relevance (1-4)                                              ││
│ │ notes                                                        ││
│ │ references                                                   ││
│ │ run_daily, create_rule, dynamic_query                        ││
│ │ anomaly_threshold_count, anomaly_threshold_endpoints         ││
│ │ pub_date                                                     ││
│ │                                                              ││
│ │ FK: connector_id    ──────────────┐                          ││
│ │ FK: category_id     ──────────┐   │                          ││
│ │ FK: created_by_id   ──────┐   │   │                          ││
│ └───────────────────────────┼───┼───┼──────────────────────────┘│
│                             │   │   │                           │
│                             ▼   ▼   ▼                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                     │
│  │   User   │   │ Category │   │Connector │                     │
│  └──────────┘   └──────────┘   └──────────┘                     │
│                                                                 │
│  Many-to-Many Relationships:                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ analytic_tags               ← Tag                       │    │
│  │ analytic_mitre_techniques   ← MitreTechnique            │    │
│  │ analytic_threats            ← ThreatName                │    │
│  │ analytic_actors             ← ThreatActor               │    │
│  │ analytic_target_os          ← TargetOs                  │    │
│  │ analytic_vulnerabilities    ← Vulnerability             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🔀 Field Mapping Flowchart

```
┌─────────────────────┐
│   Sigma YAML        │
└──────────┬──────────┘
           │
           ├─── title ──────────────────────────▶ Analytic.name
           │
           ├─── description ────────────────────▶ Analytic.description
           │
           ├─── level ──┬─ critical ──▶ 4 ─────▶ Analytic.confidence
           │            ├─ high ──────▶ 3
           │            ├─ medium ────▶ 2
           │            └─ low ───────▶ 1
           │
           ├─── tags ───┬─ attack.t1234 ───────▶ MitreTechnique
           │            │                          (M2M link)
           │            └─ [auto] ────────────────▶ Tag("From SIGMA")
           │
           ├─── references ─────────────────────▶ Analytic.references
           │
           └─── [PowerQuery from line 3] ───────▶ Analytic.query

┌─────────────────────┐
│   Default Values    │
└──────────┬──────────┘
           │
           ├─── status = 'DRAFT' ───────────────▶ Analytic.status
           │
           ├─── relevance = 2 ──────────────────▶ Analytic.relevance
           │
           ├─── run_daily = True ───────────────▶ Analytic.run_daily
           │
           ├─── create_rule = False ────────────▶ Analytic.create_rule
           │
           ├─── anomaly_threshold_* = 2 ────────▶ Analytic.anomaly_threshold_*
           │
           ├─── columns = "[default]" ──────────▶ Analytic.columns
           │
           ├─── connector = [from config] ──────▶ Analytic.connector
           │
           ├─── created_by = [superuser] ───────▶ Analytic.created_by
           │
           └─── target_os = Windows ────────────▶ TargetOs (M2M)
```

## ⚙️ Processing Logic

```
For each .md file:
  │
  ├─ Parse file
  │   ├─ Extract PowerQuery (line 3)
  │   └─ Extract YAML block
  │
  ├─ Validate
  │   ├─ Has title? ───No──▶ Skip
  │   ├─ Has query? ───No──▶ Skip
  │   └─ Valid YAML? ──No──▶ Log error, skip
  │
  ├─ Check existence
  │   ├─ Analytic.name exists?
  │   │   ├─ Yes ──▶ UPDATE existing
  │   │   └─ No ───▶ CREATE new
  │
  ├─ Save Analytic object
  │
  ├─ Add relationships
  │   ├─ Tags
  │   ├─ MITRE Techniques (get_or_create)
  │   └─ Target OS
  │
  └─ Report status
      ├─ Created ──▶ ✓ Created: [name]
      ├─ Updated ──▶ ↻ Updated: [name]
      └─ Error ────▶ ✗ Error: [message]
```

## 📈 Progress Tracking

```
Start
  │
  ├─ Setup (1 second)
  │   ├─ Load Django models
  │   ├─ Get Connector
  │   ├─ Get/Create Tag
  │   └─ Get default User
  │
  ├─ Download (30-60 seconds)
  │   ├─ Download ZIP from GitHub
  │   ├─ Extract files
  │   └─ Delete ZIP
  │
  ├─ Process (2-5 minutes)
  │   ├─ File 1/1245 ──▶ Parse ──▶ Create ──▶ Link
  │   ├─ File 2/1245 ──▶ Parse ──▶ Update ──▶ Link
  │   ├─ File 3/1245 ──▶ Parse ──▶ Create ──▶ Link
  │   │   ...
  │   └─ Progress updates every 100 files
  │
  └─ Summary
      ├─ Created: 1198
      ├─ Updated: 42
      ├─ Errors: 5
      └─ Total: 1240
```

## 🔍 Dry Run Mode (Management Command Only)

```
With --dry-run flag:
  │
  ├─ Download repo ──▶ YES (needed for parsing)
  │
  ├─ Parse files ────▶ YES
  │
  ├─ Database ops ───▶ NO (simulation only)
  │   ├─ Check exists? ──▶ Report would create/update
  │   └─ No writes
  │
  └─ Summary ────────▶ Shows what WOULD happen
      │
      └─ "[DRY RUN] Would create: [name]"
          "[DRY RUN] Would update: [name]"
```

## 🎨 Visual Summary

```
╔═══════════════════════════════════════════════════════════════════╗
║                   SIGMA TO DJANGO ANALYTICS                       ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  INPUT:  Sigma rules (YAML) on GitHub                             ║
║          ↓                                                        ║
║  PROCESS: Download → Parse → Transform → Save                     ║
║          ↓                                                        ║
║  OUTPUT: ~1,200 Analytic objects in Django database               ║
║                                                                   ║
║  RELATIONSHIPS:                                                   ║
║    ├─ Tags (From SIGMA)                                           ║
║    ├─ MITRE Techniques (T1234, T1235, ...)                        ║
║    ├─ Target OS (Windows)                                         ║
║    ├─ Connector (SentinelOne/other)                               ║
║    └─ Created by User                                             ║
║                                                                   ║
║  FEATURES:                                                        ║
║    ✓ Duplicate handling (update existing)                         ║
║    ✓ Error logging                                                ║
║    ✓ Progress reporting                                           ║
║    ✓ Configurable defaults                                        ║
║    ✓ Dry run mode (management command)                            ║
╚═══════════════════════════════════════════════════════════════════╝
```
