import pandas as pd
stopwords = pd.read_csv('./stopwords_small.csv', index_col=0)

# 불용어를 리스트에 추가하고 실행
a = pd.DataFrame({'stopword':['렉스','년대','메르','일자리','여전히','동영상 첨부','만드는','모습','과정']})
stopwords = pd.concat([stopwords, a],ignore_index=True)
stopwords = stopwords.drop_duplicates()
print(stopwords.duplicated().sum())
stopwords.to_csv('./stopwords_small.csv')