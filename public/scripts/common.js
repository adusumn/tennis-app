// Shared helpers for every signed-in page (homepage, match requests, request a match, profile).
//
// Routes these pages call in httpserver.py (all return JSON):
//   GET  /api/me                      -> {"username", "gender", "age", "rating"}
//   PUT  /api/me                      <- {"gender", "age"}
//   PUT  /api/me/password             <- {"old_password", "new_password"}
//   GET  /api/requests/open           -> [[request_id, record], ...]
//   GET  /api/requests/mine           -> [[request_id, record], ...]
//   POST /api/requests                <- {"date": "YYYY-MM-DD", "time": "HH:MM"}
//   POST /api/requests/<id>/accept
//   POST /api/requests/<id>/cancel
//   GET  /api/matches                 -> [[match_id, record], ...]
//   POST /api/matches                 <- {"winner", "loser", "date", "score"}
//   POST /api/matches/<id>/confirm
//   POST /api/matches/<id>/decline
// A request record looks like {"user", "date", "time", "status", "accepted_by"}.
// A match record looks like {"winner", "loser", "date", "score", "status", "reported_by"}.

const GENDER_LABELS = {
  male: "Male",
  female: "Female",
  other: "Other",
  prefer_not: "Prefer not to say",
};

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
    throw new Error("Not signed in");
  }
  if (!response.ok) {
    throw new Error("Request failed: " + response.status);
  }
  return response.json();
}

// Loads the signed-in user and puts their email in the header. Every page calls this first.
async function loadMe() {
  const me = await api("GET", "/api/me");
  document.getElementById("header-user").textContent = me.username;
  return me;
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

function pad(n) {
  return String(n).padStart(2, "0");
}

// today as "YYYY-MM-DD" (local time)
function todayString() {
  const now = new Date();
  return now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
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
  const today = todayString();
  const currentTime = pad(now.getHours()) + ":" + pad(now.getMinutes());
  if (record.date !== today) return record.date > today;
  return record.time >= currentTime;
}

// rows are [request_id, record] pairs; buildItem(id, record) returns an <li>
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

// Runs a page's start-up function and shows a message if the server can't be reached.
async function startPage(start) {
  try {
    await start();
  } catch (err) {
    if (err.message !== "not signed in") {
      showNotice("Couldn't load your data. Is the server running?", true);
    }
  }
}
