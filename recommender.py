import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import scipy

# Carregar o DataFrame do arquivo de livros
file_path = 'books.csv'
df_books = pd.read_csv(file_path)

# Padronizar os títulos
df_books['title'] = df_books['title'].str.strip().str.lower()

# Criação da matriz de utilidade
matrix_utility = df_books.pivot_table(index='bookID', values='average_rating')

reader = Reader(rating_scale=(0, 5))
data = Dataset.load_from_df(df_books[['bookID', 'bookID', 'average_rating']], reader)

# Dividir em conjunto de treinamento e teste
trainset, testset = train_test_split(data, test_size=0.2)

# Inicializar e treinar o modelo colaborativo
collaborative_model = SVD()
collaborative_model.fit(trainset)

# TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=6000, ngram_range=(1, 2))
tfidf_matrix_content = tfidf_vectorizer.fit_transform(df_books['title'].fillna('') + ' ' + df_books['authors'].fillna(''))

# Adicionar as novas features ao modelo baseado em conteúdo
additional_features = df_books[['language_code', 'num_pages', 'ratings_count', 'text_reviews_count']]
additional_features_text = additional_features.apply(lambda x: ' '.join(x.astype(str)), axis=1)
tfidf_matrix_additional = tfidf_vectorizer.transform(additional_features_text)

# Concatenar a matriz TF-IDF original com as novas features
tfidf_matrix = scipy.sparse.hstack([tfidf_matrix_content, tfidf_matrix_additional])

# Função para obter recomendações baseadas em conteúdo
def content_based_recommendation(bookID, item_similarities):

    item_row = df_books[df_books['bookID'].astype(str) == bookID]

    if not item_row.empty:
        item_idx = item_row.index[0]

        if 0 <= item_idx < len(item_similarities) and item_similarities[item_idx].any():
            similar_items = item_similarities[item_idx].argsort()[::-1][1:6]
            return similar_items

    return []

# Função para obter títulos dos livros recomendados
def get_titles_from_content_based_predictions(content_based_predictions):
    recommended_books = []
    for item_idx in content_based_predictions:
        title = df_books.loc[item_idx, 'title'].strip()
        recommended_books.append({'bookID': item_idx, 'title': title})

    return recommended_books

item_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

# Função hybrida de recomendação
def hybrid_recommendation(bookID):
    user_id = '1'  
    collaborative_prediction = collaborative_model.predict(user_id, bookID).est
    content_based_predictions = content_based_recommendation(bookID, item_similarities)
    recommended_books = get_titles_from_content_based_predictions(content_based_predictions)

    # Calcular a média ponderada das predições de conteúdo e colaborativo
    if any(content_based_predictions):
        content_based_df = df_books[df_books['bookID'].isin(content_based_predictions)]
        if not content_based_df.empty and bookID in content_based_df['bookID']:
            content_based_prediction = content_based_df.set_index('bookID').loc[bookID, 'average_rating']
        else:
            content_based_prediction = 0
    else:
        content_based_prediction = 0
    
    # Combinar por votação simples
    hybrid_prediction = (collaborative_prediction * 0.8 + content_based_prediction * 0.2)
    return collaborative_prediction, content_based_prediction, hybrid_prediction, recommended_books

# Calcular as previsões do modelo híbrido
predictions = [hybrid_recommendation(str(row[1])) for row in testset]
predictions_surprise = [(str('1'), str(row[1]), row[2], row[2], {}) for row in predictions]

# Avaliar o desempenho do modelo híbrido
hybrid_rmse = accuracy.rmse(predictions_surprise)

# Avaliar desempenho do modelo colaborativo
collaborative_predictions = collaborative_model.test(testset)
collaborative_rmse = accuracy.rmse(collaborative_predictions)

