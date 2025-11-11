from fastapi import APIRouter, Depends
from app.auth.auth_utils import role_requires
from app.services import backup_service

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("/create")
def create_backup(current_user: dict = Depends(role_requires("Admin"))):
    """Create backup and upload to Google Drive"""
    return backup_service.create_backup()


@router.get("/list")
def list_backups(current_user: dict = Depends(role_requires("Admin"))):
    """List all backups from Google Drive"""
    files = backup_service.list_backups()
    return {"total": len(files), "backups": files}


@router.post("/restore")
def restore_backup(file_id: str, current_user: dict = Depends(role_requires("Admin"))):
    """Download from Google Drive and restore database"""
    return backup_service.restore_from_drive(file_id)
