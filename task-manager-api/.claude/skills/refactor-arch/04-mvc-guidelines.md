# 04 — Guidelines de Arquitetura MVC

Regras do padrão MVC alvo para a Fase 3 — Refatoração. Adapte à linguagem e framework detectados.

---

## 1. Visão Geral do Padrão MVC

```
Request → Routes → Controller → Service (opcional) → Model → DB
                      ↓
                   Response
```

| Camada | Responsabilidade | O que NÃO deve fazer |
|--------|-----------------|---------------------|
| **Config** | Carregar variáveis de ambiente, configurar app | Lógica de negócio, queries |
| **Models** | Definir estrutura de dados, operações de persistência | Lógica de rota, formatação de resposta HTTP |
| **Controllers** | Orquestrar requisição → model → resposta | Queries SQL diretas, lógica de negócio complexa |
| **Routes/Views** | Registrar rotas e associar controllers | Qualquer lógica além de `router.get('/path', controller.method)` |
| **Services** (opcional) | Lógica de negócio reutilizável | Operações de banco diretas, contexto HTTP |
| **Middlewares** | Autenticação, logging, error handling | Lógica de negócio |

---

## 2. Estrutura de Diretórios Alvo

### Python/Flask

```
src/
├── config/
│   └── settings.py          # Todas as configurações, variáveis de ambiente
├── models/
│   ├── __init__.py
│   ├── produto_model.py      # Um arquivo por entidade
│   └── usuario_model.py
├── controllers/
│   ├── __init__.py
│   ├── produto_controller.py
│   └── usuario_controller.py
├── routes/
│   ├── __init__.py
│   └── api_routes.py         # Registro das rotas
├── middlewares/
│   └── error_handler.py      # Error handling centralizado
└── app.py                    # Entry point — composition root
```

### Node.js/Express

```
src/
├── config/
│   └── settings.js
├── models/
│   ├── userModel.js
│   └── courseModel.js
├── controllers/
│   ├── userController.js
│   └── courseController.js
├── routes/
│   └── index.js              # ou routes separadas por domínio
├── middlewares/
│   └── errorHandler.js
└── app.js                    # Entry point
```

---

## 3. Regras por Camada

### 3.1 Config (`config/settings.py` ou `config/settings.js`)

**Deve conter:**
- Leitura de variáveis de ambiente com `os.getenv()` (Python) ou `process.env` (Node.js)
- Valores default para desenvolvimento (nunca produção)
- URI do banco de dados
- SECRET_KEY, porta, etc.

**Python:**
```python
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
```

**Node.js:**
```javascript
module.exports = {
    secretKey: process.env.SECRET_KEY || 'dev-key-change-in-production',
    dbPath: process.env.DB_PATH || ':memory:',
    port: process.env.PORT || 3000,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

---

### 3.2 Models

**Deve conter:**
- Definição da estrutura de dados (campos, tipos)
- Operações CRUD básicas (create, read, update, delete)
- Queries parametrizadas (nunca concatenação de strings)
- Validações de dados de nível de persistência

**NÃO deve conter:**
- Lógica de negócio (cálculo de descontos, regras de fluxo)
- Imports de Flask/Express (request, response)
- Envio de notificações ou efeitos colaterais externos

**Python (SQLite direto):**
```python
# models/produto_model.py
from config.settings import get_db

class ProdutoModel:
    @staticmethod
    def get_by_id(produto_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        return cursor.fetchone()

    @staticmethod
    def create(nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        db.commit()
        return cursor.lastrowid
```

**Python (SQLAlchemy):**
```python
# models/user.py
from database import db
import bcrypt

class User(db.Model):
    # ... campos ...

    def set_password(self, pwd):
        self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

    def check_password(self, pwd):
        return bcrypt.checkpw(pwd.encode(), self.password.encode())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            # NUNCA incluir 'password' aqui
        }
```

**Node.js:**
```javascript
// models/userModel.js
const db = require('../config/database');

const UserModel = {
    findByEmail: (email) => new Promise((resolve, reject) => {
        db.get("SELECT id, name, email, role FROM users WHERE email = ?", [email],
            (err, row) => err ? reject(err) : resolve(row));
    }),
    create: (name, email, hashedPassword) => new Promise((resolve, reject) => {
        db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, hashedPassword],
            function(err) { err ? reject(err) : resolve(this.lastID); });
    }),
};
module.exports = UserModel;
```

---

### 3.3 Controllers

**Deve conter:**
- Leitura e validação dos dados da requisição
- Chamada ao Model ou Service
- Formatação e retorno da resposta HTTP
- Tratamento de erros de fluxo (not found, validation errors)

**NÃO deve conter:**
- Queries SQL diretas
- Lógica de negócio complexa (extrair para Services se necessário)
- Múltiplas responsabilidades de domínio

**Python:**
```python
# controllers/produto_controller.py
from flask import request, jsonify
from models.produto_model import ProdutoModel

def listar_produtos():
    try:
        produtos = ProdutoModel.get_all()
        return jsonify({"dados": produtos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def buscar_produto(produto_id):
    produto = ProdutoModel.get_by_id(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"dados": dict(produto), "sucesso": True}), 200
```

**Node.js:**
```javascript
// controllers/checkoutController.js
const CourseModel = require('../models/courseModel');
const UserModel = require('../models/userModel');
const PaymentService = require('../services/paymentService');

const checkout = async (req, res, next) => {
    try {
        const { userName, email, courseId, cardNumber } = req.body;
        if (!userName || !email || !courseId || !cardNumber) {
            return res.status(400).json({ error: 'Campos obrigatórios faltando' });
        }
        const result = await PaymentService.processCheckout({ userName, email, courseId, cardNumber });
        return res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        next(err);
    }
};
module.exports = { checkout };
```

---

### 3.4 Routes/Views

**Deve conter:**
- Apenas declaração de rotas e associação com controllers
- Criação de Blueprint (Flask) ou Router (Express)

**NÃO deve conter:**
- Lógica além do registro de rotas

**Python:**
```python
# routes/produto_routes.py
from flask import Blueprint
from controllers import produto_controller

produto_bp = Blueprint('produtos', __name__)

produto_bp.route('/produtos', methods=['GET'])(produto_controller.listar_produtos)
produto_bp.route('/produtos/<int:id>', methods=['GET'])(produto_controller.buscar_produto)
produto_bp.route('/produtos', methods=['POST'])(produto_controller.criar_produto)
produto_bp.route('/produtos/<int:id>', methods=['PUT'])(produto_controller.atualizar_produto)
produto_bp.route('/produtos/<int:id>', methods=['DELETE'])(produto_controller.deletar_produto)
```

**Node.js:**
```javascript
// routes/checkoutRoutes.js
const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

router.post('/checkout', checkoutController.checkout);
module.exports = router;
```

---

### 3.5 Middlewares

**Error Handler centralizado (obrigatório):**

Python:
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"erro": str(e), "sucesso": False}), 500
```

Node.js:
```javascript
// middlewares/errorHandler.js
const errorHandler = (err, req, res, next) => {
    console.error(err.stack);
    res.status(err.status || 500).json({
        error: err.message || 'Erro interno do servidor',
    });
};
module.exports = errorHandler;
```

---

### 3.6 Entry Point (`app.py` ou `app.js`)

**Deve conter:**
- Criação da instância da aplicação
- Carregamento de configurações
- Registro de blueprints/routers
- Registro de middlewares
- Ponto de inicialização (`app.run()` ou `app.listen()`)

**NÃO deve conter:**
- Definições de rotas
- Lógica de negócio
- Queries de banco

**Python:**
```python
# app.py — Composition root
from flask import Flask
from config.settings import Config
from database import init_db
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    register_error_handlers(app)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
```

---

## 4. Adaptar ao contexto do projeto

Se o projeto já tem separação parcial, **melhore** a estrutura existente:
- Se já tem `models/`: mantenha, mas corrija as responsabilidades
- Se já usa Blueprints (Flask): mantenha, mas crie controllers separados
- Se já tem `routes/`: mantenha, mas extraia lógica para controllers

Não remova estrutura que já está correta — apenas corrija o que está errado.
