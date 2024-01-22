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
});