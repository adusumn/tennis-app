// Sign-up page: before the form is sent, ask the user to confirm their rating,
// because it can't be changed after the account is created.

const form = document.querySelector('form[action="/signup"]');
const dialog = document.getElementById("confirm-rating");
const ratingInput = document.getElementById("rating");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");

// tell the browser the passwords don't match so it shows the message before submitting
function checkPasswordsMatch() {
  if (confirmPassword.value && confirmPassword.value !== password.value) {
    confirmPassword.setCustomValidity("Passwords don't match.");
  } else {
    confirmPassword.setCustomValidity("");
  }
}
password.addEventListener("input", checkPasswordsMatch);
confirmPassword.addEventListener("input", checkPasswordsMatch);

// the submit event only fires after the browser's own checks (required, min/max, pattern) pass
form.addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("confirm-rating-value").textContent = Number(ratingInput.value).toFixed(1);
  dialog.showModal();
});

document.getElementById("confirm-rating-back").addEventListener("click", () => {
  dialog.close();
  ratingInput.focus();
});

document.getElementById("confirm-rating-yes").addEventListener("click", () => {
  dialog.close();
  // form.submit() sends the form without firing the submit event again
  form.submit();
});
