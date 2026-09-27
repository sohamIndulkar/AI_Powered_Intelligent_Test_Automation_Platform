document.addEventListener('DOMContentLoaded', function () {
    // --- Element Selectors ---
    const runTestBtn = document.getElementById('run-test');
    const startVoiceBtn = document.getElementById('start-voice');
    const translateBtn = document.getElementById('translate-btn');
    const saveBtn = document.getElementById('save-btn');
    const approveBaselineBtn = document.getElementById('approve-baseline-btn');
    const generateScriptConfirmBtn = document.getElementById('generate-script-confirm-btn');
    const urlInput = document.getElementById('url');
    const commandsInput = document.getElementById('commands');
    const resultsContainer = document.getElementById('results-container');
    const spinner = document.getElementById('spinner');
    const downloadBtn = document.getElementById('download-btn');
    const downloadExcelBtn = document.getElementById('download-excel-btn');
    const visualTestActions = document.getElementById('visual-test-actions');
    const testGoalInput = document.getElementById('test-goal-input');

    let lastTestRunId = null; 

    // --- AI SCRIPT GENERATOR LOGIC ---
    if (generateScriptConfirmBtn) {
        generateScriptConfirmBtn.addEventListener('click', async () => {
            const url = urlInput.value;
            const goal = testGoalInput.value;

            if (!url || !goal) {
                alert('Please provide both a Website URL and a Test Goal.');
                return;
            }

            const originalText = generateScriptConfirmBtn.textContent;
            generateScriptConfirmBtn.textContent = 'Generating...';
            generateScriptConfirmBtn.disabled = true;

            try {
                const response = await fetch('/generate-script', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, goal }),
                });
                const data = await response.json();
                
                if (data.script) {
                    commandsInput.value = data.script;
                    const modalEl = document.getElementById('generateScriptModal');
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) {
                        modal.hide();
                    }

                    const backdrops = document.getElementsByClassName('modal-backdrop');
                    while(backdrops.length > 0){
                        document.body.removeChild(backdrops[0]);
                    }
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = 'auto';

                } else {
                    alert('AI could not generate a script. Error: ' + data.error);
                }
            } catch (error) {
                alert('An error occurred during script generation: ' + error);
            } finally {
                generateScriptConfirmBtn.textContent = 'Generate';
                generateScriptConfirmBtn.disabled = false;
            }
        });
    }

    // --- Save Button Logic ---
    saveBtn.addEventListener('click', async () => {
        const commands = commandsInput.value;
        if (!commands) { alert('There are no commands to save.'); return; }
        const name = prompt('Please enter a name for this test case:');
        if (!name) { alert('Save cancelled.'); return; }
        try {
            const response = await fetch('/save_test_case', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, commands }),
            });
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            alert('An error occurred while saving: ' + error);
        }
    });

    // --- Translate Button Logic ---
    translateBtn.addEventListener('click', async () => {
        const commands = commandsInput.value;
        if (!commands) { alert('Please enter a command to translate.'); return; }
        const originalText = translateBtn.textContent;
        translateBtn.textContent = "Translating...";
        translateBtn.disabled = true;
        try {
            const response = await fetch('/translate-command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ commands }),
            });
            const data = await response.json();
            if (data.structured_commands) {
                commandsInput.value = data.structured_commands;
            } else {
                alert('Could not translate the command. Error: ' + data.error);
            }
        } catch (error) {
            alert('An error occurred during translation: ' + error);
        } finally {
            translateBtn.textContent = originalText;
            translateBtn.disabled = false;
        }
    });

    // --- Voice Recognition Logic ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        startVoiceBtn.addEventListener('click', () => {
            let langCode = prompt("Enter language code (e.g., en-US, hi-IN, mr-IN):", "en-US");
            if (langCode) {
                recognition.lang = langCode;
                recognition.start();
                startVoiceBtn.textContent = "🎙️ Listening...";
                startVoiceBtn.disabled = true;
            }
        });
        recognition.onresult = (event) => { commandsInput.value += event.results[0][0].transcript + '\n'; };
        recognition.onspeechend = () => { recognition.stop(); };
        recognition.onend = () => {
            startVoiceBtn.textContent = "🎤 Start Voice";
            startVoiceBtn.disabled = false;
        };
        recognition.onerror = (event) => { alert('Error occurred in recognition: ' + event.error); };
    } else {
        startVoiceBtn.disabled = true;
        startVoiceBtn.textContent = "🎤 Voice Not Supported";
    }
    
    // --- Approve Baseline Button Logic ---
    approveBaselineBtn.addEventListener('click', async () => {
        const testCaseId = document.getElementById('test-case-id').value;
        if (!testCaseId || !lastTestRunId) {
            alert('Could not find the necessary test case or test run ID to approve the baseline.');
            return;
        }
        approveBaselineBtn.textContent = 'Saving...';
        approveBaselineBtn.disabled = true;
        try {
            const response = await fetch('/approve_baseline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_case_id: testCaseId, test_run_id: lastTestRunId }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert('Baseline approved and saved successfully! Future visual tests will compare against this new baseline.');
                visualTestActions.classList.add('d-none');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('An error occurred while approving the baseline: ' + error);
        } finally {
            approveBaselineBtn.textContent = 'Approve New Baseline';
            approveBaselineBtn.disabled = false;
        }
    });

    // --- Run Test Button Logic ---
    runTestBtn.addEventListener('click', async () => {
        const url = urlInput.value;
        const commands = commandsInput.value;
        const testCaseId = document.getElementById('test-case-id').value;
        const isVisualTest = document.getElementById('is-visual-test').value.toLowerCase() === 'true';
        if (!url || !commands) { alert('Please provide a URL and at least one command.'); return; }

        spinner.classList.remove('d-none');
        resultsContainer.innerHTML = '<p class="text-muted">Results will appear here.</p>';
        downloadBtn.classList.add('d-none');
        downloadExcelBtn.classList.add('d-none');
        visualTestActions.classList.add('d-none');
        runTestBtn.disabled = true;
        translateBtn.disabled = true;
        saveBtn.disabled = true;

        try {
            const response = await fetch('/run-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, commands, test_case_id: testCaseId, is_visual_test: isVisualTest }),
            });
            const data = await response.json();
            displayResults(data.results, isVisualTest);
            if (data.test_run_id) {
                downloadBtn.href = `/download_history/${data.test_run_id}`;
                downloadExcelBtn.href = `/download_excel/${data.test_run_id}`;
                lastTestRunId = data.test_run_id;
            }
        } catch (error) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error}</div>`;
        } finally {
            spinner.classList.add('d-none');
            runTestBtn.disabled = false;
            translateBtn.disabled = false;
            saveBtn.disabled = false;
            downloadBtn.classList.remove('d-none');
            downloadExcelBtn.classList.remove('d-none');
        }
    });

    // --- Display Results Helper Function ---
    function displayResults(results, isVisualTest) {
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = '<p>No results returned from the test.</p>';
            return;
        }
        const needsApproval = results.some(res => res.status === 'New Baseline' || res.status === 'Visual Mismatch');
        if (isVisualTest && needsApproval) {
            visualTestActions.classList.remove('d-none');
        }
        let headers = '<th>Step</th><th>Command</th><th>Status</th><th>Details</th>';
        if (isVisualTest) {
            headers += '<th>Screenshot</th>';
        }
        let tableHtml = `<table class="table table-dark table-bordered align-middle"><thead><tr>${headers}</tr></thead><tbody>`;
        results.forEach(res => {
            let statusClass = '';
            if (res.status === 'Success') statusClass = 'row-success';
            if (res.status === 'Failed') statusClass = 'row-danger';
            if (res.status === 'Visual Mismatch') statusClass = 'row-warning';
            if (res.status === 'New Baseline') statusClass = 'row-info';
            const aiSuggestionHtml = res.ai_suggestion ? `<div class="ai-suggestion mt-2"><strong>AI Assistant:</strong><br>${res.ai_suggestion.replace(/\n/g, '<br>')}</div>` : '';
            let rowHtml = `<tr class="${statusClass}">
                            <td>${res.step}</td>
                            <td><pre>${res.command}</pre></td>
                            <td>${res.status}</td>
                            <td>${res.details}${aiSuggestionHtml}</td>`;
            if (isVisualTest) {
                const screenshotHtml = res.screenshot ? `<img src="data:image/png;base64,${res.screenshot}" class="img-fluid rounded" alt="Test Screenshot">` : 'N/A';
                rowHtml += `<td>${screenshotHtml}</td>`;
            }
            rowHtml += `</tr>`;
            tableHtml += rowHtml;
        });
        tableHtml += '</tbody></table>';
        resultsContainer.innerHTML = tableHtml;
    }
});