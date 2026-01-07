async function update() {
  try {
    const res = await fetch("http://127.0.0.1:8000/track");
    const t = await res.json();
    if (!t.title) return;

    document.querySelector("#wrap img").src = t.cover;
    document.querySelector(".artists").textContent = t.artists.join(", ");
    document.querySelector(".title").textContent = t.title;
  } catch (e) {
    console.error("Ошибка обновления трека:", e);
  }
}

update(); // обновляем сразу при загрузке
setInterval(update, 1000);
