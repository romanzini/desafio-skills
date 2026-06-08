# 05 — Playbook de Refatoração

Padrões concretos de transformação para cada anti-pattern. Use na Fase 3. Cada padrão tem exemplo antes/depois com código real.

---

## PT-01 — SQL Injection → Queries Parametrizadas

**Anti-pattern alvo:** AP-01

### Antes (Python — concatenação de string)
```python
# INSEGURO: concatenação direta
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")

query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND nome LIKE '%" + termo + "%'"
cursor.execute(query)
```

### Depois (Python — placeholders)
```python
# SEGURO: parâmetros vinculados
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))

query = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    query += " AND nome LIKE ?"
    params.append(f"%{termo}%")
cursor.execute(query, params)
```

### Antes (Node.js — template string)
```javascript
db.run(`DELETE FROM users WHERE id = ${id}`)
db.get("SELECT * FROM users WHERE email = '" + email + "'")
```

### Depois (Node.js — placeholders)
```javascript
db.run("DELETE FROM users WHERE id = ?", [id])
db.get("SELECT * FROM users WHERE email = ?", [email])
```

---

## PT-02 — Credenciais Hardcoded → Variáveis de Ambiente

**Anti-pattern alvo:** AP-02

### Antes (Python)
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
self.email_password = 'senha123'
```

### Depois (Python)
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-CHANGE-IN-PRODUCTION')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# app.py
app.config.from_object(Config)
```

Criar `.env.example` (nunca `.env` com valores reais no repositório):
```
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
EMAIL_PASSWORD=your-email-password
DATABASE_URL=sqlite:///app.db
```

### Antes (Node.js)
```javascript
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

### Depois (Node.js)
```javascript
// config/settings.js
module.exports = {
    dbPass: process.env.DB_PASSWORD || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    port: parseInt(process.env.PORT) || 3000,
};
```

---

## PT-03 — God Class → Separação MVC

**Anti-pattern alvo:** AP-04

### Antes (Python — tudo em um arquivo)
```python
# app.py — God File
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/produtos')
def produtos():
    conn = sqlite3.connect('loja.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    # ... lógica de formatação, regras de negócio...
    return jsonify(rows)
```

### Depois (Python — separado em camadas)
```python
# models/produto_model.py
class ProdutoModel:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [dict(row) for row in cursor.fetchall()]

# controllers/produto_controller.py
from models.produto_model import ProdutoModel
from flask import jsonify

def listar_produtos():
    produtos = ProdutoModel.get_all()
    return jsonify({"dados": produtos, "sucesso": True}), 200

# routes/produto_routes.py
from flask import Blueprint
from controllers import produto_controller
produto_bp = Blueprint('produtos', __name__)
produto_bp.route('/produtos', methods=['GET'])(produto_controller.listar_produtos)

# app.py
from routes.produto_routes import produto_bp
app.register_blueprint(produto_bp)
```

### Antes (Node.js — classe com tudo)
```javascript
class AppManager {
    constructor() { this.db = new sqlite3.Database(':memory:') }
    initDb() { /* schema + seeds */ }
    setupRoutes(app) {
        app.post('/checkout', (req, res) => {
            // query + lógica de pagamento + criação de usuário + log
        })
    }
}
```

### Depois (Node.js — separado em camadas)
```javascript
// models/courseModel.js
const CourseModel = { findById: (id) => new Promise(...) }

// services/paymentService.js
const PaymentService = { processCheckout: async ({ userId, courseId, cardNumber }) => { ... } }

// controllers/checkoutController.js
const checkout = async (req, res, next) => {
    try {
        const result = await PaymentService.processCheckout(req.body)
        res.json({ msg: 'Sucesso', ...result })
    } catch (err) { next(err) }
}

// routes/checkoutRoutes.js
router.post('/checkout', checkoutController.checkout)
```

---

## PT-04 — Senha em Texto Plano / Hash Fraco → bcrypt

**Anti-pattern alvo:** AP-16

### Antes (Python — MD5)
```python
import hashlib
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()  # INSEGURO

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

### Depois (Python — bcrypt)
```python
# Instalar: pip install bcrypt
import bcrypt

def set_password(self, pwd):
    self.password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(self, pwd):
    return bcrypt.checkpw(pwd.encode('utf-8'), self.password.encode('utf-8'))
```

### Antes (Node.js — badCrypto)
```javascript
function badCrypto(pwd) {
    let hash = ""
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2)
    }
    return hash.substring(0, 10)  // NÃO é um hash seguro
}
```

### Depois (Node.js — bcrypt)
```javascript
// npm install bcrypt
const bcrypt = require('bcrypt')
const SALT_ROUNDS = 10

async function hashPassword(pwd) {
    return bcrypt.hash(pwd, SALT_ROUNDS)
}

async function verifyPassword(pwd, hash) {
    return bcrypt.compare(pwd, hash)
}
```

---

## PT-05 — N+1 Queries → JOIN ou Eager Loading

**Anti-pattern alvo:** AP-09

### Antes (Python — N+1 com cursores aninhados)
```python
cursor.execute("SELECT * FROM pedidos")
rows = cursor.fetchall()
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

### Depois (Python — JOIN único)
```python
cursor.execute("""
    SELECT p.*, ip.quantidade, ip.preco_unitario, pr.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
""")
rows = cursor.fetchall()
# Agrupar em Python:
pedidos = {}
for row in rows:
    pid = row['id']
    if pid not in pedidos:
        pedidos[pid] = {
            'id': row['id'], 'status': row['status'],
            'total': row['total'], 'itens': []
        }
    if row['quantidade']:
        pedidos[pid]['itens'].append({
            'produto_nome': row['produto_nome'],
            'quantidade': row['quantidade'],
            'preco_unitario': row['preco_unitario']
        })
return list(pedidos.values())
```

### Antes (SQLAlchemy — N+1)
```python
users = User.query.all()
for u in users:
    tasks = Task.query.filter_by(user_id=u.id).all()  # N queries
```

### Depois (SQLAlchemy — joinedload)
```python
from sqlalchemy.orm import joinedload
users = User.query.options(joinedload(User.tasks)).all()
# tasks já estão carregadas, sem queries adicionais
```

---

## PT-06 — Callback Hell → async/await (Node.js)

**Anti-pattern alvo:** AP-11

### Antes (callback hell — 5 níveis)
```javascript
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    db.get("SELECT id FROM users WHERE email = ?", [email], (err, user) => {
        db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {
            db.run("INSERT INTO payments ...", [this.lastID, ...], function(err) {
                db.run("INSERT INTO audit_logs ...", [...], (err) => {
                    res.json({ msg: "Sucesso" })
                })
            })
        })
    })
})
```

### Depois (async/await + promisificação)
```javascript
const { promisify } = require('util')
// Ou usar biblioteca 'better-sqlite3' que é síncrona

async function checkout(req, res, next) {
    try {
        const course = await CourseModel.findActiveById(courseId)
        if (!course) return res.status(404).json({ error: 'Curso não encontrado' })

        const userId = await UserModel.findOrCreate(userName, email, password)
        const paymentStatus = await PaymentService.charge(cardNumber, course.price)
        if (paymentStatus === 'DENIED') return res.status(400).json({ error: 'Pagamento recusado' })

        const enrollmentId = await EnrollmentModel.create(userId, courseId)
        await PaymentModel.record(enrollmentId, course.price, paymentStatus)
        await AuditModel.log(`Checkout curso ${courseId} por ${userId}`)

        res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId })
    } catch (err) {
        next(err)
    }
}
```

---

## PT-07 — Error Handling Descentralizado → Middleware Centralizado

**Anti-pattern alvo:** AP-10

### Antes (Python — try/except bare em cada função)
```python
def listar_produtos():
    try:
        ...
    except:  # bare except
        return jsonify({'error': 'Erro interno'}), 500

def criar_produto():
    try:
        ...
    except Exception as e:
        print("ERRO: " + str(e))
        return jsonify({"erro": str(e)}), 500
```

### Depois (Python — error handlers registrados no app)
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

# app.py
from middlewares.error_handler import register_error_handlers
register_error_handlers(app)

# controllers — mais limpos, sem try/except boilerplate
def listar_produtos():
    produtos = ProdutoModel.get_all()
    return jsonify({"dados": produtos, "sucesso": True}), 200
```

### Antes (Node.js — sem middleware de erro)
```javascript
app.post('/checkout', (req, res) => {
    // sem try/catch, erros não tratados
    db.get("...", (err, row) => {
        if (err) return res.status(500).send("Erro DB")  // string, não JSON
    })
})
```

### Depois (Node.js — middleware centralizado)
```javascript
// middlewares/errorHandler.js
const errorHandler = (err, req, res, next) => {
    console.error(`[ERROR] ${err.message}`)
    res.status(err.status || 500).json({
        error: err.message || 'Erro interno do servidor',
    })
}
module.exports = errorHandler

// app.js (registrar DEPOIS de todas as rotas)
const errorHandler = require('./middlewares/errorHandler')
app.use(errorHandler)

// controllers — usar next(err) para propagar
const checkout = async (req, res, next) => {
    try { ... }
    catch (err) { next(err) }
}
```

---

## PT-08 — APIs Deprecated → APIs Modernas

**Anti-pattern alvo:** AP-12

### Antes (SQLAlchemy — Query.get() deprecated)
```python
# DEPRECATED no SQLAlchemy 2.0
task = Task.query.get(task_id)
user = User.query.get(user_id)
```

### Depois (SQLAlchemy — db.session.get())
```python
# CORRETO para SQLAlchemy 2.0+
task = db.session.get(Task, task_id)
user = db.session.get(User, user_id)
```

### Antes (Node.js — bodyParser separado)
```javascript
const bodyParser = require('body-parser')
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }))
```

### Depois (Express 4.16+ — built-in)
```javascript
app.use(express.json())
app.use(express.urlencoded({ extended: true }))
```

---

## PT-09 — Dados Sensíveis na Resposta → Serialização Explícita

**Anti-pattern alvo:** AP-07

### Antes (Python — password no to_dict())
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,  # REMOVIDO
        'role': self.role,
    }
```

### Depois (Python — sem campos sensíveis)
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'role': self.role,
        'active': self.active,
        'created_at': str(self.created_at),
        # 'password' NUNCA incluído
    }
```

### Health check sem exposição de secrets
```python
# Antes (INSEGURO)
return jsonify({
    "secret_key": "minha-chave-super-secreta-123",  # REMOVER
    "db_path": "loja.db",
    "debug": True,
})

# Depois (seguro)
return jsonify({
    "status": "ok",
    "version": "1.0.0",
    "database": "connected",
    "timestamp": datetime.utcnow().isoformat(),
})
```

---

## PT-10 — Código Duplicado → Extração para Método/Função

**Anti-pattern alvo:** AP-13

### Antes (Python — lógica de overdue repetida 4+ vezes)
```python
# Em get_tasks(), get_task(), task_stats(), user_tasks() — REPETIDO:
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
        else:
            task_data['overdue'] = False
    else:
        task_data['overdue'] = False
else:
    task_data['overdue'] = False
```

### Depois (Python — extraído para método do Model)
```python
# models/task.py — método já existente, mas não estava sendo usado:
def is_overdue(self):
    if self.due_date and self.due_date < datetime.utcnow():
        return self.status not in ['done', 'cancelled']
    return False

# routes/task_routes.py — uso consistente:
task_data['overdue'] = t.is_overdue()
```
