document.addEventListener("DOMContentLoaded", () => {
    const user = JSON.parse(localStorage.getItem("user"));
  
    if (!user) {
      window.location.href = "login.html";
      return;
    }
  
    const name = user.full_name || user.email.split("@")[0];
    document.getElementById("welcomeMsg").textContent = `Welcome back, ${name}!`;
    document.getElementById("navUsername").textContent = `Hey, ${name}!`;
  
    loadTrips();
  });
  
  async function loadTrips() {
    try {
      const res = await apiRequest("/trips");
  
      if (res.success && res.data.length > 0) {
        document.getElementById("emptyState").style.display = "none";
        document.getElementById("totalTrips").textContent = res.data.length;
  
        const upcoming = res.data.filter(t => new Date(t.start_date) > new Date());
        document.getElementById("upcomingTrips").textContent = upcoming.length;
  
        const grid = document.getElementById("tripsGrid");
        res.data.slice(0, 3).forEach(trip => {
          const card = document.createElement("div");
          card.className = "trip-card";
          card.innerHTML = `
            <h3>${trip.name}</h3>
            <div class="trip-dates">${trip.start_date} → ${trip.end_date}</div>
            <span class="trip-tag">${trip.destination_count || 0} stops</span>
          `;
          grid.appendChild(card);
        });
      }
    } catch (err) {
      console.log("No trips yet.");
    }
  }
  
  async function handleLogout() {
    await apiRequest("/logout", "POST");
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
  }