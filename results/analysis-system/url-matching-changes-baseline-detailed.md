# URL matching impact — baseline re-simulation

**Analysis run:** `analysis-system 2026-04-30 15-00`  
**Method:** Re-classify stored `classified_results` with the new Help Center URL matcher and compare metrics to the stored baseline.

## Summary

| | Count |
|---|---:|
| Changed queries | 38 |
| Help Center / locale-related | 20 |
| hybrid-search developers (re-simulation artifact) | 18 |
| Reclassified link rows | 86 |

### Metric legend

| Metric | Meaning |
|--------|---------|
| `target_found` | Expected doc found in the **same locale** as the query |
| `target_different_loc_found` | Expected doc found in a **different locale** |
| `target_any_locale_found` | Expected doc found in **any** locale |

### Changed queries (quick index)

| # | Issue | Source | Locale / style | `target_found` | `different_loc` | `any_locale` |
|--:|-------|--------|----------------|----------------|-----------------|--------------|
| [1](#query-1) | `bitcoin-payment-01` | `external-search.google-search-playwright` | en / familiar | `False` → `False` | `False` → `True` | `False` → `True` |
| [2](#query-2) | `bitcoin-payment-01` | `external-search.google-search-playwright` | en / expert | `False` → `False` | `False` → `True` | `False` → `True` |
| [3](#query-3) | `cms-migration-01` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [4](#query-4) | `cms-migration-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [5](#query-5) | `conciliations-payment-01` | `llm.chatgpt` | en / naive | `True` → `False` | `False` → `True` | `True` → `True` |
| [6](#query-6) | `conciliations-payment-01` | `llm.chatgpt` | en / familiar | `False` → `False` | `False` → `True` | `False` → `True` |
| [7](#query-7) | `conciliations-payment-01` | `llm.chatgpt` | es / naive | `True` → `True` | `False` → `True` | `True` → `True` |
| [8](#query-8) | `conciliations-payment-01` | `llm.chatgpt` | es / expert | `True` → `True` | `False` → `True` | `True` → `True` |
| [9](#query-9) | `conditions-payment-01` | `external-search.google-search-playwright` | es / naive | `True` → `True` | `False` → `True` | `True` → `True` |
| [10](#query-10) | `conditions-payment-01` | `external-search.google-search-playwright` | es / familiar | `True` → `True` | `False` → `True` | `True` → `True` |
| [11](#query-11) | `conditions-payment-01` | `external-search.google-search-playwright` | pt / naive | `True` → `True` | `False` → `True` | `True` → `True` |
| [12](#query-12) | `conditions-payment-01` | `external-search.google-search-playwright` | pt / familiar | `False` → `False` | `False` → `True` | `False` → `True` |
| [13](#query-13) | `conditions-payment-01` | `external-search.google-search-playwright` | pt / expert | `True` → `True` | `False` → `True` | `True` → `True` |
| [14](#query-14) | `conditions-payment-01` | `llm.chatgpt` | en / naive | `True` → `True` | `False` → `True` | `True` → `True` |
| [15](#query-15) | `conditions-payment-01` | `llm.chatgpt` | en / familiar | `True` → `True` | `False` → `True` | `True` → `True` |
| [16](#query-16) | `conditions-payment-01` | `llm.chatgpt` | en / expert | `True` → `True` | `False` → `True` | `True` → `True` |
| [17](#query-17) | `conditions-payment-01` | `llm.chatgpt` | es / expert | `False` → `False` | `False` → `True` | `False` → `True` |
| [18](#query-18) | `content-delivery-optimization-01` | `internal-search.hybrid-search` | en / naive | `True` → `False` | `False` → `False` | `True` → `False` |
| [19](#query-19) | `content-delivery-optimization-01` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [20](#query-20) | `content-delivery-optimization-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [21](#query-21) | `customer-credit-01` | `internal-search.hybrid-search` | en / naive | `True` → `False` | `False` → `False` | `True` → `False` |
| [22](#query-22) | `customer-credit-01` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [23](#query-23) | `customer-credit-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [24](#query-24) | `payment-provider-01` | `internal-search.hybrid-search` | en / naive | `True` → `False` | `False` → `False` | `True` → `False` |
| [25](#query-25) | `payment-provider-01` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [26](#query-26) | `payment-provider-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [27](#query-27) | `payment-provider-02` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [28](#query-28) | `payment-provider-02` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [29](#query-29) | `product-indexing-01` | `llm.chatgpt` | pt / naive | `False` → `False` | `False` → `True` | `False` → `True` |
| [30](#query-30) | `product-not-visible-01` | `llm.chatgpt` | pt / familiar | `True` → `True` | `False` → `True` | `True` → `True` |
| [31](#query-31) | `product-not-visible-01` | `llm.chatgpt` | pt / expert | `False` → `False` | `False` → `True` | `False` → `True` |
| [32](#query-32) | `pwa-implementation-01` | `llm.gemini` | en / naive | `False` → `False` | `False` → `True` | `False` → `True` |
| [33](#query-33) | `sap-catalog-01` | `internal-search.hybrid-search` | en / naive | `True` → `False` | `False` → `False` | `True` → `False` |
| [34](#query-34) | `sap-catalog-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |
| [35](#query-35) | `support-work-01` | `external-search.google-search-playwright` | pt / expert | `True` → `True` | `False` → `True` | `True` → `True` |
| [36](#query-36) | `webstore-oauth2-01` | `internal-search.hybrid-search` | en / naive | `True` → `False` | `False` → `False` | `True` → `False` |
| [37](#query-37) | `webstore-oauth2-01` | `internal-search.hybrid-search` | en / familiar | `True` → `False` | `False` → `False` | `True` → `False` |
| [38](#query-38) | `webstore-oauth2-01` | `internal-search.hybrid-search` | en / expert | `True` → `False` | `False` → `False` | `True` → `False` |

---

## Query details

<a id="query-1"></a>

### 1. `bitcoin-payment-01` — external-search.google-search-playwright (en/familiar)

**Query:** configure bitcoin payment method vtex

| Field | Value |
|-------|-------|
| Issue | `bitcoin-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin)
- `[en]` [https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/como-habilitar-pagamentos-com-bitcoin](https://help.vtex.com/pt/tutorial/como-habilitar-pagamentos-com-bitcoin)
- `[es]` [https://help.vtex.com/es/tutorial/habilitar-pagos-con-bitcoin](https://help.vtex.com/es/tutorial/habilitar-pagos-con-bitcoin)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-habilitar-pagamentos-com-bitcoin](https://help.vtex.com/pt/docs/tutorials/como-habilitar-pagamentos-com-bitcoin)
- `[es]` [https://help.vtex.com/es/docs/tutorials/habilitar-pagos-con-bitcoin](https://help.vtex.com/es/docs/tutorials/habilitar-pagos-con-bitcoin)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-tuna-gateway-affiliation](https://help.vtex.com/docs/tutorials/configuring-tuna-gateway-affiliation)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/setting-up-payments-with-cielo-orquestrador](https://help.vtex.com/docs/tutorials/setting-up-payments-with-cielo-orquestrador)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-tuna-gateway-affiliation](https://help.vtex.com/en/docs/tutorials/configuring-tuna-gateway-affiliation)
- `[en]` [https://help.vtex.com/en/docs/tutorials/setting-up-payments-with-cielo-orquestrador](https://help.vtex.com/en/docs/tutorials/setting-up-payments-with-cielo-orquestrador)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurar-a-afiliacao-de-gateway-tuna](https://help.vtex.com/pt/docs/tutorials/configurar-a-afiliacao-de-gateway-tuna)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-la-afiliacion-a-la-tuna](https://help.vtex.com/es/docs/tutorials/configurar-la-afiliacion-a-la-tuna)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurar-pagamento-com-cielo-orquestrador](https://help.vtex.com/pt/docs/tutorials/configurar-pagamento-com-cielo-orquestrador)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-pago-con-cielo-orquestrador](https://help.vtex.com/es/docs/tutorials/configurar-pago-con-cielo-orquestrador)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/pt/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/pt/docs/tutorials/enabling-payments-with-bitcoin) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin; https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin |

---

<a id="query-2"></a>

### 2. `bitcoin-payment-01` — external-search.google-search-playwright (en/expert)

**Query:** enabling payments with bitcoin vtex

| Field | Value |
|-------|-------|
| Issue | `bitcoin-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin)
- `[en]` [https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/como-habilitar-pagamentos-com-bitcoin](https://help.vtex.com/pt/tutorial/como-habilitar-pagamentos-com-bitcoin)
- `[es]` [https://help.vtex.com/es/tutorial/habilitar-pagos-con-bitcoin](https://help.vtex.com/es/tutorial/habilitar-pagos-con-bitcoin)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-habilitar-pagamentos-com-bitcoin](https://help.vtex.com/pt/docs/tutorials/como-habilitar-pagamentos-com-bitcoin)
- `[es]` [https://help.vtex.com/es/docs/tutorials/habilitar-pagos-con-bitcoin](https://help.vtex.com/es/docs/tutorials/habilitar-pagos-con-bitcoin)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-tuna-gateway-affiliation](https://help.vtex.com/docs/tutorials/configuring-tuna-gateway-affiliation)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/setting-up-payments-with-cielo-orquestrador](https://help.vtex.com/docs/tutorials/setting-up-payments-with-cielo-orquestrador)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-tuna-gateway-affiliation](https://help.vtex.com/en/docs/tutorials/configuring-tuna-gateway-affiliation)
- `[en]` [https://help.vtex.com/en/docs/tutorials/setting-up-payments-with-cielo-orquestrador](https://help.vtex.com/en/docs/tutorials/setting-up-payments-with-cielo-orquestrador)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurar-a-afiliacao-de-gateway-tuna](https://help.vtex.com/pt/docs/tutorials/configurar-a-afiliacao-de-gateway-tuna)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-la-afiliacion-a-la-tuna](https://help.vtex.com/es/docs/tutorials/configurar-la-afiliacion-a-la-tuna)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurar-pagamento-com-cielo-orquestrador](https://help.vtex.com/pt/docs/tutorials/configurar-pagamento-com-cielo-orquestrador)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-pago-con-cielo-orquestrador](https://help.vtex.com/es/docs/tutorials/configurar-pago-con-cielo-orquestrador)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/pt/docs/tutorials/enabling-payments-with-bitcoin](https://help.vtex.com/pt/docs/tutorials/enabling-payments-with-bitcoin) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/enabling-payments-with-bitcoin; https://help.vtex.com/en/docs/tutorials/enabling-payments-with-bitcoin |

---

<a id="query-3"></a>

### 3. `cms-migration-01` — internal-search.hybrid-search (en/familiar)

**Query:** Store Framework migration production rollback

| Field | Value |
|-------|-------|
| Issue | `cms-migration-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io](https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/getting-started-with-storefront-solutions](https://developers.vtex.com/docs/guides/getting-started-with-storefront-solutions)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [developers.vtex.com/vtex-io-documentation-migrating-storefront-from-...](https://developers.vtex.com/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | none |
| 2 | [developers.vtex.com/vtex-io-documentation-migrating-storefront-from-...](https://developers.vtex.com/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | none |

---

<a id="query-4"></a>

### 4. `cms-migration-01` — internal-search.hybrid-search (en/expert)

**Query:** CMS Legacy Store Framework migration rollback

| Field | Value |
|-------|-------|
| Issue | `cms-migration-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io](https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/getting-started-with-storefront-solutions](https://developers.vtex.com/docs/guides/getting-started-with-storefront-solutions)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [developers.vtex.com/vtex-io-documentation-migrating-storefront-from-...](https://developers.vtex.com/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | none |
| 3 | [developers.vtex.com/vtex-io-documentation-migrating-storefront-from-...](https://developers.vtex.com/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/vtex-io-documentation-migrating-storefront-from-legacy-to-io) | none |

---

<a id="query-5"></a>

### 5. `conciliations-payment-01` — llm.chatgpt (en/naive)

**Query:** how do i manage bank reconciliations for bank slip payments in vtex

| Field | Value |
|-------|-------|
| Issue | `conciliations-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `en` / `naive` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/bank-reconciliations](https://help.vtex.com/docs/tutorials/bank-reconciliations)
- `[en]` [https://help.vtex.com/en/docs/tutorials/bank-reconciliations](https://help.vtex.com/en/docs/tutorials/bank-reconciliations)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/conciliacoes-bancarias](https://help.vtex.com/pt/tutorial/conciliacoes-bancarias)
- `[es]` [https://help.vtex.com/es/tutorial/conciliaciones-bancarias](https://help.vtex.com/es/tutorial/conciliaciones-bancarias)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias](https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias)
- `[es]` [https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias](https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/registered-ticket-flow](https://help.vtex.com/docs/tutorials/registered-ticket-flow)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/orders-overview](https://help.vtex.com/docs/tutorials/orders-overview)
- `[en]` [https://help.vtex.com/en/docs/tutorials/registered-ticket-flow](https://help.vtex.com/en/docs/tutorials/registered-ticket-flow)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[en]` [https://help.vtex.com/en/docs/tutorials/orders-overview](https://help.vtex.com/en/docs/tutorials/orders-overview)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento](https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento)
- `[es]` [https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo](https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto](https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto](https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral](https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral)
- `[es]` [https://help.vtex.com/es/docs/tutorials/pedidos-vision-general](https://help.vtex.com/es/docs/tutorials/pedidos-vision-general)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/docs/tutorials/bank-reconciliations?locale=pt&utm_source...](https://help.vtex.com/docs/tutorials/bank-reconciliations?locale=pt&utm_source=chatgpt.com) | `target_doc` → `target_doc_different_loc` | unresolved (stored as `target_doc`; strict baseline: https://help.vtex.com/docs/tutorials/bank-reconciliations) | https://help.vtex.com/docs/tutorials/bank-reconciliations; https://help.vtex.com/en/docs/tutorials/bank-reconciliations |

---

<a id="query-6"></a>

### 6. `conciliations-payment-01` — llm.chatgpt (en/familiar)

**Query:** steps to reconcile boleto payments in vtex

| Field | Value |
|-------|-------|
| Issue | `conciliations-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `en` / `familiar` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/bank-reconciliations](https://help.vtex.com/docs/tutorials/bank-reconciliations)
- `[en]` [https://help.vtex.com/en/docs/tutorials/bank-reconciliations](https://help.vtex.com/en/docs/tutorials/bank-reconciliations)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/conciliacoes-bancarias](https://help.vtex.com/pt/tutorial/conciliacoes-bancarias)
- `[es]` [https://help.vtex.com/es/tutorial/conciliaciones-bancarias](https://help.vtex.com/es/tutorial/conciliaciones-bancarias)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias](https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias)
- `[es]` [https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias](https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/registered-ticket-flow](https://help.vtex.com/docs/tutorials/registered-ticket-flow)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/orders-overview](https://help.vtex.com/docs/tutorials/orders-overview)
- `[en]` [https://help.vtex.com/en/docs/tutorials/registered-ticket-flow](https://help.vtex.com/en/docs/tutorials/registered-ticket-flow)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[en]` [https://help.vtex.com/en/docs/tutorials/orders-overview](https://help.vtex.com/en/docs/tutorials/orders-overview)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento](https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento)
- `[es]` [https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo](https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto](https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto](https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral](https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral)
- `[es]` [https://help.vtex.com/es/docs/tutorials/pedidos-vision-general](https://help.vtex.com/es/docs/tutorials/pedidos-vision-general)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/pt/docs/tutorials/bank-reconciliations?utm_source=chatgpt.com](https://help.vtex.com/pt/docs/tutorials/bank-reconciliations?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/bank-reconciliations; https://help.vtex.com/en/docs/tutorials/bank-reconciliations |
| 4 | [help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source...](https://help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/conciliacoes-bancarias; https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias |

---

<a id="query-7"></a>

### 7. `conciliations-payment-01` — llm.chatgpt (es/naive)

**Query:** cómo gestionar conciliaciones bancarias para pagos con boleto en vtex

| Field | Value |
|-------|-------|
| Issue | `conciliations-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `es` / `naive` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `es`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[es]` [https://help.vtex.com/es/tutorial/conciliaciones-bancarias](https://help.vtex.com/es/tutorial/conciliaciones-bancarias)
- `[es]` [https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias](https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/conciliacoes-bancarias](https://help.vtex.com/pt/tutorial/conciliacoes-bancarias)
- `[en]` [https://help.vtex.com/en/docs/tutorials/bank-reconciliations](https://help.vtex.com/en/docs/tutorials/bank-reconciliations)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias](https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias)

**Helpful (same locale)**

- `[es]` [https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo](https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto](https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto)
- `[es]` [https://help.vtex.com/es/docs/tutorials/pedidos-vision-general](https://help.vtex.com/es/docs/tutorials/pedidos-vision-general)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento](https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto](https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral](https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral)
- `[en]` [https://help.vtex.com/en/docs/tutorials/registered-ticket-flow](https://help.vtex.com/en/docs/tutorials/registered-ticket-flow)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[en]` [https://help.vtex.com/en/docs/tutorials/orders-overview](https://help.vtex.com/en/docs/tutorials/orders-overview)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt](https://help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/conciliacoes-bancarias; https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias |
| 8 | [help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source...](https://help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/conciliacoes-bancarias; https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias |

---

<a id="query-8"></a>

### 8. `conciliations-payment-01` — llm.chatgpt (es/expert)

**Query:** cómo gestionar conciliaciones bancarias en pagos vtex

| Field | Value |
|-------|-------|
| Issue | `conciliations-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `es` / `expert` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `es`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[es]` [https://help.vtex.com/es/tutorial/conciliaciones-bancarias](https://help.vtex.com/es/tutorial/conciliaciones-bancarias)
- `[es]` [https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias](https://help.vtex.com/es/docs/tutorials/conciliaciones-bancarias)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/conciliacoes-bancarias](https://help.vtex.com/pt/tutorial/conciliacoes-bancarias)
- `[en]` [https://help.vtex.com/en/docs/tutorials/bank-reconciliations](https://help.vtex.com/en/docs/tutorials/bank-reconciliations)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias](https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias)

**Helpful (same locale)**

- `[es]` [https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo](https://help.vtex.com/es/docs/tutorials/boleto-bancario-registrado-flujo)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto](https://help.vtex.com/es/docs/tutorials/como-se-hace-la-aprobacion-de-pago-del-boleto)
- `[es]` [https://help.vtex.com/es/docs/tutorials/pedidos-vision-general](https://help.vtex.com/es/docs/tutorials/pedidos-vision-general)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento](https://help.vtex.com/pt/docs/tutorials/boleto-bancario-registrado-fluxo-basico-de-um-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto](https://help.vtex.com/pt/docs/tutorials/como-e-feita-a-aprovacao-de-pagamento-do-boleto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral](https://help.vtex.com/pt/docs/tutorials/gerenciamento-de-pedidos-visao-geral)
- `[en]` [https://help.vtex.com/en/docs/tutorials/registered-ticket-flow](https://help.vtex.com/en/docs/tutorials/registered-ticket-flow)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved](https://help.vtex.com/en/docs/tutorials/how-are-the-payments-made-through-bank-slips-approved)
- `[en]` [https://help.vtex.com/en/docs/tutorials/orders-overview](https://help.vtex.com/en/docs/tutorials/orders-overview)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source...](https://help.vtex.com/docs/tutorials/conciliacoes-bancarias?locale=pt&utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/conciliacoes-bancarias; https://help.vtex.com/pt/docs/tutorials/conciliacoes-bancarias |

---

<a id="query-9"></a>

### 9. `conditions-payment-01` — external-search.google-search-playwright (es/naive)

**Query:** cómo configurar condiciones especiales para métodos de pago en vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `es` / `naive` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `es`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Helpful (same locale)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 6 | [help.vtex.com/docs/tutorials/condicoes-especiais?locale=en](https://help.vtex.com/docs/tutorials/condicoes-especiais?locale=en) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/condicoes-especiais; https://help.vtex.com/pt/docs/tutorials/condicoes-especiais |

---

<a id="query-10"></a>

### 10. `conditions-payment-01` — external-search.google-search-playwright (es/familiar)

**Query:** configurar condiciones especiales de pago vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `es` / `familiar` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `es`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Helpful (same locale)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 4 | [help.vtex.com/en/tutorial/condicoes-especiais](https://help.vtex.com/en/tutorial/condicoes-especiais) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/condicoes-especiais; https://help.vtex.com/pt/docs/tutorials/condicoes-especiais |

---

<a id="query-11"></a>

### 11. `conditions-payment-01` — external-search.google-search-playwright (pt/naive)

**Query:** como configurar condições especiais para métodos de pagamento no vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `pt` / `naive` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 4 | [help.vtex.com/docs/tutorials/condicoes-especiais?locale=en](https://help.vtex.com/docs/tutorials/condicoes-especiais?locale=en) | `target_doc` → `target_doc_different_loc` | unresolved (stored as `target_doc`; strict baseline: https://help.vtex.com/pt/tutorial/condicoes-especiais) | https://help.vtex.com/pt/tutorial/condicoes-especiais; https://help.vtex.com/pt/docs/tutorials/condicoes-especiais |

---

<a id="query-12"></a>

### 12. `conditions-payment-01` — external-search.google-search-playwright (pt/familiar)

**Query:** configurar condições especiais de pagamento vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `pt` / `familiar` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/en/tutorial/condicoes-especiais](https://help.vtex.com/en/tutorial/condicoes-especiais) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/tutorial/condicoes-especiais; https://help.vtex.com/pt/docs/tutorials/condicoes-especiais |

---

<a id="query-13"></a>

### 13. `conditions-payment-01` — external-search.google-search-playwright (pt/expert)

**Query:** condições especiais vtex pagamentos

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `pt` / `expert` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [help.vtex.com/docs/tutorials/condicoes-especiais?locale=en](https://help.vtex.com/docs/tutorials/condicoes-especiais?locale=en) | `target_doc` → `target_doc_different_loc` | unresolved (stored as `target_doc`; strict baseline: https://help.vtex.com/pt/tutorial/condicoes-especiais) | https://help.vtex.com/pt/tutorial/condicoes-especiais; https://help.vtex.com/pt/docs/tutorials/condicoes-especiais |

---

<a id="query-14"></a>

### 14. `conditions-payment-01` — llm.chatgpt (en/naive)

**Query:** how do i configure special conditions for payment methods in vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `en` / `naive` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/special-conditions](https://help.vtex.com/docs/tutorials/special-conditions)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/docs/tracks/configuring-a-payment-condition)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings](https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments](https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments](https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com](https://help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/special-conditions; https://help.vtex.com/en/docs/tutorials/special-conditions |

---

<a id="query-15"></a>

### 15. `conditions-payment-01` — llm.chatgpt (en/familiar)

**Query:** steps to set special conditions for vtex payment methods

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `en` / `familiar` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/special-conditions](https://help.vtex.com/docs/tutorials/special-conditions)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/docs/tracks/configuring-a-payment-condition)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings](https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments](https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments](https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com](https://help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/special-conditions; https://help.vtex.com/en/docs/tutorials/special-conditions |

---

<a id="query-16"></a>

### 16. `conditions-payment-01` — llm.chatgpt (en/expert)

**Query:** how to configure special conditions for payment methods in vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `en` / `expert` |
| Result flags | `?locale=` · Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/special-conditions](https://help.vtex.com/docs/tutorials/special-conditions)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/docs/tracks/configuring-a-payment-condition)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings](https://help.vtex.com/docs/tracks/vtex-modules-ii#optional-payments-settings)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments](https://help.vtex.com/docs/tutorials/how-trade-policies-work#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments](https://help.vtex.com/docs/tutorials/configuring-a-marketplace-trade-policy#payments)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/docs/tutorials/what-is-the-issuing-bank)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com](https://help.vtex.com/pt/docs/tutorials/special-conditions?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/special-conditions; https://help.vtex.com/en/docs/tutorials/special-conditions |

---

<a id="query-17"></a>

### 17. `conditions-payment-01` — llm.chatgpt (es/expert)

**Query:** cómo configurar condiciones especiales para métodos de pago en vtex

| Field | Value |
|-------|-------|
| Issue | `conditions-payment-01` |
| Source | `llm.chatgpt` |
| Locale / style | `es` / `expert` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `es`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[es]` [https://help.vtex.com/es/tutorial/condiciones-especiales](https://help.vtex.com/es/tutorial/condiciones-especiales)
- `[es]` [https://help.vtex.com/es/docs/tutorials/condiciones-especiales](https://help.vtex.com/es/docs/tutorials/condiciones-especiales)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/condicoes-especiais](https://help.vtex.com/pt/tutorial/condicoes-especiais)
- `[en]` [https://help.vtex.com/en/docs/tutorials/special-conditions](https://help.vtex.com/en/docs/tutorials/special-conditions)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/condicoes-especiais](https://help.vtex.com/pt/docs/tutorials/condicoes-especiais)

**Helpful (same locale)**

- `[es]` [https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago](https://help.vtex.com/es/docs/tracks/configurar-una-condicion-de-pago)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii#ajustes-opcionales-en-pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace#pagos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor](https://help.vtex.com/es/docs/tutorials/que-es-el-banco-emisor)
- `[es]` [https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii](https://help.vtex.com/es/docs/tracks/modulos-de-vtex-ii)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial](https://help.vtex.com/es/docs/tutorials/como-funciona-una-politica-comercial)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace](https://help.vtex.com/es/docs/tutorials/configurar-politica-comercial-para-marketplace)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento](https://help.vtex.com/pt/docs/tracks/configurar-uma-condicao-de-pagamento)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii#configuracoes-opcionais-em-pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace#pagamentos)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor](https://help.vtex.com/pt/docs/tutorials/o-que-e-banco-emissor)
- `[en]` [https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition](https://help.vtex.com/en/docs/tracks/configuring-a-payment-condition)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-modules-ii](https://help.vtex.com/en/docs/tracks/vtex-modules-ii)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii](https://help.vtex.com/pt/docs/tracks/modulos-da-vtex-ii)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-trade-policies-work](https://help.vtex.com/en/docs/tutorials/how-trade-policies-work)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial](https://help.vtex.com/pt/docs/tutorials/como-funciona-uma-politica-comercial)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy](https://help.vtex.com/en/docs/tutorials/configuring-a-marketplace-trade-policy)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace](https://help.vtex.com/pt/docs/tutorials/configurando-a-politica-comercial-para-marketplace)
- `[en]` [https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank](https://help.vtex.com/en/docs/tutorials/what-is-the-issuing-bank)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [help.vtex.com/en/docs/tutorials/condiciones-especiales?utm_source=chatgpt.com](https://help.vtex.com/en/docs/tutorials/condiciones-especiales?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/es/tutorial/condiciones-especiales; https://help.vtex.com/es/docs/tutorials/condiciones-especiales |

---

<a id="query-18"></a>

### 18. `content-delivery-optimization-01` — internal-search.hybrid-search (en/naive)

**Query:** content delivery optimization

| Field | Value |
|-------|-------|
| Issue | `content-delivery-optimization-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `naive` |
| Result flags | developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/cloud-infrastructure](https://developers.vtex.com/docs/guides/cloud-infrastructure)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex](https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex](https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex](https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |

---

<a id="query-19"></a>

### 19. `content-delivery-optimization-01` — internal-search.hybrid-search (en/familiar)

**Query:** CDN caching content delivery

| Field | Value |
|-------|-------|
| Issue | `content-delivery-optimization-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/cloud-infrastructure](https://developers.vtex.com/docs/guides/cloud-infrastructure)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex](https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex](https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex](https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |
| 3 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |
| 3 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |

---

<a id="query-20"></a>

### 20. `content-delivery-optimization-01` — internal-search.hybrid-search (en/expert)

**Query:** cloud infrastructure content delivery optimization

| Field | Value |
|-------|-------|
| Issue | `content-delivery-optimization-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/cloud-infrastructure](https://developers.vtex.com/docs/guides/cloud-infrastructure)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex](https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex](https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex](https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 6 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |
| 6 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |
| 6 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |
| 6 | [developers.vtex.com/cloud-infrastructure](https://developers.vtex.com/cloud-infrastructure) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/cloud-infrastructure) | none |

---

<a id="query-21"></a>

### 21. `customer-credit-01` — internal-search.hybrid-search (en/naive)

**Query:** customer credit api

| Field | Value |
|-------|-------|
| Issue | `customer-credit-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `naive` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/customer-credit-integration-guide](https://developers.vtex.com/docs/guides/customer-credit-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice](https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/customer-credit-overview](https://help.vtex.com/docs/tutorials/customer-credit-overview)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api](https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api)
- `[en]` [https://help.vtex.com/en/docs/tutorials/customer-credit-overview](https://help.vtex.com/en/docs/tutorials/customer-credit-overview)
- `[en]` [https://help.vtex.com/en/docs/tracks/creating-accounts](https://help.vtex.com/en/docs/tracks/creating-accounts)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral](https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral)
- `[es]` [https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general](https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api](https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api](https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas](https://help.vtex.com/pt/docs/tracks/criando-contas)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas](https://help.vtex.com/es/docs/tracks/creando-cuentas)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 3 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 8 | [developers.vtex.com/managing-a-customer-credit-invoice](https://developers.vtex.com/managing-a-customer-credit-invoice) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 9 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 9 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |

---

<a id="query-22"></a>

### 22. `customer-credit-01` — internal-search.hybrid-search (en/familiar)

**Query:** manage customer credit account

| Field | Value |
|-------|-------|
| Issue | `customer-credit-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/customer-credit-integration-guide](https://developers.vtex.com/docs/guides/customer-credit-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice](https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/customer-credit-overview](https://help.vtex.com/docs/tutorials/customer-credit-overview)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api](https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api)
- `[en]` [https://help.vtex.com/en/docs/tutorials/customer-credit-overview](https://help.vtex.com/en/docs/tutorials/customer-credit-overview)
- `[en]` [https://help.vtex.com/en/docs/tracks/creating-accounts](https://help.vtex.com/en/docs/tracks/creating-accounts)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral](https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral)
- `[es]` [https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general](https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api](https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api](https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas](https://help.vtex.com/pt/docs/tracks/criando-contas)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas](https://help.vtex.com/es/docs/tracks/creando-cuentas)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 5 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 5 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |

---

<a id="query-23"></a>

### 23. `customer-credit-01` — internal-search.hybrid-search (en/expert)

**Query:** managing a customer credit account

| Field | Value |
|-------|-------|
| Issue | `customer-credit-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/customer-credit-integration-guide](https://developers.vtex.com/docs/guides/customer-credit-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice](https://developers.vtex.com/docs/guides/managing-a-customer-credit-invoice)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/managing-a-customer-credit-account](https://developers.vtex.com/docs/guides/managing-a-customer-credit-account)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/customer-credit-overview](https://help.vtex.com/docs/tutorials/customer-credit-overview)
- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api](https://help.vtex.com/docs/tracks/creating-accounts#create-account-via-api)
- `[en]` [https://help.vtex.com/en/docs/tutorials/customer-credit-overview](https://help.vtex.com/en/docs/tutorials/customer-credit-overview)
- `[en]` [https://help.vtex.com/en/docs/tracks/creating-accounts](https://help.vtex.com/en/docs/tracks/creating-accounts)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral](https://help.vtex.com/pt/docs/tutorials/customer-credit-visao-geral)
- `[es]` [https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general](https://help.vtex.com/es/docs/tutorials/customer-credit-vision-general)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api](https://help.vtex.com/pt/docs/tracks/criando-contas#criar-conta-via-api)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api](https://help.vtex.com/es/docs/tracks/creando-cuentas#crear-cuenta-a-traves-de-api)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/criando-contas](https://help.vtex.com/pt/docs/tracks/criando-contas)
- `[es]` [https://help.vtex.com/es/docs/tracks/creando-cuentas](https://help.vtex.com/es/docs/tracks/creando-cuentas)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 4 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 4 | [developers.vtex.com/customer-credit-integration-guide](https://developers.vtex.com/customer-credit-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/customer-credit-integration-guide) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |
| 10 | [developers.vtex.com/managing-a-customer-credit-account](https://developers.vtex.com/managing-a-customer-credit-account) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/managing-a-customer-credit-account) | none |

---

<a id="query-24"></a>

### 24. `payment-provider-01` — internal-search.hybrid-search (en/naive)

**Query:** add payment provider vtex

| Field | Value |
|-------|-------|
| Issue | `payment-provider-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `naive` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-overview](https://developers.vtex.com/docs/guides/payments-overview)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework](https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-guide](https://developers.vtex.com/docs/guides/payments-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-composable-components](https://developers.vtex.com/docs/guides/vtex-composable-components)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [developers.vtex.com/payments-integration-payment-provider-framework](https://developers.vtex.com/payments-integration-payment-provider-framework) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 5 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |

---

<a id="query-25"></a>

### 25. `payment-provider-01` — internal-search.hybrid-search (en/familiar)

**Query:** payment provider integration

| Field | Value |
|-------|-------|
| Issue | `payment-provider-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-overview](https://developers.vtex.com/docs/guides/payments-overview)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework](https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-guide](https://developers.vtex.com/docs/guides/payments-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-composable-components](https://developers.vtex.com/docs/guides/vtex-composable-components)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [developers.vtex.com/payments-overview](https://developers.vtex.com/payments-overview) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 5 | [developers.vtex.com/payments-integration-guide](https://developers.vtex.com/payments-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 9 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |
| 9 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |
| 9 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |
| 10 | [developers.vtex.com/vtex-composable-components](https://developers.vtex.com/vtex-composable-components) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |

---

<a id="query-26"></a>

### 26. `payment-provider-01` — internal-search.hybrid-search (en/expert)

**Query:** integrating a new payment provider on vtex

| Field | Value |
|-------|-------|
| Issue | `payment-provider-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-overview](https://developers.vtex.com/docs/guides/payments-overview)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework](https://developers.vtex.com/docs/guides/payments-integration-payment-provider-framework)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-guide](https://developers.vtex.com/docs/guides/payments-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-composable-components](https://developers.vtex.com/docs/guides/vtex-composable-components)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [developers.vtex.com/payments-integration-payment-provider-framework](https://developers.vtex.com/payments-integration-payment-provider-framework) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 3 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |
| 3 | [developers.vtex.com/integrating-a-new-payment-provider-on-vtex](https://developers.vtex.com/integrating-a-new-payment-provider-on-vtex) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/integrating-a-new-payment-provider-on-vtex) | none |
| 5 | [developers.vtex.com/payments-integration-guide](https://developers.vtex.com/payments-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 7 | [developers.vtex.com/payments-overview](https://developers.vtex.com/payments-overview) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |
| 9 | [developers.vtex.com/vtex-composable-components](https://developers.vtex.com/vtex-composable-components) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-overview) | none |

---

<a id="query-27"></a>

### 27. `payment-provider-02` — internal-search.hybrid-search (en/familiar)

**Query:** payment provider implementation

| Field | Value |
|-------|-------|
| Issue | `payment-provider-02` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider](https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-guide](https://developers.vtex.com/docs/guides/payments-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-purchase-flows](https://developers.vtex.com/docs/guides/payments-integration-purchase-flows)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider](https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 4 | [developers.vtex.com/payments-integration-implementing-a-payment-prov...](https://developers.vtex.com/payments-integration-implementing-a-payment-provider) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider) | none |
| 4 | [developers.vtex.com/payments-integration-implementing-a-payment-prov...](https://developers.vtex.com/payments-integration-implementing-a-payment-provider) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider) | none |

---

<a id="query-28"></a>

### 28. `payment-provider-02` — internal-search.hybrid-search (en/expert)

**Query:** implementing a payment provider

| Field | Value |
|-------|-------|
| Issue | `payment-provider-02` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider](https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-guide](https://developers.vtex.com/docs/guides/payments-integration-guide)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-purchase-flows](https://developers.vtex.com/docs/guides/payments-integration-purchase-flows)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider](https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [developers.vtex.com/payments-integration-implementing-a-payment-prov...](https://developers.vtex.com/payments-integration-implementing-a-payment-provider) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-integration-implementing-a-payment-provider) | none |
| 10 | [developers.vtex.com/payments-integration-guide](https://developers.vtex.com/payments-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/payments-integration-guide) | none |

---

<a id="query-29"></a>

### 29. `product-indexing-01` — llm.chatgpt (pt/naive)

**Query:** Por que as atualizações dos meus produtos não aparecem quando os clientes pesquisam na minha loja VTEX?

| Field | Value |
|-------|-------|
| Issue | `product-indexing-01` |
| Source | `llm.chatgpt` |
| Locale / style | `pt` / `naive` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/tutorial/entendendo-o-funcionamento-da-indexacao](https://help.vtex.com/pt/tutorial/entendendo-o-funcionamento-da-indexacao)
- `[pt]` [https://help.vtex.com/pt/troubleshooting/nao-consigo-indexar-um-produto-do-catalogo](https://help.vtex.com/pt/troubleshooting/nao-consigo-indexar-um-produto-do-catalogo)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/utilizar-o-relatorio-de-indexacao](https://help.vtex.com/pt/docs/tutorials/utilizar-o-relatorio-de-indexacao)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/entendendo-o-funcionamento-da-indexacao](https://help.vtex.com/pt/docs/tutorials/entendendo-o-funcionamento-da-indexacao)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/tutorial/entendiendo-el-funcionamento-de-la-indexacion](https://help.vtex.com/es/tutorial/entendiendo-el-funcionamento-de-la-indexacion)
- `[es]` [https://help.vtex.com/es/troubleshooting/no-logro-indexar-un-producto-del-catalogo](https://help.vtex.com/es/troubleshooting/no-logro-indexar-un-producto-del-catalogo)
- `[es]` [https://help.vtex.com/es/docs/tutorials/utilizando-el-informe-de-indexacion](https://help.vtex.com/es/docs/tutorials/utilizando-el-informe-de-indexacion)
- `[en]` [https://help.vtex.com/en/docs/tutorials/understanding-how-indexation-works](https://help.vtex.com/en/docs/tutorials/understanding-how-indexation-works)
- `[es]` [https://help.vtex.com/es/docs/tutorials/entendiendo-el-funcionamento-de-la-indexacion](https://help.vtex.com/es/docs/tutorials/entendiendo-el-funcionamento-de-la-indexacion)
- `[en]` [https://help.vtex.com/en/troubleshooting/i-cant-index-a-product-in-the-catalog](https://help.vtex.com/en/troubleshooting/i-cant-index-a-product-in-the-catalog)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-to-use-the-index-report](https://help.vtex.com/en/docs/tutorials/how-to-use-the-index-report)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site](https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site)

**Helpful (other locales)**

- `[en]` [https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website](https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website)
- `[es]` [https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web](https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/es/troubleshooting/nao-consigo-indexar-um-produt...?utm_source=chatgpt.com](https://help.vtex.com/es/troubleshooting/nao-consigo-indexar-um-produto-do-catalogo?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/troubleshooting/nao-consigo-indexar-um-produto-do-catalogo |
| 4 | [help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com](https://help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com) | `unrelated` → `other_helpful_doc_different_loc` | none | https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site |

---

<a id="query-30"></a>

### 30. `product-not-visible-01` — llm.chatgpt (pt/familiar)

**Query:** Por que o meu produto VTEX não está aparecendo no site?

| Field | Value |
|-------|-------|
| Issue | `product-not-visible-01` |
| Source | `llm.chatgpt` |
| Locale / style | `pt` / `familiar` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site](https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web](https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web)
- `[en]` [https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website](https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-produto](https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-produto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-sku](https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-sku)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/produtos-e-skus](https://help.vtex.com/pt/docs/tutorials/produtos-e-skus)

**Helpful (other locales)**

- `[es]` [https://help.vtex.com/es/docs/tutorials/agregar-o-editar-productos](https://help.vtex.com/es/docs/tutorials/agregar-o-editar-productos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/agregar-o-editar-skus](https://help.vtex.com/es/docs/tutorials/agregar-o-editar-skus)
- `[es]` [https://help.vtex.com/es/docs/tutorials/productos-y-skus](https://help.vtex.com/es/docs/tutorials/productos-y-skus)
- `[en]` [https://help.vtex.com/en/docs/tutorials/adding-or-editing-products](https://help.vtex.com/en/docs/tutorials/adding-or-editing-products)
- `[en]` [https://help.vtex.com/en/docs/tutorials/adding-or-editing-skus](https://help.vtex.com/en/docs/tutorials/adding-or-editing-skus)
- `[en]` [https://help.vtex.com/en/docs/tutorials/products-and-skus](https://help.vtex.com/en/docs/tutorials/products-and-skus)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com](https://help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site |

---

<a id="query-31"></a>

### 31. `product-not-visible-01` — llm.chatgpt (pt/expert)

**Query:** Por que o produto não está visível no site no VTEX?

| Field | Value |
|-------|-------|
| Issue | `product-not-visible-01` |
| Source | `llm.chatgpt` |
| Locale / style | `pt` / `expert` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `llm.chatgpt`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site](https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web](https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web)
- `[en]` [https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website](https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-produto](https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-produto)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-sku](https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-sku)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/produtos-e-skus](https://help.vtex.com/pt/docs/tutorials/produtos-e-skus)

**Helpful (other locales)**

- `[es]` [https://help.vtex.com/es/docs/tutorials/agregar-o-editar-productos](https://help.vtex.com/es/docs/tutorials/agregar-o-editar-productos)
- `[es]` [https://help.vtex.com/es/docs/tutorials/agregar-o-editar-skus](https://help.vtex.com/es/docs/tutorials/agregar-o-editar-skus)
- `[es]` [https://help.vtex.com/es/docs/tutorials/productos-y-skus](https://help.vtex.com/es/docs/tutorials/productos-y-skus)
- `[en]` [https://help.vtex.com/en/docs/tutorials/adding-or-editing-products](https://help.vtex.com/en/docs/tutorials/adding-or-editing-products)
- `[en]` [https://help.vtex.com/en/docs/tutorials/adding-or-editing-skus](https://help.vtex.com/en/docs/tutorials/adding-or-editing-skus)
- `[en]` [https://help.vtex.com/en/docs/tutorials/products-and-skus](https://help.vtex.com/en/docs/tutorials/products-and-skus)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 1 | [help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com](https://help.vtex.com/en/faq/por-que-o-produto-nao-aparece-no-site?utm_source=chatgpt.com) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site |

---

<a id="query-32"></a>

### 32. `pwa-implementation-01` — llm.gemini (en/naive)

**Query:** I want my customers to be able to install my VTEX store website on their phones like an app. How do I do that?

| Field | Value |
|-------|-------|
| Issue | `pwa-implementation-01` |
| Source | `llm.gemini` |
| Locale / style | `en` / `naive` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `False` → `False` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `False` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `llm.gemini`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://help.vtex.com/docs/tutorials/configuring-pwa-in-your-store-framework-store](https://help.vtex.com/docs/tutorials/configuring-pwa-in-your-store-framework-store)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-to-turn-my-store-website-into-a-pwa](https://help.vtex.com/en/docs/tutorials/how-to-turn-my-store-website-into-a-pwa)
- `[en]` [https://help.vtex.com/en/docs/tutorials/enabling-pwa-push-notifications-in-your-store](https://help.vtex.com/en/docs/tutorials/enabling-pwa-push-notifications-in-your-store)
- `[en]` [https://help.vtex.com/en/docs/tutorials/configuring-pwa-in-your-store-framework-store](https://help.vtex.com/en/docs/tutorials/configuring-pwa-in-your-store-framework-store)

**Target (other locales)**

- `[pt]` [https://help.vtex.com/pt/tutorial/configurando-pwa-em-sua-loja-store-framework](https://help.vtex.com/pt/tutorial/configurando-pwa-em-sua-loja-store-framework)
- `[es]` [https://help.vtex.com/es/tutorial/configurar-pwa-en-tu-tienda-store-framework](https://help.vtex.com/es/tutorial/configurar-pwa-en-tu-tienda-store-framework)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-transformar-o-site-da-minha-loja-em-um-pwa](https://help.vtex.com/pt/docs/tutorials/como-transformar-o-site-da-minha-loja-em-um-pwa)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-transformar-el-sitio-de-mi-tienda-en-un-pwa](https://help.vtex.com/es/docs/tutorials/como-transformar-el-sitio-de-mi-tienda-en-un-pwa)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/habilitando-notificacoes-pwa-da-loja](https://help.vtex.com/pt/docs/tutorials/habilitando-notificacoes-pwa-da-loja)
- `[es]` [https://help.vtex.com/es/docs/tutorials/habilitar-las-notificaciones-pwa-de-la-tienda](https://help.vtex.com/es/docs/tutorials/habilitar-las-notificaciones-pwa-de-la-tienda)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/configurando-pwa-em-sua-loja-store-framework](https://help.vtex.com/pt/docs/tutorials/configurando-pwa-em-sua-loja-store-framework)
- `[es]` [https://help.vtex.com/es/docs/tutorials/configurar-pwa-en-tu-tienda-store-framework](https://help.vtex.com/es/docs/tutorials/configurar-pwa-en-tu-tienda-store-framework)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/how-to-install-a-service-worker](https://help.vtex.com/en/docs/tutorials/how-to-install-a-service-worker)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-io-documentation-using-several-service-workers-in-your-store](https://developers.vtex.com/docs/guides/vtex-io-documentation-using-several-service-workers-in-your-store)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/vtex-io-documentation-enabling-the-stores-pwa-notice](https://developers.vtex.com/docs/guides/vtex-io-documentation-enabling-the-stores-pwa-notice)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-instalar-um-service-worker](https://help.vtex.com/pt/docs/tutorials/como-instalar-um-service-worker)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-instalar-un-service-worker](https://help.vtex.com/es/docs/tutorials/como-instalar-un-service-worker)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 8 | [help.vtex.com/es/docs/tutorials/configuring-pwa-in-your-store-...](https://help.vtex.com/es/docs/tutorials/configuring-pwa-in-your-store-framework-store) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/docs/tutorials/configuring-pwa-in-your-store-framework-store; https://help.vtex.com/en/docs/tutorials/configuring-pwa-in-your-store-framework-store |

---

<a id="query-33"></a>

### 33. `sap-catalog-01` — internal-search.hybrid-search (en/naive)

**Query:** product catalog business software online store

| Field | Value |
|-------|-------|
| Issue | `sap-catalog-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `naive` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/catalog-overview](https://developers.vtex.com/docs/guides/catalog-overview)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/erp-integration-import-products](https://developers.vtex.com/docs/guides/erp-integration-import-products)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/erp-integration-guide](https://developers.vtex.com/docs/guides/erp-integration-guide)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [developers.vtex.com/catalog-overview](https://developers.vtex.com/catalog-overview) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/catalog-overview) | none |

---

<a id="query-34"></a>

### 34. `sap-catalog-01` — internal-search.hybrid-search (en/expert)

**Query:** integrate catalog SAP ERP VTEX backend

| Field | Value |
|-------|-------|
| Issue | `sap-catalog-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/catalog-overview](https://developers.vtex.com/docs/guides/catalog-overview)
- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/erp-integration-import-products](https://developers.vtex.com/docs/guides/erp-integration-import-products)

**Helpful (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/erp-integration-guide](https://developers.vtex.com/docs/guides/erp-integration-guide)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 3 | [developers.vtex.com/erp-integration-import-products](https://developers.vtex.com/erp-integration-import-products) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/catalog-overview) | none |
| 4 | [developers.vtex.com/erp-integration-guide](https://developers.vtex.com/erp-integration-guide) | `other_helpful_doc` → `unrelated` | unresolved (stored as `other_helpful_doc`; strict baseline: https://developers.vtex.com/docs/guides/erp-integration-guide) | none |
| 6 | [developers.vtex.com/catalog-overview](https://developers.vtex.com/catalog-overview) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/catalog-overview) | none |

---

<a id="query-35"></a>

### 35. `support-work-01` — external-search.google-search-playwright (pt/expert)

**Query:** planos de suporte VTEX sistema de tickets

| Field | Value |
|-------|-------|
| Issue | `support-work-01` |
| Source | `external-search.google-search-playwright` |
| Locale / style | `pt` / `expert` |
| Result flags | Help Center |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `True` |
| `target_different_loc_found` | `False` → `True` |
| `target_any_locale_found` | `True` → `True` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `pt`, source = `external-search.google-search-playwright`).

**Strict target (same locale)**

- `[pt]` [https://help.vtex.com/pt/tutorial/como-funciona-o-suporte-da-vtex](https://help.vtex.com/pt/tutorial/como-funciona-o-suporte-da-vtex)
- `[pt]` [https://help.vtex.com/pt/docs/tutorials/como-funciona-o-suporte-da-vtex](https://help.vtex.com/pt/docs/tutorials/como-funciona-o-suporte-da-vtex)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/funcionamento-do-suporte-vtex](https://help.vtex.com/pt/docs/tracks/funcionamento-do-suporte-vtex)
- `[pt]` [https://help.vtex.com/pt/docs/tracks/suporte-na-vtex](https://help.vtex.com/pt/docs/tracks/suporte-na-vtex)

**Target (other locales)**

- `[es]` [https://help.vtex.com/es/tutorial/como-funciona-el-soporte-de-vtex](https://help.vtex.com/es/tutorial/como-funciona-el-soporte-de-vtex)
- `[en]` [https://help.vtex.com/en/docs/tracks/how-vtex-support-works](https://help.vtex.com/en/docs/tracks/how-vtex-support-works)
- `[en]` [https://help.vtex.com/en/docs/tutorials/how-does-vtex-support-work](https://help.vtex.com/en/docs/tutorials/how-does-vtex-support-work)
- `[es]` [https://help.vtex.com/es/docs/tutorials/como-funciona-el-soporte-de-vtex](https://help.vtex.com/es/docs/tutorials/como-funciona-el-soporte-de-vtex)
- `[es]` [https://help.vtex.com/es/docs/tracks/funcionamiento-del-soporte-vtex](https://help.vtex.com/es/docs/tracks/funcionamiento-del-soporte-vtex)
- `[en]` [https://help.vtex.com/en/docs/tracks/vtex-support](https://help.vtex.com/en/docs/tracks/vtex-support)
- `[es]` [https://help.vtex.com/es/docs/tracks/soporte-vtex](https://help.vtex.com/es/docs/tracks/soporte-vtex)

**Helpful (same locale)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/abrir-chamados-para-o-suporte-vtex](https://help.vtex.com/pt/docs/tutorials/abrir-chamados-para-o-suporte-vtex)

**Helpful (other locales)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/opening-tickets-to-vtex-support](https://help.vtex.com/en/docs/tutorials/opening-tickets-to-vtex-support)
- `[es]` [https://help.vtex.com/es/docs/tutorials/abrir-tickets-para-el-soporte-vtex](https://help.vtex.com/es/docs/tutorials/abrir-tickets-para-el-soporte-vtex)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 4 | [help.vtex.com/es/docs/tracks/funcionamento-do-suporte-vtex](https://help.vtex.com/es/docs/tracks/funcionamento-do-suporte-vtex) | `unrelated` → `target_doc_different_loc` | none | https://help.vtex.com/pt/docs/tracks/funcionamento-do-suporte-vtex |

---

<a id="query-36"></a>

### 36. `webstore-oauth2-01` — internal-search.hybrid-search (en/naive)

**Query:** custom login external identity

| Field | Value |
|-------|-------|
| Issue | `webstore-oauth2-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `naive` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2](https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication](https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2](https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2)
- `[es]` [https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2](https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |

---

<a id="query-37"></a>

### 37. `webstore-oauth2-01` — internal-search.hybrid-search (en/familiar)

**Query:** OAuth webstore identity provider configure

| Field | Value |
|-------|-------|
| Issue | `webstore-oauth2-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `familiar` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2](https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication](https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2](https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2)
- `[es]` [https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2](https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 10 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |

---

<a id="query-38"></a>

### 38. `webstore-oauth2-01` — internal-search.hybrid-search (en/expert)

**Query:** login integration guide webstore OAuth2

| Field | Value |
|-------|-------|
| Issue | `webstore-oauth2-01` |
| Source | `internal-search.hybrid-search` |
| Locale / style | `en` / `expert` |
| Result flags | Help Center · developers.vtex.com |

#### Metric changes

| Metric | Stored → new |
|--------|--------------|
| `target_found` | `True` → `False` |
| `target_different_loc_found` | `False` → `False` |
| `target_any_locale_found` | `True` → `False` |

#### Catalog baseline

Issue catalog URLs used for matching (query locale = `en`, source = `internal-search.hybrid-search`).

**Strict target (same locale)**

- `[locale-less (bridged to query locale)]` [https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2](https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2)

**Helpful (same locale)**

- `[en]` [https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication](https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication)

**Helpful (other locales)**

- `[pt]` [https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2](https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2)
- `[es]` [https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2](https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2)

#### Test links reclassified

| Rank | Test URL | Stored → new | Catalog match (stored) | Catalog match (new) |
|-----:|----------|--------------|------------------------|---------------------|
| 2 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |
| 2 | [developers.vtex.com/login-integration-guide-webstore-oauth2](https://developers.vtex.com/login-integration-guide-webstore-oauth2) | `target_doc` → `unrelated` | unresolved (stored as `target_doc`; strict baseline: https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2) | none |

---
