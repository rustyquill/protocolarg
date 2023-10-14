// prepare identification form
const form = document.querySelector("#identification-form");

form.addEventListener("submit", function (event) {
  if (!form.checkValidity()) {
    event.preventDefault();

  }
  form.classList.add('was-validated');
});
