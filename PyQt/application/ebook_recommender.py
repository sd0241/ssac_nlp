import sys
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import requests
import re
import pickle
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
from PyQt5.QtWidgets import QApplication, QWidget, QAbstractItemView, QCompleter, QTableWidgetItem
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

form_window = uic.loadUiType('./book_application_.ui')[0]


class Recommender(QWidget, form_window):

    # scroll bar stylesheet
    __scroll_bar_stylesheet = """
        QScrollBar:vertical {
            width:10px;    
            border: 0px solid #999999;
            background:white;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            min-height: 20px;
            border: 0px solid red;
            border-radius: 4px;
            background-color: gray;
        }
        QScrollBar::add-line:vertical {
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            height: 0 px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        
        QScrollBar:horizontal{
            height: 10px;  
            border: 0px solid #999999;
            background:white;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal{
            min-width: 20px;
            border: 0px solid red;
            border-radius: 4px;
            background-color: gray;
        }
        QScrollBar::add-line:horizontal{
            height: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:horizontal{
            width: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }
        """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("영화 추천") # window title

        # 데이터 불러오기
        self.df_book = pd.read_csv('../datasets/movie_data_final_.csv', index_col=0)
        self.df_book['year'] = self.df_book['year'].apply(lambda _: str(_))

        # tfidf.pickle 불러오기
        with open('../datasets/tfidf_komor.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)
        # matrix 불러오기
        self.Tfidf_matrix = mmread('../datasets/tfidf_movie_komor.mtx').tocsr()

        # 이미지 처리 정보
        self.pixmap = QPixmap()
        self.img_main_height = self.lbl_first_image.height()    # 메인 화면의 weekly best 책 표지 사이즈
        self.img_keyword_height = self.lbl_image_1.height()     # keyword 이용한 추천 목록 책 표지 사이즈
        self.img_height = self.lbl_book_image.height()          # 책 검색 화면의 검색 목록에서 선택한 책 표지 사이즈
        self.img_name_height = self.lbl_image_9.height()        # 지정한 책과 유사한 추천 목록  책 표지 사이즈

        # 메인화면 책 이미지와 제목
        self.main_covers = [self.lbl_first_image, self.lbl_second_image, self.lbl_third_image]
        self.main_titles = [self.lbl_first_title, self.lbl_second_title, self.lbl_third_title]

        # 키워드 추천 목록 이미지와 제목
        self.keyword_covers = [self.lbl_image_1, self.lbl_image_2, self.lbl_image_3, self.lbl_image_4,
                               self.lbl_image_5, self.lbl_image_6, self.lbl_image_7, self.lbl_image_8]
        self.keyword_titles = [self.lbl_title_1, self.lbl_title_2, self.lbl_title_3, self.lbl_title_4,
                               self.lbl_title_5, self.lbl_title_6, self.lbl_title_7, self.lbl_title_8]

        # 유사한 책 추천 목록 이미지와 제목
        self.name_covers = [self.lbl_image_9, self.lbl_image_10, self.lbl_image_11, self.lbl_image_12,
                            self.lbl_image_13, self.lbl_image_14, self.lbl_image_15, self.lbl_image_16]
        self.name_titles = [self.lbl_title_9, self.lbl_title_10, self.lbl_title_11, self.lbl_title_12,
                            self.lbl_title_13, self.lbl_title_14, self.lbl_title_15, self.lbl_title_16]

        # 라벨에 있는 하이퍼링크 이용해서 웹 페이지 열도록 설정
        for title in self.main_titles:
            title.setOpenExternalLinks(True)

        for title in self.keyword_titles:
            title.setOpenExternalLinks(True)

        for title in self.name_titles:
            title.setOpenExternalLinks(True)

        # 각 페이지 (stacked widget의 하위 페이지들) 생성
        self.generate_page_1()
        self.generate_page_2()
        self.generate_page_3()

        # 메인 화면에서 시작하도록 설정
        self.stackedWidget.setCurrentIndex(0)
        self.setStyleSheet("border-image: url(:/background/form_blue.png);")

    def generate_page_1(self):
        # 주간 베스트 3위 책 읽어오기
        url_weekly = "https://search.naver.com/search.naver?where=nexearch&query=%eb%b0%95%ec%8a%a4%ec%98%a4%ed%94%bc%ec%8a%a4%ec%88%9c%ec%9c%84"

        # 책 이미지, 제목 정보
        css_book = '#main_pack .item img'
        attr_image = 'src'
        attr_title = 'alt'

        # 책 코드 정보
        # css_code = '#category_layout .goods_name > a:nth-of-type(1)'
        # # css_code = '#category_layout .goods_name > a:first-of-type' # 나는 되는데 신궁님은 error 발생... 원인 불명
        # attr_code = 'href'
        # pat_code = re.compile(r'Goods/(.+)$')

        # weekly best 접속
        soup = BeautifulSoup(requests.get(url_weekly).text, 'lxml')
        books = soup.select(css_book)
        # codes = soup.select(css_code)

        # 읽어온 내용 중 처음 3권 화면에 노출
        for i, book in enumerate(books[:3]):
            # code = pat_code.findall(codes[i].get(attr_code))[0]

            # pixmap 이용해서 웹 상의 책 표지 이미지 다운
            cover = urllib.request.urlopen(book.get(attr_image)).read()
            self.pixmap.loadFromData(cover)

            # 책 이미지와 제목 설정
            self.main_covers[i].setPixmap(self.pixmap.scaledToHeight(self.main_covers[i].height()))
            # self.main_titles[i].setText(self.gen_title(code, book.get(attr_title)))

        # 시그널 슬롯 연결
        self.btn_find_name.clicked.connect(self.move_to_name)
        self.btn_find_keyword.clicked.connect(self.move_to_keyword)

    def generate_page_2(self):
        # 시그널 슬롯 연결
        # 검색창에서 입력 후 엔터 누르거나 검색 버튼 누르면 책 추천하도록 slot 연결
        self.le_keyword_find.returnPressed.connect(self.le_keyword_slot)
        self.btn_find.clicked.connect(self.le_keyword_slot)

        # 하단의 main 또는 이름으로 검색하는 창으로 이동하는 버튼 설정
        self.btn_main.clicked.connect(self.move_to_main)
        self.btn_name.clicked.connect(self.move_to_name)

    def generate_page_3(self):
        # line edit에 자동완성 기능 추가
        model = QStringListModel()
        model.setStringList(self.df_book['title'].unique())
        completer = QCompleter()
        completer.setModel(model)
        completer.popup().setStyleSheet(Recommender.__scroll_bar_stylesheet)    # scroll bar style 적용
        self.le_bookname_find.setCompleter(completer)

        # 책 목록 검색 결과창
        # column 설정
        tbl_book_columns = ["제목",'개봉년도', "장르"]
        self.tbl_book.setColumnCount(len(tbl_book_columns))         # column 개수 설정
        self.tbl_book.setHorizontalHeaderLabels(tbl_book_columns)   # column 값 설정

        # scroll bar style 적용
        self.tbl_book.setStyleSheet("QTableWidget {border: 1px solid #dddddd; gridline-color: #dddddd}" + Recommender.__scroll_bar_stylesheet)

        # 책 목록 기본 설정
        self.tbl_book.verticalHeader().setVisible(False)                    # row 번호 안 보이게
        self.tbl_book.setEditTriggers(QAbstractItemView.NoEditTriggers)     # 책 목록 테이블 수정 금지
        self.tbl_book.horizontalHeader().setStretchLastSection(True)        # header 넓이 꽉차게 설정
        self.tbl_book.setSelectionBehavior(QAbstractItemView.SelectRows)    # 열 전체 선택하게 설정

        # 시그널 슬롯 연결
        # 검색창에서 입력 후 엔터 누르거나 검색 버튼 누르면 책 추천하도록 slot 연결
        self.le_bookname_find.returnPressed.connect(self.le_bookname_slot)
        self.btn_find_2.clicked.connect(self.le_bookname_slot)

        # 검색한 책 목록 중에서 셀을 선택하면 선택한 책 이미지가 노출되도록 slot 연결
        self.tbl_book.cellClicked.connect(self.tbl_book_cell_clicked_slot)

        # 선택한 책과 유사한 책 추천 해주도록 slot 연결
        self.btn_similar.clicked.connect(self.btn_similar_clicked_slot)

        # 추천한 책 목록 화면에서 다시 검색 화면으로 돌아갈 수 있도록 slot 연결
        self.btn_back.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(0))

        # 하단의 main 또는 키워드로 검색하는 창으로 이동하는 버튼 설정
        self.btn_main_2.clicked.connect(self.move_to_main)
        self.btn_keyword.clicked.connect(self.move_to_keyword)

    # 키워드 검색
    def le_keyword_slot(self):
        # 현재 노출되어 있는 기존 검색 결과 책 표지와 제목 안 보이게 설정
        for i, title in enumerate(self.keyword_titles):
            title.setVisible(False)
            self.keyword_covers[i].setVisible(False)

        # 입력받은 문구를 공백 기준으로 분할
        keywords = self.le_keyword_find.text().split(' ')
        sentence = keywords * 10

        # 입력 받은 키워드들과 다른 책들과의 cosine 유사도 계산
        cosine_sim = linear_kernel(self.Tfidf.transform(sentence), self.Tfidf_matrix)

        # cosine 유사도를 기반으로 책 추천
        rec_books = self.gen_recommendation(cosine_sim)

        # 추천한 책 목록 설정
        for i, code in enumerate(rec_books.index):
            title, img = rec_books.loc[code]['title'], rec_books.loc[code]['image_link']

            # pixmap 이용해서 웹 상의 책 표지 이미지 다운
            cover = urllib.request.urlopen(img).read()
            self.pixmap.loadFromData(cover)

            # 책 이미지와 제목 설정
            self.keyword_covers[i].setPixmap(self.pixmap.scaledToHeight(self.img_keyword_height))
            self.keyword_titles[i].setText(self.gen_title(code, title))

        # 책 이미지와 제목 노출하도록 설정 (위에서 안 보이게 처리했던 거 다시 푸는 작업)
        for i, title in enumerate(self.keyword_titles):
            title.setVisible(True)
            self.keyword_covers[i].setVisible(True)

    def le_bookname_slot(self):
        # 기존에 테이블에 남아있는 정보 초기화
        self.tbl_book.clearContents()
        self.tbl_book.setRowCount(0)
        
        # 입력한 문구가 포함되어 있는 책 목록 검색
        keyword = self.le_bookname_find.text()
        books = self.df_book[self.df_book['title'].str.match(f'.*{keyword}.*')]
        
        # 책 목록 표에 검색 결과 노출
        self.tbl_book.setRowCount(len(books.index))     # row 개수 설정

        for i, code in enumerate(books.index): # 검색한 결과의 index (책 코드) 별


            for j, col in enumerate(['title','year','genre']):      # column 제목, 저자, 출판사 별
                print(col)
                print('debug5')
                item_title = QTableWidgetItem(books.loc[code][col])     # 책 목록 표의 하나의 셀 생성
                print(item_title)
                item_title.setData(Qt.UserRole, code) # 선택한 셀 식별용 책 code 저장
                print(item_title)
                self.tbl_book.setItem(i, j, item_title)    # 표에 해당 셀 추가
    def tbl_book_cell_clicked_slot(self):
        # 현재 선택한 cell에 미리 저장해 놓은 책 코드 읽어오기
        code = self.tbl_book.currentItem().data(Qt.UserRole)
        
        # 지정한 책 식별
        book = self.df_book.loc[code]

        # pixmap 이용해서 웹 상의 책 표지 이미지 다운
        cover = urllib.request.urlopen(book['image_link']).read()
        self.pixmap.loadFromData(cover)
        
        # 책 표지 노출, 추천 버튼 노출
        self.lbl_book_image.setPixmap(self.pixmap.scaledToHeight(self.img_height))
        self.lbl_book_image.setVisible(True)
        self.btn_similar.setVisible(True)

    def btn_similar_clicked_slot(self):
        # 현재 선택한 cell에 미리 저장해 놓은 책 코드 읽어오기
        code = self.tbl_book.currentItem().data(Qt.UserRole)

        # 선택한 책의 위치 index 식별 (Tfidf_matrix는 index가 코드가 아니라 그냥 순서이기 때문에)
        idx = self.df_book.index.get_loc(code)

        # 선택한 책의 벡터와 다른 책의 벡터들 간의 cosine 유사도 계산
        cosine_sim = linear_kernel(self.Tfidf_matrix[idx], self.Tfidf_matrix)

        # cosien 유사도 기반 추천 책 목록 생성
        rec_books = self.gen_recommendation(cosine_sim, code)

        # 추천한 책 목록 설정
        for i, code in enumerate(rec_books.index):

            title, img = rec_books.loc[code]['title'], rec_books.loc[code]['image_link']

            # pixmap 이용해서 웹 상의 책 표지 이미지 다운
            cover = urllib.request.urlopen(img).read()
            self.pixmap.loadFromData(cover)

            # 책 이미지와 제목 설정
            self.name_covers[i].setPixmap(self.pixmap.scaledToHeight(self.img_name_height))
            self.name_titles[i].setText(self.gen_title(code, title))

        # 추천 책 목록 화면으로 전환
        self.stackedWidget_2.setCurrentIndex(1)

    # 페이지 이동
    def move_to_main(self):
        self.stackedWidget.setCurrentIndex(0)

    def move_to_keyword(self):
        self.stackedWidget.setCurrentIndex(1)

        # 검색 결과 초기화
        self.le_keyword_find.clear()           # 검색창에 남은 문자 제거
        for i, title in enumerate(self.keyword_titles):     # 검색했던 책, 이미지들 모두 안 보이게 설정
            title.setVisible(False)
            self.keyword_covers[i].setVisible(False)

    def move_to_name(self):
        self.stackedWidget.setCurrentIndex(2)
        self.stackedWidget_2.setCurrentIndex(0)     # 책 검색하는 페이지로 설정

        # 검색 결과 초기화
        self.le_bookname_find.clear()           # 검색창에 남은 문자 제거
        self.tbl_book.clearContents()           # 기존에 검색했던 책 목록 삭제
        self.tbl_book.setRowCount(0)            # 비어있는 열 삭제
        self.tbl_book.horizontalHeader().setStretchLastSection(True)    # header 조절한 부분 원상복귀
        self.lbl_book_image.setVisible(False)   # 이미지 안 보이게
        self.btn_similar.setVisible(False)      # 유사한 책 추천 버튼 안 보이게

    # 유사한 책 목록 생성
    def gen_recommendation(self, cosine_sim, book_code=None):
        # cosine 유사도가 높은 순으로 정렬
        sim_scores = pd.Series(cosine_sim[-1], index=self.df_book.index)
        sim_scores.sort_values(ascending=False, inplace=True)

        # 자기 자신을 제외하고 가장 유사한 책 추출
        rec_codes = sim_scores.index[:9]
        if book_code is not None and book_code in rec_codes:
            rec_codes = rec_codes.drop([book_code])
        else:
            rec_codes = rec_codes[:-1]

        return self.df_book.loc[rec_codes][['title', 'image_link']]

    # hyperlink 설정된 책 제목 생성 (라벨용)
    # 객체마다 다르게 동작하는 것이 아니라서 staticmethod로 설정했는데 무시하셔도 괜찮습니다.
    @staticmethod
    def gen_title(code, title):

        return f'<a style="color:black;text-decoration:none;" href="https://movie.naver.com/movie/bi/mi/basic.naver?code={code}">{title}</a>'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Recommender()
    w.show()
    sys.exit(app.exec_())
