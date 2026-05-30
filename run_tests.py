#!/usr/bin/env python3
import unittest
import os, sys

HOME = os.path.expanduser("~")
PROJECT = os.path.join(HOME, ".local", "share", "FreeCAD", "v1-1", "Mod", "SmartFurnitureWB")
if not os.path.isdir(PROJECT):
    PROJECT = os.path.join(HOME, ".FreeCAD", "Mod", "SmartFurnitureWB")
sys.path.append(PROJECT)

print("🛡️  Starting SMART CABINET PRO Automated Test Suite...\n")

loader = unittest.TestLoader()
suite = loader.discover(os.path.join(PROJECT, 'tests'))
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if result.wasSuccessful():
    print("\n✅ SUCCESS: Kernel is stable. Safe to proceed to next features.")
else:
    print("\n❌ FAILURE: Regressions detected! Do not deploy.")
    sys.exit(1)
