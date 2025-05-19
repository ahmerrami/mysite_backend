import subprocess
from datetime import datetime, timedelta
import os
from decouple import config

# === Configuration ===
username = config('DB_USER')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
database = config('DB_NAME')
host = config('DB_HOST')
backup_dir = f"/home/{username}/mysite"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

# === Commande mysqldump ===
command = [
    "mysqldump",
    f"--host={host}",
    f"--user={db_user}",
    f"--password={db_password}",
    "--no-tablespaces",
    "--column-statistics=0",
    database
]

# === Exécution de la commande ===
with open(backup_file, "w") as f:
    result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)

# === Vérification du résultat ===
if result.returncode != 0:
    print("❌ Erreur lors de la sauvegarde :", result.stderr)
else:
    print(f"✅ Backup enregistré : {backup_file}")

# === Nettoyage des anciens fichiers ===
days_to_keep = 10
now = datetime.now()

for filename in os.listdir(backup_dir):
    if filename.startswith("backup_") and filename.endswith(".sql"):
        file_path = os.path.join(backup_dir, filename)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_mtime > timedelta(days=days_to_keep):
            os.remove(file_path)
            print(f"🗑️ Supprimé : {file_path}")
