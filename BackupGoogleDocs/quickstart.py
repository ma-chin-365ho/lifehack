from __future__ import print_function
import os
import shutil
import datetime

from googleapiclient.errors import HttpError

from google_drive import GoogleDrive, MINE_TYPE_DOCS
from google_docs import GoogleDocs

target_folder_id = "" # バックアップ対象フォルダのIDを設定
to_folder_id = "" # バックアップファイル格納先フォルダのIDを設定

TMP_DIR_NAME = "tmp"
DOCS_DIR_NAME = "docs"

def main():

    try:
        gdrive = GoogleDrive()
        gdocs = GoogleDocs()

        gfiles = gdrive.ls(target_folder_id, is_recursive= True, add_fields=["parents_path"])

        text_dicts = []
        for gfile in gfiles:
            if gfile["mimeType"] == MINE_TYPE_DOCS:
                text_dict = gdocs.get(gfile["id"], filter_fields=["title", "text"])
                text_dict["file_name"] = gfile["name"] + ".txt"
                text_dict["dir_path"] = gfile["parents_path"]
                text_dicts.append(text_dict)

        if os.path.exists(TMP_DIR_NAME):
            shutil.rmtree(TMP_DIR_NAME)
        
        for text_dict in text_dicts:
            os.makedirs(os.path.join(TMP_DIR_NAME, DOCS_DIR_NAME, text_dict["dir_path"]), exist_ok=True)
            with open(os.path.join(TMP_DIR_NAME, DOCS_DIR_NAME, text_dict["dir_path"], text_dict["file_name"]), "w") as f:
                f.write(text_dict["text"])
        
        zip_file_path = os.path.join(TMP_DIR_NAME, datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ".zip"
        zip_file_path_without_ext, _ = os.path.splitext(zip_file_path)

        shutil.make_archive(
            zip_file_path_without_ext,
            format='zip',
            root_dir=os.path.join(TMP_DIR_NAME, DOCS_DIR_NAME)
        )

        gdrive.upload(zip_file_path,to_folder_id)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()