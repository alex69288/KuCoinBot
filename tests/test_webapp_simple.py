"""
Тест запуска webapp_simple.py
"""
import sys
import subprocess
import time
import requests
import os

def test_webapp_simple_startup():
    """Проверка запуска упрощенного webapp"""
    print("=" * 60)
    print("[TEST] Testing webapp_simple.py")
    print("=" * 60)
    
    env = os.environ.copy()
    env['PORT'] = '8002'
    
    print("\n[1] Starting server...", flush=True)
    
    process = subprocess.Popen(
        [sys.executable, 'webapp_simple.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    print("[WAIT] Waiting for server startup (5 seconds)...", flush=True)
    time.sleep(5)
    
    try:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("\n[ERROR] Server crashed!")
            print("\nSTDOUT:")
            print(stdout)
            print("\nSTDERR:")
            print(stderr)
            return False
        
        print("[OK] Process is running", flush=True)
        
        print("\n[2] Testing endpoints...", flush=True)
        
        try:
            response = requests.get('http://localhost:8002/ping', timeout=5)
            print(f"[OK] /ping: {response.status_code}")
            print(f"     Response: {response.json()}")
            
            response = requests.get('http://localhost:8002/', timeout=5)
            print(f"[OK] /: {response.status_code}")
            print(f"     Content type: {response.headers.get('content-type')}")
            
            response = requests.get('http://localhost:8002/api/health', timeout=5)
            print(f"[OK] /api/health: {response.status_code}")
            print(f"     Response: {response.json()}")
            
            print("\n[SUCCESS] All tests passed!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
            
    finally:
        print("\n[3] Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
            print("[OK] Server stopped")
        except subprocess.TimeoutExpired:
            process.kill()
            print("[WARNING] Server killed")

if __name__ == "__main__":
    try:
        success = test_webapp_simple_startup()
        
        print("\n" + "=" * 60)
        if success:
            print("[SUCCESS] webapp_simple.py works correctly!")
            print("\nReady to deploy to Amvera.")
        else:
            print("[FAILED] webapp_simple.py has issues.")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted")
        sys.exit(1)
