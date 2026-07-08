#!/usr/bin/env node
/**
 * VTEX Docs Assistant Path Runner
 * 
 * Runs queries from the test suite through the VTEX Docs Assistant API
 * (https://docs-assistant.vtex.com/stream) and outputs results in the
 * unified format documented in docs/test-suite/results-layout.md.
 * 
 * Usage:
 *   node scripts/run-docs-assistant-path.js [options]
 * 
 * Options:
 *   --run-id TEXT           Run identifier (default: docs-assistant-run-YYYY-MM-DD-HHmmss)
 *   --issues TEXT           Comma-separated issue IDs to filter (default: all)
 *   --top-n INT             Number of top results to capture (default: 10)
 *   --output-dir TEXT       Output directory (default: results/docs-assistant)
 *   --generate-analysis     Generate markdown analysis report (default: true)
 *   --no-generate-analysis  Skip markdown analysis report
 *   --delay INT             Delay between API calls in ms (default: 1000)
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

function pad2(value) {
  return String(value).padStart(2, '0');
}

function formatRunFolderTimestamp(date) {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())} ${pad2(date.getHours())}-${pad2(date.getMinutes())}`;
}

function createRunDirectory(baseDir, variantSlug, pathSlug, date = new Date()) {
  const variantDir = path.join(baseDir, variantSlug);
  const baseName = `${pathSlug} ${formatRunFolderTimestamp(date)}`;
  let candidate = path.join(variantDir, baseName);
  let suffix = 2;
  while (fs.existsSync(candidate)) {
    candidate = path.join(variantDir, `${baseName} (${suffix})`);
    suffix += 1;
  }
  fs.mkdirSync(candidate, { recursive: true });
  return candidate;
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    runId: null,
    issues: null,
    topN: 10,
    outputDir: 'results/docs-assistant',
    generateAnalysis: true,
    delay: 1000
  };
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--run-id':
        options.runId = args[++i];
        break;
      case '--issues':
        options.issues = args[++i].split(',').map(s => s.trim());
        break;
      case '--top-n':
        options.topN = parseInt(args[++i], 10);
        break;
      case '--output-dir':
        options.outputDir = args[++i];
        break;
      case '--generate-analysis':
        options.generateAnalysis = true;
        break;
      case '--no-generate-analysis':
        options.generateAnalysis = false;
        break;
      case '--delay':
        options.delay = parseInt(args[++i], 10);
        break;
    }
  }
  
  if (!options.runId) {
    const now = new Date();
    const dateStr = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
    options.runId = `docs-assistant-run-${dateStr}`;
  }
  
  return options;
}

// Load target_doc_url from an issue markdown file (secondary metadata lookup)
function loadTargetDocUrl(filepath) {
  try {
    const content = fs.readFileSync(filepath, 'utf-8');
    const match = content.match(/\|\s*\*\*(target_doc_url|expected_doc_url)\*\*\s*\|\s*([^|]+)\s*\|/);
    return match ? match[2].trim() : null;
  } catch (e) {
    return null;
  }
}

// Build a map of issue_id -> target_doc_url from all issue .md files
function loadTargetDocUrls(issuesDir) {
  const map = {};
  try {
    const files = fs.readdirSync(issuesDir).filter(f => f.endsWith('.md')).sort();
    for (const filename of files) {
      const filepath = path.join(issuesDir, filename);
      const content = fs.readFileSync(filepath, 'utf-8');
      const idMatch = content.match(/\|\s*\*\*issue_id\*\*\s*\|\s*([^|]+)\s*\|/);
      if (idMatch) {
        const issueId = idMatch[1].trim();
        const urlMatch = content.match(/\|\s*\*\*(target_doc_url|expected_doc_url)\*\*\s*\|\s*([^|]+)\s*\|/);
        if (urlMatch) map[issueId] = urlMatch[2].trim();
      }
    }
  } catch (e) {
    console.log(`  Warning: Could not read issues directory for target_doc_url: ${e.message}`);
  }
  return map;
}

// Call the docs assistant API
function callDocsAssistantAPI(query, timeout = 60000) {
  return new Promise((resolve) => {
    const encodedQuery = encodeURIComponent(query);
    const url = `https://docs-assistant.vtex.com/stream?q=${encodedQuery}`;
    
    const options = {
      hostname: 'docs-assistant.vtex.com',
      path: `/stream?q=${encodedQuery}`,
      method: 'GET',
      headers: {
        'Accept': 'text/event-stream',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: timeout,
      rejectUnauthorized: false
    };
    
    let fullResponse = '';
    const errors = [];
    
    const req = https.request(options, (res) => {
      res.setEncoding('utf8');
      
      res.on('data', (chunk) => {
        fullResponse += chunk;
      });
      
      res.on('end', () => {
        resolve({ response: fullResponse, errors });
      });
    });
    
    req.on('error', (e) => {
      errors.push(`Request error: ${e.message}`);
      resolve({ response: fullResponse, errors });
    });
    
    req.on('timeout', () => {
      req.destroy();
      errors.push(`Request timed out after ${timeout}ms`);
      resolve({ response: fullResponse, errors });
    });
    
    req.end();
  });
}

// Parse SSE response and extract content (legacy: join all data lines)
function parseSSEResponse(sseText) {
  const lines = sseText.split('\n');
  const contentParts = [];
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = line.slice(6);
      if (data.trim()) contentParts.push(data);
    }
  }
  return contentParts.length > 0 ? contentParts.join('\n') : sseText;
}

/**
 * Parse final_answer output like the UI (docs-assistant ui/src/lib/answerParser.ts).
 * Returns { content, references, locale, confidence } so we mirror what the user sees.
 */
function parseFinalAnswerLikeUI(output) {
  if (typeof output !== 'string') return { content: '', references: [], locale: null, confidence: null };
  const result = { content: output, references: [], locale: null, confidence: null };

  const referencesMatch = output.match(/## References\n((?:- \[.+?\]\(.+?\)\n?)+)/);
  if (referencesMatch) {
    const referencesText = referencesMatch[1];
    const refRegex = /- \[(.+?)\]\((.+?)\)/g;
    let match;
    while ((match = refRegex.exec(referencesText)) !== null) {
      result.references.push({ title: match[1], url: match[2] });
    }
    result.content = output.substring(0, referencesMatch.index).trim();
  }

  const metadataMatch = output.match(/\*Language: (\w+) \| Confidence: (\w+)\*\s*$/);
  if (metadataMatch) {
    result.locale = metadataMatch[1];
    result.confidence = metadataMatch[2];
    result.content = result.content.replace(/\*Language: \w+ \| Confidence: \w+\*\s*$/, '').trim();
  }

  return result;
}

/**
 * Extract markdown links [text](url) from the answer content the user sees.
 * Returns array of { title, url } in order of appearance.
 */
function extractLinksFromAnswerMarkdown(answerContent) {
  const links = [];
  if (!answerContent) return links;
  const seen = new Set();
  const mdLinkPattern = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  let match;
  while ((match = mdLinkPattern.exec(answerContent)) !== null) {
    const url = match[2].trim();
    const norm = normalizeUrl(url);
    if (!seen.has(norm)) {
      seen.add(norm);
      links.push({ title: match[1].trim(), url });
    }
  }
  return links;
}

/**
 * Parse SSE stream as JSON events (UI format: ToolCall, ToolOutput, FinalAnswerStep).
 * Extracts: doc links from search_documentation ToolOutput, final answer (parsed like UI) and sources.
 */
function parseSSEEvents(sseText) {
  const out = { docLinks: [], finalAnswer: null, sources: [], answer_content: null, references: [], locale: null, confidence: null };
  let lastToolCall = null;
  const lines = sseText.split('\n');

  for (const line of lines) {
    if (!line.startsWith('data: ')) continue;
    const raw = line.slice(6).trim();
    if (!raw) continue;
    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      continue;
    }
    if (!data || typeof data !== 'object') continue;

    if (data.type === 'ToolCall' && data.name) {
      lastToolCall = data.name;
    }

    if (data.type === 'ToolOutput') {
      const text = data.output || data.observation || (data.content && typeof data.content === 'string' ? data.content : '') || '';
      if (text.includes('**URL:**') && (text.includes('## 1.') || text.includes('Search results for'))) {
        const extracted = extractUrlsFromContent(text);
        for (const e of extracted) {
          const norm = normalizeUrl(e.url);
          if (!out.docLinks.some(x => normalizeUrl(x.url) === norm)) {
            out.docLinks.push({ url: e.url, title: e.title || extractTitleFromUrl(e.url) });
          }
        }
      }
      if (lastToolCall === 'final_answer' || (text.includes('## References') && text.length > 200)) {
        out.finalAnswer = text;
        const parsed = parseFinalAnswerLikeUI(text);
        out.answer_content = parsed.content;
        out.references = parsed.references;
        out.sources = parsed.references;
        if (parsed.locale) out.locale = parsed.locale;
        if (parsed.confidence) out.confidence = parsed.confidence;
      }
    }

    if (data.type === 'FinalAnswerStep' && data.output) {
      out.finalAnswer = data.output;
      const parsed = parseFinalAnswerLikeUI(data.output);
      out.answer_content = parsed.content;
      out.references = parsed.references;
      out.sources = parsed.references;
      if (parsed.locale) out.locale = parsed.locale;
      if (parsed.confidence) out.confidence = parsed.confidence;
    }
  }

  return out;
}

// Normalize URL for comparison
function normalizeUrl(url) {
  let normalized = url.replace(/^https?:\/\//, '');
  normalized = normalized.replace(/\/$/, '');
  normalized = normalized.replace(/#.*$/, '');
  normalized = normalized.replace(/\/(en|pt|es)\//g, '/');
  normalized = normalized.replace(/\/(en|pt|es)$/, '');
  return normalized.toLowerCase();
}

// Extract URLs from markdown content
function extractUrlsFromContent(content) {
  const results = [];
  const seenUrls = new Set();
  
  // Pattern for markdown links: [text](url)
  const mdLinkPattern = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  let match;
  
  while ((match = mdLinkPattern.exec(content)) !== null) {
    const title = match[1].trim();
    const url = match[2].trim();
    const normalized = normalizeUrl(url);
    
    if (!seenUrls.has(normalized)) {
      seenUrls.add(normalized);
      results.push({
        url,
        title,
        snippet: getSnippetAroundMatch(content, match.index, 200)
      });
    }
  }
  
  // Pattern for plain VTEX URLs
  const plainUrlPattern = /(https?:\/\/(?:help|developers)\.vtex\.com[^\s)\]<>"']+)/g;
  
  while ((match = plainUrlPattern.exec(content)) !== null) {
    let url = match[1].trim().replace(/[.,;:!?)+]+$/, '');
    const normalized = normalizeUrl(url);
    
    if (!seenUrls.has(normalized)) {
      seenUrls.add(normalized);
      results.push({
        url,
        title: extractTitleFromUrl(url),
        snippet: getSnippetAroundMatch(content, match.index, 200)
      });
    }
  }
  
  return results;
}

// Get snippet around a match position
function getSnippetAroundMatch(content, position, maxLength) {
  const start = Math.max(0, position - Math.floor(maxLength / 2));
  const end = Math.min(content.length, position + Math.floor(maxLength / 2));
  
  let snippet = content.slice(start, end).trim().replace(/\s+/g, ' ');
  
  if (snippet.length >= maxLength) {
    snippet = snippet.slice(0, maxLength - 3) + '...';
  }
  
  return snippet;
}

// Extract title from URL path
function extractTitleFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const segments = urlObj.pathname.split('/').filter(s => 
      s && !['en', 'pt', 'es', 'docs', 'tutorials', 'tracks', 'guides'].includes(s)
    );
    
    if (segments.length > 0) {
      const title = segments[segments.length - 1]
        .replace(/-/g, ' ')
        .replace(/_/g, ' ');
      return title.charAt(0).toUpperCase() + title.slice(1);
    }
  } catch (e) {}
  
  return 'Unknown';
}

// Sleep function
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Generate console summary (user-experience simulation: no target_doc_url comparison)
function generateConsoleSummary(results, jsonPath) {
  const lines = [
    '',
    '='.repeat(50),
    'Docs Assistant Path Runner — Summary',
    '='.repeat(50),
    `Run ID: ${results.run_id}`,
    `Timestamp: ${results.timestamp}`,
    '',
    `Issues processed: ${results.config.issues_count}`,
    `Total queries run: ${results.config.queries_count}`,
    ''
  ];

  const linkCounts = results.results.map(r => (r.links || []).length);
  const totalEntries = linkCounts.length;
  const minLinks = totalEntries > 0 ? Math.min(...linkCounts) : 0;
  const maxLinks = totalEntries > 0 ? Math.max(...linkCounts) : 0;
  const avgLinks = totalEntries > 0
    ? (linkCounts.reduce((a, b) => a + b, 0) / totalEntries).toFixed(1)
    : '0';

  const mdCounts = results.results.map(r => (r.links || []).filter(l => l.context === 'markdown').length);
  const ssCounts = results.results.map(r => (r.links || []).filter(l => l.context === 'suggested_sources').length);

  lines.push(`Results saved to: ${jsonPath}`);
  lines.push('');
  lines.push('Links per query (markdown + suggested sources):');
  lines.push(`  Total links per query: min ${minLinks}, avg ${avgLinks}, max ${maxLinks}`);
  lines.push(`  Queries with at least one link: ${linkCounts.filter(n => n > 0).length}/${totalEntries || 1}`);
  lines.push(`  Avg markdown links: ${totalEntries > 0 ? (mdCounts.reduce((a, b) => a + b, 0) / totalEntries).toFixed(1) : '0'}`);
  lines.push(`  Avg suggested sources: ${totalEntries > 0 ? (ssCounts.reduce((a, b) => a + b, 0) / totalEntries).toFixed(1) : '0'}`);
  lines.push('');
  lines.push(`Errors encountered: ${results.errors.length}`);

  if (results.errors.length > 0) {
    const errorTypes = {};
    for (const err of results.errors) {
      const et = err.error_type || 'unknown';
      errorTypes[et] = (errorTypes[et] || 0) + 1;
    }
    for (const [et, count] of Object.entries(errorTypes)) {
      lines.push(`  - ${et}: ${count}`);
    }
  }

  lines.push('');
  lines.push('='.repeat(50));

  return lines.join('\n');
}

// Generate markdown report (user-experience simulation: no target_doc_url comparison)
function generateMarkdownReport(results, outputPath) {
  const timestamp = results.timestamp;
  const runId = results.run_id;
  const totalIssues = results.config.issues_count;
  const totalQueries = results.config.queries_count;

  const linkCounts = results.results.map(r => (r.links || []).length);
  const avgLinks = linkCounts.length > 0
    ? (linkCounts.reduce((a, b) => a + b, 0) / linkCounts.length).toFixed(1)
    : '0';
  const minLinks = linkCounts.length > 0 ? Math.min(...linkCounts) : 0;
  const maxLinks = linkCounts.length > 0 ? Math.max(...linkCounts) : 0;

  const styleStats = {};
  for (const style of ['naive', 'familiar', 'expert']) {
    const styleResults = results.results.filter(r => r.query_style === style);
    const styleLinkCounts = styleResults.map(r => (r.links || []).length);
    const styleMdCounts = styleResults.map(r => (r.links || []).filter(l => l.context === 'markdown').length);
    const styleSsCounts = styleResults.map(r => (r.links || []).filter(l => l.context === 'suggested_sources').length);
    styleStats[style] = {
      total: styleResults.length,
      avgLinks: styleLinkCounts.length > 0
        ? (styleLinkCounts.reduce((a, b) => a + b, 0) / styleLinkCounts.length).toFixed(1)
        : '0',
      avgMdLinks: styleMdCounts.length > 0
        ? (styleMdCounts.reduce((a, b) => a + b, 0) / styleMdCounts.length).toFixed(1)
        : '0',
      avgSsLinks: styleSsCounts.length > 0
        ? (styleSsCounts.reduce((a, b) => a + b, 0) / styleSsCounts.length).toFixed(1)
        : '0',
      withLinks: styleLinkCounts.filter(n => n > 0).length
    };
  }

  let report = `# Docs Assistant — User Experience Simulation Report

**Run ID:** ${runId}  
**Run date:** ${timestamp}  
**Issues tested:** ${totalIssues}  
**Total queries:** ${totalQueries}  
**API endpoint:** https://docs-assistant.vtex.com/stream

This run simulates the user experience at https://docs-assistant.vtex.com/ui/.  
Report structure: **docs/test-suite/docs-assistant/run-docs-assistant-path.md** (§6). Parsing/UI alignment: **docs/test-suite/docs-assistant/UI-SPECS-FOR-RUNNER.md**. Content mirrors the UI: answer (no truncation), references \`{ title, url }\`, optional locale/confidence.

---

## Response Overview

- **Links per query:** min ${minLinks}, avg ${avgLinks}, max ${maxLinks}
- **Queries returning at least one link:** ${linkCounts.filter(n => n > 0).length}/${totalQueries}

## By Query Style

| Style | Queries | Avg links | Avg markdown | Avg suggested sources | Queries with ≥1 link |
|-------|---------|-----------|--------------|-----------------------|------------------------|
| Naive | ${styleStats.naive.total} | ${styleStats.naive.avgLinks} | ${styleStats.naive.avgMdLinks} | ${styleStats.naive.avgSsLinks} | ${styleStats.naive.withLinks} |
| Familiar | ${styleStats.familiar.total} | ${styleStats.familiar.avgLinks} | ${styleStats.familiar.avgMdLinks} | ${styleStats.familiar.avgSsLinks} | ${styleStats.familiar.withLinks} |
| Expert | ${styleStats.expert.total} | ${styleStats.expert.avgLinks} | ${styleStats.expert.avgMdLinks} | ${styleStats.expert.avgSsLinks} | ${styleStats.expert.withLinks} |

## Errors Encountered

`;

  if (results.errors.length > 0) {
    report += '| Issue ID | Query Style | Error Type | Message |\n';
    report += '|----------|-------------|------------|----------|\n';
    for (const err of results.errors.slice(0, 20)) {
      const msg = (err.error_message || '').slice(0, 50);
      report += `| ${err.issue_id} | ${err.query_style} | ${err.error_type} | ${msg} |\n`;
    }
    if (results.errors.length > 20) {
      report += `\n*...and ${results.errors.length - 20} more errors*\n`;
    }
  } else {
    report += '*No errors encountered.*\n';
  }

  report += `

## Results by Issue (links per query style: markdown / suggested sources)

| Issue ID | Naive | Familiar | Expert |
|----------|-------|----------|--------|
`;

  for (const issue of results.summary_by_issue) {
    const fmtStyle = (s) => {
      if (!s || s.links_count === undefined) return '-';
      return `${s.links_count} (${s.markdown_links_count || 0}md / ${s.suggested_sources_count || 0}ss)`;
    };
    const naive = issue.results_by_style.naive || {};
    const familiar = issue.results_by_style.familiar || {};
    const expert = issue.results_by_style.expert || {};
    report += `| ${issue.issue_id} | ${fmtStyle(naive)} | ${fmtStyle(familiar)} | ${fmtStyle(expert)} |\n`;
  }

  report += `

---

## Results

**Links:** Unified list of links the user sees — from the answer markdown and from the "Suggested sources" pills — with context.
**Answer markdown:** Full answer as the UI shows it (no truncation).

`;

  for (const r of results.results) {
    report += `### ${r.issue_id} — ${r.query_style}\n\n`;
    report += `**Query:** ${r.query}\n\n`;
    const targetUrl = r.target_doc_url ?? r.expected_doc_url;
    const targetFound = r.target_doc_url_found ?? r.expected_doc_url_found;
    const targetRank = r.target_doc_url_rank ?? r.expected_doc_url_rank;
    if (targetUrl != null) {
      const escapedTargetUrl = (targetUrl || '').replace(/\|/g, '\\|');
      const foundStr = targetFound ? 'Yes' : 'No';
      const rankStr = targetRank != null ? String(targetRank) : '—';
      report += '| Target doc URL | Found | Rank |\n|----------------|-------|------|\n';
      report += `| ${escapedTargetUrl} | ${foundStr} | ${rankStr} |\n\n`;
    }
    report += '#### Links\n\n';
    report += '| # | Title | URL | Context |\n|---|-------|-----|----------|\n';
    const links = r.links || [];
    for (const link of links) {
      const title = (link.title || '').replace(/\|/g, '\\|').slice(0, 60);
      const url = (link.url || '').replace(/\|/g, '\\|');
      report += `| ${link.position} | ${title} | ${url} | ${link.context} |\n`;
    }
    report += '\n#### Answer markdown\n\n';
    const answerText = r.answer_markdown || '';
    if (answerText) {
      report += answerText + '\n\n';
    }
    if (r.locale || r.confidence) {
      report += `*Language: ${r.locale || '—'} | Confidence: ${r.confidence || '—'}*\n\n`;
    }
    report += '---\n\n';
  }

  report += `\n*Generated by Docs Assistant Path Runner (user-experience simulation) on ${timestamp}*\n`;

  fs.writeFileSync(outputPath, report, 'utf-8');
  console.log(`\nMarkdown report saved to: ${outputPath}`);
}

// Main function
async function main() {
  const options = parseArgs();
  
  const workspaceDir = path.resolve(__dirname, '..', '..', '..');
  const queriesFile = path.join(workspaceDir, 'data', 'test-suite', 'docs-assistant', 'all_queries.json');
  const issuesDir = path.join(workspaceDir, 'docs', 'test-suite', 'issues');
  const outputDir = path.join(workspaceDir, options.outputDir);
  
  console.log('VTEX Docs Assistant Path Runner');
  console.log('================================');
  console.log(`Run ID: ${options.runId}`);
  console.log(`Query source: ${queriesFile}`);
  console.log(`Output directory: ${outputDir}`);
  console.log(`Top N results: ${options.topN}`);
  console.log(`API delay: ${options.delay}ms`);
  
  if (options.issues) {
    console.log(`Issue filter: ${options.issues.join(', ')}`);
  }
  
  // Load queries from all_queries.json
  console.log(`\nLoading queries from ${queriesFile}...`);
  
  let allQueriesData;
  try {
    allQueriesData = JSON.parse(fs.readFileSync(queriesFile, 'utf-8'));
  } catch (e) {
    console.error(`Fatal: Could not read ${queriesFile}: ${e.message}`);
    process.exit(1);
  }

  // Load target_doc_url from issue .md files (secondary lookup)
  console.log(`Loading target_doc_url from ${issuesDir}...`);
  const targetDocUrls = loadTargetDocUrls(issuesDir);

  // Build issues array from all_queries.json, enriched with target_doc_url
  const issues = [];
  for (const entry of allQueriesData.issues) {
    if (options.issues && !options.issues.includes(entry.issue_id)) {
      continue;
    }
    if (!entry.queries || entry.queries.length === 0) {
      console.log(`  Skipping ${entry.issue_id}: no queries found`);
      continue;
    }
    issues.push({
      issue_id: entry.issue_id,
      query_mcp: entry.queries,
      target_doc_url: targetDocUrls[entry.issue_id] || null,
      expected_doc_url: targetDocUrls[entry.issue_id] || null
    });
  }
  
  console.log(`Loaded ${issues.length} issues (${issues.reduce((s, i) => s + i.query_mcp.length, 0)} queries)`);
  
  // Initialize results
  const timestamp = new Date().toISOString();
  const results = {
    run_id: options.runId,
    path: 'docs-assistant',
    timestamp: timestamp,
    config: {
      top_n: options.topN,
      issues_count: issues.length,
      queries_count: issues.reduce((sum, i) => sum + (i.query_mcp?.length || 0), 0),
      api_endpoint: 'https://docs-assistant.vtex.com/stream'
    },
    summary_by_issue: [],
    errors: [],
    results: []
  };
  
  const totalIssues = issues.length;
  
  // Process each issue (simulate user experience: no target_doc_url comparison)
  for (let issueIdx = 0; issueIdx < issues.length; issueIdx++) {
    const issue = issues[issueIdx];
    const issueId = issue.issue_id;
    const queries = issue.query_mcp || [];

    console.log(`\n[Issue ${issueIdx + 1}/${totalIssues}] ${issueId}`);

    const issueSummary = {
      issue_id: issueId,
      results_by_style: {}
    };

    for (let queryIdx = 0; queryIdx < queries.length; queryIdx++) {
      const queryObj = queries[queryIdx];
      const queryText = queryObj.query || '';
      const queryStyle = queryObj.style || 'unknown';

      console.log(`  [${queryIdx + 1}/${queries.length} (${queryStyle})] ${queryText.slice(0, 50)}...`);

      // Rate limiting
      await sleep(options.delay);

      // Call API (same as https://docs-assistant.vtex.com/ui/)
      const { response: responseText, errors: apiErrors } = await callDocsAssistantAPI(queryText);

      if (apiErrors.length > 0) {
        console.log(`    ERROR: ${apiErrors[0]}`);
        results.errors.push({
          issue_id: issueId,
          query: queryText,
          query_style: queryStyle,
          error_type: 'api_call_failed',
          error_message: apiErrors[0],
          timestamp: new Date().toISOString()
        });

        const errTargetUrl = (issue.target_doc_url || issue.expected_doc_url || '').trim();
        const errEntry = {
          issue_id: issueId,
          path: 'docs-assistant',
          query: queryText,
          query_style: queryStyle,
          answer_markdown: '',
          links: [],
          locale: null,
          confidence: null,
          raw_response_length: 0
        };
        if (errTargetUrl) {
          errEntry.target_doc_url = errTargetUrl;
          errEntry.target_doc_url_found = false;
          errEntry.target_doc_url_rank = null;
          errEntry.expected_doc_url = errTargetUrl;
          errEntry.expected_doc_url_found = false;
          errEntry.expected_doc_url_rank = null;
        }
        results.results.push(errEntry);

        issueSummary.results_by_style[queryStyle] = {
          links_count: 0,
          markdown_links_count: 0,
          suggested_sources_count: 0
        };
        continue;
      }

      // Parse response: UI-style JSON events (ToolOutput, FinalAnswerStep) and/or legacy markdown
      const events = parseSSEEvents(responseText);

      // Build unified links array: markdown links + suggested sources, each with context
      const markdownLinks = extractLinksFromAnswerMarkdown(events.answer_content || '');
      const suggestedSources = (events.references || []);

      const links = [];
      let position = 1;
      for (const link of markdownLinks) {
        links.push({ position: position++, url: link.url, title: link.title, context: 'markdown' });
      }
      for (const src of suggestedSources) {
        links.push({ position: position++, url: src.url, title: src.title, context: 'suggested_sources' });
      }

      console.log(`    → ${links.length} links (${markdownLinks.length} markdown, ${suggestedSources.length} suggested sources)`);

      const targetUrl = (issue.target_doc_url || issue.expected_doc_url || '').trim();
      let targetFound = false;
      let targetRank = null;
      if (targetUrl) {
        const targetNorm = normalizeUrl(targetUrl);
        const matchIdx = links.findIndex(l => normalizeUrl(l.url) === targetNorm);
        if (matchIdx >= 0) {
          targetFound = true;
          targetRank = links[matchIdx].position;
        }
      }

      const resultEntry = {
        issue_id: issueId,
        path: 'docs-assistant',
        query: queryText,
        query_style: queryStyle,
        answer_markdown: events.answer_content || '',
        links: links,
        locale: events.locale || null,
        confidence: events.confidence || null,
        raw_response_length: responseText.length
      };
      if (targetUrl) {
        resultEntry.target_doc_url = targetUrl;
        resultEntry.target_doc_url_found = targetFound;
        resultEntry.target_doc_url_rank = targetRank;
        resultEntry.expected_doc_url = targetUrl;
        resultEntry.expected_doc_url_found = targetFound;
        resultEntry.expected_doc_url_rank = targetRank;
      }
      results.results.push(resultEntry);

      issueSummary.results_by_style[queryStyle] = {
        links_count: links.length,
        markdown_links_count: markdownLinks.length,
        suggested_sources_count: suggestedSources.length
      };
    }

    // Was target_doc_url found in any link surfaced to the user for this issue?
    const targetUrl = (issue.target_doc_url || issue.expected_doc_url || '').trim();
    if (targetUrl) {
      const targetNorm = normalizeUrl(targetUrl);
      const issueResultEntries = results.results.filter(r => r.issue_id === issueId);
      const allUrls = issueResultEntries.flatMap(r => (r.links || []).map(l => l.url));
      const found = allUrls.some(url => normalizeUrl(url) === targetNorm);
      issueSummary.target_doc_url = targetUrl;
      issueSummary.target_doc_url_found = found;
      issueSummary.expected_doc_url = targetUrl;
      issueSummary.expected_doc_url_found = found;
    } else {
      issueSummary.target_doc_url_found = null;
      issueSummary.expected_doc_url_found = null;
    }

    results.summary_by_issue.push(issueSummary);
  }
  
  // Create run-specific output directory
  fs.mkdirSync(outputDir, { recursive: true });
  const runDir = createRunDirectory(outputDir, 'api', 'docs-assistant');
  
  // Determine output filename
  const jsonFilename = options.issues && options.issues.length === 1
    ? `${options.runId}-${options.issues[0]}.json`
    : `${options.runId}.json`;
  
  const jsonPath = path.join(runDir, jsonFilename);
  
  // Save JSON results
  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`\nJSON results saved to: ${jsonPath}`);
  
  // Generate console summary
  const summary = generateConsoleSummary(results, jsonPath);
  console.log(summary);
  
  // Generate markdown report if requested
  if (options.generateAnalysis) {
    const mdPath = path.join(runDir, `analysis-${options.runId}.md`);
    generateMarkdownReport(results, mdPath);
  }
  
  return 0;
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
