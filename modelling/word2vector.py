import pandas as pd
from gensim.models import Word2Vec

# 파일 불러오기
review_words = pd.read_csv(
    './movie_data_final.csv.csv',
    index_col=0)

clean_token_review = list(review_words['review'])
print(clean_token_review[0])
cleaned_tokens = []

# 토큰별로 변환
for sentence in clean_token_review:
    token = sentence.split(' ')
    cleaned_tokens.append(token)
print(cleaned_tokens[0])

# 모델링 및 파라미터 조정
embedding_model = Word2Vec(cleaned_tokens, vector_size=350,  # 벡터 사이즈 -> 차원 수
                          window=4, min_count=20,ns_exponent=0.75  
                           # ns_exponent -> 1.0 빈도에 정확히 비례하여 표본 추출,
                           # 0.0 값은 모든 단어를 동일하게 표본 추출하며 
                           # 음수 값은 고빈도 단어보다 저빈도 단어를 표본 추출
                          workers=-1,sg=1)
# embedding_model.save('./word2VecModel_final.model')
print(len(embedding_model))