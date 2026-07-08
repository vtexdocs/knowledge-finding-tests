(function () {
  const dashboardData = window.ANALYSIS_DASHBOARD_DATA || {};

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatPercent(value) {
    const numeric = Number(value ?? 0);
    return `${(numeric * 100).toFixed(2)}%`;
  }

  function formatDecimal(value) {
    const numeric = Number(value ?? 0);
    return numeric.toFixed(6).replace(/0+$/, "").replace(/\.$/, "");
  }

  function formatInt(value) {
    return Number(value ?? 0).toLocaleString("en-US");
  }

  function firstPresent(obj, keys) {
    for (const key of keys) {
      if (obj && obj[key] !== undefined) {
        return obj[key];
      }
    }
    return undefined;
  }

  function formatMaybe(value, kind) {
    if (value === null || value === undefined || value === "") {
      return "-";
    }
    if (kind === "percent") {
      return formatPercent(value);
    }
    if (kind === "decimal") {
      return formatDecimal(value);
    }
    if (kind === "int") {
      return formatInt(value);
    }
    return escapeHtml(value);
  }

  function initPanelToggles() {
    const panels = Array.from(document.querySelectorAll(".panel"));
    const expand = document.querySelector("[data-expand-all]");
    const collapse = document.querySelector("[data-collapse-all]");
    if (expand) {
      expand.addEventListener("click", () => {
        panels.forEach((panel) => {
          panel.open = true;
        });
      });
    }
    if (collapse) {
      collapse.addEventListener("click", () => {
        panels.forEach((panel) => {
          panel.open = false;
        });
      });
    }
  }

  function initSortableTables() {
    const tables = Array.from(document.querySelectorAll(".js-sortable"));
    tables.forEach((table) => {
      const headers = Array.from(table.querySelectorAll("thead th"));
      const tbody = table.querySelector("tbody");
      if (!tbody) {
        return;
      }

      headers.forEach((header, index) => {
        const button = header.querySelector(".sort-button");
        if (!button) {
          return;
        }

        button.addEventListener("click", () => {
          const currentDirection = header.dataset.sortDirection === "asc" ? "desc" : "asc";
          headers.forEach((cell) => {
            delete cell.dataset.sortDirection;
          });
          header.dataset.sortDirection = currentDirection;

          const rows = Array.from(tbody.querySelectorAll("tr"));
          rows.sort((rowA, rowB) => {
            const cellA = rowA.children[index];
            const cellB = rowB.children[index];
            const rawA = cellA?.dataset.sort ?? cellA?.textContent?.trim() ?? "";
            const rawB = cellB?.dataset.sort ?? cellB?.textContent?.trim() ?? "";
            const numericA = Number(rawA);
            const numericB = Number(rawB);
            const bothNumeric = !Number.isNaN(numericA) && !Number.isNaN(numericB);
            let comparison = 0;
            if (bothNumeric) {
              comparison = numericA - numericB;
            } else {
              comparison = rawA.localeCompare(rawB);
            }
            return currentDirection === "asc" ? comparison : -comparison;
          });

          rows.forEach((row) => tbody.appendChild(row));
        });
      });
    });
  }

  function initFailureExplorer() {
    const section = document.getElementById("failure-explorer");
    if (!section || !Array.isArray(dashboardData.failure_rows)) {
      return;
    }

    const failures = dashboardData.failure_rows;
    const pathSelect = section.querySelector("[data-filter='path']");
    const localeSelect = section.querySelector("[data-filter='locale']");
    const styleSelect = section.querySelector("[data-filter='style']");
    const issueInput = section.querySelector("[data-filter='issue']");
    const tbody = section.querySelector("tbody");
    const countNode = section.querySelector("[data-role='failure-count']");

    function populateSelect(select, values) {
      if (!select) {
        return;
      }
      const options = ['<option value="">All</option>']
        .concat(
          Array.from(values)
            .sort()
            .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)
        )
        .join("");
      select.innerHTML = options;
    }

    populateSelect(pathSelect, new Set(failures.map((row) => row.path)));
    populateSelect(localeSelect, new Set(failures.map((row) => row.locale)));
    populateSelect(styleSelect, new Set(failures.map((row) => row.style)));

    function filteredRows() {
      const pathValue = pathSelect?.value || "";
      const localeValue = localeSelect?.value || "";
      const styleValue = styleSelect?.value || "";
      const issueValue = (issueInput?.value || "").trim().toLowerCase();

      return failures.filter((row) => {
        if (pathValue && row.path !== pathValue) {
          return false;
        }
        if (localeValue && row.locale !== localeValue) {
          return false;
        }
        if (styleValue && row.style !== styleValue) {
          return false;
        }
        if (issueValue && !row.issue_id.toLowerCase().includes(issueValue)) {
          return false;
        }
        return true;
      });
    }

    function render() {
      const rows = filteredRows();
      if (countNode) {
        countNode.textContent = `${formatInt(rows.length)} failures shown`;
      }
      if (!tbody) {
        return;
      }
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No failures match the current filters.</td></tr>';
        return;
      }

      tbody.innerHTML = rows
        .map(
          (row) => `
            <tr>
              <td data-sort="${escapeHtml(row.path_identifier)}">${escapeHtml(row.path_identifier)}</td>
              <td data-sort="${escapeHtml(row.locale)}">${escapeHtml(row.locale.toUpperCase())}</td>
              <td data-sort="${escapeHtml(row.style)}">${escapeHtml(row.style)}</td>
              <td data-sort="${escapeHtml(row.issue_id)}">${escapeHtml(row.issue_id)}</td>
              <td data-sort="${escapeHtml(row.query)}">${escapeHtml(row.query)}</td>
              <td data-sort="${row.helpful_found ? 1 : 0}">${row.helpful_found ? "Yes" : "No"}</td>
              <td data-sort="${escapeHtml(row.link_source || "")}">${escapeHtml(row.link_source || "-")}</td>
            </tr>
          `
        )
        .join("");
    }

    [pathSelect, localeSelect, styleSelect, issueInput].forEach((control) => {
      control?.addEventListener("input", render);
      control?.addEventListener("change", render);
    });

    render();
  }

  function renderMetricListRows(rows, columns) {
    if (!rows.length) {
      return '<div class="empty-state">No metrics available for this issue.</div>';
    }

    const header = columns
      .map((column) => `<th><button class="sort-button" type="button">${escapeHtml(column.label)}</button></th>`)
      .join("");

    const body = rows
      .map((row) => {
        const cells = columns
          .map((column) => {
            const value = row[column.key];
            const sortValue = value === null || value === undefined || value === "" ? "" : value;
            return `<td data-sort="${escapeHtml(sortValue)}">${formatMaybe(value, column.kind)}</td>`;
          })
          .join("");
        return `<tr>${cells}</tr>`;
      })
      .join("");

    return `
      <div class="table-wrap">
        <table class="data-table data-table--compact js-sortable">
          <thead><tr>${header}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    `;
  }

  function renderClassifiedResults(rows) {
    if (!Array.isArray(rows) || !rows.length) {
      return '<div class="empty-state">No classified results for this query.</div>';
    }
    const body = rows
      .map(
        (row) => `
          <tr>
            <td data-sort="${row.rank}">${row.rank}</td>
            <td data-sort="${escapeHtml(row.link_type)}">${escapeHtml(row.link_type)}</td>
            <td data-sort="${escapeHtml(row.link_source || "")}">${escapeHtml(row.link_source || "-")}</td>
            <td data-sort="${escapeHtml(row.url)}"><a href="${escapeHtml(row.url)}">${escapeHtml(row.url)}</a></td>
          </tr>
        `
      )
      .join("");

    return `
      <div class="table-wrap">
        <table class="data-table data-table--compact js-sortable">
          <thead>
            <tr>
              <th><button class="sort-button" type="button">Rank</button></th>
              <th><button class="sort-button" type="button">Link type</button></th>
              <th><button class="sort-button" type="button">Link source</button></th>
              <th><button class="sort-button" type="button">URL</button></th>
            </tr>
          </thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    `;
  }

  function renderStylePayload(styleName, payload) {
    const metrics = payload.combined_ranked_list || payload;
    const query = payload.query || metrics.query || "";
    const columns = [
      { key: "coverage_status", label: "Coverage", kind: "text" },
      { key: "target_found", label: "Target found", kind: "text" },
      { key: "target_rank", label: "Target rank", kind: "int" },
      { key: "target_mrr", label: "Target MRR", kind: "decimal" },
      { key: "target_different_loc_found", label: "Target doc different locale", kind: "text" },
      { key: "target_different_loc_rank", label: "Target doc different locale rank", kind: "int" },
      { key: "target_any_locale_found", label: "Target any locale", kind: "text" },
      { key: "helpful_found", label: "Helpful found", kind: "text" },
      { key: "helpful_rank", label: "Helpful rank", kind: "int" },
      { key: "helpful_translated_found", label: "Helpful different locale", kind: "text" },
      { key: "helpful_any_locale_found", label: "Helpful any locale", kind: "text" },
    ];

    const metricsRow = {
      coverage_status: metrics.coverage_status,
      target_found: firstPresent(metrics, ["target_found", "expected_found"]) ? "Yes" : "No",
      target_rank: firstPresent(metrics, ["target_rank", "expected_rank"]),
      target_mrr: firstPresent(metrics, ["target_mrr", "expected_mrr"]),
      target_different_loc_found: firstPresent(metrics, ["target_different_loc_found", "expected_translated_found"]) ? "Yes" : "No",
      target_different_loc_rank: firstPresent(metrics, ["target_different_loc_rank", "expected_translated_rank"]),
      target_any_locale_found: firstPresent(metrics, ["target_any_locale_found", "expected_any_locale_found"]) ? "Yes" : "No",
      helpful_found: metrics.helpful_found ? "Yes" : "No",
      helpful_rank: metrics.helpful_rank,
      helpful_translated_found: metrics.helpful_translated_found ? "Yes" : "No",
      helpful_any_locale_found: metrics.helpful_any_locale_found ? "Yes" : "No",
    };

    let sourcesHtml = "";
    if (payload.link_sources) {
      const sourceBlocks = Object.entries(payload.link_sources)
        .map(([sourceName, sourcePayload]) => {
          const sourceRow = {
            coverage_status: sourcePayload.coverage_status,
            target_found: firstPresent(sourcePayload, ["target_found", "expected_found"]) ? "Yes" : "No",
            target_rank: firstPresent(sourcePayload, ["target_rank", "expected_rank"]),
            target_mrr: firstPresent(sourcePayload, ["target_mrr", "expected_mrr"]),
            target_different_loc_found: firstPresent(sourcePayload, ["target_different_loc_found", "expected_translated_found"]) ? "Yes" : "No",
            target_different_loc_rank: firstPresent(sourcePayload, ["target_different_loc_rank", "expected_translated_rank"]),
            target_any_locale_found: firstPresent(sourcePayload, ["target_any_locale_found", "expected_any_locale_found"]) ? "Yes" : "No",
            helpful_found: sourcePayload.helpful_found ? "Yes" : "No",
            helpful_rank: sourcePayload.helpful_rank,
            helpful_translated_found: sourcePayload.helpful_translated_found ? "Yes" : "No",
            helpful_any_locale_found: sourcePayload.helpful_any_locale_found ? "Yes" : "No",
          };

          return `
            <details>
              <summary>${escapeHtml(sourceName)}</summary>
              <div class="nested-details__body">
                ${renderMetricListRows([sourceRow], columns)}
                ${renderClassifiedResults(sourcePayload.classified_results)}
              </div>
            </details>
          `;
        })
        .join("");

      sourcesHtml = `
        <details>
          <summary>Link-source breakdown</summary>
          <div class="nested-details__body">${sourceBlocks}</div>
        </details>
      `;
    }

    return `
      <details>
        <summary>${escapeHtml(styleName)}</summary>
        <div class="nested-details__body">
          <p class="inline-note"><strong>Query:</strong> ${escapeHtml(query)}</p>
          ${renderMetricListRows([metricsRow], columns)}
          ${renderClassifiedResults(metrics.classified_results)}
          ${sourcesHtml}
        </div>
      </details>
    `;
  }

  function renderIssuePathTree(pathStyle) {
    const pathEntries = Object.entries(pathStyle || {});
    if (!pathEntries.length) {
      return '<div class="empty-state">No per-path detail available for this issue.</div>';
    }

    return pathEntries
      .map(([pathType, variantList]) => {
        const variantsHtml = (variantList || [])
          .map((variantEntry) => {
            return Object.entries(variantEntry)
              .map(([variantName, localeMap]) => {
                const localesHtml = Object.entries(localeMap || {})
                  .map(([locale, styleMap]) => {
                    const stylesHtml = Object.entries(styleMap || {})
                      .map(([styleName, payload]) => renderStylePayload(styleName, payload))
                      .join("");

                    return `
                      <details>
                        <summary>${escapeHtml(locale.toUpperCase())}</summary>
                        <div class="nested-details__body">${stylesHtml || '<div class="empty-state">No styles available.</div>'}</div>
                      </details>
                    `;
                  })
                  .join("");

                return `
                  <details>
                    <summary>${escapeHtml(variantName)}</summary>
                    <div class="nested-details__body">${localesHtml || '<div class="empty-state">No locale data available.</div>'}</div>
                  </details>
                `;
              })
              .join("");
          })
          .join("");

        return `
          <details>
            <summary>${escapeHtml(pathType)}</summary>
            <div class="nested-details__body">${variantsHtml}</div>
          </details>
        `;
      })
      .join("");
  }

  function renderIssueDetail(issue) {
    const totals = issue.totals || {};
    return `
      <div class="issue-detail__header">
        <h3 class="issue-detail__title">${escapeHtml(issue.issue_id)}</h3>
        <div class="meta-row">
          <span class="meta-pill">${escapeHtml(issue.persona)}</span>
          <span class="meta-pill">${escapeHtml(issue.product)}</span>
          <span class="meta-pill">Tested styles: ${formatInt(totals.tested_styles || 0)}</span>
          <span class="meta-pill">Misses: ${formatInt(totals.misses || 0)}</span>
          <span class="meta-pill">Hit rate: ${formatPercent(totals.hit_rate || 0)}</span>
          <span class="meta-pill">Hit rate any locale: ${formatPercent(totals.hit_rate_any_locale || 0)}</span>
        </div>
        <p class="lede">${escapeHtml(issue.user_intent)}</p>
      </div>

      <div class="card-grid">
        <article class="metric-card">
          <p class="metric-card__label">Tested styles</p>
          <p class="metric-card__value">${formatInt(totals.tested_styles || 0)}</p>
          <p class="metric-card__note">Combined path-level tested style count.</p>
        </article>
        <article class="metric-card">
          <p class="metric-card__label">Hits</p>
          <p class="metric-card__value">${formatInt(totals.hits || 0)}</p>
          <p class="metric-card__note">Target-doc hits estimated from aggregate rows.</p>
        </article>
        <article class="metric-card">
          <p class="metric-card__label">Misses</p>
          <p class="metric-card__value">${formatInt(totals.misses || 0)}</p>
          <p class="metric-card__note">Target-doc misses across combined path rows.</p>
        </article>
        <article class="metric-card">
          <p class="metric-card__label">Hit rate</p>
          <p class="metric-card__value">${formatPercent(totals.hit_rate || 0)}</p>
          <p class="metric-card__note">Hits divided by tested styles.</p>
        </article>
        <article class="metric-card">
          <p class="metric-card__label">Hit rate any locale</p>
          <p class="metric-card__value">${formatPercent(totals.hit_rate_any_locale || 0)}</p>
          <p class="metric-card__note">Target-doc hits including different-locale target docs.</p>
        </article>
      </div>

      <div class="subpanel">
        <h3>Target docs</h3>
        ${
          (issue.target_docs || issue.expected_docs)?.length
            ? `<ul class="link-list">${(issue.target_docs || issue.expected_docs)
                .map((url) => `<li><a href="${escapeHtml(url)}">${escapeHtml(url)}</a></li>`)
                .join("")}</ul>`
            : '<div class="empty-state">No target docs listed.</div>'
        }
      </div>

      <div class="subpanel">
        <h3>Other helpful docs</h3>
        ${
          issue.other_helpful_docs?.length
            ? `<ul class="link-list">${issue.other_helpful_docs
                .map((url) => `<li><a href="${escapeHtml(url)}">${escapeHtml(url)}</a></li>`)
                .join("")}</ul>`
            : '<div class="empty-state">No additional helpful docs listed.</div>'
        }
      </div>

      <div class="subpanel">
        <h3>Combined path aggregates</h3>
        ${renderMetricListRows(issue.aggregate_rows || [], [
          { key: "path_identifier", label: "Path", kind: "text" },
          { key: "target_pass_rate", label: "Target pass", kind: "percent" },
          { key: "target_any_locale_pass_rate", label: "Target pass any locale", kind: "percent" },
          { key: "target_mean_mrr", label: "Target MRR", kind: "decimal" },
          { key: "helpful_pass_rate", label: "Helpful pass", kind: "percent" },
          { key: "n_tested_styles", label: "Tested", kind: "int" },
          { key: "n_not_available_styles", label: "N/A", kind: "int" },
        ])}
      </div>

      <div class="subpanel">
        <h3>Per-path and per-style detail</h3>
        <div class="nested-details">
          ${renderIssuePathTree(issue.path_style)}
        </div>
      </div>
    `;
  }

  function initIssueDrilldown() {
    const section = document.getElementById("issue-drilldown");
    if (!section || !Array.isArray(dashboardData.issues)) {
      return;
    }

    const issues = dashboardData.issues;
    const searchInput = section.querySelector("[data-role='issue-search']");
    const listNode = section.querySelector("[data-role='issue-list']");
    const detailNode = section.querySelector("[data-role='issue-detail']");
    const countNode = section.querySelector("[data-role='issue-count']");

    let selectedIssueId = issues[0]?.issue_id || "";

    function filteredIssues() {
      const query = (searchInput?.value || "").trim().toLowerCase();
      if (!query) {
        return issues;
      }
      return issues.filter((issue) => {
        const haystack = [
          issue.issue_id,
          issue.persona,
          issue.product,
          issue.user_intent,
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(query);
      });
    }

    function renderList() {
      if (!listNode) {
        return;
      }
      const rows = filteredIssues();
      if (countNode) {
        countNode.textContent = `${formatInt(rows.length)} issues shown`;
      }
      if (!rows.length) {
        listNode.innerHTML = '<div class="empty-state">No issues match the current search.</div>';
        if (detailNode) {
          detailNode.innerHTML = '<div class="empty-state">Select an issue to inspect its detailed metrics.</div>';
        }
        return;
      }

      if (!rows.some((issue) => issue.issue_id === selectedIssueId)) {
        selectedIssueId = rows[0].issue_id;
      }

      listNode.innerHTML = rows
        .map((issue) => {
          const active = issue.issue_id === selectedIssueId ? " is-active" : "";
          return `
            <button class="issue-button${active}" type="button" data-issue-id="${escapeHtml(issue.issue_id)}">
              <span class="issue-button__id">${escapeHtml(issue.issue_id)}</span>
              <span class="issue-button__meta">${escapeHtml(issue.product)} | ${escapeHtml(issue.persona)}</span>
            </button>
          `;
        })
        .join("");

      Array.from(listNode.querySelectorAll("[data-issue-id]")).forEach((button) => {
        button.addEventListener("click", () => {
          selectedIssueId = button.getAttribute("data-issue-id") || "";
          renderList();
          renderDetail();
        });
      });
    }

    function renderDetail() {
      if (!detailNode) {
        return;
      }
      const issue = issues.find((row) => row.issue_id === selectedIssueId);
      if (!issue) {
        detailNode.innerHTML = '<div class="empty-state">Select an issue to inspect its detailed metrics.</div>';
        return;
      }
      detailNode.innerHTML = renderIssueDetail(issue);
      initSortableTables();
    }

    searchInput?.addEventListener("input", () => {
      renderList();
      renderDetail();
    });

    renderList();
    renderDetail();
  }

  const CHART_COLORS = [
    "#58a6ff", "#3fb950", "#f85149", "#d29922",
    "#bc8cff", "#f778ba", "#39d2c0", "#79c0ff",
    "#7ee787", "#ffa657", "#ff7b72", "#d2a8ff",
  ];

  const chartInstances = {};

  function formatChartValue(value, isPercent) {
    if (isPercent) return (value * 100).toFixed(2) + "%";
    return value.toFixed(4);
  }

  function fallbackChartMax(datasets) {
    const values = datasets.flatMap(function (dataset) {
      return dataset.data || [];
    });
    const maxValue = values.reduce(function (best, value) {
      return Math.max(best, Math.abs(value || 0));
    }, 0);
    return maxValue > 0 ? maxValue : 1;
  }

  function renderFallbackBarChart(canvas, labels, datasets) {
    const container = canvas?.parentElement;
    if (!container) return;

    canvas.style.display = "none";
    const existing = container.querySelector(".fallback-chart");
    if (existing) {
      existing.remove();
    }

    const root = document.createElement("div");
    root.className = "fallback-chart";

    const legend = document.createElement("div");
    legend.className = "fallback-chart__legend";
    datasets.forEach(function (dataset) {
      const item = document.createElement("div");
      item.className = "fallback-chart__legend-item";
      item.innerHTML =
        '<span class="fallback-chart__legend-swatch" style="background:' + escapeHtml(dataset.backgroundColor || "#58a6ff") + '"></span>' +
        '<span>' + escapeHtml(dataset.label || "") + "</span>";
      legend.appendChild(item);
    });
    root.appendChild(legend);

    const maxValue = fallbackChartMax(datasets);
    labels.forEach(function (label, index) {
      const row = document.createElement("div");
      row.className = "fallback-chart__row";

      const labelNode = document.createElement("div");
      labelNode.className = "fallback-chart__label";
      labelNode.textContent = label;
      row.appendChild(labelNode);

      const bars = document.createElement("div");
      bars.className = "fallback-chart__bars";

      datasets.forEach(function (dataset) {
        const rawValue = Number((dataset.data || [])[index] || 0);
        const track = document.createElement("div");
        track.className = "fallback-chart__track";

        const bar = document.createElement("div");
        bar.className = "fallback-chart__bar";
        bar.style.background = dataset.backgroundColor || "#58a6ff";
        bar.style.width = Math.min(Math.abs(rawValue) / maxValue * 100, 100).toFixed(2) + "%";

        const value = document.createElement("span");
        value.className = "fallback-chart__value";
        value.textContent = formatChartValue(rawValue, !!dataset.isPercent);

        track.appendChild(bar);
        track.appendChild(value);
        bars.appendChild(track);
      });

      row.appendChild(bars);
      root.appendChild(row);
    });

    container.appendChild(root);
  }

  function buildBarChart(canvasId, labels, datasets) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    if (typeof Chart !== "function") {
      renderFallbackBarChart(canvas, labels, datasets);
      return;
    }
    const fallback = canvas.parentElement?.querySelector(".fallback-chart");
    if (fallback) {
      fallback.remove();
    }
    canvas.style.display = "";
    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }
    chartInstances[canvasId] = new Chart(canvas, {
      type: "bar",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#e6edf3", font: { size: 11 } },
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const v = ctx.parsed.y;
                return ctx.dataset.label + ": " + formatChartValue(v, !!ctx.dataset.isPercent);
              },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: "#8b949e", font: { size: 10 }, maxRotation: 45 },
            grid: { color: "rgba(48,54,61,0.5)" },
          },
          y: {
            ticks: {
              color: "#8b949e",
              callback: function (v) {
                if (this.chart.config.data.datasets.some(function (d) { return d.isPercent; })) {
                  return (v * 100).toFixed(0) + "%";
                }
                return v;
              },
            },
            grid: { color: "rgba(48,54,61,0.5)" },
          },
        },
      },
    });
  }

  function getPathChartMetric() {
    var active = document.querySelector('[data-metric-toggle="paths"] .metric-toggle__btn.active');
    return active ? active.getAttribute("data-metric") : "pass";
  }

  function initChartPaths() {
    var mode = dashboardData.mode;
    var rows = (dashboardData.path_rows || []).filter(function (r) { return !r.link_source; });
    if (!rows.length) return;
    var labels = rows.map(function (r) { return r.path + " / " + (r.locale || "").toUpperCase(); });
    var metric = getPathChartMetric();
    var datasets;
    if (mode === "comparison") {
      if (metric === "mrr") {
        datasets = [
          { label: "Delta MRR", data: rows.map(function (r) { return r.delta_target_mean_mrr || r.delta_expected_mean_mrr || 0; }), backgroundColor: CHART_COLORS[0], isPercent: false },
        ];
      } else {
        datasets = [
          { label: "Delta Target Pass Rate", data: rows.map(function (r) { return r.delta_target_pass_rate || r.delta_expected_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        ];
      }
    } else if (metric === "mrr") {
      datasets = [
        { label: "Target MRR", data: rows.map(function (r) { return r.target_mean_mrr || r.expected_mean_mrr || 0; }), backgroundColor: CHART_COLORS[0], isPercent: false },
      ];
    } else {
      datasets = [
        { label: "Target Pass Rate", data: rows.map(function (r) { return r.target_pass_rate || r.expected_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        { label: "Target Pass Any Locale", data: rows.map(function (r) { return r.target_any_locale_pass_rate || r.expected_any_locale_pass_rate || 0; }), backgroundColor: CHART_COLORS[1], isPercent: true },
      ];
    }
    buildBarChart("chart-paths", labels, datasets);
  }

  function initChartPathFamilies() {
    var mode = dashboardData.mode;
    var rows = dashboardData.path_family_rows || [];
    if (!rows.length) return;
    var labels = rows.map(function (r) { return r.family; });
    var datasets;
    if (mode === "comparison") {
      datasets = [
        { label: "Weighted Delta Pass", data: rows.map(function (r) { return r.delta_target_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        { label: "Weighted Delta MRR", data: rows.map(function (r) { return r.delta_target_mean_mrr || 0; }), backgroundColor: CHART_COLORS[1], isPercent: false },
      ];
    } else {
      datasets = [
        { label: "Weighted Pass Rate", data: rows.map(function (r) { return r.target_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        { label: "Weighted MRR", data: rows.map(function (r) { return r.target_mean_mrr || 0; }), backgroundColor: CHART_COLORS[1], isPercent: false },
      ];
    }
    buildBarChart("chart-path-families", labels, datasets);
  }

  function initPathMetricToggle() {
    var toggle = document.querySelector('[data-metric-toggle="paths"]');
    if (!toggle) return;
    Array.from(toggle.querySelectorAll(".metric-toggle__btn")).forEach(function (btn) {
      btn.addEventListener("click", function () {
        Array.from(toggle.querySelectorAll(".metric-toggle__btn")).forEach(function (b) {
          b.classList.remove("active");
        });
        btn.classList.add("active");
        initChartPaths();
      });
    });
  }

  function initChartDimension(sectionId, dataKey, rowKey) {
    var mode = dashboardData.mode;
    var rows = dashboardData[dataKey] || [];
    if (!rows.length) return;
    var labels = rows.map(function (r) {
      if (rowKey === "label") {
        if (r.label) return r.label;
        if (r.style && r.locale) return r.style + " / " + String(r.locale).toUpperCase();
        if (r.persona && r.locale) return r.persona + " / " + String(r.locale).toUpperCase();
        return "";
      }
      var v = r[rowKey] || "";
      return typeof v === "string" ? v.toUpperCase() : v;
    });
    var datasets;
    if (mode === "comparison") {
      datasets = [
        { label: "Delta Target Pass Rate", data: rows.map(function (r) { return r.delta_target_pass_rate || r.delta_expected_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        { label: "Delta MRR", data: rows.map(function (r) { return r.delta_target_mean_mrr || r.delta_expected_mean_mrr || 0; }), backgroundColor: CHART_COLORS[1], isPercent: false },
      ];
    } else {
      datasets = [
        { label: "Target Pass Rate", data: rows.map(function (r) { return r.target_pass_rate || r.expected_pass_rate || 0; }), backgroundColor: CHART_COLORS[0], isPercent: true },
        { label: "Target Pass Any Locale", data: rows.map(function (r) { return r.target_any_locale_pass_rate || r.expected_any_locale_pass_rate || 0; }), backgroundColor: CHART_COLORS[1], isPercent: true },
        { label: "Target MRR", data: rows.map(function (r) { return r.target_mean_mrr || r.expected_mean_mrr || 0; }), backgroundColor: CHART_COLORS[2], isPercent: false },
        { label: "Helpful Pass Rate", data: rows.map(function (r) { return r.helpful_pass_rate || 0; }), backgroundColor: CHART_COLORS[3], isPercent: true },
      ];
    }
    buildBarChart("chart-" + sectionId, labels, datasets);
  }

  function initFailureDeltaExplorer() {
    var section = document.getElementById("failure-delta-explorer");
    if (!section || !dashboardData.failure_delta) {
      return;
    }

    var delta = dashboardData.failure_delta;
    var categorySelect = section.querySelector("[data-filter='category']");
    var pathSelect = section.querySelector("[data-filter='path']");
    var localeSelect = section.querySelector("[data-filter='locale']");
    var issueInput = section.querySelector("[data-filter='issue']");
    var tbody = section.querySelector("tbody");
    var countNode = section.querySelector("[data-role='failure-delta-count']");

    function currentRows() {
      var category = categorySelect ? categorySelect.value : "new_failures";
      return Array.isArray(delta[category]) ? delta[category] : [];
    }

    function populateSelect(select, values) {
      if (!select) {
        return;
      }
      var options = ['<option value="">All</option>']
        .concat(
          Array.from(values)
            .sort()
            .map(function (value) {
              return '<option value="' + escapeHtml(value) + '">' + escapeHtml(value) + "</option>";
            })
        )
        .join("");
      select.innerHTML = options;
    }

    function refreshFilters() {
      var rows = currentRows();
      populateSelect(pathSelect, new Set(rows.map(function (row) { return row.path; })));
      populateSelect(localeSelect, new Set(rows.map(function (row) { return row.locale; })));
      renderRows();
    }

    function renderRows() {
      if (!tbody) {
        return;
      }
      var rows = currentRows();
      var pathValue = pathSelect ? pathSelect.value : "";
      var localeValue = localeSelect ? localeSelect.value : "";
      var issueValue = (issueInput ? issueInput.value : "").trim().toLowerCase();
      var filtered = rows.filter(function (row) {
        if (pathValue && row.path !== pathValue) return false;
        if (localeValue && row.locale !== localeValue) return false;
        if (issueValue && String(row.issue_id || "").toLowerCase().indexOf(issueValue) === -1) return false;
        return true;
      });
      if (countNode) {
        countNode.textContent = filtered.length + " row(s) shown";
      }
      tbody.innerHTML = filtered.map(function (row) {
        return (
          "<tr>" +
          "<td>" + escapeHtml(row.path) + "</td>" +
          "<td>" + escapeHtml(row.locale) + "</td>" +
          "<td>" + escapeHtml(row.style) + "</td>" +
          "<td>" + escapeHtml(row.issue_id) + "</td>" +
          "<td>" + escapeHtml(row.query) + "</td>" +
          "<td>" + escapeHtml(row.link_source) + "</td>" +
          "</tr>"
        );
      }).join("") || '<tr><td colspan="6" class="empty-state">No rows match the current filters.</td></tr>';
      initSortableTables();
    }

    categorySelect?.addEventListener("change", refreshFilters);
    pathSelect?.addEventListener("change", renderRows);
    localeSelect?.addEventListener("change", renderRows);
    issueInput?.addEventListener("input", renderRows);
    refreshFilters();
  }

  function initViewToggles() {
    var toggles = Array.from(document.querySelectorAll(".view-toggle"));
    toggles.forEach(function (toggle) {
      var panel = toggle.closest(".panel__body");
      if (!panel) return;
      var tableView = panel.querySelector("[data-role='table-view']");
      var chartView = panel.querySelector("[data-role='chart-view']");
      var heatmapView = panel.querySelector("[data-role='heatmap-view']");
      var metricToggle = panel.querySelector("[data-metric-toggle]");
      var buttons = Array.from(toggle.querySelectorAll(".view-toggle__btn"));
      var sectionId = toggle.getAttribute("data-chart-section");

      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var view = btn.getAttribute("data-view");
          buttons.forEach(function (b) { b.classList.remove("active"); });
          btn.classList.add("active");
          if (view === "chart") {
            if (tableView) tableView.style.display = "none";
            if (heatmapView) heatmapView.classList.remove("visible");
            if (chartView) chartView.classList.add("visible");
            if (metricToggle) metricToggle.style.display = sectionId === "paths" ? "" : "none";
            if (sectionId === "paths") initChartPaths();
            else if (sectionId === "path-families") initChartPathFamilies();
            else if (sectionId === "locales") initChartDimension("locales", "locale_rows", "locale");
            else if (sectionId === "styles") initChartDimension("styles", "style_rows", "style");
            else if (sectionId === "personas") initChartDimension("personas", "persona_rows", "persona");
            else if (sectionId === "styles-locale") initChartDimension("styles-locale", "style_locale_rows", "label");
            else if (sectionId === "personas-locale") initChartDimension("personas-locale", "persona_locale_rows", "label");
            else if (sectionId === "portals") initChartDimension("portals", "portal_rows", "label");
          } else if (view === "heatmap") {
            if (tableView) tableView.style.display = "none";
            if (chartView) chartView.classList.remove("visible");
            if (heatmapView) heatmapView.classList.add("visible");
            if (metricToggle) metricToggle.style.display = "none";
          } else {
            if (tableView) tableView.style.display = "";
            if (chartView) chartView.classList.remove("visible");
            if (heatmapView) heatmapView.classList.remove("visible");
            if (metricToggle) metricToggle.style.display = "none";
          }
        });
      });
      if (metricToggle && sectionId === "paths") {
        metricToggle.style.display = "none";
      }
    });
  }

  function safeInit(name, fn) {
    try {
      fn();
    } catch (error) {
      console.error("Dashboard init failed:", name, error);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    safeInit("initPanelToggles", initPanelToggles);
    safeInit("initSortableTables", initSortableTables);
    safeInit("initFailureExplorer", initFailureExplorer);
    safeInit("initFailureDeltaExplorer", initFailureDeltaExplorer);
    safeInit("initPathMetricToggle", initPathMetricToggle);
    safeInit("initViewToggles", initViewToggles);
    safeInit("initIssueDrilldown", initIssueDrilldown);
  });
})();
