from django.shortcuts import render

# Create your views here.

def home(request):

    return render(request, 'home.html')



def recommend(request):

    import pandas as pd
    import numpy as np
    import sys
    import pickle
    from scipy.io import mmwrite, mmread
    

    sys.stdout.flush()
    movie_data = pd.read_csv("./data/movie_data_final3.csv",index_col=0)
    movie_data.drop_duplicates(subset=['title'],keep='first',inplace=True)
    # movies_data = movies_data.iloc[:6000]
    movie_data.columns = ['movie_id','title','year','star','movie_rating','genre','director','actors','summary','review','nmf_topic','lda_topic','image_link','wnfrjfl']
    movie_data['director'] = movie_data['director'].replace(np.nan, " ")
    movie_data['actors'] = movie_data['actors'].replace(np.nan, " ")
    movie_data['genre'] = movie_data['genre'].replace(np.nan, " ")
    movie_data['movie_rating'] = movie_data['movie_rating'].replace(np.nan, " ")
    movie_data['summary'] = movie_data['summary'].replace(np.nan, " ")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    from gensim.models import Word2Vec



    def recommendation(embedding_model,key_word,movie_data,Tfidf,Tfidf_matrix):
        sentence = [key_word] * 10
        if key_word in embedding_model.wv.index_to_key:
            sim_word = embedding_model.wv.most_similar(key_word, topn=10)
            # print(sim_word)
            labels = []
            for label, _ in sim_word:
                labels.append(label)
            print(labels)
            for i, word in enumerate(labels):
                sentence += [word] * (9 - i)
        sentence = ' '.join(map(str,sentence))
        # print(sentence)
        sentence_vec = Tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec,
                                   Tfidf_matrix)
        simScores = list(enumerate(cosine_sim[-1]))
        simScores = sorted(simScores, key=lambda x: x[1],
                           reverse=True)
        simScores = simScores[0:15]
        movieidx = [i[0] for i in simScores]
        RecMovielist = movie_data.iloc[movieidx].sort_values(by='star',ascending=False).reset_index(drop=True)

        return RecMovielist

    # def find_similar_moive(movies_data, new_user_input):
    #     movie_index_list = []
        
    #     for categorie, value in new_user_input.items():
    #         movie_index = movies_data[movies_data[str(categorie)]==value].index.values
    #         movie_index_list.append(movie_index)
        
    #     return movie_index


    # def find_info(movie_data, key_word, value):
    #     lengh = movie_data[key_word].shape[0]
        
    #     find_lst = []
    #     if key_word == 'title':
    #         return movie_data['title']==value
    #     else:
    #         for i in range(lengh):
    #             if value in movie_data[key_word][i].split():
    #                 find_lst.append(True)
    #             else:
    #                 find_lst.append(False)
    #         return find_lst


    # def getRecommendation(movie_data, cosine_sim):
    #     simScores = list(enumerate(cosine_sim[-1]))
    #     simScores = sorted(simScores, key=lambda x: x[1],
    #                     reverse=True)
    #     simScores = simScores[0:10]
    #     movieidx = [i[0] for i in simScores]
    #     RecMovielist = movie_data.iloc[movieidx].reset_index(drop=True)
    #     # fig = plt.figure(figsize=(20, 20))
    #     # for index, row in RecMovielist.iterrows():
    #     #     response = requests.get(row['image_link'])
    #     #     img = Image.open(BytesIO(response.content))
    #     #     fig.add_subplot(2, 5, index + 1)
    #     #     plt.imshow(img)
    #     #     plt.title(row['title'])
    #     return RecMovielist
    
    key_word = request.POST['data']
    # key_word2 = request.POST['data2']

    key_word = key_word.split()
    # key_word2 = key_word2.split()
    # new_user_input = {key:value for (key, value) in zip(key_word, key_word2) }
    print("검색중.....")
    with open("./models/Word2vec_final.pickle", "rb") as fr:
        embedding_model = pickle.load(fr)
    with open("./models/tfidf_okt.pickle", "rb") as fr:
        Tfidf = pickle.load(fr)
    Tfidf_matrix = mmread('./models/tfidf_movie_okt.mtx')
    data = recommendation(embedding_model,key_word,movie_data,Tfidf,Tfidf_matrix)


    # new_user_input = {key:value for (key, value)in zip(key_word, key_word2) }

    context ={
        'data': data,
        'link' : 'https://movie.naver.com/movie/bi/mi/basic.nhn?code='
    }

    return render(request, 'recommend.html', context)


def nmf_recommend(request):
    import pandas as pd
    import numpy as np
    import sys
    import pickle
    from scipy.io import mmread
    from scipy.stats import mode

    sys.stdout.flush()
    movie_data = pd.read_csv("./data/movie_data_final3.csv", index_col=0)
    movie_data.drop_duplicates(subset=['title'],keep='first',inplace=True)
    # movies_data = movies_data.iloc[:6000]
    movie_data.columns = ['movie_id', 'title', 'year', 'star', 'movie_rating', 'genre', 'director', 'actors', 'summary',
                          'review', 'nmf_topic', 'lda_topic', 'image_link', 'wnfrjfl']
    movie_data['director'] = movie_data['director'].replace(np.nan, " ")
    movie_data['actors'] = movie_data['actors'].replace(np.nan, " ")
    movie_data['genre'] = movie_data['genre'].replace(np.nan, " ")
    movie_data['movie_rating'] = movie_data['movie_rating'].replace(np.nan, " ")
    movie_data['summary'] = movie_data['summary'].replace(np.nan, " ")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    from gensim.models import Word2Vec

    def recommendation(embedding_model, key_word, movie_data, Tfidf, Tfidf_matrix):
        sentence = [key_word] * 10
        if key_word in embedding_model.wv.index_to_key:
            sim_word = embedding_model.wv.most_similar(key_word, topn=10)
            # print(sim_word)
            labels = []
            for label, _ in sim_word:
                labels.append(label)
            print(labels)
            for i, word in enumerate(labels):
                sentence += [word] * (9 - i)
        sentence = ' '.join(map(str, sentence))
        # print(sentence)
        sentence_vec = Tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec,
                                   Tfidf_matrix)
        simScores = list(enumerate(cosine_sim[-1]))
        simScores = sorted(simScores, key=lambda x: x[1],
                           reverse=True)
        simScores = simScores[1:50]
        movieidx = [i[0] for i in simScores]
        RecMovielist = movie_data.iloc[movieidx].reset_index(drop=True)
        w = list(range(10, 0, -1))
        tp = list(RecMovielist['nmf_topic'])
        for i in range(len(w)):
            tp += ([tp[i]] * w[i])

        topic_mode = mode(tp)[0]
        res = []
        for i in movieidx:
            if movie_data['nmf_topic'].loc[i] == topic_mode[0]:
                res.append(i)
                if len(res) == 15:
                    break
        RecMovielist = movie_data.iloc[res].sort_values(by='star',ascending=False).reset_index(drop=True)
        #     fig = plt.figure(figsize=(20,20))
        #     for index, row in RecMovielist.iterrows():
        #         response = requests.get(row['image_link'])
        #         img = Image.open(BytesIO(response.content))
        #         fig.add_subplot(2, 5, index+1)
        #         plt.imshow(img)
        #         plt.title(row['title'])
        return RecMovielist

    # def find_similar_moive(movies_data, new_user_input):
    #     movie_index_list = []

    #     for categorie, value in new_user_input.items():
    #         movie_index = movies_data[movies_data[str(categorie)]==value].index.values
    #         movie_index_list.append(movie_index)

    #     return movie_index

    # def find_info(movie_data, key_word, value):
    #     lengh = movie_data[key_word].shape[0]

    #     find_lst = []
    #     if key_word == 'title':
    #         return movie_data['title']==value
    #     else:
    #         for i in range(lengh):
    #             if value in movie_data[key_word][i].split():
    #                 find_lst.append(True)
    #             else:
    #                 find_lst.append(False)
    #         return find_lst

    # def getRecommendation(movie_data, cosine_sim):
    #     simScores = list(enumerate(cosine_sim[-1]))
    #     simScores = sorted(simScores, key=lambda x: x[1],
    #                     reverse=True)
    #     simScores = simScores[0:10]
    #     movieidx = [i[0] for i in simScores]
    #     RecMovielist = movie_data.iloc[movieidx].reset_index(drop=True)
    #     # fig = plt.figure(figsize=(20, 20))
    #     # for index, row in RecMovielist.iterrows():
    #     #     response = requests.get(row['image_link'])
    #     #     img = Image.open(BytesIO(response.content))
    #     #     fig.add_subplot(2, 5, index + 1)
    #     #     plt.imshow(img)
    #     #     plt.title(row['title'])
    #     return RecMovielist

    # key_word = request.POST['data']
    key_word2 = request.POST['data2']

    # key_word = key_word.split()
    key_word2 = key_word2.split()
    # new_user_input = {key: value for (key, value) in zip(key_word, key_word2)}
    print("검색중.....")
    with open("./models/Word2vec_final.pickle", "rb") as fr:
        embedding_model = pickle.load(fr)
    with open("./models/tfidf_okt.pickle", "rb") as fr:
        Tfidf = pickle.load(fr)
    Tfidf_matrix = mmread('./models/tfidf_movie_okt.mtx')
    data2 = recommendation(embedding_model, key_word2, movie_data, Tfidf, Tfidf_matrix)

    # new_user_input = {key:value for (key, value)in zip(key_word, key_word2) }

    context2 = {
        'data2': data2,
        'link': 'https://movie.naver.com/movie/bi/mi/basic.nhn?code='
    }

    return render(request, 'nmf_recommend.html', context2)


def lda_recommend(request):
    import pandas as pd
    import numpy as np
    import sys
    import pickle
    from scipy.io import mmread
    from scipy.stats import mode

    sys.stdout.flush()
    movie_data = pd.read_csv("./data/movie_data_final3.csv", index_col=0)
    movie_data.drop_duplicates(subset=['title'],keep='first',inplace=True)
    # movies_data = movies_data.iloc[:6000]
    movie_data.columns = ['movie_id', 'title', 'year', 'star', 'movie_rating', 'genre', 'director', 'actors', 'summary',
                          'review', 'nmf_topic', 'lda_topic', 'image_link', 'wnfrjfl']
    movie_data['director'] = movie_data['director'].replace(np.nan, " ")
    movie_data['actors'] = movie_data['actors'].replace(np.nan, " ")
    movie_data['genre'] = movie_data['genre'].replace(np.nan, " ")
    movie_data['movie_rating'] = movie_data['movie_rating'].replace(np.nan, " ")
    movie_data['summary'] = movie_data['summary'].replace(np.nan, " ")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    from gensim.models import Word2Vec

    def recommendation(embedding_model, key_word, movie_data, Tfidf, Tfidf_matrix):
        sentence = [key_word] * 10
        if key_word in embedding_model.wv.index_to_key:
            sim_word = embedding_model.wv.most_similar(key_word, topn=10)
            # print(sim_word)
            labels = []
            for label, _ in sim_word:
                labels.append(label)
            print(labels)
            for i, word in enumerate(labels):
                sentence += [word] * (9 - i)
        sentence = ' '.join(map(str, sentence))
        # print(sentence)
        sentence_vec = Tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec,
                                   Tfidf_matrix)
        simScores = list(enumerate(cosine_sim[-1]))
        simScores = sorted(simScores, key=lambda x: x[1],
                           reverse=True)
        simScores = simScores[1:50]
        movieidx = [i[0] for i in simScores]
        RecMovielist = movie_data.iloc[movieidx].reset_index(drop=True)
        topic_mode = mode(RecMovielist['lda_topic'])[0]
        w = list(range(10, 0, -1))
        tp = list(RecMovielist['lda_topic'])
        for i in range(len(w)):
            tp += ([tp[i]] * w[i])

        topic_mode = mode(tp)[0]
        res = []
        for i in movieidx:
            if movie_data['lda_topic'].loc[i] == topic_mode[0]:
                res.append(i)
                if len(res) == 15:
                    break
        RecMovielist = movie_data.iloc[res].sort_values(by='star',ascending=False).reset_index(drop=True)
        #     fig = plt.figure(figsize=(20,20))
        #     for index, row in RecMovielist.iterrows():
        #         response = requests.get(row['image_link'])
        #         img = Image.open(BytesIO(response.content))
        #         fig.add_subplot(2, 5, index+1)
        #         plt.imshow(img)
        #         plt.title(row['title'])
        return RecMovielist

    # def find_similar_moive(movies_data, new_user_input):
    #     movie_index_list = []

    #     for categorie, value in new_user_input.items():
    #         movie_index = movies_data[movies_data[str(categorie)]==value].index.values
    #         movie_index_list.append(movie_index)

    #     return movie_index

    # def find_info(movie_data, key_word, value):
    #     lengh = movie_data[key_word].shape[0]

    #     find_lst = []
    #     if key_word == 'title':
    #         return movie_data['title']==value
    #     else:
    #         for i in range(lengh):
    #             if value in movie_data[key_word][i].split():
    #                 find_lst.append(True)
    #             else:
    #                 find_lst.append(False)
    #         return find_lst

    # def getRecommendation(movie_data, cosine_sim):
    #     simScores = list(enumerate(cosine_sim[-1]))
    #     simScores = sorted(simScores, key=lambda x: x[1],
    #                     reverse=True)
    #     simScores = simScores[0:10]
    #     movieidx = [i[0] for i in simScores]
    #     RecMovielist = movie_data.iloc[movieidx].reset_index(drop=True)
    #     # fig = plt.figure(figsize=(20, 20))
    #     # for index, row in RecMovielist.iterrows():
    #     #     response = requests.get(row['image_link'])
    #     #     img = Image.open(BytesIO(response.content))
    #     #     fig.add_subplot(2, 5, index + 1)
    #     #     plt.imshow(img)
    #     #     plt.title(row['title'])
    #     return RecMovielist

    # key_word = request.POST['data']
    key_word3 = request.POST['data3']

    # key_word = key_word.split()
    key_word3 = key_word3.split()
    # new_user_input = {key: value for (key, value) in zip(key_word, key_word2)}
    print("검색중.....")
    with open("./models/Word2vec_final.pickle", "rb") as fr:
        embedding_model = pickle.load(fr)
    with open("./models/tfidf_okt.pickle", "rb") as fr:
        Tfidf = pickle.load(fr)
    Tfidf_matrix = mmread('./models/tfidf_movie_okt.mtx')
    data3 = recommendation(embedding_model, key_word3, movie_data, Tfidf, Tfidf_matrix)

    # new_user_input = {key:value for (key, value)in zip(key_word, key_word2) }

    context3 = {
        'data3': data3,
        'link': 'https://movie.naver.com/movie/bi/mi/basic.nhn?code='
    }

    return render(request, 'lda_recommend.html', context3)