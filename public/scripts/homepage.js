// Homepage: greeting, quick stats, pending match results to confirm, and the user's upcoming (accepted) matches.

let me = null;

// "2026-11-01" -> "Sun, Nov 1"
function formatDay(date) {
  const [y, m, d] = date.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

// Pending results the user is part of. The opponent of whoever reported it gets Confirm/Decline;
// the reporter just sees that it's waiting.
async function loadMatchesToConfirm() {
  let matches;
  try {
    matches = await api("GET", "/api/matches");
  } catch (err) {
    renderList("confirm-list", [], "Couldn't load your matches.", null);
    return;
  }
  const pending = matches.filter(([id, m]) => m.status === "pending");

  renderList("confirm-list", pending, "Nothing to confirm right now.", (id, m) => {
    const won = m.winner === me.username;
    const opponent = won ? m.loser : m.winner;
    const title = (won ? "You beat " : "You lost to ") + opponent + " · " + m.score;

    if (m.reported_by === me.username) {
      return listItem(title, formatDay(m.date) + " · Waiting for " + opponent + " to confirm");
    }

    const actions = el("div", "item-actions");
    actions.appendChild(actionButton("Confirm", "", async () => {
      try {
        await api("POST", "/api/matches/" + id + "/confirm");
        showNotice("Result confirmed. Your rating has been updated.");
        const updated = await loadMe();
        document.getElementById("stat-rating").textContent = Number(updated.rating).toFixed(2);
      } catch (err) {
        showNotice("Couldn't confirm that match.", true);
      }
      await loadMatchesToConfirm();
    }));
    actions.appendChild(actionButton("Decline", "btn-outline", async () => {
      try {
        await api("POST", "/api/matches/" + id + "/decline");
        showNotice("Result declined. No ratings were changed.");
      } catch (err) {
        showNotice("Couldn't decline that match.", true);
      }
      await loadMatchesToConfirm();
    }));
    return listItem(title, formatDay(m.date) + " · Reported by " + opponent, actions);
  });
}

startPage(async () => {
  me = await loadMe();
  loadMatchesToConfirm();
  const firstName = me.username.split("@")[0];
  document.getElementById("greeting").textContent = "Welcome back, " + firstName + ".";
  document.getElementById("stat-rating").textContent = Number(me.rating).toFixed(2);

  const [open, mine] = await Promise.all([
    api("GET", "/api/requests/open"),
    api("GET", "/api/requests/mine"),
  ]);

  // Scheduled: accepted requests that haven't happened yet
  const scheduled = mine.filter(([id, r]) => r.status === "accepted" && isUpcoming(r));
  document.getElementById("stat-upcoming").textContent = scheduled.length;
  document.getElementById("stat-open").textContent = open.length;

  renderList("schedule-list", scheduled, "No matches scheduled yet. Accept a request or post your own.", (id, r) => {
    const opponent = r.user === me.username ? r.accepted_by : r.user;
    return listItem(formatWhen(r.date, r.time), "vs " + opponent);
  });
});
