const authModal = document.getElementById('authModal');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const authTitle = document.getElementById('authModalTitle');
const authTabs = document.querySelectorAll('.auth-tab');

function openAuthModal(tab = 'login') {
    authModal.classList.add('active');
    switchAuthTab(tab);
}

function closeAuthModal() {
    authModal.classList.remove('active');
    clearErrors(loginForm);
    clearErrors(signupForm);
}

function switchAuthTab(tab) {
    // Update Tabs
    authTabs.forEach(t => t.classList.remove('active'));
    
    // Update Forms
    loginForm.classList.remove('active');
    signupForm.classList.remove('active');

    if (tab === 'login') {
        authTabs[0].classList.add('active');
        loginForm.classList.add('active');
        authTitle.innerText = 'Welcome Back';
    } else {
        authTabs[1].classList.add('active');
        signupForm.classList.add('active');
        authTitle.innerText = 'Join the Club';
    }
}

// Validation Functions
function validateMoodleId(id) {
    // Simple alphanumeric check, 8-12 chars
    const regex = /^[a-zA-Z0-9]{8,12}$/;
    return regex.test(id);
}

function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function showError(inputElement, show = true) {
    const group = inputElement.closest('.form-group');
    if (show) {
        group.classList.add('error');
        // Reset animation
        const errorMsg = group.querySelector('.input-error');
        errorMsg.style.animation = 'none';
        errorMsg.offsetHeight; /* trigger reflow */
        errorMsg.style.animation = 'shake 0.4s ease';
    } else {
        group.classList.remove('error');
    }
}

function clearErrors(form) {
    const groups = form.querySelectorAll('.form-group');
    groups.forEach(g => g.classList.remove('error'));
}

// Handlers
function handleLogin(e) {
    e.preventDefault();
    clearErrors(loginForm);
    
    const moodleId = document.getElementById('loginMoodleId');
    const password = document.getElementById('loginPassword');
    let isValid = true;

    if (!validateMoodleId(moodleId.value)) {
        showError(moodleId);
        isValid = false;
    }

    if (!password.value) {
        showError(password);
        isValid = false;
    }

    if (isValid) {
        // Mock Login Success
        alert(`Logged in as code: ${moodleId.value}`);
        closeAuthModal();
        // Update UI logic here (e.g., change buttons to Profile)
    }
}

function handleSignup(e) {
    e.preventDefault();
    clearErrors(signupForm);

    const name = document.getElementById('signupName');
    const moodleId = document.getElementById('signupMoodleId');
    const email = document.getElementById('signupEmail');
    const password = document.getElementById('signupPassword');
    const confirm = document.getElementById('signupConfirmPassword');
    let isValid = true;

    if (!name.value.trim()) {
        showError(name);
        isValid = false;
    }

    if (!validateMoodleId(moodleId.value)) {
        showError(moodleId);
        isValid = false;
    }

    if (!validateEmail(email.value)) {
        showError(email);
        isValid = false;
    }

    if (password.value.length < 6) {
        showError(password);
        isValid = false;
    }

    if (password.value !== confirm.value) {
        showError(confirm);
        isValid = false;
    }

    if (isValid) {
        // Mock Signup Success
        alert('Account created successfully! Please login.');
        switchAuthTab('login');
    }
}

// Close on outside click is already in index.html, but let's reinforce it for this specific modal id
window.addEventListener('click', (e) => {
    if (e.target === authModal) {
        closeAuthModal();
    }
});
