document.getElementById('fashion-form').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get form data
    const clothingType = document.getElementById('clothing-type').value;
    const budget = document.getElementById('budget').value;
    const priority = document.getElementById('priority').value;

    // Send data to backend
    fetch('/get-recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            clothing_type: clothingType,
            budget: budget,
            priority: priority
        })
    })
    .then(response => response.json())
    .then(data => {
        // Display results
        const list = document.getElementById('recommendation-list');
        list.innerHTML = '';

        if (data.length > 0) {
            data.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = `${rec.brand} (${rec.rating}): $${rec.price} - ${rec.focus}`;
                list.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No options match your criteria. Try adjusting your preferences!';
            list.appendChild(li);
        }
    })
    .catch(error => console.error('Error:', error));
});