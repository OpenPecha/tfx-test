from pathlib import Path
import re
import sys
import polib
from text_formatting import format_fr


class Po:
    def __init__(self):
        self.par_marker = '\n\n\n'
        self.trans_pattern = r'(.*?\n\t.*)\n'
        self.trans_delimiter = '\n\t'
        self.file = polib.POFile()
        self.file.metadata = {
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

    def _create_entry(self, msgid, msgstr="", msgctxt=None, comment=None, tcomment=None):
        entry = polib.POEntry(
            msgid=msgid,
            msgstr=msgstr,
            msgctxt=msgctxt,
            comment=comment,
            tcomment=tcomment
        )
        self.file.append(entry)

    def write_to_file(self, filename):
        self.file.save(filename)

    def dump_po_entries(self, dump, origin):
        sent_num = 0
        for num, par in enumerate(dump.strip().split(self.par_marker)):
            pairs = re.split(self.trans_pattern, par)
            pairs = [p for p in pairs if p]
            source = []
            comment = []
            for pair in pairs:
                s, c = pair.split(self.trans_delimiter)
                source.append(s)
                comment.append(f' {sent_num+1}. {c}')
                sent_num += 1
            source = ' '.join(source)
            source = format_fr(source)
            comment = ' '.join(comment)
            self._create_entry(msgid=source, msgctxt=f'line {num + 1}, {origin}', tcomment=comment)

    def txt_to_po(self, filename):
        lines = filename.read_text(encoding='utf-8')
        if self.par_marker not in lines:
            print(' — has no paragraphs. passing...')
            return
        else:
            print('')

        self.dump_po_entries(lines, filename.name)
        self.write_to_file((filename.parent / (filename.stem + ".po")))


if __name__ == '__main__':
    folder = 'fr/sem_pars'
    if len(sys.argv) > 1:
        stem = sys.argv[1]
        file = Path(folder) / (stem + '.txt')
        print(file, end='')
        po = Po()
        po.txt_to_po(file)
    else:
        files = sorted(list(Path(folder).glob('*.txt')))
        for file in files:
            print(file, end='')
            po = Po()
            po.txt_to_po(file)
