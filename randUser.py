import pandas as pd
import random

# Géneros musicales y tracks para generar datos aleatorios
genres = ["pop", "rock", "classical", "jazz", "hiphop", "rap", "electronic", "country", "blues", "reggae"]
tracks = [f"track_{i}" for i in range(1, 101)]  # 100 canciones simuladas

# Generar datos para 50 usuarios
users_data = {
    "user_id": [f"user_{i}" for i in range(1, 51)],  # IDs de usuarios del 1 al 50
    "preferred_genres": [",".join(random.sample(genres, k=2)) for _ in range(50)],  # 2 géneros favoritos por usuario
    "favorite_tracks": [",".join(random.sample(tracks, k=2)) for _ in range(50)]  # 2 tracks favoritos por usuario
}

# Crear DataFrame
users_df = pd.DataFrame(users_data)

# Guardar como archivo CSV
users_df.to_csv("users.csv", index=False)  # Guarda el archivo como 'users.csv' en el directorio actual

print("Archivo 'users.csv' generado con éxito.")