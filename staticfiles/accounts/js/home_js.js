document.addEventListener('DOMContentLoaded', function () {
    // Ocultar o campo de código de ativação por padrão
    const activationCodeField = document.getElementById('id_activation_code');
    activationCodeField.style.display = 'none';

    // Adicione um ouvinte ao campo de email para mostrar o campo de código de ativação
    const emailField = document.getElementById('id_email');
    emailField.addEventListener('blur', function () {
        if (emailField.value) {
            activationCodeField.style.display = 'block';
        } else {
            activationCodeField.style.display = 'none';
        }
    });
});
