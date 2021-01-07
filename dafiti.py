import requests
import os
from bs4 import BeautifulSoup
import multiprocessing
from multiprocessing import Pool, Process

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

NUMBER_THREADS = 2

class CrawlerDafiti():
    def __init__(self):
        jobs = []

        for url_grid in self.getInitialUrls():
            # self.getGridProducts(
            #     url_grid
            # )

            p = multiprocessing.Process(target=self.getGridProducts, args=(url_grid,))
            jobs.append(p)

        for i in self.chunks(jobs,NUMBER_THREADS):
            for j in i:
                j.start()
            for j in i:
                j.join()

    def chunks(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def getInitialUrls(self):
        array_urls = []
        
        initial_request = requests.get('https://www.dafiti.com.br/')
        initial_soup = BeautifulSoup(initial_request.content, 'html.parser')

        for url_block in initial_soup.select('li.menu-dropdown-title a.menu-dropdown-link'):
            if url_block.has_attr('href'):
                url = url_block['href']
                if url not in array_urls:
                    array_urls.append(
                        url
                    )

        return array_urls

    def getGridProducts(self, url_grid):
        url_grid_base = url_grid
        page = 1

        while True:
            print ('[ PAGE ]',url_grid,'\n')

            requisicao_grid = requests.get(url_grid)
            soup_grid = BeautifulSoup(requisicao_grid.content, 'html.parser')

            jobs = []

            array_products = soup_grid.select('div.product-box a.product-box-link.is-lazyloaded.image.product-image-rotate')
            if len(array_products) != 0:
                for url_product_block in array_products:
                    if url_product_block.has_attr('href'):
                        url_product = url_product_block['href']
                        # self.getProductDetails(
                        #     url_product
                        # )
                        p = multiprocessing.Process(target=self.getProductDetails, args=(url_product,))
                        jobs.append(p)

                for i in self.chunks(jobs,NUMBER_THREADS):
                    for j in i:
                        j.start()
                    for j in i:
                        j.join()

                page+=1
                url_grid = str(url_grid_base) + '?page={}'.format(page)
            else:
                break

    def getProductDetails(self, url_product):
        print ('[ PRODUCT ]',url_product)

        requisicao_product = requests.get(url_product)
        soup_product = BeautifulSoup(requisicao_product.content, 'html.parser')

        dict_product = {
                'product_name' : self.soupStringTreatment( soup_product.find('h1', {'itemprop' : 'name'}) ),
                'product_url' : url_product,
                'product_details' : self.soupStringTreatment( soup_product.find('p', {'itemprop' : 'description'}) ),
                'product_brand' : self.soupStringTreatment( soup_product.find('a', {'itemprop' : 'brand'}) ),
                'product_value_with_discount' : self.soupStringTreatment( soup_product.find('span', {'data-field' : 'finalPrice'}) ),
        }

        self.saveProductInFile(dict_product)

    def saveProductInFile(self, dict_product):
        if 'products.csv' not in os.listdir(ROOT_DIR):
            file = open(f'{ROOT_DIR}/products.csv', 'w', encoding='utf-8')
            file.write('{};{};{};{};{}\n'.format(
                'product_name', 'product_url', 'product_details', 'product_brand', 'product_value_with_discount'
            ))
            file.close()

        file = open(f'{ROOT_DIR}/products.csv', 'a+', encoding='utf-8')
        file.write('{};{};{};{};{}\n'.format(
            dict_product['product_name'],
            dict_product['product_url'],
            dict_product['product_details'],
            dict_product['product_brand'],
            dict_product['product_value_with_discount'],
        ))
        file.close()

    def soupStringTreatment(self, string):
        if string != None:
            return str(string.text).strip().replace('\n','.').replace('\t','.').replace('\r','.').replace(';','.').strip()
        else:
            return ''

if __name__ == "__main__":
    CrawlerDafiti()