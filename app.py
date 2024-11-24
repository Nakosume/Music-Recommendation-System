import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Cargar datos
songs_data = pd.read_csv('dataset.csv')
users_data = pd.read_csv('./static/users.csv')

def recommend_songs_and_more(user_row, song_data, user_data, method="average"):
    try:
        # Asegurarse de que las columnas son listas y no cadenas
        preferred_genres = user_row["preferred_genres"].split(',') if isinstance(user_row["preferred_genres"], str) else user_row["preferred_genres"]

        # Filtrar canciones que coincidan con los géneros preferidos
        filtered_songs = song_data[
            (song_data["track_genre"].isin(preferred_genres))
        ].copy()

        # Métodos de agregación
        if method == "average":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].mean(axis=1)
        elif method == "minimum_misery":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].min(axis=1)
        elif method == "maximum_pleasure":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].max(axis=1)

        # Top 10 canciones
        top_songs = filtered_songs.sort_values(by="score", ascending=False).head(10)

        # Top 5 álbumes y artistas
        top_albums = top_songs["album_name"].value_counts().head(5).index.tolist()
        top_artists = top_songs["artists"].value_counts().head(5).index.tolist()

        # Top 3 usuarios similares
        user_genres = set(preferred_genres)
        user_similarity = []

        for _, other_user in user_data.iterrows():
            if other_user["user_id"] == user_row["user_id"]:
                continue
            other_genres = set(other_user["preferred_genres"].split(','))
            genre_similarity = len(user_genres & other_genres)
            user_similarity.append((other_user["user_id"], genre_similarity))

        top_users = [u[0] for u in sorted(user_similarity, key=lambda x: x[1], reverse=True)[:3]]

        return {
            "songs": top_songs[["track_name", "artists", "album_name", "track_genre", "popularity"]].to_dict(orient="records"),
            "albums": top_albums,
            "artists": top_artists,
            "similar_users": top_users
        }

    except Exception as e:
        print(f"Error en recommend_songs_and_more: {e}")
        raise



@app.route('/')
def home():
    return render_template('index.html')

# Endpoint para obtener usuarios
@app.route('/users', methods=['GET'])
def get_users():
    # Cargar usuarios desde el CSV
    users_df = pd.read_csv("users.csv")
    # Convertir a lista de diccionarios
    users = users_df[["user_id"]].to_dict(orient="records")
    return jsonify(users)

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id')
    method = request.args.get('method', 'average')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        # Verificar si el usuario existe
        user_row = users_data[users_data['user_id'] == user_id]
        if user_row.empty:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user_row = user_row.iloc[0]
        recommendations = recommend_songs_and_more(user_row, songs_data, users_data, method=method)

        return jsonify(recommendations)
    except Exception as e:
        print(f"Error en /recommend: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)