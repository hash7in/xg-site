/**
 * POST /api/lead —— 官网报价表单落库（Cloudflare Pages Function + D1）
 *
 * 为什么要有它：静态站只有 WhatsApp 预填消息，客户不点发送就没痕迹。
 * 这个函数把「表单填了什么、从哪来」多存一份，晚上由仓库的 growth/leads_pull.py 拉回 SQLite。
 *
 * 绑定（Cloudflare 后台 → Pages → Settings → Functions）：
 *   D1 database  binding = DB     ← schema.sql 已建好表
 *   Secret       LEADS_PULL_TOKEN = <随机串>   ← 拉取用，不写在仓库里
 *
 * 不存 cookie、不存 IP、不存 UA，只存客户自己填的字段 + 来源串（utm / referrer / path）。
 */

const FIELDS = ['feedstock', 'tpd', 'country', 'contact', 'source', 'page'];

function clean(value, max = 200) {
  return String(value ?? '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max);
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ ok: false, error: 'D1 binding DB missing' }, 503);

  let data;
  try {
    data = await request.json();
  } catch {
    return json({ ok: false, error: 'invalid json' }, 400);
  }
  if (typeof data !== 'object' || data === null) return json({ ok: false, error: 'invalid body' }, 400);

  const row = Object.fromEntries(FIELDS.map((k) => [k, clean(data[k])]));
  if (!row.feedstock && !row.country && !row.contact) {
    return json({ ok: false, error: 'empty lead' }, 400);
  }
  const tpd = Number.parseFloat(row.tpd);

  try {
    const res = await env.DB.prepare(
      `insert into leads (created_at, feedstock, tpd, country, contact, source, page, referrer)
       values (?, ?, ?, ?, ?, ?, ?, ?)`,
    ).bind(
      new Date().toISOString(),
      row.feedstock,
      Number.isFinite(tpd) ? tpd : null,
      row.country,
      row.contact,
      row.source,
      row.page,
      clean(request.headers.get('referer'), 300),
    ).run();
    return json({ ok: true, id: res.meta?.last_row_id ?? null });
  } catch (err) {
    return json({ ok: false, error: String(err).slice(0, 200) }, 500);
  }
}

/** GET /api/leads?since=2026-11-01T00:00:00Z —— 给仓库的夜间拉取用，必须带 token。 */
export async function onRequestGet({ request, env }) {
  if (!env.DB) return json({ ok: false, error: 'D1 binding DB missing' }, 503);
  const token = (request.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  if (!env.LEADS_PULL_TOKEN || token !== env.LEADS_PULL_TOKEN) {
    return json({ ok: false, error: 'unauthorized' }, 401);
  }
  const since = clean(new URL(request.url).searchParams.get('since') || '1970-01-01T00:00:00Z', 40);
  const { results } = await env.DB.prepare(
    'select * from leads where created_at >= ? order by id asc limit 500',
  ).bind(since).all();
  return json({ ok: true, leads: results || [] });
}
