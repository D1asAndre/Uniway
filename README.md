Para poder dar runserver ao servidor é preciso criar um ambiente virtual e em seguido instalar o requirements.txt, encontra-se diponível 
no projeto (\djangoProject).

Se já tiver um ambiente virtual é só passar para 4º topico.

Instalar o ambiente virtual:

1º Abrir o cmd na localização do projeto e realizar o ->
pip install virtualenv;

2º No directorio do projeto executar
virtualenv venv;

3º Ativar o ambiente virtual (Linux/macOS -> source venv/bin/activate),
(Windows -> venv\Scripts\activate);

4º Instalar as dependências do projeto ->
pip install -r requirements.txt


Neste projeto para poder configurar o seu arranque é preciso realizar algumas operações:

**Abrir 3 separadores da cmd**

1º
Entrar no directorio do REDIS -> \djangoProject\Redis-x64-3.0.504

E inserir o código de arranque -> redis-server;

2º
Estar no directorio principal onde se encontra o manage.py -> \djangoProject

E inserir o seguinte código -> python run_huey.py;

3º
*(Este topico é importante para que o servidor esteja na porta correta)*
Com isto tudo realizado podemos dar runserver ao servidor, deve estar no directorio \djangoProject

->**python manage.py runserver 8035**;


O consumo desta API deve-se ao facto de poder criar pessoa da UA para dentro da nossa API, Assim poder realizar a autenticação
com a conta da Universidade de Aveiro.


API:
Exitem alguns endpoint especificos neste projeto para poder aceder a API
É preciso fazer login na conta admin:
username: UniWay
password: Projeto.Psi.2023

Assim temos acesso aos endpoint que consomem a API

1º http://127.0.0.1:8035/api/criar/registo/

2º http://127.0.0.1:8035/api/listar/registo/

3º http://127.0.0.1:8035/api/excluir/registo/<int:num_mec>/

4º http://127.0.0.1:8035/api/editar/registo/<int:num_mec>/


Depois de criar uma pessoa poderá fazer o login com a autenticação da UA
Antes de realizar a autenticação deverá realizar o logout.

Encontra-se disponível aqui -> http://127.0.0.1:8035 
