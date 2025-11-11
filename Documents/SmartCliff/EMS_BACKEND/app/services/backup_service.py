import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote
from app.config import settings
from google_drive import upload_to_drive, download_from_drive, list_drive_files

_maintenance_mode = False

def is_maintenance_mode():
    return _maintenance_mode

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


def get_db_credentials():
    parsed = urlparse(settings.database_url )
    return {
        "user": parsed.username,
        "password": unquote(parsed.password), 
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path[1:]
    }


def create_backup():
    _maintenance_mode = True
     
     
    """Create backup, upload to Drive, delete local"""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backups/backup_{timestamp}.sql"
    
    db = get_db_credentials()
    
    env = os.environ.copy()
    env['PGPASSWORD'] = db['password']
    
    command = [
        'pg_dump',
        '-U', db['user'],
        '-h', db['host'],
        '-p', str(db['port']),
        '-d', db['database'],
        '-F', 'c',
        '-f', backup_file
    ]
    
    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        
        # Verify file
        if not os.path.exists(backup_file):
            raise Exception("Backup file was not created")
        
        file_size = os.path.getsize(backup_file)
        if file_size == 0:
            raise Exception("Backup file is empty")
        
        # Upload to Google Drive
        file_id = upload_to_drive(backup_file)
        
        # Delete local file
        os.remove(backup_file)
        _maintenance_mode = False
        return {
            "message": "✅ Backup uploaded to Google Drive",
            "file_id": file_id,
            "timestamp": timestamp,
            "size_kb": round(file_size / 1024, 2)
        }
    
    except subprocess.CalledProcessError as e:
        if os.path.exists(backup_file):
            os.remove(backup_file)
        raise Exception(f"pg_dump failed: {e.stderr}")
    
    except Exception as e:
        if os.path.exists(backup_file):
            os.remove(backup_file)
        raise Exception(f"Backup failed: {str(e)}")


def restore_from_drive(file_id: str):
    """Download from Drive and restore"""
    temp_backup = "backups/temp_restore.sql"
    
    _maintenance_mode = True
    
    try:
        download_from_drive(file_id, temp_backup)
        
        if os.path.getsize(temp_backup) == 0:
            raise Exception("Downloaded backup file is empty")
        
        db = get_db_credentials()
        env = os.environ.copy()
        env['PGPASSWORD'] = db['password']
        
        command = [
            'pg_restore',
            '-U', db['user'],
            '-h', db['host'],
            '-p', str(db['port']),
            '-d', db['database'],
            '-c',
            temp_backup
        ]
        
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        os.remove(temp_backup)
        _maintenance_mode = False

        
        return {"message": "✅ Database restored from Google Drive"}
    
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_backup):
            os.remove(temp_backup)
        raise Exception(f"pg_restore failed: {e.stderr}")
    
    except Exception as e:
        if os.path.exists(temp_backup):
            os.remove(temp_backup)
        raise Exception(f"Restore failed: {str(e)}")


def list_backups():
    return list_drive_files()
