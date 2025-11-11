# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google.auth.transport.requests import Request
# import os

# # Define scopes
# SCOPES = ['https://www.googleapis.com/auth/drive.file']

# # Folder ID where you want to upload
# FOLDER_ID = '1wy8N4yCJNNscK_TS18zyO_ufl0-tLvtb'


# def upload_to_drive(file_path):
#     creds = None

#     # Load saved credentials if exist
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)

#     # Refresh or get new credentials if needed
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     # Build the Drive service
#     service = build('drive', 'v3', credentials=creds)

#     # File metadata including folder
#     file_metadata = {
#         'name': os.path.basename(file_path),
#         'parents': [FOLDER_ID]
#     }

#     media = MediaFileUpload(file_path, resumable=True)
#     uploaded_file = service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id'
#     ).execute()

#     print(f"✅ File uploaded successfully! File ID: {uploaded_file.get('id')}")

# # Example usage
# upload_to_drive('tickets/ticket_TKT000028.pdf')


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import os
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1wy8N4yCJNNscK_TS18zyO_ufl0-tLvtb'


def get_service():
    """Get authenticated Google Drive service"""
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)


def upload_to_drive(file_path):
    """Upload file to Google Drive"""
    service = get_service()
    file_metadata = {'name': os.path.basename(file_path), 'parents': [FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def download_from_drive(file_id, save_path):
    """Download file from Google Drive"""
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    
    fh = io.FileIO(save_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    return save_path


def list_drive_files():
    """List all backup files in Google Drive"""
    service = get_service()
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name, createdTime, size)"
    ).execute()
    return results.get('files', [])
