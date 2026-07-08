# Issue: Manage bank reconciliations for bank slip payments

| Field | Value |
|-------|--------|
| **issue_id** | conciliations-payment-01 |
| **persona** | Store operator |
| **product** | Payments |
| **user_intent** | How to manage bank reconciliations of payments made by bank slip. |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/bank-reconciliations |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/conciliacoes-bancarias", "https://help.vtex.com/docs/tutorials/bank-reconciliations", "https://help.vtex.com/es/tutorial/conciliaciones-bancarias", "https://help.vtex.com/en/docs/tutorials/bank-reconciliations", "https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias", "https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento", "https://help.vtex.com/docs/tutorials/registered-ticket-flow", "https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo", "https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto", "https://help.vtex.com/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved", "https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto", "https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral", "https://help.vtex.com/docs/tutorials/orders-overview", "https://help.vtex.com/es/docs/tutorials/pedidos-vision-general", "https://help.vtex.com/en/docs/tutorials/registered-ticket-flow", "https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved", "https://help.vtex.com/en/docs/tutorials/orders-overview"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to reconcile bank slip payments in vtex |
| en | familiar | manage bank reconciliation for boleto payments vtex |
| en | expert | bank reconciliations vtex payments |
| pt | naive | como conciliar pagamentos com boleto no vtex |
| pt | familiar | gerenciar conciliação bancária para pagamentos com boleto vtex |
| pt | expert | conciliações bancárias vtex pagamentos |
| es | naive | cómo conciliar pagos con boleto en vtex |
| es | familiar | gestionar conciliación bancaria para pagos con boleto vtex |
| es | expert | conciliaciones bancarias vtex pagos |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to reconcile bank slip payments in vtex" },
  { "locale": "en", "style": "familiar", "query": "manage bank reconciliation for boleto payments vtex" },
  { "locale": "en", "style": "expert", "query": "bank reconciliations vtex payments" },
  { "locale": "pt", "style": "naive", "query": "como conciliar pagamentos com boleto no vtex" },
  { "locale": "pt", "style": "familiar", "query": "gerenciar conciliação bancária para pagamentos com boleto vtex" },
  { "locale": "pt", "style": "expert", "query": "conciliações bancárias vtex pagamentos" },
  { "locale": "es", "style": "naive", "query": "cómo conciliar pagos con boleto en vtex" },
  { "locale": "es", "style": "familiar", "query": "gestionar conciliación bancaria para pagos con boleto vtex" },
  { "locale": "es", "style": "expert", "query": "conciliaciones bancarias vtex pagos" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | bank reconciliation boleto |
| en | familiar | bank reconciliations |
| en | expert | bank reconciliations |
| pt | naive | conciliação bancária boleto |
| pt | familiar | conciliações bancárias |
| pt | expert | conciliações bancárias |
| es | naive | conciliación bancaria boleto |
| es | familiar | conciliaciones bancarias |
| es | expert | conciliaciones bancarias |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "bank reconciliation boleto" },
  { "locale": "en", "style": "familiar", "query": "bank reconciliations" },
  { "locale": "en", "style": "expert", "query": "bank reconciliations" },
  { "locale": "pt", "style": "naive", "query": "conciliação bancária boleto" },
  { "locale": "pt", "style": "familiar", "query": "conciliações bancárias" },
  { "locale": "pt", "style": "expert", "query": "conciliações bancárias" },
  { "locale": "es", "style": "naive", "query": "conciliación bancaria boleto" },
  { "locale": "es", "style": "familiar", "query": "conciliaciones bancarias" },
  { "locale": "es", "style": "expert", "query": "conciliaciones bancarias" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs on bank reconciliations |
| en | familiar | vtex bank reconciliation for boleto payments |
| en | expert | bank reconciliations |
| pt | naive | vtex docs sobre conciliações bancárias |
| pt | familiar | vtex conciliação bancária para pagamentos com boleto |
| pt | expert | conciliações bancárias |
| es | naive | vtex docs sobre conciliaciones bancarias |
| es | familiar | vtex conciliación bancaria para pagos con boleto |
| es | expert | conciliaciones bancarias |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs on bank reconciliations" },
  { "locale": "en", "style": "familiar", "query": "vtex bank reconciliation for boleto payments" },
  { "locale": "en", "style": "expert", "query": "bank reconciliations" },
  { "locale": "pt", "style": "naive", "query": "vtex docs sobre conciliações bancárias" },
  { "locale": "pt", "style": "familiar", "query": "vtex conciliação bancária para pagamentos com boleto" },
  { "locale": "pt", "style": "expert", "query": "conciliações bancárias" },
  { "locale": "es", "style": "naive", "query": "vtex docs sobre conciliaciones bancarias" },
  { "locale": "es", "style": "familiar", "query": "vtex conciliación bancaria para pagos con boleto" },
  { "locale": "es", "style": "expert", "query": "conciliaciones bancarias" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how do i manage bank reconciliations for bank slip payments in vtex |
| en | familiar | steps to reconcile boleto payments in vtex |
| en | expert | how to manage bank reconciliations in vtex payments |
| pt | naive | como gerenciar conciliações bancárias para pagamentos com boleto no vtex |
| pt | familiar | passos para conciliar pagamentos com boleto no vtex |
| pt | expert | como gerenciar conciliações bancárias em pagamentos vtex |
| es | naive | cómo gestionar conciliaciones bancarias para pagos con boleto en vtex |
| es | familiar | pasos para conciliar pagos con boleto en vtex |
| es | expert | cómo gestionar conciliaciones bancarias en pagos vtex |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do i manage bank reconciliations for bank slip payments in vtex" },
  { "locale": "en", "style": "familiar", "query": "steps to reconcile boleto payments in vtex" },
  { "locale": "en", "style": "expert", "query": "how to manage bank reconciliations in vtex payments" },
  { "locale": "pt", "style": "naive", "query": "como gerenciar conciliações bancárias para pagamentos com boleto no vtex" },
  { "locale": "pt", "style": "familiar", "query": "passos para conciliar pagamentos com boleto no vtex" },
  { "locale": "pt", "style": "expert", "query": "como gerenciar conciliações bancárias em pagamentos vtex" },
  { "locale": "es", "style": "naive", "query": "cómo gestionar conciliaciones bancarias para pagos con boleto en vtex" },
  { "locale": "es", "style": "familiar", "query": "pasos para conciliar pagos con boleto en vtex" },
  { "locale": "es", "style": "expert", "query": "cómo gestionar conciliaciones bancarias en pagos vtex" }
]
```


