# test.py - SIMPLE TEST
print("="*60)
print("🧪 AGENTIC CORE - SIMPLE TEST")
print("="*60)

import os
print(f"✅ Current directory: {os.getcwd()}")

import sys
print(f"✅ Python version: {sys.version}")

print("\n📁 Checking project structure...")
folders = ['agents', 'tools', 'memory', 'tests']
for folder in folders:
    exists = os.path.exists(folder)
    print(f"   {'✅' if exists else '❌'} {folder}: {'Exists' if exists else 'Missing'}")

print("\n" + "="*60)
print("🎉 If you see this, Python is working!")
print("="*60)