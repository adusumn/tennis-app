// Report a result page: pick a match you've played (an accepted request whose time has passed),
// say who won and the score, and send it to the opponent to confirm.

const form = document.getElementById("report-form");
const matchSelect = document.getElementById("report-match");
const resultSelect = document.getElementById("report-result");
const scoreInput = document.getElementById("report-score");

let me = null;
let played = new Map(); // request id -> request record

function requestOpponent(r) {
  return r.user === me.username ? r.accepted_by : r.user;
}

function matchOpponent(m) {
  return m.winner === me.username ? m.loser : m.winner;
}

async function loadPlayedMatches() {
  const [mine, matches] = await Promise.all([
    api("GET", "/api/requests/mine"),
    api("GET", "/api/matches"),
  ]);

  // count the results already sent (pending or confirmed) per opponent and day; a declined one can be
  // reported again, e.g. with the score corrected. Matches don't store which request they came from,
  // so if 1 result exists and 3 matches were played against that person that day, the earliest one
  // counts as reported and the other 2 still show up.
  const reportedCount = new Map();
  for (const [id, m] of matches) {
    if (m.status === "declined") continue;
    const key = matchOpponent(m) + "|" + m.date;
    reportedCount.set(key, (reportedCount.get(key) || 0) + 1);
  }

  played = new Map();
  // mine is sorted by date and time, so the earliest match of the day is skipped first
  for (const [id, r] of mine) {
    if (r.status !== "accepted" || isUpcoming(r)) continue;
    const key = requestOpponent(r) + "|" + r.date;
    if (reportedCount.get(key) > 0) {
      reportedCount.set(key, reportedCount.get(key) - 1);
      continue;
    }
    played.set(id, r);
  }

  matchSelect.replaceChildren();
  const placeholder = el("option", "", "Select a match");
  placeholder.value = "";
  placeholder.disabled = true;
  placeholder.selected = true;
  matchSelect.appendChild(placeholder);
  // newest first, so the match they just played is at the top
  for (const [id, r] of [...played].reverse()) {
    const option = el("option", "", requestOpponent(r) + " · " + formatWhen(r.date, r.time));
    option.value = id;
    matchSelect.appendChild(option);
  }

  document.getElementById("report-card").hidden = played.size === 0;
  document.getElementById("report-empty").hidden = played.size !== 0;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();

  const r = played.get(Number(matchSelect.value));
  const opponent = requestOpponent(r);
  const won = resultSelect.value === "won";

  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await api("POST", "/api/matches", {
      winner: won ? me.username : opponent,
      loser: won ? opponent : me.username,
      date: r.date,
      score: scoreInput.value.trim(),
    });
    showNotice("Sent to " + opponent + " to confirm. Both ratings update once they do.");
    form.reset();
    await loadPlayedMatches();
  } catch (err) {
    showNotice("Couldn't send that result. Check the score and try again.", true);
  }
  button.disabled = false;
});

startPage(async () => {
  me = await loadMe();
  await loadPlayedMatches();
});
