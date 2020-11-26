from pathlib import Path
import re
import sys
from uuid import uuid4
import polib
from antx import transfer
from botok import Text


class Po:
    def __init__(self):
        self.transfer = Transfer()
        self.file = polib.POFile()
        self.file.metadata = {
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

    def _create_entry(self, msgid, msgstr="", msgctxt=None, comment=None, tcomment=None):
        """

        :param msgid: string, the entry msgid.
        :param msgstr: string, the entry msgstr.
        :param msgctxt: string, the entry context.
        :param comment: string, the entry comment.
        :param tcomment: string, the entry translator comment.
        """
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

    def lines_to_entries(self, dump, po_file):
        lines = self.transfer.generate_entries(dump, po_file)
        for num, l in enumerate(lines):
            line, ctxt = l
            no_notes = self.remove_peydurma_notes(line)
            if no_notes == "":
                no_notes, line = line, no_notes
            no_notes = re.sub('\[.+?\]', '', no_notes)
            # segment
            t = Text(no_notes)
            no_notes = t.tokenize_words_raw_text
            # format tokens
            no_notes = re.sub('([^།་_]) ([^_།་])', '\g<1>␣\g<2>', no_notes)   # affixed particles
            no_notes = re.sub('_', ' ', no_notes)   # spaces
            self._create_entry(msgid=no_notes, msgctxt=ctxt, tcomment=line)

    def txt_to_po(self, filename):
        lines = filename.read_text(encoding='utf-8')
        outfile = filename.parent / (filename.stem + ".po")

        self.lines_to_entries(lines, outfile)
        self.write_to_file(outfile)

    @staticmethod
    def remove_pagination(line):
        note = re.split(r'(\[.*?\])', line)
        if len(note) > 1:
            return ''.join([a for a in note if not a.startswith('\[')])
        else:
            return ""

    @staticmethod
    def remove_peydurma_notes(line):
        note = re.split(r'(<.*?>)', line)
        if len(note) > 1:
            return ''.join([a for a in note if not a.startswith('<')]).replace(':', '')
        else:
            return ""


class Transfer:
    """
    limitation : in case a line is split on two lines in the updated .txt, it will keep
    the same uuid on the second line and only add a new uuid on the first line.
    """
    def __init__(self):
        self.transfer = transfer

    def generate_entries(self, dump, po_file):
        if po_file.is_file():
            dump = self.extract_entries(dump, po_file)

        updated = self.add_missing_uuids(dump)

        entries = []
        for line in updated.strip().split('\n'):
            line = line.strip()
            line = self.remove_extra_uuid(line)
            txt, ctxt = line[:-1].split('—')
            entries.append([txt, ctxt])
        return entries

    def extract_entries(self, dump, po_file):
        po_file = polib.pofile(po_file)
        po_entries = []
        for p in po_file:
            if p.tcomment:
                line = p.tcomment
            else:
                line = p.msgid.replace(' ', '').replace(' ', ' ')
            po_entries.append([line, p.msgctxt])
        po_dump = '\n'.join([''.join((a, f'—{b}—')) for a, b in po_entries])
        pattern = [['uuid', '(—.+?—)']]
        transfered = self.transfer(po_dump, pattern, dump, 'txt')
        return transfered

    def add_missing_uuids(self, dump):
        lines = dump.strip().split('\n')
        for num, l in enumerate(lines):
            l = l.strip()
            if not l.endswith('—'):
                lines[num] = l + f'—{self.get_unique_id()}—'
        return '\n'.join(lines)

    @staticmethod
    def remove_extra_uuid(line):
        if line.count('—') > 2:
            idx1 = line.find('—')
            idx2 = line.find('—', idx1+1)
            return (line[:idx1] + line[idx2+1:]).strip()

        else:
            return line

    def get_unique_id(self):
        return uuid4().hex


if __name__ == '__main__':
    folder = 'sem/bo/'
    if len(sys.argv) > 1:
        stem = sys.argv[1]
        file = Path(folder) / (stem + '.txt')
        print(file)
        po = Po()
        po.txt_to_po(file)
    else:
        files = sorted(list(Path(folder).glob('*.txt')))
        for file in files:
            print(file)
            po = Po()
            po.txt_to_po(file)
