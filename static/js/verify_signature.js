document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const verifyForm = document.getElementById("verifyForm");
    const verificationResult = document.getElementById("verificationResult");
    const verifySignatureForm = document.getElementById("verifySignatureForm");
    const verifyBtn = document.getElementById("verifyBtn");
    const verifySpinner = document.getElementById("verifySpinner");
    const resultAlert = document.getElementById("resultAlert");
    const documentName = document.getElementById("documentName");
    const documentSize = document.getElementById("documentSize");
    const documentType = document.getElementById("documentType");
    const verificationStatus = document.getElementById("verificationStatus");
    const verificationDetails = document.getElementById("verificationDetails");
    const verifyAnother = document.getElementById("verifyAnother");

    // State management
    let verificationData = {
        document: null,
        isValid: false,
        details: ""
    };

    // Initialize the page
    function initPage() {
        // Reset form and UI
        verifySignatureForm.reset();
        verifyForm.style.display = "block";
        verificationResult.style.display = "none";
        verifyBtn.disabled = false;
        verifySpinner.classList.add("d-none");
        verifyBtn.innerHTML = "Verify Signature";
        resultAlert.style.display = "none";
    }

    // Verify signature
    verifySignatureForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const documentFile = document.getElementById("document").files[0];
        const signatureFile = document.getElementById("signature").files[0];
        const publicKeyFile = document.getElementById("public_key").files[0];
        
        if (!documentFile || !signatureFile || !publicKeyFile) {
            showAlert("Please select all required files", "warning");
            return;
        }

        // UI Feedback
        verifyBtn.disabled = true;
        verifySpinner.classList.remove("d-none");
        verifyBtn.innerHTML = "Verifying...";
        
        try {
            const formData = new FormData();
            formData.append("document", documentFile);
            formData.append("signature", signatureFile);
            formData.append("public_key", publicKeyFile);

            const response = await fetch("http://127.0.0.1:5500/verify_signature", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.error) {
                showAlert(result.message, "danger");
                resetForm();
                return;
            }

            // Display results
            verifyForm.style.display = "none";
            verificationResult.style.display = "block";

            // Update document info
            documentName.textContent = documentFile.name;
            documentSize.textContent = formatFileSize(documentFile.size);
            documentType.textContent = documentFile.type || "application/octet-stream";

            // Update verification status
            const statusClass = result.is_valid ? "signature-valid" : "signature-invalid";
            const statusIcon = result.is_valid ? "✓" : "✗";
            verificationStatus.className = statusClass;
            verificationStatus.innerHTML = `${statusIcon} ${result.is_valid ? "Valid Signature" : "Invalid Signature"}`;
            
            // Update verification details
            verificationDetails.textContent = result.message;
            
            // Update alert
            showAlert(result.message, result.is_valid ? "success" : "danger");
            
        } catch (error) {
            console.error("Verification error:", error);
            showAlert("Failed to verify signature. Please try again.", "danger");
            resetForm();
        } finally {
            verifyBtn.disabled = false;
            verifySpinner.classList.add("d-none");
            verifyBtn.innerHTML = "Verify Signature";
        }
    });

    // Display verification result
    function displayVerificationResult() {
        if (!verificationData.document) return;
        
        // Document info
        documentName.textContent = verificationData.document.name;
        documentSize.textContent = verificationData.document.size;
        documentType.textContent = verificationData.document.type;
        
        // Verification status
        if (verificationData.isValid) {
            resultAlert.className = "alert alert-success";
            resultAlert.innerHTML = `<strong>✓ Signature Valid</strong>`;
            verificationStatus.className = "signature-valid";
            verificationStatus.innerHTML = "✓ Signature is VALID";
        } else {
            resultAlert.className = "alert alert-danger";
            resultAlert.innerHTML = `<strong>✗ Signature Invalid</strong>`;
            verificationStatus.className = "signature-invalid";
            verificationStatus.innerHTML = "✗ Signature is INVALID";
        }
        
        verificationDetails.textContent = verificationData.details;
        
        // Show result section
        verifyForm.style.display = "none";
        verificationResult.style.display = "block";
    }

    // Verify another document
    verifyAnother.addEventListener("click", initPage);

    // Helper functions
    function showAlert(message, type) {
        resultAlert.className = `alert alert-${type}`;
        resultAlert.textContent = message;
        resultAlert.style.display = "block";
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function resetForm() {
        verifySignatureForm.reset();
        verifyBtn.disabled = false;
        verifySpinner.classList.add("d-none");
        verifyBtn.innerHTML = "Verify Signature";
        verifyForm.style.display = "block";
        verificationResult.style.display = "none";
    }

    // Clear data when leaving the page
    window.addEventListener("beforeunload", () => {
        localStorage.removeItem("verificationData");
    });

    // Load verification data from localStorage if available
    const savedVerification = localStorage.getItem("verificationData");
    if (savedVerification) {
        try {
            verificationData = JSON.parse(savedVerification);
            displayVerificationResult();
        } catch (e) {
            console.error("Error loading saved verification:", e);
            initPage();
        }
    } else {
        initPage();
    }
});
