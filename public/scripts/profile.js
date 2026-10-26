// Profile page: shows the locked rating, edits gender and age, and changes the password.
// The rating is display-only here; there is no way to send a new rating from this page.

function fillProfile(me) {
  document.getElementById("profile-username").textContent = me.username;
  document.getElementById("profile-rating").textContent = Number(me.rating).toFixed(2);
  document.getElementById("edit-gender").value = me.gender;
  document.getElementById("edit-age").value = me.age;
}

document.getElementById("details-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();
  const form = event.target;
  try {
    // only gender and age are sent
    await api("PUT", "/api/me", { gender: form.gender.value, age: Number(form.age.value) });
    fillProfile(await loadMe());
    showNotice("Details saved.");
  } catch (err) {
    if (err.message !== "not signed in") {
      showNotice("Couldn't save your details. Please try again.", true);
    }
  }
});

document.getElementById("password-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  hideNotice();
  const form = event.target;
  if (form.new_password.value !== form.confirm_password.value) {
    showNotice("The new passwords don't match.", true);
    return;
  }
  try {
    await api("PUT", "/api/me/password", {
      old_password: form.old_password.value,
      new_password: form.new_password.value,
    });
    form.reset();
    showNotice("Password changed.");
  } catch (err) {
    if (err.message !== "not signed in") {
      showNotice("Couldn't change your password. Check that your current password is right.", true);
    }
  }
});

startPage(async () => {
  fillProfile(await loadMe());
});
