// Globals
window.activeChatbotId = null;
window.activeChatbotName = null;
let selectedDetailFiles = [];

function showSection(section) {
  // All possible sections including dashboard
  const sections = [
    "dashboard",
    "chatbots",
    "vendors",
    "documents",
    "embeddings",
    "llms",
    "chatbotDetails",
    "adminApiTokens"
  ];

  // Hide all sections
  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add("d-none");
  });

  // Show the requested section
  const target = document.getElementById(section);
  if (target) target.classList.remove("d-none");

  // Chat bubble & window references
  const chatBubble = document.getElementById("chatBubble");
  const chatWindow = document.getElementById("chatWindow");

  // Always hide chat bubble & window first
  if (chatBubble) chatBubble.style.display = "none";
  if (chatWindow) chatWindow.style.display = "none";

  // Only show chat bubble if we're in chatbotDetails
  if (section === "chatbotDetails" && chatBubble) {
    chatBubble.style.display = "flex";
  }

  // Load dynamic content depending on section
  switch(section) {
    case "chatbots":
      loadChatbots();
      break;
    case "vendors":
      loadVendors();
      break;
    case "documents":
      const select = document.getElementById("documentChatbotSelect");
      if (select.options.length > 1) { // skip placeholder
        const firstChatbotId = select.options[1].value; // first actual chatbot
        loadDocuments(firstChatbotId);
      } else {
        loadDocuments();
      }
      break;
    case "embeddings":
      loadEmbeddings();
      break;
    case "llms":
      loadLLMs();
      break;
    case "adminApiTokens":
      break;
  }
}

function openChat(chatbotId, chatbotName) {
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.style.display = "flex";

  // Set active chatbot name in header
  document.getElementById("chatHeaderName").innerText = chatbotName;

  // Clear previous messages & input
  document.getElementById("chatMessages").innerHTML = "";
  document.getElementById("chatInput").value = "";

  window.currentChatbotId = chatbotId;
  window.currentChatbotName = chatbotName;
}

function closeChat() {
  document.getElementById("chatWindow").style.display = "none";
}

// ===================== SHOW CHATBOT DETAILS =====================
async function showChatbotDetails(chatbotId) {
  // Show the chatbot details section
  showSection("chatbotDetails");

  try {
    // Fetch chatbot details from API
    const res = await fetch(`${API_BASE}/chatbots/role-based-stats/${chatbotId}/${role}`, { headers });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to fetch chatbot details");
    }
    const data = await res.json();

    // Store active chatbot info globally
    window.activeChatbotId = chatbotId;
    window.activeChatbotName = data.name;
    window.currentChatbotId = chatbotId;

    // Build the details container HTML
    const container = document.getElementById("chatbotDetailsContainer");
    container.innerHTML = `
      <div class="card shadow-sm p-3 mb-3">
        <h3 class="card-title">${data.name}</h3>
        <p><strong>Vendor:</strong> ${data.vendor?.name || "N/A"}</p>
        <p><strong>Status:</strong>
          <span class="badge bg-${data.is_active ? "success" : "secondary"}">
            ${data.is_active ? "Active" : "Inactive"}
          </span>
        </p>
        <p><strong>Created At:</strong> ${new Date(data.created_at).toLocaleString()}</p>
        <p><strong>Description:</strong> ${data.description || "N/A"}</p>
        <p><strong>System Prompt:</strong></p>
        <div class="border p-2 mb-3">${data.system_prompt || "<em>N/A</em>"}</div>

        <!-- Widget Snippet Section -->
        <h5 class="mt-4">🔌 Widget</h5>
        <div class="border p-3 mb-3" style="background-color: #1e1e1e;">
          <p><strong class="text-light">Widget Embed Code:</strong></p>
          <div class="d-flex align-items-start gap-2">
            <pre class="p-2 rounded flex-grow-1" id="widgetCodeContainer" style="background-color: #1e1e1e; color: #ffffff; white-space: pre-wrap;"></pre>
            <button class="btn btn-sm btn-outline-light" id="copyWidgetBtn">Copy</button>
          </div>
          <small class="text-light">Click "Copy" to copy the snippet to clipboard</small>
        </div>


        <!-- Documents Section (last) -->
        <h5>📄 Documents</h5>
        <div id="chatbotDocumentsContainer">Loading documents...</div>

        <!-- Upload documents in details page -->
        <div class="mt-3">
          <label for="documentFilesDetail" class="form-label">Upload Documents</label>
          <input type="file" id="documentFilesDetail" class="form-control" multiple
            onchange="Array.from(this.files).forEach(f => {
              if(!selectedDetailFiles.some(x => x.name === f.name)) selectedDetailFiles.push(f);
              renderDetailSelectedFiles();
            })">
          <ul id="selectedFilesPreviewDetail" class="list-group mt-2 mb-2"></ul>
          <button class="btn btn-primary" onclick="uploadDocumentsForDetail(${chatbotId})">Upload</button>
        </div>

        <button class="btn btn-secondary mt-3" onclick="showSection('chatbots')">Back</button>
      </div>
    `;

    // Set chat bubble click to open chatbot
    document.getElementById("chatBubble").onclick = () => openChat(chatbotId, data.name);

    // Load documents for this chatbot
    loadChatbotDocuments(chatbotId);

    // Fetch latest active API token for this chatbot
    let widgetToken = "CREATE_TOKEN"; // fallback

    try {
      const tokenRes = await fetch(`${API_BASE}/api-keys/by-chatbot/${chatbotId}`, {
        headers
      });

      if (tokenRes.ok) {
        const tokens = await tokenRes.json();
        // Use the first active token
        const activeToken = tokens.find(t => t.status === "active");
        if (activeToken) widgetToken = activeToken.token_hash; // <-- real token
      }
    } catch (err) {
      console.error("Failed to fetch widget token:", err);
    }

    // Prepare the widget snippet as text (not executed)
    const widgetSnippet = `
      <script 
        src="https://seekers-beside-absent-computational.trycloudflare.com/static/widget.js" 
        data-chatbot-name="${data.name}" 
        data-chatbot-token="${widgetToken}">
      </script>
    `;

    // Show snippet in <pre>
    document.getElementById("widgetCodeContainer").textContent = widgetSnippet.trim();

    // Copy button functionality
    document.getElementById("copyWidgetBtn").onclick = () => {
      navigator.clipboard.writeText(widgetSnippet.trim())
        .then(() => alert("Widget snippet copied to clipboard!"))
        .catch(err => alert("Failed to copy snippet: " + err));
    };

  } catch (err) {
    console.error(err);
    alert("Failed to load chatbot details.");
  }
}



/* ===================== LOAD CHATBOT DOCUMENTS ===================== */
async function loadChatbotDocuments(chatbotId) {
  const docsContainer = document.getElementById("chatbotDocumentsContainer");

  try {
    const res = await fetch(`${API_BASE}/documents/chatbots_documents/${chatbotId}`, { headers });
    if (!res.ok) {
      docsContainer.innerHTML = `<p class="text-danger">No documents found.</p>`;
      return;
    }

    const documents = await res.json();

    if (!documents.length) {
      docsContainer.innerHTML = `<p class="text-muted">No documents available.</p>`;
      return;
    }

    docsContainer.innerHTML = `
      <ul class="list-group">
        ${documents.map(doc => `
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>${doc.title || "Unnamed Document"}</div>
            <div class="text-end">
              <span class="badge bg-${doc.status === "processing" ? "warning" : doc.status === "active" ? "success" : "secondary"} mb-1">
                ${doc.status}
              </span><br>
              <small class="text-muted">${doc.created_at ? new Date(doc.created_at).toLocaleString() : ""}</small>
            </div>
          </li>
        `).join("")}
      </ul>
    `;

  } catch (error) {
    docsContainer.innerHTML = `<p class="text-danger">Error loading documents.</p>`;
    console.error(error);
  }
}


/* ===================== SEND MESSAGE ===================== */
// Send Message
let sessionId = null; // store session_id for multi-turn conversation

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  const chatMessages = document.getElementById("chatMessages");

  // --- Display user message ---
  const userMsgDiv = document.createElement("div");
  userMsgDiv.classList.add("chat-message", "user");
  userMsgDiv.innerHTML = `${message}`;
  chatMessages.appendChild(userMsgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  input.value = "";
  input.disabled = true;

  try {
    // Build request body
    const body = { question: message };
    if (sessionId) body.session_id = sessionId;

    // Send request to multi-turn backend
    const res = await fetch(`${API_BASE}/chatbots/test/${currentChatbotId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Optional: only send token if logged in
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(body)
    });

    if (!res.ok) throw new Error("Failed to get response from chatbot");
    const data = await res.json();

    // --- Save session_id for next messages ---
    if (!sessionId && data.session_id) {
      sessionId = data.session_id;
    }
    // --- Display bot response ---
    const botMsgDiv = document.createElement("div");
    botMsgDiv.classList.add("chat-message", "bot");
    botMsgDiv.innerHTML = `${data.answer}`;
    chatMessages.appendChild(botMsgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

  } catch (err) {
    const errDiv = document.createElement("div");
    errDiv.classList.add("chat-message", "bot");
    errDiv.innerHTML = `Error: ${err.message}`;
    chatMessages.appendChild(errDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } finally {
    input.disabled = false;
    input.focus();
  }
}

// ===================== RENDER SELECTED FILES =====================
function renderDetailSelectedFiles() {
  const preview = document.getElementById("selectedFilesPreviewDetail");
  preview.innerHTML = "";

  selectedDetailFiles.forEach((file, index) => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center";
    li.textContent = file.name;

    const btn = document.createElement("button");
    btn.className = "btn btn-sm btn-danger";
    btn.textContent = "Remove";
    btn.addEventListener("click", () => {
      selectedDetailFiles.splice(index, 1);
      renderDetailSelectedFiles();
    });

    li.appendChild(btn);
    preview.appendChild(li);
  });
}

// ===================== UPLOAD DOCUMENTS FOR DETAIL =====================
async function uploadDocumentsForDetail(chatbotId) {
  if (!chatbotId) return alert("Invalid chatbot");
  if (selectedDetailFiles.length === 0) return alert("Select files to upload");

  const formData = new FormData();
  selectedDetailFiles.forEach(f => formData.append("files", f));

  try {
    const res = await fetch(`${API_BASE}/documents/chatbots/${chatbotId}/documents`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });

    if (!res.ok) {
      const err = await res.text();
      return alert("Upload failed: " + err);
    }

    alert("Upload successful");

    selectedDetailFiles = [];
    document.getElementById("documentFilesDetail").value = "";
    renderDetailSelectedFiles();

    loadChatbotDocuments(chatbotId); // refresh documents list

  } catch (error) {
    alert("Upload failed: " + error.message);
  }
}
