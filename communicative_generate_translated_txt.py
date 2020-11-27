from pathlib import Path
import re
import sys
import shutil
import polib
from antx import transfer
from to_docx import create_total_docx, create_trans_docx
from text_formatting import format_fr
import subprocess


class Po:
    def __init__(self, infile):
        self.infile = Path(infile)
        self.file = polib.pofile(self.infile)
        self._format_fields()
        self.par_marker = '\n\n\n'
        self.trans_pattern = r'(.*?\n\t.*)\n'
        self.trans_delimiter = '\n\t'

    def format_entries(self):
        entries = []
        for entry in self.file:
            text = "\t" + entry.msgid
            entries.append((entry.msgstr, text))

        all = []
        pair_dump = Path('fr/sem_pars/') / (self.infile.stem + '.txt')
        source_sem_pairs = self.parse_txt_dump(pair_dump.read_text(encoding='utf-8'))
        if len(entries) != len(source_sem_pairs):
            exit('source/semantic paragraphs and communicative paragraph have different lengths.\nExiting...')
        sent_num = 1
        for i in range(len(entries)):
            src_sem_pairs = source_sem_pairs[i]
            for j in range(len(src_sem_pairs)):
                pair = src_sem_pairs[j]
                src_sem_pairs[j] = (f'{sent_num}. {pair[0]}', pair[1])
                sent_num += 1
            all.append([entries[i][0], src_sem_pairs])

        all_formatted = ''
        for com, pairs in all:
            pairs = '\n'.join(['\n'.join(['\t' + a, '\t' + b]) for a, b in pairs])
            all_formatted += com + '\n' + pairs + '\n\n'

        orig_trans = '\n'.join(['\n'.join(e) for e in entries])
        trans = '\n\n'.join([e[0] for e in entries]).replace('\n\n\n', '\n\n')
        return orig_trans, trans, all_formatted, all

    def parse_txt_dump(self, dump):
        parsed = []
        for par in dump.strip().split(self.par_marker):
            pairs = re.split(self.trans_pattern, par)
            pairs = [p for p in pairs if p]
            parsed_pairs = []
            for pair in pairs:
                c, s = pair.split(self.trans_delimiter)
                parsed_pairs.append((s, c))
            parsed.append(parsed_pairs)
        return parsed

    def write_txt(self, enforce=False):
        orig_trans, trans, all, data = self.format_entries()

        bitext = self.infile.parent / (self.infile.stem + '.txt')
        if self.is_changed(orig_trans, bitext) or enforce or not bitext.is_file():
            bitext.write_text(orig_trans)

        trans_txt = self.infile.parent / (self.infile.stem + '_translation.txt')
        trans = self._update_translation_pars(trans, trans_txt)
        if self.is_changed(trans, trans_txt) or enforce or not trans_txt.is_file():
            trans_txt.write_text(trans)

            trans_docx = self.infile.parent / (self.infile.stem + '_translation.docx')
            create_trans_docx(trans, trans_docx)

            gen_pdf(trans_docx)

        total = self.infile.parent / (self.infile.stem + '_total.txt')
        if self.is_changed(all, total) or enforce or not total.is_file():
            total.write_text(all)

            total_docx = self.infile.parent / (self.infile.stem + '_total.docx')
            create_total_docx(data, total_docx)

            gen_pdf(total_docx)

    def is_changed(self, new_content, filepath):
        if not filepath.is_file():
            return False
        old_content = filepath.read_text(encoding='utf-8')
        if new_content != old_content:
            return True
        return False

    def _update_translation_pars(self, orig_trans, existing):
        if not existing.is_file():
            return orig_trans
        else:
            # update file retaining the paragraph delimitations
            old_trans = existing.read_text(encoding='utf-8')
            if old_trans.replace('\n\n', '') != orig_trans.replace('\n\n', ''):
                updated = self._update_pars(old_trans, orig_trans)
                return updated
            else:
                return orig_trans

    @staticmethod
    def _update_pars(source, target):
        target = target.replace('\n\n', ' ')
        pattern = [["pars", "(\n\n)"]]
        updated = transfer(source, pattern, target, "txt")
        updated = re.sub(r'([!?”:;…,.»"]+?)([^ \f\v\u202f\u00a0\n!?”:;…,.»"])', r'\1 \2', updated)  # reinserting spaces where needed
        updated = re.sub(r'\n\n/ +', '/\n\n', updated)
        updated = re.sub(r'/ /\n\n([^\n])', r'/\n\n/\1', updated)
        # updated = updated.replace(' /', '/')
        updated = re.sub(r'\n\n” ', '”\n\n', updated)
        updated = updated.replace('\n ', '\n')
        updated = updated.replace(' \n', '\n')
        updated = re.sub(r'([!?”:;…,.»"]+?) —', r'\1\n—', updated)
        updated = updated.replace('\n\n\n', '\n\n')

        return updated

    def _format_fields(self):
        for entry in self.file:
            entry.msgid = format_fr(entry.msgid)
            entry.msgstr = format_fr(entry.msgstr)


LOEXE = shutil.which('libreoffice')


def gen_pdf(file):
    print(f'{file.name}: Generating PDF...')
    docxs = list(file.absolute().parent.glob(f'{file.stem}*.docx'))
    for doc in docxs:
        pdf = doc.parent / (doc.stem + '.pdf')
        if pdf.is_file():
            pdf.unlink()
        subprocess.check_call([LOEXE, '--convert-to', 'pdf', '--outdir', str(doc.parent), str(doc)], stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    """
    arguments structure:
    
    communicative_generate_translated_txt.py filename_stem enforce
        will enforce generation of all output files, even if they exist and if there is no change in the content
    
    communicative_generate_translated_txt.py filename_stem
        will check if output files have different content than new output. skips changes that don't affect content like paragraph boundaries
    
    if "filename_stem" == "all", all files are processed
    
    """

    folder = 'fr/reader'
    to_process = None
    if len(sys.argv) == 1:
        to_process = 'all'
        enforce = False
    elif len(sys.argv) == 2:
        to_process = sys.argv[1]
        enforce = False
    elif len(sys.argv) == 3:
        to_process = sys.argv[1]
        if sys.argv[2] == 'enforce':
            enforce = True
        else:
            enforce = False
    else:
        raise(SyntaxError('not right'))

    if to_process and to_process != 'all':
        file = Path(folder) / (to_process + '.po')
        print(file.name)
        po = Po(file)
        po.write_txt(enforce=enforce)
    else:
        files = sorted(list(Path(folder).glob('*.po')))
        for file in files:
            print('\n' + file.name)
            po = Po(file)
            po.write_txt(enforce=enforce)
