import os

print("Test started")
print(f"Current dir: {os.getcwd()}")

# Test 1: Check index.html exists
if os.path.exists('webapp/static/index.html'):
    print("✓ index.html found")
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'Уведомления' in content and 'notify-trades' in content:
        print("✓ Notification settings found")
    else:
        print("✗ Notification settings NOT found")
        
    if 'today-trades' in content:
        print("✓ Today statistics found")
    else:
        print("✗ Today statistics NOT found")
else:
    print("✗ index.html NOT found")

# Test 2: Check server.py exists
if os.path.exists('webapp/server.py'):
    print("✓ server.py found")
    with open('webapp/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '/api/settings/notifications' in content:
        print("✓ Notifications API endpoint found")
    else:
        print("✗ Notifications API endpoint NOT found")
        
    if 'today' in content and 'date.today()' in content:
        print("✓ Today statistics logic found")
    else:
        print("✗ Today statistics logic NOT found")
else:
    print("✗ server.py NOT found")

print("\nTest completed")
