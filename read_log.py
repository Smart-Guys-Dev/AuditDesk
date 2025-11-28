
import os

log_file = 'audit_plus.log'
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print("".join(lines[-50:]))
else:
    print("Log file not found.")
