// C:\xampp\htdocs\PaginaWeb-Examen\public\script.js
document.addEventListener('DOMContentLoaded', () => {
    const commandList = document.querySelectorAll('ul li');
    const outputArea = document.getElementById('output-area');
    // Estilos básicos para la salida (puedes mover esto a style.css)
    outputArea.style.backgroundColor = '#333';
    outputArea.style.color = '#0f0';
    outputArea.style.padding = '15px';
    outputArea.style.marginTop = '20px';
    outputArea.style.borderRadius = '5px';
    outputArea.style.whiteSpace = 'pre-wrap';
    outputArea.style.overflowX = 'auto';

    commandList.forEach(item => {
        item.addEventListener('click', async (event) => {
            const commandType = event.target.dataset.commandType;
            outputArea.textContent = `Solicitando datos de ${commandType}...`;

            // La URL de la API ahora usa el tipo de comando para construir la ruta
            const apiEndpoint = `/api/eigrp_${commandType}`;

            try {
                const response = await fetch(apiEndpoint);
                const result = await response.json();

                if (result.status === 'success') {
                    outputArea.textContent = JSON.stringify(result.data, null, 2);
                } else {
                    outputArea.textContent = `Error del servidor Flask: ${result.message}`;
                    console.error('Error del servidor Flask:', result.message);
                }
            } catch (error) {
                outputArea.textContent = `Error de conexión con el servidor Flask: ${error.message}`;
                console.error('Error de conexión o API:', error);
            }
        });
    });
});
