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
