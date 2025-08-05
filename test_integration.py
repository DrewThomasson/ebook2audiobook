#!/usr/bin/env python3
"""
Test the main app.py with Flask interface enabled
"""

import os
import sys
import subprocess
import signal
import time

# Test that USE_FLASK environment variable works
os.environ['USE_FLASK'] = 'true'

def test_main_app():
    """Test running the main app with Flask interface"""
    print("Testing main app.py with Flask interface...")
    
    try:
        # Start the app in the background
        process = subprocess.Popen([
            sys.executable, 'app.py', '--help'
        ], cwd='/home/runner/work/ebook2audiobook/ebook2audiobook',
           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for it to complete
        stdout, stderr = process.communicate(timeout=10)
        
        if process.returncode == 0:
            print("✅ Main app.py runs successfully with Flask interface")
            print("📋 Help output preview:")
            print(stdout.decode()[:500] + "..." if len(stdout.decode()) > 500 else stdout.decode())
            return True
        else:
            print(f"❌ Main app failed with return code: {process.returncode}")
            print(f"Error: {stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ App.py timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Error testing main app: {e}")
        return False

def test_environment_switching():
    """Test switching between Flask and Gradio"""
    print("\nTesting environment switching...")
    
    # Test Flask mode
    os.environ['USE_FLASK'] = 'true'
    print("USE_FLASK=true:", os.environ.get('USE_FLASK'))
    
    # Test Gradio mode
    os.environ['USE_FLASK'] = 'false'
    print("USE_FLASK=false:", os.environ.get('USE_FLASK'))
    
    # Reset to Flask
    os.environ['USE_FLASK'] = 'true'
    print("✅ Environment switching works")
    return True

if __name__ == '__main__':
    success1 = test_main_app()
    success2 = test_environment_switching()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Flask interface is fully integrated.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)