from pathlib import Path
import re
import md2mp3

def main():
    text = Path('test_ssml.md').read_text(encoding='utf-8')
    no = md2mp3.MarkdownCleaner.clean_text(text, 'fr', enable_ssml=False)
    yes = md2mp3.MarkdownCleaner.clean_text(text, 'fr', enable_ssml=True)
    Path('_temp_clean_no.txt').write_text(no, encoding='utf-8')
    Path('_temp_clean_yes.txt').write_text(yes, encoding='utf-8')
    report = []
    report.append(f"NO_SSML_HAS_TAGS={bool(re.search(r'<(emphasis|prosody|break)\\\b', no))}")
    report.append(f"YES_SSML_HAS_TAGS={bool(re.search(r'<(emphasis|prosody|break)\\\b', yes))}")
    for label, s in [('NO', no), ('YES', yes)]:
        idx = s.find('cantine')
        if idx != -1:
            start = max(0, idx-40); end = idx+40
            snippet = s[start:end].replace('\n',' ')
            report.append(f"{label}_SNIPPET={snippet}")
    Path('_temp_clean_report.txt').write_text('\n'.join(report), encoding='utf-8')

if __name__ == '__main__':
    main()
