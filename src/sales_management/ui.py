"""HTML UI router for sales-management."""

from datetime import UTC, datetime
from html import escape

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from sales_management.store import SalesStore

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]


def _default_date(store: SalesStore) -> str:
    records = store.list_records()
    if records:
        return datetime.fromisoformat(records[-1].recorded_at).date().isoformat()
    return datetime.now(UTC).date().isoformat()


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "sales" else ""}" href="{href}">'
        f"{escape(label)}</a>"
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("daily", "日次売上ダッシュボード", "/ui/sales/daily"),
        ("monthly", "月次・年次集計レポート", "/ui/sales/monthly"),
        ("records", "売上計上明細一覧", "/ui/sales/records"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">'
        f"{escape(label)}</a>"
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{ --bg:#f8fafc; --surface:#fff; --navy:#0f172a; --slate:#334155;
      --muted:#64748b; --border:#e2e8f0; --accent:#ea580c; --accent-soft:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--navy); line-height:1.5;
      font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }}
    .topbar {{ background:var(--navy); color:#fff; padding:0 24px; height:54px;
      display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; align-items:center; gap:10px; font-weight:700;
      font-size:15px; white-space:nowrap; }}
    .brand-badge {{ background:var(--accent); color:#fff; padding:2px 8px;
      border-radius:6px; font-size:11px; }}
    .nav-links {{ display:flex; gap:4px; overflow-x:auto; }}
    .nav-pill {{ color:#cbd5e1; text-decoration:none; font-size:12px; font-weight:600;
      padding:6px 10px; border-radius:6px; white-space:nowrap; }}
    .nav-pill.active {{ background:var(--accent); color:#fff; }}
    .subbar {{ background:var(--surface); border-bottom:1px solid var(--border);
      padding:12px 24px; display:flex; align-items:center; justify-content:space-between;
      gap:16px; }}
    .subbar h1 {{ margin:0; font-size:18px; }}
    .subbar .subtitle {{ margin:2px 0 0; font-size:12px; color:var(--muted); }}
    .subtabs {{ display:flex; gap:8px; }}
    .subtab {{ text-decoration:none; color:var(--slate); font-size:13px; font-weight:600;
      padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
    .subtab.active {{ background:var(--accent-soft); color:var(--accent);
      border-color:#fdba74; }}
    .container {{ max-width:1220px; margin:0 auto; padding:20px 24px 28px; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }}
    .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
      padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .kpi-label {{ font-size:12px; color:var(--muted); font-weight:600; }}
    .kpi-value {{ font-size:24px; font-weight:800; margin-top:4px; }}
    .bar-track {{ height:18px; background:#f1f5f9; border-radius:999px; overflow:hidden;
      display:flex; margin:12px 0; }}
    .badge {{ display:inline-block; padding:2px 9px; border-radius:999px;
      font-size:11px; font-weight:700; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:10px 12px; background:#f8fafc; color:var(--muted);
      font-size:12px; border-bottom:1px solid var(--border); }}
    td {{ padding:10px 12px; border-bottom:1px solid var(--border); }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def create_ui_router(store: SalesStore) -> APIRouter:
    """Create FastAPI router providing HTML UI screens for sales-management."""
    router = APIRouter(tags=["ui"])

    @router.get("/ui/sales/daily", response_class=HTMLResponse)
    def daily_sales_page(date: str | None = Query(default=None)) -> str:
        target_date = date or _default_date(store)
        summary = store.summarize(target_date)
        dine_amt = summary.by_channel.get("dine_in", 0)
        take_amt = summary.by_channel.get("takeout", 0)
        total = summary.total_amount
        dine_pct = round(dine_amt / total * 100) if total else 50
        take_pct = 100 - dine_pct if total else 50
        avg_spend = round(total / summary.order_count) if summary.order_count else 0

        body = f"""
        <div class="kpi-grid">
          <div class="card"><div class="kpi-label">対象日 ({escape(target_date)}) 売上</div>
            <div class="kpi-value" style="color:#ea580c">¥{total:,}</div></div>
          <div class="card"><div class="kpi-label">計上注文件数</div>
            <div class="kpi-value">{summary.order_count} 件</div></div>
          <div class="card"><div class="kpi-label">客単価（平均注文額）</div>
            <div class="kpi-value">¥{avg_spend:,}</div></div>
          <div class="card"><div class="kpi-label">店内 / 持ち帰り比率</div>
            <div class="kpi-value">{dine_pct}% / {take_pct}%</div></div>
        </div>
        <div class="card">
          <h2 style="margin:0 0 10px;font-size:16px">
            チャネル別売上構成比（{escape(target_date)}）</h2>
          <div class="bar-track">
            <div style="width:{dine_pct}%;background:#2563eb"></div>
            <div style="width:{take_pct}%;background:#f59e0b"></div>
          </div>
          <div style="display:flex;gap:24px;font-size:13px">
            <span><strong style="color:#2563eb">■ 店内飲食 (dine_in):</strong>
              ¥{dine_amt:,} ({dine_pct}%)</span>
            <span><strong style="color:#d97706">■ 持ち帰り (takeout):</strong>
              ¥{take_amt:,} ({take_pct}%)</span>
          </div>
        </div>
        """
        return _render_shell(
            title="売上管理 › 日次売上ダッシュボード",
            subtitle="会計管理から計上された日次の総売上・注文件数・チャネル別内訳を表示します",
            active_subtab="daily",
            body_html=body,
        )

    @router.get("/ui/sales/monthly", response_class=HTMLResponse)
    def monthly_sales_page(month: str | None = Query(default=None)) -> str:
        target_date = _default_date(store)
        target_month = month or target_date[:7]
        target_year = target_month[:4]
        m_sum = store.summarize(target_month)
        y_sum = store.summarize(target_year)

        body = f"""
        <div class="grid-2">
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">
              月次売上レポート（{escape(target_month)}）</h2>
            <div style="font-size:28px;font-weight:800;color:#ea580c;margin-bottom:10px">
              ¥{m_sum.total_amount:,}</div>
            <table>
              <tbody>
                <tr><th>集計期間</th><td>{escape(m_sum.period)}</td></tr>
                <tr><th>注文件数</th><td>{m_sum.order_count} 件</td></tr>
                <tr><th>店内売上</th><td>¥{m_sum.by_channel.get("dine_in", 0):,}</td></tr>
                <tr><th>持ち帰り売上</th><td>¥{m_sum.by_channel.get("takeout", 0):,}</td></tr>
              </tbody>
            </table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">
              年次累計レポート（{escape(target_year)}）</h2>
            <div style="font-size:28px;font-weight:800;color:#0f172a;margin-bottom:10px">
              ¥{y_sum.total_amount:,}</div>
            <table>
              <tbody>
                <tr><th>集計年</th><td>{escape(y_sum.period)} 年</td></tr>
                <tr><th>累計注文件数</th><td>{y_sum.order_count} 件</td></tr>
                <tr><th>店内累計</th><td>¥{y_sum.by_channel.get("dine_in", 0):,}</td></tr>
                <tr><th>持ち帰り累計</th><td>¥{y_sum.by_channel.get("takeout", 0):,}</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        """
        return _render_shell(
            title="売上管理 › 月次・年次売上集計レポート",
            subtitle="月間および年間の売上推移とチャネル別貢献度を確認します",
            active_subtab="monthly",
            body_html=body,
        )

    @router.get("/ui/sales/records", response_class=HTMLResponse)
    def sales_records_page() -> str:
        records = store.list_records()
        rows = []
        for r in records:
            ch_badge = (
                '<span class="badge" style="background:#dbeafe;color:#1e40af">店内</span>'
                if r.channel == "dine_in"
                else '<span class="badge" style="background:#fef3c7;color:#92400e">持ち帰り</span>'
            )
            rows.append(
                f"<tr><td><code>{escape(r.id[:12])}</code></td>"
                f"<td><code>{escape(r.order_id)}</code></td>"
                f"<td><code>{escape(r.payment_id)}</code></td>"
                f"<td>{ch_badge}</td>"
                f"<td><strong>¥{r.amount:,}</strong></td>"
                f"<td>{escape(r.recorded_at)}</td></tr>"
            )
        rows_html = "".join(rows) or (
            '<tr><td colspan="6" style="text-align:center;color:#64748b">'
            "売上計上レコードはまだありません。</td></tr>"
        )
        body = f"""
        <div class="card">
          <h2 style="margin:0 0 12px;font-size:16px">売上計上明細一覧（I-4 重複排除保護済み）</h2>
          <table>
            <thead><tr><th>売上ID</th><th>注文ID</th><th>決済ID</th>
              <th>チャネル</th><th>金額</th><th>計上日時</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        return _render_shell(
            title="売上管理 › 売上計上明細一覧",
            subtitle="会計管理から供給された重複なしの売上実績レコード明細を確認します",
            active_subtab="records",
            body_html=body,
        )

    return router
