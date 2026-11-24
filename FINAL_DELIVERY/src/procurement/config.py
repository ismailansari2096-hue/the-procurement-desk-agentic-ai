"""
Configuration module for The Procurement Desk.
Defines canonical paths, allowed actions, and environment settings.
"""

from pathlib import Path

# Workspace Root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PLAYBOOK_DIR = PROCESSED_DATA_DIR / "playbook"

# Knowledge Base Paths
KB_DIR = BASE_DIR / "knowledge_base"
POLICY_REF_PATH = KB_DIR / "policy_reference.json"
SUPPLIER_REGISTRY_PATH = KB_DIR / "supplier_registry.json"
AMENDMENTS_PATH = KB_DIR / "amendments.json"
HISTORICAL_DECISIONS_PATH = KB_DIR / "historical_decisions.json"

# Output Paths
OUTPUTS_DIR = BASE_DIR / "outputs"
SUBMISSION_PATH = OUTPUTS_DIR / "submission.csv"
VALIDATION_REPORT_PATH = OUTPUTS_DIR / "validation_report.json"
AUDIT_REPORT_PATH = OUTPUTS_DIR / "audit_report.json"
REPORTS_DIR = BASE_DIR / "reports"

# Canonical Action Enum
VALID_ACTIONS = {"ACCEPT", "COUNTER", "REJECT", "ESCALATE"}
