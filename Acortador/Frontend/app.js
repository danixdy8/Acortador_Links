// ============================================================
// LÓGICA DE LA INTERFAZ WEB (FRONTEND)
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    // Referencias al DOM
    const form = document.getElementById("shorten-form");
    const urlInput = document.getElementById("original-url");
    const submitBtn = document.getElementById("submit-btn");
    const btnText = document.getElementById("btn-text");
    const spinner = document.getElementById("spinner");

    const alertError = document.getElementById("alert-error");
    const alertSuccess = document.getElementById("alert-success");

    const resultBox = document.getElementById("result-box");
    const shortUrlOutput = document.getElementById("short-url-output");
    const copyBtn = document.getElementById("copy-btn");
    const openBtn = document.getElementById("open-btn");
    const shortCodeMeta = document.getElementById("meta-short-code");
    const originalUrlMeta = document.getElementById("meta-original-url");

    const apiDisplay = document.getElementById("api-display");
    const changeApiBtn = document.getElementById("change-api-btn");

    // Inicializar visualización del Backend URL
    function updateApiDisplay() {
        const currentUrl = window.CONFIG.getApiUrl();
        apiDisplay.textContent = currentUrl;
    }
    updateApiDisplay();

    // Permitir cambiar la URL del backend dinámicamente
    changeApiBtn.addEventListener("click", () => {
        const currentUrl = window.CONFIG.getApiUrl();
        const newUrl = prompt(
            "Ingrese la URL base del Backend FastAPI desplegado en EC2 (ejemplo: http://54.210.12.34:8000):",
            currentUrl
        );
        if (newUrl !== null && newUrl.trim() !== "") {
            window.CONFIG.setApiUrl(newUrl.trim());
            updateApiDisplay();
            showSuccess(`URL del backend actualizada a: ${window.CONFIG.getApiUrl()}`);
        }
    });

    // Manejo de Alertas
    function showError(message) {
        alertError.textContent = message;
        alertError.style.display = "block";
        alertSuccess.style.display = "none";
    }

    function showSuccess(message) {
        alertSuccess.textContent = message;
        alertSuccess.style.display = "block";
        alertError.style.display = "none";
    }

    function clearAlerts() {
        alertError.style.display = "none";
        alertSuccess.style.display = "none";
    }

    // Estado del botón de envío
    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            spinner.style.display = "inline-block";
            btnText.textContent = "Acortando...";
        } else {
            submitBtn.disabled = false;
            spinner.style.display = "none";
            btnText.textContent = "Acortar enlace";
        }
    }

    // Copiar al portapapeles con fallback para entornos HTTP
    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback para HTTP (común en S3 static website sin CloudFront)
            return new Promise((resolve, reject) => {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                textArea.style.top = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    const successful = document.execCommand("copy");
                    document.body.removeChild(textArea);
                    if (successful) resolve();
                    else reject(new Error("Falló execCommand('copy')"));
                } catch (err) {
                    document.body.removeChild(textArea);
                    reject(err);
                }
            });
        }
    }

    // Manejo del formulario
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        clearAlerts();
        resultBox.style.display = "none";

        const originalUrl = urlInput.value.trim();

        // Validación de URL
        if (!originalUrl) {
            showError("Por favor ingrese una URL válida.");
            urlInput.focus();
            return;
        }

        if (!/^https?:\/\/.+/i.test(originalUrl)) {
            showError("La URL debe comenzar con http:// o https://");
            urlInput.focus();
            return;
        }

        const apiBaseUrl = window.CONFIG.getApiUrl().replace(/\/+$/, "");
        setLoading(true);

        try {
            const response = await fetch(`${apiBaseUrl}/shorten`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ original_url: originalUrl })
            });

            if (!response.ok) {
                let errorMessage = `Error del servidor (${response.status})`;
                try {
                    const errData = await response.json();
                    if (errData && errData.detail) {
                        errorMessage = typeof errData.detail === "string"
                            ? errData.detail
                            : JSON.stringify(errData.detail);
                    }
                } catch {
                    // Si la respuesta no es JSON
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();

            // Desplegar resultado
            shortUrlOutput.value = data.short_url;
            openBtn.href = data.short_url;
            shortCodeMeta.textContent = data.short_code;
            originalUrlMeta.textContent = data.original_url;

            resultBox.style.display = "block";
            showSuccess("¡Enlace acortado con éxito! Registro persistido en DynamoDB.");

            // Limpiar campo de entrada
            urlInput.value = "";
        } catch (error) {
            console.error("Error al acortar enlace:", error);
            showError(
                error.message.includes("Failed to fetch") || error.message.includes("NetworkError")
                    ? `No se pudo conectar con el backend en "${apiBaseUrl}". Verifique que la instancia EC2 esté en ejecución, que el puerto 8000 esté permitido en el Security Group y que CORS esté habilitado.`
                    : error.message
            );
        } finally {
            setLoading(false);
        }
    });

    // Acción de Copiar
    copyBtn.addEventListener("click", async () => {
        const textToCopy = shortUrlOutput.value;
        if (!textToCopy) return;

        try {
            await copyToClipboard(textToCopy);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = "¡Copiado! ✓";
            copyBtn.classList.add("copied");

            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.classList.remove("copied");
            }, 2000);
        } catch (err) {
            console.error("No se pudo copiar el texto:", err);
            showError("No se pudo copiar automáticamente. Por favor selecciónelo y cópielo manualmente.");
        }
    });
});
