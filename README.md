# XG 官网（静态站）

XG 环保装备官网：中英两页纯静态站点，无 Node、无构建依赖。

- `index.html` — 中文首页
- `en/index.html` — English
- `assets/` — 图片 / 字体 / logo / site.css

## 怎么更新

**不要在这里手改**：文案与配图在生成仓 `~/liejie`。

```bash
cd ~/liejie && make site     # 重新生成到本目录（SITE_DIR 可改指向）
cd ~/xg-site && git add -A && git commit -m "site: 更新文案" && git push
```

## 部署

任意静态托管（nginx / 对象存储 / GitHub Pages）直接指向本目录根即可。
