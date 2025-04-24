# cleanup_old_logs.py
import os
import time
from datetime import datetime

# === PARAMÈTRES ===
log_dir = "."
extensions = [".csv", ".log"]
age_limit_days = 7
now = time.time()

def clean_old_logs():
    print("🧹 Suppression automatique des fichiers log de +7 jours...")
    for file in os.listdir(log_dir):
        if any(file.endswith(ext) for ext in extensions):
            path = os.path.join(log_dir, file)
            if os.path.isfile(path):
                age_days = (now - os.path.getmtime(path)) / (60 * 60 * 24)
                if age_days > age_limit_days:
                    os.remove(path)
                    print(f"🗑️ Supprimé: {file} (age: {int(age_days)}j)")
    print("✅ Nettoyage terminé.")

if __name__ == "__main__":
    clean_old_logs()