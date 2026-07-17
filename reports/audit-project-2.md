================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.18.2
Files:   3 analyzed | ~170 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials
File: src/utils.js:2-6
Description: Credenciais de DB, payment gateway (`pk_live_...`) e SMTP hardcoded no código-fonte.
Impact: Vazamento via VCS; risco PCI e acesso indevido a serviços externos.
Recommendation: Extrair para variáveis de ambiente (`PAYMENT_GATEWAY_KEY`, etc.) e usar chaves de teste por padrão.

### [CRITICAL] Credit Card Data Logged
File: src/AppManager.js:45
Description: Número completo do cartão e chave do gateway impressos no console.
Impact: Violação PCI-DSS; cartões em logs de aplicação.
Recommendation: Logar apenas últimos 4 dígitos; nunca logar PAN completo nem chaves.

### [CRITICAL] Insecure Password Storage (badCrypto)
File: src/utils.js:17-23
Description: Função `badCrypto` gera “hash” previsível por concatenação de base64 truncado.
Impact: Senhas reversíveis/adivináveis; falsa sensação de segurança.
Recommendation: Substituir por `crypto.scrypt`/`bcrypt` com salt.

### [CRITICAL] God Class
File: src/AppManager.js:4-139
Description: Classe única concentra schema DB, seed, checkout, relatório financeiro e delete de usuários.
Impact: Impossível evoluir ou testar camadas isoladamente.
Recommendation: Separar models, controllers, views/routes e services (payment).

### [HIGH] Account Takeover via Email-only Checkout
File: src/AppManager.js:66-75
Description: Se o email já existe, o checkout matricula o usuário sem validar senha.
Impact: Atacante matricula cursos em nome de terceiros conhecendo só o email.
Recommendation: Exigir autenticação (password check) para usuários existentes.

### [HIGH] Unprotected Financial Report
File: src/AppManager.js:80-128
Description: `/api/admin/financial-report` expõe receita e alunos sem autenticação.
Impact: Vazamento de dados financeiros e PII.
Recommendation: Proteger com auth admin (mínimo) e estruturar em controller dedicado.

### [HIGH] Callback Hell / Race-prone Aggregation
File: src/AppManager.js:89-122
Description: Relatório financeiro com callbacks aninhados e contadores manuais para `res.json`.
Impact: Respostas duplicadas/corrompidas sob timing adverso; código ilegível.
Recommendation: Promisificar sqlite3 e agregar com SQL JOIN/`GROUP BY`.

### [HIGH] Orphan Data on User Delete
File: src/AppManager.js:131-137
Description: Delete remove só o usuário; matrículas e pagamentos ficam órfãos (mensagem admite o problema).
Impact: Integridade referencial quebrada.
Recommendation: Cascata explícita (payments → enrollments → user) em transação.

### [MEDIUM] Global Mutable Cache
File: src/utils.js:9-14
Description: `globalCache` mutável compartilhado no módulo.
Impact: Estado oculto, vazamento de memória e testes não isolados.
Recommendation: Remover ou encapsular cache com TTL/DI.

### [MEDIUM] Cryptic API Field Names
File: src/AppManager.js:29-33
Description: Payload usa `usr`, `eml`, `pwd`, `c_id` sem documentação clara no contrato.
Impact: DX ruim e erros de integração.
Recommendation: Aceitar aliases legíveis (`name`, `email`, `password`, `course_id`) mantendo compatibilidade.

### [MEDIUM] Deprecated Pattern — Nested Callbacks
File: src/AppManager.js:37-76
Description: Fluxo assíncrono baseado apenas em callbacks sqlite3 aninhados.
Impact: Manutenção difícil; padrão obsoleto frente a async/await.
Recommendation: Wrappers Promise + async controllers.

### [LOW] Dead Import / Unused Revenue Counter
File: src/AppManager.js:2, src/utils.js:10
Description: `totalRevenue` importado e nunca usado de forma coerente.
Impact: Ruído e falsa lógica financeira.
Recommendation: Remover dead code.

### [LOW] Package Identity Mismatch
File: package.json:2
Description: Nome do pacote `desafio-arquitetura-ia-boilerplate` não reflete o domínio LMS.
Impact: Confusão operacional.
Recommendation: Renomear para identidade do serviço.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
