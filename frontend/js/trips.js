document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('create-trip-form');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const tripName = document.getElementById('trip-name').value;
            // Handle trip creation
            try {
                const response = await fetch('/api/trip', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: tripName })
                });
                const data = await response.json();
                if (data.success) {
                    alert(data.message);
                } else {
                    alert('Error: ' + data.message);
                }
            } catch (error) {
                console.error('Error creating trip:', error);
            }
        });
    }

    // Function to load trips on my_trips.html
    const tripsList = document.getElementById('trips-list');
    if (tripsList) {
        async function loadTrips() {
            try {
                const response = await fetch('/api/trips');
                const data = await response.json();
                if (data.success) {
                    tripsList.innerHTML = `<p>${data.message}</p>`;
                    // Render data.data here
                }
            } catch (error) {
                console.error('Error loading trips:', error);
            }
        }
        loadTrips();
    }
});
