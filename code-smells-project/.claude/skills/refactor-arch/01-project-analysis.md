# 01 — Análise de Projeto

Heurísticas para detectar linguagem, framework, banco de dados e arquitetura atual de qualquer codebase.

---

## 1. Detecção de Linguagem

| Sinal | Linguagem |
|-------|-----------|
| Arquivos `*.py` presentes | Python |
| Arquivos `*.js` ou `*.ts` com `package.json` | Node.js / JavaScript / TypeScript |
| Arquivos `*.java` com `pom.xml` ou `build.gradle` | Java |
| Arquivos `*.go` com `go.mod` | Go |
| Arquivos `*.rb` com `Gemfile` | Ruby |
| Arquivos `*.php` com `composer.json` | PHP |

**Ação:** Contar arquivos por extensão. A extensão dominante define a linguagem.

---

## 2. Detecção de Framework

### Python
| Sinal | Framework |
|-------|-----------|
| `from flask import Flask` ou `import flask` | Flask |
| `from django.` imports | Django |
| `from fastapi import FastAPI` | FastAPI |
| `requirements.txt` contém `flask` | Flask |
| `requirements.txt` contém `django` | Django |
| `requirements.txt` contém `fastapi` | FastAPI |

### Node.js
| Sinal | Framework |
|-------|-----------|
| `require('express')` ou `import express` | Express |
| `require('fastify')` | Fastify |
| `package.json` contém `"express"` em dependencies | Express |
| `package.json` contém `"@nestjs/core"` | NestJS |
| `package.json` contém `"koa"` | Koa |

### Versão do framework
- Python: `requirements.txt` lista a versão (ex: `flask==3.1.1`)
- Node.js: `package.json` em `dependencies` (ex: `"express": "^4.18.2"`)
- Se versão não está explícita, registre como "versão não especificada"

---

## 3. Detecção de Banco de Dados

| Sinal | Banco |
|-------|-------|
| `import sqlite3` ou `sqlite3.connect(` | SQLite |
| `require('sqlite3')` | SQLite |
| `psycopg2` ou `pg` | PostgreSQL |
| `pymysql` ou `mysql2` | MySQL |
| `from flask_sqlalchemy import SQLAlchemy` | SQLAlchemy ORM (banco depende da URI) |
| `SQLALCHEMY_DATABASE_URI = 'sqlite:///` | SQLite via SQLAlchemy |
| `SQLALCHEMY_DATABASE_URI = 'postgresql://` | PostgreSQL via SQLAlchemy |
| `:memory:` no connect | SQLite in-memory |
| `mongoose` | MongoDB |

**Mapeamento de tabelas/entidades:**
- Python/SQLite direto: procurar `CREATE TABLE` statements
- SQLAlchemy: procurar classes com `db.Model` ou `Base`
- Node.js/sqlite3: procurar `CREATE TABLE` em `db.run(` ou `db.serialize(`
- Mongoose: procurar `new Schema(` ou `mongoose.model(`

---

## 4. Detecção de Domínio da Aplicação

Leia os nomes das rotas, tabelas e funções para inferir o domínio:

| Padrão encontrado | Domínio provável |
|-------------------|-----------------|
| `produtos`, `pedidos`, `carrinho`, `checkout`, `pagamento` | E-commerce |
| `tasks`, `usuarios`, `categorias`, `prioridade` | Task Manager |
| `cursos`, `matriculas`, `alunos`, `aulas`, `enrollment` | LMS / Plataforma de ensino |
| `posts`, `comentarios`, `categorias`, `tags` | Blog / CMS |
| `pacientes`, `consultas`, `medicos`, `prescricoes` | Saúde |
| `funcionarios`, `departamentos`, `salarios` | RH |

---

## 5. Mapeamento de Arquitetura Atual

### 5.1 Identificar separação de camadas

**Monolito completo (sem camadas):**
- Tudo em 1-3 arquivos
- Queries SQL, rotas e lógica no mesmo arquivo
- Sem diretórios `models/`, `controllers/`, `routes/`

**Separação mínima:**
- Arquivo de rotas separado (ex: `routes.py`, `app.js`)
- Arquivo de modelos/queries (ex: `models.py`)
- Mas ainda com lógica de negócio misturada

**Separação parcial:**
- Diretórios `models/`, `routes/` presentes
- Mas sem `controllers/` explícito, ou com lógica de negócio nos route handlers
- Services podem existir mas não são usados corretamente

**MVC adequado:**
- `models/` — apenas dados e persistência
- `controllers/` — fluxo da requisição
- `views/` ou `routes/` — apenas roteamento
- `config/` — configurações externas
- Entry point limpo

### 5.2 Heurísticas de detecção de camadas

**Verificar se há Models:**
- Python: arquivos com classes herdando de `db.Model` ou funções que executam queries SQL
- Node.js: arquivos com `db.run(`, `db.get(`, `db.all(` ou ORM models

**Verificar se há Controllers:**
- Funções que chamam models E retornam respostas HTTP (`jsonify`, `res.json`)
- Se essas funções estão no mesmo arquivo das rotas: não há separação Controller/Route

**Verificar se há Services:**
- Classes ou módulos com lógica de negócio pura (sem request/response)
- Se lógica de negócio está nos Controllers: sem Service layer

**Verificar se há Config:**
- Arquivo separado para configurações (`config.py`, `settings.py`, `config.js`)
- Se `SECRET_KEY`, `DB_URI` ou credenciais estão no código principal: sem Config layer

### 5.3 Descrições de arquitetura para o relatório

Use estas descrições padronizadas na Fase 1:

- "Monolítica — tudo em N arquivo(s), sem separação de camadas"
- "Separação mínima — N arquivos sem estrutura de diretórios"
- "MVC parcial — models e routes separados, sem controllers"
- "MVC incompleto — estrutura de diretórios presente mas com responsabilidades misturadas"
- "MVC adequado — separação clara de Models, Controllers e Routes"

---

## 6. Contagem de arquivos fonte

**Incluir:**
- Python: `*.py` (exceto `__init__.py` vazios, arquivos de teste)
- Node.js: `*.js`, `*.ts` (exceto `*.test.js`, `*.spec.ts`, `node_modules/`)
- Arquivos de configuração relevantes: `requirements.txt`, `package.json`

**Excluir:**
- `node_modules/`
- `__pycache__/`
- `.git/`
- Arquivos de teste (`*_test.py`, `*.test.js`, `*.spec.ts`)
- Arquivos de build/dist

---

## 7. Checklist de análise completa

Antes de encerrar a Fase 1, verifique:

- [ ] Linguagem identificada com evidência (extensão de arquivo ou import)
- [ ] Framework identificado com evidência (import ou package.json)
- [ ] Versão do framework registrada (ou "não especificada")
- [ ] Banco de dados identificado
- [ ] Tabelas/entidades listadas
- [ ] Domínio de negócio descrito em uma frase
- [ ] Número de arquivos fonte contados
- [ ] Arquitetura atual descrita honestamente
