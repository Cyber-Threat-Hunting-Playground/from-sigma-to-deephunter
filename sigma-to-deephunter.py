import os
import re
import json
import yaml
import requests
import zipfile
import shutil

# Configuration
GITHUB_REPO_URL = 'https://github.com/wikijm/ConvertSigmaRepo2SentinelOnePQ/archive/refs/heads/main.zip'
LOCAL_REPO_PATH = 'local_repo'
QUERY_JSON_PATH = 'query.json'
ZIP_FILE_PATH = 'repo.zip'
ERRORS_LOG_PATH = 'errors.log'

def download_and_extract_repo(repo_url, zip_path, extract_path):
    try:
        # Clean up old extraction if it exists
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
            
        response = requests.get(repo_url)
        response.raise_for_status()

        with open(zip_path, 'wb') as zip_file:
            zip_file.write(response.content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        os.remove(zip_path)
        return True
    except Exception as e:
        log_error(f"Error downloading or extracting the repository: {e}")
        return False

def get_md_files(local_path):
    md_files = []
    for root, _, files in os.walk(local_path):
        for file in files:
            if file.endswith('.md') and file != 'README.md':
                md_files.append(os.path.join(root, file))
    return md_files

def extract_info(content):
    lines = content.split('\n')
    # Powerquery is typically on the 3rd line based on your logic
    powerquery = lines[2].strip() if len(lines) > 2 else ''
    sigma_rule = re.search(r'```yaml(.*?)```', content, re.DOTALL)
    sigma_rule = sigma_rule.group(1).strip() if sigma_rule else ''
    return powerquery, sigma_rule

def parse_sigma_rule(sigma_rule):
    try:
        sigma_data = yaml.safe_load(sigma_rule)
        if not sigma_data:
            raise ValueError("Invalid or empty YAML content")

        description = sigma_data.get('description', '')
        title = sigma_data.get('title', '')
        tags = sigma_data.get('tags', []) or []
        mitre_techniques = [tag.split('.')[1] for tag in tags if tag.startswith('attack.t')]

        return description, title, mitre_techniques
    except Exception as e:
        log_error(f"Error parsing the SIGMA rule: {e}")
        return '', '', []

def update_query_json(entries):
    # This now overwrites the file from scratch every time.
    # This prevents the file from growing > 100MB and fixes JSONDecodeErrors.
    try:
        with open(QUERY_JSON_PATH, 'w', encoding='utf-8') as json_file:
            json.dump(entries, json_file, indent=4)
        print(f"Successfully wrote {len(entries)} entries to {QUERY_JSON_PATH}")
    except Exception as e:
        log_error(f"Error writing to {QUERY_JSON_PATH}: {e}")

def log_error(message):
    print(message) # Also print to console for GitHub Action logs
    with open(ERRORS_LOG_PATH, 'a') as log_file:
        log_file.write(message + '\n')

if __name__ == "__main__":
    if download_and_extract_repo(GITHUB_REPO_URL, ZIP_FILE_PATH, LOCAL_REPO_PATH):
        # Path adjustment for the extracted folder name
        extracted_folder = os.path.join(LOCAL_REPO_PATH, 'ConvertSigmaRepo2SentinelOnePQ-main')
        md_files = get_md_files(extracted_folder)
        
        query_entries = []
        pk = 1

        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                powerquery, sigma_rule = extract_info(content)
                description, title, mitre_techniques = parse_sigma_rule(sigma_rule)

                query_data = {
                    "fields": {
                        "actors": [],
                        "anomaly_threshold_count": 2,
                        "anomaly_threshold_endpoints": 2,
                        "columns": "| columns event.time, event.type, site.name, agent.uuid, src.process.storyline.id, src.process.user, src.process.uid, src.process.cmdline, src.ip.address, src.port.number, dst.ip.address, dst.port.number, src.process.parent.cmdline, tgt.process.cmdline",
                        "confidence": 1,
                        "description": description,
                        "dynamic_query": False,
                        "emulation_validation": "",
                        "mitre_techniques": mitre_techniques,
                        "name": title,
                        "notes": "",
                        "pub_date": "",
                        "pub_status": "DIST",
                        "query": powerquery,
                        "references": "",
                        "relevance": 1,
                        "run_daily": True,
                        "star_rule": False,
                        "tags": ["From SIGMA"],
                        "target_os": [1],
                        "threats": [],
                        "update_date": "",
                        "vulnerabilities": [],
                        "weighted_relevance": 1.5
                    },
                    "model": "qm.query",
                    "pk": pk
                }

                query_entries.append(query_data)
                pk += 1
            except Exception as e:
                log_error(f"Error processing the file {file_path}: {e}")

        update_query_json(query_entries)
