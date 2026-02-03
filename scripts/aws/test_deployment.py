#!/usr/bin/env python3
"""Test script to verify AWS deployment is working correctly."""

import httpx
import sys
import uuid
from datetime import datetime

API_URL = "https://nmpjiqngaz.us-east-1.awsapprunner.com"
PATIENT_URL = "http://puar-patients-patient-pwa-860599907983.s3-website-us-east-1.amazonaws.com"
DOCTOR_URL = "http://puar-patients-doctor-pwa-860599907983.s3-website-us-east-1.amazonaws.com"


def log_result(test_name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}")
    if detail:
        print(f"       {detail}")


def test_api_health():
    """Test API health endpoint."""
    try:
        response = httpx.get(f"{API_URL}/api/v1/health", timeout=10)
        data = response.json()
        passed = (
            response.status_code == 200
            and data.get("status") == "healthy"
            and data.get("environment") == "production"
        )
        log_result(
            "API Health Check",
            passed,
            f"Status: {data.get('status')}, Env: {data.get('environment')}"
        )
        return passed
    except Exception as e:
        log_result("API Health Check", False, str(e))
        return False


def test_api_ready():
    """Test API readiness endpoint."""
    try:
        response = httpx.get(f"{API_URL}/api/v1/ready", timeout=10)
        passed = response.status_code == 200
        log_result("API Ready Check", passed)
        return passed
    except Exception as e:
        log_result("API Ready Check", False, str(e))
        return False


def test_patient_registration_and_login():
    """Test patient registration and login flow."""
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    try:
        # Register
        response = httpx.post(
            f"{API_URL}/api/v1/auth/patients/register",
            json={
                "email": test_email,
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "Patient",
            },
            timeout=10,
        )

        if response.status_code != 200:
            log_result("Patient Registration", False, f"Status: {response.status_code}, Body: {response.text[:200]}")
            return False

        log_result("Patient Registration", True, f"Email: {test_email}")

        # Login
        response = httpx.post(
            f"{API_URL}/api/v1/auth/patients/login",
            json={
                "email": test_email,
                "password": "TestPassword123!",
            },
            timeout=10,
        )

        if response.status_code != 200:
            log_result("Patient Login", False, f"Status: {response.status_code}")
            return False

        data = response.json()
        token = data.get("access_token")
        if not token:
            log_result("Patient Login", False, "No access token received")
            return False

        log_result("Patient Login", True, "Access token received")

        # Get profile
        response = httpx.get(
            f"{API_URL}/api/v1/patients/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

        passed = response.status_code == 200
        log_result("Patient Profile", passed)
        return passed

    except Exception as e:
        log_result("Patient Auth Flow", False, str(e))
        return False


def test_doctor_registration_and_login():
    """Test doctor registration and login flow."""
    test_email = f"doctor_{uuid.uuid4().hex[:8]}@example.com"

    try:
        # Register
        response = httpx.post(
            f"{API_URL}/api/v1/auth/doctors/register",
            json={
                "email": test_email,
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "Doctor",
                "specialisation": "General Practice",
                "licence_number": f"DOC{uuid.uuid4().hex[:6].upper()}",
            },
            timeout=10,
        )

        if response.status_code != 200:
            log_result("Doctor Registration", False, f"Status: {response.status_code}, Body: {response.text[:200]}")
            return False

        log_result("Doctor Registration", True, f"Email: {test_email}")

        # Login
        response = httpx.post(
            f"{API_URL}/api/v1/auth/doctors/login",
            json={
                "email": test_email,
                "password": "TestPassword123!",
            },
            timeout=10,
        )

        if response.status_code != 200:
            log_result("Doctor Login", False, f"Status: {response.status_code}")
            return False

        log_result("Doctor Login", True, "Access token received")
        return True

    except Exception as e:
        log_result("Doctor Auth Flow", False, str(e))
        return False


def test_patient_pwa_accessible():
    """Test that patient PWA is accessible."""
    try:
        response = httpx.get(PATIENT_URL, timeout=10, follow_redirects=True)
        passed = response.status_code == 200 and "<!DOCTYPE html>" in response.text
        log_result("Patient PWA Accessible", passed, PATIENT_URL)
        return passed
    except Exception as e:
        log_result("Patient PWA Accessible", False, str(e))
        return False


def test_doctor_pwa_accessible():
    """Test that doctor PWA is accessible."""
    try:
        response = httpx.get(DOCTOR_URL, timeout=10, follow_redirects=True)
        passed = response.status_code == 200 and "<!DOCTYPE html>" in response.text
        log_result("Doctor PWA Accessible", passed, DOCTOR_URL)
        return passed
    except Exception as e:
        log_result("Doctor PWA Accessible", False, str(e))
        return False


def main():
    print("=" * 60)
    print("PUAR-Patients AWS Deployment Tests")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    print()

    results = []

    # Run all tests
    print("Backend API Tests:")
    print("-" * 40)
    results.append(test_api_health())
    results.append(test_api_ready())
    print()

    print("Authentication Tests:")
    print("-" * 40)
    results.append(test_patient_registration_and_login())
    results.append(test_doctor_registration_and_login())
    print()

    print("Frontend PWA Tests:")
    print("-" * 40)
    results.append(test_patient_pwa_accessible())
    results.append(test_doctor_pwa_accessible())
    print()

    # Summary
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"SUMMARY: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\nDEPLOYMENT VERIFICATION: SUCCESS")
        print("\nPublic URLs:")
        print(f"  API:         {API_URL}")
        print(f"  Patient PWA: {PATIENT_URL}")
        print(f"  Doctor PWA:  {DOCTOR_URL}")
        return 0
    else:
        print("\nDEPLOYMENT VERIFICATION: FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
