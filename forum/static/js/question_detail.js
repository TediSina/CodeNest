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

    renderMarkdownBlocks('.js-markdown');

    const markdownInput = document.querySelector('.markdown-input');
    const previewElement = document.getElementById('markdown-preview');

    if (markdownInput && previewElement) {
        renderPreview(markdownInput, previewElement);
        markdownInput.addEventListener('input', () => renderPreview(markdownInput, previewElement));
    }
});
