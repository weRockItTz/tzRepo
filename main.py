from gsClass import *
from pprint import pprint
from parseClass import *
import datetime
spreadsheetId = '1AZAXtR3-JxQSXYkXISVIQO31lFbQtupoL2bErC9HIfg'


gs = Gs(spreadsheetId)
parser = parseWb()


searchData = gs.getSheetData('Лист1', 'F3:H4')                 # список условий по которым будет идти поиск (а так же высота для вставки)
header = gs.getSheetData('Лист1', 'F2:QQQ2')[0]                 # длина нашей таблици, на основе этого будем подсатвлять данные
    
# генерируем матрицу размерностью с нашу таблицу
pasteMatrix = []                                                    
for y in range((len(searchData)+10)):
    pasteMatrix.append([])
    for x in range(len(header)):
        pasteMatrix[y].append(None)

errorMatrix = []                                                # массив с ошибками
notInTenMatrix = []                                             # массив не найденых заявок
pasteRow = 1                                                    # индекс строки для вставки
#идем циклом по всем параметрам поиска
for row in searchData:
    pasteRow+=1
    dataByCode = None                                           # изначально считаем, что данные спарсить не получилось
    # парсим информацию по артиклу
    try:
        dataByCode = parser.parseByCode(row[2])
    except Exception as e:                                      # если не данные так и не спарсили, то записываем в лист ошибок
        errorRow = [row[0], row[1], row[2], e]
        errorMatrix.append(errorRow)
    if dataByCode:                                              # если успешно получилось все определить, то записываем в основную таблицу данные
        pasteMatrix[pasteRow][9] = dataByCode['rating']
        pasteMatrix[pasteRow][11] = dataByCode['reviewCount']
        pasteMatrix[pasteRow][12] = dataByCode['finalPrice']


    dataByWord = -1                                             # изначально опять же считаем, что данных нет
    # теперь папрсим инфу по поисковой строке
    try:
        dataByWord = parser.parseBySearchWord(row[0], row[2])
    except Exception as e:                                      # если сталкнулись с ошибкой - логируем
        # если натолкнулись на ошибку, то так же фиксируем ее
        errorRow = [row[0], row[1], row[2], e]
        errorMatrix.append(errorRow)
    if dataByWord != -1:                                        # если нашли данные, то записываем их на сегодняшний день
        nowDay = datetime.datetime.now().day                    # определяем сегодщняшний день
        pasteIndex = 17 + int(nowDay)*6                         
        pasteMatrix[pasteRow][pasteIndex] = dataByWord
    else:
        # если поиск по слову так и остался -1, то значит ошибок не было но и в 10 страницах запроса тоже не было
        notInTenMatrix.append([row[0], row[1], row[2]])


gs.pasteData('Лист1', 'A1:QQQ', pasteMatrix)
gs.pasteData('Не найдено на первых 10 страницах', 'A2:QQQ', notInTenMatrix)
gs.pasteData('Ошибки', 'A2:QQQ', errorMatrix)

