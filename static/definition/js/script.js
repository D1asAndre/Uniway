document.addEventListener('DOMContentLoaded', function() {
    // Função para esconder as mensagens após 5 segundos
    function hideMessages() {
        var messages = document.querySelectorAll('.messages li');

        messages.forEach(function(message) {
            // Oculta cada mensagem
            setTimeout(function() {
                message.style.display = 'none';
            }, 5000);  // Tempo em milissegundos (5 segundos)
        });
    }

    // Chama a função para esconder as mensagens
    hideMessages();

    // Exemplo: Adicionar manipuladores de eventos para os botões
    const editButton = document.getElementById('editButton');
    const saveButton = document.getElementById('saveButton');

    editButton.addEventListener('click', function() {
        // Lógica para tornar os campos editáveis
        console.log('Campos agora são editáveis.');
    });

    saveButton.addEventListener('click', function() {
        // Lógica para salvar os dados através da API
        console.log('Dados salvos com sucesso.');
    });

    // Adicione mais lógica conforme necessário
});
