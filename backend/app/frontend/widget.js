// const API_BASE = "http://127.0.0.1:9000"; 
const API_BASE = "https://seekers-beside-absent-computational.trycloudflare.com"
// Get chatbot ID from the script tag
const scriptTag = document.currentScript;
const selectedChatbotName = scriptTag.getAttribute("data-chatbot-name") || "Chatbot";
const selectedChatbottoken = scriptTag.getAttribute("data-chatbot-token");

// Default chatbot name (optional until fetched)
let chatSessionId = null;
let userApiKey = null;

// ------------------ Load Chatbots ------------------
async function loadChatbots() {
    try {
        const res = await fetch(`${API_BASE}/users/vendor_chatbots`, {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) throw new Error("Failed to load chatbots");

        const chatbots = await res.json();

        if (!Array.isArray(chatbots)) {
            console.error("Invalid chatbots response: ", chatbots);
            throw new Error("Invalid chatbots response");
        }

        const listContainer = document.getElementById("chatbotList");
        listContainer.innerHTML = "";

        chatbots.forEach(cb => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `
                <span>${cb.name}</span>
                <button class="btn btn-sm btn-primary">Select</button>
            `;
            li.querySelector("button").addEventListener("click", () => {
                selectedChatbotId = cb.id;
                selectedChatbotName = cb.name;
                chatSessionId = null;
                userApiKey = null;

                updateChatHeader();
            });
            listContainer.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        alert("Failed to load chatbots");
    }
}

// ------------------ Chat Header Update ------------------
function updateChatHeader() {
    chatHeader.innerHTML = `
        ${selectedChatbotName}  <!-- <-- show chatbot name in window header -->
        <button class="closeChat" onclick="chatWindow.style.display='none'">✖</button>
    `;
}

document.addEventListener("DOMContentLoaded", () => {

    // --- Inject UI FIRST ---
    const widgetUI = `
        <div id="chatBubble" style="
                position:fixed; bottom:20px; right:20px; width:60px; height:60px;
                background:#0d6efd; color:white; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                cursor:pointer; font-size:26px; z-index:999999;
            ">💬</div>

        <div id="chatWindow" style="
                display:none; position:fixed; bottom:90px; right:20px;
                width:350px; height:420px; background:white; border-radius:12px;
                box-shadow:0 4px 18px rgba(0,0,0,0.25); z-index:999999;
                flex-direction:column; overflow:hidden;
            ">
            <div id="chatHeader" style="
                    background:#0d6efd; color:white; padding:10px;
                    display:flex; justify-content:space-between; align-items:center;
                ">${selectedChatbotName} <button id="chatCloseBtn">✖</button></div>

            <div id="chatMessages" style="flex:1; padding:10px; overflow-y:auto; background:#f7f7f7; display:flex; flex-direction: column;"></div>

            <div style="display:flex; gap:5px; padding:10px;">
                <input id="chatInput" style="flex:1; padding:8px; border:1px solid #ccc; border-radius:6px;" placeholder="Type...">
                <button id="sendBtn" style="padding:8px 12px; background:#0d6efd; color:white; border:none; border-radius:6px;">Send</button>
            </div>
        </div>`;

    document.body.insertAdjacentHTML("beforeend", widgetUI);

    // --- NOW select elements AFTER they exist ---
    const chatBubble = document.getElementById("chatBubble");
    const chatWindow = document.getElementById("chatWindow");
    const chatHeader = document.getElementById("chatHeader");
    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");
    const closeBtn = document.getElementById("chatCloseBtn");

    // --- Only now attach listeners ---
    if (chatBubble) {
        chatBubble.addEventListener("click", () => {
            chatWindow.style.display = 
                chatWindow.style.display === "flex" ? "none" : "flex";

            chatWindow.style.flexDirection = "column";
            chatInput.focus();
        });
    }

    closeBtn.addEventListener("click", () => {
        chatWindow.style.display = "none";
    });
    sendBtn.addEventListener("click", sendMessage);

    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

});


let sessionId = null; 

// ------------------ Send Message ------------------
async function sendMessage() {
    if (!selectedChatbottoken) {
        alert("Chatbot token missing from widget script tag!");
        return;
    }

    const message = chatInput.value.trim();
    if (!message) return;

    const userMsgDiv = document.createElement("div");
    userMsgDiv.classList.add("message", "user");
    userMsgDiv.style.alignSelf = "flex-end";            
    userMsgDiv.style.background = "#0d6efd";           
    userMsgDiv.style.color = "white";                  
    userMsgDiv.style.padding = "8px 12px";
    userMsgDiv.style.borderRadius = "20px 0 20px 20px"; 
    userMsgDiv.style.marginBottom = "8px";
    userMsgDiv.style.maxWidth = "80%";
    userMsgDiv.innerHTML = `${message}`;
    userMsgDiv.setAttribute("data-time", new Date().toLocaleTimeString());

    chatMessages.appendChild(userMsgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatInput.value = "";
    chatInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/chatbots/${selectedChatbottoken}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                question: message,
                session_id: sessionId  // send existing sessionId or null
            })
        });

        if (!res.ok) throw new Error("Chat request failed");

        const data = await res.json();

        // Save sessionId from backend response if not already set
        if (!sessionId && data.session_id) {
            sessionId = data.session_id;
        }

        const botMsgDiv = document.createElement("div");
        botMsgDiv.classList.add("message", "chatbot");
        botMsgDiv.style.alignSelf = "flex-start";        
        botMsgDiv.style.background = "#e9ecef";          
        botMsgDiv.style.color = "#212529";               
        botMsgDiv.style.padding = "8px 12px";
        botMsgDiv.style.display = "flex"; 
        botMsgDiv.style.borderRadius = "0 20px 20px 20px"; 
        botMsgDiv.style.marginBottom = "8px";
        botMsgDiv.style.flexDirection= "column";
        botMsgDiv.style.maxWidth = "80%";
        botMsgDiv.innerHTML = `${data.answer}`;
        botMsgDiv.setAttribute("data-time", new Date().toLocaleTimeString());

        chatMessages.appendChild(botMsgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (err) {
        console.error(err);
        alert("Error sending message");
    } finally {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}


