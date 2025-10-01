## Descrição

API em Django REST para gerenciamento de profissionais de saúde e agendamento de consultas desenvolvida para processo seletivo da Lacrei Saúde. 
### Features
- Cadastro e gerenciamento de profissionais de saúde
- Cadastro e gerenciamento de consultas + filtro de consultas por profissional.
- Autenticação via token simples.
### Tecnologias utilizadas

- **Django** e **Django REST Framework**
- **PostgreSQL**
- **Docker** e **Docker Compose**
- **Poetry** (gerenciamento de dependências)
- **GitHub Actions** (CI/CD e Rollback)
- **AWS Elastic Beanstalk**  e **Amazon RDS** (deploy)
- **Linters**: Black, isort, Flake8
- **Testes**: ApiTestCase
- **Documentação**: Swagger e drf-spectacular

## Deploy funcional

#### Ambiente de produção
O ambiente de produção está com o **banco de dados vazio**.
- **API base**:  
    [http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/](http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/)
- **Documentação**
    - **Swagger UI**: [http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/docs/](http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/docs/)
    - **Redoc**:[http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/docs/](http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/redoc/)
    - **OpenAPI (schema JSON)**: http://lacrei-saude-production.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/schema/

#### Ambiente de staging
O **ambiente de staging** já contém dados fictícios para testes.
- **API base**:  
    [http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/](http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/)
- **Documentação**
    - **Swagger UI**: [http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/docs/](http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/docs/)
    - **Redoc**: [http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/redoc/](http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/redoc/)
    - **OpenAPI (schema JSON)**: http://lacrei-saude-staging.eba-hz6k8hw7.us-east-2.elasticbeanstalk.com/api/schema/

####  Autenticação (todos os endpoints são protegidos)
Você pode autenticar **pela interface da api** (Rest-Framework) ou **através de um Token** de usuário.

1) **Login pela interface (staging).** Use as credenciais de teste para entrar pelo link da API (canto superior direito “Login”):
	- Usuário: `teste@email.com`
	- Senha: `1234pass`

2) **Token via API (staging)**. Para chamadas HTTP diretas, utilize o token no **header**:
```
Authorization: Token eac9e4a5e904426d8097163e52b24f7869acdd40
```

3) **Swagger UI**  utilizar os mesmos credenciais
	- Se você estiver logado pela inteface, conseguirá testar todos os endpoints
	- Caso contrário, clique em "Authenticate" e informe o token acima,

## Rodando o aplicativo em sua máquina
Para rodar o aplicativo localmente siga os passos abaixo. 
#### Pré requisitos
- **Python 3.13+**
- **Postgres**
- **Poetry** (v2.2)
- **Docker**: Opcional, para rodar o aplicativo via container.
#### Opção 1: set up local (sem o Docker)

1. **Clone esse repositório**: para ter o código em sua máquina clone o repositório usando o comando abaixo.
```bash
git clone https://github.com/juliavillela/lacrei-saude.git 
```

2. **Vá para a pasta raiz do projeto**
```bash
cd lacrei-saude
```

3. **Instale as dependências** e **ative o ambiente virtual**: use o poetry para instalar as dependências e em seguida ative o ambiente virtual pra rodar o aplicativo utilizando ele
```bash
poetry install --no-root
poetry env activate
```

4. **Configure as variáveis de ambiente**: Copie o arquivo de exemplo `.env.example` para criar seu `.env` local. Se necessário, ajuste os valores das variáveis.
```bash
# macOS / Linux
cp .env.example .env
```

```bash
# Windows
copy .env.example .env
```

5. **Inicie o postgres**: 
```bash
brew services start postgresql
```

6. **Crie uma base de dados**: com o postgres inicie uma base de dados com o mesmo nome descrito no `.env`
```bash
createdb lacrei_saude_db
```

7. **Execute as migrações**: Peça ao Django que execute as migrações necessárias para rodar o aplicativo.
```bash
poetry run python manage.py migrate
```

8. **Opcional: Crie um superuser(admin)**: Você não precisa criar um superuser para que o aplicativo rode, mas a api é protegida e você precisará de um usuário para fazer o login e conseguir acessar as rotas.
```bash
poetry run python manage.py createsuperuser
```

9. **Rode o servidor local**: 
```bash
poetry run python manage.py runserver
```

A API estará disponível em [http://localhost:8000](http://localhost:8000). Atenção, a página de entrada é vazia, vá para `/api` para ver a API. 

Você não estará logado, faça o login com seu email e senha que designou ao criar o super user. Clicando em "Login" no canto superior direito da tela.

#### Opção 2: set up via docker

1. **Clone esse repositório**: para ter o código em sua máquina clone o repositório usando o comando abaixo.
```bash
git clone https://github.com/juliavillela/lacrei-saude.git 
```

2. **Vá para a pasta raiz do projeto**
```bash
cd lacrei-saude
```

3. **Configure as variáveis de ambiente**: Copie o arquivo de exemplo `.env.example` para criar seu `.env` local. Se necessário, ajuste os valores das variáveis.
```bash
# macOS / Linux
cp .env.example .env
```

```bash
# Windows
copy .env.example .env
```


4. **Faça o build da imagem**: (explicar)
```bash
sudo docker compose build
```

5. **Rode o container do Docker**: (explicar)
```bash
sudo docker compose up
```

8. **Opcional: Crie um superuser(admin)**: Você não precisa criar um superuser para que o aplicativo rode, mas a api é protegida e você precisará de um usuário para fazer o login e conseguir acessar as rotas.
   No comando abaixo, substitua `<container_id>` pelo ID ou nome do container da aplicação (ex.: `lacrei-saude`).
```bash
docker exec -it <container_id> python manage.py test
```

A API estará disponível em [http://localhost:8000](http://localhost:8000). Atenção, a página de entrada é vazia, vá para `/api` para ver a API. 

Você não estará logado, faça o login com seu email e senha que designou ao criar o super user. Clicando em "Login" no canto superior direito da tela.

## Execução dos testes
Com o aplicativo instalado em sua máquina seguindo os passo acima você pode rodar os testes com os passos abaixo:
#### Opção 1: set up local (sem o Docker)

```bash
poetry run python manage.py test
```

#### Opção 2: set up via docker

No comando abaixo, substitua `<container_id>` pelo ID ou nome do container da aplicação (ex.: `lacrei-saude`).
```bash
docker exec -it <container_id> python manage.py test
```


##  Fluxo de Deploy (CI/CD)

O processo de deploy é gerenciado por **GitHub Actions** com integração ao **AWS Elastic Beanstalk**:

- **Branches**:
    - **`main`**: **CI apenas** (lint + testes).
	- **`staging`**: CI + **deploy automático** para o EB _staging_.
	- **`production`**: CI + **deploy automático** para o EB _production_.

- **Pipeline de CI/CD**:
	1. **Lint e Testes**: black, isort, flake8, API TestCase.
	2. **Build e Push da imagem Docker**.
	3. **Gerar bundle do EB**: pin da imagem no `Dockerrun.aws.json` + zip do deploy (`Dockerrun.aws.json` + `.platform/`).
	4. **Deploy no EB**: cria **versão** com rótulo identificável e atualiza o ambiente (staging/production).

## Rollback de Deploy (Elastic Beanstalk)

O projeto possui um workflow manual para **rollback** de deploys em **staging** e **production**, permitindo retornar o deploy  para uma versão anterior sem precisar refazer um build. Cada deploy cria uma nova **Application Version**  no Elastic Beanstalk e **Github Release**, identificadas por um **VERSION_LABEL** (`<sha8>-<YYYYMMDDHHMMSS>`).

**passo a passo:**
1. Acesse **Actions > EB Rollback > Run workflow**.
2. Escolha o `environment` (`staging` ou `production`).
3. Copie o `EB Version` desejado do corpo do Release anterior (exemplo: `45855a2b-20250930183157`).
4. Cole o valor em `version_label` e clique em **Run workflow**.
## Justificativas Técnicas e Detalhes da implementação
O projeto contém 3 aplicações: 
- **Professionals**: Responsável pelos profissionais de saúde. contém os modelos e CRUD
- **Appointments**: Responsável pelas consultas
- **Accounts**: Responsável pelo modelo de usuário, criação dos tokens e validação
### Contas 
Escolhi implementar um modelo customizado de usuário para autenticação via email, pois considero esse fluxo mais usual e seguro do que o padrão baseado em username. Ao ser criado, através de um script de `signals`, cada usuário recebe um token simples (`rest_framework.authtoken`) que pode ser usado para chamadas à API.

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
| **DELETE** | `/api/professionals/<id>/` | Exclui o profissional                        |                                                                                                                                                                                             |
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

| Método     | Endpoint                  | Descrição                                                      | Body / Parâmetros                                                                            |
| ---------- | ------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **GET**    | `/api/appointments/`      | Lista todas as consultas com opção de filtrar por profissional | Filtro opcional: `?professional=ID`                                                          |
| **GET**    | `/api/appointments/<id>/` | Retorna os detalhes de uma consulta                            | Parâmetro de URL: `id`                                                                       |
| **POST**   | `/api/appointments/`      | Cria uma nova consulta                                         | JSON body: `professional_id` (int), `scheduled_at` (datetime)                                |
| **PATCH**  | `/api/appointments/<id>/` | Atualiza as informações de consulta                            | Parâmetro de URL: `id` JSON body (opcionais, exceto `id`): `professional_id`, `scheduled_at` |
| **DELETE** | `/api/appointments/<id>/` | Exclui a consulta                                              | Parâmetro de URL: `id`                                                                       |
