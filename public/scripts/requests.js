// Match requests page: other players' open requests (accept) and the user's own open requests (cancel).

let me = null;

async function loadRequests() {
  const [open, mine] = await Promise.all([
    api("GET", "/api/requests/open"),
    api("GET", "/api/requests/mine"),
  ]);

  renderList("open-list", open, "No open requests right now. Check back later or post your own.", (id, r) => {
    const button = actionButton("Accept", "", async () => {
      try {
        await api("POST", "/api/requests/" + id + "/accept");
        showNotice("Match with " + r.user + " added to your schedule. You can see it on your homepage.");
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

startPage(async () => {
  me = await loadMe();
  if (new URLSearchParams(window.location.search).get("posted") === "1") {
    showNotice("Request posted. Other players can now see it.");
  }
  await loadRequests();
});
