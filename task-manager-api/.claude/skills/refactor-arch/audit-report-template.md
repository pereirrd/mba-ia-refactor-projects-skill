# Template de Relatório de Auditoria (Fase 2)

Use este formato **exatamente** na saída da Fase 2 e ao salvar
`reports/audit-project-N.md`.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <Language> + <Framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Título do anti-pattern>
File: <path>:<start>-<end>   # ou path:line
Description: <o que foi encontrado, com evidência>
Impact: <consequência prática>
Recommendation: <ação concreta de refatoração>

### [CRITICAL] ...
...

### [HIGH] ...
...

### [MEDIUM] ...
...

### [LOW] ...
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

1. **Ordenação:** CRITICAL → HIGH → MEDIUM → LOW.
2. **Localização:** sempre arquivo + linha(s) reais.
3. **Mínimo:** ≥ 5 findings; ≥ 1 CRITICAL ou HIGH.
4. **Deprecated:** se houver API obsoleta, incluir finding dedicado.
5. **Sem inventar:** só o que existe no código analisado.
6. **Idioma:** português para description/impact/recommendation (como nos exemplos do desafio), títulos de anti-pattern podem permanecer em inglês técnico.

## Exemplo de finding (referência)

```
### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões.
Recommendation: Mover para variável de ambiente SECRET_KEY e documentar em .env.example.
```
