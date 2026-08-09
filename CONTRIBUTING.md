# Contributing

Thank you for helping make power-system concepts easier to learn. Contributions can be corrections, clearer explanations, new worked examples, or complete tutorials.

## Before writing

For a substantial new article, consider opening an issue first. This makes it easier to agree on scope and avoid duplicated work.

A tutorial should:

- state its audience and prerequisites;
- define symbols, units, sign conventions, and modelling assumptions;
- connect the mathematical model to its physical meaning;
- cite primary or authoritative references for nontrivial claims;
- use reproducible code when numerical results are presented; and
- avoid copyrighted figures or text unless their licence permits reuse.

## Local workflow

1. Install the [Quarto CLI](https://quarto.org/docs/get-started/) and [uv](https://docs.astral.sh/uv/).
2. Create a branch from `main`.
3. Copy `templates/article.qmd.template` to `articles/your-topic.qmd`.
4. Run `uv sync --frozen` to install the Python environment.
5. Run `uv run quarto preview` while editing.
6. Run `uv run quarto render` before opening a pull request.

Use `$...$` for inline equations and `$$...$$` for display equations. Labels beginning with `eq-`, `fig-`, `tbl-`, and `sec-` enable Quarto cross-references, for example:

```markdown
Equation @eq-ohm gives the branch relation.

$$
\mathbf{i} = \mathbf{Y}\mathbf{v}.
$$ {#eq-ohm}
```

Add bibliographic entries to `references.bib` and cite them with Pandoc syntax such as `[@citation-key]`.

## Pull-request checklist

- [ ] The site builds successfully with `quarto render`.
- [ ] Equations, figures, tables, and references render correctly.
- [ ] New terminology and symbols are defined.
- [ ] Images include useful alternative text.
- [ ] Sources and reused assets have appropriate attribution.
- [ ] The change is focused and the commit history is understandable.
