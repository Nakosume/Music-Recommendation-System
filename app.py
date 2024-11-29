import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Cargar datos
songs_data = pd.read_csv('dataset.csv')
users_data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vR0uI5CdJu2KAfL5FUqTmr_eFrtmyavT2uCCZUMOFDAIH7zuAf2LwRLwONLjSjHKZumHjLE0lvymAiQ/pub?output=csv')

""" 
EN CASO QUE EL CSV DEL DOCS NO FUNCIONES
users_data = pd.read_csv('./static/users.csv')
 """

def recommend_songs_and_more(user_row, song_data, user_data, method="average", preferred_genres=None, favorite_track=None):
    try:
        if preferred_genres is None:
            preferred_genres = user_row["preferred_genres"].split(',')

        # Filtrar canciones que coincidan con exactamente uno de los géneros preferidos
        filtered_songs = song_data[
            song_data["track_genre"].apply(
                lambda genres: any(genre in genres.split(',') for genre in preferred_genres)
            )
        ].copy()

        # Métodos de agregación (average, minimum_misery, maximum_pleasure)
        if method == "average":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].mean(axis=1)
        elif method == "minimum_misery":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].min(axis=1)
        elif method == "maximum_pleasure":
            filtered_songs["score"] = filtered_songs[["popularity", "danceability", "energy"]].max(axis=1)

        # Top 10 canciones, top 5 álbumes y artistas
        top_songs = filtered_songs.sort_values(by="score", ascending=False).head(10)
        top_albums = top_songs["album_name"].value_counts().head(5).index.tolist()
        top_artists = top_songs["artists"].value_counts().head(5).index.tolist()

        # Top 3 usuarios similares
        """user_genres = set(preferred_genres)
        user_similarity = []
        for _, other_user in user_data.iterrows():
            if other_user["user_id"] == user_row["user_id"]:
                continue
            other_genres = set(other_user["preferred_genres"].split(','))
            genre_similarity = len(user_genres & other_genres)
            user_similarity.append((other_user["user_id"], genre_similarity))

        top_users = [u[0] for u in sorted(user_similarity, key=lambda x: x[1], reverse=True)[:3]]"""

        # Top 5 Similar Songs

        features = ['danceability', 'energy', 'popularity']
        songs_features = songs_data[features].dropna()

        knn = NearestNeighbors(n_neighbors=5, metric='cosine') 
        knn.fit(songs_features)

        def get_similar_tracks(track_name):
            print("Hey Hey", track_name.title())
            t_name = track_name.title()
            track = songs_data[songs_data['track_name'] == t_name][features]
            if track.empty:
                return ["No song was found / Your song isn't in our Data Base"]
            
            distances, indices = knn.kneighbors(track)
            
            similar_track = songs_data.iloc[indices[0]]['track_name']
            similar_artist = songs_data.iloc[indices[0]]['artists']
            similar_song = ""+similar_track +" by "+ similar_artist
            similar_tracks = similar_song.tolist()
            return similar_tracks

        similar_tracks = get_similar_tracks(favorite_track[0])
        print("Tracks similares:", similar_tracks)
        top_users = similar_tracks

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
    users_df = users_data
    # Convertir a lista de diccionarios
    users = users_df[["user_id"]].to_dict(orient="records")
    print("Usuarios:", users)
    return jsonify(users)

@app.route('/user_preferences', methods=['GET'])
def user_preferences():
    try:
        user_id = request.args.get('user_id')
        user_row = users_data[users_data["user_id"] == user_id].iloc[0]
        
        # Obtener los géneros preferidos del usuario
        preferred_genres = user_row["preferred_genres"]
        
        return jsonify({"preferred_genres": preferred_genres})
    
    except Exception as e:
        print(f"Error en user_preferences: {e}")
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/recommend', methods=['GET'])
def recommend():
    try:
        user_id = request.args.get('user_id')
        selected_genre = request.args.get('genre')  
        method = request.args.get('method', 'average')  

        user_row = users_data[users_data["user_id"] == user_id].iloc[0]
        preferred_genres = user_row["preferred_genres"].split(',')
        favorite_track = user_row["favorite_track"].split(',')

        if selected_genre:
            preferred_genres = [selected_genre]

        recommendations = recommend_songs_and_more(user_row, songs_data, users_data, method, preferred_genres, favorite_track)

        return jsonify(recommendations)

    except Exception as e:
        print(f"Error en recommend: {e}")
        return jsonify({"error": "Error procesando las recomendaciones"}), 500




if __name__ == '__main__':
    app.run(debug=True)