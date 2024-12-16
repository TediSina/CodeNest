document.addEventListener('DOMContentLoaded', () => {
    const converter = new showdown.Converter({ tables: true, simplifiedAutoLink: true });

    document.querySelectorAll('.answer-body').forEach((element) => {
        const markdownContent = element.textContent;
        const htmlContent = converter.makeHtml(markdownContent);
        element.innerHTML = htmlContent;

        element.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);

            const languageClass = block.className.match(/language-([\w-]+)/);
            if (languageClass) {
                const language = languageClass[1];
                const label = document.createElement('div');
                label.textContent = language.toUpperCase();
                label.style.cssText = `
                    position: absolute;
                    top: 5px;
                    right: 10px;
                    background: #444;
                    color: #fff;
                    padding: 2px 6px;
                    font-size: 12px;
                    border-radius: 4px;
                `;
                block.parentElement.style.position = 'relative';
                block.parentElement.appendChild(label);
            }
        });
    });
});
