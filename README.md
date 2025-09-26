# Lacrei Saúde API
API em Django REST para gerenciamento de profissionais de saúde e agendamento de consultas.

### Deploy na AWS

**Ambiente de produção**: [http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/](http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/)  

**Ambiente de Staging**: [http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/](http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/)  

O ambiente de Staging está populado com alguns dados para teste do funcionamento da API. O ambiente de produção está com a database vazia.

Credenciais de acesso (login via interface) para o ambiente de staging:
- Usuário: teste@email.com
- Senha: 1234pass

Autenticação via API (Postman, Insomnia, etc.) para o ambiente de staging:
Utilizar o token do usuário no header da requisição:
`Authentication: Token eac9e4a5e904426d8097163e52b24f7869acdd40`

## Set Up
### Pré Requisitos
- postgres
- Python 3.13+
- [Poetry](https://python-poetry.org/docs/) (v2.2)
- Docker (opcional, para rodar via container)

### Setup local (sem Docker)

Clone o repositório:
```bash
git clone https://github.com/juliavillela/lacrei-saude.git 
cd lacrei-saude
```

Instale as dependências e ative o ambiente virtual:
```bash
poetry install --no-root
poetry env activate
```
Criar arquivo `.env`. Este projeto utiliza variáveis de ambiente para separar configurações sensíveis (secret key, banco de dados, etc.) do código. Essas variáveis devem ficar em um arquivo `.env` na raiz do projeto. 
Exemplo de conteúdo do arquivo:
```
DJANGO_ENV = development
SECRET_KEY = fakesecretkeyq-q8lxd-ys4-@l&yw-8d39vv-qrd5kqag!%5g
POSTGRES_DB=lacrei_saude_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
ALLOWED_HOSTS=127.0.0.1,0.0.0.0,localhost
```

Iniciar o postgres
```bash
brew services start postgresql
```

Criar base de dados com o mesmo nome descrito no `.env` em `POSTGRESS_DB`
```bash
createdb lacrei_saude_db
```

Execute as migrações:
```bash
poetry run python manage.py migrate
```

Opcional: Crie um superuser (admin):
```bash
poetry run python manage.py createsuperuser
```

Rode o servidor local:
```bash
poetry run python manage.py runserver
```
A API estará disponível em [http://localhost:8000](http://localhost:8000). Atenção, a página de entrada é vazia, vá para `/api` para ver a API.

### Setup via Docker

Clone o repositório:
```bash
git clone https://github.com/juliavillela/lacrei-saude.git 
cd lacrei-saude
```

Build da imagem:
```bash
docker compose build
```

Suba o container:
```bash
docker compose up
```
A API estará disponível em [http://0.0.0.0:8000/](http://0.0.0.0:8000/). Atenção, a página de entrada é vazia, vá para `/api` para ver a API.

### Execução dos Testes

Localmente (sem Docker):
```bash
poetry run python manage.py test
```

```bash
docker exec -it <container_id> python manage.py test
```

##  Fluxo de Deploy (CI/CD)

O processo de deploy é gerenciado por **GitHub Actions** com integração ao **AWS Elastic Beanstalk**:

- **Branches**:
    - `main`: ambiente de desenvolvimento. Commits nessa branch rodam **apenas testes e lint**, sem deploy.
    - `staging`: Ao commitar nesta branch, o GitHub Actions executa **lint + testes** e realiza o **deploy automático** no ambiente de **staging** na AWS.
    - `production`: Ao commitar nesta branch, o GitHub Actions executa **lint + testes** e realiza o **deploy automático** no ambiente de **produção** na AWS. 

- **Pipeline**:
    1. Rodar testes (Black, isort, Flake8 e Django TestCase).
    2. Build da imagem Docker e push para Docker Hub.
    3. Deploy no Elastic Beanstalk (AWS) de acordo com a branch. 

## Justificativas Técnicas e Detalhes da implementação

### Usuário Customizado
Escolhi implementar um modelo customizado de usuário para autenticação via email, pois considero esse fluxo mais usual e seguro do que o padrão baseado em username.

### Profissionais de saúde `Professional`
**Atributos**:
- **Nome Social (`name`)**
- **Endereço (`Address`)**:
    - Implementado como classe abstrata com múltiplos campos (`street`, `number`, `complement`, `neighborhood`, `city`, `state`, `zipcode`). Permite validação individual de cada dado e mantém consistência no banco.
    - Serializer expõe um **campo `address` read-only**, retornando o endereço formatado como string.
- **Contato (`contact`)**:
    - Email (`email`) e telefone (`phone`) agrupados em objeto `contact` no serializer, mantendo o padrão de saída solicitado.
- **Profissão (`profession`)**:
    - Implementada com `TextChoices` para garantir consistência nos dados e facilitar a futura implementação de filtros por profissão.
**Validações e padronizações**:
    - `email`: convertido para lowercase e espaços removidos para evitar duplicidades.
    - `name`: espaços extras removidos.
    - `phone`: Limpo para conter apenas números e validado para conter até **10 ou 11 dígitos** (DDD + número fixo ou celular).
    - `zipcode`: Limpo para conter apenas números validado para conter **exatamente 8 dígitos**.
#### Endpoints

| Método     | Endpoint                   | Descrição                                    | Body / Parâmetros                                                                                                                                                                           |
| ---------- | -------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GET**    | `/api/professionals/`      | Lista todos os profissionais da saúde        | -                                                                                                                                                                                           |
| **GET**    | `/api/professionals/<id>/` | Retorna os detalhes de um único profissional | Parâmetro de URL: `id`                                                                                                                                                                      |
| **POST**   | `/api/professionals/`      | Cria um novo profissional                    | JSON body: `name`, `profession`, `contact`, `phone`, `email`, `street`, `number`, `complement`, `neighborhood`, `city`, `state`, `zipcode`                                                  |
| **PATCH**  | `/api/professionals/<id>/` | Atualiza os dados de um profissional         | Parâmetro de URL: `id` JSON body (opcionais, exceto `id`): `name`, `profession`,  `contact`, `phone`, `email`, `street`, `number`, `complement`, `neighborhood`, `city`, `state`, `zipcode` |
| **DELETE** | `/api/professionals/<id>/` | Exclui o profissional                        | -                                                                                                                                                                                           |
### Consultas `Appointments`
**Atributos**:
- **Profissional**(`professional`): Cada consulta está vinculada a um profissional via `ForeignKey` (`related_name="appointments"`).
- **Data e horário**(`scheduled_at`): armazena data e hora da consulta.

**Validações**:
- Não é permitido agendar consultas no **passado**.
- Um profissional não pode ter **duas consultas no mesmo horário**.

**Exposição de dados na API**:
- `professional_id`: **write-only**, para referenciar o profissional ao criar/atualizar a consulta.
- `professional`: **read-only**, usando `PartialProfessionalSerializer` (apenas `id`, `name` e `profession`) com o objetivo de melhorar a performance.
#### Endpoints

| Método     | Endpoint                   | Descrição                                                      | Body / Parâmetros                                                                            |
| ---------- | -------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **GET**    | `/api/appointments/`       | Lista todas as consultas com opção de filtrar por profissional | Filtro opcional: `?professional=ID`                                                          |
| **GET**    | `/api/appointments/<id>/`  | Retorna os detalhes de uma consulta                            | Parâmetro de URL: `id`                                                                       |
| **POST**   | `/api/appointments/`       | Cria uma nova consulta                                         | JSON body: `professional_id` (int), `scheduled_at` (datetime)                                |
| **PATCH**  | `/api/professionals/<id>/` | Atualiza as informações de consulta                            | Parâmetro de URL: `id` JSON body (opcionais, exceto `id`): `professional_id`, `scheduled_at` |
| **DELETE** | `/api/appointments/<id>/`  | Exclui a consulta                                              | Parâmetro de URL: `id`                                                                       |
