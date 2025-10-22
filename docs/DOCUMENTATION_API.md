# GradMate API — Documentação

Este documento consolida visão, arquitetura, padrões e os principais endpoints da API GradMate. Use-o como referência rápida durante o desenvolvimento do front e para integração com terceiros.

## 1) Visão Geral

- Objetivo: gestão de TCC (projetos), com cadastro de alunos, professores, cursos, relatórios, arquivos e atas de defesa.
- Stack:
  - API: Python (Flask + Flask-RESTX)
  - Banco: MySQL/MariaDB
  - Auth: JWT (Bearer Token)
- Ambiente: pode rodar com XAMPP (MySQL) + Python local. Base URL típica: `http://localhost:5000/`.
- Documentação interativa: fornecida pelo Flask-RESTX (Swagger). Dependendo da configuração, a UI aparece na raiz da API.

## 2) Estrutura (resumo)

- `source/api/` — endpoints
  - `auth.py`, `project.py`, `teacher.py`, `student.py`, `course.py`, `report.py`, `date.py`
- `source/models/` — acesso a dados (consultas SQL centralizadas)
- `source/migrations/` — scripts de migração do banco (executados por `run_migrations.py`)
- `source/utils/` — config, JWT, MySQL e utilitários de request

## 3) Autenticação e Perfis

- Login retorna um JWT; use-o no header:
  - `Authorization: Bearer <token>`
- Perfis e escopo de acesso:
  - `admin` → acesso a todos os recursos
  - `teacher` → acesso aos seus projetos e operações correlatas
  - `student` → acesso aos seus projetos e dados relacionados
- Notas:
  - O listing de projetos é filtrado automaticamente pelo perfil do usuário logado.
  - Algumas rotas exigem perfis específicos (ex.: bulk delete de arquivos exige admin/teacher com vínculo ao projeto).

## 4) Convenções da API

- JSON:
  - Envie `Content-Type: application/json` em POST/PUT com corpo JSON.
  - O backend tolera payloads como string JSON, mas o ideal é enviar objeto JSON válido.
- Datas/horas: utilize ISO (`YYYY-MM-DD` ou `YYYY-MM-DDTHH:mm:ssZ`) quando aplicável.
- IDs: campos seguem padrão `snake_case` (ex.: `course_id`); para criação/edição de projeto, `courseId` também é aceito.
- Uploads: multipart form-data com campo `files[]`.
- Respostas: geralmente no formato `{ key: value }` (ex.: `{ projects: [...] }`).
- Erros: retornam `status` HTTP com `{ error: string, details?: any }` quando apropriado.

## 5) Migrações

- Execute sempre antes de iniciar a API:
  - `python source/run_migrations.py`
- Destaques recentes:
  - Tabela `defense_minutes` (atas de defesa)
  - `student_name` nas atas tornou-se opcional (NULL permitido)
  - FK de arquivos nas atas com `ON DELETE SET NULL`

## 6) Endpoints (referência)

Observação: nomes podem variar conforme evolução. Quando em dúvida, consulte a Swagger UI.

### 6.1 Auth

- POST `/auth/login`
  - Body: `{ "username": string, "password": string }`
  - 200 → `{ token, user: { id, name, role } }`
- GET `/auth/user`
  - Header: `Authorization`
  - 200 → `{ id, name, role, ... }`
- POST `/auth/user/password`
  - Header: `Authorization`
  - Body: `{ currentPassword: string, newPassword: string }`
  - 200 → `{ success: true, message: "Senha atualizada com sucesso" }`
  - 400 → `{ success: false, message: "Senha atual inválida" | "A nova senha deve ser diferente da atual" | "currentPassword e newPassword são obrigatórios" }`
  - 403 → `{ success: false, message: "Usuário inativo" }`
  - 404 → `{ success: false, message: "Usuário não encontrado" }`

### 6.2 Courses

- GET `/course?status=all|active` → `{ courses: [...] }`
- GET `/course/{id}` → `{ course }`
- POST `/course`
  - Body: `{ name: string, observation?: string }`
- PUT `/course`
  - Body: `{ id: number, name?: string, observation?: string }`
- DELETE `/course`
  - Body: `{ id: number }` (desativa)
- POST `/course/active`
  - Body: `{ id: number }` (reativa)

### 6.3 Teachers

- GET `/teacher` → `{ teachers: [...] }`

### 6.4 Students

- GET `/student` → `{ students: [...] }`

### 6.5 Projects

- GET `/project?status=<filtro>`
  - Filtra por perfil: student/teacher veem apenas seus projetos; admin vê todos.
  - 200 → `{ projects: [...] }`
- POST `/project`
  - Body: `{ name: string, description?: string, observation?: string, course_id?: number, courseId?: number }`
  - Se o criador for professor, ele é auto-atribuído como orientador.
- GET `/project/{id}` → `{ project }`
- PUT `/project/{id}`
  - Body: `{ name?, description?, observation?, course_id?, status? }`
  - Observação: ao definir status para “Concluído”/“Finalizado”, todos os alunos do projeto são marcados como `formado` automaticamente.
- DELETE `/project/{id}`

Professores no Projeto
- POST `/project/{id}/teachers` → `{ teacher_ids: number[] }`
- DELETE `/project/{id}/teachers/{teacherId}`

Alunos no Projeto
- POST `/project/{id}/students` → `{ student_ids: number[] }`
- DELETE `/project/{id}/students/{studentId}`

Relatórios do Projeto
- POST `/project/{id}/reports` → `{ description: string, status: string }`
- PUT `/project/{id}/reports/{reportId}` → `{ description?: string, status?: string }`
- DELETE `/project/{id}/reports/{reportId}`

Arquivos do Projeto
- GET `/project/{id}/files` → `{ files: [{ id, original_name, size, created_at }] }`
- POST `/project/{id}/files` (multipart: `files[]`)
- GET `/project/{id}/files/{fileId}/download` → Content-Disposition filename
- DELETE `/project/{id}/files/{fileId}`
- POST `/project/{id}/files/bulk-delete` → `{ file_ids: number[] }`
  - Resposta: `{ deleted: number[], failed: [{ id, reason }] }`

Atas de Defesa (Defense Minutes)
- GET `/project/atas` → lista global com `project_name`: `{ atas: [...] }`
- GET `/project/{id}/atas` → lista por projeto: `{ atas: [...] }`
- POST `/project/{id}/atas`
  - Body típico: `{ date: 'YYYY-MM-DD', result: 'Aprovado|Reprovado|...', file_id?: number, student_name?: string }`
- DELETE `/project/{id}/atas/{ataId}`

Datas/Calendário
- GET `/date` → `{ dates: [...] }` (status de marcos do calendário)
- PUT `/date` → atualiza status/flags conforme corpo enviado

## 7) Regras de Autorização (resumo)

- Bearer Token obrigatório na maioria dos endpoints (exceto login).
- Projetos
  - Listagem: filtrada por perfil automaticamente
  - Alterações sensíveis (ex.: incluir/remover professor, bulk-delete de arquivos): requer admin ou teacher vinculado ao projeto
- Arquivos
  - Download: requer acesso ao projeto
  - Bulk-delete: best-effort; retorna listas de sucesso/falha

## 8) Padrões de Resposta e Erros

- Sucesso: 200/201 com objeto JSON; em deleções, pode retornar `{ success: true }`.
- 400 (Bad Request): payload inválido, campos ausentes.
- 401 (Unauthorized): token ausente/expirado.
- 403 (Forbidden): sem permissão para o recurso.
- 404 (Not Found): recurso inexistente.
- 409 (Conflict): violação de unicidade, vínculo já existente.
- 500 (Internal Error): exceções não tratadas.

Mensagens comuns
- JSON inválido → garanta `Content-Type: application/json` e body JSON válido.
- Ownership → tentativa de operar arquivo/ata/projeto sem vínculo.
- Duplicidade → adicionar aluno/professor já vinculado.

## 9) Exemplos Rápidos

Login
```http
POST /auth/login
Content-Type: application/json

{ "username": "admin", "password": "secret" }
```
Resposta
```json
{ "token": "<jwt>", "user": { "id": 1, "name": "Admin", "role": "admin" } }
```

Criar Projeto
```http
POST /project
Authorization: Bearer <jwt>
Content-Type: application/json

{ "name": "Sistema X", "courseId": 2, "description": "TCC sobre ..." }
```

Upload de Arquivos
```http
POST /project/10/files
Authorization: Bearer <jwt>
Content-Type: multipart/form-data

files[]: <file1>
files[]: <file2>
```

Bulk-delete de Arquivos
```http
POST /project/10/files/bulk-delete
Authorization: Bearer <jwt>
Content-Type: application/json

{ "file_ids": [12, 13, 99] }
```
Resposta
```json
{ "deleted": [12, 13], "failed": [{ "id": 99, "reason": "not-found" }] }
```


---

Se notar divergência entre este documento e a API em execução, confie na Swagger UI e atualize este arquivo.