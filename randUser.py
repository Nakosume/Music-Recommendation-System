import pandas as pd
import random

# Cargar el dataset de canciones para obtener los nombres de las canciones disponibles
dataset_path = './dataset.csv'
songs_data = pd.read_csv(dataset_path)

# Obtener los géneros y nombres únicos de las canciones del dataset
unique_genres = songs_data['track_genre'].dropna().unique()
unique_tracks = songs_data['track_name'].dropna().unique()

# Generar datos para 50 usuarios con tracks limitados al dataset
users_data = {
    "user_id": [f"user_{i}" for i in range(1, 51)],
    "preferred_genres": [",".join(random.sample(list(unique_genres), k=2)) for _ in range(50)],  # 2 géneros favoritos por usuario
    "favorite_tracks": [",".join(random.sample(list(unique_tracks), k=1)) for _ in range(50)]  # 1 track favorito por usuario
}

# Crear DataFrame y guardar como CSV
users_df = pd.DataFrame(users_data)
users_csv_path = './static/users.csv'
users_df.to_csv(users_csv_path, index=False)

users_csv_path
