
### Overall:

action:
 - translate a tibetan text

input: 
 - `.txt` of the text to translate

output: 2 translated files
 - translation: only contains the communicative version 
 - total: contains tibetan + literal version + communicative version

### 1. semantic translation
- 1.0 Overall:
    - input: [`sem/bo/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/bo/11.txt)
    - output:
        - actual:
            - [`sem/fr/*_translation.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/fr/11_translation.txt) (target) semantic translation. for reference
        - others:
            - [`sem/fr/*.txt`]() (source + target) for reference
            - [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/fr/11.txt) (source + target) for communicative translation. base for paragraph segmentation

- 1.1 Before Tx (Transifex)
    - reinsert peydurma notes inline\
    - segment in sentences\
        [`sem/bo/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/bo/11.txt)\
        manually segment in sentences (guidelines as described by 84 000).
    - 1.1.2 generate `.po` to upload to Tx
        - script: [`semantic_generate_po.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/semantic_generate_po.py)
        - input: [`sem/bo/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/bo/11.txt) (processes whole folder)
        - output: [`sem/bo/*.po`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/bo/11.po)
    - 1.1.3 push output to repo (Tx knows where to find its input)

- 1.2 translate in Tx
    - sentence segmentation update LOOP:
        - translate
        - update segmentation
            - manually modify segmentation
            - generate `.po`: see 1.1.2
            - push: see 1.1.3
        - REPEAT
        
    - Tx commits completed files in [`sem/fr/*.po`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/fr/11.po)

- 1.3 process `.po` received from Tx
    - Tx pushes completed files to repo
    - generate output :
        - script: `semantic_generate_translated_txt.py`
        - input: `sem/fr/*.po` (processes whole folder)
        - output:
            - a. translation + source. 2 copies:
                - [`sem/fr/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/fr/11.txt) (for reference only)
                - [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt) (base of paragraph segmentation)
            - b.  translation only: [`sem/fr/*_translation.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/sem/fr/11_translation.txt) (for reference only)

### 2. communicative translation
- 2.0 Overall
    - input: [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt)
    - output:
        - actual:
            - [`fr/reader/*_total.txt+docx+pdf`](https://github.com/OpenPecha/tfx-test/tree/tfx-workflow/fr/reader) (bo + semantic + communicative)
            - [`fr/reader/*_translation.txt+docx+pdf`](https://github.com/OpenPecha/tfx-test/tree/tfx-workflow/fr/reader) (communicative)
        - others:
            - [`fr/reader/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11.txt) (semantic + communicative) for DocFetcher

- 2.1 Before Tx
    - 2.1.1 segment in paragraphs:\
        insert two empty lines at paragraph boundaries
    - 2.1.2 generate `.po` to upload to Tx
        - script: [`communicative_generate_po.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/communicative_generate_po.py)
        - input: [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt)
        - output: [`fr/sem_pars/*.po`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.po)
    - 2.1.3 push output to repo (Tx knows where to find its input)
    
- 2.2 translate in Tx
    - 2.2.1 semantic translation update LOOP:
        - translate (use DocFetcher to leverage finished files)
        - modify LOOP:
            - open semantic segment (in Tx)
            - modify translation (in Tx)
            - REPEAT
        - propagate modifs:
            - locally pull modifs found in Tx commits
            - in semantic translation + segmentation basis: [`semantic_generate_translated_txt.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/semantic_generate_translated_txt.py) (see 1.1.2)
            - generate `.po` to upload to Tx: [`communicative_generate_po.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/communicative_generate_po.py) (see 2.1.2)
            - push to repo (see 2.1.3)
        - if already translated:
            - retrieve it from the suggestions
            - check it's ok and save it
        - REPEAT
    
    - 2.2.2 paragraph segmentation update LOOP:
        - translate
        - manually modify segmentation in [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt)
        - generate `.po` to upload to Tx: [`communicative_generate_po.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/communicative_generate_po.py) (see 2.1.2)
        - push to repo (see 2.1.3)
        - REPEAT
    
    - Tx commits completed files in [`fr/reader/*.po`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11.po)

- 2.3 Process `.po` received from Tx
    - 2.3.1 First run (the paragraphs are not right in the `translation` output files)
        - script: [`communicative_generate_translated_txt.py`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/communicative_generate_translated_txt.py) (see script for arguments)
        - input:
            - [`fr/reader/*.po`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11.po) from Tx
            - [`fr/sem_pars/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt) for source/semantic pairs (for total output files)
        - output:
            - a. translation files: [`fr/reader/*_translation.txt+docx+pdf`](https://github.com/OpenPecha/tfx-test/tree/tfx-workflow/fr/reader)
            - b. total files: [`fr/reader/*_total.txt+docx+pdf`](https://github.com/OpenPecha/tfx-test/tree/tfx-workflow/fr/reader) DocFetcher is given [`fr/reader/*_total.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11_total.txt) to index using filters
            - c. [`fr/reader/*.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11.txt) (semantic + communicative)
     
    - 2.3.2 paragraph adjustment run
        - adjust paragraph in [`fr/reader/*_translation.txt`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/reader/11_translation.txt) (compare with [initial paragraph segmentation](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt#L4-L17))
        - rerun 2.3.1
    
    - 2.3.3 communicative translation adjustment LOOP
        - open [`fr/reader/*_translation.pdf`](https://github.com/OpenPecha/tfx-test/blob/tfx-workflow/fr/sem_pars/11.txt#L4-L17) (first time)
        - read until you find something to change\
            (having a static pdf is similar to having a printed page. errors are easier to spot)
        - adjust in Tx:
            - in Tx, find the communicative segment to modify
            - make adjustment
            - if this adjustment may need to be done over many files:
                - open search window for all files
                - search
                - adjust all segments
        - locally pull Tx commits with adjustments
        - rerun 2.3.1
        - check the pdf
        - REPEAT

### 3. Integrating feedback
- feedback on the semantic translation: 1.2 onwards
    - adjust semantic translation
    - generate semantic output
    - generate `.po` to upload on Tx (communicative translation)
    - retrieve previous translation from TM in Tx or from DocFetcher + adjust it
    - generate communicative output in 2.3

- feedback on the communicative translation:
    - modify on Tx
    - 2.3 onwards to generate output

- feedback on the paragraph segmentation: from 2.2.2 onwards
    - adjust paragraph segmentation
    - adjust communicative versions in Tx
    - generate output files

### notes
- Tx is the single source of truth for the translators
- modifications are never made in the output files, .docx or .txt files
- history of project is consulted in github
- history of a segment is stored in Tx (as long as the source of the segment is not modified)
