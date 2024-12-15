document.addEventListener('DOMContentLoaded', () => {
    const converter = new showdown.Converter({ tables: true, simplifiedAutoLink: true });

    const questionBodyElement = document.querySelector('.question-body p');
    if (questionBodyElement) {
        const markdownContent = questionBodyElement.textContent;
        const htmlContent = converter.makeHtml(markdownContent);
        questionBodyElement.innerHTML = htmlContent;
    }

    const answerElements = document.querySelectorAll('.answers-list .answer p');
    answerElements.forEach(answerElement => {
        const markdownContent = answerElement.textContent;
        const htmlContent = converter.makeHtml(markdownContent);
        answerElement.innerHTML = htmlContent;
    });

    document.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block);

        const blockClasses = block.className.split(/\s+/);
        const languageClass = blockClasses.find(cls => cls.startsWith('language-'));
        const language = languageClass ? languageClass.replace('language-', '') : 'plaintext';

        const languageLabel = document.createElement('div');
        languageLabel.textContent = language.toUpperCase();
        languageLabel.classList.add('code-block-language-label');

        const preElement = block.parentElement;
        const wrapper = document.createElement('div');
        wrapper.classList.add('code-block-wrapper');
        preElement.parentElement.insertBefore(wrapper, preElement);
        wrapper.appendChild(languageLabel);
        wrapper.appendChild(preElement);
    });

    const markdownInput = document.querySelector('.markdown-input');
    const previewElement = document.querySelector('#markdown-preview');

    if (markdownInput && previewElement) {
        markdownInput.addEventListener('input', () => {
            const markdownContent = markdownInput.value;
            const htmlContent = converter.makeHtml(markdownContent);
            previewElement.innerHTML = htmlContent;

            previewElement.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        });
    }
});
