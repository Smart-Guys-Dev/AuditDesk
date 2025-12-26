
import sys
import os

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

from src.database import db_manager

try:
    db_manager.init_db()
    
    print("--- ROI Stats ---")
    roi_stats = db_manager.get_roi_stats()
    print(roi_stats)
    
    print("\n--- Dashboard Stats ---")
    dash_stats = db_manager.get_dashboard_stats()
    print(dash_stats)
    
    print("\n--- Checking for NaNs ---")
    import math
    
    for r in roi_stats.get('top_rules', []):
        val = r['total_impact']
        print(f"Rule: {r['rule_id']}, Impact: {val}, Type: {type(val)}")
        if isinstance(val, float) and math.isnan(val):
            print("FOUND NaN in ROI Stats!")

except Exception as e:
    print(f"Error running debug: {e}")
