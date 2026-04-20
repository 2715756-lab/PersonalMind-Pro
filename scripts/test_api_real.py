#!/usr/bin/env python3
"""
Real API Testing Script
Tests all endpoints of the mock backend
"""
import asyncio
import json
import time
from datetime import datetime
import httpx


async def test_endpoints():
    """Test all API endpoints"""
    
    print("\n" + "="*70)
    print("🚀 PersonalMind Pro - Real API Testing")
    print("="*70 + "\n")
    
    base_url = "http://localhost:9000"
    results = []
    
    # Wait for server startup
    max_retries = 10
    for i in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    break
        except (httpx.ConnectError, httpx.TimeoutException):
            if i < max_retries - 1:
                print(f"⏳ Waiting for server to start... ({i+1}/{max_retries})")
                await asyncio.sleep(1)
            else:
                print("❌ Server failed to start!")
                return
    
    tests = [
        # 1. Health check
        {
            "name": "Health Check",
            "method": "GET",
            "path": "/health",
            "expected_status": 200,
        },
        # 2. Chat endpoint
        {
            "name": "Chat Message",
            "method": "POST",
            "path": "/chat",
            "body": {"user_id": "test_user", "message": "Hello bot!"},
            "expected_status": 200,
        },
        # 3. Memory stats
        {
            "name": "Memory Statistics",
            "method": "GET",
            "path": "/memory/stats",
            "expected_status": 200,
        },
        # 4. User profile
        {
            "name": "Get User Profile",
            "method": "GET",
            "path": "/profile?user_id=test_user",
            "expected_status": 200,
        },
        # 5. Documents list
        {
            "name": "List Documents",
            "method": "GET",
            "path": "/documents",
            "expected_status": 200,
        },
        # 6. Commerce search
        {
            "name": "Commerce Search",
            "method": "POST",
            "path": "/commerce/search",
            "body": {"query": "pizza"},
            "expected_status": 200,
        },
        # 7. Root endpoint
        {
            "name": "API Info",
            "method": "GET",
            "path": "/",
            "expected_status": 200,
        },
    ]
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for i, test in enumerate(tests, 1):
            test_name = test["name"]
            method = test["method"]
            path = test["path"]
            url = f"{base_url}{path}"
            
            print(f"\n[{i}/{len(tests)}] Testing: {test_name}")
            print(f"    {method} {path}")
            
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json=test.get("body", {}))
                
                elapsed = time.time() - start_time
                
                # Check status code
                if response.status_code == test["expected_status"]:
                    print(f"    ✅ Status: {response.status_code} ({elapsed*1000:.0f}ms)")
                    
                    # Try to parse JSON response
                    try:
                        data = response.json()
                        print(f"    📊 Response keys: {', '.join(list(data.keys())[:3])}...")
                        results.append({
                            "test": test_name,
                            "status": "PASS",
                            "code": response.status_code,
                            "time_ms": elapsed * 1000
                        })
                    except:
                        print(f"    ⚠️  Response is not JSON")
                        results.append({
                            "test": test_name,
                            "status": "PASS",
                            "code": response.status_code,
                            "time_ms": elapsed * 1000
                        })
                else:
                    print(f"    ❌ Status: {response.status_code} (expected {test['expected_status']})")
                    results.append({
                        "test": test_name,
                        "status": "FAIL",
                        "code": response.status_code,
                        "time_ms": elapsed * 1000
                    })
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                results.append({
                    "test": test_name,
                    "status": "ERROR",
                    "error": str(e)
                })
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else ("❌" if result["status"] == "FAIL" else "⚠️ ")
        time_str = f"{result.get('time_ms', 0):.0f}ms" if "time_ms" in result else "N/A"
        print(f"{status_icon} {result['test']:<30} [{time_str}]")
    
    print(f"\n{'='*70}")
    print(f"✅ Passed: {passed}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"⚠️  Errors: {errors}/{len(results)}")
    print(f"{'='*70}\n")
    
    # Overall result
    if failed == 0 and errors == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_endpoints())
    exit(exit_code)
