function getRecommendations() {
    var bookID = document.getElementById("bookID").value;

    // Adicione uma classe de animação enquanto as recomendações estão sendo carregadas
    document.getElementById("recommendations").classList.add("loading");

    // Enviar solicitação para o backend (Flask)
    fetch(`/recommender?bookID=${bookID}`)
    .then(response => response.json())
    .then(data => {
        console.log("Data Received:", data);
        
        // Remova a classe de animação após o recebimento dos dados
        document.getElementById("recommendations").classList.remove("loading");

        // Atualize as informações com uma transição suave
        updateRecommendationUI(data);
    })
    .catch(error => {
        console.error('Erro na solicitação:', error);

        // Remova a classe de animação em caso de erro
        document.getElementById("recommendations").classList.remove("loading");

        document.getElementById("recommendations").innerHTML = 'Erro ao obter recomendações.';
    });
}

function updateRecommendationUI(data) {
    // Adicione lógica para exibir informações com animações ou transições
    document.getElementById("recommendations").innerHTML = `
        <p>Recommended Books:</p>
        <ul>
            ${data.recommended_books.map(book => `<li>${book.title}</li>`).join('')}
        </ul>
    `;
}
