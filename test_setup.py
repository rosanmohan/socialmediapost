"""
Test script to verify setup is correct
"""
import sys
import os

print("=" * 60)
print("Social Media Agent - Setup Verification")
print("=" * 60)
print()

# Check Python version
print(f"[OK] Python Version: {sys.version}")
print(f"[OK] Python Executable: {sys.executable}")
print()

# Check virtual environment
venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if venv_active:
    print("[OK] Virtual Environment: ACTIVE")
else:
    print("[WARN] Virtual Environment: NOT ACTIVE (but may still work)")
print()

# Test imports
print("Testing imports...")
try:
    from database import init_db
    print("[OK] Database module imported")
except Exception as e:
    print(f"[FAIL] Database module failed: {e}")

try:
    from config import *
    print(f"[OK] Config module imported (LLM Provider: {LLM_PROVIDER})")
except Exception as e:
    print(f"[FAIL] Config module failed: {e}")

try:
    from news_service import NewsService
    print("[OK] News service imported")
except Exception as e:
    print(f"[FAIL] News service failed: {e}")

try:
    from content_generator import ContentGenerator
    print("[OK] Content generator imported")
except Exception as e:
    print(f"[FAIL] Content generator failed: {e}")

try:
    from media_generator import MediaGenerator
    print("[OK] Media generator imported")
except Exception as e:
    print(f"[FAIL] Media generator failed: {e}")

try:
    from pipeline import Pipeline
    print("[OK] Pipeline imported")
except Exception as e:
    print(f"[FAIL] Pipeline failed: {e}")

print()

# Test database
print("Testing database...")
try:
    init_db()
    print("[OK] Database initialized successfully")
except Exception as e:
    print(f"[FAIL] Database initialization failed: {e}")

print()
print("=" * 60)
print("Setup verification complete!")
print("=" * 60)
print()
print("Next steps:")
print("1. Edit .env file and add your API keys")
print("2. Run: python quick_start.py")
print("3. Run: python main.py --mode run --slot test")

