# xg-site

官网（静态站，**只读下游**）。构建说明见 `README.md`。

## 内容真源在 liejie 仓

- 文案 `content/brochure.yaml`、配图 `assets/src/` 的**真源在 `~/liejie`**（`content/brochure.yaml` + `assets/src/`）。
- 不要在这里改这两样，会被 `make site` 覆盖。改内容永远 `cd ~/liejie`。
- 上线：`cd ~/liejie && make deploy`（同步内容 → 本仓 `make site` → `wrangler pages deploy`）。
- 本仓只保留：生成器 `build/`、站点专属文案 `content/pages.yaml`、`brand.yaml`、字体/logo、生成物、Pages Functions。

## 硬规则

- 生成物（`index.html`、`en/`、`insights.html`、`*.html`、`sitemap.xml`、`robots.txt`、`assets/css/`、`assets/img/`）跟源码一起提交，别只提交 `build/`。
- 只用 `git add <具体路径>`；不要 `git add -A`（会把 `.cloudflare/`、`.wrangler/` 缓存带进去）。
- 数字不在这里新编，取自设备配置表与画册。
