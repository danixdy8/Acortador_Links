// ============================================================
// CONFIGURACIÓN DEL FRONTEND - ACORTADOR DE ENLACES
// ============================================================
// Modifique la variable API_BASE_URL con la IP pública o DNS de su instancia EC2.
// Ejemplo: "http://54.210.12.34:8000"
// En desarrollo local use: "http://localhost:8000"

const CONFIG = {
    // Si ha guardado una URL personalizada en localStorage, se utilizará esa;
    // de lo contrario, se usará la URL predeterminada definida aquí.
    DEFAULT_API_URL: "http://18.216.136.191:8000/",

    getApiUrl() {
        return localStorage.getItem("shortener_api_url") || this.DEFAULT_API_URL;
    },

    setApiUrl(newUrl) {
        if (!newUrl) {
            localStorage.removeItem("shortener_api_url");
        } else {
            localStorage.setItem("shortener_api_url", newUrl.replace(/\/+$/, ""));
        }
    }
};

window.CONFIG = CONFIG;
