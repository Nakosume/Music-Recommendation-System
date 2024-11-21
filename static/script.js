// Obtener referencias a los elementos
const userSelect = document.getElementById("user-select");
const recommendationSection = document.getElementById("recommendation-section");
const recommendationList = document.getElementById("recommendation-list");
const getRecommendationsButton = document.getElementById("get-recommendations");

// Cargar usuarios en el selector al cargar la página
window.onload = async () => {
  const users = await fetch("/static/users.csv")
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
};

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


// Manejar clic en el botón para obtener recomendaciones
getRecommendationsButton.addEventListener("click", async () => {
  const userId = userSelect.value;
  const method = document.getElementById("method-select").value;

  if (!userId) {
    alert("Please select a user!");
    return;
  }

  const recommendations = await fetch(`/recommend?user_id=${userId}&method=${method}`)
    .then((response) => response.json())
    .catch((error) => {
      console.error("Error fetching recommendations:", error);
      return null;
    });

  if (recommendations.error) {
    alert(recommendations.error);
    return;
  }

  // Mostrar Top 10 canciones
  const songList = document.getElementById("top-songs");
  songList.innerHTML = recommendations.songs
    .map(song => `<li>${song.track_name} by ${song.artists} (Album: ${song.album_name}, Genre: ${song.track_genre})</li>`)
    .join("");

  // Mostrar Top 5 álbumes
  const albumList = document.getElementById("top-albums");
  albumList.innerHTML = recommendations.albums.map(album => `<li>${album}</li>`).join("");

  // Mostrar Top 5 artistas
  const artistList = document.getElementById("top-artists");
  artistList.innerHTML = recommendations.artists.map(artist => `<li>${artist}</li>`).join("");

  // Mostrar Top 3 usuarios similares
  const userList = document.getElementById("similar-users");
  userList.innerHTML = recommendations.similar_users.map(user => `<li>${user}</li>`).join("");
});
