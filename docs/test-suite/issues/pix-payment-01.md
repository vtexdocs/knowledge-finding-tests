# Issue: Set up PIX payment in my VTEX store

| Field | Value |
|-------|--------|
| **issue_id** | pix-payment-01 |
| **persona** | Store operator |
| **product** | Payments |
| **user_intent** | Set up PIX payment in my VTEX store |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/setting-up-pix-as-a-payment-method |
| **surface** | help-center and developers-portal |
| **target_docs** | ["https://help.vtex.com/pt/docs/tutorials/configurar-pix-como-meio-de-pagamento", "https://help.vtex.com/docs/tutorials/setting-up-pix-as-a-payment-method", "https://help.vtex.com/es/docs/tutorials/configurar-pix-como-medio-de-pago", "https://help.vtex.com/en/docs/tutorials/setting-up-pix-as-a-payment-method"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tracks/configurar-pix", "https://help.vtex.com/docs/tracks/setting-up-pix", "https://help.vtex.com/es/docs/tracks/configuracion-de-pix", "https://help.vtex.com/pt/announcements/2020-11-16-pix-configure-o-meio-de-pagamento-via-admin", "https://help.vtex.com/announcements/2020-11-16-pix-configure-the-payment-method-via-admin", "https://help.vtex.com/es/announcements/2020-11-16-pix-configure-el-medio-de-pago-via-admin", "https://help.vtex.com/pt/docs/tutorials/pix-faq", "https://help.vtex.com/docs/tutorials/pix-faq", "https://help.vtex.com/es/docs/tutorials/pix-faq", "https://help.vtex.com/pt/docs/tutorials/configurar-a-afiliacao-de-gateway-tuna", "https://help.vtex.com/docs/tutorials/configuring-tuna-gateway-affiliation", "https://help.vtex.com/es/docs/tutorials/configurar-la-afiliacion-a-la-tuna", "https://help.vtex.com/pt/docs/tutorials/configurar-pagamento-com-iugu", "https://help.vtex.com/en/docs/tutorials/setting-up-payments-with-iugu", "https://help.vtex.com/es/docs/tutorials/configurar-pagamento-com-iugu", "https://developers.vtex.com/docs/guides/payments-integration-pix-instant-payments-in-brazil", "https://developers.vtex.com/docs/guides/payments-integration-guide", "https://help.vtex.com/en/docs/tracks/setting-up-pix", "https://help.vtex.com/en/announcements/2020-11-16-pix-configure-the-payment-method-via-admin", "https://help.vtex.com/en/docs/tutorials/pix-faq", "https://help.vtex.com/en/docs/tutorials/configuring-tuna-gateway-affiliation", "https://help.vtex.com/es/docs/tutorials/configurar-pago-con-iugu"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

*Note: PIX can be enabled via several payment providers (e.g. BluePay, PagoExpress, Pay4Fun, Shipay). The URL above is one representative tutorial; success may also be measured against other provider setup docs or a generic payment-provider overview.*

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | accept instant bank transfers from customers in my VTEX online store |
| en | familiar | enable PIX payment in my VTEX store |
| en | expert | how to set up PIX payment provider in VTEX |
| pt | naive | aceitar transferências bancárias instantâneas de clientes na minha loja VTEX |
| pt | familiar | habilitar pagamento PIX na minha loja VTEX |
| pt | expert | como configurar provedor de pagamento PIX no VTEX |
| es | naive | aceptar transferencias bancarias instantáneas de clientes en mi tienda VTEX |
| es | familiar | habilitar pago PIX en mi tienda VTEX |
| es | expert | cómo configurar proveedor de pago PIX en VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "accept instant bank transfers from customers in my VTEX online store" },
  { "locale": "en", "style": "familiar", "query": "enable PIX payment in my VTEX store" },
  { "locale": "en", "style": "expert", "query": "how to set up PIX payment provider in VTEX" },
  { "locale": "pt", "style": "naive", "query": "aceitar transferências bancárias instantâneas de clientes na minha loja VTEX" },
  { "locale": "pt", "style": "familiar", "query": "habilitar pagamento PIX na minha loja VTEX" },
  { "locale": "pt", "style": "expert", "query": "como configurar provedor de pagamento PIX no VTEX" },
  { "locale": "es", "style": "naive", "query": "aceptar transferencias bancarias instantáneas de clientes en mi tienda VTEX" },
  { "locale": "es", "style": "familiar", "query": "habilitar pago PIX en mi tienda VTEX" },
  { "locale": "es", "style": "expert", "query": "cómo configurar proveedor de pago PIX en VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | payment instant transfer online store |
| en | familiar | PIX payment VTEX provider setup |
| en | expert | set up PIX payment provider VTEX Store Settings |
| pt | naive | pagamento transferência instantânea loja online |
| pt | familiar | configuração de provedor PIX VTEX |
| pt | expert | configurar provedor de pagamento PIX VTEX configurações da loja |
| es | naive | pago transferencia instantánea tienda online |
| es | familiar | configuración de proveedor PIX VTEX |
| es | expert | configurar proveedor de pago PIX VTEX configuración de tienda |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "payment instant transfer online store" },
  { "locale": "en", "style": "familiar", "query": "PIX payment VTEX provider setup" },
  { "locale": "en", "style": "expert", "query": "set up PIX payment provider VTEX Store Settings" },
  { "locale": "pt", "style": "naive", "query": "pagamento transferência instantânea loja online" },
  { "locale": "pt", "style": "familiar", "query": "configuração de provedor PIX VTEX" },
  { "locale": "pt", "style": "expert", "query": "configurar provedor de pagamento PIX VTEX configurações da loja" },
  { "locale": "es", "style": "naive", "query": "pago transferencia instantánea tienda online" },
  { "locale": "es", "style": "familiar", "query": "configuración de proveedor PIX VTEX" },
  { "locale": "es", "style": "expert", "query": "configurar proveedor de pago PIX VTEX configuración de tienda" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to accept PIX payments in my store |
| en | familiar | configure PIX payment provider VTEX |
| en | expert | setting up payments with PIX provider VTEX |
| pt | naive | como aceitar pagamentos PIX na minha loja |
| pt | familiar | configurar provedor de pagamento PIX VTEX |
| pt | expert | configurar pagamentos com provedor PIX VTEX |
| es | naive | cómo aceptar pagos PIX en mi tienda |
| es | familiar | configurar proveedor de pago PIX VTEX |
| es | expert | configurar pagos con proveedor PIX VTEX |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to accept PIX payments in my store" },
  { "locale": "en", "style": "familiar", "query": "configure PIX payment provider VTEX" },
  { "locale": "en", "style": "expert", "query": "setting up payments with PIX provider VTEX" },
  { "locale": "pt", "style": "naive", "query": "como aceitar pagamentos PIX na minha loja" },
  { "locale": "pt", "style": "familiar", "query": "configurar provedor de pagamento PIX VTEX" },
  { "locale": "pt", "style": "expert", "query": "configurar pagamentos com provedor PIX VTEX" },
  { "locale": "es", "style": "naive", "query": "cómo aceptar pagos PIX en mi tienda" },
  { "locale": "es", "style": "familiar", "query": "configurar proveedor de pago PIX VTEX" },
  { "locale": "es", "style": "expert", "query": "configurar pagos con proveedor PIX VTEX" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How can I let customers pay with PIX in my VTEX store? |
| en | familiar | How do I set up PIX payment in my VTEX store? |
| en | expert | How do I configure a PIX payment provider in VTEX Admin? |
| pt | naive | Como posso deixar clientes pagar com PIX na minha loja VTEX? |
| pt | familiar | Como configuro o pagamento PIX na minha loja VTEX? |
| pt | expert | Como configuro um provedor de pagamento PIX no VTEX Admin? |
| es | naive | ¿Cómo puedo dejar que los clientes paguen con PIX en mi tienda VTEX? |
| es | familiar | ¿Cómo configuro el pago PIX en mi tienda VTEX? |
| es | expert | ¿Cómo configuro un proveedor de pago PIX en VTEX Admin? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How can I let customers pay with PIX in my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "How do I set up PIX payment in my VTEX store?" },
  { "locale": "en", "style": "expert", "query": "How do I configure a PIX payment provider in VTEX Admin?" },
  { "locale": "pt", "style": "naive", "query": "Como posso deixar clientes pagar com PIX na minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como configuro o pagamento PIX na minha loja VTEX?" },
  { "locale": "pt", "style": "expert", "query": "Como configuro um provedor de pagamento PIX no VTEX Admin?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo puedo dejar que los clientes paguen con PIX en mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo configuro el pago PIX en mi tienda VTEX?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo configuro un proveedor de pago PIX en VTEX Admin?" }
]
```


