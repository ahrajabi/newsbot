var username;
var password;

function save_options() {
  username = document.getElementById('username-form').value;
  password = document.getElementById('password-form').value;
  chrome.storage.local.set({
    username: username,
    password: password,
    all_date: []
  }, function() {
    // Update status to let user know options were saved.
    var status = document.getElementById('status');
    status.textContent = username + ' ذخیره شده است.';
  });
}

function restore_options() {
  // Use default value color = 'red' and likesColor = true.
  chrome.storage.local.get({
    username: '',
    password: ''
  }, function(items) {
      username = items.username;
      password = items.password;
    document.getElementById('username-form').value = items.username;
    document.getElementById('password-form').value = items.password;
  });
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('submit').addEventListener('click',
    save_options);