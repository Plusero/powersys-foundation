# Power Systems Foundation

An open collection of practical tutorials for understanding and analysing electric power systems. The website is built with [Quarto](https://quarto.org/) and published with GitHub Pages.

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

## Add a tutorial

Copy `templates/article.qmd.template` into `articles/` with a `.qmd` extension, give it a descriptive kebab-case filename, and replace the placeholder content. The tutorials page discovers article files automatically.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the content expectations and pull-request checklist.

## Deployment

The workflow in `.github/workflows/publish.yml` renders and deploys the site after every push to `main`. In the GitHub repository, select **Settings → Pages → Build and deployment → Source → GitHub Actions** once before the first deployment.

Pull requests render the complete site as a build check but do not deploy it.
