#!/usr/bin/env python3
"""
DEBT AI Business Assistant (ShellGPT) Test Script
Verifies ShellGPT installation and AI business assistance functionality
"""

import subprocess
import sys

def test_shellgpt_import():
    """Test if DEBT AI Business Assistant (ShellGPT) can be imported successfully"""
    try:
        import sgpt
        print("✓ DEBT AI Business Assistant (ShellGPT) successfully imported")
        return True
    except ImportError as e:
        print(f"✗ Failed to import DEBT AI Business Assistant: {e}")
        return False

def test_shellgpt_command():
    """Test if DEBT AI business assistant sgpt command is available"""
    try:
        result = subprocess.run(['sgpt', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ DEBT AI Business Assistant command available: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ DEBT AI Business Assistant command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ DEBT AI Business Assistant command timed out")
        return False
    except FileNotFoundError:
        print("✗ DEBT AI Business Assistant (sgpt) command not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error running DEBT AI Business Assistant command: {e}")
        return False

def test_shellgpt_help():
    """Test if ShellGPT help works"""
    try:
        result = subprocess.run(['sgpt', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'usage:' in result.stdout.lower():
            print("✓ ShellGPT help command works")
            return True
        else:
            print("✗ ShellGPT help command failed")
            return False
    except Exception as e:
        print(f"✗ Error running sgpt help: {e}")
        return False

def show_usage_examples():
    """Show business usage examples for DEBT AI Assistant"""
    print("\n" + "=" * 60)
    print("DEBT AI Business Assistant Usage Examples:")
    print("=" * 60)
    print("# Business Intelligence queries:")
    print("sgpt 'analyze quarterly sales performance trends'")
    print("sgpt 'explain key business metrics for financial reporting'")
    print("")
    print("# Business code generation:")
    print("sgpt --code 'create a python script for financial dashboard'")
    print("sgpt --code 'generate business intelligence reporting functions'")
    print("")
    print("# Business automation commands:")
    print("sgpt --shell 'find all business reports modified in last 24 hours'")
    print("sgpt --shell 'backup financial data files to secure location'")
    print("")
    print("# Execute business automation directly:")
    print("sgpt --shell 'list quarterly report contents' --execute")
    print("")
    print("# Interactive business consultation mode:")
    print("sgpt --repl")
    print("")
    print("Note: For full DEBT business functionality, configure your API key.")
    print("Run 'sgpt --install-integration' for DEBT business setup instructions.")

def main():
    """Run all DEBT AI Business Assistant tests"""
    print("Testing DEBT AI Business Assistant (ShellGPT)...")
    print("=" * 50)
    
    tests = [
        test_shellgpt_import,
        test_shellgpt_command,
        test_shellgpt_help
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"DEBT AI Business Assistant Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All DEBT AI Business Assistant tests passed! Ready for business intelligence.")
        show_usage_examples()
    else:
        print("✗ Some DEBT AI tests failed. Please check ShellGPT installation.")
        if passed > 0:
            show_usage_examples()

if __name__ == "__main__":
    main()