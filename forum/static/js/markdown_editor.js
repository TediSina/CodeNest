document.addEventListener('DOMContentLoaded', () => {
    const openingFencePattern = /^( {0,3})```$/;
    const fencedLinePattern = /^ {0,3}`{3,}/;
    const nextLineClosingFencePattern = /^\r?\n {0,3}`{3,}\s*(?:\r?\n|$)/;

    function isInsideFencedBlock(value, lineStart) {
        return value
            .slice(0, lineStart)
            .split(/\r?\n/)
            .reduce((isInside, line) => {
                return fencedLinePattern.test(line) ? !isInside : isInside;
            }, false);
    }

    function appendClosingFence(textarea, event) {
        if (
            event.inputType !== 'insertText'
            || event.data !== '`'
            || textarea.selectionStart !== textarea.selectionEnd
        ) {
            return;
        }

        const caretPosition = textarea.selectionStart;
        const lineStart = textarea.value.lastIndexOf('\n', caretPosition - 1) + 1;
        const openingFence = textarea.value
            .slice(lineStart, caretPosition)
            .match(openingFencePattern);

        if (!openingFence || isInsideFencedBlock(textarea.value, lineStart)) {
            return;
        }

        const nextLineStart = textarea.value.indexOf('\n', caretPosition);
        const insertAt = nextLineStart === -1 ? textarea.value.length : nextLineStart;

        if (nextLineClosingFencePattern.test(textarea.value.slice(insertAt))) {
            return;
        }

        textarea.setRangeText(
            `\n${openingFence[1]}\`\`\``,
            insertAt,
            insertAt,
            'preserve',
        );
        textarea.setSelectionRange(caretPosition, caretPosition);
    }

    document.querySelectorAll('textarea.markdown-input').forEach((textarea) => {
        textarea.addEventListener('input', (event) => {
            appendClosingFence(textarea, event);
        });
    });
});
