document.addEventListener('DOMContentLoaded', function () {
    const analyzeCodeBtn = document.getElementById('analyze-code-btn');
    const generateTestsBtn = document.getElementById('generate-tests-btn');
    const refactorCodeBtn = document.getElementById('refactor-code-btn');
    const codeInput = document.getElementById('code-input');
    const resultsOutput = document.getElementById('results-output');
    const spinner = document.getElementById('spinner-analysis');
    const downloadPdfBtn = document.getElementById('download-analysis-pdf');

    let lastAIResultMarkdown = ''; // Store the last AI Markdown result

    // --- PDF Download Logic ---
    downloadPdfBtn.addEventListener('click', async () => {
        if (!lastAIResultMarkdown) {
            alert("Please generate an analysis before downloading.");
            return;
        }

        // Disable button during download
        downloadPdfBtn.disabled = true;
        downloadPdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';

        try {
            const response = await fetch('/download_code_analysis_pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ai_result_markdown: lastAIResultMarkdown }),
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'ai_code_analysis_report.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                const errorData = await response.json();
                alert(`Error generating PDF: ${errorData.error || response.statusText}`);
            }
        } catch (error) {
            console.error('Download PDF error:', error);
            alert('An error occurred while trying to download the PDF.');
        } finally {
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Download PDF';
        }
    });

    // --- AI Request Logic ---
    const handleAIRequest = async (endpoint) => {
        const code = codeInput.value;
        if (!code) {
            alert('Please enter some code first.');
            return;
        }

        spinner.classList.remove('d-none');
        resultsOutput.innerHTML = '<p class="text-muted">The AI is analyzing your code...</p>';
        analyzeCodeBtn.disabled = true;
        generateTestsBtn.disabled = true;
        refactorCodeBtn.disabled = true;
        downloadPdfBtn.disabled = true; // Disable PDF button while generating new results

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code }),
            });

            const data = await response.json();

            if (data.result) {
                lastAIResultMarkdown = data.result; // Store the raw Markdown here
                resultsOutput.innerHTML = marked.parse(data.result);
                resultsOutput.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            } else {
                resultsOutput.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
                lastAIResultMarkdown = ''; // Clear stored markdown on error
            }
        } catch (error) {
            resultsOutput.innerHTML = `<p class="text-danger">An unexpected error occurred: ${error}</p>`;
            lastAIResultMarkdown = ''; // Clear stored markdown on error
        } finally {
            spinner.classList.add('d-none');
            analyzeCodeBtn.disabled = false;
            generateTestsBtn.disabled = false;
            refactorCodeBtn.disabled = false;
            if (lastAIResultMarkdown) { // Only enable PDF download if there's valid content
                downloadPdfBtn.disabled = false;
            }
        }
    };

    analyzeCodeBtn.addEventListener('click', () => {
        handleAIRequest('/analyze-code');
    });

    generateTestsBtn.addEventListener('click', () => {
        handleAIRequest('/generate-tests');
    });

    refactorCodeBtn.addEventListener('click', () => {
        handleAIRequest('/refactor-code');
    });
});