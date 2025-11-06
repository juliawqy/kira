import { apiReport } from "../api.js";
import { showToast } from "../state.js";

let currentExportFormat = null;

/**
 * Downloads a report file (PDF or Excel) for a given project.
 * @param {number} projectId - The project ID
 * @param {string} format - 'pdf' or 'excel'
 * @param {Object} options - Optional parameters
 * @param {Function} options.log - Logging function
 */
export async function downloadReport(projectId, format, { log } = {}) {
  if (!projectId || projectId <= 0) {
    showToast("Please select a valid project", "error");
    return;
  }

  const formatLower = format.toLowerCase();
  if (formatLower !== "pdf" && formatLower !== "excel") {
    showToast("Invalid format. Please select PDF or Excel", "error");
    return;
  }

  const endpoint = formatLower === "pdf" ? "pdf" : "excel";
  const fileExtension = formatLower === "pdf" ? "pdf" : "xlsx";

  try {
    log?.("Download report", { projectId, format });
    
    const blob = await apiReport(`/project/${projectId}/${endpoint}`, {
      method: "GET"
    });

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `project_${projectId}_schedule_report.${fileExtension}`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showToast(`Report downloaded successfully (${format.toUpperCase()})`, "success");
    log?.("Report downloaded", { projectId, format });
    
  } catch (error) {
    const errorMessage = error.message || "Failed to download report";
    showToast(`Export failed: ${errorMessage}`, "error");
    log?.("Report download error", errorMessage);
    console.error("Report download error:", error);
  }
}

/**
 * Shows the export report dialog and handles user input.
 * @param {string} format - 'pdf' or 'excel'
 * @param {Object} options - Optional parameters
 * @param {Function} options.log - Logging function
 */
function showExportDialog(format, { log } = {}) {
  const dialog = document.getElementById("dlgExportReport");
  const titleEl = document.getElementById("exportReportTitle");
  const projectIdInput = document.getElementById("exportProjectId");
  const errorEl = document.getElementById("exportProjectId_err");

  if (!dialog) {
    console.error("Export dialog not found");
    return;
  }

  // Set format and update title
  currentExportFormat = format.toLowerCase();
  const formatUpper = format.toUpperCase();
  titleEl.textContent = `Export ${formatUpper} Report`;

  // Clear previous input and errors
  projectIdInput.value = "";
  errorEl.textContent = "";

  // Define handleConfirm
  const handleConfirm = async () => {
    const projectIdValue = projectIdInput.value.trim();
    
    // Validate input
    if (!projectIdValue) {
      errorEl.textContent = "Please enter a project ID";
      projectIdInput.focus();
      return;
    }

    const projectId = parseInt(projectIdValue);
    if (isNaN(projectId) || projectId <= 0) {
      errorEl.textContent = "Please enter a valid project ID (must be a positive number)";
      projectIdInput.focus();
      return;
    }

    // Clear error
    errorEl.textContent = "";

    // Close dialog
    dialog.close();
    currentExportFormat = null;

    // Download report
    await downloadReport(projectId, format, { log });
  };

  // Use event delegation on the dialog form to handle button clicks
  const form = dialog.querySelector("form");
  const abortController = new AbortController();

  // Clean up listeners when dialog closes
  dialog.addEventListener("close", () => {
    abortController.abort();
  }, { once: true });

  form.addEventListener("click", (e) => {
    if (e.target.id === "btnCancelExport" || e.target.value === "cancel") {
      e.preventDefault();
      dialog.close();
      currentExportFormat = null;
    } else if (e.target.id === "btnConfirmExport" || e.target.value === "default") {
      e.preventDefault();
      handleConfirm();
    }
  }, { signal: abortController.signal });

  // Handle Enter key in input
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleConfirm();
    }
  };
  projectIdInput.addEventListener("keypress", handleKeyPress, { signal: abortController.signal });

  // Show dialog and focus input
  dialog.showModal();
  projectIdInput.focus();
}

/**
 * Binds export buttons to the report download functionality.
 * @param {Object} options - Options object
 * @param {Function} options.log - Logging function
 */
export function bindReportExport({ log } = {}) {
  // Bind PDF export buttons
  const pdfButtons = document.querySelectorAll("[data-export-pdf]");
  pdfButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      showExportDialog("pdf", { log });
    });
  });

  // Bind Excel export buttons
  const excelButtons = document.querySelectorAll("[data-export-excel]");
  excelButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      showExportDialog("excel", { log });
    });
  });
}

