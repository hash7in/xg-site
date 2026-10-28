# 官网静态站（自包含）：文案 content/、配图 assets/src/、生成器 build/
# 依赖：pip install -r requirements.txt（或 uv run --with-requirements requirements.txt）
# 依赖由 uv 现装（已 pip install -r requirements.txt 的话可 PY=python3 覆盖）
PY ?= uv run --with-requirements requirements.txt python

site:
	$(PY) build/site.py

# 只改了文案时用（跳过图片重压）
fast:
	$(PY) build/site.py --fast

preview:
	$(PY) -m http.server 8080 -d .

.PHONY: site fast preview
