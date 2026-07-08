# Issue: Payment refunds

| Field | Value |
|-------|--------|
| **issue_id** | refund-payment-01 |
| **persona** | Decision Maker |
| **product** | Payments |
| **user_intent** | Identify how the payment refund was made at VTEX. |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/payment-refunds |
| **surface** | help-center and developers-portal|
| **target_docs** | ["https://help.vtex.com/pt/tutorial/reembolso-de-pagamentos", "https://help.vtex.com/docs/tutorials/payment-refunds", "https://help.vtex.com/es/tutorial/reembolso-de-pagos", "https://help.vtex.com/en/docs/tutorials/payment-refunds", "https://help.vtex.com/pt/docs/tutorials/reembolso-de-pagamentos", "https://help.vtex.com/es/docs/tutorials/reembolso-de-pagos"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tutorials/operacoes-de-pagamentos-pos-compra", "https://help.vtex.com/docs/tutorials/post-purchase-payment-operations", "https://help.vtex.com/es/docs/tutorials/operaciones-de-pago-poscompra", "https://help.vtex.com/pt/docs/tutorials/payment-provider-protocol", "https://help.vtex.com/en/docs/tutorials/payment-provider-protocol", "https://help.vtex.com/es/docs/tutorials/payment-provider-protocol", "https://help.vtex.com/pt/docs/tutorials/como-funciona-estorno-quando-ha-devolucao-do-item", "https://help.vtex.com/docs/tutorials/how-do-reversals-work-when-an-item-is-returned", "https://help.vtex.com/es/docs/tutorials/como-se-da-el-funciona-extorno-cuando-hay-devolucion-del-item", "https://help.vtex.com/pt/docs/tutorials/como-devolver-itens-do-pedido", "https://help.vtex.com/docs/tutorials/how-to-return-order-items", "https://help.vtex.com/es/docs/tutorials/como-devolver-itens-do-pedido", "https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider", "https://developers.vtex.com/docs/guides/payments-integration-purchase-flows", "https://developers.vtex.com/docs/guides/split-payouts-on-payment-provider-protocol", "https://help.vtex.com/en/docs/tutorials/post-purchase-payment-operations", "https://help.vtex.com/en/docs/tutorials/how-do-reversals-work-when-an-item-is-returned", "https://help.vtex.com/en/docs/tutorials/how-to-return-order-items", "https://help.vtex.com/es/docs/tutorials/como-devolver-items-del-pedido"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to see how a payment refund was made in vtex |
| en | familiar | identify payment refund method vtex |
| en | expert | payment refunds vtex |
| pt | naive | como ver como um reembolso de pagamento foi feito no vtex |
| pt | familiar | identificar método de reembolso de pagamento vtex |
| pt | expert | reembolso de pagamentos vtex |
| es | naive | cómo ver cómo se realizó un reembolso de pago en vtex |
| es | familiar | identificar método de reembolso de pago vtex |
| es | expert | reembolso de pagos vtex |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to see how a payment refund was made in vtex" },
  { "locale": "en", "style": "familiar", "query": "identify payment refund method vtex" },
  { "locale": "en", "style": "expert", "query": "payment refunds vtex" },
  { "locale": "pt", "style": "naive", "query": "como ver como um reembolso de pagamento foi feito no vtex" },
  { "locale": "pt", "style": "familiar", "query": "identificar método de reembolso de pagamento vtex" },
  { "locale": "pt", "style": "expert", "query": "reembolso de pagamentos vtex" },
  { "locale": "es", "style": "naive", "query": "cómo ver cómo se realizó un reembolso de pago en vtex" },
  { "locale": "es", "style": "familiar", "query": "identificar método de reembolso de pago vtex" },
  { "locale": "es", "style": "expert", "query": "reembolso de pagos vtex" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | payment refunds |
| en | familiar | refund method |
| en | expert | payment refunds |
| pt | naive | reembolso de pagamentos |
| pt | familiar | método de reembolso |
| pt | expert | reembolso de pagamentos |
| es | naive | reembolso de pagos |
| es | familiar | método de reembolso |
| es | expert | reembolso de pagos |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "payment refunds" },
  { "locale": "en", "style": "familiar", "query": "refund method" },
  { "locale": "en", "style": "expert", "query": "payment refunds" },
  { "locale": "pt", "style": "naive", "query": "reembolso de pagamentos" },
  { "locale": "pt", "style": "familiar", "query": "método de reembolso" },
  { "locale": "pt", "style": "expert", "query": "reembolso de pagamentos" },
  { "locale": "es", "style": "naive", "query": "reembolso de pagos" },
  { "locale": "es", "style": "familiar", "query": "método de reembolso" },
  { "locale": "es", "style": "expert", "query": "reembolso de pagos" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs on payment refunds |
| en | familiar | vtex payment refunds guide |
| en | expert | payment refunds |
| pt | naive | vtex docs sobre reembolso de pagamentos |
| pt | familiar | guia de reembolso de pagamentos vtex |
| pt | expert | reembolso de pagamentos |
| es | naive | vtex docs sobre reembolso de pagos |
| es | familiar | guía de reembolso de pagos vtex |
| es | expert | reembolso de pagos |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs on payment refunds" },
  { "locale": "en", "style": "familiar", "query": "vtex payment refunds guide" },
  { "locale": "en", "style": "expert", "query": "payment refunds" },
  { "locale": "pt", "style": "naive", "query": "vtex docs sobre reembolso de pagamentos" },
  { "locale": "pt", "style": "familiar", "query": "guia de reembolso de pagamentos vtex" },
  { "locale": "pt", "style": "expert", "query": "reembolso de pagamentos" },
  { "locale": "es", "style": "naive", "query": "vtex docs sobre reembolso de pagos" },
  { "locale": "es", "style": "familiar", "query": "guía de reembolso de pagos vtex" },
  { "locale": "es", "style": "expert", "query": "reembolso de pagos" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how do i identify how a payment refund was made in vtex |
| en | familiar | where can i see refund details in vtex payments |
| en | expert | how to identify payment refunds in vtex |
| pt | naive | como identifico como um reembolso de pagamento foi feito no vtex |
| pt | familiar | onde posso ver detalhes de reembolso em pagamentos vtex |
| pt | expert | como identificar reembolsos de pagamentos no vtex |
| es | naive | cómo identifico cómo se realizó un reembolso de pago en vtex |
| es | familiar | dónde puedo ver los detalles de reembolso en pagos vtex |
| es | expert | cómo identificar reembolsos de pagos en vtex |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do i identify how a payment refund was made in vtex" },
  { "locale": "en", "style": "familiar", "query": "where can i see refund details in vtex payments" },
  { "locale": "en", "style": "expert", "query": "how to identify payment refunds in vtex" },
  { "locale": "pt", "style": "naive", "query": "como identifico como um reembolso de pagamento foi feito no vtex" },
  { "locale": "pt", "style": "familiar", "query": "onde posso ver detalhes de reembolso em pagamentos vtex" },
  { "locale": "pt", "style": "expert", "query": "como identificar reembolsos de pagamentos no vtex" },
  { "locale": "es", "style": "naive", "query": "cómo identifico cómo se realizó un reembolso de pago en vtex" },
  { "locale": "es", "style": "familiar", "query": "dónde puedo ver los detalles de reembolso en pagos vtex" },
  { "locale": "es", "style": "expert", "query": "cómo identificar reembolsos de pagos en vtex" }
]
```


