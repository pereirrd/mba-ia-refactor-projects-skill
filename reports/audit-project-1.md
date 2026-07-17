================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection / Query String Concatenation
File: models.py:47-50, models.py:109-110, models.py:289-297
Description: Queries montadas com concatenação de strings do usuário (INSERT de produtos, login e busca com LIKE).
Impact: Bypass de autenticação e exfiltração/destruição de dados via payloads clássicos.
Recommendation: Substituir por prepared statements (`?`) em todos os pontos de acesso a dados.

### [CRITICAL] Arbitrary SQL Admin Endpoint
File: app.py:59-78
Description: Endpoint `/admin/query` executa SQL arbitrário enviado no body sem autenticação.
Impact: Comprometimento total do banco (DROP, SELECT sensível, UPDATE em massa).
Recommendation: Remover o endpoint; operações administrativas devem ser scripts controlados ou rotas com allowlist.

### [CRITICAL] Hardcoded Credentials
File: app.py:7, controllers.py:289
Description: `SECRET_KEY` hardcoded e ainda exposta no JSON de `/health`.
Impact: Vazamento de segredo de sessão/criptografia via repositório e API pública.
Recommendation: Mover para variável de ambiente e nunca retornar secrets em responses.

### [CRITICAL] Insecure Password Storage
File: database.py:76-82, models.py:83, models.py:99
Description: Senhas armazenadas e retornadas em plaintext nas listagens de usuários.
Impact: Account takeover imediato se a API ou o banco vazarem.
Recommendation: Hash com werkzeug/bcrypt e omitir o campo senha nas serializações.

### [CRITICAL] God Class / God Method
File: models.py:1-314
Description: Arquivo único concentra SQL, regras de estoque, descontos e montagem de pedidos para múltiplos domínios.
Impact: Impossível testar em isolamento; qualquer mudança arrisca regressões cruzadas.
Recommendation: Separar models/controllers por domínio (produto, usuário, pedido).

### [HIGH] Fat Controller / Side Effects Inline
File: controllers.py:208-210, controllers.py:247-250
Description: Controllers misturam validação HTTP com “notificações” via `print` (email/SMS/push).
Impact: Acoplamento e impossibilidade de testar side-effects.
Recommendation: Extrair `NotificationService` e manter controllers como orquestradores.

### [HIGH] Missing Auth on Admin Destructive Routes
File: app.py:47-57
Description: `/admin/reset-db` apaga todas as tabelas sem autenticação.
Impact: Qualquer cliente pode zerar a base em produção.
Recommendation: Remover em runtime ou exigir autenticação admin + ambiente controlado.

### [HIGH] Global Mutable DB Singleton
File: database.py:4-10
Description: Conexão SQLite global com `check_same_thread=False`.
Impact: Condições de corrida e comportamento indefinido sob concorrência.
Recommendation: Factory/connection-per-request com commit/rollback explícitos.

### [HIGH] DEBUG=True Hardcoded
File: app.py:8, app.py:88
Description: Aplicação sobe com debug habilitado no código.
Impact: Exposição de stack traces e debugger remoto.
Recommendation: Controlar via `DEBUG` em settings/env.

### [MEDIUM] N+1 Queries
File: models.py:171-233
Description: Listagem de pedidos abre novos cursores por item e por produto.
Impact: Latência cresce linearmente com volume de pedidos/itens.
Recommendation: JOIN único agregando itens e nomes de produtos.

### [MEDIUM] Duplicated Validation
File: controllers.py:24-62 vs controllers.py:64-96
Description: Regras de validação de produto duplicadas entre create e update.
Impact: Drift de regras e manutenção duplicada.
Recommendation: Extrair validador único reutilizado pelos controllers.

### [MEDIUM] Deprecated / Weak Patterns
File: controllers.py (vários), models.py (concat SQL)
Description: Tratamento genérico `except Exception` retornando `str(e)` ao cliente; ausência de hashing moderno.
Impact: Vazamento de detalhes internos e segurança frágil.
Recommendation: Error handler centralizado + hashing forte.

### [LOW] Magic Numbers in Business Rules
File: models.py:256-262
Description: Faixas de desconto `10000/5000/1000` e taxas `0.1/0.05/0.02` literais.
Impact: Regra de negócio opaca e difícil de ajustar.
Recommendation: Constantes nomeadas em `config/settings.py`.

### [LOW] Poor Logging Style
File: controllers.py:8, controllers.py:57
Description: Logs com concatenação de strings em vez de logger estruturado.
Impact: Observabilidade fraca.
Recommendation: Usar `logging` com campos estruturados.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
