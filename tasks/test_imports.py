import sys
print(f"Python: {sys.executable}")

try:
    import rest_framework
    print("✅ DRF imported")
except ImportError as e:
    print(f"❌ DRF failed: {e}")

try:
    import django_filters
    print("✅ Django Filters imported")
except ImportError as e:
    print(f"❌ Filters failed: {e}")

try:
    import drf_spectacular
    print("✅ DRF Spectacular imported")
except ImportError as e:
    print(f"❌ Spectacular failed: {e}")