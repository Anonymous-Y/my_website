A Github Pages template for academic websites. This was forked (then detached) by [Stuart Geiger](https://github.com/staeiou) from the [Minimal Mistakes Jekyll Theme](https://mmistakes.github.io/minimal-mistakes/), which is © 2016 Michael Rose and released under the MIT License. See LICENSE.md.

To preview the website locally, run these commands from the repository folder:

```bash
bundle install
bundle exec jekyll serve --livereload --config _config.yml,_config.dev.yml
```

Open http://127.0.0.1:4000 and keep the terminal running. Press Ctrl+C to stop the server.

The development config overrides the production URL so navigation and assets stay on the local server. It also disables analytics and incremental builds so switching configurations rebuilds all page links. Restart the server after changing configuration files.

Use Jekyll's built-in `serve --livereload` command. The old `liveserve` command came from the unmaintained Hawkins plugin, which is incompatible with this project's Jekyll version and causes HTTP 500 errors.

After pulling changes, use `bundle install` to install the versions recorded in `Gemfile.lock`. Use `bundle update` only when intentionally updating dependencies.

The Datasets section lives at `/datasets/`. Add pages describing each dataset to `_datasets/` without a date prefix in the filename; they are listed by `_pages/datasets.html` and published under `/datasets/`. Store dataset downloads in `_datasets/data/<dataset-name>/` and figures in `_datasets/image/<dataset-name>/`. Link to their published paths under `/datasets/data/` and `/datasets/image/`. Jekyll reserves `_data/` for configuration files such as navigation. The old `/data/` and `/attnAI/` addresses redirect to `/datasets/`.

Keep `assets/js/_main.js`, the JavaScript plugins and vendor files, and `package.json` as the inputs for rebuilding `assets/js/main.min.js` with `npm run build:js`. Jekyll compiles `assets/css/main.scss` and its imports in `_sass/` automatically.

The `_site/`, `.jekyll-metadata`, `.jekyll-cache/`, and `.sass-cache/` paths are generated output or caches and should not be committed. Keep `Gemfile.lock` to preserve dependency versions and `LICENSE` for the theme attribution.
