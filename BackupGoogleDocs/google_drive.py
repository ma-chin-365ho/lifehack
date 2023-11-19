from googleapiclient.discovery import build

from google_creds import get_creds

MINE_TYPE_FOLDER = "application/vnd.google-apps.folder"
MINE_TYPE_DOCS = "application/vnd.google-apps.document"

class GoogleDrive:

    def __init__(self) -> None:
        self.service = build('drive', 'v3', credentials=get_creds())

    def ls(self, folder_id, is_recursive = False, add_fields=[]):
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
                        sub_items.extend(self.ls(item["id"], is_recursive = True, add_fields=[]))
                items.extend(sub_items)

            if "parents_path" in add_fields:
                for item in items:
                    s_path = ""
                    tmp_item = item
                    while True:
                        parents = tmp_item.get("parents")
                        if parents is not None and len(parents) != 0:
                            if parents[0] == folder_id:
                                break
                            else:
                                is_hit_parents_folder = False
                                is_hit_parents_path_chache = False
                                for item2 in items:
                                    if item2["mimeType"] == MINE_TYPE_FOLDER and item2["id"] == parents[0]:
                                        is_hit_parents_folder = True
                                        if s_path != "":
                                            s_path = "/" + s_path
                                        s_path = item2["name"] + s_path
                                        tmp_item = item2

                                        parents_path = item2.get("parents_path")
                                        if parents_path is not None:
                                            is_hit_parents_path_chache = True
                                            if item2["parents_path"] != "":
                                                s_path = "/" + s_path
                                            s_path = item2["parents_path"] + s_path
                                        break
                                if is_hit_parents_folder == False or is_hit_parents_path_chache == True:
                                    break
                        else:
                            break
                    item["parents_path"] = s_path
                
            return items
