// const API_BASE = "http://127.0.0.1:9000";
const API_BASE = "";
const token = localStorage.getItem("access_token");
const currentVendor = JSON.parse(localStorage.getItem("vendor") || "{}");

// ── Global State ──
let selectedNewFiles = [];
let selectedDetailFiles = [];
let selectedAgentDetailFiles = [];
let selectedAgentFiles = [];
let llmMap = {};
let globalLLMs = [];
let currentChatbotId = null;
let currentAgentId = null;
let sessionId = null;
let vendorSystemPromptEditor = null;
let agentSystemPromptEditor = null;

// Agent logs pagination
let agentCurrentPage = 0;
let agentPageSize = 50;
let agentTotalLogs = 0;
let activeAgentType = null;

// ══════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  if (currentVendor.name) {
    document.getElementById("vendorNameDisplay").textContent = currentVendor.name;
    document.getElementById("vendorInitial").textContent = currentVendor.name.charAt(0).toUpperCase();
  }

  // Chatbot modal Quill
  vendorSystemPromptEditor = new Quill("#chatbotSystemPromptEditor", {
    theme: "snow",
    placeholder: "Optional system instructions…",
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ["bold", "italic", "underline"],
        ["blockquote", "code-block", "link"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["clean"]
      ]
    }
  });

  // Agent modal Quill
  agentSystemPromptEditor = new Quill("#agentSystemPromptEditor", {
    theme: "snow",
    placeholder: "System instructions for this agent…",
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ["bold", "italic", "underline"],
        ["blockquote", "code-block", "link"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["clean"]
      ]
    }
  });

  showMainDashboard();
});

// ══════════════════════════════════════════════
//  TOAST
// ══════════════════════════════════════════════
function toast(msg, type = "success") {
  const container = document.getElementById("toastContainer");
  const el = document.createElement("div");
  el.className = `toast-msg ${type}`;
  const icon = type === "success" ? "bi-check-circle-fill" : "bi-exclamation-circle-fill";
  const color = type === "success" ? "var(--green)" : "var(--accent)";
  el.innerHTML = `<i class="bi ${icon}" style="color:${color}"></i> ${msg}`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ══════════════════════════════════════════════
//  SECTION CONTROL
// ══════════════════════════════════════════════
const ALL_SECTIONS = [
  "analyticsSection", "chatbotsSection", "chatbotDetailsSection",
  "agentMgmtSection", "agentDetailsSection",
  "documentsSection", "agentsSection", "apiTokensSection",
  "llmsSection", "embeddingsSection", "profileSection"
];

function showSection(section) {
  ALL_SECTIONS.forEach(id => document.getElementById(id).classList.add("d-none"));
  document.getElementById(section + "Section").classList.remove("d-none");

  const bubble = document.getElementById("chatBubble");
  const win = document.getElementById("chatWindow");
  if (section === "chatbotDetails") {
    bubble.style.display = "flex";
  } else {
    bubble.style.display = "none";
    win.style.display = "none";
  }
}

function setActiveNav(id) {
  document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
  if (id) document.getElementById(id)?.classList.add("active");
}

// ══════════════════════════════════════════════
//  AUTH / PROFILE
// ══════════════════════════════════════════════
function logout() { localStorage.clear(); window.location.href = "/"; }

function showProfileForm() {
  showSection("profile"); setActiveNav(null);
  document.getElementById("vendorName").value = currentVendor.name || "";
  document.getElementById("vendorEmail").value = currentVendor.email || "";
  document.getElementById("vendorDomain").value = currentVendor.domain || "";
}

async function saveProfile() {
  const res = await fetch(`${API_BASE}/vendors/update/${currentVendor.id}`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      name: document.getElementById("vendorName").value,
      email: document.getElementById("vendorEmail").value,
      domain: document.getElementById("vendorDomain").value
    })
  });
  res.ok ? toast("Profile updated successfully") : toast("Failed to update profile", "error");
}

function showChangePasswordModal() {
  new bootstrap.Modal(document.getElementById("changePasswordModal")).show();
}

async function submitChangePassword() {
  const current = document.getElementById("currentPassword").value;
  const newPass = document.getElementById("newPassword").value;
  const confirm = document.getElementById("confirmNewPassword").value;
  if (!current || !newPass || !confirm) return toast("Please fill all fields", "error");
  if (newPass !== confirm) return toast("Passwords do not match", "error");

  const res = await fetch(`${API_BASE}/vendors/change-password`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ current_password: current, new_password: newPass })
  });
  const data = await res.json();
  if (!res.ok) return toast(data.detail || "Failed", "error");
  toast("Password updated. Logging out…");
  bootstrap.Modal.getInstance(document.getElementById("changePasswordModal")).hide();
  setTimeout(logout, 1500);
}

// ══════════════════════════════════════════════
//  ANALYTICS
// ══════════════════════════════════════════════
async function showMainDashboard() {
  showSection("analytics"); setActiveNav("nav-analytics");
  await loadVendorUsers();
  await loadAnalytics();
}

async function loadVendorUsers() {
  const sel = document.getElementById("analyticsUserSelect");
  sel.innerHTML = `<option value="">All Users</option>`;
  try {
    const res = await fetch(`${API_BASE}/users/`, { headers: { Authorization: `Bearer ${token}` } });
    const users = await res.json();
    users.forEach(u => { sel.innerHTML += `<option value="${u.id}">${u.email || u.id}</option>`; });
  } catch (e) { console.error(e); }
}

async function loadAnalytics() {
  const list = document.getElementById("analyticsList");
  const userId = document.getElementById("analyticsUserSelect").value;
  const userCard = document.getElementById("userAnalyticsCard");
  const userContent = document.getElementById("userAnalyticsContent");
  list.innerHTML = "";

  if (userId) {
    userCard.classList.remove("d-none");
    userContent.innerHTML = "";
    const eps = [
      { label: "Tokens (Last 7 Days)", url: `/vendors/user/${userId}/tokens-last7`, key: "tokens_last_7_days", icon: "bi-lightning", color: "blue" },
      { label: "Total Tokens Used", url: `/vendors/user/${userId}/tokens-total`, key: "total_tokens", icon: "bi-stack", color: "purple" }
    ];
    for (const ep of eps) {
      const card = document.createElement("div");
      card.className = "stat-card";
      try {
        const res = await fetch(API_BASE + ep.url, { headers: { Authorization: `Bearer ${token}` } });
        const data = await res.json();
        const value = (typeof data === "number") ? data : data[ep.key] ?? 0;
        card.innerHTML = `
          <div class="stat-icon ${ep.color}"><i class="bi ${ep.icon}"></i></div>
          <div class="stat-label">${ep.label}</div>
          <div class="stat-value">${value.toLocaleString()}</div>`;
      } catch {
        card.innerHTML = `<div class="stat-label">${ep.label}</div><div style="color:var(--text-3);font-size:13px;">Failed to load</div>`;
      }
      userContent.appendChild(card);
    }
  } else {
    userCard.classList.add("d-none");
  }

  const endpoints = [
    { title: "Top Chatbots by Conversations", url: "/vendors/top-chatbots/conversations", headers: ["Chatbot", "Conversations"], keys: ["chatbot_name", "conversation_count"], icon: "bi-chat-square-dots" },
    { title: "Top Chatbots by Users", url: "/vendors/top-chatbots/users", headers: ["Chatbot", "Unique Users"], keys: ["chatbot_name", "unique_users"], icon: "bi-people" },
    { title: "Daily Messages", url: "/vendors/daily/messages", headers: ["Day", "Chatbot", "Messages"], keys: ["day", "chatbot_name", "messages"], icon: "bi-graph-up" },
    { title: "Daily Unique Users", url: "/vendors/daily/unique-users", headers: ["Day", "Chatbot", "Users"], keys: ["day", "chatbot_name", "unique_users"], icon: "bi-person-lines-fill" }
  ];

  for (const ep of endpoints) {
    const card = document.createElement("div");
    card.className = "card";
    try {
      const res = await fetch(API_BASE + ep.url, { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      let inner = `<div class="card-header-section"><div class="card-title"><i class="bi ${ep.icon}"></i> ${ep.title}</div></div>`;
      if (Array.isArray(data) && data.length) {
        inner += `<div style="overflow-x:auto;"><table class="data-table">
          <thead><tr>${ep.headers.map(h => `<th>${h}</th>`).join("")}</tr></thead>
          <tbody>${data.map(row => `<tr>${ep.keys.map(k => `<td>${row[k]}</td>`).join("")}</tr>`).join("")}</tbody>
        </table></div>`;
      } else {
        inner += `<div class="empty-state" style="padding:30px;"><i class="bi bi-inbox"></i><p>No data available</p></div>`;
      }
      card.innerHTML = inner;
    } catch {
      card.innerHTML = `<div class="card-header-section"><div class="card-title"><i class="bi ${ep.icon}"></i> ${ep.title}</div></div>
        <div style="padding:20px;color:var(--text-3);font-size:13px;">Failed to load</div>`;
    }
    list.appendChild(card);
  }
}

document.getElementById("analyticsUserSelect")?.addEventListener("change", loadAnalytics);

// ══════════════════════════════════════════════
//  LLM MAP
// ══════════════════════════════════════════════
async function loadLLMsMap() {
  try {
    const res = await fetch(`${API_BASE}/llms/`, { headers: { Authorization: `Bearer ${token}` } });
    globalLLMs = await res.json();
    llmMap = {};
    globalLLMs.forEach(l => llmMap[l.id] = l);
  } catch (e) { console.error(e); }
}

// ══════════════════════════════════════════════
//  CHATBOTS — LIST
// ══════════════════════════════════════════════
async function loadChatbots() {
  showSection("chatbots"); setActiveNav("nav-chatbots");
  const tbody = document.getElementById("chatbotList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="4"><span class="spinner"></span></td></tr>`;
  await loadLLMsMap();

  try {
    const res = await fetch(`${API_BASE}/chatbots/`, { headers: { Authorization: `Bearer ${token}` } });
    const bots = await res.json();

    if (!bots.length) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:40px;color:var(--text-3);">No chatbots found. Create your first one!</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    bots.forEach(b => {
      const llm = llmMap[b.llm_id];
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="color:var(--text-1);font-weight:500;">${b.name}</td>
        <td>${llm?.name || "N/A"}</td>
        <td><span class="badge ${b.is_active ? 'badge-green' : 'badge-gray'}">${b.is_active ? 'Active' : 'Inactive'}</span></td>
        <td>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            <button class="btn-warning-sm" onclick='openUpdateChatbotModal(${JSON.stringify(b).replace(/'/g, "\\'")})'>
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="btn-danger-sm" onclick="deleteChatbot(${b.id})">
              <i class="bi bi-trash"></i> Delete
            </button>
            <button class="btn-info-sm" onclick="showChatbotDetails(${b.id})">
              <i class="bi bi-arrow-right"></i> Details
            </button>
          </div>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" style="color:var(--accent);text-align:center;padding:20px;">Failed to load chatbots</td></tr>`;
  }
}

// ══════════════════════════════════════════════
//  CHATBOTS — MODAL
// ══════════════════════════════════════════════
function populateChatbotLLMDropdown(selectedId = null) {
  const sel = document.getElementById("chatbotLLMId");
  sel.innerHTML = "";
  globalLLMs.forEach(l => {
    const opt = document.createElement("option");
    opt.value = l.id; opt.text = l.name;
    opt.dataset.path = l.path || "";
    if (selectedId && l.id === selectedId) opt.selected = true;
    sel.appendChild(opt);
  });
  updateLLMPath();
}

function updateLLMPath() {
  const sel = document.getElementById("chatbotLLMId");
  const opt = sel.options[sel.selectedIndex];
  document.getElementById("chatbotLLMPath").value = opt?.dataset?.path || "";
}

function openAddChatbotModal() {
  document.getElementById("chatbotModalTitle").innerText = "Add Chatbot";
  document.getElementById("chatbotId").value = "";
  document.getElementById("chatbotName").value = "";
  document.getElementById("chatbotDescription").value = "";
  document.getElementById("chatbotIsActive").value = "true";
  populateChatbotLLMDropdown();
  new bootstrap.Modal(document.getElementById("chatbotModal")).show();
}

function openUpdateChatbotModal(bot) {
  if (typeof bot === "string") { try { bot = JSON.parse(bot); } catch { return toast("Failed to parse chatbot data", "error"); } }
  document.getElementById("chatbotModalTitle").innerText = "Update Chatbot";
  document.getElementById("chatbotId").value = bot.id;
  document.getElementById("chatbotName").value = bot.name;
  document.getElementById("chatbotDescription").value = bot.description || "";
  document.getElementById("chatbotIsActive").value = bot.is_active ? "true" : "false";
  document.getElementById("chatbotLLMPath").value = bot.llm_path || "";
  populateChatbotLLMDropdown(bot.llm_id);
  new bootstrap.Modal(document.getElementById("chatbotModal")).show();
}

async function submitChatbotForm() {
  const id = document.getElementById("chatbotId").value;
  const formData = new FormData();
  formData.append("name", document.getElementById("chatbotName").value);
  formData.append("description", document.getElementById("chatbotDescription").value || "");
  formData.append("llm_id", document.getElementById("chatbotLLMId").value);
  formData.append("llm_path", document.getElementById("chatbotLLMPath").value);
  formData.append("is_active", document.getElementById("chatbotIsActive").value === "true");
  formData.append("vendor_id", currentVendor.id);

  const url = id ? `${API_BASE}/chatbots/${id}` : `${API_BASE}/chatbots/create`;
  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, { method, headers: { Authorization: `Bearer ${token}` }, body: formData });
    if (!res.ok) { const err = await res.json(); return toast(err.detail || "Failed to save chatbot", "error"); }
    bootstrap.Modal.getInstance(document.getElementById("chatbotModal")).hide();
    toast(id ? "Chatbot updated" : "Chatbot created");
    loadChatbots();
  } catch (e) { toast("Something went wrong", "error"); }
}

async function deleteChatbot(id) {
  if (!confirm("Delete this chatbot?")) return;
  const res = await fetch(`${API_BASE}/chatbots/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
  res.ok ? (toast("Chatbot deleted"), loadChatbots()) : toast("Failed to delete", "error");
}

// ══════════════════════════════════════════════
//  CHATBOT DETAILS
// ══════════════════════════════════════════════
async function showChatbotDetails(chatbotId) {
  currentChatbotId = chatbotId;
  showSection("chatbotDetails");

  try {
    const res = await fetch(`${API_BASE}/chatbots/role-based-stats/${chatbotId}/vendor`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();

    document.getElementById("detailsChatbotName").innerText = data.name;
    document.getElementById("detailsChatbotCreatedAt").innerText = new Date(data.created_at).toLocaleString();
    document.getElementById("detailsChatbotDescription").innerText = data.description || "—";
    const statusEl = document.getElementById("detailsChatbotStatus");
    statusEl.textContent = data.is_active ? "Active" : "Inactive";
    statusEl.className = `badge ${data.is_active ? "badge-green" : "badge-gray"}`;

    let tokenHash = "";
    try {
      const keysRes = await fetch(`${API_BASE}/api-keys/list_of_keys`, { headers: { Authorization: `Bearer ${token}` } });
      const keysData = await keysRes.json();
      const k = (Array.isArray(keysData) ? keysData : []).find(k => k.chatbot_id === chatbotId);
      if (k) tokenHash = k.token_hash;
    } catch (e) { }

    const widgetScript = `<script 
  src="https://stolen-dev-intend-assessment.trycloudflare.com/static/widget.js" 
  data-chatbot-name="${data.name}" 
  data-chatbot-token="${tokenHash}">
<\/script>`;
    document.getElementById("detailsChatbotWidget").textContent = widgetScript;
    document.getElementById("copyWidgetBtn").onclick = () => {
      navigator.clipboard.writeText(widgetScript).then(() => toast("Snippet copied!")).catch(() => toast("Failed", "error"));
    };

    document.getElementById("chatBubble").onclick = () => openChat(chatbotId, data.name);

    await loadChatbotAgents(chatbotId);
    await loadChatbotDocuments(chatbotId);
  } catch (e) { toast("Failed to load chatbot details", "error"); }
}

async function loadChatbotAgents(chatbotId) {
  const container = document.getElementById("chatbotAgentsContainer");
  const countEl = document.getElementById("chatbotAgentCount");
  if (!container) return;
  container.innerHTML = `<div style="text-align:center;padding:16px;"><span class="spinner"></span></div>`;
  try {
    const res = await fetch(`${API_BASE}/agents-config/chatbot/${chatbotId}`, { headers: { Authorization: `Bearer ${token}` } });
    const agents = await res.json();
    if (countEl) countEl.textContent = `${agents.length} agent${agents.length !== 1 ? "s" : ""}`;

    if (!agents.length) {
      container.innerHTML = `<div class="empty-state" style="padding:24px;"><i class="bi bi-cpu"></i><p>No agents linked yet</p></div>`;
      return;
    }
    container.innerHTML = agents.map(a => {
      const typeCls = a.agent_type === "bank" ? "badge-blue" : "badge-purple";
      const statusCls = a.status === "active" ? "badge-green" : "badge-gray";
      return `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border-bottom:1px solid var(--border);">
          <div style="display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:13px;font-weight:600;color:var(--text-1);">${a.agent_name}</div>
            <span class="badge ${typeCls}" style="width:fit-content;">${a.agent_type}</span>
          </div>
          <span class="badge ${statusCls}">${a.status}</span>
        </div>`;
    }).join("");
  } catch (e) {
    container.innerHTML = `<div style="padding:16px;color:var(--accent);font-size:13px;">Failed to load agents</div>`;
  }
}

async function loadChatbotDocuments(chatbotId) {
  const container = document.getElementById("chatbotDocumentsContainer");
  if (!container) return;
  container.innerHTML = `<div style="text-align:center;padding:20px;"><span class="spinner"></span></div>`;
  try {
    const res = await fetch(`${API_BASE}/documents/chatbots_documents/${chatbotId}`, { headers: { Authorization: `Bearer ${token}` } });
    const docs = await res.json();
    if (!docs.length) { container.innerHTML = `<div class="empty-state"><i class="bi bi-file-earmark-x"></i><p>No documents</p></div>`; return; }
    container.innerHTML = docs.map(doc => {
      const cls = doc.status === "active" ? "badge-green" : doc.status === "processing" ? "badge-amber" : "badge-gray";
      return `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
        <div style="font-size:13px;color:var(--text-1);font-weight:500;">${doc.title}</div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
          <span class="badge ${cls}">${doc.status}</span>
          <span style="font-size:11px;color:var(--text-3);">${doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ""}</span>
        </div>
      </div>`;
    }).join("");
  } catch (e) { container.innerHTML = `<div style="color:var(--accent);font-size:13px;padding:16px;">Failed to load</div>`; }
}

function renderDetailSelectedFiles() {
  const preview = document.getElementById("selectedFilesPreviewDetail");
  preview.innerHTML = "";
  selectedDetailFiles.forEach((file, index) => {
    const li = document.createElement("div");
    li.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--surface2);border-radius:var(--radius-sm);margin-top:6px;font-size:12px;color:var(--text-2);";
    li.innerHTML = `<span><i class="bi bi-file-earmark" style="margin-right:6px;"></i>${file.name}</span>`;
    const btn = document.createElement("button");
    btn.innerHTML = '<i class="bi bi-x"></i>';
    btn.style.cssText = "background:none;border:none;color:var(--text-3);cursor:pointer;";
    btn.onclick = () => { selectedDetailFiles.splice(index, 1); renderDetailSelectedFiles(); };
    li.appendChild(btn); preview.appendChild(li);
  });
}

async function uploadDocumentsForDetail() {
  if (!currentChatbotId) return toast("No chatbot selected", "error");
  if (!selectedDetailFiles.length) return toast("Select files first", "error");
  const formData = new FormData();
  selectedDetailFiles.forEach(f => formData.append("files", f));
  const res = await fetch(`${API_BASE}/documents/chatbots/${currentChatbotId}/documents`, {
    method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData
  });
  if (!res.ok) { toast("Upload failed", "error"); return; }
  toast("Documents uploaded");
  selectedDetailFiles = [];
  document.getElementById("documentFilesDetail").value = "";
  renderDetailSelectedFiles();
  loadChatbotDocuments(currentChatbotId);
}

// ══════════════════════════════════════════════
//  CHAT
// ══════════════════════════════════════════════
function openChat(chatbotId, chatbotName) {
  const win = document.getElementById("chatWindow");
  win.style.display = "flex";
  document.getElementById("chatHeaderName").innerText = chatbotName;
  document.getElementById("chatMessages").innerHTML = "";
  document.getElementById("chatInput").value = "";
  currentChatbotId = chatbotId;
}

function closeChat() { document.getElementById("chatWindow").style.display = "none"; }

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  const chatMessages = document.getElementById("chatMessages");
  const userDiv = document.createElement("div");
  userDiv.classList.add("chat-message", "user");
  userDiv.textContent = message;
  chatMessages.appendChild(userDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  input.value = ""; input.disabled = true;

  try {
    const body = { question: message };
    if (sessionId) body.session_id = sessionId;
    const res = await fetch(`${API_BASE}/chatbots/test/${currentChatbotId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error("Failed to get response");
    const data = await res.json();
    if (!sessionId && data.session_id) sessionId = data.session_id;
    const botDiv = document.createElement("div");
    botDiv.classList.add("chat-message", "bot");
    botDiv.textContent = data.answer;
    chatMessages.appendChild(botDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (e) {
    const errDiv = document.createElement("div");
    errDiv.classList.add("chat-message", "bot");
    errDiv.textContent = `Error: ${e.message}`;
    chatMessages.appendChild(errDiv);
  } finally { input.disabled = false; input.focus(); }
}

// ══════════════════════════════════════════════
//  DOCUMENTS
// ══════════════════════════════════════════════
async function loadDocuments() {
  showSection("documents"); setActiveNav("nav-documents");
  selectedNewFiles = []; renderSelectedFiles();
  document.getElementById("documentList").innerHTML = "";
  document.getElementById("documentChatbotSelect").innerHTML = "";

  try {
    const botRes = await fetch(`${API_BASE}/chatbots/`, { headers: { Authorization: `Bearer ${token}` } });
    const bots = await botRes.json();
    bots.forEach(b => { document.getElementById("documentChatbotSelect").innerHTML += `<option value="${b.id}">${b.name}</option>`; });
    if (bots.length) loadDocumentsForChatbot(bots[0].id);
  } catch (e) { console.error(e); }
}

async function loadDocumentsForChatbot(chatbotId) {
  const list = document.getElementById("documentList");
  list.innerHTML = `<li style="padding:20px;text-align:center;"><span class="spinner"></span></li>`;
  try {
    const res = await fetch(`${API_BASE}/documents/specific_documents/${chatbotId}`, { headers: { Authorization: `Bearer ${token}` } });
    const docs = await res.json();
    if (!Array.isArray(docs) || !docs.length) {
      list.innerHTML = `<li style="padding:20px;text-align:center;color:var(--text-3);font-size:13px;">No documents found</li>`;
      return;
    }
    list.innerHTML = docs.map(d => {
      const cls = { processing: "badge-amber", embedded: "badge-green", processing_failed: "badge-red" }[d.status] || "badge-gray";
      return `<li style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--border);">
        <span style="font-size:13px;color:var(--text-1);">${d.title}</span>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="badge ${cls}">${d.status}</span>
          <button class="btn-danger-sm" onclick="deleteDocument(${d.id},this)"><i class="bi bi-trash"></i></button>
        </div>
      </li>`;
    }).join("");
  } catch (e) { list.innerHTML = `<li style="padding:20px;color:var(--accent);font-size:13px;">Failed to load</li>`; }
}

document.getElementById("documentChatbotSelect")?.addEventListener("change", e => loadDocumentsForChatbot(e.target.value));

function handleDocumentFileSelect(e) {
  Array.from(e.target.files).forEach(f => {
    if (!selectedNewFiles.some(x => x.name === f.name && x.size === f.size)) selectedNewFiles.push(f);
  });
  e.target.value = "";
  renderSelectedFiles();
}

function renderSelectedFiles() {
  const preview = document.getElementById("selectedFilesPreview");
  preview.innerHTML = "";
  selectedNewFiles.forEach((f, index) => {
    const li = document.createElement("div");
    li.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--surface2);border-radius:var(--radius-sm);font-size:12px;color:var(--text-2);";
    li.innerHTML = `<span><i class="bi bi-file-earmark" style="margin-right:6px;"></i>${f.name}</span>`;
    const btn = document.createElement("button");
    btn.innerHTML = '<i class="bi bi-x"></i>';
    btn.style.cssText = "background:none;border:none;color:var(--text-3);cursor:pointer;";
    btn.addEventListener("click", () => { selectedNewFiles.splice(index, 1); renderSelectedFiles(); });
    li.appendChild(btn); preview.appendChild(li);
  });
}

async function uploadDocuments() {
  if (!selectedNewFiles.length) return toast("Select files first", "error");
  const chatbotId = document.getElementById("documentChatbotSelect").value;
  if (!chatbotId) return toast("Select a chatbot", "error");
  const formData = new FormData();
  selectedNewFiles.forEach(f => formData.append("files", f));
  const res = await fetch(`${API_BASE}/documents/chatbots/${chatbotId}/documents`, {
    method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData
  });
  if (!res.ok) { toast("Upload failed", "error"); return; }
  toast("Documents uploaded");
  selectedNewFiles = []; renderSelectedFiles(); loadDocuments();
}

async function deleteDocument(id, btn) {
  await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
  btn.closest("li").remove();
  toast("Document deleted");
}

// ══════════════════════════════════════════════
//  AGENTS MANAGEMENT
// ══════════════════════════════════════════════
async function loadAgentMgmt() {
  showSection("agentMgmt");
  setActiveNav("nav-agentMgmt");

  const tbody = document.getElementById("agentMgmtList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="6"><span class="spinner"></span></td></tr>`;

  await loadLLMsMap(); // this builds llmMap

  try {
    const res = await fetch(`${API_BASE}/agents-config/vendor/my-agents`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const agents = await res.json();

    if (!agents.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center;padding:40px;color:var(--text-3);">
            No agents found. Create your first one!
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = "";

    agents.forEach(a => {
      const typeCls = a.agent_type === "bank" ? "badge-blue" : "badge-purple";
      const statusCls = a.status === "active" ? "badge-green" : "badge-gray";

      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td><span class="badge ${typeCls}">${a.agent_type}</span></td>
        <td style="color:var(--text-1);font-weight:500;">${a.agent_name}</td>
        <td style="color:var(--text-2);font-size:12px;">${llmMap[a.llm_id] || "N/A"}</td>
        <td style="color:var(--text-2);font-size:12px;">${a.vector_store_type || "N/A"}</td>
        <td><span class="badge ${statusCls}">${a.status}</span></td>
        <td>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            <button class="btn-warning-sm" data-agent-id="${a.id}">
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="btn-danger-sm" onclick="deleteAgent(${a.id})">
              <i class="bi bi-trash"></i> Delete
            </button>
            <button class="btn-info-sm" onclick="showAgentDetails(${a.id})">
              <i class="bi bi-arrow-right"></i> Details
            </button>
          </div>
        </td>
      `;

      tr.querySelector(".btn-warning-sm")
        .addEventListener("click", () => openUpdateAgentModal(a));

      tbody.appendChild(tr);
    });

  } catch (e) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="color:var(--accent);text-align:center;padding:20px;">
          Failed to load agents
        </td>
      </tr>`;
    console.error(e);
  }
}

// ── Activate Agent (beside Add Agent button) ──
async function activateAgentFromSelect() {
  const agentType = document.getElementById("activeAgentSelect").value;
  if (!agentType) return toast("Please select an agent type first", "error");

  const btn = document.querySelector('[onclick="activateAgentFromSelect()"]');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Activating…'; }

  try {
    const res = await fetch(`${API_BASE}/agents-config/activate`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ agent_type: agentType })
    });

    if (!res.ok) {
      const err = await res.json();
      return toast(err.detail || "Activation failed", "error");
    }

    toast(`${agentType.charAt(0).toUpperCase() + agentType.slice(1)} agent activated successfully`);
    document.getElementById("activeAgentSelect").value = "";
  } catch (e) {
    toast("Could not reach server", "error");
    console.error(e);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-check2-circle"></i> Activate'; }
  }
}

// ── Agent Details ──
async function showAgentDetails(agentId) {
  currentAgentId = agentId;
  showSection("agentDetails");

  try {
    const res = await fetch(`${API_BASE}/agents-config/${agentId}`, { headers: { Authorization: `Bearer ${token}` } });
    const agent = await res.json();

    const typeCls = agent.agent_type === "bank" ? "badge-blue" : "badge-purple";
    const statusCls = agent.status === "active" ? "badge-green" : "badge-gray";

    document.getElementById("agentDetailName").textContent = agent.agent_name;
    document.getElementById("agentDetailVectorStore").textContent = agent.vector_store_type || "N/A";
    document.getElementById("agentDetailCreatedAt").textContent = new Date(agent.created_at).toLocaleString();

    // ── Render system prompt as formatted HTML (from Quill) ──
    const spEl = document.getElementById("agentDetailSystemPrompt");
    const rawPrompt = (agent.system_prompt || "").trim();
    if (rawPrompt && rawPrompt !== "<p><br></p>") {
      // Detect if it's HTML (Quill output) or plain text
      const isHtml = /<[a-z][\s\S]*>/i.test(rawPrompt);
      if (isHtml) {
        spEl.innerHTML = rawPrompt;
      } else {
        // Plain text — wrap paragraphs
        spEl.innerHTML = rawPrompt
          .split("\n\n")
          .map(para => `<p>${para.replace(/\n/g, "<br>")}</p>`)
          .join("");
      }
    } else {
      spEl.innerHTML = `<span style="color:var(--text-3);">No system prompt set.</span>`;
    }

    const typeEl = document.getElementById("agentDetailType");
    typeEl.innerHTML = `<span class="badge ${typeCls}">${agent.agent_type}</span>`;

    const statusEl = document.getElementById("agentDetailStatus");
    statusEl.textContent = agent.status;
    statusEl.className = `badge ${statusCls}`;

    // Chatbot name
    try {
      const botRes = await fetch(`${API_BASE}/chatbots/${agent.chatbot_id}`, { headers: { Authorization: `Bearer ${token}` } });
      const bot = await botRes.json();
      document.getElementById("agentDetailChatbot").textContent = `${bot.name} (ID: ${bot.id})`;
    } catch { document.getElementById("agentDetailChatbot").textContent = `Chatbot ID: ${agent.chatbot_id}`; }

    // Vector DB info
    try {
      const vdbRes = await fetch(`${API_BASE}/vector_dbs/agent/${agentId}`, { headers: { Authorization: `Bearer ${token}` } });
      if (vdbRes.ok) {
        const vdb = await vdbRes.json();
        document.getElementById("agentDetailVectorDB").innerHTML = vdb
          ? `<div style="font-size:13px;color:var(--text-1);font-weight:500;margin-bottom:6px;">${vdb.name}</div>
             <code style="font-size:11px;color:var(--text-3);background:var(--surface2);padding:4px 8px;border-radius:4px;display:block;word-break:break-all;">${vdb.db_path}</code>
             <div style="margin-top:8px;"><span class="badge ${vdb.is_active ? 'badge-green' : 'badge-gray'}">${vdb.is_active ? 'Active' : 'Inactive'}</span></div>`
          : "No vector DB attached yet.";
      }
    } catch { }

    await loadAgentDetailDocs(agentId);
  } catch (e) { toast("Failed to load agent details", "error"); console.error(e); }
}

async function loadAgentDetailDocs(agentId) {
  const container = document.getElementById("agentDetailDocsList");
  container.innerHTML = `<div style="text-align:center;padding:20px;"><span class="spinner"></span></div>`;
  try {
    const res = await fetch(`${API_BASE}/documents/agent/${agentId}`, { headers: { Authorization: `Bearer ${token}` } });
    const docs = await res.json();
    if (!docs.length) {
      container.innerHTML = `<div class="empty-state" style="padding:24px;"><i class="bi bi-file-earmark-x"></i><p>No documents yet</p></div>`;
      return;
    }
    container.innerHTML = docs.map(doc => {
      const cls = { processing: "badge-amber", embedded: "badge-green", processing_failed: "badge-red" }[doc.status] || "badge-gray";
      return `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);">
        <div>
          <div style="font-size:13px;color:var(--text-1);font-weight:500;">${doc.title}</div>
          ${doc.hash_address ? `<div style="font-size:11px;color:var(--text-3);margin-top:2px;">Hash: ${doc.hash_address}</div>` : ""}
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
          <span class="badge ${cls}">${doc.status}</span>
          <span style="font-size:11px;color:var(--text-3);">${doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ""}</span>
        </div>
      </div>`;
    }).join("");
  } catch (e) { container.innerHTML = `<div style="color:var(--accent);font-size:13px;padding:16px;">Failed to load documents</div>`; }
}

function renderAgentDetailFiles() {
  const preview = document.getElementById("agentDocFilesPreview");
  preview.innerHTML = "";
  selectedAgentDetailFiles.forEach((file, index) => {
    const li = document.createElement("div");
    li.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--surface2);border-radius:var(--radius-sm);margin-top:6px;font-size:12px;color:var(--text-2);";
    li.innerHTML = `<span><i class="bi bi-file-earmark" style="margin-right:6px;"></i>${file.name}</span>`;
    const btn = document.createElement("button");
    btn.innerHTML = '<i class="bi bi-x"></i>';
    btn.style.cssText = "background:none;border:none;color:var(--text-3);cursor:pointer;";
    btn.onclick = () => { selectedAgentDetailFiles.splice(index, 1); renderAgentDetailFiles(); };
    li.appendChild(btn); preview.appendChild(li);
  });
}

async function uploadAgentDocuments() {
  if (!currentAgentId) return toast("No agent selected", "error");
  if (!selectedAgentDetailFiles.length) return toast("Select files first", "error");
  const formData = new FormData();
  selectedAgentDetailFiles.forEach(f => formData.append("files", f));
  const res = await fetch(`${API_BASE}/documents/agents/${currentAgentId}/documents`, {
    method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData
  });
  if (!res.ok) { toast("Upload failed", "error"); return; }
  toast("Documents uploaded");
  selectedAgentDetailFiles = [];
  document.getElementById("agentDocFiles").value = "";
  renderAgentDetailFiles();
  loadAgentDetailDocs(currentAgentId);
}

function populateAgentLLMDropdown(selectedId = null) {
  const sel = document.getElementById("agentLLMId");
  sel.innerHTML = "";
  globalLLMs.forEach(l => {
    const opt = document.createElement("option");
    opt.value = l.id; opt.text = l.name;
    opt.dataset.path = l.path || "";
    if (selectedId && l.id === selectedId) opt.selected = true;
    sel.appendChild(opt);
  });
  updateLLMPath();
}

function updateLLMPath() {
  const sel = document.getElementById("agentLLMId");
  const opt = sel.options[sel.selectedIndex];
  document.getElementById("agentLLMPath").value = opt?.dataset?.path || "";
}

// ── Agent Modal ──
async function openAddAgentModal() {
  document.getElementById("agentModalTitle").innerText = "New Agent";
  document.getElementById("agentId").value = "";
  document.getElementById("agentType").value = "";
  document.getElementById("agentName").value = "";

  await populateAgentLLMDropdown();

  document.getElementById("agentVectorStore").value = "chroma";
  document.getElementById("agentStatus").value = "active";

  if (agentSystemPromptEditor) {
    agentSystemPromptEditor.root.innerHTML = "";
  }

  selectedAgentFiles = [];
  renderAgentFilesPreview();

  new bootstrap.Modal(document.getElementById("agentModal")).show();
}

async function openUpdateAgentModal(agent) {
  if (typeof agent === "string") {
    try {
      agent = JSON.parse(agent);
    } catch {
      return toast("Failed to parse", "error");
    }
  }

  document.getElementById("agentModalTitle").innerText = "Update Agent";
  document.getElementById("agentId").value = agent.id;
  document.getElementById("agentType").value = agent.agent_type;
  document.getElementById("agentName").value = agent.agent_name;

  document.getElementById("agentLLMPath").value = agent.llm_path || "";

  await populateAgentLLMDropdown(agent.llm_id);

  document.getElementById("agentVectorStore").value =
    agent.vector_store_type || "chroma";

  document.getElementById("agentStatus").value =
    agent.status || "active";

  if (agentSystemPromptEditor) {
    agentSystemPromptEditor.root.innerHTML =
      agent.system_prompt || "";
  }

  selectedAgentFiles = [];
  renderAgentFilesPreview();

  new bootstrap.Modal(document.getElementById("agentModal")).show();
}

// ── FILE HANDLING ──
function handleAgentFileSelect(event) {
  Array.from(event.target.files).forEach(f => {
    if (!selectedAgentFiles.some(x => x.name === f.name && x.size === f.size)) {
      selectedAgentFiles.push(f);
    }
  });

  event.target.value = "";
  renderAgentFilesPreview();
}

function renderAgentFilesPreview() {
  const preview = document.getElementById("agentFilesPreview");
  preview.innerHTML = "";

  selectedAgentFiles.forEach((file, index) => {
    const li = document.createElement("div");

    li.style.cssText =
      "display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--surface2);border-radius:var(--radius-sm);font-size:12px;color:var(--text-2);";

    li.innerHTML = `
      <span>
        <i class="bi bi-file-earmark" style="margin-right:6px;"></i>
        ${file.name}
      </span>
    `;

    const btn = document.createElement("button");
    btn.innerHTML = '<i class="bi bi-x"></i>';
    btn.style.cssText =
      "background:none;border:none;color:var(--text-3);cursor:pointer;";

    btn.addEventListener("click", () => {
      selectedAgentFiles.splice(index, 1);
      renderAgentFilesPreview();
    });

    li.appendChild(btn);
    preview.appendChild(li);
  });
}

// ── SUBMIT FORM ──
async function submitAgentForm() {
  const id = document.getElementById("agentId").value;

  const systemPrompt = agentSystemPromptEditor
    ? agentSystemPromptEditor.root.innerHTML
    : "";

  const formData = new FormData();

  // 🔥 SAFE vendor_id handling
  const vendorId = Number(currentVendor?.id);
  if (!vendorId) {
    return toast("Vendor not found. Please log in again.", "error");
  }

  // ── REQUIRED FIELDS ──
  formData.append("vendor_id", vendorId);
  formData.append("agent_type", document.getElementById("agentType").value);
  formData.append("agent_name", document.getElementById("agentName").value);

  formData.append(
    "llm_id",
    Number(document.getElementById("agentLLMId").value)
  );

  formData.append(
    "llm_path",
    document.getElementById("agentLLMPath").value || ""
  );

  formData.append(
    "vector_store_type",
    document.getElementById("agentVectorStore").value || "chroma"
  );

  formData.append(
    "status",
    document.getElementById("agentStatus").value
  );

  formData.append("system_prompt", systemPrompt || "");

  // ── FILES ──
  selectedAgentFiles.forEach(f => formData.append("files", f));

  const url = id
    ? `${API_BASE}/agents-config/${id}`
    : `${API_BASE}/agents-config/create`;

  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      return toast(err.detail || "Failed to save agent", "error");
    }

    bootstrap.Modal.getInstance(
      document.getElementById("agentModal")
    ).hide();

    selectedAgentFiles = [];
    renderAgentFilesPreview();

    toast(id ? "Agent updated" : "Agent created");

    loadAgentMgmt();
  } catch (e) {
    toast("Something went wrong", "error");
    console.error(e);
  }
}

async function deleteAgent(agentId) {
  if (!confirm("Delete this agent? This will also remove its documents and vector DB.")) return;
  const res = await fetch(`${API_BASE}/agents-config/${agentId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
  res.ok ? (toast("Agent deleted"), loadAgentMgmt()) : toast("Failed to delete agent", "error");
}

// ══════════════════════════════════════════════
//  AGENT LOGS
// ══════════════════════════════════════════════
function loadAgents() {
  showSection("agents"); setActiveNav("nav-agents");
  agentCurrentPage = 0; activeAgentType = null;
  document.querySelectorAll(".agent-tab").forEach(t => t.classList.remove("active"));
  document.getElementById("tab-all")?.classList.add("active");
  loadAgentLogs();
}

function selectAgentType(type, btn) {
  activeAgentType = type; agentCurrentPage = 0;
  document.querySelectorAll(".agent-tab").forEach(t => t.classList.remove("active"));
  btn.classList.add("active");
  loadAgentLogs();
}

function applyAgentFilters() { agentCurrentPage = 0; loadAgentLogs(); }

function clearAgentFilters() {
  ["filterAgentName", "filterToolName", "filterFromDate", "filterToDate"].forEach(id => document.getElementById(id).value = "");
  document.getElementById("filterToolStatus").value = "";
  agentCurrentPage = 0; loadAgentLogs();
}

function changePage(dir) { agentCurrentPage += dir; loadAgentLogs(); }

async function loadAgentLogs() {
  const tbody = document.getElementById("agentLogsList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="6"><span class="spinner"></span></td></tr>`;

  const params = new URLSearchParams();
  if (activeAgentType) params.set("agent_type", activeAgentType);

  const agentName = document.getElementById("filterAgentName")?.value.trim();
  const toolStatus = document.getElementById("filterToolStatus")?.value;
  const toolName = document.getElementById("filterToolName")?.value.trim();
  const fromDate = document.getElementById("filterFromDate")?.value;
  const toDate = document.getElementById("filterToDate")?.value;

  if (agentName) params.set("agent_name", agentName);
  if (toolStatus) params.set("tool_status", toolStatus);
  if (toolName) params.set("tool_name", toolName);
  if (fromDate) params.set("from_date", fromDate);
  if (toDate) params.set("to_date", toDate);

  params.set("limit", agentPageSize);
  params.set("offset", agentCurrentPage * agentPageSize);

  try {
    const [logsRes, countRes] = await Promise.all([
      fetch(`${API_BASE}/agents/vendor/agent-logs?${params}`, { headers: { Authorization: `Bearer ${token}` } }),
      fetch(`${API_BASE}/agents/vendor/agent-logs/count?${params}`, { headers: { Authorization: `Bearer ${token}` } })
    ]);

    const logs = await logsRes.json();
    const countData = await countRes.json();
    agentTotalLogs = countData.total_logs ?? 0;
    document.getElementById("logCount").textContent = `${agentTotalLogs.toLocaleString()} log${agentTotalLogs !== 1 ? "s" : ""}`;

    if (!logs.length) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><i class="bi bi-journal-x"></i><p>No logs found</p></div></td></tr>`;
      document.getElementById("logsPagination").style.display = "none";
      return;
    }

    tbody.innerHTML = logs.map(log => {
      const statusCls = { success: "badge-green", failed: "badge-red", error: "badge-amber" }[log.tool_status] || "badge-gray";
      const typeCls = { bank: "badge-blue", hotel: "badge-purple" }[log.agent_type] || "badge-gray";
      const time = new Date(log.created_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
      return `
        <tr>
          <td>
            <div style="display:flex;flex-direction:column;gap:4px;">
              <span class="badge ${typeCls}" style="width:fit-content;">${log.agent_type}</span>
              <span style="font-size:11px;color:var(--text-3);">${log.agent_name}</span>
            </div>
          </td>
          <td><code style="font-size:11px;color:var(--blue);background:rgba(77,158,247,0.08);padding:3px 7px;border-radius:4px;">${log.tool_name || "—"}</code></td>
          <td><span class="badge ${statusCls}">${log.tool_status || "—"}</span></td>
          <td><div class="log-desc" title="${log.short_description}">${log.short_description}</div></td>
          <td style="font-size:12px;color:var(--text-3);">${log.user_identifier || "—"}</td>
          <td style="font-size:12px;color:var(--text-3);white-space:nowrap;">${time}</td>
        </tr>`;
    }).join("");

    const totalPages = Math.ceil(agentTotalLogs / agentPageSize);
    const pagination = document.getElementById("logsPagination");
    if (totalPages > 1) {
      pagination.style.display = "flex";
      document.getElementById("paginationInfo").textContent = `Page ${agentCurrentPage + 1} of ${totalPages}`;
      document.getElementById("prevPage").disabled = agentCurrentPage === 0;
      document.getElementById("nextPage").disabled = agentCurrentPage >= totalPages - 1;
    } else {
      pagination.style.display = "none";
    }
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--accent);font-size:13px;">Failed to load logs</td></tr>`;
    console.error(e);
  }
}

// ══════════════════════════════════════════════
//  API TOKENS
// ══════════════════════════════════════════════
async function loadAPITokens() {
  showSection("apiTokens"); setActiveNav("nav-apiTokens");
  const tbody = document.getElementById("apiTokensList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="5"><span class="spinner"></span></td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api-keys/list_of_keys`, { headers: { Authorization: `Bearer ${token}` } });
    const keys = await res.json();
    if (!keys.length) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--text-3);">No API tokens found</td></tr>`; return; }

    const botsRes = await fetch(`${API_BASE}/chatbots/`, { headers: { Authorization: `Bearer ${token}` } });
    const bots = await botsRes.json();
    const botMap = {}; bots.forEach(b => botMap[b.id] = b.name);

    tbody.innerHTML = keys.map(k => `
      <tr>
        <td style="color:var(--text-1);font-weight:500;">${botMap[k.chatbot_id] || "N/A"}</td>
        <td>${k.vendor_domain}</td>
        <td>
          <div style="display:flex;align-items:center;gap:8px;">
            <code style="font-size:11px;color:var(--text-3);background:var(--surface2);padding:4px 8px;border-radius:4px;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${k.token_hash}</code>
            <button class="btn-ghost" style="padding:4px 10px;font-size:11px;" onclick="copyToken('${k.token_hash}',this)">
              <i class="bi bi-clipboard"></i> Copy
            </button>
          </div>
        </td>
        <td><span class="badge ${k.status === 'active' ? 'badge-green' : 'badge-gray'}">${k.status}</span></td>
        <td style="color:var(--text-3);font-size:12px;">${new Date(k.created_at).toLocaleString()}</td>
      </tr>`).join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" style="color:var(--accent);text-align:center;padding:20px;">Failed to load tokens</td></tr>`;
  }
}

function copyToken(hash, btn) {
  navigator.clipboard.writeText(hash).then(() => {
    btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
    setTimeout(() => btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy', 1500);
  });
}

async function openCreateApiTokenModal() {
  const sel = document.getElementById("apiTokenChatbotSelect");
  sel.innerHTML = `<option value="">Loading…</option>`;
  document.getElementById("apiTokenDomain").value = currentVendor.domain || "";
  try {
    const res = await fetch(`${API_BASE}/chatbots/`, { headers: { Authorization: `Bearer ${token}` } });
    const bots = await res.json();
    sel.innerHTML = `<option value="">-- Select Chatbot --</option>`;
    bots.forEach(b => { const o = document.createElement("option"); o.value = b.id; o.textContent = b.name; sel.appendChild(o); });
  } catch { sel.innerHTML = `<option value="">Failed to load chatbots</option>`; }
  new bootstrap.Modal(document.getElementById("createApiTokenModal")).show();
}

async function submitCreateApiToken() {
  const chatbotId = document.getElementById("apiTokenChatbotSelect").value;
  const domain = document.getElementById("apiTokenDomain").value.trim();
  if (!chatbotId) return toast("Please select a chatbot", "error");
  if (!domain) return toast("Domain is required", "error");

  try {
    const res = await fetch(`${API_BASE}/api-keys/create`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ vendor_id: currentVendor.id, chatbot_id: parseInt(chatbotId), vendor_domain: domain })
    });
    if (!res.ok) { const err = await res.json(); return toast(err.detail || "Failed", "error"); }
    const data = await res.json();
    bootstrap.Modal.getInstance(document.getElementById("createApiTokenModal")).hide();
    toast("API Token created");
    if (data.token) setTimeout(() => alert(`Your new API Token (save this — it won't be shown again):\n\n${data.token}`), 300);
    loadAPITokens();
  } catch (e) { toast("Something went wrong", "error"); }
}

// ══════════════════════════════════════════════
//  EMBEDDINGS — FULL CRUD
// ══════════════════════════════════════════════
async function loadEmbeddings() {
  showSection("embeddings"); setActiveNav("nav-embeddings");
  const tbody = document.getElementById("embeddingList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="3"><span class="spinner"></span></td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/embeddings/`, { headers: { Authorization: `Bearer ${token}` } });
    const embeds = await res.json();

    if (!embeds.length) {
      tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;padding:40px;color:var(--text-3);">No embedding models yet. Add your first one!</td></tr>`;
      return;
    }

    tbody.innerHTML = embeds.map(e => `
      <tr>
        <td style="color:var(--text-1);font-weight:500;">${e.model_name}</td>
        <td><span class="badge badge-blue">${e.provider}</span></td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn-warning-sm" onclick='openUpdateEmbeddingModal(${JSON.stringify(e).replace(/'/g, "\\'")})'>
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="btn-danger-sm" onclick="deleteEmbedding(${e.id})">
              <i class="bi bi-trash"></i> Delete
            </button>
          </div>
        </td>
      </tr>`).join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="3" style="color:var(--accent);text-align:center;padding:20px;">Failed to load embeddings</td></tr>`;
  }
}

function openAddEmbeddingModal() {
  document.getElementById("embeddingModalTitle").innerText = "Add Embedding";
  document.getElementById("embeddingId").value = "";
  document.getElementById("embeddingModelName").value = "";
  document.getElementById("embeddingProvider").value = "ollama";
  document.getElementById("embeddingPath").value = "";
  new bootstrap.Modal(document.getElementById("embeddingModal")).show();
}

function openUpdateEmbeddingModal(embed) {
  if (typeof embed === "string") { try { embed = JSON.parse(embed); } catch { return toast("Parse error", "error"); } }
  document.getElementById("embeddingModalTitle").innerText = "Update Embedding";
  document.getElementById("embeddingId").value = embed.id;
  document.getElementById("embeddingModelName").value = embed.model_name;
  document.getElementById("embeddingProvider").value = embed.provider;
  document.getElementById("embeddingPath").value = embed.path || "";
  new bootstrap.Modal(document.getElementById("embeddingModal")).show();
}

async function submitEmbeddingForm() {
  const id = document.getElementById("embeddingId").value;
  const payload = {
    model_name: document.getElementById("embeddingModelName").value,
    provider: document.getElementById("embeddingProvider").value,
    path: document.getElementById("embeddingPath").value || null,
  };

  const url = id ? `${API_BASE}/embeddings/update/${id}` : `${API_BASE}/embeddings/create`;
  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) { const err = await res.json(); return toast(err.detail || "Failed", "error"); }
    bootstrap.Modal.getInstance(document.getElementById("embeddingModal")).hide();
    toast(id ? "Embedding updated" : "Embedding added");
    loadEmbeddings();
  } catch (e) { toast("Something went wrong", "error"); }
}

async function deleteEmbedding(id) {
  if (!confirm("Delete this embedding model? Any LLMs using it will be affected.")) return;
  const res = await fetch(`${API_BASE}/embeddings/delete/${id}`, {
    method: "DELETE", headers: { Authorization: `Bearer ${token}` }
  });
  res.ok ? (toast("Embedding deleted"), loadEmbeddings()) : toast("Failed to delete", "error");
}

// ══════════════════════════════════════════════
//  LLMs — FULL CRUD
// ══════════════════════════════════════════════
async function loadLLMs() {
  showSection("llms"); setActiveNav("nav-llms");
  const tbody = document.getElementById("llmList");
  tbody.innerHTML = `<tr class="loading-row"><td colspan="5"><span class="spinner"></span></td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/llms/`, { headers: { Authorization: `Bearer ${token}` } });
    const llms = await res.json();

    if (!llms.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--text-3);">No LLMs yet. Add your first one!</td></tr>`;
      return;
    }

    tbody.innerHTML = llms.map(l => `
      <tr>
        <td style="color:var(--text-1);font-weight:500;">${l.name}</td>
        <td><span class="badge badge-purple">${l.provider}</span></td>
        <td style="color:var(--text-2);font-size:12px;">${l.embedding?.model_name || "N/A"}</td>
        <td style="color:var(--text-3);font-size:12px;">${(l.def_token_limit || 0).toLocaleString()} / ${(l.def_context_limit || 0).toLocaleString()}</td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn-warning-sm" onclick='openUpdateLLMModal(${JSON.stringify(l).replace(/'/g, "\\'")})'>
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="btn-danger-sm" onclick="deleteLLM(${l.id})">
              <i class="bi bi-trash"></i> Delete
            </button>
          </div>
        </td>
      </tr>`).join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" style="color:var(--accent);text-align:center;padding:20px;">Failed to load LLMs</td></tr>`;
  }
}

async function populateLLMEmbeddingDropdown(selectedId = null) {
  const sel = document.getElementById("llmEmbeddingId");
  sel.innerHTML = `<option value="">Loading…</option>`;
  try {
    const res = await fetch(`${API_BASE}/embeddings/`, { headers: { Authorization: `Bearer ${token}` } });
    const embeds = await res.json();
    sel.innerHTML = embeds.length
      ? embeds.map(e => `<option value="${e.id}" ${selectedId === e.id ? "selected" : ""}>${e.model_name} (${e.provider})</option>`).join("")
      : `<option value="">No embeddings found — add one first</option>`;
  } catch { sel.innerHTML = `<option value="">Failed to load</option>`; }
}

async function openAddLLMModal() {
  document.getElementById("llmModalTitle").innerText = "Add LLM";
  document.getElementById("llmId").value = "";
  document.getElementById("llmName").value = "";
  document.getElementById("llmProvider").value = "ollama";
  document.getElementById("llmTokenLimit").value = "";
  document.getElementById("llmContextLimit").value = "";
  document.getElementById("llmPath").value = "";
  await populateLLMEmbeddingDropdown();
  new bootstrap.Modal(document.getElementById("llmModal")).show();
}

async function openUpdateLLMModal(llm) {
  if (typeof llm === "string") { try { llm = JSON.parse(llm); } catch { return toast("Parse error", "error"); } }
  document.getElementById("llmModalTitle").innerText = "Update LLM";
  document.getElementById("llmId").value = llm.id;
  document.getElementById("llmName").value = llm.name;
  document.getElementById("llmProvider").value = llm.provider;
  document.getElementById("llmTokenLimit").value = llm.def_token_limit;
  document.getElementById("llmContextLimit").value = llm.def_context_limit;
  document.getElementById("llmPath").value = llm.path || "";
  await populateLLMEmbeddingDropdown(llm.embedding_id);
  new bootstrap.Modal(document.getElementById("llmModal")).show();
}

async function submitLLMForm() {
  const id = document.getElementById("llmId").value;
  const payload = {
    name: document.getElementById("llmName").value,
    provider: document.getElementById("llmProvider").value,
    embedding_id: parseInt(document.getElementById("llmEmbeddingId").value),
    def_token_limit: parseInt(document.getElementById("llmTokenLimit").value),
    def_context_limit: parseInt(document.getElementById("llmContextLimit").value),
    path: document.getElementById("llmPath").value || null,
  };

  if (!payload.name || !payload.embedding_id || !payload.def_token_limit || !payload.def_context_limit) {
    return toast("Please fill all required fields", "error");
  }

  const url = id ? `${API_BASE}/llms/${id}` : `${API_BASE}/llms/`;
  const method = id ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) { const err = await res.json(); return toast(err.detail || "Failed", "error"); }
    bootstrap.Modal.getInstance(document.getElementById("llmModal")).hide();
    toast(id ? "LLM updated" : "LLM added");
    loadLLMs();
    loadLLMsMap();
  } catch (e) { toast("Something went wrong", "error"); }
}

async function deleteLLM(id) {
  if (!confirm("Delete this LLM? Any chatbots using it will be affected.")) return;
  const res = await fetch(`${API_BASE}/llms/${id}`, {
    method: "DELETE", headers: { Authorization: `Bearer ${token}` }
  });
  res.ok ? (toast("LLM deleted"), loadLLMs()) : toast("Failed to delete", "error");
}