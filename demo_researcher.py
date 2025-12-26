"""
Demo script for Phase 5.2 - Shows real-world usage
"""

from agents.researcher import ResearcherAgent

def main():
    print("🎬 Phase 5.2 - Researcher Agent Demo")
    print("=" * 50)
    
    # Initialize researcher
    researcher = ResearcherAgent()
    
    # Demo 1: Package research
    print("\n📦 DEMO 1: Package Research")
    print("-" * 30)
    
    packages_to_research = ["langchain", "openai", "pydantic"]
    
    for package in packages_to_research:
        print(f"\nResearching {package}...")
        data = researcher.fetch_pypi_package(package)
        
        if data["success"]:
            print(f"  ✅ Latest version: {data['latest_version']}")
            print(f"  📝 {data['summary'][:80]}..." if data.get('summary') else "  📝 No summary")
            print(f"  👤 Author: {data.get('author', 'Unknown')}")
            print(f"  🔗 Homepage: {data.get('home_page', 'N/A')}")
        else:
            print(f"  ❌ Failed: {data.get('error')}")
    
    # Demo 2: Version comparison
    print("\n\n🔍 DEMO 2: Version Comparison")
    print("-" * 30)
    
    comparison = researcher.compare_pypi_versions("flask", "fastapi")
    if comparison["success"]:
        p1 = comparison["package1"]
        p2 = comparison["package2"]
        comp = comparison["comparison"]
        print(f"\n{p1['name']} {p1['version']} {comp['difference']} {p2['name']} {p2['version']}")
        print(f"Newer package: {comp['newer_package']}")
    else:
        print(f"Comparison failed: {comparison.get('error')}")
    
    # Demo 3: API Testing
    print("\n\n🌐 DEMO 3: API Integration")
    print("-" * 30)
    
    # Test with httpbin
    api_result = researcher.call_api(
        "https://httpbin.org/post",
        method="POST",
        json_data={"demo": "phase5.2", "timestamp": "now"}
    )
    
    if api_result["success"]:
        print(f"✅ API call successful")
        print(f"📊 Status code: {api_result['status_code']}")
        print(f"📦 Response type: {api_result['data_type']}")
    else:
        print(f"❌ API call failed: {api_result.get('error')}")
    
    # Demo 4: Statistics
    print("\n\n📊 DEMO 4: Performance Statistics")
    print("-" * 30)
    
    stats = researcher.get_stats()
    print(f"Total requests made: {stats['requests_made']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Error rate: {(stats['errors'] / stats['requests_made'] * 100):.1f}%" if stats['requests_made'] > 0 else "0%")
    print(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
    
    print("\n" + "=" * 50)
    print("🎯 Demo Complete! Your researcher agent is ready for real work.")
    print("\nNext steps:")
    print("1. Integrate with your orchestrator")
    print("2. Add more data sources (GitHub API, Stack Overflow, etc.)")
    print("3. Implement caching to disk for persistence")
    print("4. Add authentication for private APIs")

if __name__ == "__main__":
    main()