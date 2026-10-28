# 官网静态站：页面骨架/样式在本仓 build/，文案与配图在生成仓 ~/liejie
LJ ?= $(HOME)/liejie

site:
	uv run --project $(LJ) python build/site.py

# 只改了文案时用（跳过图片重压）
fast:
	uv run --project $(LJ) python build/site.py --fast

preview:
	uv run --project $(LJ) python -m http.server 8080 -d .

.PHONY: site fast preview
