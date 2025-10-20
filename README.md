# GradMate API

API REST para gerenciamento de projetos de TCC (Trabalho de Conclusão de Curso), desenvolvida com Flask e MySQL.

Documentação detalhada dos endpoints está em docs/DOCUMENTATION_API.md.

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

# GradMate API

Este projeto é a API REST que usamos para gerenciar projetos de TCC (Trabalho de Conclusão de Curso) — coisas como projetos, alunos, orientadores, relatórios, arquivos e atas de defesa. Escrevi este README de forma direta, sem frescura, pra você entender rápido como rodar, desenvolver e onde olhar quando algo estranha acontecer.

---

Sumário rápido
- O backend é em Python (Flask + Flask-RESTX)
- Banco: MySQL
- Autenticação por JWT
- Uploads salvos em `uploads/projects/{project_id}/`

Pré-requisitos
- Python 3.7+ instalado
- MySQL rodando (pode usar XAMPP)

Instalação e execução (modo rápido)
1) Clone o repositório e entre na pasta:

```powershell
git clone <repo-url>
cd gradmateAPI
```

2) Crie um ambiente virtual e instale dependências (exemplo com venv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se não tiver `requirements.txt`, instale o mínimo:

```powershell
pip install flask flask-restx mysqlclient werkzeug
```

3) Ajuste as configurações em `source/utils/config.py` (user, senha, nome do DB, etc.)

4) Rode as migrações e inicie a API:

```powershell
python source/run_migrations.py
python source/apiRest.py
```

A aplicação vai abrir em `http://localhost:5000`.

Endpoints e uso básico
- A API usa JWT. Faça login em `/auth/login` e passe o token nas requisições:

```
Authorization: Bearer <seu-token>
```

Principais rotas (resumo):
- Auth: `/auth/*` (login, register, current user, gestão de usuários)
- Projetos: `/project/*` (listar, criar, atualizar, deletar, estatísticas)
- Arquivos: `/project/{id}/files` (upload, lista, download, delete, bulk-delete)
- Relatórios: `/project/{id}/reports` (CRUD)
- Atas: `/project/{id}/atas` (CRUD de atas de defesa)
- Professores / Alunos / Cursos / Calendário: endpoints óbvios dentro de `source/api/`

Extras e comportamentos importantes
- Quando você marcar um projeto como `Concluído` (ou `Finalizado`), o sistema marca automaticamente os alunos vinculados como `formado`.
- Existe um endpoint de bulk-delete de arquivos: `POST /project/{id}/files/bulk-delete` que tenta deletar cada arquivo e retorna arrays `deleted` e `failed`.
- Uploads são armazenados em disco com nomes únicos; o banco mantém o original.

Migrações
- As migrações estão em `source/migrations/`. O `run_migrations.py` tenta executar todas — se já existirem tabelas/colunas, o script imprime a mensagem e segue.

Desenvolvimento rápido
- Para adicionar endpoint: crie/edite um arquivo em `source/api/` e registre o namespace em `apiRest.py`.
- Para alterar modelo/migrations: crie um arquivo em `source/migrations/NNN_descricao.py` com `run_migration()` e adicione o nome no `run_migrations.py`.


Contato / Autor
- Projeto mantido por: chrono2k

Licença
- Uso acadêmico / interno