const API = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

function getPayload() {
  const token = getToken();
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch { return null; }
}


const profilesGrid = document.getElementById("profiles-grid");
if (profilesGrid) {
  const ROLE_COLORS = {
    rh:        "#3b82f6",
    technique: "#f97316",
    support:   "#10b981",
    wiki:      "#8b5cf6",
    admin:     "#ef4444",
  };

  async function loadProfiles() {
    const errorDiv = document.getElementById("profiles-error");
    try {
      const r = await fetch(`${API}/profiles`);
      if (!r.ok) throw new Error("Erreur serveur");
      const data = await r.json();
      renderProfiles(data.profiles);
    } catch (e) {
      profilesGrid.innerHTML = "";
      errorDiv.textContent = "Impossible de charger les profils. Le serveur est-il démarré ?";
      errorDiv.style.display = "block";
    }
  }

  function renderProfiles(profiles) {
    profilesGrid.innerHTML = "";
    profiles.forEach((p) => {
      const card = document.createElement("button");
      card.className = "profile-card";
      const color = ROLE_COLORS[p.role] || "#6b7280";
      card.innerHTML = `
        <div class="profile-avatar" style="background:${color}">${p.username[0].toUpperCase()}</div>
        <span class="profile-username">${p.username}</span>
        <span class="profile-role" style="color:${color}">${p.role}</span>
      `;
      card.addEventListener("click", () => selectProfile(p.username));
      profilesGrid.appendChild(card);
    });
  }

  async function selectProfile(username) {
    const errorDiv = document.getElementById("profiles-error");
    const r = await fetch(`${API}/select-profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    if (r.ok) {
      const data = await r.json();
      localStorage.setItem("token", data.access_token);
      // Clear conversations when switching profile
      localStorage.removeItem("conversations");
      window.location.href = "chat.html";
    } else {
      errorDiv.textContent = "Erreur lors de la sélection du profil.";
      errorDiv.style.display = "block";
    }
  }

  loadProfiles();
}


const messagesDiv = document.getElementById("messages");
if (messagesDiv) {
  const token = getToken();
  if (!token) window.location.href = "index.html";

  let activeConvId = null;

  const welcomeDiv = document.getElementById("welcome");

  function showWelcome() {
    if (welcomeDiv) welcomeDiv.classList.remove("hidden");
    messagesDiv.style.display = "none";
  }

  function hideWelcome() {
    if (welcomeDiv) welcomeDiv.classList.add("hidden");
    messagesDiv.style.display = "";
  }

  // Show current profile in sidebar footer
  const profileEl = document.getElementById("current-profile");
  if (profileEl) {
    const payload = getPayload();
    if (payload) {
      const ROLE_COLORS = {
        rh: "#3b82f6", technique: "#f97316",
        support: "#10b981", wiki: "#8b5cf6", admin: "#ef4444",
      };
      const color = ROLE_COLORS[payload.role] || "#6b7280";
      profileEl.innerHTML = `
        <div class="profile-mini-avatar" style="background:${color}">${payload.username[0].toUpperCase()}</div>
        <div class="profile-mini-info">
          <span class="profile-mini-name">${payload.username}</span>
          <span class="profile-mini-role" style="color:${color}">${payload.role}</span>
        </div>
      `;
    }
  }

  document.getElementById("new-conv").addEventListener("click", createConversation);
  document.getElementById("send").addEventListener("click", sendMessage);
  document.getElementById("question").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const input = document.getElementById("question");
      input.value = chip.dataset.q || chip.textContent;
      input.focus();
    });
  });

  // Conversations list in localStorage: [{id, title, date}]
  function getConversations() {
    try { return JSON.parse(localStorage.getItem("conversations") || "[]"); }
    catch { return []; }
  }

  function saveConversations(list) {
    try { localStorage.setItem("conversations", JSON.stringify(list)); } catch {}
  }

  function renderSidebar() {
    const list = document.getElementById("conv-list");
    const convs = getConversations();
    list.innerHTML = "";
    convs.forEach((conv) => {
      const item = document.createElement("div");
      item.className = "conv-item" + (conv.id === activeConvId ? " active" : "");

      const info = document.createElement("div");
      info.className = "conv-info";
      info.innerHTML = `<span class="conv-title">${conv.title}</span><span class="conv-date">${conv.date}</span>`;
      info.addEventListener("click", () => switchConversation(conv.id));

      const del = document.createElement("button");
      del.className = "conv-delete";
      del.title = "Supprimer";
      del.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
      del.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteConversation(conv.id);
      });

      item.appendChild(info);
      item.appendChild(del);
      list.appendChild(item);
    });
  }

  async function createConversation() {
    const r = await fetch(`${API}/conversation`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!r.ok) return;
    const data = await r.json();

    const conv = {
      id: data.conversation_id,
      title: "Nouvelle conversation",
      date: new Date().toLocaleDateString("fr-FR"),
    };

    const convs = getConversations();
    convs.unshift(conv);
    saveConversations(convs);

    activeConvId = conv.id;
    messagesDiv.innerHTML = "";
    showWelcome();
    renderSidebar();
  }

  async function deleteConversation(convId) {
    await fetch(`${API}/conversation/${convId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    let convs = getConversations().filter((c) => c.id !== convId);
    saveConversations(convs);

    if (activeConvId === convId) {
      messagesDiv.innerHTML = "";
      if (convs.length > 0) {
        await switchConversation(convs[0].id);
      } else {
        await createConversation();
      }
    } else {
      renderSidebar();
    }
  }

  async function switchConversation(convId) {
    activeConvId = convId;
    messagesDiv.innerHTML = "";
    renderSidebar();

    const r = await fetch(`${API}/history/${convId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!r.ok) return;
    const data = await r.json();

    if (data.messages.length === 0) {
      showWelcome();
    } else {
      hideWelcome();
      data.messages.forEach((msg) => addMessage(msg.content, msg.role));
    }
  }

  function addMessage(text, role) {
    const row = document.createElement("div");
    row.className = `msg-row ${role}`;

    if (role === "assistant") {
      const avatar = document.createElement("div");
      avatar.className = "msg-avatar";
      avatar.textContent = "S";
      row.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.className = "message";
    bubble.textContent = text;
    row.appendChild(bubble);

    messagesDiv.appendChild(row);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  async function sendMessage() {
    const input = document.getElementById("question");
    const question = input.value.trim();
    if (!question || !activeConvId) return;

    input.value = "";
    hideWelcome();
    addMessage(question, "user");

    const convs = getConversations();
    const conv = convs.find((c) => c.id === activeConvId);
    if (conv && conv.title === "Nouvelle conversation") {
      conv.title = question.length > 32 ? question.slice(0, 32) + "…" : question;
      saveConversations(convs);
      renderSidebar();
    }

    const loadingRow = document.createElement("div");
    loadingRow.className = "msg-row assistant";
    const loadingAvatar = document.createElement("div");
    loadingAvatar.className = "msg-avatar";
    loadingAvatar.textContent = "S";
    const loadingBubble = document.createElement("div");
    loadingBubble.className = "message loading-dots";
    loadingBubble.innerHTML = "<span></span><span></span><span></span>";
    loadingRow.appendChild(loadingAvatar);
    loadingRow.appendChild(loadingBubble);
    messagesDiv.appendChild(loadingRow);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    const response = await fetch(`${API}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ question, conversation_id: activeConvId }),
    });

    loadingRow.remove();

    if (response.ok) {
      const data = await response.json();
      addMessage(data.response, "assistant");
    } else {
      addMessage("Erreur lors de la requête.", "assistant");
    }
  }

  // Init
  const convs = getConversations();
  if (convs.length === 0) {
    createConversation();
  } else {
    switchConversation(convs[0].id);
  }
}


const indexBtn = document.getElementById("index-btn");
if (indexBtn) {
  const token = getToken();
  if (!token) window.location.href = "index.html";

  document.getElementById("logout").addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "index.html";
  });

  indexBtn.addEventListener("click", async () => {
    const content  = document.getElementById("content").value.trim();
    const source   = document.getElementById("source").value.trim();
    const acl_role = document.getElementById("acl_role").value;
    const status   = document.getElementById("status");

    if (!content || !source) {
      status.textContent = "Contenu et source sont obligatoires.";
      status.className = "error";
      return;
    }

    const response = await fetch(`${API}/index`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content, source, acl_role }),
    });

    if (response.ok) {
      status.textContent = "Document indexé avec succès.";
      status.className = "success";
      document.getElementById("content").value = "";
      document.getElementById("source").value = "";
    } else {
      status.textContent = "Erreur : accès refusé ou problème serveur.";
      status.className = "error";
    }
  });
}
