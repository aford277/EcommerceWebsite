function togglePasswordVisibility() {
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    const toggleCheckbox = document.getElementById('show_password');
    const type = toggleCheckbox.checked ? 'text' : 'password';
    passwordField.type = type;
    confirmPasswordField.type = type;
}