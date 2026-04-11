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

            const label = document.createElement('div');
            label.textContent = language.toUpperCase();
            label.classList.add('code-block-language-label');

            const wrapper = document.createElement('div');
            wrapper.classList.add('code-block-wrapper');
            preElement.parentElement.insertBefore(wrapper, preElement);
            wrapper.appendChild(label);
            wrapper.appendChild(preElement);
        });
    }

    document.querySelectorAll('.js-markdown').forEach((element) => {
        const markdownContent = element.textContent.trim();

        if (!markdownContent) {
            element.innerHTML = '';
            return;
        }

        element.innerHTML = converter.makeHtml(markdownContent);
        decorateCodeBlocks(element);
    });
});
