## Set Up
#### Setup local (sem Docker)

Clone o repositório:
```bash
git clone https://github.com/juliavillela/lacrei-saude.git 
cd lacrei-saude
```

Instale as dependências:
```bash
poetry install
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

A API estará disponível em [http://localhost:8000](http://localhost:8000).
#### Setup via Docker

Build da imagem:
```bash
docker build -t api-saude .
```

Suba o container:
```bash
docker run -p 8000:8000 api-saude
```

#### Execução dos Testes

Localmente (sem Docker):
```bash
poetry run python manage.py test
```

```bash
docker exec -it <container_id> python manage.py test
```

###  Fluxo de Deploy (CI/CD)

O fluxo de deploy é gerenciado por **GitHub Actions**:

- **Branches**:
    - `main` → ambiente de desenvolvimento (roda apenas testes/lint).
    - `staging` → deploy automático para ambiente de **staging** na AWS.
    - `production` → deploy automático para ambiente de **produção** na AWS.

- **Pipeline**:
    1. Rodar testes (Black, isort, Flake8 e Django TestCase).
    2. Build da imagem Docker e push para Docker Hub.
    3. Deploy no **Elastic Beanstalk**:
        - `staging` → ambiente de homologação.
        - `production` → ambiente de produção.

## Justificativas Técnicas

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
