"""تطبيق جميع التصحيحات دفعة واحدة."""
import os, sys, importlib

PATCH_DIR = os.path.dirname(__file__)
PROJECT = os.path.abspath(os.path.join(PATCH_DIR, ".."))

def apply_all():
    patches = sorted([f for f in os.listdir(PATCH_DIR) if f.startswith("patch_") and f.endswith(".py")])
    for p in patches:
        mod = importlib.import_module(f"patches.{p[:-3]}")
        if hasattr(mod, "apply"):
            print(f"Applying {p}...")
            mod.apply(PROJECT)
