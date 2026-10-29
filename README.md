# Sofia Strukova's website

Live site: https://strukovas.github.io/

The maintained Hugo source is in **`site/`**. GitHub Actions builds and publishes it on every push to `main`. Generated HTML is an artifact of the build; do not edit it directly or copy it back into this repository.

## Edit content

| Change | Source |
| --- | --- |
| Biography, role, affiliations, education, links | `site/content/authors/admin/_index.md` |
| Portrait | `site/content/authors/admin/avatar.jpg` |
| Homepage sections | `site/content/home/` |
| Current research themes | `site/content/home/research.md` |
| Experience | `site/content/home/experience.md` |
| News | `site/content/home/accomplishments.md` |
| Academic service | `site/content/home/academic-service.md` |
| Teaching (within Academic service) | `site/content/home/academic-service.md` |
| Publications | `site/content/publication/<slug>/index.md` |
| BibTeX citation | `site/content/publication/<slug>/cite.bib` |
| Navigation | `site/config/_default/menus.yaml` |
| General settings | `site/config/_default/` |
| Custom styling | `site/assets/scss/custom.scss` |

To add a publication, create a folder with `index.md` and `cite.bib`, following an existing publication. Use a unique slug and the actual publication or posting date. Use `admin` for Sofia's author entry. Set `publication_types: ['2']` for journal articles or `['3']` for preprints. Store a **bare DOI**, for example `10.9781/ijimai.2026.2211`, without `https://doi.org/`; the theme adds the URL. Keep preprints clearly labeled in `publication_short` and the page body.

The homepage shows the six selected publications in the order configured in `site/content/home/publications.md`. Edit that slug list to change the selection or order. The full publication archive remains at `/publication/` and is linked in navigation and below the featured list. Work-in-progress titles are maintained in `site/content/home/work-in-progress.md`; they are separate from published papers and preprints.

## Local preview

Use **Hugo Extended 0.97.3**, matching the existing Wowchemy theme. The theme is committed in `site/_vendor/` so builds do not depend on fetching an old module version. Go is not required for ordinary builds.

```sh
./scripts/preview.sh
```

Open http://127.0.0.1:8000/. Save edits to see them automatically. If Hugo is outside your PATH:

```sh
HUGO_BIN=/absolute/path/to/hugo ./scripts/preview.sh
```

On the configured Mac, the two `.command` launchers in the parent Personal Webpage folder already select the installed Hugo binary and this source checkout. They use ports 8000 and 1313.

## Build and check

```sh
hugo --source site --destination ../build --minify --environment production
python3 scripts/check-site.py build
```

The checks preserve the migrated publication records and homepage content, check citation files and internal resources, reject malformed DOI links and the misspelled site domain, and prevent starter demo pages from being republished.

## Publish

```sh
git add site scripts .github README.md .gitignore
git diff --cached
git commit -m "Update website content"
git push origin main
```

The **Build and publish Hugo site** workflow builds, validates and deploys to GitHub Pages. Failed validation prevents deployment. Pull requests build and validate without publishing. A workflow can also be run manually from Actions. No personal access token or cross-repository deploy key is required.

GitHub Pages must use **Settings → Pages → Source → GitHub Actions**. The workflow retains the existing public website URL.

## Source migration

The older `strukovas/hugo-academic` repository is a historical copy. Its old `public` submodule and Windows Hugo binary are no longer part of publishing. All maintained edits now belong in this repository's `site/` directory.

The migration recovered the current profile, affiliation, biography, experience, news and all 16 publications from the published site, including direct HTML changes made after the older source diverged. Existing publication URLs are preserved. Starter posts, sample talks/projects/slides and placeholder PDFs were removed. Hugo and Wowchemy are deliberately pinned; upgrade them together as a separate change.
