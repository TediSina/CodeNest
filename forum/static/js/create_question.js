const converter = new showdown.Converter({ tables: true });
const input = document.querySelector('.markdown-input');
const preview = document.getElementById('markdown-preview');

function highlightCode() {
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
}

input.addEventListener('input', () => {
    preview.innerHTML = converter.makeHtml(input.value);

    highlightCode();
});
