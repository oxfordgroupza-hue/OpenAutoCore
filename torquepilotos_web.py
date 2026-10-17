import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TorquePilotOS",
    description="Browser-based workshop management platform foundation",
    version="0.1.0",
)

# Same-origin UI and API are served by this application. CORS is intentionally
# not opened broadly; configure explicit origins if a separate frontend is added.
@app.get("/health")
def health():
    return {"status": "ok", "product": "TorquePilotOS", "version": "0.1.0"}

@app.get("/api/status")
def api_status():
    return {
        "product": "TorquePilotOS",
        "flagship": "TorquePilot Workshop",
        "stage": "foundation",
        "database_configured": all(
            os.getenv(key)
            for key in ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_NAME")
        ),
        "notice": "Workshop modules are not connected yet.",
    }

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101820">
  <title>TorquePilotOS | TorquePilot Workshop</title>
  <style>
    :root{color-scheme:dark;--bg:#0b1117;--panel:#121c25;--panel2:#17232e;--line:#283744;--text:#edf3f7;--muted:#93a5b3;--accent:#f5a623;--green:#72d6a1}
    *{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 90% 0%,#1c2b36 0,transparent 38%),var(--bg);color:var(--text);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
    .shell{max-width:1240px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;align-items:center;gap:18px;border-bottom:1px solid var(--line);padding-bottom:22px}
    .brand{display:flex;align-items:center;gap:13px}.mark{width:44px;height:44px;border-radius:12px;background:var(--accent);color:#141a20;display:grid;place-items:center;font-weight:900;font-size:20px;letter-spacing:-1px}.brand strong{display:block;font-size:18px;letter-spacing:.2px}.brand span{display:block;color:var(--muted);font-size:12px;letter-spacing:1.4px;text-transform:uppercase}
    .status{border:1px solid #315b48;background:#10271e;color:var(--green);padding:7px 11px;border-radius:99px;font-size:12px;white-space:nowrap}.hero{padding:42px 0 28px;display:flex;justify-content:space-between;align-items:end;gap:24px}.eyebrow{color:var(--accent);font-size:12px;font-weight:750;letter-spacing:2px;text-transform:uppercase}.hero h1{font-size:clamp(32px,5vw,54px);line-height:1.06;letter-spacing:-1.8px;margin:10px 0 14px}.hero p{color:var(--muted);max-width:620px;margin:0}.version{color:var(--muted);font-size:12px}
    .section-head{display:flex;justify-content:space-between;align-items:center;margin:28px 0 14px}.section-head h2{font-size:16px;margin:0}.section-head span{font-size:12px;color:var(--muted)}
    .grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.card{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:16px;padding:20px;min-height:160px}.card .icon{width:38px;height:38px;border:1px solid #3b4b58;border-radius:11px;display:grid;place-items:center;color:var(--accent);font-size:18px;margin-bottom:18px}.card h3{font-size:15px;margin:0 0 6px}.card p{font-size:13px;color:var(--muted);margin:0}.pill{display:inline-block;margin-top:15px;font-size:11px;color:#d7c08f;background:#302719;border:1px solid #594526;border-radius:99px;padding:4px 8px}
    .notice{margin-top:20px;padding:15px 17px;border:1px solid #5b4826;background:#241e14;border-radius:12px;color:#e8d4aa;font-size:13px}.footer{display:flex;justify-content:space-between;gap:14px;border-top:1px solid var(--line);margin-top:32px;padding-top:18px;color:var(--muted);font-size:12px}
    @media(max-width:760px){.shell{padding:18px}.hero{display:block;padding-top:32px}.version{display:block;margin-top:18px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.footer{display:block}.footer span{display:block;margin-top:6px}}
    @media(max-width:480px){.grid{grid-template-columns:1fr}.top{align-items:flex-start}.status{font-size:11px}.hero h1{letter-spacing:-1px}}
  </style>
</head>
<body>
  <main class="shell">
    <header class="top">
      <div class="brand"><div class="mark">TP</div><div><strong>TorquePilotOS</strong><span>Automotive business platform</span></div></div>
      <div class="status">● Foundation online</div>
    </header>
    <section class="hero">
      <div><div class="eyebrow">One platform. Your entire workshop.</div><h1>Run your workshop<br>with more control.</h1><p>TorquePilot Workshop is the flagship workshop management product within TorquePilotOS. This is the first web foundation, ready for the next implementation phase.</p></div>
      <div class="version">WEB FOUNDATION · v0.1.0</div>
    </section>
    <div class="section-head"><h2>Workshop workspace</h2><span>Module connections are in development</span></div>
    <section class="grid" aria-label="Workshop modules">
      <article class="card"><div class="icon">▤</div><h3>Customers</h3><p>Customer profiles and contact records.</p><span class="pill">Next integration</span></article>
      <article class="card"><div class="icon">⌁</div><h3>Vehicles</h3><p>Vehicle details, registrations and ownership links.</p><span class="pill">Next integration</span></article>
      <article class="card"><div class="icon">▣</div><h3>Repair orders</h3><p>Track workshop jobs from intake through completion.</p><span class="pill">Next integration</span></article>
      <article class="card"><div class="icon">≡</div><h3>Estimates &amp; invoices</h3><p>Prepare estimates and follow invoice status.</p><span class="pill">Next integration</span></article>
      <article class="card"><div class="icon">◷</div><h3>Appointments</h3><p>Plan bookings and workshop capacity.</p><span class="pill">Next integration</span></article>
      <article class="card"><div class="icon">⚙</div><h3>Workshop settings</h3><p>Prepare business profile and operational preferences.</p><span class="pill">Next integration</span></article>
    </section>
    <aside class="notice"><strong>Development preview:</strong> This page confirms the web service can run. It does not yet authenticate users or read/write workshop data. Do not enter real customer information until authentication, database access and authorisation are implemented.</aside>
    <footer class="footer"><span>TorquePilotOS · TorquePilot Workshop</span><span>Built for the modern automotive workshop</span></footer>
  </main>
</body>
</html>"""
