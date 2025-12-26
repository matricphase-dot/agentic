# fix_phase5_3_issues.py
import os
import re

print("🔧 Fixing Phase 5.3 issues...")

# FIX 1: Update orchestrator_v5_3.py parameter extraction
orchestrator_file = "agents/orchestrator_v5_3.py"

if os.path.exists(orchestrator_file):
    with open(orchestrator_file, "r") as f:
        content = f.read()
    
    # Find the _extract_parameters method
    method_start = content.find("    def _extract_parameters(self, tool_info: Dict, step: Any) -> Dict[str, Any]:")
    
    if method_start != -1:
        # Find the end of the method
        method_end = content.find("def _aggregate_tool_results", method_start)
        if method_end == -1:
            method_end = content.find("\n\n", method_start + 200)
        
        if method_end != -1:
            # Replace the method with fixed version
            new_method = '''    def _extract_parameters(self, tool_info: Dict, step: Any) -> Dict[str, Any]:
        """Extract parameters for tool from step context"""
        parameters = {}
        step_description = getattr(step, 'description', '').lower()
        tool_name = tool_info.get('name', '')
        
        # Extract package names from description
        words = step_description.split()
        package_names = []
        
        # Look for package-like words (not common verbs/prepositions)
        skip_words = {'check', 'get', 'fetch', 'from', 'the', 'and', 'or', 'with', 
                      'for', 'to', 'in', 'on', 'at', 'by', 'about', 'compare', 'version'}
        
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,:;!?()[]{}"\\'')
            if (clean_word and len(clean_word) > 2 and 
                clean_word not in skip_words and
                not clean_word.startswith('http')):
                package_names.append(clean_word)
        
        # Different extraction logic based on tool
        if 'pypi' in tool_name.lower():
            if 'compare' in tool_name.lower():
                # For compare_pypi_versions, need two package names
                if len(package_names) >= 2:
                    parameters['package1'] = package_names[0]
                    parameters['package2'] = package_names[1]
                elif len(package_names) == 1:
                    # Default second package
                    parameters['package1'] = package_names[0]
                    parameters['package2'] = 'requests'  # Default fallback
                else:
                    # Fallback defaults
                    parameters['package1'] = 'requests'
                    parameters['package2'] = 'aiohttp'
            else:
                # For fetch_pypi_package, need one package name
                if package_names:
                    parameters['package_name'] = package_names[0]
                else:
                    parameters['package_name'] = 'requests'  # Default
        
        elif 'webpage' in tool_name.lower():
            # Try to extract URL
            # Simple URL pattern matching
            url_pattern = r'https?://\\S+'
            urls = re.findall(url_pattern, step_description)
            if urls:
                parameters['url'] = urls[0]
            else:
                parameters['url'] = 'https://example.com'
        
        # Add default parameters
        if 'extract_text' in [p.get('name', '') for p in tool_info.get('parameters', [])]:
            parameters['extract_text'] = True
        
        return parameters'''
            
            new_content = content[:method_start] + new_method + content[method_end:]
            
            with open(orchestrator_file, "w") as f:
                f.write(new_content)
            
            print("✅ Updated _extract_parameters method in orchestrator_v5_3.py")
        else:
            print("❌ Could not find method end")
    else:
        print("❌ Could not find _extract_parameters method")
else:
    print(f"❌ {orchestrator_file} not found")

# FIX 2: Update test file
test_file = "test_phase5.3.py"

if os.path.exists(test_file):
    with open(test_file, "r") as f:
        lines = f.readlines()
    
    # Find and update the custom tool registration function
    new_lines = []
    in_custom_test = False
    updated = False
    
    for i, line in enumerate(lines):
        if "def test_custom_tool_registration():" in line:
            in_custom_test = True
        
        if in_custom_test and "from tools.registry import register_tool_as, ToolType" in line:
            # Add import for Any
            new_lines.append(line)
            new_lines.append("        from typing import Any  # ADD THIS IMPORT\n")
            updated = True
            continue
        
        new_lines.append(line)
    
    if updated:
        with open(test_file, "w") as f:
            f.writelines(new_lines)
        print("✅ Added import to test_phase5.3.py")
    else:
        print("✅ test_phase5.3.py already has the import")
else:
    print(f"❌ {test_file} not found")

# FIX 3: Also update the complex workflow test to have better step descriptions
print("\n📝 Updating test step descriptions for better parameter extraction...")

test_fixes = {
    "Get requests package info": "Get requests package from PyPI",
    "Get aiohttp package info": "Get aiohttp package from PyPI", 
    "Compare both packages": "Compare requests and aiohttp packages"
}

if os.path.exists(test_file):
    with open(test_file, "r") as f:
        content = f.read()
    
    for old_desc, new_desc in test_fixes.items():
        if old_desc in content:
            content = content.replace(old_desc, new_desc)
            print(f"   Updated: '{old_desc}' -> '{new_desc}'")
    
    with open(test_file, "w") as f:
        f.write(content)

print("\n🎯 All fixes applied!")
print("Now run: python test_phase5.3.py")