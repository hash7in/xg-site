# XG 官网（静态站）

XG 环保装备官网：中英两页纯静态站点，无 Node、无构建依赖。

- `index.html` — 中文首页
- `en/index.html` — English
- `assets/` — 图片 / 字体 / logo / site.css（生成物）
- `build/` — 生成器：`site.py` + `site.html` + `style-site.css`

## 怎么更新

页面骨架/样式改本仓 `build/`；**文案与配图不在这里**，在生成仓 `~/liejie`：
`content/zh/brochure.yaml`（与 PDF 画册共用）、`assets/images/brochure/`、`brand.yaml`。

```bash
cd ~/xg-site
make site                 # 重新生成（读 ~/liejie，LJ=... 可改指向）
make preview              # http://localhost:8080 看效果
git add -A && git commit -m "site: 更新文案" && git push
```

## 部署

任意静态托管（nginx / 对象存储 / GitHub Pages）直接指向本目录根即可。
