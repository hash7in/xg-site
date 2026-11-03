-- 官网报价表单落库（Cloudflare D1）。建库后执行一次：
--   wrangler d1 execute xg-leads --remote --file schema.sql
create table if not exists leads (
  id         integer primary key autoincrement,
  created_at text not null,
  feedstock  text default '',
  tpd        real,
  country    text default '',
  contact    text default '',
  source     text default '',
  page       text default '',
  referrer   text default ''
);
create index if not exists idx_leads_created on leads(created_at);
