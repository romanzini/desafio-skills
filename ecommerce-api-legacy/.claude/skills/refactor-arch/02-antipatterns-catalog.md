# 02 — Catálogo de Anti-Patterns

Referência para a Fase 2 — Auditoria. Cada anti-pattern inclui: definição, sinais de detecção por linguagem, severidade e recomendação.

---

## CRITICAL

### AP-01 — SQL Injection

**Definição:** Queries SQL construídas por concatenação de strings com dados do usuário, permitindo injeção de código malicioso.

**Severidade:** CRITICAL

**Sinais de detecção:**

Python:
```python
# DETECTAR: concatenação de string em execute()
cursor.execute("SELECT * FROM tabela WHERE id = " + str(id))
cursor.execute("SELECT * FROM tabela WHERE nome = '" + nome + "'")
cursor.execute(f"SELECT * FROM tabela WHERE email = '{email}'")
query = "SELECT * FROM tabela WHERE 1=1"
query += " AND nome LIKE '%" + termo + "%'"  # query dinâmica com concatenação
cursor.execute(query)
```

Node.js:
```javascript
// DETECTAR: template strings ou concatenação em queries
db.run(`DELETE FROM tabela WHERE id = ${id}`)
db.get("SELECT * FROM tabela WHERE email = '" + email + "'")
```

**Impacto:** Permite leitura, modificação ou destruição de dados. Bypass de autenticação.

**Recomendação:** Usar queries parametrizadas (placeholders `?` ou `%s`).

---

### AP-02 — Credenciais Hardcoded

**Definição:** Senhas, chaves de API, tokens ou secrets embutidos diretamente no código-fonte.

**Severidade:** CRITICAL

**Sinais de detecção:**

Python:
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"  # DETECTAR
DB_PASSWORD = "senha_prod_123"  # DETECTAR
API_KEY = "pk_live_abcdef1234"  # DETECTAR
self.email_password = 'senha123'  # DETECTAR
```

Node.js:
```javascript
const config = {
    dbPass: "senha_super_secreta_prod_123",  // DETECTAR
    paymentGatewayKey: "pk_live_1234567890abcdef",  // DETECTAR
}
```

**Impacto:** Exposição de credenciais no histórico do Git. Comprometimento de sistemas externos.

**Recomendação:** Mover para variáveis de ambiente (`.env` + `python-dotenv` / `dotenv`).

---

### AP-03 — Endpoint Sem Autenticação / Acesso Irrestrito

**Definição:** Endpoints administrativos, destrutivos ou sensíveis acessíveis sem autenticação.

**Severidade:** CRITICAL

**Sinais de detecção:**

Python/Flask:
```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():  # DETECTAR: sem verificação de token/sessão

@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = dados.get("sql", "")
    cursor.execute(query)  # DETECTAR: execução livre de SQL + sem auth
```

**Impacto:** Qualquer usuário pode deletar dados, executar SQL arbitrário ou acessar informações privilegiadas.

**Recomendação:** Implementar middleware de autenticação/autorização antes dos handlers.

---

### AP-04 — God Class / God Method

**Definição:** Classe ou módulo que concentra responsabilidades de múltiplas camadas (banco de dados, lógica de negócio, roteamento, formatação) em um único lugar.

**Severidade:** CRITICAL

**Sinais de detecção:**

Python (arquivo único com tudo):
```python
# DETECTAR: arquivo com imports de flask + sqlite3 + lógica de negócio
from flask import Flask, request, jsonify
import sqlite3
# ... rota + query + lógica tudo junto
```

Node.js (classe com tudo):
```javascript
class AppManager {
    constructor() { this.db = ... }     // banco
    initDb() { ... }                    // schema
    setupRoutes(app) {                  // rotas
        app.post('/checkout', (req, res) => {
            this.db.run(...)            // query
            // lógica de pagamento     // negócio
        })
    }
}
```

**Impacto:** Impossível testar em isolamento. Qualquer mudança pode afetar todo o sistema.

**Recomendação:** Separar em Models (dados), Controllers (fluxo) e Services (negócio).

---

## HIGH

### AP-05 — Lógica de Negócio no Controller/Route Handler

**Definição:** Regras de negócio, cálculos ou decisões complexas dentro de funções de rota ou controllers, em vez de em Services ou Models.

**Severidade:** HIGH

**Sinais de detecção:**

Python (Route handler com mais de 30 linhas de lógica):
```python
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    # DETECTAR: validação complexa, cálculo de desconto,
    # verificação de estoque, lógica de notificação
    # tudo dentro do handler
    for item in itens:
        if produto['estoque'] < item['quantidade']:  # regra de negócio
            ...
        total += produto['preco'] * item['quantidade']  # cálculo
```

Node.js:
```javascript
app.post('/checkout', (req, res) => {
    // DETECTAR: processamento de pagamento, criação de usuário,
    // matrícula, log de auditoria tudo dentro do callback de rota
})
```

**Impacto:** Impossível reutilizar a lógica. Difícil de testar. Viola SRP.

**Recomendação:** Extrair para classes/funções de Service ou métodos de Model.

---

### AP-06 — Estado Global Mutável

**Definição:** Variáveis globais ou de módulo que são modificadas em tempo de execução e compartilhadas entre requisições.

**Severidade:** HIGH

**Sinais de detecção:**

Python:
```python
db_connection = None  # DETECTAR: global mutável
# ... sendo modificada dentro de funções
global db_connection
db_connection = sqlite3.connect(...)
```

Node.js:
```javascript
let globalCache = {};    // DETECTAR: mutável e compartilhado
let totalRevenue = 0;   // DETECTAR: estado de aplicação global
module.exports = { globalCache, totalRevenue }  // exportado = compartilhado
```

**Impacto:** Race conditions em ambientes com múltiplas requisições. Dados stale entre requisições.

**Recomendação:** Usar injeção de dependência, connection pools ou gerenciadores de contexto.

---

### AP-07 — Exposição de Dados Sensíveis na Resposta

**Definição:** Dados confidenciais (senhas, hashes, chaves) incluídos na serialização padrão de objetos retornados pela API.

**Severidade:** HIGH

**Sinais de detecção:**

Python:
```python
def to_dict(self):
    return {
        'password': self.password,  # DETECTAR: hash de senha na resposta
        'secret_key': app.config['SECRET_KEY'],  # DETECTAR
    }
```

Também detectar em health checks:
```python
return jsonify({
    "secret_key": "minha-chave-super-secreta-123"  # DETECTAR
})
```

**Impacto:** Vazamento de hashes de senha, chaves e dados internos para qualquer cliente.

**Recomendação:** Criar serialização explícita que exclui campos sensíveis. Nunca incluir `password` em `to_dict()`.

---

### AP-08 — Cascade Deletion Não Tratada

**Definição:** Deleção de entidades pai sem tratar as entidades filhas relacionadas, deixando dados órfãos.

**Severidade:** HIGH

**Sinais de detecção:**

Node.js:
```javascript
app.delete('/api/users/:id', (req, res) => {
    db.run("DELETE FROM users WHERE id = ?", [id])
    // DETECTAR: sem deletar enrollments, payments, etc.
    // até o próprio código comenta o problema
    res.send("...as matrículas ficaram sujos no banco.")
})
```

Python:
```python
cursor.execute("DELETE FROM usuarios WHERE id = " + str(id))
# DETECTAR: sem tratar pedidos, itens_pedido relacionados
```

**Impacto:** Integridade referencial corrompida. Queries futuras retornam dados inconsistentes.

**Recomendação:** Usar foreign key constraints com CASCADE, ou deletar entidades filhas explicitamente antes.

---

## MEDIUM

### AP-09 — N+1 Queries

**Definição:** Para cada registro de uma consulta principal, são feitas N consultas adicionais ao banco, resultando em N+1 queries no total.

**Severidade:** MEDIUM

**Sinais de detecção:**

Python:
```python
rows = cursor.fetchall()  # Query 1: busca todos os pedidos
for row in rows:          # Para CADA pedido...
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))  # +1 query
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))  # +1 query
```

SQLAlchemy:
```python
users = User.query.all()   # Query 1
for u in users:
    task_count = Task.query.filter_by(user_id=u.id).all()  # DETECTAR: N queries adicionais
```

Node.js:
```javascript
courses.forEach(c => {
    db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
        enrollments.forEach(enr => {
            db.get("SELECT name FROM users WHERE id = ?", [enr.user_id], ...)  // DETECTAR
        })
    })
})
```

**Impacto:** Degrada performance significativamente com volume de dados. Pode tornar endpoints lentos.

**Recomendação:** Usar JOINs, eager loading, ou queries com IN().

---

### AP-10 — Ausência de Error Handling Centralizado

**Definição:** Erros tratados de forma inconsistente (ou não tratados) em cada rota, sem middleware centralizado.

**Severidade:** MEDIUM

**Sinais de detecção:**

Python (try/except bare):
```python
except:          # DETECTAR: bare except sem tipo
    return jsonify({'error': 'Erro interno'}), 500
```

Node.js (sem middleware de erro):
```javascript
// DETECTAR: ausência de app.use((err, req, res, next) => { ... })
// Erros retornando strings simples em vez de JSON
res.status(500).send("Erro DB")  // DETECTAR: resposta não padronizada
```

**Impacto:** Respostas de erro inconsistentes. Erros internos vazando para o cliente. Difícil debugar.

**Recomendação:** Implementar middleware de error handling centralizado que padroniza respostas de erro.

---

### AP-11 — Callback Hell / Deeply Nested Callbacks

**Definição:** Callbacks aninhados em múltiplos níveis, tornando o código ilegível e impossível de manter.

**Severidade:** MEDIUM

**Sinais de detecção:**

Node.js (mais de 3 níveis de aninhamento):
```javascript
db.get(..., (err, result) => {
    db.get(..., (err, result2) => {
        db.run(..., function(err) {
            db.run(..., function(err) {
                db.run(..., (err) => {  // DETECTAR: 5+ níveis
                    res.json(...)
                })
            })
        })
    })
})
```

**Impacto:** Código ilegível. Difícil de testar e manter. Propenso a erros de lógica assíncrona.

**Recomendação:** Refatorar para async/await ou Promises encadeadas.

---

### AP-12 — APIs Deprecated

**Definição:** Uso de métodos, funções ou APIs que foram marcados como obsoletos na versão atual do framework/biblioteca.

**Severidade:** MEDIUM

**Sinais de detecção:**

SQLAlchemy 2.0+:
```python
# DETECTAR: Query.get() foi removido no SQLAlchemy 2.0
Task.query.get(task_id)    # deprecated
User.query.get(user_id)    # deprecated
# Correto:
db.session.get(Task, task_id)
db.session.get(User, user_id)
```

Flask (versões antigas):
```python
# DETECTAR: uso de before_first_request (removido no Flask 2.3+)
@app.before_first_request
def setup(): ...
```

Node.js / Express:
```javascript
// DETECTAR: res.json() sendo usado incorretamente
// bodyParser separado (integrado no Express 4.16+)
const bodyParser = require('body-parser')  // deprecated para JSON/URL-encoded simples
app.use(bodyParser.json())  // substituir por app.use(express.json())
```

**Impacto:** Pode quebrar em upgrades de versão. Funcionalidade pode ser removida sem aviso.

**Recomendação:** Atualizar para API equivalente moderna conforme documentação oficial.

---

## LOW

### AP-13 — Código Duplicado (DRY Violation)

**Definição:** Mesma lógica ou bloco de código repetido em múltiplos lugares sem abstração.

**Severidade:** LOW

**Sinais de detecção:**
```python
# DETECTAR: mesmo bloco de código em 3+ lugares
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
# ... repetido em get_tasks(), get_task(), task_stats(), get_user_tasks()
```

**Impacto:** Manutenção custosa — mudança precisa ser feita em N lugares. Inconsistências emergem.

**Recomendação:** Extrair para método utilitário ou método do Model.

---

### AP-14 — Nomenclatura Ruim / Magic Numbers

**Definição:** Variáveis com nomes de uma letra, abreviações obscuras, ou valores numéricos/string sem contexto.

**Severidade:** LOW

**Sinais de detecção:**

Node.js:
```javascript
let u = req.body.usr;   // DETECTAR: uma letra
let e = req.body.eml;   // DETECTAR
let p = req.body.pwd;   // DETECTAR
let cid = req.body.c_id;  // DETECTAR: abreviação sem contexto
let cc = req.body.card;   // DETECTAR
```

Python:
```python
if faturamento > 10000:   # DETECTAR: magic number sem nome
    desconto = faturamento * 0.1   # DETECTAR: magic number (10%)
elif faturamento > 5000:  # DETECTAR
    desconto = faturamento * 0.05  # DETECTAR
```

**Impacto:** Baixa legibilidade. Difícil entender a intenção do código.

**Recomendação:** Usar nomes descritivos. Extrair magic numbers para constantes nomeadas.

---

### AP-15 — Imports Desnecessários / Código Morto

**Definição:** Imports não utilizados, variáveis declaradas mas nunca usadas, ou código comentado.

**Severidade:** LOW

**Sinais de detecção:**

Python:
```python
import os, sys, json, datetime  # DETECTAR: verificar quais são realmente usados
```

Node.js:
```javascript
const { config, logAndCache, badCrypto, totalRevenue } = require('./utils')
// DETECTAR: verificar se totalRevenue é realmente usado
```

**Impacto:** Poluição do namespace. Dependências desnecessárias carregadas. Confusão sobre o que está em uso.

**Recomendação:** Remover imports não utilizados. Ativar linter com regra `no-unused-vars`.

---

### AP-16 — Criptografia Fraca / Insegura

**Definição:** Uso de algoritmos de hash inadequados para senhas (MD5, SHA1) ou implementações de crypto caseiras sem segurança.

**Severidade:** LOW (pode ser CRITICAL dependendo do contexto)

**Sinais de detecção:**

Python:
```python
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()  # DETECTAR: MD5 para senha
self.password = hashlib.sha1(pwd.encode()).hexdigest() # DETECTAR: SHA1 para senha
```

Node.js:
```javascript
function badCrypto(pwd) {  // DETECTAR: nome já indica o problema
    hash += Buffer.from(pwd).toString('base64')  // DETECTAR: base64 não é hash
}
```

**Impacto:** Senhas vulneráveis a rainbow tables e brute force. MD5/SHA1 são computacionalmente baratos para atacantes.

**Recomendação:** Usar `bcrypt` (Python: `bcryptpy`, Node.js: `bcrypt`) ou `argon2`.

> **Nota sobre severidade:** Se o sistema é de produção com dados reais, elevar para HIGH ou CRITICAL.
