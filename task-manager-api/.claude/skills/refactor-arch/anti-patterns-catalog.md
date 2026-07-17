# Catálogo de Anti-Patterns

Catálogo mínimo para a **Fase 2**. Cada item inclui sinais de detecção e
severidade padrão. Ajuste a severidade se o impacto no contexto for maior/menor.

---

## 1. God Class / God Method
**Severidade:** CRITICAL

**Sinais:**
- Um arquivo/classe > ~200–300 LOC misturando rotas, SQL, validação e regras
- Métodos que orquestram DB + pagamento + notificação + resposta HTTP

**Impacto:** Impossível testar em isolamento; qualquer mudança afeta tudo.

**Recomendação:** Separar Models, Controllers e Views/Routes por domínio.

---

## 2. Hardcoded Credentials / Secrets
**Severidade:** CRITICAL

**Sinais:**
- `SECRET_KEY = "..."`, senhas SMTP, API keys `pk_live_`, DB user/pass no código
- Secrets retornados em endpoints (`health` expondo secret_key)

**Impacto:** Compromete produção; vazamento via VCS.

**Recomendação:** Extrair para env (`os.environ` / `process.env`) + `.env.example`.

---

## 3. SQL Injection / Query String Concatenation
**Severidade:** CRITICAL

**Sinais:**
- `"... WHERE id = " + str(id)` / `` `... ${var}` `` em SQL
- Endpoint que executa SQL arbitrário do cliente (`/admin/query`)

**Impacto:** Exfiltração/destruição de dados; RCE em casos extremos.

**Recomendação:** Queries parametrizadas (`?` / `%s`) e remover SQL arbitrário.

---

## 4. Insecure Password Storage
**Severidade:** CRITICAL

**Sinais:**
- Senha plaintext no banco / resposta JSON
- Hash fraco: MD5, SHA1 sem salt, “crypto” caseira (loops base64)

**Impacto:** Account takeover em massa.

**Recomendação:** `werkzeug.security` / `bcrypt` / `argon2`; nunca retornar hash.

---

## 5. Fat Controller / Business Logic in Routes
**Severidade:** HIGH

**Sinais:**
- Handlers HTTP com validação + queries + regras de desconto/estoque
- Blueprints com CRUD de outro domínio (ex.: categories dentro de reports)

**Impacto:** Acoplamento HTTP↔domínio; difícil reutilizar e testar.

**Recomendação:** Controllers finos orquestram; Models/Services concentram regras.

---

## 6. Missing Dependency Injection / Global Mutable State
**Severidade:** HIGH

**Sinais:**
- Singleton global de conexão DB compartilhado sem factory
- `globalCache`, `totalRevenue` mutáveis em módulo
- `check_same_thread=False` para “funcionar”

**Impacto:** Race conditions; testes flaky; estado oculto.

**Recomendação:** Factory/DI; connection-per-request ou pool; cache encapsulado.

---

## 7. N+1 Queries
**Severidade:** MEDIUM

**Sinais:**
- Loop sobre pedidos/items com novo `SELECT` por item
- `for task in tasks: User.query.get(task.user_id)`

**Impacto:** Latência cresce linearmente com volume.

**Recomendação:** JOIN / `joinedload` / batch query / agregação SQL.

---

## 8. Duplicated Validation / Dead Code
**Severidade:** MEDIUM

**Sinais:**
- Mesmas regras copiadas em create/update
- Helpers/services importados mas nunca usados
- Dependências no manifesto sem uso

**Impacto:** Drift de regras; manutenção cara.

**Recomendação:** Extrair validadores únicos; remover ou wiring real de services.

---

## 9. Magic Numbers / Poor Naming / Weak Logging
**Severidade:** LOW

**Sinais:**
- Limites numéricos soltos (`10000`, `0.1`) sem constante nomeada
- Campos de API crípticos (`usr`, `eml`, `c_id`)
- `print` como notificação/email

**Impacto:** Legibilidade e onboarding ruins.

**Recomendação:** Constantes nomeadas; nomes claros; logger estruturado.

---

## 10. Deprecated APIs (obrigatório detectar)
**Severidade:** MEDIUM (ou HIGH se segurança)

| API deprecated / obsoleta | Stack | Equivalente moderno |
|---|---|---|
| `datetime.utcnow()` | Python 3.12+ | `datetime.now(timezone.utc)` |
| `datetime.utcfromtimestamp()` | Python 3.12+ | `datetime.fromtimestamp(..., tz=timezone.utc)` |
| MD5/SHA1 para senhas | Qualquer | bcrypt / argon2 / pbkdf2 |
| Callback hell (`db.get` aninhado) | Node sqlite3 | `util.promisify` / `sqlite` async / better-sqlite3 |
| `Flask` `app.run(debug=True)` hardcoded em “prod” | Flask | config por env; debug só em development |
| `User.query.get()` (legado SQLAlchemy) | Flask-SQLAlchemy 3 | `db.session.get(Model, id)` |
| `type(x) == list` | Python | `isinstance(x, list)` |

**Sinais:** grep pelos padrões acima; recomendar o equivalente moderno no finding.

---

## Distribuição mínima exigida

O relatório da Fase 2 deve cobrir **pelo menos 8** anti-patterns do catálogo
(quando presentes no código), com severidades distribuídas entre CRITICAL, HIGH,
MEDIUM e LOW, e **sempre** incluir finding de APIs deprecated quando aplicável.
