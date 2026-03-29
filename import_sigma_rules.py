"""
Django management command to import Sigma rules as Analytics.

Place this file in: your_app/management/commands/import_sigma_rules.py

Usage:
    python manage.py import_sigma_rules
    python manage.py import_sigma_rules --connector-id 2
    python manage.py import_sigma_rules --category-id 5
    python manage.py import_sigma_rules --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from qm.models import (  # Replace 'your_app' with your actual app name
    Analytic, Connector, Category, Tag, MitreTechnique,
    ThreatName, ThreatActor, TargetOs, Vulnerability
)
import os
import re
import yaml
import requests
import zipfile
from datetime import datetime


class Command(BaseCommand):
    help = 'Import Sigma rules as Analytic objects from ConvertSigmaRepo2SentinelOnePQ repository'

    def add_arguments(self, parser):
        parser.add_argument(
            '--connector-id',
            type=int,
            default=1,
            help='ID of the connector to use (default: 1)',
        )
        parser.add_argument(
            '--category-id',
            type=int,
            default=None,
            help='ID of the category to assign (optional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes to the database',
        )
        parser.add_argument(
            '--repo-url',
            type=str,
            default='https://github.com/wikijm/ConvertSigmaRepo2SentinelOnePQ/archive/refs/heads/main.zip',
            help='GitHub repository URL to download',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.connector_id = options['connector_id']
        self.category_id = options['category_id']
        self.repo_url = options['repo_url']
        
        self.created_count = 0
        self.updated_count = 0
        self.error_count = 0
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('SIGMA TO DJANGO ANALYTIC CONVERTER'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        # Setup
        self.setup()
        
        # Download and process
        self.process_sigma_rules()
        
        # Summary
        self.print_summary()

    def setup(self):
        """Setup required Django objects."""
        # Get default user
        self.default_user = User.objects.filter(is_superuser=True).first()
        if not self.default_user:
            self.default_user = User.objects.first()
        
        if not self.default_user:
            raise CommandError('No users found in database. Create a user first.')
        
        # Get connector
        try:
            self.default_connector = Connector.objects.get(id=self.connector_id)
        except Connector.DoesNotExist:
            raise CommandError(f'Connector with ID {self.connector_id} not found.')
        
        # Get category (optional)
        self.default_category = None
        if self.category_id:
            try:
                self.default_category = Category.objects.get(id=self.category_id)
            except Category.DoesNotExist:
                raise CommandError(f'Category with ID {self.category_id} not found.')
        
        # Get or create Sigma tag
        if not self.dry_run:
            self.sigma_tag, _ = Tag.objects.get_or_create(
                name="From SIGMA"
            )
        else:
            self.sigma_tag = Tag.objects.filter(name="From SIGMA").first()
            if not self.sigma_tag:
                self.sigma_tag = Tag(name="From SIGMA")
        
        self.stdout.write('Setup complete:')
        self.stdout.write(f'  - User: {self.default_user.username}')
        self.stdout.write(f'  - Connector: {self.default_connector}')
        self.stdout.write(f'  - Category: {self.default_category or "None"}')
        self.stdout.write(f'  - Sigma Tag: {self.sigma_tag.name}')
        self.stdout.write('')

    def download_and_extract_repo(self, repo_url, zip_path, extract_path):
        """Download and extract the GitHub repository."""
        # Check if local zip file exists first
        local_zip = 'ConvertSigmaRepo2SentinelOnePQ-main.zip'
        if os.path.exists(local_zip):
            self.stdout.write(f'Found local zip file: {local_zip}')
            zip_path = local_zip
            use_local = True
        else:
            use_local = False
        
        try:
            # Download from GitHub if local file doesn't exist
            if not use_local:
                self.stdout.write(f'Downloading repository from {repo_url}...')
                response = requests.get(repo_url, timeout=60, verify=False)
                response.raise_for_status()

                with open(zip_path, 'wb') as zip_file:
                    zip_file.write(response.content)
                self.stdout.write('Download successful.')

            self.stdout.write(f'Extracting to {extract_path}...')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Delete the zip file after extraction (only if downloaded)
            if not use_local and os.path.exists(zip_path):
                os.remove(zip_path)
            self.stdout.write(self.style.SUCCESS('Extraction successful.\n'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error downloading repository: {e}'))
            self.stdout.write(self.style.WARNING("TIP: Place 'ConvertSigmaRepo2SentinelOnePQ-main.zip' in the same folder as this script."))
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

            mitre_techniques = [
                tag.split('.')[1].upper() 
                for tag in tags 
                if tag.startswith('attack.t')
            ]

            return description, title, mitre_techniques, references, level
        except Exception as e:
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
                    self.stdout.write(self.style.WARNING(f'Could not create MITRE technique {technique_id}: {e}'))
                    technique = MitreTechnique.objects.filter(name__iexact=technique_id).first()
                    if not technique:
                        # Try finding by mitre_id as fallback
                        technique = MitreTechnique.objects.filter(mitre_id=technique_id).first()
                    if not technique:
                        continue  # Skip this technique if we can't create or find it
            techniques.append(technique)
        return techniques

    def get_target_os(self, os_name='Windows'):
        """Get target OS object."""
        try:
            return TargetOs.objects.get(name__iexact=os_name)
        except TargetOs.DoesNotExist:
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
        return level_mapping.get(level.lower(), 2)

    def create_or_update_analytic(self, title, description, query, mitre_techniques, 
                                   references, level, columns):
        """Create or update an Analytic object."""
        try:
            if self.dry_run:
                # Check if exists
                exists = Analytic.objects.filter(name=title).exists()
                if exists:
                    self.updated_count += 1
                    self.stdout.write(self.style.WARNING(f'[DRY RUN] Would update: {title}'))
                else:
                    self.created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'[DRY RUN] Would create: {title}'))
                return None
            
            analytic, created = Analytic.objects.get_or_create(
                name=title,
                defaults={
                    'description': description,
                    'query': query,
                    'columns': columns,
                    'connector': self.default_connector,
                    'status': 'DRAFT',
                    'confidence': self.map_level_to_confidence(level),
                    'relevance': 2,
                    'category': self.default_category,
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
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {title}'))
            else:
                analytic.description = description
                analytic.query = query
                analytic.columns = columns
                analytic.confidence = self.map_level_to_confidence(level)
                analytic.notes = f'Updated from Sigma rule. Level: {level}'
                analytic.references = '\n'.join(references) if isinstance(references, list) else references
                analytic.save()
                self.updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {title}'))
            
            # Add relationships
            analytic.tags.add(self.sigma_tag)
            
            if mitre_techniques:
                technique_objs = self.get_or_create_mitre_techniques(mitre_techniques)
                analytic.mitre_techniques.add(*technique_objs)
            
            target_os = self.get_target_os('Windows')
            if target_os:
                analytic.target_os.add(target_os)
            
            return analytic
        except Exception as e:
            self.error_count += 1
            self.stdout.write(self.style.ERROR(f'✗ Error with "{title}": {e}'))
            return None

    def process_sigma_rules(self):
        """Main processing function."""
        local_repo_path = 'local_repo'
        zip_file_path = 'repo.zip'
        
        if not self.download_and_extract_repo(self.repo_url, zip_file_path, local_repo_path):
            raise CommandError('Failed to download repository')
        
        md_files = self.get_md_files(os.path.join(local_repo_path, 'ConvertSigmaRepo2SentinelOnePQ-main'))
        self.stdout.write(f'Found {len(md_files)} markdown files to process.\n')
        
        default_columns = "| columns event.time, event.type, site.name, agent.uuid, src.process.storyline.id, src.process.user, src.process.uid, src.process.cmdline, src.ip.address, src.port.number, dst.ip.address, dst.port.number, src.process.parent.cmdline, tgt.process.cmdline"
        
        for idx, file_path in enumerate(md_files, 1):
            try:
                if idx % 100 == 0:
                    self.stdout.write(f'\nProgress: {idx}/{len(md_files)} files processed...\n')
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                powerquery, sigma_rule = self.extract_info(content)
                
                if not powerquery or powerquery == '```yml':
                    continue
                
                description, title, mitre_techniques, references, level = self.parse_sigma_rule(sigma_rule)
                
                if not title:
                    continue
                
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
                self.stdout.write(self.style.ERROR(f'Error processing {file_path}: {e}'))

    def print_summary(self):
        """Print summary of the import process."""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*80)
        self.stdout.write(f'Analytics created: {self.created_count}')
        self.stdout.write(f'Analytics updated: {self.updated_count}')
        self.stdout.write(f'Errors: {self.error_count}')
        self.stdout.write(f'\nTotal processed: {self.created_count + self.updated_count}')
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made to the database.'))
            self.stdout.write(self.style.WARNING('Run without --dry-run to actually import the rules.'))
        
        self.stdout.write('='*80 + '\n')
