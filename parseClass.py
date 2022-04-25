import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class parseWb:
    # обертка над парсером
    # начальные ссылки, которые нужны под 2 типа поисков
    parseByCodeLink = "https://www.wildberries.ru/catalog/internalNum/detail.aspx?targetUrl=XS"                
    parseBySearchLink = "https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search=searchWord"
    def __init__(self, url = None):
        #тут следует передавать другие параметры, например сколько страниц следует искать
        self.url = url

    def parseByCode(self, code):
        # парсинг страницы по артукулу
        #формируем нужный линк
        url = self.parseByCodeLink
        url = url.replace('internalNum', code)

        #инстанцируем драйвер
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        #загружаем страницу
        driver.get(url)
        # Знаю(( по-хорошему здесь слеует ждать не тайм_слип, а ровно столько - сколько нужно на подгрузку страницы
        #WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_class_name('product-card__img'))
        time.sleep(5)  # ))

        # получаем код странички
        htmlContent = driver.page_source
        # инстанцируем объект бс4 с уже загруженный страницей
        soup = BeautifulSoup(htmlContent, 'html5lib')
        # из priceBlock'a получаем количество отзывов и цену
        priceBlock = soup.find(attrs = {"id":{"infoBlockProductCard"}})
        reviewCount = priceBlock.find('span', class_="same-part-kt__count-review").text
        finalPrice = priceBlock.find('span', class_="price-block__final-price").text
        
        # изначально точный рейтинг нам не доступн, он находится в блоке с комментариями
        commentLink = soup.find(attrs = {"id":{"comments_reviews_link"}}).get('href')
        # загружаем блок с комментариями
        driver.get(commentLink)
        time.sleep(5)   # )))
        htmlContent = driver.page_source
        driver.quit()

        soup = BeautifulSoup(htmlContent, 'html5lib')
        # находим точный рейтинг на страничке
        ratingDiv = soup.find(attrs={"class":{"user-scores__score"}})
        return {'rating': ratingDiv.text, 'reviewCount': reviewCount, 'finalPrice': finalPrice}

    def parseBySearchWord(self, serachWord, itemCode):
        # парсинг страницы по поисковому слову
        #формируем нужный линк
        url = self.parseBySearchLink
        serachWord = serachWord.replace(' ', '+')
        url = url.replace('searchWord', serachWord)

        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        page = 0
        myItem = None
        # ищем значения до тех пор, пока не найдем нужный артикул на странице или страница не станет больше 10
        while myItem == None and page < 10:
            page+=1
            url = url+"&page="+str(page)

            driver.get(url)
            time.sleep(3)  

            htmlContent = driver.page_source
            soup = BeautifulSoup(htmlContent, 'html5lib')
            # если в списке нет нужного нам артикула, то открываем нест страницу
            myItem = soup.find(attrs={"data-popup-nm-id": itemCode})
            if myItem:
                return page
            else:
                myItem = None
        return -1
