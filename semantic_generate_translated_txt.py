from pathlib import Path
import polib
from antx import transfer
from text_formatting import format_fr


class Po:
    def __init__(self, infile):
        self.infile = Path(infile)
        self.file = polib.pofile(self.infile)
        self._format_fields()

    def format_entries(self):
        entries = []
        for entry in self.file:
            if entry.tcomment:
                text = entry.tcomment
            else:
                text = entry.msgid
                text = text.replace(' ', '').replace('␣', '').replace(' ', ' ')
            text = text.replace('\n', ' ')
            text = "\t" + text  # add tab to indent original
            entries.append((entry.msgstr, text))
        return '\n'.join(['\n'.join(e) for e in entries]), '\n'.join([e[0] for e in entries])

    def write_txt(self):
        orig_trans, trans = self.format_entries()

        bitext = self.infile.parent / (self.infile.stem + '.txt')
        bitext.write_text(orig_trans)

        translation = self.infile.parent / (self.infile.stem + '_translation.txt')
        translation.write_text(trans)

        pars = Path(copy_folder) / (self.infile.stem + '.txt')
        if not pars.is_file():
            pars.write_text(orig_trans)
        else:
            # update file retaining the paragraph delimitations
            pars_old = pars.read_text(encoding='utf-8')
            if pars_old.replace('\n\n\n', '\n') != orig_trans:
                updated = self._update_pars(pars_old, orig_trans)
                pars.write_text(updated)

    @staticmethod
    def _update_pars(source, target):
        pattern = [["pars", "(\n\n\n)"]]
        updated = transfer(source, pattern, target, "txt")
        updated = updated.replace('\n\n\n\n', '\n\n\n')  # hack for a strange behaviour
        return updated

    def _format_fields(self):
        for entry in self.file:
            entry.msgstr = format_fr(entry.msgstr)


if __name__ == '__main__':
    folder = 'sem/fr'
    copy_folder = 'fr/sem_pars'
    for file in Path(folder).glob('*.po'):
        po = Po(file)
        po.write_txt()
