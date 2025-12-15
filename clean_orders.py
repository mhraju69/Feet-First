import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

print("Cleaning up conflicting order data...")
with connection.cursor() as cursor:
    # Check if table exists first just in case
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Others_order';")
    if cursor.fetchone():
        cursor.execute("DELETE FROM Others_order")
        print("Successfully deleted all rows from Others_order table.")
    else:
        print("Others_order table not found.")
