function predict() {
    var text = document.getElementById('text').value.trim();
    if (text === '') {
        document.getElementById('prediction').innerHTML = 'Please Enter Some Text';
        return;
    }

    document.getElementById('prediction').innerHTML = 'Analyzing...';

    fetch('/spam-detector', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        var category = data.category;
        document.getElementById('prediction').innerHTML = `Result: ${category[0]}`;
        
        anime({
            targets: '#prediction',
            opacity: [0, 1],
            translateY: [-20, 0],
            duration: 1000,
            easing: 'easeOutExpo'
        });
    })
    .catch(function(error) {
        document.getElementById('prediction').innerHTML = 'Error: ' + error.message;
    });
}