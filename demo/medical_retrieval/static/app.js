const DEMO_PRESETS = [
  { id: 1021, title: "Tăng huyết áp & Đái tháo đường", badge: "Chuẩn xác · 2 khái niệm" },
  { id: 1064, title: "Xét nghiệm G6PD (VI → EN+ZH)", badge: "Đa ngôn ngữ" },
  { id: 471, title: "Viêm gan B · Thận · Thiếu máu", badge: "Graph 3 khái niệm" },
  { id: 488, title: "Tiểu đường thai kỳ", badge: "Vinmec · Ngắn gọn" },
  { id: 178, title: "Sốt xuất huyết Dengue", badge: "Cảnh báo lâm sàng" }
];

const PIPELINE_STAGES = [
  { step: "01", title: "Truy hồi đa biểu diễn", detail: "BAAI/bge-m3 (dense + learned-sparse) và Qwen/Qwen3-Embedding-0.6B quét 1.724.798 đoạn trích VI / EN / ZH." },
  { step: "02", title: "Xếp hạng tài liệu", detail: "Qwen/Qwen3-Reranker-4B chấm điểm tài liệu, giữ Top-130 và bảo toàn tài liệu sở hữu đoạn bằng chứng." },
  { step: "03", title: "Lọc đoạn & bổ sung nguồn", detail: "Giữ top-90% chunks có điểm kết hợp Exp142 bổ sung tối đa 5 parent evidence còn thiếu." },
  { step: "04", title: "Định vị đoạn dài (Exp143)", detail: "BAAI/bge-reranker-v2-m3 chọn tối đa 3 cửa sổ nguồn ngắn giàu thông tin từ nhóm chunk dài." }
];

const state = {
  health: null,
  selected: null,
  runId: null,
  kind: "chunks",
  offset: 0,
  limit: 20,
  totals: { docs: 0, chunks: 0 },
  activeChunkRef: null
};

const $ = id => document.getElementById(id);

function notify(message, type = "info") {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = `toast ${type === "error" ? "error" : ""} show`;
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => { toast.className = "toast"; }, 3600);
}

async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = response.statusText;
    try { detail = (await response.json()).detail || detail; } catch {}
    throw new Error(detail);
  }
  return response.json();
}

function metric(value, label) {
  const node = document.createElement("div");
  node.className = "metric";
  const b = document.createElement("b");
  b.textContent = value;
  const s = document.createElement("span");
  s.textContent = label;
  node.append(b, s);
  return node;
}

function detectLanguage(text) {
  if (/[\u3400-\u9fff]/.test(text)) return "ZH";
  if (/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(text)) return "VI";
  return "EN";
}

function extractDomain(url) {
  if (!url) return "";
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

function renderPresets() {
  const container = $("preset-list");
  container.replaceChildren();
  for (const preset of DEMO_PRESETS) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "preset-chip";
    btn.dataset.qid = String(preset.id);
    btn.setAttribute("aria-pressed", "false");
    const title = document.createElement("strong");
    title.textContent = preset.title;
    const tag = document.createElement("span");
    tag.textContent = `#${preset.id} · ${preset.badge}`;
    btn.append(title, tag);
    btn.onclick = () => openQueryById(preset.id);
    container.append(btn);
  }
}

function syncPresetHighlight(queryId) {
  document.querySelectorAll(".preset-chip").forEach(btn => {
    const active = Number(btn.dataset.qid) === Number(queryId);
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function syncListHighlight(queryId) {
  document.querySelectorAll(".query-option").forEach(btn => {
    const active = Number(btn.dataset.qid) === Number(queryId);
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function syncActiveChunkCard() {
  document.querySelectorAll(".result-card[data-chunk-ref]").forEach(card => {
    const active = Number(card.dataset.chunkRef) === Number(state.activeChunkRef);
    card.classList.toggle("active", active);
    card.setAttribute("aria-current", active ? "true" : "false");
  });
}

async function init() {
  renderPresets();
  try {
    state.health = await api("/api/health");
    $("release-id").textContent = state.health.release_id + " · healthy";
    const m = $("metrics");
    m.replaceChildren(
      metric(state.health.public_metrics.final_score.toFixed(4), "Public Final F2 (Exp143 · tăng từ 0.3075)"),
      metric(state.health.public_metrics.docs_f2_macro.toFixed(4), "Documents F2-macro (Top-130 + owner)"),
      metric(state.health.public_metrics.chunks_f2_macro.toFixed(4), "Chunks F2-macro (Keep-90 + spans)"),
      metric(state.health.counts.index_chunks.toLocaleString("vi-VN"), "Đoạn trích từ 1,21M tài liệu VI / EN / ZH")
    );
    const f = $("fingerprints");
    f.replaceChildren();
    for (const [key, value] of Object.entries(state.health.fingerprints)) {
      const row = document.createElement("div");
      const s = document.createElement("span");
      s.textContent = key.toUpperCase() + " SHA256";
      const c = document.createElement("code");
      c.textContent = value;
      row.append(s, c);
      f.append(row);
    }
    const queryData = await loadQueries();
    const params = new URLSearchParams(location.search);
    const requestedId = Number(params.get("query_id") || (params.get("demo") === "1" ? 1021 : 1021));
    await openQueryById(requestedId, queryData.items[0] || null, true);
  } catch (error) {
    $("release-id").textContent = "Release unavailable";
    notify(error.message, "error");
  }
}

async function openQueryById(queryId, fallbackItem = null, silent = false) {
  try {
    const item = await api(`/api/queries/${encodeURIComponent(queryId)}`);
    await selectQuery(item, true, silent);
  } catch {
    if (fallbackItem) {
      await selectQuery(fallbackItem, true, silent);
    } else if (!silent) {
      notify(`Không tìm thấy Query ${queryId}`, "error");
    }
  }
}

async function loadQueries() {
  const search = $("query-search").value.trim();
  const data = await api(`/api/queries?search=${encodeURIComponent(search)}&limit=50`);
  const list = $("query-list");
  list.replaceChildren();
  for (const item of data.items) {
    const button = document.createElement("button");
    button.className = "query-option";
    button.type = "button";
    button.dataset.qid = String(item.id);
    const isActive = state.selected && Number(state.selected.id) === Number(item.id);
    button.classList.toggle("active", !!isActive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
    const b = document.createElement("b");
    b.textContent = `QUERY ${item.id}`;
    const span = document.createElement("span");
    span.textContent = item.query;
    button.append(b, span);
    button.onclick = () => selectQuery(item, true);
    list.append(button);
  }
  if (!data.items.length) {
    const empty = document.createElement("p");
    empty.className = "query-empty";
    empty.textContent = "Không tìm thấy câu hỏi khớp.";
    list.append(empty);
  }
  return data;
}

async function selectQuery(item, autoRun = true, silent = false) {
  state.selected = item;
  state.activeChunkRef = null;
  syncPresetHighlight(item.id);
  syncListHighlight(item.id);
  $("selected-id").textContent = `QUERY ${item.id}`;
  $("selected-text").textContent = item.query;
  $("run-button").disabled = false;
  document.dispatchEvent(new CustomEvent("r2ai:query-selected", { detail: { id: item.id } }));
  if (autoRun) {
    await runReplay({ autoOpenFirst: true, silent });
  }
}

async function runReplay(options = {}) {
  const { autoOpenFirst = true, silent = false } = options;
  if (!state.selected) return;
  $("run-button").disabled = true;
  $("run-button").setAttribute("aria-busy", "true");
  $("run-button").textContent = "Đang mở kết quả…";
  try {
    const run = await api("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "replay", query_id: state.selected.id, query: state.selected.query })
    });
    state.runId = run.run_id;
    state.offset = 0;
    $("export-button").disabled = false;
    $("result-summary").textContent = `Query ${run.query_id} · kết quả đã kiểm chứng`;
    await refreshCounts();
    const firstChunkRef = await loadResults();
    if (autoOpenFirst && firstChunkRef !== null && firstChunkRef !== undefined) {
      await loadEvidence(firstChunkRef);
    }
    if (!silent) {
      notify(`Đã mở kết quả Query ${run.query_id}`);
    }
  } catch (error) {
    notify(error.message, "error");
  } finally {
    $("run-button").disabled = false;
    $("run-button").removeAttribute("aria-busy");
    $("run-button").textContent = "Xem kết quả truy hồi";
  }
}

async function refreshCounts() {
  for (const kind of ["docs", "chunks"]) {
    const data = await api(`/api/runs/${state.runId}/results?kind=${kind}&limit=1`);
    state.totals[kind] = data.total;
  }
  $("doc-count").textContent = state.totals.docs;
  $("chunk-count").textContent = state.totals.chunks;
}

function updateResultHint(items) {
  const hint = $("result-hint");
  if (state.kind === "chunks" && items.length) {
    const langs = Array.from(new Set(items.map(it => detectLanguage(it.chunk_text))));
    hint.textContent = `Ngôn ngữ trang này: ${langs.join(" · ")} — bấm một đoạn để đối chiếu nguyên văn ở cột 03 →`;
    hint.classList.remove("hidden");
  } else if (state.kind === "docs" && items.length) {
    hint.textContent = "Danh sách tài liệu xếp hạng bởi Qwen3-Reranker-4B (Top-130 + bảo toàn owner).";
    hint.classList.remove("hidden");
  } else {
    hint.classList.add("hidden");
  }
}

async function loadResults() {
  if (!state.runId) return null;
  if (state.kind === "trace") {
    updateResultHint([]);
    renderTrace();
    return null;
  }
  const data = await api(`/api/runs/${state.runId}/results?kind=${state.kind}&offset=${state.offset}&limit=${state.limit}`);
  const list = $("result-list");
  list.className = "result-list";
  list.replaceChildren();
  updateResultHint(data.items);

  for (const item of data.items) {
    const card = document.createElement("article");
    card.className = "result-card";
    const meta = document.createElement("div");
    meta.className = "result-meta";
    const leftGroup = document.createElement("div");
    leftGroup.className = "meta-left";
    const rank = document.createElement("span");
    rank.className = "rank-pill";
    rank.textContent = `#${item.ordinal + 1}`;
    leftGroup.append(rank);

    if (state.kind === "chunks") {
      const lang = detectLanguage(item.chunk_text);
      const langPill = document.createElement("span");
      langPill.className = `lang-pill lang-${lang.toLowerCase()}`;
      langPill.textContent = lang;
      leftGroup.append(langPill);

      const domain = extractDomain(item.url);
      if (domain) {
        const domainSpan = document.createElement("span");
        domainSpan.className = "domain-tag";
        domainSpan.textContent = domain;
        leftGroup.append(domainSpan);
      }

      card.dataset.chunkRef = String(item.chunk_ref);
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", `Mở đối chiếu nguồn cho đoạn ${item.ordinal + 1}, tài liệu ${item.doc_id}`);
      if (Number(state.activeChunkRef) === Number(item.chunk_ref)) {
        card.classList.add("active");
        card.setAttribute("aria-current", "true");
      }
    } else {
      const domain = extractDomain(item.url);
      if (domain) {
        const domainSpan = document.createElement("span");
        domainSpan.className = "domain-tag";
        domainSpan.textContent = domain;
        leftGroup.append(domainSpan);
      }
    }

    const right = document.createElement("span");
    right.className = "doc-id-tag";
    right.textContent = `DOC ${item.doc_id}`;
    meta.append(leftGroup, right);
    card.append(meta);

    if (state.kind === "chunks") {
      const p = document.createElement("p");
      p.className = "chunk-preview";
      p.textContent = item.chunk_text;
      card.append(p);
      card.onclick = () => loadEvidence(item.chunk_ref);
      card.onkeydown = e => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          loadEvidence(item.chunk_ref);
        }
      };
    } else {
      const p = document.createElement("p");
      p.textContent = "Tài liệu thuộc corpus chính thức BTC";
      const url = document.createElement("div");
      url.className = "doc-url";
      if (item.url && /^https?:\/\//i.test(item.url)) {
        const a = document.createElement("a");
        a.href = item.url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = item.url;
        url.append(a);
      } else {
        url.textContent = "URL không có trong mapping";
      }
      card.append(p, url);
    }
    list.append(card);
  }
  renderPagination(data.total);
  if (state.kind === "chunks" && data.items.length) {
    return data.items[0].chunk_ref;
  }
  return null;
}

function renderPagination(total) {
  const pages = Math.max(1, Math.ceil(total / state.limit));
  const page = Math.floor(state.offset / state.limit) + 1;
  $("pagination").classList.toggle("hidden", total <= state.limit);
  $("page-label").textContent = `Trang ${page} / ${pages}`;
  $("first-page").disabled = state.offset === 0;
  $("prev").disabled = state.offset === 0;
  $("next").disabled = state.offset + state.limit >= total;
}

function renderTrace() {
  const list = $("result-list");
  list.className = "result-list";
  list.replaceChildren();

  const pipelineWrap = document.createElement("div");
  pipelineWrap.className = "pipeline-steps";
  for (const item of PIPELINE_STAGES) {
    const step = document.createElement("div");
    step.className = "pipeline-step";
    const num = document.createElement("span");
    num.className = "step-num";
    num.textContent = item.step;
    const body = document.createElement("div");
    const h4 = document.createElement("strong");
    h4.textContent = item.title;
    const p = document.createElement("p");
    p.textContent = item.detail;
    body.append(h4, p);
    step.append(num, body);
    pipelineWrap.append(step);
  }
  list.append(pipelineWrap);

  const grid = document.createElement("div");
  grid.className = "trace-grid";
  const rows = {
    "Chế độ": "Verified replay · Kết quả bài nộp Exp143 đã khóa",
    "Release ID": state.health.release_id,
    "Submission SHA256": state.health.fingerprints.submission,
    "Predictions SHA256": state.health.fingerprints.predictions,
    "Private score": "Chưa công bố"
  };
  for (const [label, value] of Object.entries(rows)) {
    const r = document.createElement("div");
    r.className = "trace-row";
    const s = document.createElement("span");
    s.textContent = label;
    const c = document.createElement("code");
    c.textContent = value;
    r.append(s, c);
    grid.append(r);
  }
  list.append(grid);
  $("pagination").classList.add("hidden");
}

async function loadEvidence(ref) {
  state.activeChunkRef = ref;
  syncActiveChunkCard();
  const target = $("evidence");
  target.className = "";
  target.textContent = "Đang đối chiếu với snapshot gốc…";
  try {
    const item = await api(`/api/runs/${state.runId}/evidence/${ref}`);
    target.replaceChildren();
    const meta = document.createElement("div");
    meta.className = "evidence-meta";
    const badges = [
      [`DOC ${item.doc_id}`, ""],
      [item.resolved ? "Khớp nguyên văn 100%" : "Chưa khớp nguyên văn", item.resolved ? "resolved" : "unresolved"],
      [item.source_part || "no source part", ""]
    ];
    for (const [text, cls] of badges) {
      const p = document.createElement("span");
      p.className = `pill ${cls}`;
      p.textContent = text;
      if (cls === "resolved") p.title = "EXACT RESOLVED · khớp liên tiếp 100% trong snapshot gốc";
      meta.append(p);
    }
    target.append(meta);

    if (item.url && /^https?:\/\//i.test(item.url)) {
      const a = document.createElement("a");
      a.className = "source-link";
      a.href = item.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = item.url;
      target.append(a);
    }

    const box = document.createElement("div");
    box.className = "evidence-text";
    if (item.resolved) {
      const before = document.createTextNode(item.context.slice(0, item.highlight_start));
      const mark = document.createElement("mark");
      mark.textContent = item.context.slice(item.highlight_start, item.highlight_end);
      const after = document.createTextNode(item.context.slice(item.highlight_end));
      box.append(before, mark, after);
    } else {
      box.textContent = item.chunk_text + "\n\n[" + item.reason + "]";
    }
    target.append(box);

    const mark = box.querySelector("mark");
    if (mark) {
      requestAnimationFrame(() => mark.scrollIntoView({ block: "center", behavior: "smooth" }));
    }

    const details = document.createElement("details");
    details.className = "hash-details";
    const summary = document.createElement("summary");
    summary.textContent = "Mã kiểm chứng SHA256";
    const hash = document.createElement("p");
    hash.className = "hash";
    hash.textContent = `chunk sha256: ${item.text_sha256}` + (item.source_sha256 ? `\nsource sha256: ${item.source_sha256}` : "");
    details.append(summary, hash);
    target.append(details);
  } catch (error) {
    target.textContent = error.message;
    notify(error.message, "error");
  }
}

document.addEventListener("r2ai:graph-doc-selected", async event => {
  const { docId } = event.detail || {};
  if (!state.runId || !docId) return;
  try {
    const data = await api(`/api/runs/${state.runId}/results?kind=chunks&offset=0&limit=100`);
    const match = data.items.find(it => Number(it.doc_id) === Number(docId));
    if (match) {
      await loadEvidence(match.chunk_ref);
      $("review-workspace").scrollIntoView({ behavior: "smooth", block: "start" });
      notify(`Đã mở đoạn bằng chứng từ DOC ${docId}`);
    } else {
      notify(`DOC ${docId} là ứng viên minh họa từ đồ thị khái niệm (không nằm trong Top-100 đoạn trích).`);
    }
  } catch {
    notify(`Không thể tải đối chiếu cho DOC ${docId}`, "error");
  }
});

$("query-search").addEventListener("input", () => {
  clearTimeout(window.queryTimer);
  window.queryTimer = setTimeout(loadQueries, 220);
});
$("run-button").onclick = () => runReplay({ autoOpenFirst: true });
$("export-button").onclick = () => {
  if (state.runId) location.href = `/api/runs/${state.runId}/export`;
};
document.querySelectorAll(".tab").forEach(tab => {
  tab.onclick = () => {
    document.querySelectorAll(".tab").forEach(t => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    tab.classList.add("active");
    tab.setAttribute("aria-selected", "true");
    state.kind = tab.dataset.kind;
    state.offset = 0;
    loadResults();
  };
});
$("first-page").onclick = () => {
  state.offset = 0;
  loadResults();
};
$("prev").onclick = () => {
  state.offset = Math.max(0, state.offset - state.limit);
  loadResults();
};
$("next").onclick = () => {
  state.offset += state.limit;
  loadResults();
};

init();
