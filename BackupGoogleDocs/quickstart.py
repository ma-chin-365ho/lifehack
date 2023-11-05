from __future__ import print_function

from googleapiclient.errors import HttpError

from google_drive import GoogleDrive, MINE_TYPE_DOCS
from google_docs import GoogleDocs

target_folder_id = ""

def main():

    try:
        gdrive = GoogleDrive()
        gdocs = GoogleDocs()

        gfiles = gdrive.ls(target_folder_id, is_recursive= True)

        text_dicts = []
        for gfile in gfiles:
            if gfile["mimeType"] == MINE_TYPE_DOCS:
                text_dict = gdocs.get(gfile["id"], filter_fields=["title", "text"])
                text_dicts.append(text_dict)
        print(text_dicts)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()