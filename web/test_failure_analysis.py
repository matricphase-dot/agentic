"""
🧪 TEST SCRIPT FOR FAILURE ANALYSIS ENGINE (Week 25-26)
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def test_failure_analysis():
    """Test the failure analysis engine"""
    
    print("🧪 Testing Failure Analysis Engine (Week 25-26)")
    print("=" * 60)
    
    # 1. Test main dashboard
    print("\n1. Testing main dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Main dashboard accessible")
        else:
            print(f"   ❌ Main dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return
    
    # 2. Test failure analysis dashboard
    print("\n2. Testing failure analysis dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/failure")
        if response.status_code == 200:
            print("   ✅ Failure analysis dashboard accessible")
        else:
            print(f"   ❌ Failure dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test failure statistics API
    print("\n3. Testing failure statistics API...")
    try:
        response = requests.get(f"{BASE_URL}/failure/api/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Statistics API working")
            print(f"   • Total failures: {data.get('stats', {}).get('overall', {}).get('total_failures', 'N/A')}")
            print(f"   • Patterns identified: {data.get('stats', {}).get('overall', {}).get('patterns_identified', 'N/A')}")
        else:
            print(f"   ❌ Statistics API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test simulating failures
    print("\n4. Testing failure simulation...")
    failure_ids = []
    for i in range(3):
        try:
            failure_data = {
                "error_type": f"TestError_{i}",
                "error_message": f"Simulated failure test {i+1} for pattern recognition"
            }
            response = requests.post(
                f"{BASE_URL}/failure/api/simulate",
                json=failure_data
            )
            if response.status_code == 200:
                data = response.json()
                failure_ids.append(data.get('failure_id'))
                print(f"   ✅ Simulated failure {i+1}: {data.get('failure_id', 'N/A')}")
            else:
                print(f"   ❌ Simulation {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 5. Wait for analysis
    print("\n5. Waiting for analysis to run...")
    time.sleep(2)
    
    # 6. Test triggering analysis
    print("\n6. Testing manual analysis trigger...")
    try:
        response = requests.post(f"{BASE_URL}/failure/api/analyze")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analysis triggered: {data.get('analyzed', 0)} failures analyzed")
        else:
            print(f"   ❌ Analysis trigger failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Test getting recent failures
    print("\n7. Testing recent failures list...")
    try:
        response = requests.get(f"{BASE_URL}/failure")
        if response.status_code == 200:
            print("   ✅ Recent failures list accessible")
        else:
            print(f"   ❌ Failed to get recent failures: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 8. Test system health endpoint
    print("\n8. Testing system health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System health: {data.get('status', 'unknown')}")
            print(f"   • Version: {data.get('version', 'N/A')}")
            print(f"   • Week: {data.get('week', 'N/A')}")
            print(f"   • Feature: {data.get('feature', 'N/A')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST SUMMARY:")
    print(f"   • Simulated {len(failure_ids)} test failures")
    print(f"   • Failure IDs: {', '.join(failure_ids[:3])}")
    print(f"   • System should now be learning from these failures")
    print(f"   • Check dashboard for pattern recognition")
    print("\n📊 Next steps:")
    print("   1. Open http://localhost:5000/failure")
    print("   2. Click 'Simulate Test Failure' button")
    print("   3. Observe pattern recognition")
    print("   4. View generated solutions")

if __name__ == "__main__":
    test_failure_analysis()