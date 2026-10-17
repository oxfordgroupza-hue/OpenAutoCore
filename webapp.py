from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone

app = FastAPI(
    title="TorquePilotOS",
    description="Browser-based workshop management interface for TorquePilotOS.",
    version="0.1.0",
)

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TorquePilotOS | Workshop</title>
<style>
:root{color-scheme:dark;--bg:#0b1017;--panel:#121a24;--panel2:#172230;--line:#273545;--text:#edf3f8;--muted:#92a2b5;--accent:#55d6be;--blue:#78a9ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.5 Inter,Segoe UI,Arial,sans-serif}button{font:inherit}
.shell{display:grid;grid-template-columns:240px 1fr;min-height:100vh}.side{background:#0e151e;border-right:1px solid var(--line);padding:24px 16px}.brand{font-weight:800;font-size:19px;letter-spacing:.3px}.brand span{color:var(--accent)}.tag{font-size:10px;color:var(--muted);letter-spacing:2px;margin:4px 0 30px}.navlabel{font-size:10px;color:#718398;letter-spacing:1.5px;margin:20px 10px 8px}.nav{display:flex;align-items:center;gap:12px;width:100%;padding:11px 12px;border:0;border-radius:9px;background:transparent;color:#b5c2d0;text-align:left;cursor:pointer;margin:3px 0}.nav:hover,.nav.active{background:#1b2a37;color:#fff}.nav.active{box-shadow:inset 3px 0 var(--accent)}.nav .ico{width:20px;text-align:center;color:var(--accent)}.sidefoot{position:absolute;bottom:20px;color:#718398;font-size:11px}.main{min-width:0}.top{height:74px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 32px}.crumb{color:var(--muted)}.status{display:flex;gap:8px;align-items:center;color:var(--muted);font-size:12px}.dot{width:8px;height:8px;border-radius:50%;background:var(--accent)}.content{padding:30px 32px;max-width:1400px;margin:auto}.eyebrow{color:var(--accent);font-size:11px;letter-spacing:2px;font-weight:700}.heading{font-size:29px;letter-spacing:-.8px;margin:5px 0}.sub{color:var(--muted);margin:0 0 24px}.notice{border:1px solid #345b58;background:#122a2a;border-radius:10px;padding:13px 16px;margin-bottom:22px;color:#bde9df;font-size:12px}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}.statlabel{color:var(--muted);font-size:12px}.statvalue{font-size:28px;font-weight:750;margin:10px 0 4px}.statfoot{font-size:11px;color:#7f91a5}.sectionhead{display:flex;justify-content:space-between;align-items:center;margin:28px 0 12px}.sectionhead h2{font-size:16px;margin:0}.pill{border:1px solid var(--line);border-radius:20px;padding:4px 9px;color:var(--muted);font-size:11px}.quick{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.quick button{display:flex;align-items:center;gap:13px;text-align:left;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:17px;cursor:pointer}.quick button:hover{border-color:var(--accent)}.qico{font-size:22px;color:var(--accent)}.qtitle{font-weight:650}.qsub{font-size:11px;color:var(--muted);margin-top:3px}.tablewrap{overflow:auto}.table{width:100%;border-collapse:collapse;min-width:520px}.table th{text-align:left;font-size:10px;letter-spacing:1px;color:#8293a6;font-weight:600;padding:12px;border-bottom:1px solid var(--line)}.table td{padding:14px 12px;border-bottom:1px solid #202d3a}.empty{text-align:center;color:var(--muted);padding:28px!important}.pageview{display:none}.pageview.active{display:block}.footer{margin-top:28px;color:#65778b;font-size:11px}
@media(max-width:900px){.shell{grid-template-columns:72px 1fr}.side{padding:18px 9px}.brand{font-size:0;text-align:center}.brand:after{content:"TP";font-size:18px}.tag,.navlabel,.navtext,.sidefoot{display:none}.nav{justify-content:center;padding:12px 4px}.nav .ico{font-size:18px}.top{padding:0 18px}.content{padding:24px 18px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.quick{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.stats{gap:8px}.card{padding:13px}.statvalue{font-size:23px}.quick{grid-template-columns:1fr}.heading{font-size:24px}.top{height:60px}.content{padding:20px 13px}}
</style>
</head>
<body>
<div class="shell">
<aside class="side">
  <div class="brand">Torque<span>Pilot</span>OS</div><div class="tag">WORKSHOP OPERATING SYSTEM</div>
  <div class="navlabel">WORKSPACE</div>
  <button class="nav active" data-page="overview"><span class="ico">▦</span><span class="navtext">Overview</span></button>
  <button class="nav" data-page="customers"><span class="ico">♙</span><span class="navtext">Customers</span></button>
  <button class="nav" data-page="vehicles"><span class="ico">▰</span><span class="navtext">Vehicles</span></button>
  <button class="nav" data-page="appointments"><span class="ico">▦</span><span class="navtext">Appointments</span></button>
  <div class="navlabel">WORKSHOP</div>
  <button class="nav" data-page="repairs"><span class="ico">⚙</span><span class="navtext">Repair orders</span></button>
  <button class="nav" data-page="estimates"><span class="ico">≡</span><span class="navtext">Estimates</span></button>
  <button class="nav" data-page="invoices"><span class="ico">▤</span><span class="navtext">Invoices</span></button>
  <div class="navlabel">SYSTEM</div>
  <button class="nav" data-page="settings"><span class="ico">⚙</span><span class="navtext">Settings</span></button>
  <div class="sidefoot">TORQUEPILOTOS · WEB PREVIEW</div>
</aside>
<main class="main">
<header class="top"><div class="crumb" id="crumb">Workspace / Overview</div><div class="status"><span class="dot"></span> Web preview running</div></header>
<div class="content">
<section class="pageview active" id="page-overview">
  <div class="eyebrow">WORKSHOP COMMAND CENTRE</div><h1 class="heading">Your workshop, at a glance.</h1><p class="sub">A single workspace for the work that keeps your workshop moving.</p>
  <div class="notice"><strong>Development preview:</strong> sample figures are illustrative. Customer records, live database data, sign-in and saving changes are not connected yet.</div>
  <div class="stats">
    <div class="card"><div class="statlabel">Customers</div><div class="statvalue">—</div><div class="statfoot">Awaiting database connection</div></div>
    <div class="card"><div class="statlabel">Vehicles</div><div class="statvalue">—</div><div class="statfoot">Awaiting database connection</div></div>
    <div class="card"><div class="statlabel">Open repair orders</div><div class="statvalue">—</div><div class="statfoot">Awaiting database connection</div></div>
    <div class="card"><div class="statlabel">Pending estimates</div><div class="statvalue">—</div><div class="statfoot">Awaiting database connection</div></div>
  </div>
  <div class="sectionhead"><h2>Quick access</h2><span class="pill">Navigation preview</span></div>
  <div class="quick">
    <button data-goto="customers"><span class="qico">♙</span><span><div class="qtitle">Customer records</div><div class="qsub">Find and manage customer details</div></span></button>
    <button data-goto="vehicles"><span class="qico">▰</span><span><div class="qtitle">Vehicle register</div><div class="qsub">Vehicle profiles and history</div></span></button>
    <button data-goto="repairs"><span class="qico">⚙</span><span><div class="qtitle">Repair orders</div><div class="qsub">Track workshop jobs</div></span></button>
  </div>
  <div class="sectionhead"><h2>Recent workshop activity</h2><span class="pill">No live data</span></div>
  <div class="card tablewrap"><table class="table"><thead><tr><th>REFERENCE</th><th>CUSTOMER</th><th>VEHICLE</th><th>STATUS</th></tr></thead><tbody><tr><td colspan="4" class="empty">Activity will appear here after database integration.</td></tr></tbody></table></div>
</section>
<section class="pageview" id="page-customers"><div class="eyebrow">CUSTOMER MANAGEMENT</div><h1 class="heading">Customers</h1><p class="sub">A future view of customer profiles and contact details.</p><div class="notice">This screen is a navigation placeholder. No customer data is being read or changed.</div><div class="card">Next integration step: map the existing MySQL customer table and build searchable customer records.</div></section>
<section class="pageview" id="page-vehicles"><div class="eyebrow">VEHICLE MANAGEMENT</div><h1 class="heading">Vehicles</h1><p class="sub">Vehicle profiles linked to workshop customers.</p><div class="notice">This screen is a navigation placeholder. No vehicle data is being read or changed.</div><div class="card">Next integration step: map the existing vehicle schema, registration and VIN fields.</div></section>
<section class="pageview" id="page-appointments"><div class="eyebrow">WORKSHOP CALENDAR</div><h1 class="heading">Appointments</h1><p class="sub">Plan bookings and workshop capacity.</p><div class="notice">This screen is a navigation placeholder. No appointments are saved.</div><div class="card">Next integration step: connect the existing scheduling model and appointment workflow.</div></section>
<section class="pageview" id="page-repairs"><div class="eyebrow">JOB CONTROL</div><h1 class="heading">Repair orders</h1><p class="sub">Track jobs from check-in through completion.</p><div class="notice">This screen is a navigation placeholder. No repair orders are being read or changed.</div><div class="card">Next integration step: map repair_orders and its relationships to customers, vehicles, estimates and invoices.</div></section>
<section class="pageview" id="page-estimates"><div class="eyebrow">ESTIMATING</div><h1 class="heading">Estimates</h1><p class="sub">Prepare and track repair estimates.</p><div class="notice">This screen is a navigation placeholder. No estimates are saved.</div><div class="card">Next integration step: connect the existing pricing and estimate workflow.</div></section>
<section class="pageview" id="page-invoices"><div class="eyebrow">BILLING</div><h1 class="heading">Invoices</h1><p class="sub">A consolidated view of workshop billing.</p><div class="notice">This screen is a navigation placeholder. No invoice or payment data is connected.</div><div class="card">Next integration step: connect invoice records and review payment handling before enabling any financial actions.</div></section>
<section class="pageview" id="page-settings"><div class="eyebrow">CONFIGURATION</div><h1 class="heading">Settings</h1><p class="sub">Workspace configuration and integrations.</p><div class="notice">Settings are not persisted in this preview.</div><div class="card"><strong>Deployment status</strong><p style="color:var(--muted)">The web shell runs independently from the original PyQt6 desktop application. Database credentials should be added only after the database provider and connection details have been verified.</p></div></section>
<div class="footer">TorquePilotOS · One platform. Your entire workshop. · Browser MVP preview</div>
</div></main></div>
<script>
function showPage(page){
  document.querySelectorAll('.pageview').forEach(el=>el.classList.toggle('active',el.id==='page-'+page));
  document.querySelectorAll('.nav[data-page]').forEach(el=>el.classList.toggle('active',el.dataset.page===page));
  const label=page.charAt(0).toUpperCase()+page.slice(1);
  document.getElementById('crumb').textContent='Workspace / '+(page==='repairs'?'Repair orders':label);
}
document.querySelectorAll('[data-page]').forEach(el=>el.addEventListener('click',()=>showPage(el.dataset.page)));
document.querySelectorAll('[data-goto]').forEach(el=>el.addEventListener('click',()=>showPage(el.dataset.goto)));
</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(PAGE)

@app.get("/health")
def health():
    return {"status": "ok", "app": "TorquePilotOS", "version": app.version}

@app.get("/api/status")
def api_status():
    return {
        "app": "TorquePilotOS",
        "mode": "web-preview",
        "database_connected": False,
        "authentication_enabled": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
