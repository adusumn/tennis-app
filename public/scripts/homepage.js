// Homepage: greeting, quick stats, and the user's upcoming (accepted) matches.

startPage(async () => {
  const me = await loadMe();
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
