# Contributing

Thank you for helping make power-system concepts easier to learn. Contributions can be corrections, clearer explanations, new worked examples, or complete tutorials.

## Before writing

For a substantial new article, consider opening an issue first. This makes it easier to agree on scope and avoid duplicated work.

A tutorial should:

- state its audience and prerequisites;
- define symbols, units, sign conventions, and modelling assumptions;
- connect the mathematical model to its physical meaning;
- cite primary or authoritative references for nontrivial claims;
- include at least one executable Python example that helps the reader explore the method;
- interpret the code output and suggest a meaningful input for the reader to change; and
- avoid copyrighted figures or text unless their licence permits reuse.

## Local workflow

1. Install the [Quarto CLI](https://quarto.org/docs/get-started/) and [uv](https://docs.astral.sh/uv/).
2. Create a branch from `main`.
3. Copy `templates/article.qmd.template` to `articles/your-topic.qmd`.
4. Run `uv sync --frozen` to install the Python environment.
5. Run `uv run quarto preview` while editing.
6. Run `uv run python scripts/check_tutorial_python.py` to verify the hands-on Python requirement.
7. Run `uv run quarto render` before opening a pull request.

## Python companion requirement

Every tutorial must declare the Python Jupyter engine and include `Python` in its categories:

```yaml
categories: [Your topic, Python]
jupyter: python3
execute:
  echo: true
  warning: false
```

Use an executable Quarto cell rather than a display-only Python fence:

````markdown
```{python}
#| label: lst-your-topic-example
#| code-summary: "Run the worked example"

# Small, reproducible example
```
````

At least one Python cell must be executable; a tutorial whose cells all set `eval: false` does not meet the requirement. Keep examples deterministic, state units and base quantities, print or plot an interpretable result, and explain what the reader should learn by modifying the inputs.

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
- [ ] The tutorial contains an executable, deterministic Python example and interprets its output.
- [ ] New terminology and symbols are defined.
- [ ] Images include useful alternative text.
- [ ] Sources and reused assets have appropriate attribution.
- [ ] The change is focused and the commit history is understandable.
