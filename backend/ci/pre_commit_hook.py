#!/usr/bin/env python3
import subprocess
import sys
import os

def run_tests():
    """Run test suite before commit"""
    print("Running tests...")
    result = subprocess.run(
        ['pytest', 'tests/e2e/', '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Tests failed! Commit blocked.")
        print(result.stdout)
        return False
    
    print("✓ All tests passed")
    return True

def check_coverage():
    """Check code coverage"""
    print("Checking code coverage...")
    result = subprocess.run(
        ['pytest', 'tests/e2e/', '--cov=backend/app', '--cov-report=term', '--tb=no', '-q'],
        capture_output=True,
        text=True
    )
    
    # Parse coverage percentage
    for line in result.stdout.split('\n'):
        if 'TOTAL' in line:
            parts = line.split()
            if len(parts) >= 4:
                coverage = int(parts[-1].replace('%', ''))
                print(f"Coverage: {coverage}%")
                
                if coverage < 70:
                    print(f"❌ Coverage {coverage}% is below 70% threshold")
                    return False
                
                print(f"✓ Coverage {coverage}% meets threshold")
                return True
    
    return True

def validate_data_tags():
    """Validate data tags in modified files"""
    print("Validating data tags...")
    
    # Get staged files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    
    staged_files = result.stdout.strip().split('\n')
    
    for file in staged_files:
        if file.endswith('models.py'):
            print(f"Checking {file}...")
            result = subprocess.run(
                ['python', 'backend/ci/tag_validator.py', file],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                return False
    
    print("✓ Data tags validated")
    return True

def main():
    """Main pre-commit hook"""
    print("\n" + "="*60)
    print("PRE-COMMIT VALIDATION")
    print("="*60 + "\n")
    
    checks = [
        ("Data Tag Validation", validate_data_tags),
        ("Test Suite", run_tests),
        ("Code Coverage", check_coverage)
    ]
    
    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        if not check_func():
            print(f"\n{'='*60}")
            print(f"❌ PRE-COMMIT FAILED: {check_name}")
            print(f"{'='*60}\n")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ ALL CHECKS PASSED - Commit allowed")
    print("="*60 + "\n")
    sys.exit(0)

if __name__ == '__main__':
    main()