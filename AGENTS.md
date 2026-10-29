# xg-site

官网（静态站，自包含）。构建说明见 `README.md`。

## 硬规则

- **改完就推**：任何对官网的修改（文案 `content/`、配图 `assets/src/`、生成器 `build/`、页面生成物）做完 `make site` / `make fast` 后，直接 `git push`，不用问。push 即触发部署。
- 生成物（`index.html`、`en/`、`insights.html`、`*.html`、`sitemap.xml`、`robots.txt`、`assets/css/`、`assets/img/`）跟源码一起提交，别只提交 `build/` 和 `content/`。
- 只用 `git add <具体路径>`；不要 `git add -A`（会把 `.cloudflare/`、`.wrangler/` 缓存带进去）。
- 文案唯一来源是 `content/brochure.yaml`（首页）与 `content/pages.yaml`（技术页 + 资源中心分组）；数字不在这里新编，取自设备配置表与画册。
