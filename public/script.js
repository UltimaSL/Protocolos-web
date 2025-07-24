// C:\xampp\htdocs\PaginaWeb-Examen\public\script.js
document.addEventListener('DOMContentLoaded', () => {
    const commandList = document.querySelectorAll('ul li');
    const outputArea = document.getElementById('output-area');
    // Estilos básicos para la salida
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
            outputArea.textContent = `Solicitando datos para ${commandType}...`;

            // La API de Flask se ejecuta en el mismo puerto que la página si Flask sirve el frontend
            // Por lo tanto, no necesitamos especificar http://localhost:5000 si Flask corre ahí.
            const apiEndpoint = `/api/eigrp_${commandType}_v4`; // Ruta relativa a la misma aplicación Flask

            try {
                const response = await fetch(apiEndpoint);
                const result = await response.json();

                if (result.status === 'success') {
                    // Si el parsing es completo, mostrar el objeto JSON
                    if (typeof result.data === 'object' && result.data !== null && !result.data.raw_output) {
                        outputArea.textContent = JSON.stringify(result.data, null, 2);
                    } else {
                        // Si el parsing no está completo, mostrar la salida raw
                        outputArea.textContent = result.data.raw_output || JSON.stringify(result.data, null, 2);
                    }
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