#!/usr/bin/env python3
"""Incomplete research pipeline orchestrator for the Tom Street investigation.

NOT A VERIFIED COMPLETE ACQUISITION OR RELEASE SYSTEM. Required modules may be
missing; execution must fail closed rather than report a misleading success.

Provides a single unified command-line entry point to:
1. Run proactive multi-agency discovery (`discover_agency_updates.py`).
2. Execute all existing and new acquisition scripts (`acquire_*.py`) with
   standardized working directory (`cwd=REPO_ROOT` so relative paths in legacy
   scripts never break), bounded concurrency, and automatic retry backoff.
3. Run quantitative LiDAR & terrain window analysis (`analyze_lidar_terrain_change.py`)
   and external resident photo privacy verification (`audit_private_photo_vault.py`).
4. Synchronize newly captured files and manifests into `00_CONTROL/SOURCE_REGISTER.csv`
   via `sync_evidence_registers.py` without overwriting historical evidence.
5. Run all audit, jurisdiction, claim, and consistency verification checks.
6. Rebuild the public-safe homeowner meeting draft packet (`build_reconciled_packet.py`)
   and write a comprehensive pipeline run report to
   `00_CONTROL/AUTONOMOUS_PIPELINE_REPORT.json`.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent

# Ordered phases of the autonomous evidence pipeline
DISCOVERY_SCRIPTS = [
    "discover_agency_updates.py",
]

ACQUISITION_SCRIPTS = [
    "acquire_live_permits_and_parcels.py",
    "acquire_hydrology_fema_usgs.py",
    "acquire_noaa_precipitation_and_storms.py",
    "acquire_question_sources.py",
    "acquire_followup_sources.py",
    "acquire_public_primary_sources.py",
    "acquire_east_navarre_official_study_map.py",
    "acquire_public_tom_street_watershed_pdfs.py",
    "acquire_fdep_aerial_mosaic_provenance.py",
    "acquire_fdep_historical_tom_street_aerials.py",
    "acquire_fdot_aerial_index.py",
    "acquire_tom_street_historical_aerials.py",
    "acquire_usda_naip_2021_tom_street.py",
    "acquire_usda_naip_2023_tom_street.py",
    "acquire_noaa_survey_reports.py",
    "acquire_noaa_tom_street_2006_index.py",
    # Dependent on 2006 index: run after index completes
    "acquire_noaa_tom_street_2006_laz.py",
    "acquire_noaa_tom_street_2017.py",
    "acquire_noaa_tom_street_2018.py",
]

ANALYSIS_AND_SYNC_SCRIPTS = [
    "analyze_lidar_terrain_change.py",
    "audit_private_photo_vault.py",
    "sync_evidence_registers.py",
]

AUDIT_AND_VERIFY_SCRIPTS = [
    "audit_historical_public_evidence.py",
    "check_jurisdiction_scope.py",
    "check_document_claims.py",
    "check_question_findings.py",
    "check_historical_evidence_crosslinks.py",
    "check_repository_consistency.py",
]

BUILD_AND_RELEASE_SCRIPTS = [
    "build_reconciled_packet.py",
    "verify_reconciled_release.py",
]


def run_script(script_name: str, extra_args: list[str] | None = None, timeout: int = 240, retries: int = 1) -> dict:
    script_path = TOOLS_DIR / script_name
    if not script_path.is_file():
        return {
            "script": script_name,
            "status": "SKIPPED_NOT_FOUND",
            "duration_sec": 0.0,
        }

    cmd = [sys.executable, str(script_path), *(extra_args or [])]
    attempt = 0
    start = time.monotonic()
    last_result = None

    while attempt <= retries:
        attempt += 1
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),  # Critical fix: always run from REPO_ROOT so relative paths work
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = round(time.monotonic() - start, 3)
            if proc.returncode == 0:
                return {
                    "script": script_name,
                    "status": "SUCCEEDED",
                    "attempts": attempt,
                    "duration_sec": elapsed,
                    "stdout_tail": proc.stdout.strip().splitlines()[-10:],
                }
            last_result = {
                "script": script_name,
                "status": "FAILED",
                "return_code": proc.returncode,
                "attempts": attempt,
                "duration_sec": elapsed,
                "stdout_tail": proc.stdout.strip().splitlines()[-10:],
                "stderr_tail": proc.stderr.strip().splitlines()[-10:],
            }
        except subprocess.TimeoutExpired:
            elapsed = round(time.monotonic() - start, 3)
            last_result = {
                "script": script_name,
                "status": "TIMEOUT",
                "attempts": attempt,
                "duration_sec": elapsed,
            }
        if attempt <= retries:
            time.sleep(2.0 * attempt)

    return last_result or {"script": script_name, "status": "FAILED"}


def run_phase_parallel(scripts: list[str], max_workers: int = 4, retries: int = 1) -> list[dict]:
    # Separate sequential dependencies (e.g., 2006 LAZ depends on 2006 index)
    deferred = [s for s in scripts if s == "acquire_noaa_tom_street_2006_laz.py"]
    initial = [s for s in scripts if s not in deferred]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {pool.submit(run_script, s, None, 240, retries): s for s in initial}
        for fut in concurrent.futures.as_completed(fut_map):
            results.append(fut.result())

    for s in deferred:
        results.append(run_script(s, retries=retries))

    order = {name: idx for idx, name in enumerate(scripts)}
    results.sort(key=lambda r: order.get(r["script"], 999))
    return results


def run_phase_sequential(scripts: list[str], extra_args: list[str] | None = None) -> list[dict]:
    return [run_script(s, extra_args=extra_args, retries=0) for s in scripts]


def required_scripts(mode: str) -> list[str]:
    """Return all scripts whose successful presence is required for the mode.

    This check is intentionally separate from source-file provenance checks.
    A skipped or unavailable acquisition step cannot count as a successful
    end-to-end evidence review.
    """
    groups = (
        ("discovery", DISCOVERY_SCRIPTS, ("full", "discover")),
        ("acquisition", ACQUISITION_SCRIPTS, ("full", "acquire")),
        ("analysis_and_sync", ANALYSIS_AND_SYNC_SCRIPTS, ("full", "sync")),
        ("audit_and_verify", AUDIT_AND_VERIFY_SCRIPTS, ("full", "verify")),
        ("build_and_release", BUILD_AND_RELEASE_SCRIPTS, ("full", "build")),
    )
    names: list[str] = []
    for _phase, scripts, modes in groups:
        if mode in modes:
            for name in scripts:
                if name not in names:
                    names.append(name)
    return names


def missing_required_scripts(mode: str) -> list[str]:
    """Report missing expected implementations without changing any files."""
    return [name for name in required_scripts(mode)
            if not (TOOLS_DIR / name).is_file()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("full", "discover", "acquire", "sync", "verify", "build"),
        default="full",
        help="Pipeline execution mode (default: full end-to-end autonomous run).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Max concurrent workers during acquisition phase (default: 4).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned phases and scripts without executing network or file writes.",
    )
    parser.add_argument(
        "--allow-network-and-writes",
        action="store_true",
        help="Operator acknowledges network acquisition and source-file writes; never implies agency or release approval",
    )
    args = parser.parse_args(argv)

    if args.dry_run:
        plan = {
            "mode": args.mode,
            "repo_root": str(ROOT),
            "tools_dir": str(TOOLS_DIR),
            "phases": {
                "discovery": DISCOVERY_SCRIPTS if args.mode in ("full", "discover") else [],
                "acquisition": ACQUISITION_SCRIPTS if args.mode in ("full", "acquire") else [],
                "analysis_and_sync": ANALYSIS_AND_SYNC_SCRIPTS if args.mode in ("full", "sync") else [],
                "audit_and_verify": AUDIT_AND_VERIFY_SCRIPTS if args.mode in ("full", "verify") else [],
                "build_and_release": BUILD_AND_RELEASE_SCRIPTS if args.mode in ("full", "build") else [],
            },
        }
        missing = missing_required_scripts(args.mode)
        plan["missing_required_scripts"] = missing
        plan["ready_to_execute"] = not missing
        print(json.dumps(plan, indent=2))
        return 0  # diagnostic output only; not a successful pipeline run

    if not args.allow_network_and_writes:
        print(json.dumps({
            "status": "BLOCKED_OPERATOR_CONFIRMATION_REQUIRED",
            "mode": args.mode,
            "note": "No acquisition, report, source update or publication step was started. Re-run with explicit --allow-network-and-writes only after reviewing scripts and permission scope.",
        }, indent=2), file=sys.stderr)
        return 3

    missing = missing_required_scripts(args.mode)
    if missing:
        print(json.dumps({
            "status": "BLOCKED_MISSING_REQUIRED_SCRIPTS",
            "mode": args.mode,
            "missing_required_scripts": missing,
            "note": "No acquisition, report or publication steps were started.",
        }, indent=2), file=sys.stderr)
        return 2

    started_utc = datetime.now(timezone.utc).isoformat()
    phases_output: dict[str, list[dict]] = {}

    if args.mode in ("full", "discover"):
        phases_output["discovery"] = run_phase_sequential(DISCOVERY_SCRIPTS)

    if args.mode in ("full", "acquire"):
        phases_output["acquisition"] = run_phase_parallel(
            ACQUISITION_SCRIPTS, max_workers=args.workers, retries=1
        )

    if args.mode in ("full", "sync"):
        phases_output["analysis_and_sync"] = run_phase_sequential(ANALYSIS_AND_SYNC_SCRIPTS)

    if args.mode in ("full", "verify"):
        phases_output["audit_and_verify"] = run_phase_sequential(AUDIT_AND_VERIFY_SCRIPTS)

    if args.mode in ("full", "build"):
        phases_output["build_and_release"] = run_phase_sequential(BUILD_AND_RELEASE_SCRIPTS)

    all_runs = [item for phase_list in phases_output.values() for item in phase_list]
    succeeded = sum(1 for r in all_runs if r["status"] == "SUCCEEDED")
    failed = sum(1 for r in all_runs if r["status"] != "SUCCEEDED")

    report = {
        "started_utc": started_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "summary": {
            "total_scripts_executed": len(all_runs),
            "succeeded": succeeded,
            "failed": failed,
        },
        "phases": phases_output,
    }

    report_path = ROOT / "00_CONTROL" / "AUTONOMOUS_PIPELINE_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report_path": report_path.relative_to(ROOT).as_posix(),
        "summary": report["summary"],
    }, indent=2))
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
