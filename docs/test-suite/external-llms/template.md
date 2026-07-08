# External LLMs Test: {issue_id}

| Field | Value |
|-------|--------|
| **issue_id** | {issue_id} |
| **persona** | {persona} |
| **product** | {product} |
| **user_intent** | {user_intent} |
| **target_doc_url** | {target_doc_url} |
| **test_date** | {YYYY-MM-DD} |
| **tester** | {tester_name} |

---

## Instructions

1. **Click URLs** for ChatGPT and Gemini
2. **Copy the LLM response** (including markdown and links)
3. **Paste into the Response section** below each query
4. **Commit** this file to main to keep records

**Note:** Processing and evaluation of responses will be done separately. This document is for recording raw responses only.

**Note:** Ensure [Gemini URL Prompt extension](https://chromewebstore.google.com/detail/gemini-url-prompt/kdbgjkfdooaiompgeckjbegnnccchmma) is installed for Gemini URLs to work.

---

## Queries (query_llm)

### Naive query

**Query:** {naive_query}

**Full prompt:**
```
{naive_query}

Please provide your answer in copiable markdown format and include all links you used to answer this question.
```

#### P0 — ChatGPT (Priority: Must)

- **URL:** [{naive_query}](https://chat.openai.com/?q={naive_query_encoded})
- **Response:**
  ```
  [Paste ChatGPT response here]
  ```

#### P0 — Gemini (Priority: Must)

- **URL:** [{naive_query}](https://gemini.google.com/app?prompt={naive_query_encoded})
- **Response:**
  ```
  [Paste Gemini response here]
  ```

---

### Familiar query

**Query:** {familiar_query}

**Full prompt:**
```
{familiar_query}

Please provide your answer in copiable markdown format and include all links you used to answer this question.
```

#### P0 — ChatGPT (Priority: Must)

- **URL:** [{familiar_query}](https://chat.openai.com/?q={familiar_query_encoded})
- **Response:**
  ```
  [Paste ChatGPT response here]
  ```

#### P0 — Gemini (Priority: Must)

- **URL:** [{familiar_query}](https://gemini.google.com/app?prompt={familiar_query_encoded})
- **Response:**
  ```
  [Paste Gemini response here]
  ```

---

### Expert query

**Query:** {expert_query}

**Full prompt:**
```
{expert_query}

Please provide your answer in copiable markdown format and include all links you used to answer this question.
```

#### P0 — ChatGPT (Priority: Must)

- **URL:** [{expert_query}](https://chat.openai.com/?q={expert_query_encoded})
- **Response:**
  ```
  [Paste ChatGPT response here]
  ```

#### P0 — Gemini (Priority: Must)

- **URL:** [{expert_query}](https://gemini.google.com/app?prompt={expert_query_encoded})
- **Response:**
  ```
  [Paste Gemini response here]
  ```

