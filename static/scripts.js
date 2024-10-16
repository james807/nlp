document.addEventListener('DOMContentLoaded', function () {
    const uploadBtn = document.getElementById('upload-btn');
    const queryBtn = document.getElementById('query-btn');
    const toggleDarkMode = document.getElementById('toggle-dark-mode');

    // File upload handling
    uploadBtn.addEventListener('click', () => {
        const fileInput = document.getElementById('file');
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    document.getElementById('data-table').innerHTML = data.table;
                }
            });
        }
    });

    // Query handling
    queryBtn.addEventListener('click', () => {
        const query = document.getElementById('query-input').value;
        const file = document.getElementById('file').files[0];

        if (query && file) {
            fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, file: file.name })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('query-result').innerText = data.result;
            });
        }
    });

    // Dark mode toggle
    toggleDarkMode.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode');
    });
});
