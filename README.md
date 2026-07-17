# Criação de Skills — Refatoração Arquitetural Automatizada

Fork do desafio de Skills com a skill **`refactor-arch`** (Claude Code) e a execução das 3 fases nos projetos legados fornecidos.

Ferramenta escolhida: **Claude Code** (`.claude/skills/refactor-arch/`).

---

## Análise Manual

Antes de criar a skill, os 3 projetos foram lidos arquivo a arquivo. Abaixo, o recorte mínimo exigido (≥5 problemas / projeto, com CRITICAL/HIGH, MEDIUM e LOW).

### 1) `code-smells-project` (Python/Flask — E-commerce)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | SQL Injection por concatenação em `models.py` (login, busca, CRUD) | Compromete autenticação e dados |
| CRITICAL | Endpoint `/admin/query` executa SQL arbitrário | Backdoor de banco sem auth |
| CRITICAL | `SECRET_KEY` hardcoded + exposta em `/health` | Segredo público |
| HIGH | Senhas plaintext no seed e nas listagens | Account takeover |
| MEDIUM | N+1 na montagem de pedidos/itens | Performance frágil |
| MEDIUM | Validação de produto duplicada create/update | Drift de regras |
| LOW | Magic numbers nas faixas de desconto | Regra de negócio opaca |
| LOW | Logs via concatenação/`print` | Observabilidade fraca |

Arquitetura observada: monolito flat (4 arquivos) com camadas nominais (`controllers`/`models`) sem MVC real.

### 2) `ecommerce-api-legacy` (Node.js/Express — LMS + checkout)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | Secrets de gateway/DB/SMTP em `utils.js` | Vazamento PCI/credenciais |
| CRITICAL | Cartão completo logado no checkout | Violação PCI-DSS |
| CRITICAL | `badCrypto` como “hash” de senha | Segurança ilusória |
| HIGH | God class `AppManager` (DB+rotas+pagamento+report) | Impede testes e evolução |
| HIGH | Checkout matricula usuário existente sem senha | Account takeover |
| MEDIUM | Callback hell no relatório financeiro | Race / respostas inconsistentes |
| MEDIUM | Cache global mutável | Estado oculto |
| LOW | Campos crípticos (`usr`, `eml`, `c_id`) | Contrato de API ruim |

Arquitetura observada: bootstrap fino + God Class.

### 3) `task-manager-api` (Python/Flask — Task Manager)

| Severidade | Problema | Por que importa |
|---|---|---|
| CRITICAL | MD5 para senhas | Hash quebrável |
| CRITICAL | Hash retornado em `to_dict()` / login | Vazamento de credenciais |
| CRITICAL | SMTP + `SECRET_KEY` hardcoded | Secrets no código |
| HIGH | Token fake sem middleware | Auth cosmética |
| HIGH | CRUD de categories dentro de `report_routes` | Violação MVC/SRP |
| MEDIUM | N+1 na listagem de tasks | Performance |
| MEDIUM | `datetime.utcnow()` deprecated | API obsoleta |
| LOW | `debug=True` e `create_all` no import | Side-effects e config insegura |

Arquitetura observada: camadas parciais (`models`/`routes`/`services`), com services mortos e rotas gordas.

---

## Construção da Skill

### Decisões de design

A skill vive em `.claude/skills/refactor-arch/` (copiada nos 3 projetos) com:

| Arquivo | Papel |
|---|---|
| `SKILL.md` | Prompt operacional das 3 fases + confirmação obrigatória antes da Fase 3 |
| `project-analysis.md` | Heurísticas agnósticas de linguagem/framework/DB/arquitetura |
| `anti-patterns-catalog.md` | ≥8 anti-patterns + detecção de APIs deprecated |
| `audit-report-template.md` | Formato fixo do relatório (Fase 2) |
| `mvc-architecture-guidelines.md` | Responsabilidades Model / View / Controller / Config / Middleware |
| `refactoring-playbook.md` | ≥8 transformações before/after |

### Anti-patterns do catálogo (e por quê)

1. God Class/Method (CRITICAL) — comum nos 3 projetos  
2. Hardcoded Credentials (CRITICAL) — segurança transversal  
3. SQL Injection (CRITICAL) — presente no Flask legado  
4. Insecure Password Storage (CRITICAL) — plaintext/MD5/badCrypto  
5. Fat Controller (HIGH) — rotas com regra de negócio  
6. Global Mutable State (HIGH) — singletons/caches  
7. N+1 Queries (MEDIUM) — performance  
8. Duplicação / Dead Code (MEDIUM) — manutenção  
9. Magic Numbers / Poor Naming (LOW) — qualidade  
10. Deprecated APIs (MEDIUM/HIGH) — `utcnow`, callbacks, MD5, `Query.get`

### Agnosticismo de tecnologia

- Heurísticas baseadas em **sinais de manifesto e imports**, não em um projeto específico.
- Playbook com exemplos Python **e** Node.
- Fase 3 adapta profundidade: rewrite MVC em monolitos; melhoria incremental em projetos parcialmente organizados.

### Desafios e soluções

- **Projeto 3 já tinha pastas:** a skill não “destrói” a estrutura — extrai controllers, move categories, wire do notification service.
- **Preservar contratos HTTP:** endpoints de negócio mantidos; backdoors (`/admin/query`) removidos como correção de segurança.
- **Validação pós-refatoração:** smoke tests com Flask `test_client` e HTTP real no Express.

> Nota de execução neste repositório: a skill foi criada no formato Claude Code. As Fases 1–3 foram **executadas neste ambiente** seguindo o `SKILL.md` e os arquivos de referência (análise → auditoria com confirmação → refatoração MVC + validação), gerando os artefatos em `reports/` e o código refatorado commitado.

---

## Resultados

### Resumo dos findings (Fase 2)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| code-smells-project | 5 | 4 | 3 | 2 | 14 |
| ecommerce-api-legacy | 4 | 4 | 3 | 2 | 13 |
| task-manager-api | 3 | 4 | 4 | 2 | 13 |

Relatórios completos:

- `reports/audit-project-1.md`
- `reports/audit-project-2.md`
- `reports/audit-project-3.md`

### Antes / depois — estrutura

#### Projeto 1 — code-smells-project

**Antes:** `app.py`, `controllers.py`, `models.py`, `database.py`  
**Depois:**

```
code-smells-project/
├── app.py                      # entry point
├── .claude/skills/refactor-arch/
├── src/
│   ├── config/settings.py
│   ├── models/                 # produto, usuario, pedido + database
│   ├── views/routes.py
│   ├── controllers/
│   ├── services/notification_service.py
│   ├── middlewares/error_handler.py
│   └── app.py
└── legacy/                     # código original arquivado
```

#### Projeto 2 — ecommerce-api-legacy

**Antes:** `AppManager.js` + `utils.js`  
**Depois:**

```
ecommerce-api-legacy/src/
├── config/settings.js
├── models/                     # database + domain models
├── controllers/
├── views/routes.js
├── services/paymentService.js
├── middlewares/errorHandler.js
└── app.js
```

#### Projeto 3 — task-manager-api

**Antes:** routes gordas + service morto + MD5  
**Depois:** `config/` + `controllers/` + routes finas + categories separadas + notification wiring + hashing seguro.

### Checklist de validação

#### Projeto 1

##### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask)
- [x] Domínio descrito (E-commerce)
- [x] Arquivos analisados coerentes (4)

##### Fase 2 — Auditoria
- [x] Relatório no template
- [x] Findings com arquivo:linha
- [x] Ordenados CRITICAL→LOW
- [x] ≥5 findings (+ CRITICAL/HIGH)
- [x] APIs/padrões fracos/deprecated cobertos
- [x] Confirmação antes da Fase 3

##### Fase 3 — Refatoração
- [x] Estrutura MVC
- [x] Config sem secrets hardcoded
- [x] Models / Views / Controllers
- [x] Error handling centralizado
- [x] Entry point claro
- [x] App sobe e endpoints respondem

#### Projeto 2
- [x] Mesmos itens do checklist (stack Node/Express detectada; LMS/checkout; MVC async; endpoints `/api/checkout`, report e delete OK)

#### Projeto 3
- [x] Mesmos itens (Python/Flask Task Manager; findings mesmo com camadas parciais; endpoints preservados após melhoria MVC)

### Logs de validação (pós-refatoração)

**Projeto 1**
```
health 200 ... status=ok, versao=2.0.0
produtos 200 (10 itens)
login 200 admin@loja.com
pedido 201 pedido_id=1
usuarios sem campo senha
```

**Projeto 2**
```
LMS API (MVC) rodando na porta 3000...
checkout 200 enrollment_id=2
denied 400 Pagamento recusado
report 200 Clean Architecture + Docker
```

**Projeto 3**
```
Seed: 3 usuários, 4 categorias, 10 tasks
health 200
tasks 200 (10)
categories 200 (4)
login 200 (sem password no JSON)
summary 200
```

### Observações multi-stack

A mesma skill guiou Flask monolítico, Express God Class e Flask semi-organizado. A diferença esteve na **profundidade da Fase 3**: rewrite completo nos projetos 1–2 e refino estrutural no 3, sem quebrar contratos.

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado
- Python 3.10+ e `pip`
- Node.js 18+ e `npm`

### Executar a skill (Claude Code)

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 2 imprime o relatório e pergunta `Proceed with refactoring (Phase 3)? [y/n]`.  
Salve a saída da Fase 2 em `reports/audit-project-{1,2,3}.md` (já presentes neste fork).

### Subir as APIs refatoradas

```bash
# Projeto 1 — http://localhost:5000
cd code-smells-project
pip install -r requirements.txt
python3 app.py

# Projeto 2 — http://localhost:3000
cd ecommerce-api-legacy
npm install
npm start

# Projeto 3 — http://localhost:5000
cd task-manager-api
pip install -r requirements.txt
python3 seed.py
python3 app.py
```

### Validar rapidamente

```bash
curl -s http://localhost:5000/health          # projeto 1 ou 3
curl -s http://localhost:5000/produtos        # projeto 1
curl -s http://localhost:3000/api/admin/financial-report
curl -s http://localhost:5000/tasks           # projeto 3
```

---

## Estrutura do repositório

```
├── README.md
├── reports/
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
├── code-smells-project/
│   └── .claude/skills/refactor-arch/
├── ecommerce-api-legacy/
│   └── .claude/skills/refactor-arch/
└── task-manager-api/
    └── .claude/skills/refactor-arch/
```

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
