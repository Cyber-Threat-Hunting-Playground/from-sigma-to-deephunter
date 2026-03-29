"""
Django-based script to create Analytic objects from Sigma rules.
This script is designed to be run within a Django environment.

Usage:
    python manage.py shell < sigma-to-django.py
    OR
    python manage.py runscript sigma-to-django (if using django-extensions)
"""

import os
import re
import yaml
import requests
import zipfile
import django
from datetime import datetime

# Configuration
GITHUB_REPO_URL = 'https://github.com/wikijm/ConvertSigmaRepo2SentinelOnePQ/archive/refs/heads/main.zip'
LOCAL_REPO_PATH = 'local_repo'
ZIP_FILE_PATH = 'repo.zip'
ERRORS_LOG_PATH = 'errors.log'
DEFAULT_CONNECTOR_ID = 1  # Update this with your default connector ID
DEFAULT_CATEGORY_ID = None  # Update this with your default category ID if needed

# Django models (import after Django setup)
try:
    from django.contrib.auth.models import User
    from qm.models import (  # Replace 'your_app' with your actual app name
        Analytic, Connector, Category, Tag, MitreTechnique,
        ThreatName, ThreatActor, TargetOs, Vulnerability
    )
except ImportError:
    print("WARNING: Could not import Django models. Make sure to run this within Django environment.")
    print("Usage: python manage.py shell < sigma-to-django.py")


class SigmaToDjango:
    """Main class to handle Sigma rules to Django Analytic objects conversion."""
    
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.error_count = 0
        self.default_user = None
        self.default_connector = None
        self.sigma_tag = None
        
    def setup(self):
        """Setup required Django objects."""
        # Get or create default user (for created_by field)
        self.default_user = User.objects.filter(is_superuser=True).first()
        if not self.default_user:
            self.default_user = User.objects.first()
        
        # Get default connector
        try:
            self.default_connector = Connector.objects.get(id=DEFAULT_CONNECTOR_ID)
        except Connector.DoesNotExist:
            self.default_connector = Connector.objects.first()
            if not self.default_connector:
                raise Exception("No connector found. Please create a connector first.")
        
        # Get or create "From SIGMA" tag
        self.sigma_tag, _ = Tag.objects.get_or_create(
            name="From SIGMA"
        )
        
        print(f"Setup complete:")
        print(f"  - User: {self.default_user}")
        print(f"  - Connector: {self.default_connector}")
        print(f"  - Sigma Tag: {self.sigma_tag}")
    
    def download_and_extract_repo(self, repo_url, zip_path, extract_path):
        """Download and extract the GitHub repository."""
        # Check if local zip file exists first
        local_zip = 'ConvertSigmaRepo2SentinelOnePQ-main.zip'
        if os.path.exists(local_zip):
            print(f"Found local zip file: {local_zip}")
            zip_path = local_zip
            use_local = True
        else:
            use_local = False
        
        try:
            # Download from GitHub if local file doesn't exist
            if not use_local:
                print(f"Downloading repository from {repo_url}...")
                response = requests.get(repo_url, verify=False)
                response.raise_for_status()

                with open(zip_path, 'wb') as zip_file:
                    zip_file.write(response.content)
                print("Download successful.")

            print(f"Extracting to {extract_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Delete the zip file after extraction (only if downloaded)
            if not use_local and os.path.exists(zip_path):
                os.remove(zip_path)
            print("Extraction successful.")
            return True
        except requests.RequestException as e:
            self.log_error(f"Error downloading the repository: {e}")
            print(f"TIP: Place 'ConvertSigmaRepo2SentinelOnePQ-main.zip' in the same folder as this script.")
            return False
        except zipfile.BadZipFile as e:
            self.log_error(f"Error extracting the zip file: {e}")
            return False

    def get_md_files(self, local_path):
        """Get all .md files excluding README.md."""
        md_files = []
        for root, _, files in os.walk(local_path):
            for file in files:
                if file.endswith('.md') and file != 'README.md':
                    md_files.append(os.path.join(root, file))
        return md_files

    def extract_info(self, content):
        """Extract PowerQuery and SIGMA rule from markdown content."""
        lines = content.split('\n')
        powerquery = lines[2].strip() if len(lines) > 2 else ''
        sigma_rule = re.search(r'```yaml(.*?)```', content, re.DOTALL)
        sigma_rule = sigma_rule.group(1).strip() if sigma_rule else ''
        return powerquery, sigma_rule

    def parse_sigma_rule(self, sigma_rule):
        """Parse SIGMA rule and extract attributes."""
        try:
            sigma_data = yaml.safe_load(sigma_rule)
            if sigma_data is None:
                raise ValueError("Invalid or empty YAML content")

            description = sigma_data.get('description', '')
            title = sigma_data.get('title', '')
            tags = sigma_data.get('tags', [])
            references = sigma_data.get('references', [])
            level = sigma_data.get('level', '')

            # Extract MITRE ATT&CK technique IDs
            mitre_techniques = [
                tag.split('.')[1].upper() 
                for tag in tags 
                if tag.startswith('attack.t')
            ]

            return description, title, mitre_techniques, references, level
        except yaml.YAMLError as e:
            self.log_error(f"Error parsing the SIGMA rule: {e}")
            return '', '', [], [], ''
        except ValueError as e:
            self.log_error(f"YAML content error: {e}")
            return '', '', [], [], ''

    def get_or_create_mitre_techniques(self, technique_ids):
        """Get or create MITRE technique objects."""
        techniques = []
        for technique_id in technique_ids:
            if not technique_id or not technique_id.strip():
                continue  # Skip empty technique IDs
            
            # Try to find existing technique by name matching the ID
            technique = MitreTechnique.objects.filter(name__iexact=technique_id).first()
            if not technique:
                # If not found, create with the technique ID as name
                # Check if it's a subtechnique (contains a dot like T1234.001)
                is_subtechnique = '.' in technique_id
                try:
                    technique, _ = MitreTechnique.objects.get_or_create(
                        name=technique_id,
                        defaults={
                            'is_subtechnique': is_subtechnique,
                            'mitre_id': technique_id  # Set mitre_id to avoid duplicates
                        }
                    )
                except Exception as e:
                    # If there's a duplicate error or other issue, try to find it again
                    print(f'⚠ Could not create MITRE technique {technique_id}: {e}')
                    technique = MitreTechnique.objects.filter(name__iexact=technique_id).first()
                    if not technique:
                        # Try finding by mitre_id as fallback
                        technique = MitreTechnique.objects.filter(mitre_id=technique_id).first()
                    if not technique:
                        continue  # Skip this technique if we can't create or find it
            techniques.append(technique)
        return techniques

    def get_or_create_target_os(self, os_name='Windows'):
        """Get or create target OS object."""
        try:
            target_os = TargetOs.objects.get(name__iexact=os_name)
            return target_os
        except TargetOs.DoesNotExist:
            # Return first available OS if Windows not found
            return TargetOs.objects.first()

    def map_level_to_confidence(self, level):
        """Map Sigma level to confidence value."""
        level_mapping = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'informational': 1,
        }
        return level_mapping.get(level.lower(), 2)  # Default to Medium

    def create_or_update_analytic(self, title, description, query, mitre_techniques, 
                                   references, level, columns):
        """Create or update an Analytic object."""
        try:
            # Check if analytic already exists
            analytic, created = Analytic.objects.get_or_create(
                name=title,
                defaults={
                    'description': description,
                    'query': query,
                    'columns': columns,
                    'connector': self.default_connector,
                    'status': 'DRAFT',
                    'confidence': self.map_level_to_confidence(level),
                    'relevance': 2,  # Default to Medium
                    'category': Category.objects.get(id=DEFAULT_CATEGORY_ID) if DEFAULT_CATEGORY_ID else None,
                    'created_by': self.default_user,
                    'notes': f'Imported from Sigma rule. Level: {level}',
                    'references': '\n'.join(references) if isinstance(references, list) else references,
                    'run_daily': True,
                    'create_rule': False,
                    'dynamic_query': False,
                    'anomaly_threshold_count': 2,
                    'anomaly_threshold_endpoints': 2,
                }
            )
            
            if created:
                self.created_count += 1
                print(f"✓ Created: {title}")
            else:
                # Update existing analytic
                analytic.description = description
                analytic.query = query
                analytic.columns = columns
                analytic.confidence = self.map_level_to_confidence(level)
                analytic.notes = f'Updated from Sigma rule. Level: {level}'
                analytic.references = '\n'.join(references) if isinstance(references, list) else references
                analytic.save()
                self.updated_count += 1
                print(f"↻ Updated: {title}")
            
            # Add tags
            analytic.tags.add(self.sigma_tag)
            
            # Add MITRE techniques
            if mitre_techniques:
                technique_objs = self.get_or_create_mitre_techniques(mitre_techniques)
                analytic.mitre_techniques.add(*technique_objs)
            
            # Add target OS (default to Windows)
            target_os = self.get_or_create_target_os('Windows')
            if target_os:
                analytic.target_os.add(target_os)
            
            return analytic
        except Exception as e:
            self.error_count += 1
            self.log_error(f"Error creating/updating analytic '{title}': {e}")
            return None

    def log_error(self, message):
        """Log errors to a log file."""
        with open(ERRORS_LOG_PATH, 'a', encoding='utf-8') as log_file:
            log_file.write(f"[{datetime.now()}] {message}\n")
        print(f"✗ Error: {message}")

    def process_files(self):
        """Main processing function."""
        print("\n" + "="*80)
        print("SIGMA TO DJANGO ANALYTIC CONVERTER")
        print("="*80 + "\n")
        
        # Setup Django objects
        self.setup()
        
        # Download and extract repository
        if not self.download_and_extract_repo(GITHUB_REPO_URL, ZIP_FILE_PATH, LOCAL_REPO_PATH):
            print("Failed to download repository. Exiting.")
            return
        
        # Get all markdown files
        md_files = self.get_md_files(os.path.join(LOCAL_REPO_PATH, 'ConvertSigmaRepo2SentinelOnePQ-main'))
        print(f"\nFound {len(md_files)} markdown files to process.\n")
        
        # Default columns for SentinelOne PowerQuery
        default_columns = "| columns event.time, event.type, site.name, agent.uuid, src.process.storyline.id, src.process.user, src.process.uid, src.process.cmdline, src.ip.address, src.port.number, dst.ip.address, dst.port.number, src.process.parent.cmdline, tgt.process.cmdline"
        
        # Process each file
        for idx, file_path in enumerate(md_files, 1):
            try:
                if idx % 50 == 0:
                    print(f"\nProgress: {idx}/{len(md_files)} files processed...\n")
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Extract information
                powerquery, sigma_rule = self.extract_info(content)
                
                if not powerquery or powerquery == '```yml':
                    continue
                
                description, title, mitre_techniques, references, level = self.parse_sigma_rule(sigma_rule)
                
                if not title:
                    continue
                
                # Create or update analytic
                self.create_or_update_analytic(
                    title=title,
                    description=description,
                    query=powerquery,
                    mitre_techniques=mitre_techniques,
                    references=references,
                    level=level,
                    columns=default_columns
                )
                
            except Exception as e:
                self.error_count += 1
                self.log_error(f"Error processing file {file_path}: {e}")
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Analytics created: {self.created_count}")
        print(f"Analytics updated: {self.updated_count}")
        print(f"Errors: {self.error_count}")
        print(f"\nTotal processed: {self.created_count + self.updated_count}")
        if self.error_count > 0:
            print(f"\nCheck {ERRORS_LOG_PATH} for error details.")
        print("="*80 + "\n")


def run():
    """Main entry point for django-extensions runscript."""
    converter = SigmaToDjango()
    converter.process_files()


if __name__ == "__main__":
    # Check if running in Django environment
    try:
        django.setup()
    except:
        pass
    
    converter = SigmaToDjango()
    converter.process_files()
