// Homepage: tabs for scheduled matches, match requests, posting a request, and the profile.
//
// Expects these routes in httpserver.py (all return JSON):
//   GET  /api/me                      -> {"username", "gender", "age", "rating"}
//   PUT  /api/me                      <- {"gender", "age"}
//   GET  /api/requests/open           -> [[request_id, record], ...]
//   GET  /api/requests/mine           -> [[request_id, record], ...]
//   POST /api/requests                <- {"date": "YYYY-MM-DD", "time": "HH:MM"}
//   POST /api/requests/<id>/accept
//   POST /api/requests/<id>/cancel
// A request record looks like {"user", "date", "time", "status", "accepted_by"}.

const TABS = ["schedule", "requests", "new", "profile"];
const GENDER_LABELS = {
  male: "Male",
  female: "Female",
  other: "Other",
  prefer_not: "Prefer not to say",
};

let me = null;

// ---------- Talking to the server ----------

async function api(method, url, body) {
  const options = { method: method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  if (response.status === 401) {
    // not signed in (or the session expired)
    window.location.href = "/signin.html";
    throw new Error("not signed in");
  }
  if (!response.ok) {
    throw new Error("request failed: " + response.status);
  }
  return response.json();
}

// ---------- Small helpers ----------

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showNotice(message, isError) {
  const notice = document.getElementById("notice");
  notice.textContent = message;
  notice.classList.toggle("notice-error", Boolean(isError));
  notice.hidden = false;
}

function hideNotice() {
  document.getElementById("notice").hidden = true;
}

// "2026-11-01" + "18:30" -> "Sun, Nov 1 · 6:30 PM"
function formatWhen(date, time) {
  const [y, m, d] = date.split("-").map(Number);
  const [hh, mm] = time.split(":").map(Number);
  const when = new Date(y, m - 1, d, hh, mm);
  const day = when.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
  const clock = when.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  return day + " · " + clock;
}

function isUpcoming(record) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const today = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
  const currentTime = pad(now.getHours()) + ":" + pad(now.getMinutes());
  if (record.date !== today) return record.date > today;
  return record.time >= currentTime;
}

function renderList(listId, rows, emptyText, buildItem) {
  const list = document.getElementById(listId);
  list.replaceChildren();
  if (rows.length === 0) {
    list.appendChild(el("li", "empty", emptyText));
    return;
  }
  for (const [id, record] of rows) {
    list.appendChild(buildItem(id, record));
  }
}

function listItem(title, meta, button) {
  const item = el("li", "list-item");
  const main = el("div", "item-main");
  main.appendChild(el("span", "item-title", title));
  main.appendChild(el("span", "item-meta", meta));
  item.appendChild(main);
  if (button) item.appendChild(button);
  return item;
}

function actionButton(label, className, onClick) {
  const button = el("button", "btn btn-small " + className, label);
  button.type = "button";
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      await onClick();
    } catch (err) {
      button.disabled = false;
    }
  });
  return button;
}

// ---------- Tabs ----------

function showTab(name) {
  if (!TABS.includes(name)) name = "schedule";
  for (const tab of TABS) {
    const selected = tab === name;
    document.getElementById("tab-" + tab).setAttribute("aria-selected", String(selected));
    document.getElementById("panel-" + tab).hidden = !selected;
  }
  if (window.location.hash !== "#" + name) {
    history.replaceState(null, "", "#" + name);
  }
}

// ---------- Loading each section ----------

async function loadProfile() {
  me = await api("GET", "/api/me");
  const firstName = me.username.split("@")[0];
  document.getElementById("greeting").textContent = "Welcome back, " + firstName + ".";
  document.getElementById("header-user").textContent = me.username;
  document.getElementById("profile-username").textContent = me.username;
  document.getElementById("profile-rating").textContent = Number(me.rating).toFixed(2);
  document.getElementById("profile-gender").textContent = GENDER_LABELS[me.gender] || me.gender;
  document.getElementById("profile-age").textContent = me.age;
  document.getElementById("edit-gender").value = me.gender;
  document.getElementById("edit-age").value = me.age;
}

async function loadRequests() {
  const [open, mine] = await Promise.all([
    api("GET", "/api/requests/open"),
    api("GET", "/api/requests/mine"),
  ]);

  // Scheduled: accepted requests that haven't happened yet
  const scheduled = mine.filter(([id, r]) => r.status === "accepted" && isUpcoming(r));
  renderList("schedule-list", scheduled, "No matches scheduled yet. Accept a request or post your own.", (id, r) => {
    const opponent = r.user === me.username ? r.accepted_by : r.user;
    return listItem(formatWhen(r.date, r.time), "vs " + opponent);
  });

  renderList("open-list", open, "No open requests right now. Check back later or post your own.", (id, r) => {
    const button = actionButton("Accept", "", async () => {
      try {
        await api("POST", "/api/requests/" + id + "/accept");
        showNotice("Match with " + r.user + " added to your schedule.");
      } catch (err) {
        showNotice("Couldn't accept that request. Someone may have taken it already.", true);
      }
      await loadRequests();
    });
    return listItem(formatWhen(r.date, r.time), "Posted by " + r.user, button);
  });

  const myOpen = mine.filter(([id, r]) => r.status === "open" && r.user === me.username && isUpcoming(r));
  renderList("mine-list", myOpen, "You have no open requests.", (id, r) => {
    const button = actionButton("Cancel", "btn-outline", async () => {
      try {
        await api("POST", "/api/requests/" + id + "/cancel");
        showNotice("Request cancelled.");
      } catch (err) {
        showNotice("Couldn't cancel that request.", true);
      }
      await loadRequests();
    });
    return listItem(formatWhen(r.date, r.time), "Waiting for a player", button);
  });
}

// ---------- Forms ----------

document.getElementById("request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();
  const form = event.target;
  try {
    await api("POST", "/api/requests", { date: form.date.value, time: form.time.value });
    form.reset();
    showNotice("Request posted. Other players can now see it.");
    await loadRequests();
    showTab("requests");
  } catch (err) {
    showNotice("Couldn't post your request. Please try again.", true);
  }
});

document.getElementById("profile-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();
  const form = event.target;
  try {
    await api("PUT", "/api/me", { gender: form.gender.value, age: Number(form.age.value) });
    await loadProfile();
    showNotice("Profile updated.");
  } catch (err) {
    showNotice("Couldn't save your changes. Please try again.", true);
  }
});

// ---------- Start ----------

for (const tab of TABS) {
  document.getElementById("tab-" + tab).addEventListener("click", () => {
    hideNotice();
    showTab(tab);
  });
}

// don't let people request a match in the past
const now = new Date();
document.getElementById("request-date").min =
  now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");

showTab(window.location.hash.slice(1));

(async () => {
  try {
    await loadProfile();
    await loadRequests();
  } catch (err) {
    if (err.message !== "not signed in") {
      showNotice("Couldn't load your data. Is the server running?", true);
    }
  }
})();
