document.addEventListener('DOMContentLoaded', () => {
    // Itinerary logic goes here
    console.log("Itinerary module loaded");

    // Fetch itinerary for view
    const timeline = document.getElementById('itinerary-timeline');
    if (timeline) {
        async function loadItinerary(tripId) {
            try {
                const response = await fetch(`/api/itinerary/${tripId}`);
                const data = await response.json();
                if (data.success) {
                    timeline.innerHTML = `<p>${data.message}</p>`;
                }
            } catch (error) {
                console.error('Error loading itinerary:', error);
            }
        }
        // Example: loadItinerary(1);
    }
});
\
