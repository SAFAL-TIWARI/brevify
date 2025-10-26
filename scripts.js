 // DOM Elements
        const inputText = document.getElementById('inputText');
        const outputText = document.getElementById('outputText');
        const summarizeBtn = document.getElementById('summarizeBtn');
        const copyBtn = document.getElementById('copyBtn');
        const charCount = document.getElementById('charCount');
        const lengthSlider = document.getElementById('lengthSlider');
        const lengthLabel = document.getElementById('lengthLabel');
        const modeButtons = document.querySelectorAll('.mode-btn');
        const btnText = document.querySelector('.btn-text');
        const loader = document.querySelector('.loader');

        // State
        let selectedMode = 'paragraph';
        const lengthOptions = ['Short', 'Medium', 'Long'];

        // Character count update
        inputText.addEventListener('input', () => {
            charCount.textContent = inputText.value.length;
        });

        // Length slider update
        lengthSlider.addEventListener('input', (e) => {
            lengthLabel.textContent = lengthOptions[e.target.value];
        });

        // Mode selection
        modeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                modeButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedMode = btn.dataset.mode;
            });
        });

        // Summarize button click handler
        summarizeBtn.addEventListener('click', async () => {
            const text = inputText.value.trim();
            
            // Validation
            if (!text) {
                alert('Please enter some text to summarize.');
                return;
            }
            
            if (text.length < 50) {
                alert('Please enter at least 50 characters for meaningful summarization.');
                return;
            }

            // Get selected length
            const length = lengthOptions[lengthSlider.value];

            // UI updates
            summarizeBtn.disabled = true;
            btnText.style.display = 'none';
            loader.style.display = 'inline-block';
            outputText.innerHTML = '<p class="placeholder">✨ Generating your summary...</p>';
            copyBtn.style.display = 'none';

            try {
                /**
                 * API Call to Flask Backend
                 * POST request to /summarize endpoint with:
                 * - text: the input text to summarize
                 * - mode: selected summarization mode
                 * - length: selected summary length (Short/Medium/Long)
                 */
                const response = await fetch('http://localhost:5000/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        mode: selectedMode,
                        length: length.toLowerCase()
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Success: Display the summary
                    outputText.innerHTML = `<div class="summary-content">${formatSummary(data.summary)}</div>`;
                    copyBtn.style.display = 'block';
                } else {
                    // Error from backend
                    outputText.innerHTML = `<p class="error">❌ Error: ${data.error || 'Failed to generate summary'}</p>`;
                }
            } catch (error) {
                // Network or other errors
                outputText.innerHTML = `<p class="error">❌ Connection Error: ${error.message}</p>`;
            } finally {
                // Reset button state
                summarizeBtn.disabled = false;
                btnText.style.display = 'inline';
                loader.style.display = 'none';
            }
        });

        // Copy to clipboard functionality
        copyBtn.addEventListener('click', () => {
            const summaryText = outputText.querySelector('.summary-content').textContent;
            navigator.clipboard.writeText(summaryText).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }).catch(err => {
                alert('Failed to copy text: ' + err);
            });
        });

        // Format summary output (preserve line breaks and formatting)
        function formatSummary(summary) {
            return summary
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
        }

        // Enter key to submit (Ctrl/Cmd + Enter)
        inputText.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                summarizeBtn.click();
            }
        });