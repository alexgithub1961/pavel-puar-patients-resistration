#!/usr/bin/env python3
"""
Post-deployment verification tests using Playwright.
Tests the deployed PWAs against the live API.

Usage:
    python scripts/test_deployed.py

    # Or with custom URLs:
    PATIENT_PWA_URL=https://... DOCTOR_PWA_URL=https://... API_URL=https://... python scripts/test_deployed.py
"""

import os
import sys
import subprocess

# Default deployed URLs (AWS)
DEFAULT_API_URL = "https://nmpjiqngaz.us-east-1.awsapprunner.com"
DEFAULT_PATIENT_PWA_URL = "https://d2wowd7dw25och.cloudfront.net"
DEFAULT_DOCTOR_PWA_URL = "https://d24gl9ln0vt8cq.cloudfront.net"


def main():
    """Run post-deployment E2E tests."""
    # Set environment variables for the tests
    env = os.environ.copy()
    env["API_URL"] = os.getenv("API_URL", DEFAULT_API_URL)
    env["PATIENT_PWA_URL"] = os.getenv("PATIENT_PWA_URL", DEFAULT_PATIENT_PWA_URL)
    env["DOCTOR_PWA_URL"] = os.getenv("DOCTOR_PWA_URL", DEFAULT_DOCTOR_PWA_URL)

    print("=" * 60)
    print("PUAR-Patients Post-Deployment Verification")
    print("=" * 60)
    print(f"API URL:         {env['API_URL']}")
    print(f"Patient PWA URL: {env['PATIENT_PWA_URL']}")
    print(f"Doctor PWA URL:  {env['DOCTOR_PWA_URL']}")
    print("=" * 60)

    # First, verify the API is responding
    print("\n[1/3] Verifying API health...")
    try:
        import httpx
        response = httpx.get(f"{env['API_URL']}/", timeout=10)
        if response.status_code == 200:
            print(f"  API is healthy: {response.json()}")
        else:
            print(f"  WARNING: API returned {response.status_code}")
    except Exception as e:
        print(f"  ERROR: Could not reach API: {e}")
        sys.exit(1)

    # Run the E2E tests
    print("\n[2/3] Running Playwright E2E tests...")
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/e2e/",
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
            "--timeout=60",
        ],
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    if result.returncode != 0:
        print("\n[FAILED] E2E tests failed!")
        sys.exit(result.returncode)

    print("\n[3/3] Deployment verification complete!")
    print("=" * 60)
    print("All tests passed - deployment is verified!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
