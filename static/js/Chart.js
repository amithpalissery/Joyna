const ctx = document.getElementById('emotionChart').getContext('2d');
const emotionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Week 1', 'Week 2', 'Week 3'],
        datasets: [{
            label: 'Emotion Transition',
            data: [12, 19, 3],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    }
});
