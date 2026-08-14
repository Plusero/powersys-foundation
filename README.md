# Power Systems Foundation

An open collection of practical tutorials for understanding and analysing electric power systems. Every tutorial pairs its derivation with executable Python so readers can change inputs, rerun the method, and build practical intuition. The website is built with [Quarto](https://quarto.org/) and published with GitHub Pages.

Visit the [Power Systems Foundation website](https://plusero.github.io/powersys-foundation/).

## Preview locally

1. Install the [Quarto CLI](https://quarto.org/docs/get-started/) and [uv](https://docs.astral.sh/uv/).
2. Clone this repository.
3. Install the locked Python environment:

   ```sh
   uv sync --frozen
   ```

4. Start the preview inside that environment:

   ```sh
   uv run quarto preview
   ```

Quarto will render the site and refresh the browser when a source file changes.

## How to run the Python scripts in the tutorials

The tutorial calculations are executable Python cells embedded directly in the `.qmd` files, rather than separate `.py` scripts. Each tutorial declares the Jupyter Python engine in its front matter:

```yaml
jupyter: python3
```

When Quarto previews or renders a tutorial, it starts that Python kernel and executes the cells from top to bottom in the same session. Later cells can therefore use variables and functions created by earlier cells.

First install the [Quarto CLI](https://quarto.org/docs/get-started/) and [`uv`](https://docs.astral.sh/uv/). Then clone the repository, enter its directory, install the locked Python environment, and preview the tutorial:

```sh
git clone https://github.com/Plusero/powersys-foundation.git
cd powersys-foundation
uv sync --frozen
uv run quarto preview articles/newton-raphson-power-flow.qmd
```

Quarto executes the Python cells, displays their results in the rendered page, and refreshes the page after the `.qmd` file is edited and saved. To recalculate an example, change its input values in the `.qmd` file and save it.

For a one-time execution without starting the live preview server, render the tutorial instead:

```sh
uv run quarto render articles/newton-raphson-power-flow.qmd
```

The rendered page is written to `_site/articles/newton-raphson-power-flow.html`. To execute and render every tutorial, omit the file path:

```sh
uv run quarto render
```

The published website is static: it displays outputs calculated during the site build but does not execute Python in the reader's browser. Recalculation therefore requires a local preview or render.

## Hands-on Python guarantee

Every file in `articles/` must use the `python3` Jupyter engine and contain at least one executable Quarto Python cell. Check the whole collection locally with:

```sh
uv run python scripts/check_tutorial_python.py
```

The same check runs in GitHub Actions before the website is rendered, preventing a tutorial without runnable Python from being merged unnoticed.

## Visualizations

Use the tool that matches the type of visual evidence being presented:

| Visualization | Preferred tool | Best use |
|---|---|---|
| Electrical circuits | [Schemdraw](https://schemdraw.readthedocs.io/) | Standards-based circuit schematics and component symbols |
| Process and conceptual flows | [Mermaid](https://mermaid.js.org/) | Flowcharts, sequences, states, and explanatory relationships |
| Network and topology graphs | [Graphviz](https://graphviz.org/) | Automatically laid-out node-and-edge structures |
| Quantitative plots | [Matplotlib](https://matplotlib.org/) | Data, equations, simulations, and numerical comparisons |
| LaTeX-first publications | [Circuitikz](https://ctan.org/pkg/circuitikz) | Publication-quality circuits when LaTeX/PDF is the primary output |

Quarto supports Mermaid and Graphviz directly, but they do not provide standards-based electrical component libraries. Use Schemdraw for circuit diagrams in this HTML-first project and configure IEC-style elements where applicable.

Circuit figures are generated from `scripts/figures/generate_circuit_figures.py` into `articles/figures/generated/`. Treat the Python generator as the source of truth and do not edit generated SVG files by hand. Regenerate them with:

```sh
uv run python scripts/figures/generate_circuit_figures.py
```

Verify that committed figures are current with:

```sh
uv run python scripts/figures/generate_circuit_figures.py --check
```

Commit both the generator changes and regenerated SVG files. This keeps figures reproducible while allowing Quarto to render the site without generating assets during every build.

## Add a tutorial

Copy `templates/article.qmd.template` into `articles/` with a `.qmd` extension, give it a descriptive kebab-case filename, and replace the placeholder content and Python example. The tutorials page discovers article files automatically.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the content expectations and pull-request checklist.

## Deployment

The workflow in `.github/workflows/publish.yml` renders and deploys the site after every push to `main`. In the GitHub repository, select **Settings → Pages → Build and deployment → Source → GitHub Actions** once before the first deployment.

Pull requests render the complete site as a build check but do not deploy it.
