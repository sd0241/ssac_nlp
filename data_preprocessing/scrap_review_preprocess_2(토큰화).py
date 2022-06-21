import pandas as pd
import re
from konlpy.tag import Okt

df = pd.read_csv('movie_review_16.csv', index_col=0) # review 파일 로드
stopwords = pd.read_csv('stopwords_small.csv', index_col=0) # stop word 파일로드
stopwords = list(stopwords.stopword)
# temp_stopwords = ['배우', '영화', '감독', '출연', '리뷰', '보기', '연출', '개봉',
#                  '장면', '이야기', '연기', '보고', '스토리', '제목', '영화로', '촬영', '추천', '하였습니다']
# stopwords += temp_stopwords

okt = Okt() #tokenizer 로드
cleaned_sentences = []
count = 0
for sentence in df.review:
    count += 1
    if count % 100 == 0: # 100단위로 진행결과 표시
        print(count)
    sentence = re.sub('[^가-힣]', ' ', sentence) # 한글이 아닌 문자는 공백으로 표시
    token = okt.pos(sentence) # 품사 태깅
    df_token = pd.DataFrame(token, columns=['word', 'class'])
    df_cleaned_token = df_token[(df_token['class'] == 'Noun') | # 명사, 동사, 형용사로 이루어진 df 만들기
                                (df_token['class'] == 'Verb') |
                                (df_token['class'] == 'Adjective')]

    words = []
    for word in df_cleaned_token['word']:
        if len(word) > 1: # word가 한개 2개 이상
            if word not in stopwords: # stop words에 없는 단어 추가
                words.append(word)
    cleaned_sentence = ' '.join(words)
    cleaned_sentences.append(cleaned_sentence)

df['cleaned_review'] = cleaned_sentences
print(df.head())
df = df[['title', 'cleaned_review']]
# 영화별 리뷰를 한 문장으로 된 df 로 지정
one_sentences = []
for title in df['title'].unique():
    temp = df[df['title']==title]['cleaned_review']
    if len(temp) > 100: # review 개수가 100이 넘으면 100으로 지정
        temp = temp[:100]
    one_sentence = ' '.join(list(temp))
    one_sentences.append(one_sentence)
df_one_sentences = pd.DataFrame({'title':df['title'].unique(),'review':one_sentences})
print(df_one_sentences.head())
df_one_sentences.to_csv('./crawling/cleaned_movie_review_16.csv') # 최종 movie_review 데이터 저장




