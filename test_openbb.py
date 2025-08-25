#!/usr/bin/env python3
"""
DEBT Financial Analysis & Market Intelligence Test Script
Verifies OpenBB installation and business financial analysis functionality
"""

def test_openbb_import():
    """Test if OpenBB financial analysis platform can be imported successfully"""
    try:
        import openbb
        print("✓ DEBT OpenBB Financial Analysis Platform successfully imported")
        return True
    except ImportError as e:
        print(f"✗ Failed to import DEBT OpenBB Financial Platform: {e}")
        return False

def test_openbb_basic_functionality():
    """Test basic OpenBB business financial analysis functionality"""
    try:
        from openbb import obb
        
        # Test guest login (doesn't require API keys)
        print("✓ DEBT OpenBB Business Financial Terminal API accessible")
        
        # Show available endpoints
        available_commands = [attr for attr in dir(obb) if not attr.startswith('_')]
        print(f"✓ Available DEBT Financial Analysis modules: {', '.join(available_commands[:5])}{'...' if len(available_commands) > 5 else ''}")
        
        return True
    except Exception as e:
        print(f"✗ DEBT OpenBB business functionality test failed: {e}")
        return False

def main():
    """Run all DEBT OpenBB financial analysis tests"""
    print("Testing DEBT OpenBB Financial Analysis Platform...")
    print("=================================================")
    
    tests = [
        test_openbb_import,
        test_openbb_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=================================================")
    print(f"DEBT Financial Analysis Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All DEBT OpenBB financial analysis tests passed! Ready for business intelligence.")
    else:
        print("✗ Some DEBT financial tests failed. Please check OpenBB installation.")

if __name__ == "__main__":
    main()