#!/usr/bin/env python3
"""
Verification script for root-bot project restructuring
"""
import sys
import importlib.util
from pathlib import Path

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")

    try:
        sys.path.insert(0, str(Path.cwd()))
        from bots.watson.main import WatsonBot
        print("✅ Watson bot import successful")
    except Exception as e:
        print(f"❌ Watson bot import failed: {e}")
        return False

    try:
        from shared.cache import SimpleCache
        from shared.database import DatabaseManager
        from shared.exceptions import TradingBotError
        from shared.monitoring import MetricsCollector
        from shared.notifier import NotificationManager
        print("✅ Shared modules import successful")
    except Exception as e:
        print(f"❌ Shared modules import failed: {e}")
        return False

    try:
        import topgun
        print("✅ Topgun import successful")
    except Exception as e:
        print(f"❌ Topgun import failed: {e}")
        return False

    return True

def test_file_structure():
    """Test that required files exist"""
    print("🔍 Testing file structure...")

    required_files = [
        "env/.env",
        "env/.env.local", 
        "env/.env.example",
        "env/.env.production",
        "config/base.yml",
        "config/development.yml",
        "config/production.yml",
        "config/init.sql",
        "shared/cache.py",
        "shared/database.py",
        "shared/exceptions.py",
        "shared/monitoring.py",
        "shared/notifier.py",
        "bots/watson/main.py",
        "bots/watson/requirements.txt",
        "docs/setup.md"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def main():
    """Main verification function"""
    print("🚀 Starting root-bot restructure verification...")

    structure_ok = test_file_structure()
    imports_ok = test_imports()

    if structure_ok and imports_ok:
        print("🎉 All verification tests passed!")
        return 0
    else:
        print("❌ Some verification tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())