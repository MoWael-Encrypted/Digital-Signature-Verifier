document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const keyGenForm = document.getElementById("keyGenForm");
    const generateBtn = document.getElementById("generateBtn");
    const generateSpinner = document.getElementById("generateSpinner");
    const keyDisplay = document.getElementById("keyDisplay");
    const publicKeyDisplay = document.getElementById("publicKeyDisplay");
    const privateKeyDisplay = document.getElementById("privateKeyDisplay");
    const copyPublicKey = document.getElementById("copyPublicKey");
    const copyPrivateKey = document.getElementById("copyPrivateKey");
    const downloadPublicKey = document.getElementById("downloadPublicKey");
    const downloadPrivateKey = document.getElementById("downloadPrivateKey");
    const keySize = document.getElementById("keySize");

    // State management
    let generatedKeys = {
        publicKey: "",
        privateKey: ""
    };

    // Initialize the page
    function initPage() {
        // Clear any existing keys from localStorage
        localStorage.removeItem("rsaKeys");
        
        // Reset form and UI
        keyGenForm.reset();
        keyDisplay.style.display = "none";
        generateBtn.disabled = false;
        generateSpinner.classList.add("d-none");
        generateBtn.innerHTML = "Generate Key Pair";
    }

    // Generate RSA key pair
    keyGenForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // UI Feedback
        generateBtn.disabled = true;
        generateSpinner.classList.remove("d-none");
        generateBtn.innerHTML = "Generating...";
        
        try {
            // Generate keys using JSEncrypt
            const crypt = new JSEncrypt({
                default_key_size: parseInt(keySize.value)
            });
            
            // Get keys
            generatedKeys.privateKey = crypt.getPrivateKey();
            generatedKeys.publicKey = crypt.getPublicKey();
            
            // Validate keys
            if (!generatedKeys.privateKey || !generatedKeys.publicKey) {
                throw new Error("Key generation failed - empty keys returned");
            }
            
            // Display keys
            publicKeyDisplay.textContent = generatedKeys.publicKey;
            privateKeyDisplay.textContent = generatedKeys.privateKey;
            
            // Show key display section
            keyDisplay.style.display = "block";
            
            // Temporarily save to localStorage (only while on this page)
            localStorage.setItem("rsaKeys", JSON.stringify(generatedKeys));
            
            // Scroll to display
            keyDisplay.scrollIntoView({ behavior: "smooth" });
            
        } catch (error) {
            console.error("Key generation error:", error);
            alert("Failed to generate keys. Please try again.");
            initPage();
        } finally {
            generateBtn.disabled = false;
            generateSpinner.classList.add("d-none");
            generateBtn.innerHTML = "Generate Key Pair";
        }
    });

    // Copy keys to clipboard
    copyPublicKey.addEventListener("click", () => {
        if (!generatedKeys.publicKey) return;
        navigator.clipboard.writeText(generatedKeys.publicKey)
            .then(() => {
                showAlert("Public key copied to clipboard!", "success");
            })
            .catch(err => {
                console.error("Failed to copy:", err);
                showAlert("Failed to copy public key", "danger");
            });
    });

    copyPrivateKey.addEventListener("click", () => {
        if (!generatedKeys.privateKey) return;
        navigator.clipboard.writeText(generatedKeys.privateKey)
            .then(() => {
                showAlert("Private key copied to clipboard!", "success");
            })
            .catch(err => {
                console.error("Failed to copy:", err);
                showAlert("Failed to copy private key", "danger");
            });
    });

    // Download keys
    downloadPublicKey.addEventListener("click", () => {
        if (!generatedKeys.publicKey) return;
        downloadFile("public_key.pem", generatedKeys.publicKey);
    });

    downloadPrivateKey.addEventListener("click", () => {
        if (!generatedKeys.privateKey) return;
        downloadFile("private_key.pem", generatedKeys.privateKey);
    });

    // Helper function to download files
    function downloadFile(filename, content) {
        try {
            const element = document.createElement("a");
            element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(content));
            element.setAttribute("download", filename);
            element.style.display = "none";
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
            showAlert(`${filename} downloaded successfully`, "success");
        } catch (error) {
            console.error("Download failed:", error);
            showAlert("Failed to download file", "danger");
        }
    }

    // Show temporary alert message
    function showAlert(message, type) {
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = "20px";
        alertDiv.style.right = "20px";
        alertDiv.style.zIndex = "1000";
        alertDiv.style.minWidth = "300px";
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.classList.remove("show");
            setTimeout(() => alertDiv.remove(), 150);
        }, 3000);
    }

    // Clear data when leaving the page
    window.addEventListener("beforeunload", () => {
        localStorage.removeItem("rsaKeys");
    });

    // Load keys from localStorage if available (only persists during session)
    const savedKeys = localStorage.getItem("rsaKeys");
    if (savedKeys) {
        try {
            generatedKeys = JSON.parse(savedKeys);
            publicKeyDisplay.textContent = generatedKeys.publicKey;
            privateKeyDisplay.textContent = generatedKeys.privateKey;
            keyDisplay.style.display = "block";
        } catch (e) {
            console.error("Error loading saved keys:", e);
            initPage();
        }
    } else {
        initPage();
    }
});