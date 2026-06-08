================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + SQLAlchemy 3.1.1
Files:   10 analyzed (app.py, database.py, models/*.py, routes/*.py, services/*.py, utils/*.py) | ~600 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Hash de Senha com MD5 — Algoritmo Criptograficamente Inseguro
File: models/user.py:29, 32
Description: Metodos set_password() e check_password() usam hashlib.md5 para hash de senhas: `self.password = hashlib.md5(pwd.encode()).hexdigest()`. MD5 e uma funcao de hash criptografico, nao um KDF (Key Derivation Function). Nao tem salt, e computacionalmente trivial de inverter com rainbow tables.
Impact: Banco de dados comprometido expoe todas as senhas em segundos via rainbow tables pre-computadas. MD5 e considerado quebrado para uso criptografico desde 2004.
Recommendation: Substituir por `werkzeug.security.generate_password_hash()` (PBKDF2-SHA256 com salt automatico). Ja disponivel como dependencia do Flask. Requer migracao dos hashes existentes.

### [CRITICAL] Credencial de Email Hardcoded no Servico de Notificacao
File: services/notification_service.py:10
Description: Senha de email armazenada como literal: `self.email_password = 'senha123'`. A credencial e carregada na instanciacao da classe, tornando-a visivel em qualquer traceback ou dump de objeto.
Impact: Qualquer pessoa com acesso ao repositorio obtem acesso a conta de email. Se a conta for de producao, pode comprometer comunicacoes com usuarios.
Recommendation: Usar `os.getenv('EMAIL_PASSWORD', '')` em vez de literal hardcoded. Adicionar ao .env.example.

### [CRITICAL] Login Retorna Token Falso Sem Valor de Seguranca
File: routes/user_routes.py:210
Description: O endpoint POST /login retorna `'token': 'fake-jwt-token-' + str(user.id)`. Este token e apenas o ID do usuario prefixado com texto fixo, sem assinatura criptografica. Qualquer endpoint que aceite este token como autenticacao pode ser bypassado trivialmente.
Impact: Autenticacao completamente ineficaz. Qualquer usuario pode se passar por qualquer outro usuario construindo o token manualmente.
Recommendation: Usar `itsdangerous.URLSafeTimedSerializer` (bundled com Flask) para gerar tokens assinados com o SECRET_KEY, ou implementar JWT via flask-jwt-extended.

### [HIGH] Senha (Hash) Exposta em to_dict() do Model User
File: models/user.py:21
Description: O metodo to_dict() inclui explicitamente `'password': self.password` na serializacao. Como qualquer endpoint GET /users ou GET /users/:id chama to_dict(), o hash de senha e retornado para todos os clientes da API.
Impact: Mesmo que o hash seja seguro, expor o hash permite ataques de dicionario offline. Em combinacao com o MD5 (finding anterior), os hashes sao facilmente quebrados.
Recommendation: Remover o campo 'password' de to_dict(). Criar serializacao separada (to_admin_dict) se necessario para fins administrativos.

### [HIGH] API Deprecated: Query.get() em 5+ Locais
File: routes/task_routes.py:42, 52, 67, 117, 188; routes/user_routes.py:29, 94, 135, 155, 188; routes/report_routes.py:105
Description: Multiplas chamadas a `Task.query.get(id)` e `User.query.get(id)`. O metodo `Query.get()` foi depreciado no SQLAlchemy 1.4 e removido no SQLAlchemy 2.0. O projeto usa flask-sqlalchemy 3.1.1 que e baseado no SQLAlchemy 2.0.
Impact: As chamadas ainda funcionam via compatibilidade, mas podem quebrar em futuras atualizacoes do flask-sqlalchemy. O linter ja emite warnings sobre uso deprecated.
Recommendation: Substituir por `db.session.get(Model, id)`. Ex: `Task.query.get(task_id)` → `db.session.get(Task, task_id)`.

### [HIGH] Logica de Negocio no Route Handler (Calculo de Overdue + Resolucao de Nomes)
File: routes/task_routes.py:12-63 (get_tasks), routes/task_routes.py:153-183 (get_user_tasks)
Description: O handler get_tasks() contem: calculo de overdue (if t.due_date < datetime.utcnow()), resolucao de user_name (User.query.get(t.user_id)), resolucao de category_name (Category.query.get(t.category_id)), tudo inline no handler de rota. Cada chamada a User.query.get() e Category.query.get() dentro do loop cria N+1 queries.
Impact: Logica de negocio misturada com camada HTTP. get_tasks() com 50 tasks executa 150 queries (50 para users + 50 para categories). Impossivel reutilizar a logica.
Recommendation: Mover para controller com joinedload(Task.user) e joinedload(Task.category). Usar task.is_overdue() que ja existe no model.

### [MEDIUM] N+1 Queries no Summary Report
File: routes/report_routes.py:53-68
Description: A funcao summary_report() executa `User.query.all()` e depois para CADA usuario executa `Task.query.filter_by(user_id=u.id).all()`. Com N usuarios = N+1 queries totais.
Impact: Com 100 usuarios, sao 101 queries para um unico endpoint de relatorio.
Recommendation: Usar `User.query.options(joinedload(User.tasks)).all()` para carregar usuarios e tasks em 2 queries (1 SELECT users + 1 SELECT tasks WHERE user_id IN (...)).

### [MEDIUM] Bare Except e Exception Generica Que Engole Erros
File: routes/task_routes.py:62, 237
Description: Clausulas `except:` sem tipo e `except Exception as e:` sem logging adequado swallam todos os erros e retornam mensagens genericas: `return jsonify({'error': 'Erro interno'}), 500`. Erros de programacao (AttributeError, KeyError) sao silenciados.
Impact: Impossivel debugar problemas em producao. Erros criticos ficam invistiveis. Comportamento incorreto mascarado como "Erro interno".
Recommendation: Usar `except Exception as e: logger.error(f"Erro em {func}: {e}"); return jsonify(...)`. Nunca usar bare `except:`.

### [LOW] Logica de Overdue Duplicada em 4+ Locais
File: routes/task_routes.py:31-38, 71-80, 171-180, 282-287; routes/report_routes.py:33-43, 132-135
Description: O mesmo bloco de 6 linhas para calcular se uma task esta atrasada e repetido em pelo menos 6 lugares: `if t.due_date: if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled': overdue = True`. O model Task ja tem o metodo `is_overdue()` (linha 50) que encapsula essa logica, mas nenhum route o utiliza.
Impact: Manutencao custosa. Qualquer mudanca na regra de overdue precisa ser aplicada em 6 lugares. Inconsistencias ja existem entre as implementacoes.
Recommendation: Usar `t.is_overdue()` em todos os lugares. O metodo ja esta implementado corretamente no model.

### [LOW] Imports Nao Utilizados no app.py
File: app.py:7
Description: `import os, sys, json, datetime` — destes, apenas `datetime` e usado (na rota /health). Os outros (`os`, `sys`, `json`) sao importados mas nunca referenciados no arquivo.
Impact: Poluicao do namespace. Confusao sobre o que esta realmente em uso.
Recommendation: Remover imports nao utilizados: `import datetime` e suficiente.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
task-manager-api/
├── .claude/skills/refactor-arch/   (skill copiada)
├── config/
│   └── settings.py                 (NOVO - Config class com os.getenv())
├── controllers/                    (NOVO - logica extraida das routes)
│   ├── __init__.py
│   ├── task_controller.py          (NOVO - logica de task com joinedload + is_overdue())
│   ├── user_controller.py          (NOVO - token assinado com itsdangerous)
│   └── report_controller.py        (NOVO - N+1 fix com joinedload)
├── models/
│   ├── __init__.py
│   ├── task.py                     (sem alteracao - is_overdue() ja existia)
│   ├── user.py                     (ATUALIZADO - MD5→werkzeug, password removido de to_dict())
│   └── category.py                 (sem alteracao)
├── routes/                         (ATUALIZADO - thin wrappers delegando para controllers)
│   ├── __init__.py
│   ├── task_routes.py              (ATUALIZADO - apenas Blueprint + route decorators)
│   ├── user_routes.py              (ATUALIZADO - apenas Blueprint + route decorators)
│   └── report_routes.py            (ATUALIZADO - apenas Blueprint + route decorators)
├── services/
│   └── notification_service.py     (ATUALIZADO - credenciais via os.getenv)
├── utils/
│   └── helpers.py                  (sem alteracao)
├── app.py                          (ATUALIZADO - usa Config, imports limpos)
├── database.py                     (sem alteracao)
└── requirements.txt

## Changes Made
- Criado config/settings.py com todas as configuracoes via os.getenv()
- Criado controllers/ com task_controller, user_controller, report_controller
- Logica extraida de routes/ para controllers/ (routes agora sao thin wrappers)
- User.to_dict() corrigido: campo 'password' removido da serializacao publica
- User.set_password() e check_password() migrados para werkzeug.security (PBKDF2)
- Deprecated Query.get() substituido por db.session.get() em todos os controllers
- N+1 em get_tasks() corrigido com joinedload(Task.user) e joinedload(Task.category)
- N+1 em summary_report() corrigido com joinedload(User.tasks)
- Logica duplicada de overdue substituida por t.is_overdue() em todos os lugares
- Notificacao service: credencial movida para os.getenv('EMAIL_PASSWORD')
- Login: token fake substituido por token assinado com itsdangerous.URLSafeTimedSerializer
- app.py: imports desnecessarios (os, sys, json) removidos, Config importada

## Security Fixes
- CRITICAL MD5 password hashing: substituido por werkzeug PBKDF2-SHA256
- CRITICAL Hardcoded email password: movido para os.getenv('EMAIL_PASSWORD')
- CRITICAL Fake JWT: substituido por token assinado com URLSafeTimedSerializer
- HIGH Password exposed in API: campo 'password' removido de to_dict()

## Validation
  ✓ Application boots without errors
  ✓ All endpoints preserved (23 rotas registradas)
  ✓ Zero CRITICAL anti-patterns remaining
  ✓ Zero CRITICAL security issues remaining
================================
