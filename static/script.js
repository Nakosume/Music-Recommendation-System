// Obtener referencias a los elementos
const userSelect = document.getElementById("user-select");
const recommendationSection = document.getElementById("recommendation-section");
const recommendationList = document.getElementById("recommendation-list");
const getRecommendationsButton = document.getElementById("get-recommendations");

// Cargar usuarios en el selector al cargar la página
//No es necesario
/* window.onload = async () => {

  const users = await fetch("./static/users.csv")
    .then((response) => response.text())
    .then((text) => {
      const rows = text.split("\n").slice(1); // Omitir la cabecera
      return rows.map((row) => row.split(",")[0]); // Obtener user_id
    });

  // Agregar usuarios al selector
  users.forEach((userId) => {
    const option = document.createElement("option");
    option.value = userId;
    option.textContent = userId;
    userSelect.appendChild(option);
  });
}; */

// Función para llenar el selector de géneros con los géneros preferidos del usuario
async function populateGenreSelect(userId) {
  try {
      // Hacer una solicitud al backend para obtener los géneros preferidos
      const response = await fetch(`/user_preferences?user_id=${userId}`);
      
      if (!response.ok) {
          throw new Error('No se pudo obtener los géneros preferidos');
      }

      const data = await response.json();

      // Obtener el selector de géneros
      const genreSelect = document.getElementById('genre-select');
      
      // Limpiar las opciones previas
      genreSelect.innerHTML = '<option value="">Todos los géneros</option>';

      // Obtener los géneros preferidos y agregarlos como opciones al select
      const preferredGenres = data.preferred_genres.split(','); // Asumimos que la respuesta es algo como 'rock,pop'

      preferredGenres.forEach(genre => {
          const option = document.createElement('option');
          option.value = genre.trim(); // Eliminar espacios extra
          option.textContent = genre.trim();
          genreSelect.appendChild(option);
      });
  } catch (error) {
      console.error("Error al obtener los géneros preferidos:", error);
  }
}

// Llamar a la función cuando la página cargue o cuando el usuario sea seleccionado
populateGenreSelect('user_1');  // Asegúrate de usar el user_id correcto


document.addEventListener("DOMContentLoaded", async () => {
  const userSelect = document.getElementById("user-select");

  // Obtener usuarios del backend
  const users = await fetch("/users")
    .then(response => response.json())
    .catch(error => {
      console.error("Error al cargar usuarios:", error);
      return [];
    });

  // Llenar el select con las opciones
  if (users.length > 0) {
    users.forEach(user => {
      const option = document.createElement("option");
      option.value = user.user_id;
      option.textContent = user.user_id;
      userSelect.appendChild(option);
    });
  } else {
    const option = document.createElement("option");
    option.textContent = "No users found";
    userSelect.appendChild(option);
  }
});

// Función para llenar el selector con géneros preferidos del usuario
async function populateGenreSelect(userId) {
  const response = await fetch(`/user_preferences?user_id=${userId}`);
  const data = await response.json();
  const genreSelect = document.getElementById('genre-select');

  // Asegurarse de que el campo esté vacío antes de llenarlo
  genreSelect.innerHTML = '<option value="">Todos los géneros</option>';

  // Agregar los géneros preferidos como opciones en el select
  const preferredGenres = data.preferred_genres.split(',');  // Suponiendo que los géneros están en formato 'rock,pop'
  preferredGenres.forEach(genre => {
      const option = document.createElement('option');
      option.value = genre.trim();
      option.textContent = genre.trim();
      genreSelect.appendChild(option);
  });
}

userSelect.addEventListener("change", () => {
  const userId = userSelect.value;
  if (userId) {
    populateGenreSelect(userId);
  }
});

// Manejar clic en el botón para obtener recomendaciones
getRecommendationsButton.addEventListener("click", async () => {
  const userId = userSelect.value;
  const method = document.getElementById("method-select").value;
  const genre = document.getElementById("genre-select").value; // Obtener el género seleccionado

  if (!userId) {
    alert("Por favor, selecciona un usuario.");
    return;
  }

  try {
    const url = `/recommend?user_id=${userId}&method=${method}${genre ? `&genre=${genre}` : ""}`;
    const recommendations = await fetch(url).then((response) => response.json());

    if (recommendations.error) {
      alert(recommendations.error);
      return;
    }

    // Mostrar las recomendaciones en la interfaz
    const songList = document.getElementById("top-songs");
    songList.innerHTML = recommendations.songs
      .map(song => `<li>${song.track_name} by ${song.artists} (Album: ${song.album_name}, Genre: ${song.track_genre})</li>`)
      .join("");

    const albumList = document.getElementById("top-albums");
    albumList.innerHTML = recommendations.albums.map(album => `<li>${album}</li>`).join("");

    const artistList = document.getElementById("top-artists");
    artistList.innerHTML = recommendations.artists.map(artist => `<li>${artist}</li>`).join("");

    const userList = document.getElementById("similar-users");
    userList.innerHTML = recommendations.similar_users.map(user => `<li>${user}</li>`).join("");
  } catch (error) {
    console.error("Error obteniendo recomendaciones:", error);
    alert("Hubo un error al procesar las recomendaciones.");
  }
});

