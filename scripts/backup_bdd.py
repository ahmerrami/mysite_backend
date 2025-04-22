import subprocess
from datetime import datetime, timedelta
import os

# === Config ===
username = "errami"
database = "errami$siteweb"
backup_dir = f"/home/{username}/mysite"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

# === Sauvegarde ===
command = [
    "mysqldump",
    "--no-tablespaces",
    "--column-statistics=0",
    database
]

with open(backup_file, "w") as f:
    subprocess.run(command, stdout=f)

print(f"✅ Backup enregistré : {backup_file}")

# === Nettoyage : suppression des fichiers de plus de 10 jours ===
days_to_keep = 10
now = datetime.now()

for filename in os.listdir(backup_dir):
    if filename.startswith("backup_") and filename.endswith(".sql"):
        file_path = os.path.join(backup_dir, filename)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_mtime > timedelta(days=days_to_keep):
            os.remove(file_path)
            print(f"🗑️ Supprimé : {file_path}")
