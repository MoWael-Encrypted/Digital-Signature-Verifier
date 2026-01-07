document.addEventListener("DOMContentLoaded", () => {
    const signForm = document.getElementById("signForm");
    const signatureResult = document.getElementById("signatureResult");
    const signDocumentForm = document.getElementById("signDocumentForm");
    const signBtn = document.getElementById("signBtn");
    const signSpinner = document.getElementById("signSpinner");
    const signatureDisplay = document.getElementById("signatureDisplay");
    const copySignature = document.getElementById("copySignature");
    const downloadSignature = document.getElementById("downloadSignature");
    const signAnother = document.getElementById("signAnother");

    let generatedSignature = "";

    // Clear data when leaving the page
    window.addEventListener("beforeunload", () => {
        localStorage.removeItem("documentSignature");
    });

    // Form submission
    signDocumentForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const documentFile = document.getElementById("document").files[0];
        const privateKeyFile = document.getElementById("private_key").files[0];
        
        if (!documentFile || !privateKeyFile) {
            alert("Please select both a document and private key");
            return;
        }

        signBtn.disabled = true;
        signSpinner.classList.remove("d-none");
        signBtn.innerHTML = "Signing...";
        
        try {
            // Read private key
            const privateKey = await readFileAsText(privateKeyFile);
            
            // Read document
            const documentData = await readFileAsArrayBuffer(documentFile);
            
            // Hash the document (simplified example)
            const documentHash = CryptoJS.SHA256(CryptoJS.lib.WordArray.create(documentData)).toString();
            
            // Sign the hash (using JSEncrypt)
            const crypt = new JSEncrypt();
            crypt.setPrivateKey(privateKey);
            generatedSignature = crypt.sign(documentHash, CryptoJS.SHA256, "sha256");
            
            if (!generatedSignature) {
                throw new Error("Failed to generate signature");
            }
            
            // Display results
            signatureDisplay.textContent = generatedSignature;
            signForm.style.display = "none";
            signatureResult.style.display = "block";
            
            // Store in localStorage
            localStorage.setItem("documentSignature", JSON.stringify({
                signature: generatedSignature,
                documentName: documentFile.name
            }));
            
        } catch (error) {
            console.error("Signing error:", error);
            alert("Failed to sign document. Please try again.");
        } finally {
            signBtn.disabled = false;
            signSpinner.classList.add("d-none");
            signBtn.innerHTML = "Sign Document";
        }
    });

    // Copy signature
    copySignature.addEventListener("click", () => {
        navigator.clipboard.writeText(generatedSignature)
            .then(() => alert("Signature copied to clipboard!"))
            .catch(err => console.error("Failed to copy:", err));
    });

    // Download signature
    downloadSignature.addEventListener("click", () => {
        const docName = document.getElementById("document").files[0]?.name || "document";
        downloadFile(`${docName}.sig`, generatedSignature);
    });

    // Sign another document
    signAnother.addEventListener("click", () => {
        signForm.style.display = "block";
        signatureResult.style.display = "none";
        signDocumentForm.reset();
    });

    // Helper functions
    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    function readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    function downloadFile(filename, content) {
        const element = document.createElement("a");
        element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(content));
        element.setAttribute("download", filename);
        element.style.display = "none";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    // Load signature from localStorage if available
    const savedSignature = localStorage.getItem("documentSignature");
    if (savedSignature) {
        const { signature, documentName } = JSON.parse(savedSignature);
        generatedSignature = signature;
        signatureDisplay.textContent = signature;
        signForm.style.display = "none";
        signatureResult.style.display = "block";
    }
});