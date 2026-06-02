document.addEventListener('DOMContentLoaded', () => {
    const converter = new showdown.Converter({
        tables: true,
        simplifiedAutoLink: true,
        strikethrough: true,
        tasklists: true,
    });

    function decorateCodeBlocks(scope) {
        scope.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);

            const preElement = block.parentElement;
            if (preElement.parentElement && preElement.parentElement.classList.contains('code-block-wrapper')) {
                return;
            }

            const languageClass = Array.from(block.classList).find((cls) => cls.startsWith('language-'));
            const language = languageClass ? languageClass.replace('language-', '') : 'plaintext';

            const languageLabel = document.createElement('div');
            languageLabel.textContent = language.toUpperCase();
            languageLabel.classList.add('code-block-language-label');

            const wrapper = document.createElement('div');
            wrapper.classList.add('code-block-wrapper');
            preElement.parentElement.insertBefore(wrapper, preElement);
            wrapper.appendChild(languageLabel);
            wrapper.appendChild(preElement);
        });
    }

    function renderMarkdownBlocks(selector) {
        document.querySelectorAll(selector).forEach((element) => {
            const markdownContent = element.textContent.trim();

            if (!markdownContent) {
                element.innerHTML = '';
                return;
            }

            element.innerHTML = converter.makeHtml(markdownContent);
            decorateCodeBlocks(element);
        });
    }

    function renderPreview(input, preview) {
        const markdownContent = input.value.trim();

        if (!markdownContent) {
            preview.classList.add('preview-surface--empty');
            preview.innerHTML = '<p class="preview-placeholder">Your live preview appears here as you type.</p>';
            return;
        }

        preview.classList.remove('preview-surface--empty');
        preview.innerHTML = converter.makeHtml(input.value);
        decorateCodeBlocks(preview);
    }

    function bindVoteControls() {
        document.querySelectorAll('.vote-controls__form').forEach((form) => {
            form.addEventListener('submit', async (event) => {
                event.preventDefault();

                const submitter = event.submitter || form.querySelector('.vote-controls__button[type="submit"]');
                const controls = form.closest('.vote-controls');
                const buttons = controls.querySelectorAll('.vote-controls__button[type="submit"]');
                const formData = new FormData(form);
                formData.set(submitter.name, submitter.value);

                buttons.forEach((button) => {
                    button.disabled = true;
                });

                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        credentials: 'same-origin',
                    });

                    if (!response.ok) {
                        throw new Error('Vote request failed.');
                    }

                    const vote = await response.json();

                    document.querySelectorAll(`[data-vote-score-for="${controls.dataset.voteTarget}"]`).forEach((score) => {
                        score.textContent = vote.score;
                        score.setAttribute('aria-label', `${vote.score} vote score`);
                    });

                    controls.querySelectorAll('.vote-controls__button[name="value"]').forEach((button) => {
                        const isActive = Number(button.value) === vote.user_vote;
                        button.classList.toggle('vote-controls__button--active', isActive);
                        button.setAttribute('aria-pressed', String(isActive));
                    });
                } catch (error) {
                    console.error(error);
                } finally {
                    buttons.forEach((button) => {
                        button.disabled = false;
                    });
                }
            });
        });
    }

    renderMarkdownBlocks('.js-markdown');
    bindVoteControls();

    const markdownInput = document.querySelector('.markdown-input');
    const previewElement = document.getElementById('markdown-preview');

    if (markdownInput && previewElement) {
        renderPreview(markdownInput, previewElement);
        markdownInput.addEventListener('input', () => renderPreview(markdownInput, previewElement));
    }
});
