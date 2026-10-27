// Sign-in and sign-up pages: httpserver.py redirects back with ?error=<code> when something
// goes wrong; show the matching message above the form. Also shows a note after an account is deleted.

const AUTH_ERRORS = {
  wrong: "Wrong email or password. Please try again.",
  taken: "An account with that email already exists. Sign in instead.",
  mismatch: "Your passwords don't match.",
  invalid: "Some of your details weren't valid. Check your age (5-120) and rating (1.0-7.0).",
};

const authParams = new URLSearchParams(window.location.search);
const authError = AUTH_ERRORS[authParams.get("error")];
const authNotice = document.getElementById("notice");
if (authError) {
  authNotice.textContent = authError;
  authNotice.hidden = false;
} else if (authParams.get("deleted") === "1") {
  // profile.js sends people here after they delete their account; this one isn't an error
  authNotice.textContent = "Your account has been deleted.";
  authNotice.classList.remove("notice-error");
  authNotice.hidden = false;
}
