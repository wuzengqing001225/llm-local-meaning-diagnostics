# LaTeX source layout

`paper.tex` contains the ICLR preamble, title, abstract, ordered inputs, bibliography, and appendix switch. The nine numbered main-text sections and the two unnumbered statements are in `section/`. The six numbered appendix sections and their supporting tables are in `appendix/`. Figures remain in `figs/`.

Build from this directory with `latexmk -pdf paper.tex`. The table and stratification-figure generator writes to the new locations with `python rebuild_tables_figures.py`.

The local `iclr2027_conference.sty`, `iclr2027_conference.bst`, `fancyhdr.sty`, `natbib.sty`, and `math_commands.tex` are byte-identical to the files in the supplied ICLR 2027 style archive. The paper uses the submission style without `\iclrfinalcopy`, keeps authors anonymous, has the required AI use statement and a reproducibility statement before references, and places the appendix after references. The main text ends on page 8 of the compiled 23-page PDF, within the style archive's nine-page initial-submission limit.

The source split changes no manuscript text or layout. A pre/post check found identical extracted PDF text and identical rendered pixels on all 23 pages.
