#!/usr/bin/env python3
"""官网 —— 一份文案数据，生成中英两个静态页面。

用法（在本仓根目录）:
    python build/site.py            # 出 index.html + en/index.html
    python build/site.py --fast     # 跳过图片重新压缩（只改文案时用）

本仓自带（自包含，clone 即可构建）:
    content/brochure.yaml      画册/官网站共用文案（中英对照，唯一需要改的文件；
                               画册 PDF 在 ~/liejie，反向读这份）
    brand.yaml                 公司英文名 / 色值 / 工厂事实
    assets/src/                配图原件（构建时压到 ≤1400px → assets/img/）
    assets/fonts/ · assets/brand/
    build/site.html + style-site.css

产物是纯静态站点：直接丢给 nginx / GitHub Pages / 对象存储即可，不需要 Node。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = Path(__file__).resolve().parent        # build/
WEB = HERE.parent                             # 仓根 = 站点根
CONTENT = WEB / "content" / "brochure.yaml"
PAGES = WEB / "content" / "pages.yaml"
SRC_IMG = WEB / "assets" / "src"
BRAND = WEB / "brand.yaml"

IMAGES = [
    "cover-kiln.jpg", "cover-hero.jpg", "continuous-line.jpg", "hall-lines.jpg", "plant.jpg", "workshop-lead.jpg", "ship-reactor.jpg", "drums-pair.jpg",
    "r-batch.jpg", "r-hotskid.jpg", "r-continuous.jpg", "r-distill.jpg", "r-carbon.jpg",
    "process.jpg", "oil-pour.jpg", "carbon-black.jpg", "samples-jars.jpg",
    "cert-iso9001.jpg", "cert-iso14001.jpg", "cert-ce.jpg", "cert-export.jpg", "cert-patent.jpg",
]

FONTS = [
    ("HarmonyOS Sans SC", 400, "harmonyos-sans-sc-400-normal.woff2"),
    ("HarmonyOS Sans SC", 700, "harmonyos-sans-sc-700-normal.woff2"),
    ("Barlow", 400, "barlow-latin-400-normal.woff2"),
    ("Barlow", 500, "barlow-latin-500-normal.woff2"),
    ("Barlow", 600, "barlow-latin-600-normal.woff2"),
    ("Barlow", 700, "barlow-latin-700-normal.woff2"),
    ("IBM Plex Mono", 400, "ibm-plex-mono-latin-400-normal.woff2"),
]

META = {
    "zh": {
        "out": "index.html",
        "lang": "zh-CN",
        "title": "XG 环保装备 · 废轮胎/塑料热解、废油蒸馏、生物质炭化成套装备",
        "desc": "XG 环保装备：裂解、蒸馏、炭化三类设备同厂设计制造安装，出口 30 多个国家，"
                "从环评协助到出油与油品销路的一站式交付。",
    },
    "en": {
        "out": "en/index.html",
        "lang": "en",
        "title": "XG — Pyrolysis, Distillation & Carbonization Plants",
        "desc": "XG designs, builds and commissions pyrolysis, distillation and "
                "carbonization plants for waste tyres, plastics, waste oil and biomass — 30+ countries.",
    },
}


def optimise_images(force: bool) -> dict[str, tuple[int, int]]:
    """图片压到 ≤1400px 宽、JPEG q82；已经处理过就跳过。返回 {文件名: (宽, 高)}，写进 <img> 防抖动。"""
    from PIL import Image

    dst = WEB / "assets" / "img"
    dst.mkdir(parents=True, exist_ok=True)
    dims: dict[str, tuple[int, int]] = {}
    for name in IMAGES:
        src, out = SRC_IMG / name, dst / name
        if out.exists() and not force and out.stat().st_mtime >= src.stat().st_mtime:
            continue
        im = Image.open(src).convert("RGB")
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(out, "JPEG", quality=82, optimize=True, progressive=True)

    for name in IMAGES:
        with Image.open(dst / name) as im:
            dims[name] = im.size
    return dims


def font_css() -> str:
    rules = []
    for family, weight, fname in FONTS:
        if not (WEB / "assets" / "fonts" / fname).exists():
            continue
        rules.append(
            f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:normal;'
            f'font-display:swap;src:url(../fonts/{fname}) format("woff2");}}'
        )
    return "\n".join(rules)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成官网静态页面")
    ap.add_argument("--fast", action="store_true", help="跳过图片重新压缩")
    args = ap.parse_args()

    content = yaml.safe_load(CONTENT.read_text(encoding="utf-8")) or {}
    brand = yaml.safe_load(BRAND.read_text(encoding="utf-8")) or {}

    dims = optimise_images(force=not args.fast)

    css = (HERE / "style-site.css").read_text(encoding="utf-8").replace(
        "/*@FONTS@*/", font_css()
    )
    (WEB / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (WEB / "assets" / "css" / "site.css").write_text(css, encoding="utf-8")

    env = Environment(
        loader=FileSystemLoader(str(HERE)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template("site.html")
    page_tpl = env.get_template("page.html")
    origin = str(brand.get("website") or "").rstrip("/")
    pages = (yaml.safe_load(PAGES.read_text(encoding="utf-8")) or {}).get("pages") or []

    def url(path: str) -> str:
        path = "/" + path.lstrip("/")
        return f"{origin}{path}" if origin else path

    def href(lang: str, slug: str | None = None) -> str:
        if slug is None:
            rel = "en/index.html" if lang == "en" else "index.html"
        else:
            rel = f"en/{slug}.html" if lang == "en" else f"{slug}.html"
        return url(rel)

    line_pages = {p["line"]: p["slug"] for p in pages if p.get("line")}
    locs = [href("zh"), href("en")]

    for lang in ("zh", "en"):
        root = ".." if lang == "en" else "."
        guides = [
            {
                "href": f"{p['slug']}.html",
                "title": p["title"],
                "title_en": p["title_en"],
                "slug": p["slug"],
                "line": p.get("line"),
            }
            for p in pages
        ]
        out = WEB / META[lang]["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            tpl.render(
                c=content,
                brand=brand,
                lang=lang,
                meta=META[lang],
                dims=dims,
                root=root,
                guides=guides,
                line_pages=line_pages,
                canonical=href(lang),
                href_zh=href("zh"),
                href_en=href("en"),
            ) + "\n",
            encoding="utf-8",
        )
        print(f"✓ {out}")

        for page in pages:
            rel_out = f"en/{page['slug']}.html" if lang == "en" else f"{page['slug']}.html"
            others = [g for g in guides if g["slug"] != page["slug"]][:3]
            dest = WEB / rel_out
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(
                page_tpl.render(
                    c=content,
                    brand=brand,
                    lang=lang,
                    page=page,
                    guides=guides,
                    related=others,
                    dims=dims,
                    root=root,
                    meta={
                        "lang": META[lang]["lang"],
                        "title": page["title_en"] if lang == "en" else page["title"],
                        "desc": page["desc_en"] if lang == "en" else page["desc"],
                    },
                    canonical=href(lang, page["slug"]),
                    href_zh=href("zh", page["slug"]),
                    href_en=href("en", page["slug"]),
                    alt=f"../{page['slug']}.html" if lang == "en" else f"en/{page['slug']}.html",
                ) + "\n",
                encoding="utf-8",
            )
            if lang == "zh":
                locs.append(href("zh", page["slug"]))
                locs.append(href("en", page["slug"]))
            print(f"✓ {dest}")

    sm_rows = "\n".join(
        f"  <url><loc>{loc}</loc></url>" for loc in locs
    )
    (WEB / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sm_rows}\n</urlset>\n",
        encoding="utf-8",
    )
    sm = f"{origin}/sitemap.xml" if origin else "/sitemap.xml"
    (WEB / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {sm}\n",
        encoding="utf-8",
    )
    if not origin:
        print("! brand.yaml website 为空：sitemap 用站内路径，填上域名后重跑才是绝对地址")
    print("✓ sitemap.xml  robots.txt")

    size = sum(f.stat().st_size for f in WEB.rglob("*") if f.is_file() and ".git" not in f.parts) / 1024 / 1024
    print(f"✓ {WEB} 共 {size:.1f} MB（图片 {len(IMAGES)} 张）")
    print(f"  预览：python -m http.server 8080 -d {WEB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
