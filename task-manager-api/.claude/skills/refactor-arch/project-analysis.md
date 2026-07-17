# Análise de Projeto — Heurísticas

Use estas heurísticas na **Fase 1** para detectar stack e mapear arquitetura,
independentemente da linguagem.

## 1. Detecção de linguagem

| Sinal | Linguagem |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `*.js` / `*.ts`, `package.json` | JavaScript / TypeScript |
| `*.go`, `go.mod` | Go |
| `*.java`, `pom.xml`, `build.gradle` | Java |
| `*.rb`, `Gemfile` | Ruby |

Priorize arquivos de manifesto para versão e dependências.

## 2. Detecção de framework

### Python
- `from flask import` / `flask` em requirements → **Flask**
- `fastapi`, `django`, `bottle` → framework correspondente
- Versão: leia `requirements.txt` / `pyproject.toml`

### Node.js
- `express` em `package.json` / `require('express')` → **Express**
- `fastify`, `koa`, `nestjs` → framework correspondente
- Versão: `dependencies` / `devDependencies` no `package.json`

## 3. Detecção de banco de dados

| Sinal | Banco |
|---|---|
| `sqlite3`, `*.db`, `:memory:` | SQLite |
| `psycopg`, `pg`, `postgresql` | PostgreSQL |
| `mysql`, `mariadb` | MySQL/MariaDB |
| `mongodb`, `mongoose` | MongoDB |
| `SQLAlchemy`, `sequelize`, `prisma` | ORM sobre o banco declarado |

Liste tabelas a partir de:
- `CREATE TABLE` / migrations
- Models ORM (`__tablename__`, `Schema`, `model.define`)
- Seeds

## 4. Mapeamento de arquitetura

Classifique a arquitetura atual:

| Padrão observado | Classificação |
|---|---|
| Poucos arquivos na raiz com rotas + SQL + regras misturados | **Monolítica flat** |
| Uma classe/arquivo concentra DB, rotas e regras | **God Class / God Module** |
| Pastas `models/`, `routes/`, `services/` parcialmente usadas | **Camadas parciais** |
| Separação clara Model / View(Routes) / Controller + config | **MVC adequado** |

Conte apenas arquivos-fonte (exclua lockfiles, README, assets, `node_modules`).

## 5. Inferência de domínio

Leia nomes de rotas, models, seeds e strings de README:
- produtos/pedidos/usuários → E-commerce
- courses/enrollments/checkout → LMS / educação
- tasks/categories/users → Task Manager
- Genérico: descreva com base nas entidades principais

## 6. Checklist do resumo (Fase 1)

- [ ] Language
- [ ] Framework (+ versão)
- [ ] Dependencies (principais)
- [ ] Domain
- [ ] Architecture (1–2 frases)
- [ ] Source files (N)
- [ ] DB tables
