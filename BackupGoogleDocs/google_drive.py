from googleapiclient.discovery import build

from google_creds import get_creds

MINE_TYPE_FOLDER = "application/vnd.google-apps.folder"
MINE_TYPE_DOCS = "application/vnd.google-apps.document"

class GoogleDrive:

    def __init__(self) -> None:
        self.service = build('drive', 'v3', credentials=get_creds())

    def ls(self, folder_id, is_recursive = False):
            # Call the Drive v3 API
            items = []
            page_token = None
            while True:
                results = self.service.files().list(
                    pageSize=10,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, parents)",
                    q=f"('{folder_id}' in parents)"
                ).execute()
                items.extend(results.get('files', []))

                page_token = results.get('nextPageToken', None)
                if page_token is None:
                    break
            
            if is_recursive:
                sub_items = []
                for item in items:
                    if item['mimeType'] == MINE_TYPE_FOLDER:
                        sub_items.extend(self.ls(item["id"], is_recursive = True))
                items.extend(sub_items)
                
            return items
