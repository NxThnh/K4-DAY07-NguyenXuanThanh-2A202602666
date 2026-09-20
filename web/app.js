// Benchmark questions pre-configured for the group
const BENCHMARK_QUERIES = [
  {
    id: 1,
    title: "Câu 1: Bóc seal máy Apple",
    query: "Khách hàng có được mở seal hộp iPhone kiểm tra trước khi thanh toán không?",
    filter: "",
    gold: "Khách hàng phải thanh toán 100% trước khi mở seal hộp sản phẩm Apple; sau đó mới được mở kiểm tra thẩm mỹ."
  },
  {
    id: 2,
    title: "Câu 2: Thay pin Macbook Điện Thoại Vui",
    query: "Thay pin Macbook tại Điện Thoại Vui được bảo hành bao lâu và bảo hành những lỗi gì?",
    filter: "",
    gold: "Bảo hành 1 đổi 1 trong 12 tháng, bảo hành lỗi pin chai, báo ảo, sạc không vào, sập nguồn và cả pin phồng."
  },
  {
    id: 3,
    title: "Câu 3: Bán sỉ B2B & VAT (Cần lọc Seller)",
    query: "Doanh nghiệp mua số lượng lớn có chính sách chiết khấu và xuất hóa đơn VAT như thế nào?",
    filter: "seller",
    gold: "Mua từ 100-200 triệu giảm thêm 2-3%, trên 200 triệu có chính sách riêng, hỗ trợ xuất đầy đủ 100% hóa đơn điện tử VAT."
  },
  {
    id: 4,
    title: "Câu 4: Đổi mới linh kiện PC TNC Store",
    query: "Điều kiện để linh kiện máy tính được đổi mới tại TNC Store là gì?",
    filter: "",
    gold: "CPU/SSD/RAM đổi mới 100% trong 3 năm đầu; Nguồn/Tản nhiệt 1 năm; Main/VGA 6 tháng; tem còn nguyên, không biến dạng/cháy nổ."
  },
  {
    id: 5,
    title: "Câu 5: Gói bảo hành rơi vỡ CellphoneS",
    query: "Gói bảo hành mở rộng rơi vỡ vào nước tại CellphoneS có những quyền lợi gì?",
    filter: "",
    gold: "Tặng gói 1-1 VIP, hỗ trợ 90% chi phí sửa chữa rơi vỡ vào nước, đổi máy tương đương nếu hư hỏng quá nặng."
  }
];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  renderBenchmarkChips();
  initRagForm();
  initAbModal();
  initChunkingVisualizer();
  loadInventory();
});

// Tab Switching
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(targetTab)?.classList.add("active");

      if (targetTab === "tab-chunking" && !window.chunkingLoaded) {
        runChunkCompare();
        window.chunkingLoaded = true;
      }
    });
  });
}

// Render Benchmark Chips
function renderBenchmarkChips() {
  const container = document.getElementById("benchmark-chips");
  if (!container) return;

  container.innerHTML = BENCHMARK_QUERIES.map(q => `
    <div class="chip" data-id="${q.id}">
      <div class="chip-id">${q.title}</div>
      <div class="chip-query">${q.query}</div>
    </div>
  `).join("");

  container.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      const qid = parseInt(chip.getAttribute("data-id"));
      const bq = BENCHMARK_QUERIES.find(x => x.id === qid);
      if (!bq) return;

      document.getElementById("query-input").value = bq.query;
      
      // Auto select filter if required
      const filterRadios = document.querySelectorAll('input[name="audience-filter"]');
      filterRadios.forEach(r => {
        r.checked = (r.value === bq.filter);
      });

      // Auto trigger search
      triggerRagSearch(bq.query, bq.filter);
    });
  });
}

// RAG Form
function initRagForm() {
  const form = document.getElementById("rag-form");
  const input = document.getElementById("query-input");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    const selectedFilter = document.querySelector('input[name="audience-filter"]:checked')?.value || "";
    triggerRagSearch(query, selectedFilter);
  });
}

// Trigger RAG Search
async function triggerRagSearch(query, filterAudience) {
  const answerBody = document.getElementById("answer-content");
  const chunksContainer = document.getElementById("chunks-container");
  const chunksCount = document.getElementById("chunks-count");
  const timeBadge = document.getElementById("response-time");
  const submitBtn = document.getElementById("btn-submit");

  // Loading state
  submitBtn.disabled = true;
  timeBadge.innerText = "Đang xử lý...";
  answerBody.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon" style="animation: spin 1s infinite linear;">⚙️</div>
      <p>Đang thực hiện Semantic Retrieval & yêu cầu Google Gemini AI sinh câu trả lời tư vấn...</p>
    </div>
  `;
  chunksContainer.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">🔍</div>
      <p>Đang tìm kiếm các chunk liên quan nhất trong Vector Store...</p>
    </div>
  `;

  const startTime = performance.now();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: query,
        filter_audience: filterAudience,
        top_k: 3
      })
    });

    const data = await res.json();
    const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
    timeBadge.innerText = `Hoàn tất trong ${elapsed}s`;

    // Render Answer
    renderAnswer(data.answer);

    // Render Chunks
    renderChunks(data.results);
    chunksCount.innerText = `${data.results.length} chunks`;

  } catch (err) {
    answerBody.innerHTML = `<div class="empty-state" style="color:#f43f5e;"><p>Lỗi kết nối tới Server: ${err.message}</p></div>`;
    timeBadge.innerText = "Lỗi";
  } finally {
    submitBtn.disabled = false;
  }
}

function renderAnswer(rawText) {
  const answerBody = document.getElementById("answer-content");
  if (!rawText) {
    answerBody.innerHTML = "<p>Không nhận được câu trả lời.</p>";
    return;
  }

  // Chuẩn hóa và làm sạch chuỗi
  let text = rawText.trim();

  // Parse markdown headers
  text = text
    .replace(/^### (.*$)/gim, '<h4 style="margin: 12px 0 6px 0; color: var(--accent); font-weight: 600;">$1</h4>')
    .replace(/^## (.*$)/gim, '<h3 style="margin: 14px 0 8px 0; color: #fff; font-weight: 600;">$1</h3>')
    .replace(/^# (.*$)/gim, '<h2 style="margin: 16px 0 10px 0; color: #fff; font-weight: 700;">$1</h2>');

  // In đậm
  text = text.replace(/\*\*(.*?)\*\*/gim, '<strong style="color: #38bdf8;">$1</strong>');

  // Danh sách gạch đầu dòng
  text = text.replace(/^[\*\-] (.*$)/gim, '<li style="margin-bottom: 6px; line-height: 1.6;">$1</li>');

  // Bọc các nhóm <li> vào <ul>
  text = text.replace(/(<li.*<\/li>(\s*<li.*<\/li>)*)/gim, '<ul style="padding-left: 20px; margin: 10px 0;">$1</ul>');

  // Ngắt đoạn văn bản
  text = text.replace(/\n\n+/g, '</p><p style="margin-bottom: 12px; line-height: 1.65;">');
  text = text.replace(/\n/g, '<br>');

  answerBody.innerHTML = `<div style="line-height: 1.65; font-size: 0.95rem; color: #e2e8f0;"><p style="margin-bottom: 12px; line-height: 1.65;">${text}</p></div>`;
}

function renderChunks(results) {
  const container = document.getElementById("chunks-container");
  if (!results || results.length === 0) {
    container.innerHTML = `<div class="empty-state"><p>Không tìm thấy chunk nào phù hợp với bộ lọc.</p></div>`;
    return;
  }

  container.innerHTML = results.map((r, idx) => {
    const scoreVal = r.score.toFixed(4);
    let scoreClass = "score-low";
    if (r.score >= 0.8) scoreClass = "score-high";
    else if (r.score >= 0.6) scoreClass = "score-mid";

    const meta = r.metadata || {};
    const audience = meta.audience || "N/A";
    const category = meta.category || "N/A";
    const docId = meta.doc_id || "document";

    return `
      <div class="chunk-card">
        <div class="chunk-header">
          <div class="chunk-meta">
            <span class="chunk-id">#${idx + 1} • ${r.id}</span>
            <span class="badge accent">${docId}</span>
            <span class="badge neutral">${audience}</span>
          </div>
          <div class="score-badge ${scoreClass}">
            <span>Score: ${scoreVal}</span>
          </div>
        </div>
        <div class="chunk-text">${escapeHtml(r.content)}</div>
      </div>
    `;
  }).join("");
}

// A/B Modal
function initAbModal() {
  const modal = document.getElementById("ab-modal");
  const openBtn = document.getElementById("btn-ab-compare");
  const closeBtn = document.getElementById("btn-close-ab");

  openBtn.addEventListener("click", async () => {
    modal.classList.remove("hidden");
    const containerNo = document.getElementById("ab-results-no-filter");
    const containerWith = document.getElementById("ab-results-with-filter");

    containerNo.innerHTML = "<p>Đang chạy không lọc...</p>";
    containerWith.innerHTML = "<p>Đang chạy có lọc audience='seller'...</p>";

    try {
      const res = await fetch("/api/compare-ab", { method: "POST" });
      const data = await res.json();

      containerNo.innerHTML = data.no_filter.map(r => renderMiniChunk(r)).join("");
      containerWith.innerHTML = data.with_filter.map(r => renderMiniChunk(r)).join("");
    } catch (e) {
      containerNo.innerHTML = `<p>Lỗi: ${e.message}</p>`;
    }
  });

  closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
  });
}

function renderMiniChunk(r) {
  const meta = r.metadata || {};
  return `
    <div class="chunk-card" style="padding: 10px; margin-bottom: 8px;">
      <div class="chunk-header" style="margin-bottom: 4px;">
        <span class="badge accent" style="font-size:0.7rem;">${meta.doc_id}</span>
        <span class="badge ${meta.audience === 'seller' ? 'success' : 'neutral'}">${meta.audience}</span>
        <span class="score-badge score-high" style="font-size:0.72rem;">${r.score.toFixed(4)}</span>
      </div>
      <div class="chunk-text" style="font-size:0.78rem; padding: 6px 10px;">${escapeHtml(r.content.substring(0, 160))}...</div>
    </div>
  `;
}

// Chunking Visualizer
function initChunkingVisualizer() {
  const btn = document.getElementById("btn-run-chunk-compare");
  const select = document.getElementById("sample-text-select");

  btn.addEventListener("click", runChunkCompare);
  select.addEventListener("change", runChunkCompare);
}

async function runChunkCompare() {
  const sample = document.getElementById("sample-text-select").value;
  
  try {
    const res = await fetch("/api/compare-chunking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample: sample })
    });
    const data = await res.json();

    // Strategy 1: Fixed
    renderStrategyCol("fixed", data.fixed_size);
    // Strategy 2: Sentence
    renderStrategyCol("sentence", data.by_sentences);
    // Strategy 3: Recursive
    renderStrategyCol("recursive", data.recursive);
    // Strategy 4: Section
    renderStrategyCol("section", data.section);

  } catch (err) {
    console.error("Lỗi compare chunking:", err);
  }
}

function renderStrategyCol(key, data) {
  const statsRow = document.getElementById(`stats-${key}`);
  const scrollBox = document.getElementById(`chunks-${key}`);

  if (statsRow) {
    statsRow.innerHTML = `
      <span>Số chunk: <strong>${data.count}</strong></span>
      <span>Độ dài TB: <strong>${Math.round(data.avg_length)}</strong></span>
    `;
  }

  if (scrollBox) {
    scrollBox.innerHTML = (data.chunks || []).map((c, i) => `
      <div class="chunk-block">
        <div class="chunk-block-id">Chunk #${i + 1} (${c.length} ký tự)</div>
        <div>${escapeHtml(c.substring(0, 180))}${c.length > 180 ? '...' : ''}</div>
      </div>
    `).join("");
  }
}

// Data Inventory Loader
async function loadInventory() {
  const tbody = document.getElementById("inventory-tbody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/inventory");
    const docs = await res.json();

    tbody.innerHTML = docs.map(d => `
      <tr>
        <td><strong>${d.title}</strong><br><small style="color:var(--text-muted); font-family:var(--font-mono);">${d.doc_id}.md</small></td>
        <td><span class="badge ${d.audience === 'seller' ? 'warning' : 'accent'}">${d.audience}</span></td>
        <td><span class="badge neutral">${d.category}</span></td>
        <td style="color:var(--text-muted); text-decoration: line-through;">${d.raw_chars.toLocaleString()} ký tự</td>
        <td><strong style="color:var(--accent-emerald);">${d.clean_chars.toLocaleString()} ký tự</strong></td>
        <td><span class="badge success">-${d.reduction_percent}% rác</span></td>
        <td><code>${d.document_version}</code></td>
        <td><a href="${d.source_url}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">Xem nguồn ↗</a></td>
      </tr>
    `).join("");
  } catch (e) {
    console.error("Lỗi tải inventory:", e);
  }
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}
