# coding: utf-8

import sqlite3
import re
import hashlib
import os

# Variables
db = 'C:/temp/fzs_log.db'
logPath = "C:/Program Files (x86)/FileZilla Server/Logs/"
regexpr = '''(\(\d*\)) (\d{2}\/\d{2}\/\d{4}) (\d{2}:\d{2}:\d{2}) - (.*) \((([0-9]{1,}\.?){4})\)> (.*)'''

# Création de la base de données
try:
    print("Création des tables et des vues...")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "fzs_log" ( `id` TEXT, `date` TEXT, `hour` TEXT, `user` TEXT, `ip` TEXT, `message` TEXT, `logFile` TEXT, `checksum` TEXT, PRIMARY KEY(`checksum`) )
    """)
    conn.commit()
except Exception as e:
    print("Error")
    conn.rollback()
    # raise e
finally:
    conn.close()

# Get logfiles
if not os.path.isdir(logPath):
    print("Dossier de log FileZilla Server non trouvé.")
    exit(2)
logFiles = os.listdir(logPath)
# Garder que les 2 derniers fichiers
logFiles = logFiles[-2:]
# try:
for fileName in logFiles:
    print("Traitement de", fileName+"...")
    try:
        with open(logPath+fileName, "r", encoding="utf8") as fichier:
            for line in fichier:
                try:
                    id=date=hour=user=ip=message=checksum=None
                    m = re.search(regexpr, line)
                    checksum = int(hashlib.sha1(m.group(0).encode('utf_8')).hexdigest(), 16) % (10 ** 10)
                    checksum = str(checksum)
                    id = m.group(1)
                    date = m.group(2)
                    hour = m.group(3)
                    user = m.group(4)
                    ip = m.group(5)
                    message = m.group(7)
                except:
                    print("No match with line :",line)
                    continue
                try:
                    conn = sqlite3.connect(db)
                    cursor = conn.cursor()
                    conn.execute("""INSERT OR IGNORE INTO fzs_log (id, date, hour, user, ip, message, logFile, checksum) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",(id, date, hour, user, ip, message, fileName, checksum))
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(line,"> Warning! data already exist")
                    continue
                except Exception as e:
                    print("Erreur")
                    conn.rollback()
                    raise e
                finally:
                    conn.close()
    except Exception as e:
        raise e
        continue