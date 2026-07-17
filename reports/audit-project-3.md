================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy)
Files:   12 analyzed | ~900 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Insecure Password Hashing (MD5)
File: models/user.py:27-32
Description: Senhas hasheadas com MD5 sem salt, algoritmo inadequado para credenciais.
Impact: Hashes quebráveis offline com facilidade.
Recommendation: Migrar para `werkzeug.security.generate_password_hash` / pbkdf2-sha256.

### [CRITICAL] Password Hash Leak in API
File: models/user.py:21, routes/user_routes.py:85-86, routes/user_routes.py:209
Description: `to_dict()` inclui `password`; create/login devolvem o hash ao cliente.
Impact: Facilita cracking offline e viola privacidade.
Recommendation: Remover `password` da serialização pública.

### [CRITICAL] Hardcoded Secrets
File: app.py:13, services/notification_service.py:9-10
Description: `SECRET_KEY` e credenciais SMTP (`taskmanager@gmail.com` / `senha123`) no código.
Impact: Comprometimento de sessão e caixa de email.
Recommendation: Config via env; notification service em dry-run sem credenciais reais.

### [HIGH] Fake Authentication Token
File: routes/user_routes.py:210
Description: Login retorna `fake-jwt-token-{id}` sem assinatura nem middleware de validação.
Impact: Impersonation trivial; falsa sensação de auth.
Recommendation: Token opaco assinado ou JWT real + guards nas rotas sensíveis (mínimo: não vazar hashes).

### [HIGH] Fat Routes / Misplaced Categories
File: routes/report_routes.py:157-223
Description: CRUD de categorias vive no blueprint de reports; rotas concentram regra + SQL.
Impact: Violação SRP e MVC; reports acoplados a outro domínio.
Recommendation: Extrair `CategoryController` + blueprint `categories`.

### [HIGH] Dead Notification Service
File: services/notification_service.py (arquivo completo)
Description: Serviço nunca importado pelas rotas, apesar de existir na arquitetura.
Impact: Arquitetura “de fachada”; código morto com secrets.
Recommendation: Wiring real no create/assign de tasks ou remoção consciente.

### [HIGH] Bare except Swallowing Errors
File: routes/task_routes.py:62-63, routes/report_routes.py:186-188
Description: `except:` nu engole qualquer falha e devolve erro genérico.
Impact: Debugging impossível; mascara bugs de schema/DB.
Recommendation: Error handler centralizado + `except Exception` com logging.

### [MEDIUM] N+1 Queries on Task List
File: routes/task_routes.py:16-57
Description: Para cada task, novos `User.query.get` e `Category.query.get`.
Impact: Performance degradada com volume.
Recommendation: `joinedload(Task.user, Task.category)` e `to_dict(include_relations=True)`.

### [MEDIUM] Duplicated Overdue Logic
File: routes/task_routes.py:30-39, routes/user_routes.py:171-180, routes/report_routes.py:33-43
Description: Cálculo de overdue repetido em 3 rotas apesar de `Task.is_overdue()`.
Impact: Inconsistência futura.
Recommendation: Reutilizar método de domínio do model.

### [MEDIUM] Deprecated API — datetime.utcnow()
File: models/user.py:14, models/task.py:15-16, routes/*.py
Description: Uso de `datetime.utcnow()` (deprecated desde Python 3.12).
Impact: Warnings e problemas de timezone-aware comparisons.
Recommendation: `datetime.now(timezone.utc)` centralizado em helper `utcnow()`.

### [MEDIUM] Unused Dependencies / Helpers
File: requirements.txt:4-5, utils/helpers.py:57-108
Description: `marshmallow` e `requests` não usados; `process_task_data` existe mas rotas validam inline.
Impact: Superfície e confusão de onboarding.
Recommendation: Remover deps mortas e passar a usar helpers no controller.

### [LOW] db.create_all at Import Time
File: app.py:30-31
Description: Schema criado no import do módulo.
Impact: Side-effects dificultam testes e tooling.
Recommendation: Criar schema no `create_app()` de forma explícita.

### [LOW] Debug Hardcoded
File: app.py:34
Description: `app.run(debug=True)` fixo.
Impact: Config insegura se usada como padrão de deploy.
Recommendation: `settings.DEBUG` via env.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
