import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
from pprint import pprint


class Gs:
    # небольшая обертка над googleSHeetsAPI
    service = None
    sheetId = None
    pageId = None
    # инициализируем подключение
    def __init__(self, sheetId = None):
        CREDENTIALS_FILE = 'key.json'  
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets'])
        httpAuth = credentials.authorize(httplib2.Http()) 
        self.service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) 
        # если был передан айди документа, записываем его
        self.sheetId = sheetId

    # биндим страницу, что бы можно было не указывать его в дальнейшем
    def bindSheetId(self, sheetId):
        self.sheetId = sheetId

    # биндим лист, что бы можно было не указывать его в дальнейшем
    def bindPage(self, pageId):
        self.pageId = pageId

    # получение айдишника листа по названию
    def getSheetIdByTitle(self, title, sheetId=None):
        sheetId = sheetId if sheetId else self.sheetId
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId = sheetId).execute()
        except:
            return -1
        sheetList = spreadsheet.get('sheets')
        for sheet in sheetList:
            if sheet['properties']['title'] == title:
                return sheetList[0]['properties']['sheetId']
        return -1
           
    # всталвение данных в таблицу передаются
    def pasteData(self, page, range, values, majorDemision = "ROWS"):
        range = page+"!"+range
        try:
            self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.sheetId, body = {
                "valueInputOption": "USER_ENTERED", # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": range,
                     "majorDimension": majorDemision,    
                     "values": values}
                ]
            }).execute()
        except Exception as e:
            return -1

    # чтение данных с листа
    def getSheetData(self, page, range=None):
        if range:
            ranges = page+"!"+range
        else:
            ranges = page+"!A:QQQ"
        try:
            results = self.service.spreadsheets().values().batchGet(spreadsheetId = self.sheetId, 
                                                 ranges = ranges, 
                                                 valueRenderOption = 'FORMATTED_VALUE',  
                                                 dateTimeRenderOption = 'FORMATTED_STRING').execute() 
            sheet_values = results['valueRanges'][0]['values']
            return sheet_values
        except Exception as e:
            return -1
