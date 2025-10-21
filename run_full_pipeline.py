#!/usr/bin/env python3
"""
run_full_pipeline.py

PURPOSE:
  Master orchestration script for the core data ingestion pipeline:
  1. Filename cleanup (clean_doc.py)
  2. Date extraction & JSON generation (eval_dates.py)
  3. [Optional] Tagging validation (eval_tagging.py)
  4. Document ingestion to ChromaDB (ingest_pipeline.py)

WHY THIS EXISTS:
  The RAG pipeline requires multiple sequential steps that must be run in order.
  This script automates the entire workflow so you only need to run one command.

CORE PIPELINE:
  The standard pipeline is: Clean → Extract Dates → Ingest Documents
  This populates ChromaDB with documents ready for querying.

OPTIONAL FEATURES:
  - Add tagging validation (QA check): --validate
  - For strategic analysis, use analyze_pipeline.py separately after ingestion

USAGE:
  Standard ingestion pipeline (clean → dates → ingest):
    python run_full_pipeline.py

  With tagging validation (QA check before ingestion):
    python run_full_pipeline.py --validate

  Dry run (show what would run, no execution):
    python run_full_pipeline.py --dry-run

  Skip specific steps:
    python run_full_pipeline.py --skip-clean --skip-dates

PIPELINE TOOLS:
  clean_doc.py       - Removes special characters from filenames [AUTOMATIC]
  eval_dates.py      - Extracts dates and generates document_dates.json [AUTOMATIC]
  eval_tagging.py    - Validates auto-tagging quality on samples [--validate only]
  ingest_pipeline.py - Ingests documents into ChromaDB [AUTOMATIC]

FEATURES:
  ✓ Sequential execution with error handling
  ✓ Automatic date extraction before ingestion
  ✓ Optional tagging validation before full ingest
  ✓ Clear progress indicators with timestamps
  ✓ Dry-run mode for testing
  ✓ Flexible skip flags for reprocessing
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
import pathlib


class PipelineOrchestrator:
    """Orchestrates the full RAG pipeline execution."""

    def __init__(self, skip_clean=False, skip_dates=False, skip_ingest=False,
                 include_validate=False, dry_run=False):
        """
        Initialize pipeline orchestrator.

        Args:
            skip_clean (bool): Skip filename cleanup step
            skip_dates (bool): Skip date extraction step
            skip_ingest (bool): Skip document ingestion step
            include_validate (bool): Include tagging validation step
            dry_run (bool): Print commands without executing
        """
        self.skip_clean = skip_clean
        self.skip_dates = skip_dates
        self.skip_ingest = skip_ingest
        self.include_validate = include_validate
        self.dry_run = dry_run
        self.steps_completed = []
        self.steps_failed = []

    def cleanup_reserved_filenames(self):
        """
        Clean up Windows reserved device filenames that may have been created
        during pipeline execution. These prevent git from tracking the repository.
        """
        reserved_names = ["nul", "NUL"]
        base_dir = os.path.dirname(os.path.abspath(__file__))

        for name in reserved_names:
            file_path = os.path.join(base_dir, name)
            if os.path.exists(file_path):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.log(f"Cleaned up reserved filename: {name}", "INFO")
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                        self.log(f"Cleaned up reserved directory: {name}", "INFO")
                except Exception as e:
                    self.log(f"Could not clean up {name}: {e}", "WARNING")

    def log(self, message, level="INFO"):
        """Print timestamped log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {
            "INFO": "[i]",
            "START": "[>>]",
            "SUCCESS": "[OK]",
            "ERROR": "[!!]",
            "WARNING": "[!]"
        }.get(level, "[*]")
        print(f"[{timestamp}] {symbol} {message}")

    def run_step(self, step_name, script_name, description):
        """
        Execute a single pipeline step.

        Args:
            step_name (str): Human-readable step name
            script_name (str): Python script to run
            description (str): What this step does

        Returns:
            bool: True if successful, False if failed
        """
        self.log(f"Starting: {step_name}", "START")
        self.log(f"  Purpose: {description}")

        command = [sys.executable, script_name]

        if self.dry_run:
            self.log(f"  [DRY-RUN] Would execute: {' '.join(command)}")
            return True

        try:
            result = subprocess.run(
                command,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                check=True,
                capture_output=False
            )
            self.log(f"Completed: {step_name}", "SUCCESS")
            self.steps_completed.append(step_name)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed: {step_name} (exit code: {e.returncode})", "ERROR")
            self.steps_failed.append(step_name)
            return False

    def run_pipeline(self):
        """Execute the full pipeline."""
        self.log("=" * 60)
        self.log("RAG PIPELINE ORCHESTRATOR - Starting Full Pipeline")
        self.log("=" * 60)

        # Clean up any reserved Windows device filenames from previous runs
        self.log("Checking for and cleaning up any reserved device filenames...")
        self.cleanup_reserved_filenames()

        if self.dry_run:
            self.log("DRY-RUN MODE: No actual execution", "WARNING")

        # Step 1: Cleanup filenames
        if not self.skip_clean:
            success = self.run_step(
                "Step 1: Filename Cleanup",
                "pipeline/clean_doc.py",
                "Remove special characters from document filenames"
            )
            if not success and not self.dry_run:
                self.log("Pipeline halted due to cleanup failure", "ERROR")
                return False
        else:
            self.log("Skipped: Filename cleanup (--skip-clean)", "WARNING")

        # Step 2: Extract dates
        if not self.skip_dates:
            success = self.run_step(
                "Step 2: Date Extraction",
                "pipeline/eval_dates.py",
                "Extract dates and generate document_dates.json configuration"
            )
            if not success and not self.dry_run:
                self.log("Pipeline halted due to date extraction failure", "ERROR")
                return False
        else:
            self.log("Skipped: Date extraction (--skip-dates)", "WARNING")

        # Step 2.5: Validate tagging (optional)
        if self.include_validate:
            success = self.run_step(
                "Step 2.5: Tagging Validation",
                "pipeline/eval_tagging.py",
                "Validate auto-tagging quality on document samples"
            )
            if not success and not self.dry_run:
                self.log("Pipeline halted due to tagging validation failure", "ERROR")
                return False

        # Step 3: Ingest documents
        if not self.skip_ingest:
            success = self.run_step(
                "Step 3: Document Ingestion",
                "pipeline/ingest_pipeline.py",
                "Load documents and populate ChromaDB vector database"
            )
            if not success and not self.dry_run:
                self.log("Pipeline halted due to ingestion failure", "ERROR")
                return False
        else:
            self.log("Skipped: Document ingestion (--skip-ingest)", "WARNING")


        # Summary
        self.log("=" * 60)
        self.log("PIPELINE SUMMARY")
        self.log("=" * 60)
        self.log(f"Steps Completed: {len(self.steps_completed)}")
        if self.steps_completed:
            for step in self.steps_completed:
                self.log(f"  ✓ {step}", "SUCCESS")

        if self.steps_failed:
            self.log(f"Steps Failed: {len(self.steps_failed)}")
            for step in self.steps_failed:
                self.log(f"  ✗ {step}", "ERROR")
            self.log("=" * 60)
            return False

        self.log("=" * 60)
        self.log("PIPELINE COMPLETE - All steps executed successfully!", "SUCCESS")
        self.log("=" * 60)

        # Next steps
        self.log("\nNext Steps:")
        self.log("  - Run interactive queries: python query/interactive_query_multi_source.py")
        self.log("  - Run strategic analysis: python analysis/analyze_pipeline.py")
        self.log("  - For QA validation next time: python run_full_pipeline.py --validate")

        return True


def cleanup_root_reserved_files():
    """Clean up reserved device files in the project root before starting."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["nul", "NUL"]:
        file_path = os.path.join(base_dir, name)
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"[*] Cleaned up reserved filename: {name}")
            except Exception as e:
                print(f"[!] Could not clean up {name}: {e}")


def main():
    """Parse arguments and run pipeline."""
    # Clean up any stale reserved device filenames from previous runs
    cleanup_root_reserved_files()

    parser = argparse.ArgumentParser(
        description="Orchestrate the complete RAG pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_full_pipeline.py            # Standard: Clean → Dates → Ingest
  python run_full_pipeline.py --validate  # QA check: Clean → Dates → Validate Tag → Ingest
  python run_full_pipeline.py --dry-run   # Preview mode (no execution)
  python run_full_pipeline.py --skip-clean  # Skip cleanup, just dates & ingest

After ingestion:
  python query/interactive_query_multi_source.py    # Ask questions
  python analysis/analyze_pipeline.py               # Run strategic analysis
        """
    )

    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip filename cleanup step"
    )
    parser.add_argument(
        "--skip-dates",
        action="store_true",
        help="Skip date extraction step"
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip document ingestion step"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Include tagging validation step (eval_tagging.py) - QA check before ingestion"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show commands without executing (preview mode)"
    )

    args = parser.parse_args()

    orchestrator = PipelineOrchestrator(
        skip_clean=args.skip_clean,
        skip_dates=args.skip_dates,
        skip_ingest=args.skip_ingest,
        include_validate=args.validate,
        dry_run=args.dry_run
    )

    success = orchestrator.run_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
