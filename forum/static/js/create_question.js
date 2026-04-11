document.addEventListener('DOMContentLoaded', () => {
    const converter = new showdown.Converter({
        tables: true,
        simplifiedAutoLink: true,
        strikethrough: true,
        tasklists: true,
    });

    const input = document.querySelector('.markdown-input');
    const preview = document.getElementById('markdown-preview');

    function highlightCode(scope) {
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

    function renderPreview() {
        if (!input || !preview) {
            return;
        }

        if (!input.value.trim()) {
            preview.classList.add('preview-surface--empty');
            preview.innerHTML = '<p class="preview-placeholder">Start typing in the editor to preview your question here.</p>';
            return;
        }

        preview.classList.remove('preview-surface--empty');
        preview.innerHTML = converter.makeHtml(input.value);
        highlightCode(preview);
    }

    renderPreview();

    if (input) {
        input.addEventListener('input', renderPreview);
    }
});
