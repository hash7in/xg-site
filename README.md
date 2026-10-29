# XG 官网（静态站）

XG 环保装备官网：中英两页纯静态站点，无 Node、无构建依赖。

- `index.html` — 中文首页
- `en/index.html` — English
- `content/brochure.yaml` — 首页文案（画册 PDF 也读这份）
- `content/pages.yaml` — 常青技术页（中英各一份静态 HTML，不是博客）+ 分组与资源中心的页头文案
- `insights.html` · `en/insights.html` — 资源中心：上面全部技术页的索引（卡片式，按设备线 / 产出 / 案例排）
- `assets/src/` — 配图原件（构建时压到 ≤1400px）
- `assets/img/` · `assets/css/` · `assets/fonts/` · `assets/brand/` — 生成物/内嵌资源
- `build/` — 生成器：`site.py` + `site.html`（首页）+ `page.html`（技术页）+ `insights.html`（资源中心）+ `style-site.css`
- `brand.yaml` — 公司名/色值（从 `~/liejie` 同步过来）

## 怎么更新

文案 → `content/brochure.yaml`；配图 → `assets/src/`；页面骨架/样式 → `build/`。
本仓自包含，`pip install -r requirements.txt` 后 `make site` 即可，不依赖 `~/liejie`。
（`~/liejie` 的 PDF 画册反向读本仓的文案与配图，所以文案改这里一处就够。）

```bash
cd ~/xg-site
make site                 # 重新生成
make preview              # http://localhost:8080 看效果
git add -A && git commit -m "site: 更新文案" && git push
```

## 部署

任意静态托管（nginx / 对象存储 / GitHub Pages）直接指向本目录根即可。
