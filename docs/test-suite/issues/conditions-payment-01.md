# Issue: Configure special conditions for payment methods

| Field | Value |
|-------|--------|
| **issue_id** | conditions-payment-01 |
| **persona** | Store operator |
| **product** | Payments |
| **user_intent** | How to configure special conditions for payment methods registered in my VTEX store. |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/special-conditions |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/condicoes-especiais", "https://help.vtex.com/docs/tutorials/special-conditions", "https://help.vtex.com/es/tutorial/condiciones-especiales", "https://help.vtex.com/en/docs/tutorials/special-conditions", "https://help.vtex.com/pt/docs/tutorials/condicoes-especiais", "https://help.vtex.com/es/docs/tutorials/condiciones-especiales"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento", "https://help.vtex.com/docs/tracks/configuring-a-payment-condition", "https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago", "https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos", "https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings", "https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos", "https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos", "https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments", "https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos", "https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos", "https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments", "https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos", "https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor", "https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank", "https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor", "https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition", "https://help.vtex.com/en/docs/tracks/vtex-modules-ii", "https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii", "https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii", "https://help.vtex.com/en/docs/tutorials/how-trade-policies-work", "https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial", "https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial", "https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy", "https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace", "https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace", "https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to set special conditions for payment methods in vtex |
| en | familiar | configure special payment conditions vtex |
| en | expert | special conditions vtex payments |
| pt | naive | como configurar condições especiais para métodos de pagamento no vtex |
| pt | familiar | configurar condições especiais de pagamento vtex |
| pt | expert | condições especiais vtex pagamentos |
| es | naive | cómo configurar condiciones especiales para métodos de pago en vtex |
| es | familiar | configurar condiciones especiales de pago vtex |
| es | expert | condiciones especiales vtex pagos |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to set special conditions for payment methods in vtex" },
  { "locale": "en", "style": "familiar", "query": "configure special payment conditions vtex" },
  { "locale": "en", "style": "expert", "query": "special conditions vtex payments" },
  { "locale": "pt", "style": "naive", "query": "como configurar condições especiais para métodos de pagamento no vtex" },
  { "locale": "pt", "style": "familiar", "query": "configurar condições especiais de pagamento vtex" },
  { "locale": "pt", "style": "expert", "query": "condições especiais vtex pagamentos" },
  { "locale": "es", "style": "naive", "query": "cómo configurar condiciones especiales para métodos de pago en vtex" },
  { "locale": "es", "style": "familiar", "query": "configurar condiciones especiales de pago vtex" },
  { "locale": "es", "style": "expert", "query": "condiciones especiales vtex pagos" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | special conditions payments |
| en | familiar | payment method conditions |
| en | expert | special conditions |
| pt | naive | condições especiais pagamentos |
| pt | familiar | condições de método de pagamento |
| pt | expert | condições especiais |
| es | naive | condiciones especiales pagos |
| es | familiar | condiciones de método de pago |
| es | expert | condiciones especiales |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "special conditions payments" },
  { "locale": "en", "style": "familiar", "query": "payment method conditions" },
  { "locale": "en", "style": "expert", "query": "special conditions" },
  { "locale": "pt", "style": "naive", "query": "condições especiais pagamentos" },
  { "locale": "pt", "style": "familiar", "query": "condições de método de pagamento" },
  { "locale": "pt", "style": "expert", "query": "condições especiais" },
  { "locale": "es", "style": "naive", "query": "condiciones especiales pagos" },
  { "locale": "es", "style": "familiar", "query": "condiciones de método de pago" },
  { "locale": "es", "style": "expert", "query": "condiciones especiales" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs on special conditions for payments |
| en | familiar | vtex special payment conditions setup |
| en | expert | special conditions |
| pt | naive | vtex docs sobre condições especiais para pagamentos |
| pt | familiar | configuração de condições especiais de pagamento vtex |
| pt | expert | condições especiais |
| es | naive | vtex docs sobre condiciones especiales para pagos |
| es | familiar | configuración de condiciones especiales de pago vtex |
| es | expert | condiciones especiales |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs on special conditions for payments" },
  { "locale": "en", "style": "familiar", "query": "vtex special payment conditions setup" },
  { "locale": "en", "style": "expert", "query": "special conditions" },
  { "locale": "pt", "style": "naive", "query": "vtex docs sobre condições especiais para pagamentos" },
  { "locale": "pt", "style": "familiar", "query": "configuração de condições especiais de pagamento vtex" },
  { "locale": "pt", "style": "expert", "query": "condições especiais" },
  { "locale": "es", "style": "naive", "query": "vtex docs sobre condiciones especiales para pagos" },
  { "locale": "es", "style": "familiar", "query": "configuración de condiciones especiales de pago vtex" },
  { "locale": "es", "style": "expert", "query": "condiciones especiales" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how do i configure special conditions for payment methods in vtex |
| en | familiar | steps to set special conditions for vtex payment methods |
| en | expert | how to configure special conditions for payment methods in vtex |
| pt | naive | como configurar condições especiais para métodos de pagamento no vtex |
| pt | familiar | passos para definir condições especiais para métodos de pagamento vtex |
| pt | expert | como configurar condições especiais para métodos de pagamento no vtex |
| es | naive | cómo configurar condiciones especiales para métodos de pago en vtex |
| es | familiar | pasos para establecer condiciones especiales para métodos de pago vtex |
| es | expert | cómo configurar condiciones especiales para métodos de pago en vtex |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do i configure special conditions for payment methods in vtex" },
  { "locale": "en", "style": "familiar", "query": "steps to set special conditions for vtex payment methods" },
  { "locale": "en", "style": "expert", "query": "how to configure special conditions for payment methods in vtex" },
  { "locale": "pt", "style": "naive", "query": "como configurar condições especiais para métodos de pagamento no vtex" },
  { "locale": "pt", "style": "familiar", "query": "passos para definir condições especiais para métodos de pagamento vtex" },
  { "locale": "pt", "style": "expert", "query": "como configurar condições especiais para métodos de pagamento no vtex" },
  { "locale": "es", "style": "naive", "query": "cómo configurar condiciones especiales para métodos de pago en vtex" },
  { "locale": "es", "style": "familiar", "query": "pasos para establecer condiciones especiales para métodos de pago vtex" },
  { "locale": "es", "style": "expert", "query": "cómo configurar condiciones especiales para métodos de pago en vtex" }
]
```


