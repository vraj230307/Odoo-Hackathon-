function togglePassword() {
    const pw = document.getElementById("password");
    const btn = document.querySelector(".toggle-pw");
    if (pw.type === "password") {
      pw.type = "text";
      btn.textContent = "Hide";
    } else {
      pw.type = "password";
      btn.textContent = "Show";
    }
  }
  
  function showError(msg) {
    const box = document.getElementById("errorBox");
    box.textContent = msg;
    box.classList.add("show");
  }
  
  function hideError() {
    document.getElementById("errorBox").classList.remove("show");
  }
  
  async function handleLogin() {
    hideError();
  
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
  
    if (!email || !password) {
      showError("Please fill in all fields.");
      return;
    }
  
    if (!email.includes("@")) {
      showError("Please enter a valid email.");
      return;
    }
  
    try {
      const res = await apiRequest("/login", "POST", { email, password });
  
      if (res.success) {
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        window.location.href = "dashboard.html";
      } else {
        showError(res.message || "Login failed. Try again.");
      }
    } catch (err) {
      showError("Something went wrong. Check your connection.");
    }
  }
  function togglePassword(fieldId, btn) {
    const pw = document.getElementById(fieldId);
    if (pw.type === "password") {
      pw.type = "text";
      btn.textContent = "Hide";
    } else {
      pw.type = "password";
      btn.textContent = "Show";
    }
  }
  
  function showSuccess(msg) {
    const box = document.getElementById("successBox");
    box.textContent = msg;
    box.classList.add("show");
  }
  
  async function handleSignup() {
    hideError();
  
    const fullname = document.getElementById("fullname").value.trim();
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirm  = document.getElementById("confirm").value;
  
    if (!fullname || !email || !password || !confirm) {
      showError("Please fill in all fields.");
      return;
    }
  
    if (!email.includes("@")) {
      showError("Please enter a valid email.");
      return;
    }
  
    if (password.length < 6) {
      showError("Password must be at least 6 characters.");
      return;
    }
  
    if (password !== confirm) {
      showError("Passwords do not match.");
      return;
    }
  
    try {
      const res = await apiRequest("/register", "POST", { fullname, email, password });
  
      if (res.success) {
        showSuccess("Account created! Redirecting to login...");
        setTimeout(() => { window.location.href = "login.html"; }, 2000);
      } else {
        showError(res.message || "Signup failed. Try again.");
      }
    } catch (err) {
      showError("Something went wrong. Check your connection.");
    }
  }