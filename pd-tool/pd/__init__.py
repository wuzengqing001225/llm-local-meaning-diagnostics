"""prior-divergence: locate where a reader's public meaning of a word diverges from a document's meaning.

Pipeline (three commands, see pd.cli):
  draft  -> one meaning-dependent multiple-choice question per meaning-bearing occurrence of a term
  score  -> a local white-box proxy scores each question with and without the document's definition
  gate   -> attach a definition to a passage only where the scored risk is high
"""
__version__ = "0.1.0"
from .io import load_documents, load_glossary, extract_occurrences, read_jsonl, write_jsonl  # noqa: F401
from .score import score_questions  # noqa: F401
from .gate import gate_passages, SCOPE_STATEMENT  # noqa: F401
