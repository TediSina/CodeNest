document.addEventListener('DOMContentLoaded', () => {
    const questionBodyElement = document.querySelector('.question-body p');

    const converter = new showdown.Converter({ tables: true, simplifiedAutoLink: true });
    const markdownContent = questionBodyElement.textContent;
    const htmlContent = converter.makeHtml(markdownContent);

    questionBodyElement.innerHTML = htmlContent;

    document.querySelectorAll('pre code').forEach((block) => {
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
});
