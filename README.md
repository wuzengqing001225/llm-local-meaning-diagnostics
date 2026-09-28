# Language Models Cannot Tell When a Definition Is Missing

Code and data for the paper *Language Models Cannot Tell When a Definition Is Missing* (under double-blind review).

The paper studies errors on source-linked questions about locally defined terms. A local 7B proxy ranks other readers' errors
on the same synthetic and contract questions, while source definitions can correct many constructed-task answers. The risk
score also tracks general question difficulty, and a successful definition-allocation policy for new user requests has not
been established. The release keeps those boundaries visible in the paper, data, and tool documentation.

## Contents

| Folder | What it is | Start with |
|---|---|---|
| [`reproduction/`](reproduction/) | Everything needed to recompute the paper's numbers offline: diagnostic questions, model outputs, proxy scores, analysis scripts, the 27-item source review, and the paper itself. No API key, model download or GPU needed. | `reproduction/README.md` |
| [`pd-tool/`](pd-tool/) | An experimental command-line implementation (`pd`) for extracting occurrences, drafting and reviewing questions, scoring a local proxy, and attaching definitions. New-corpus outcomes require their own validation. | `pd-tool/README.md` |

## Quick start

Reproduce the paper's numbers:

```sh
cd reproduction
python -m pip install -r requirements.txt
python verify_release.py        # integrity of every released file
python reproduce.py             # main statistics, compared with frozen expected values
```

Build a risk index for your own documents:

```sh
cd pd-tool
pip install -e .
pd extract --documents documents.jsonl --glossary glossary.jsonl --out terms.jsonl
pd draft   --terms terms.jsonl --out questions.jsonl
pd score   --questions questions.jsonl --out riskmap.jsonl
pd report  --riskmap riskmap.jsonl --out report.html
```

## Data and licences

Code is released under the MIT licence. Each corpus keeps its own licence, described in `reproduction/DATA_CARD.md` and
`reproduction/LICENSE.md`. CUAD is CC BY 4.0. A private operations notebook used during development is not included.

## Citation

See `reproduction/CITATION.cff`.
