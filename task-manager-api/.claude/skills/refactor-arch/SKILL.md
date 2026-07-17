---
name: refactor-arch
description: >
  Analisa qualquer codebase backend, detecta linguagem/framework/arquitetura,
  audita anti-patterns MVC/SOLID com severidade (CRITICAL→LOW), gera relatório
  estruturado e, após confirmação humana, refatora para MVC validando boot e
  endpoints. Use quando o usuário pedir /refactor-arch, auditoria arquitetural,
  refatoração MVC, limpeza de code smells ou modernização de APIs legadas.
---

# Skill: refactor-arch

Você é um especialista em arquitetura de software focado em transformar backends
legados no padrão **MVC (Model–View–Controller)**, de forma **agnóstica de
tecnologia** (Python/Flask, Node.js/Express e equivalentes).

Antes de cada fase, leia os arquivos de referência nesta pasta:

| Arquivo | Quando usar |
|---|---|
| `project-analysis.md` | Fase 1 — heurísticas de stack e arquitetura |
| `anti-patterns-catalog.md` | Fase 2 — catálogo mínimo de 8 anti-patterns + APIs deprecated |
| `audit-report-template.md` | Fase 2 — formato obrigatório do relatório |
| `mvc-architecture-guidelines.md` | Fase 3 — responsabilidades das camadas MVC |
| `refactoring-playbook.md` | Fase 3 — transformações concretas before/after |

Execute **exatamente** nesta ordem. Não pule fases. Não modifique arquivos antes
da confirmação explícita do humano na Fase 2.

---

## PHASE 1: PROJECT ANALYSIS

1. Varra o diretório de trabalho (ignore `node_modules`, `.git`, `__pycache__`,
   `venv`, `.venv`, `dist`, `build`, `*.db`).
2. Aplique as heurísticas de `project-analysis.md` para detectar:
   - Linguagem e versão (se disponível)
   - Framework e versão
   - Dependências relevantes
   - Domínio da aplicação
   - Arquitetura atual (monolito flat, god class, camadas parciais, etc.)
   - Quantidade de arquivos-fonte analisados
   - Tabelas/coleções de banco (se houver)
3. Imprima o resumo neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <lang>
Framework:     <framework + version>
Dependencies:  <lista curta>
Domain:        <descrição do domínio>
Architecture:  <resumo da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas ou N/A>
================================
```

Só então avance para a Fase 2.

---

## PHASE 2: ARCHITECTURE AUDIT

1. Cruze o código contra **todos** os anti-patterns de
   `anti-patterns-catalog.md` (mínimo 8, severidades CRITICAL/HIGH/MEDIUM/LOW).
2. Inclua detecção de **APIs deprecated** (ex.: `datetime.utcnow()`, callbacks
   aninhados onde Promises/async existem, MD5 para senhas, etc.).
3. Para cada finding, registre: severidade, título, arquivo:linhas exatas,
   description, impact, recommendation.
4. Ordene findings por severidade: CRITICAL → HIGH → MEDIUM → LOW.
5. Gere o relatório seguindo `audit-report-template.md`.
6. **OBRIGATÓRIO:** pause e pergunte:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

7. Se a resposta não for afirmativa (`y`, `yes`, `sim`), **pare**. Não modifique
   arquivos.
8. Se afirmativa, salve o relatório em `../reports/audit-project-<N>.md` quando
   o caminho do repositório desafio existir; caso contrário, salve em
   `reports/audit-report.md` dentro do projeto.

---

## PHASE 3: MVC REFACTORING

Só execute após confirmação na Fase 2.

1. Siga `mvc-architecture-guidelines.md` e `refactoring-playbook.md`.
2. Adapte a profundidade da refatoração ao estado atual:
   - **Monolito flat / God Class:** criar estrutura MVC completa.
   - **Camadas parciais:** corrigir violações, extrair controllers/services,
     mover rotas misplaced, centralizar config e error handling — sem quebrar
     endpoints existentes.
3. Estrutura-alvo típica (adapte à stack):

```
src/   (ou raiz organizada)
├── config/          # settings sem secrets hardcoded
├── models/          # acesso a dados / entidades
├── views/           # rotas / apresentação HTTP
├── controllers/     # orquestração do fluxo
├── middlewares/     # error handler centralizado
└── app.(py|js)      # composition root / entry point
```

4. Elimine os findings CRITICAL/HIGH sempre que possível; trate MEDIUM/LOW
   conforme o playbook.
5. Preserve contratos públicos dos endpoints de negócio (paths, métodos, shape
   principal das respostas). Remova ou proteja backdoors perigosos
   (`/admin/query` arbitrário, etc.) documentando a mudança.
6. **Validação obrigatória:**
   - Instale dependências se necessário
   - Suba a aplicação
   - Exercite endpoints principais (health, listagens, create/login quando
     existirem)
   - Confirme boot sem erros e respostas coerentes
7. Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining (ou remanescentes LOW documentados)
================================
```

---

## Regras gerais

- Seja **agnóstico**: as mesmas fases valem para Python, Node.js e outras stacks.
- Cite sempre **arquivo:linha** nos findings.
- Não invente findings sem evidência no código.
- Prefira queries parametrizadas, hashing forte de senhas, config via env,
  error handling centralizado e camadas com responsabilidade única.
- Em projetos parcialmente organizados, **não** destrua o que já funciona —
  melhore incrementalmente em direção ao MVC.
