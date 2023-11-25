function getRecommendations() {
    var bookID = document.getElementById("bookID").value;

    document.getElementById("recommendations").classList.add("loading");

    fetch(`/recommender?bookID=${bookID}`)
    .then(response => response.json())
    .then(data => {
        console.log("Data Received:", data);
        document.getElementById("recommendations").classList.remove("loading");
        updateRecommendationUI(data);
    })
    .catch(error => {
        console.error('Erro na solicitação:', error);
        document.getElementById("recommendations").classList.remove("loading");
        document.getElementById("recommendations").innerHTML = 'Erro ao obter recomendações.';
    });
}

function updateRecommendationUI(data) {
    document.getElementById("recommendations").innerHTML = `
        <p>Recommended Books:</p>
        <ul>
            ${data.recommended_books.map(book => `<li>${book.title}</li>`).join('')}
        </ul>
    `;
}
