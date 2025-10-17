# GradMate API

API REST para gerenciamento de projetos de TCC (Trabalho de Conclusão de Curso), desenvolvida com Flask e MySQL.

## Funcionalidades

- **Autenticação**: Sistema de login com JWT
- **Gestão de Usuários**: CRUD completo com controle de permissões (admin, teacher, student)
- **Projetos TCC**: Gerenciamento de projetos com múltiplos status
- **Orientadores e Banca**: Sistema de vinculação de professores com diferentes papéis (orientador/convidado)
- **Alunos**: Cadastro e vinculação de alunos aos projetos
- **Relatórios**: Registro de acompanhamento dos projetos
- **Arquivos**: Upload, download e gerenciamento de arquivos por projeto
- **Atas de Defesa**: Registro de defesas com resultado e documentação
- **Calendário**: Controle de status de datas importantes
- **Cursos**: Gestão de cursos acadêmicos

## Tecnologias

- Python 3.x
- Flask + Flask-RESTX
- MySQL
- JWT para autenticação
- CORS habilitado

## Estrutura do Projeto

```
gradmateAPI/
├── source/
│   ├── api/              # Endpoints da API
│   │   ├── auth.py       # Autenticação e gestão de usuários
│   │   ├── project.py    # Projetos, arquivos e atas
│   │   ├── teacher.py    # Professores
│   │   ├── student.py    # Alunos
│   │   ├── course.py     # Cursos
│   │   ├── report.py     # Relatórios
│   │   └── date.py       # Status de datas
│   ├── models/           # Modelos de dados
│   ├── migrations/       # Migrações do banco
│   ├── utils/            # Utilitários (config, JWT, MySQL)
│   ├── apiRest.py        # Inicialização da aplicação
│   ├── cors.py           # Configuração CORS
│   ├── decorators.py     # Decoradores (token_required)
│   └── run_migrations.py # Executor de migrações
└── uploads/              # Arquivos enviados pelos usuários
```

## Instalação

### Pré-requisitos

- Python 3.7+
- MySQL Server
- XAMPP (ou qualquer servidor MySQL)

### Dependências

```bash
pip install flask flask-restx mysqlclient werkzeug
```

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/chrono2k/gradmateAPI.git
cd gradmateAPI
```

2. Configure o banco de dados em `source/utils/config.py`:
```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_PORT = 3306
MYSQL_DB = 'gradmate'
```

3. Configure as chaves secretas (importante para produção):
```python
SECRET_KEY = 'sua_chave_secreta'
JWT_SECRET_KEY = 'sua_chave_jwt'
```

4. Execute a aplicação:
```bash
cd source
python apiRest.py
```

A API estará disponível em `http://localhost:5000`

## Documentação

A documentação interativa Swagger está disponível em:
```
http://localhost:5000/api/docs
```

## Endpoints Principais

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Registro de novo usuário
- `GET /auth/user` - Dados do usuário autenticado

### Gestão de Usuários (Admin)
- `GET /auth/users` - Listar todos os usuários
- `GET /auth/users/{id}` - Buscar usuário por ID
- `POST /auth/users` - Criar novo usuário
- `PUT /auth/users/{id}` - Atualizar usuário
- `DELETE /auth/users/{id}` - Deletar usuário
- `PATCH /auth/users/{id}/status` - Ativar/desativar usuário
- `PATCH /auth/users/{id}/role` - Alterar papel do usuário
- `POST /auth/users/{id}/reset-password` - Resetar senha

### Projetos
- `GET /project/` - Listar projetos
- `POST /project/` - Criar projeto
- `GET /project/{id}` - Buscar projeto específico
- `PUT /project/{id}` - Atualizar projeto
- `DELETE /project/{id}` - Deletar projeto
- `GET /project/statistics` - Estatísticas dos projetos

### Orientadores/Banca
- `POST /project/{id}/teachers` - Adicionar orientadores
- `DELETE /project/{id}/teachers/{teacher_id}` - Remover orientador
- `PUT /project/{id}/guests` - Adicionar membros da banca
- `DELETE /project/{id}/guests/{guest_id}` - Remover membro da banca

### Alunos
- `POST /project/{id}/students` - Adicionar alunos ao projeto
- `DELETE /project/{id}/students/{student_id}` - Remover aluno

### Relatórios
- `POST /project/{id}/reports` - Criar relatório
- `PUT /project/{id}/reports/{report_id}` - Atualizar relatório
- `DELETE /project/{id}/reports/{report_id}` - Deletar relatório

### Arquivos
- `GET /project/{id}/files` - Listar arquivos do projeto
- `POST /project/{id}/files` - Upload de arquivos
- `GET /project/{id}/files/{file_id}/download` - Download de arquivo
- `DELETE /project/{id}/files/{file_id}` - Deletar arquivo

### Atas de Defesa
- `POST /project/{id}/atas` - Registrar ata de defesa
- `GET /project/{id}/atas` - Listar atas do projeto
- `GET /project/{id}/atas/{ata_id}` - Buscar ata específica
- `DELETE /project/{id}/atas/{ata_id}` - Deletar ata

### Calendário
- `GET /date/` - Listar status de datas
- `POST /date/` - Criar status de data
- `PUT /date/` - Atualizar status de data
- `DELETE /date/` - Deletar status de data
- `GET /date/year/{year}` - Status de um ano específico
- `GET /date/statistics` - Estatísticas do calendário

### Professores
- `GET /teacher/` - Listar professores
- `POST /teacher/` - Criar professor
- `GET /teacher/{id}` - Buscar professor
- `PUT /teacher/{id}` - Atualizar professor
- `DELETE /teacher/{id}` - Deletar professor

### Alunos
- `GET /student/` - Listar alunos
- `POST /student/` - Criar aluno
- `GET /student/{id}` - Buscar aluno
- `PUT /student/{id}` - Atualizar aluno
- `DELETE /student/{id}` - Deletar aluno

### Cursos
- `GET /course/` - Listar cursos
- `POST /course/` - Criar curso
- `GET /course/{id}` - Buscar curso
- `PUT /course/{id}` - Atualizar curso
- `DELETE /course/{id}` - Deletar curso

## Autenticação

A API utiliza JWT (JSON Web Token) para autenticação. Após o login, inclua o token no header das requisições:

```
Authorization: Bearer seu_token_aqui
```

## Níveis de Acesso

- **admin**: Acesso total ao sistema, incluindo gestão de usuários
- **teacher**: Gestão de projetos, relatórios e arquivos
- **student**: Visualização e interação limitada

## Migrações

O sistema executa automaticamente todas as migrações ao iniciar. As migrações criam as seguintes tabelas:

1. `user` - Usuários do sistema
2. `course` - Cursos
3. `student` - Alunos
4. `teacher` - Professores
5. `project` - Projetos TCC
6. `student_course` - Relação aluno-curso
7. `student_project` - Relação aluno-projeto
8. `teacher_course` - Relação professor-curso
9. `teacher_project` - Relação professor-projeto (com role: advisor/guest)
10. `report` - Relatórios de acompanhamento
11. `calendar` - Status de datas
12. `project_files` - Arquivos dos projetos
13. `defense_minutes` - Atas de defesa

## Status de Projeto

- Pré-projeto
- Qualificação
- Defesa
- Finalizado
- Trancado

## Uploads

Os arquivos são armazenados em `uploads/projects/{project_id}/` com nomes únicos gerados automaticamente. O sistema suporta arquivos de até 64MB por requisição.

## Desenvolvimento

### Adicionar Nova Migração

1. Crie um arquivo em `source/migrations/` seguindo o padrão `NNN_descricao.py`
2. Implemente a função `run_migration()`
3. Adicione o nome do arquivo (sem extensão) na lista em `run_migrations.py`

### Adicionar Novo Endpoint

1. Crie ou edite um arquivo em `source/api/`
2. Defina o namespace com `Namespace()`
3. Crie as classes Resource com os métodos HTTP
4. Registre o namespace em `apiRest.py`

## Segurança

- Senhas são hasheadas com Werkzeug Security
- JWT para autenticação stateless
- Validação de permissões em endpoints sensíveis
- CORS configurado para aceitar origens específicas

## Licença

Este projeto é de uso acadêmico.

## Autor

chrono2k
