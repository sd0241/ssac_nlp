import scrapy
from scrapy.http import Request
import pandas as pd
from scrapy_basic.items import MyscraperItem

URL = 'https://movie.naver.com/movie/bi/mi/reviewread.naver?nid={1}&code={0}' # scrapy를 시작할 URL
start_page = 0


class MybotSpider(scrapy.Spider): # 초기 값 지정
    name = 'mybot'
    allowed_domains = ['naver.com']
    df = pd.read_csv('movie_review_16.csv', index_col=0) # id, nid정보가 저장된 데이터 로드
    codes = list(df['idx'].unique())[:2]
    df_dic = dict((i, a) for i, a in zip(df['idx'], df['nid']))
    nides = df_dic[codes[0]][2:9]
    print(nides)
    start_urls = [URL.format(codes[start_page], nides)] # 초기 Scrapy 주소 지정
    print(start_urls)
    print('============='*5)


    def start_requests(self): # Scrap 클래스
        # code = 143267
        # nides = ['3543461', '4298288', '4764750', '2799073', '3556852', '3712539', '3659882', '4351564', '4346474',
        #          '4388952']
        df = pd.read_csv('movie_review_16.csv', index_col=0)
        codes = list(df['idx'].unique())
        df_dic = dict((i, a) for i, a in zip(df['idx'], df['nid'])) # ID와 nid를 dict로 저장
        print(type(df_dic))
        print(codes)
        print(type(codes))

        for code in codes: # 영화 코드 반복
            for nid in eval(df_dic[code]): # 리뷰 nid 코드 반복 / eval : string을 list형태로 변환
                print(type(eval(df_dic[code])))
                print(df_dic[code])
                print(code)
                # nid = df_dic[code][2:9]
                print(nid)
                print('========='  * 6)
                yield Request(url=URL.format(code, nid), callback=self.parse) # ID와 nid for문을 실행하면서 parse 실행

    def parse(self, response):
        titles = response.xpath('//*[@id="content"]/div[1]/div[2]/div[1]/h3/a/text()').extract() # title Xpath에서 Text 추출
        # reviews = response.xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div[4]/p[5]/text()').extract()
        reviews = [ ' '.join(line.strip()
                for line in p.xpath('.//text()').extract() # p 태그에서 text를 추출하여, 띄워쓰기 기준으로 문자르 합침
                if line.strip() )
            for p in response.xpath('//*[@id="content"]/div[1]/div[4]/div[1]//p') # 작성자 Xpath에서 p 태그 까지 접근
        ]

        print(titles)
        print(reviews)
        print('++++++++++++'*3)

        scraped_info = {
            'title': titles,
            'review': reviews} # 저장된 title과 review를 csv파일 정보로 보냄
        yield scraped_info




