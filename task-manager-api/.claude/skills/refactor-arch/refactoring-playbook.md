# Playbook de Refatoração

Padrões de transformação para a **Fase 3**. Mínimo 8 padrões com before/after.

---

## 1. Extrair Config (Hardcoded Secrets → Env)

**Before (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**After:**
```python
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    PORT = int(os.environ.get("PORT", "5000"))
```

---

## 2. Parameterizar SQL (SQL Injection → Prepared Statements)

**Before:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "'")
```

**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))
```

---

## 3. Separar God Module em MVC

**Before:** `AppManager.js` com DB + rotas + pagamento + relatório.

**After:**
```
models/userModel.js      → CRUD users
models/courseModel.js    → courses
controllers/checkoutController.js → orquestra pagamento + enrollment
controllers/reportController.js
views/routes.js          → app.post/get/delete → controllers
middlewares/errorHandler.js
config/settings.js
```

---

## 4. Fat Route → Controller + Model

**Before (Flask route com SQL e regra):**
```python
@app.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    # validação + SQL + desconto + print email...
```

**After:**
```python
# views/routes.py
@bp.post("/pedidos")
def criar_pedido():
    return pedido_controller.criar()

# controllers/pedido_controller.py
def criar():
    dados = request.get_json() or {}
    resultado, erro = PedidoModel.criar(dados.get("usuario_id"), dados.get("itens", []))
    if erro:
        return jsonify({"erro": erro, "sucesso": False}), 400
    notification_service.notify_pedido_criado(resultado)
    return jsonify({"dados": resultado, "sucesso": True}), 201
```

---

## 5. Password Hashing Seguro

**Before:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
# ou senha plaintext no INSERT
```

**After (Python):**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

**After (Node):**
```javascript
const bcrypt = require('bcryptjs');
const hash = await bcrypt.hash(password, 10);
```

E `to_dict()` **nunca** inclui `password`/`senha`.

---

## 6. N+1 → JOIN / Eager Load

**Before:**
```python
for row in pedidos:
    cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (row["id"],))
    for item in itens:
        cursor.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**After:**
```python
cursor.execute("""
    SELECT p.*, i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
# agrupar em memória por pedido_id
```

---

## 7. Deprecated API → Modern Equivalent

**Before:**
```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
if t.due_date < datetime.utcnow():
```

**After:**
```python
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

created_at = db.Column(db.DateTime, default=utcnow)
if t.due_date.replace(tzinfo=timezone.utc) < utcnow():
```

**Before (Node callbacks):**
```javascript
db.get(sql, [], (err, row) => { db.run(..., () => { res.json(...) }) })
```

**After:**
```javascript
const { promisify } = require('util');
const get = promisify(db.get.bind(db));
const run = promisify(db.run.bind(db));
const row = await get(sql, params);
```

---

## 8. Error Handling Centralizado

**Before:**
```python
except:
    return jsonify({'error': 'Erro interno'}), 500
```

**After:**
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception(err)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"erro": "Não encontrado", "sucesso": False}), 404
```

---

## 9. Remover Backdoors / Proteger Admin

**Before:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(dados.get("sql", ""))  # SQL arbitrário
```

**After:** remover o endpoint **ou** exigir auth admin + allowlist de statements
somente leitura. Preferir remoção em refatoração de segurança.

---

## 10. Mover Recursos Misplaced + Wire Services

**Before:** CRUD `/categories` dentro de `report_routes.py`; `NotificationService`
nunca importado.

**After:**
- `views/category_routes.py` + `controllers/category_controller.py`
- Controller de tasks chama `notification_service.notify_task_assigned` após
  create/assign
- Remover imports mortos e deps não usadas (ou passar a usá-las de fato)

---

## Ordem sugerida de aplicação

1. Config + secrets
2. SQL injection / crypto
3. Split MVC / god class
4. N+1 e duplicação
5. Deprecated APIs
6. Error middleware
7. Validação (boot + endpoints)
