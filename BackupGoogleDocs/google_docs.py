from googleapiclient.discovery import build

from google_creds import get_creds

class GoogleDocs:

    def __init__(self) -> None:
        self.service = build('docs', 'v1', credentials=get_creds())

    def get(self, id, filter_fields=[]):
        result = self.service.documents().get(documentId=id).execute()

        if len(filter_fields) == 0:
            return result
        
        res_dict = {}
        if "title" in filter_fields:
            res_dict["title"] = result.get('title')
        
        if "text" in filter_fields:
            text = ""
            body = result.get('body')
            if body is not None:
                for content in body["content"]:
                    paragraph = content.get("paragraph")
                    if paragraph is not None:
                        elements = paragraph.get("elements")
                        if elements is not None:
                            for element in elements:
                                textRun = element.get("textRun")
                                if textRun is not None:
                                    content2 = textRun.get('content')
                                    if content2 is not None:
                                        text += content2
            res_dict["text"] = text

        return res_dict
