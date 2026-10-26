// Request a match page: post a date and time, then go to the Match requests page.

const dateInput = document.getElementById("request-date");
const timeInput = document.getElementById("request-time");

// don't let people pick a day in the past
dateInput.min = todayString();

document.getElementById("request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();

  // a time earlier today is also in the past
  if (!isUpcoming({ date: dateInput.value, time: timeInput.value })) {
    showNotice("That time has already passed. Pick a later time.", true);
    return;
  }

  const button = event.target.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await api("POST", "/api/requests", { date: dateInput.value, time: timeInput.value });
    window.location.href = "requests.html?posted=1";
  } catch (err) {
    button.disabled = false;
    if (err.message !== "not signed in") {
      showNotice("Couldn't post your request. Please try again.", true);
    }
  }
});
startPage(loadMe);
