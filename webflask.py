from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from recommender import hybrid_recommendation, collaborative_model, tfidf_vectorizer, item_similarities, df_books

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommender', methods=['GET'])
def recommend():
    # Verificar se 'item_id' é fornecido
    item_id = request.args.get('bookID')
    
    if not item_id:
        return jsonify({'error': 'Parâmetro ausente. Forneça item_id ou bookID.'})

    try:
        collaborative_prediction, content_based_prediction, hybrid_prediction, recommended_books = hybrid_recommendation(item_id)
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar recomendações: {str(e)}'})

    # Converter int64 para int em cada dicionário de recommended_books
    recommended_books_serializable = [
        {'bookID': int(book['bookID']), 'title': str(book['title'])} 
        for book in recommended_books
    ]

    response_data = {
        'collaborative_prediction': collaborative_prediction,
        'content_based_prediction': content_based_prediction,
        'hybrid_prediction': hybrid_prediction,
        'recommended_books': recommended_books_serializable
    }

    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True)
