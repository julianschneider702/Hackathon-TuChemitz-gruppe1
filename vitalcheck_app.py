#!/usr/bin/env python3
"""VitalCheck – generiert vitalcheck.html und öffnet im Browser (lokal, kein Server)."""

import json, webbrowser
from pathlib import Path

BASE      = Path(__file__).parent
DATA_FILE = BASE / "data.json"
HTML_FILE = BASE / "vitalcheck.html"

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>VitalCheck</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:linear-gradient(135deg,#d8e4f0,#e8eef5 50%,#dde6f0);
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  gap:40px;overflow:hidden;user-select:none;
}

/* ── DEMO PANEL (neben Handy) ── */
.demo-panel{
  display:flex;flex-direction:column;align-items:stretch;gap:14px;
  background:#fff;border-radius:22px;padding:22px;width:240px;
  box-shadow:0 20px 60px rgba(0,0,0,.12),0 4px 16px rgba(0,0,0,.06);
}
.demo-title{
  font-size:11px;font-weight:800;color:#1c3d5e;letter-spacing:.8px;
  text-transform:uppercase;text-align:center;
}
.demo-btn{
  padding:16px 14px;border:none;border-radius:14px;
  background:linear-gradient(135deg,#2da44e,#22863a);color:#fff;
  font-size:15px;font-weight:800;cursor:pointer;font-family:inherit;
  box-shadow:0 6px 20px rgba(45,164,78,.4);
  transition:transform .15s,opacity .15s;
}
.demo-btn:active{transform:scale(.96);}
.demo-btn:disabled{opacity:.55;cursor:not-allowed;}
.demo-status{
  font-size:12px;color:#888;text-align:center;line-height:1.4;
  min-height:30px;padding:6px 4px;
}
.demo-status.ok{color:#2da44e;font-weight:700;}
.demo-status.err{color:#c33;font-weight:700;}
.demo-spinner{
  display:inline-block;width:11px;height:11px;border:2px solid #ccc;
  border-top-color:#1c3d5e;border-radius:50%;
  animation:spin .8s linear infinite;vertical-align:-1px;margin-right:6px;
}
@keyframes spin{to{transform:rotate(360deg);}}

/* ── PHONE ── */
.phone{
  position:relative;width:393px;height:852px;
  background:#111;border-radius:54px;flex-shrink:0;
  box-shadow:0 0 0 1px #333,0 0 0 3px #222,
    0 40px 120px rgba(0,0,0,.55),0 10px 40px rgba(0,0,0,.3),
    inset 0 1px 0 #555;
}
.phone::before{content:'';position:absolute;left:-4px;top:160px;
  width:4px;height:36px;background:#2a2a2a;border-radius:3px 0 0 3px;
  box-shadow:0 50px 0 #2a2a2a,0 100px 0 #2a2a2a;}
.phone::after{content:'';position:absolute;right:-4px;top:200px;
  width:4px;height:70px;background:#2a2a2a;border-radius:0 3px 3px 0;}

.screen{
  position:absolute;inset:12px;background:#f0f3f7;
  border-radius:43px;overflow:hidden;display:flex;flex-direction:column;
}

/* ── STATUS BAR ── */
.statusbar{
  height:52px;padding:16px 24px 0;
  display:flex;align-items:center;justify-content:space-between;
  flex-shrink:0;position:relative;z-index:10;
}
.st-time{font-size:15px;font-weight:700;color:#111;letter-spacing:-.3px;}
.st-cam{position:absolute;left:50%;transform:translateX(-50%);
  top:18px;width:13px;height:13px;background:#111;border-radius:50%;
  box-shadow:0 0 0 2px #222;}
.st-icons{display:flex;align-items:center;gap:6px;}

/* ── APP ── */
.app{flex:1;display:flex;flex-direction:column;overflow:hidden;position:relative;}

/* ── TAB SWIPER ── */
.tabs-vp{flex:1;overflow:hidden;position:relative;}
.tabs-track{
  display:flex;width:300%;height:100%;
  transition:transform .38s cubic-bezier(.25,.46,.45,.94);
  will-change:transform;
}
.tab-pane{
  width:33.3333%;height:100%;
  overflow-y:auto;overflow-x:hidden;
  -webkit-overflow-scrolling:touch;position:relative;
}
.tab-pane::-webkit-scrollbar{display:none;}

/* ── BOTTOM NAV ── */
.bottom-nav{
  height:76px;background:#1c3d5e;
  display:flex;align-items:flex-start;justify-content:space-around;
  padding-top:12px;flex-shrink:0;border-radius:0 0 43px 43px;
}
.nav-btn{
  display:flex;flex-direction:column;align-items:center;gap:4px;
  cursor:pointer;color:rgba(255,255,255,.45);transition:color .2s;
  padding:0 16px;border:none;background:transparent;font-family:inherit;
}
.nav-btn.active{color:#fff;}
.nav-btn svg{width:22px;height:22px;}
.nav-label{font-size:10px;font-weight:600;letter-spacing:.2px;}

/* ── HOME ── */
.home-pad{padding:20px 20px 24px;}
.greeting{font-size:34px;font-weight:800;color:#111;margin-bottom:22px;letter-spacing:-.5px;}
.apt-card{
  background:linear-gradient(135deg,#1c3d5e,#2a5580);
  border-radius:20px;padding:18px 20px;
  display:flex;align-items:center;gap:16px;margin-bottom:16px;
  cursor:pointer;box-shadow:0 6px 24px rgba(28,61,94,.35);
  transition:transform .15s,box-shadow .15s;
}
.apt-card:active{transform:scale(.97);}
.apt-icon-wrap{
  width:46px;height:46px;background:rgba(255,255,255,.15);
  border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:22px;flex-shrink:0;
}
.apt-title{font-size:17px;font-weight:700;color:#fff;margin-bottom:3px;}
.apt-time{font-size:14px;color:rgba(255,255,255,.75);}
.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}
.quick-btn{
  background:linear-gradient(145deg,#1c3d5e,#254e78);
  border:none;color:#fff;border-radius:20px;padding:26px 16px;
  display:flex;flex-direction:column;align-items:center;gap:10px;
  cursor:pointer;font-family:inherit;font-size:16px;font-weight:700;
  box-shadow:0 6px 20px rgba(28,61,94,.3);transition:transform .15s;
}
.quick-btn:active{transform:scale(.95);}
.quick-btn-icon{font-size:30px;}
.chat-btn{
  width:100%;background:linear-gradient(135deg,#f5a623,#e8920e);
  border:none;color:#7a3d00;border-radius:20px;padding:20px;
  display:flex;align-items:center;justify-content:center;gap:12px;
  cursor:pointer;font-family:inherit;font-size:18px;font-weight:800;
  box-shadow:0 6px 20px rgba(245,166,35,.4);transition:transform .15s;
}
.chat-btn:active{transform:scale(.97);}

/* ── CALENDAR OVERLAY ── */
.cal-overlay{
  position:absolute;inset:0;background:#f0f3f7;
  transform:translateY(100%);
  transition:transform .38s cubic-bezier(.25,.46,.45,.94);
  z-index:50;display:flex;flex-direction:column;
}
.cal-overlay.open{transform:translateY(0);}
.cal-hdr{
  display:flex;align-items:center;gap:14px;
  padding:16px 20px 10px;flex-shrink:0;
}
.cal-hdr-title{font-size:28px;font-weight:800;color:#111;letter-spacing:-.3px;}
.cal-month-nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:0 20px 12px;flex-shrink:0;
}
.cal-month-label{font-size:17px;font-weight:700;color:#111;}
.cal-nav-btn{
  width:34px;height:34px;border:none;background:#fff;
  border-radius:50%;font-size:18px;color:#1c3d5e;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(0,0,0,.1);font-weight:700;
}
.cal-grid-wrap{margin:0 20px;background:#fff;border-radius:18px;
  overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.07);flex-shrink:0;}
.cal-daynames{
  display:grid;grid-template-columns:repeat(7,1fr);
  background:#1c3d5e;padding:9px 6px;
}
.cal-dayname{text-align:center;font-size:11px;font-weight:700;
  color:rgba(255,255,255,.7);letter-spacing:.3px;}
.cal-days{display:grid;grid-template-columns:repeat(7,1fr);
  padding:6px;gap:3px;}
.cal-day{
  aspect-ratio:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  border-radius:10px;font-size:14px;font-weight:500;color:#333;
  position:relative;cursor:default;
}
.cal-day.empty{visibility:hidden;}
.cal-day.other-month{color:#ccc;}
.cal-day.today{background:#e8edf5;font-weight:800;color:#1c3d5e;}
.cal-day.has-apt{
  background:#1c3d5e;color:#fff;font-weight:700;cursor:pointer;
  transition:opacity .15s;
}
.cal-day.has-apt:active{opacity:.75;}
.cal-day.selected{background:#2a5580;color:#fff;
  box-shadow:0 2px 10px rgba(28,61,94,.35);}
.cal-dot{width:5px;height:5px;background:rgba(255,255,255,.65);
  border-radius:50%;position:absolute;bottom:3px;}
.cal-detail-area{flex:1;overflow-y:auto;padding:14px 20px 0;}
.cal-detail-area::-webkit-scrollbar{display:none;}
.apt-detail-card{
  background:#fff;border-radius:18px;padding:18px;
  box-shadow:0 2px 12px rgba(0,0,0,.07);margin-bottom:12px;
}
.apt-detail-name{font-size:19px;font-weight:800;color:#111;margin-bottom:14px;}
.apt-detail-row{display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;}
.apt-detail-row:last-child{margin-bottom:0;}
.apt-detail-icon{font-size:18px;width:24px;flex-shrink:0;text-align:center;}
.apt-detail-text{font-size:14px;color:#555;line-height:1.45;}
.apt-badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 14px;border-radius:20px;
  font-size:13px;font-weight:700;margin-top:14px;
}
.apt-badge.confirmed{background:#e8f5e9;color:#2da44e;}
.apt-badge.unconfirmed{background:#fff3e0;color:#f57c00;}
.cal-hint{text-align:center;padding:28px 20px;color:#bbb;font-size:14px;}

/* ── CHAT BOTTOM SHEET ── */
.sheet-overlay{
  position:absolute;inset:0;background:rgba(0,0,0,.4);
  opacity:0;pointer-events:none;transition:opacity .3s;
  z-index:60;border-radius:43px;
}
.sheet-overlay.open{opacity:1;pointer-events:all;}
.chat-sheet{
  position:absolute;bottom:0;left:0;right:0;height:88%;
  background:#fff;border-radius:28px 28px 0 0;
  transform:translateY(100%);
  transition:transform .38s cubic-bezier(.25,.46,.45,.94);
  z-index:61;display:flex;flex-direction:column;
  box-shadow:0 -8px 40px rgba(0,0,0,.15);
}
.chat-sheet.open{transform:translateY(0);}
.sheet-drag{width:44px;height:5px;background:#e0e0e0;
  border-radius:3px;margin:14px auto 10px;flex-shrink:0;}
.sheet-title{padding:0 20px 14px;font-size:20px;font-weight:800;color:#111;
  flex-shrink:0;border-bottom:1px solid #f0f0f0;}
.chat-msgs{flex:1;overflow-y:auto;padding:16px;
  display:flex;flex-direction:column;gap:14px;}
.chat-msgs::-webkit-scrollbar{display:none;}
.cmsg{display:flex;gap:10px;align-items:flex-end;}
.cmsg.user{flex-direction:row-reverse;}
.mavatar{width:34px;height:34px;background:#e8edf5;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:17px;flex-shrink:0;}
.mbubble{max-width:72%;padding:11px 15px;border-radius:20px;
  font-size:14px;line-height:1.5;}
.cmsg.bot .mbubble{background:#f0f3f7;color:#111;border-bottom-left-radius:5px;max-width:85%;}
.cmsg.bot .mbubble strong{color:#1c3d5e;font-weight:800;}
.cmsg.user .mbubble{background:#ccdff5;color:#1c3d5e;border-bottom-right-radius:5px;}
.choices-box{border:1px solid #e8edf5;border-radius:16px;
  padding:14px;display:flex;flex-direction:column;gap:8px;}
.choices-label{font-size:12px;color:#aaa;margin-bottom:2px;}
.choices-row{display:flex;gap:8px;}
.choice-btn{flex:1;background:#1c3d5e;color:#fff;border:none;
  padding:11px 8px;border-radius:13px;font-size:14px;font-weight:600;
  cursor:pointer;font-family:inherit;transition:opacity .15s;}
.choice-btn:active{opacity:.75;}
.chat-input-row{padding:12px 16px 16px;display:flex;gap:10px;
  align-items:center;border-top:1px solid #f0f0f0;flex-shrink:0;}
.chat-input{flex:1;border:1.5px solid #e0e8f0;border-radius:24px;
  padding:11px 18px;font-size:14px;font-family:inherit;
  outline:none;color:#111;background:#fafbfd;transition:border-color .2s;}
.chat-input:focus{border-color:#1c3d5e;}
.send-btn{width:38px;height:38px;background:#1c3d5e;border:none;
  border-radius:50%;color:#fff;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;transition:opacity .15s;}
.send-btn:active{opacity:.75;}
.send-btn:disabled{opacity:.4;cursor:not-allowed;}
.typing-dots{display:flex;gap:4px;align-items:center;padding:4px 6px;}
.typing-dots span{
  width:7px;height:7px;background:#888;border-radius:50%;
  animation:tdot 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2){animation-delay:.15s;}
.typing-dots span:nth-child(3){animation-delay:.3s;}
@keyframes tdot{
  0%,60%,100%{transform:translateY(0);opacity:.35;}
  30%{transform:translateY(-5px);opacity:1;}
}
.chat-err{
  margin:0 16px 8px;padding:9px 12px;background:#fee;color:#a33;
  border-radius:10px;font-size:12px;text-align:center;
}

/* ── TERMINE ── */
.tab-header{padding:20px 20px 10px;font-size:30px;font-weight:800;
  color:#111;letter-spacing:-.4px;background:#f0f3f7;
  position:sticky;top:0;z-index:5;}
.pill-bar{display:flex;margin:0 20px 18px;background:#e2e8f0;
  border-radius:14px;padding:3px;position:sticky;top:66px;z-index:4;}
.pill-btn{flex:1;padding:9px;border:none;background:transparent;
  border-radius:11px;font-size:14px;font-weight:600;
  cursor:pointer;color:#666;font-family:inherit;transition:all .2s;}
.pill-btn.active{background:#fff;color:#1c3d5e;
  box-shadow:0 2px 10px rgba(0,0,0,.1);}
.section-content{display:none;}
.section-content.visible{display:block;}
.imp-summary{margin:0 20px 18px;display:flex;align-items:center;gap:14px;}
.imp-icon{font-size:32px;}
.imp-num{font-size:36px;font-weight:800;color:#111;line-height:1;}
.imp-lbl{font-size:13px;color:#888;margin-top:2px;}
.vacc-card{margin:0 20px 10px;background:#fff;border-radius:18px;
  padding:16px 18px;box-shadow:0 2px 12px rgba(0,0,0,.07);}
.vacc-row{display:flex;justify-content:space-between;align-items:flex-start;}
.vacc-name{font-size:18px;font-weight:800;color:#111;}
.vacc-name.grey{color:#aaa;font-weight:600;}
.vacc-due{font-size:13px;font-weight:700;color:#2da44e;text-align:right;line-height:1.4;}
.vacc-due.overdue{color:#c33;}
.vacc-due.soon{color:#f57c00;}
.vacc-sub{font-size:13px;color:#999;margin-top:5px;line-height:1.4;}
.vacc-sub.grey{color:#ccc;}
.vors-card{margin:0 20px 10px;background:#fff;border-radius:18px;
  padding:16px 18px;display:flex;align-items:center;gap:14px;
  box-shadow:0 2px 12px rgba(0,0,0,.07);}
.vors-icon{width:46px;height:46px;background:#e8edf5;border-radius:14px;
  display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}
.vors-body{flex:1;}
.vors-name{font-size:17px;font-weight:700;color:#111;}
.vors-meta{display:flex;gap:10px;margin-top:4px;align-items:center;}
.vors-date{font-size:13px;color:#888;}
.vors-time{font-size:13px;font-weight:600;color:#2da44e;}
.vors-check{color:#aaa;font-size:20px;flex-shrink:0;}
.past-label{padding:6px 20px 10px;font-size:13px;color:#aaa;font-weight:500;}
.past-card{margin:0 20px 8px;background:#f8f9fb;border-radius:14px;padding:13px 16px;}
.past-name{font-size:16px;color:#bbb;}
.past-date{font-size:12px;color:#ccc;margin-top:3px;}

/* ── PROFIL ── */
.profil-hero{padding:28px 20px 20px;
  display:flex;flex-direction:column;align-items:center;gap:12px;
  background:linear-gradient(180deg,#e8edf5,#f0f3f7);}
.profil-av{width:76px;height:76px;background:linear-gradient(135deg,#1c3d5e,#2a5580);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:34px;box-shadow:0 6px 20px rgba(28,61,94,.3);}
.profil-name{font-size:24px;font-weight:800;color:#111;}
.profil-tag{font-size:13px;color:#888;margin-top:-6px;}
.menu-section{margin:0 20px 6px;}
.menu-label{font-size:11px;font-weight:700;color:#aaa;
  text-transform:uppercase;letter-spacing:.8px;padding:14px 4px 8px;}
.menu-item{background:#fff;border-radius:16px;padding:15px 16px;
  display:flex;align-items:center;gap:14px;cursor:pointer;margin-bottom:10px;
  box-shadow:0 2px 10px rgba(0,0,0,.06);transition:transform .15s;}
.menu-item:active{transform:scale(.97);}
.menu-icon{width:40px;height:40px;background:#e8edf5;border-radius:12px;
  display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0;}
.menu-text{flex:1;}
.menu-title{font-size:16px;font-weight:700;color:#111;}
.menu-sub{font-size:12px;color:#aaa;margin-top:2px;}
.menu-arrow{color:#ccc;font-size:20px;}

/* ── SUB-PAGES ── */
.subpage{
  position:absolute;inset:0;background:#f0f3f7;
  transform:translateX(100%);
  transition:transform .32s cubic-bezier(.25,.46,.45,.94);
  z-index:30;overflow-y:auto;overflow-x:hidden;
}
.subpage::-webkit-scrollbar{display:none;}
.subpage.open{transform:translateX(0);}
.subpage-hdr{display:flex;align-items:center;gap:14px;
  padding:16px 20px;position:sticky;top:0;background:#f0f3f7;z-index:5;}
.back-btn{width:38px;height:38px;border:none;background:#fff;
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.1);flex-shrink:0;}
.back-btn svg{width:18px;height:18px;color:#1c3d5e;}
.subpage-title{font-size:26px;font-weight:800;color:#111;letter-spacing:-.3px;}

/* ── EPA BTN ── */
.epa-btn{
  margin:0 20px 16px;
  background:linear-gradient(135deg,#1c3d5e,#2a5580);
  border-radius:18px;padding:16px 18px;
  display:flex;align-items:center;gap:14px;cursor:pointer;
  box-shadow:0 4px 16px rgba(28,61,94,.25);transition:transform .15s;
}
.epa-btn:active{transform:scale(.97);}
.epa-icon{font-size:26px;flex-shrink:0;}
.epa-text{flex:1;}
.epa-title-t{font-size:16px;font-weight:700;color:#fff;}
.epa-sub{font-size:12px;color:rgba(255,255,255,.65);margin-top:2px;}
.epa-arrow{color:rgba(255,255,255,.5);font-size:20px;}

/* ── HEALTH ROWS ── */
.health-card{margin:0 20px 12px;background:#fff;border-radius:18px;
  overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.07);}
.health-card-title{padding:14px 18px 10px;font-size:15px;font-weight:800;
  color:#111;border-bottom:1px solid #f5f5f5;}
.health-row{display:flex;flex-direction:column;
  padding:13px 18px;border-bottom:1px solid #f8f8f8;
  cursor:pointer;transition:background .15s;}
.health-row:last-child{border-bottom:none;}
.health-row:active{background:#f5f7fb;}
.h-row-top{display:flex;align-items:center;gap:12px;}
.h-icon{font-size:18px;width:24px;text-align:center;flex-shrink:0;}
.h-label{flex:1;font-size:14px;color:#555;}
.h-arrow{color:#ccc;font-size:15px;flex-shrink:0;}
.h-val{font-size:15px;font-weight:600;color:#111;
  margin-top:6px;padding-left:36px;line-height:1.45;}

/* ── FIELD DETAIL ── */
.field-detail-inner{padding:20px;}
.field-big-icon{font-size:52px;text-align:center;padding:16px 0 8px;}
.field-big-label{font-size:13px;color:#aaa;font-weight:600;
  text-align:center;text-transform:uppercase;letter-spacing:.7px;}
.field-big-value{
  font-size:22px;font-weight:800;color:#111;
  text-align:center;padding:10px 10px 0;line-height:1.4;
}
.pad-bottom{height:24px;}

/* ── EDIT FORM ── */
.form-pad{padding:6px 20px 28px;}
.form-row{margin-bottom:16px;}
.form-label{
  font-size:12px;font-weight:700;color:#888;
  text-transform:uppercase;letter-spacing:.6px;
  margin-bottom:8px;display:block;
}
.form-input{
  width:100%;padding:14px 16px;background:#fff;border:1.5px solid #e2e8f0;
  border-radius:14px;font-size:16px;font-family:inherit;color:#111;
  outline:none;transition:border-color .2s;
}
.form-input:focus{border-color:#1c3d5e;}
.form-textarea{min-height:90px;resize:vertical;line-height:1.4;}
.input-row{display:flex;gap:10px;align-items:center;}
.input-suffix{
  font-size:15px;font-weight:700;color:#888;flex-shrink:0;
}
.choice-grid{display:flex;gap:8px;flex-wrap:wrap;}
.choice-chip{
  flex:1;min-width:90px;padding:14px 10px;background:#fff;
  border:1.5px solid #e2e8f0;border-radius:14px;
  font-size:14px;font-weight:600;color:#555;
  cursor:pointer;font-family:inherit;text-align:center;
  transition:all .15s;
}
.choice-chip.active{
  background:#1c3d5e;color:#fff;border-color:#1c3d5e;
  box-shadow:0 4px 12px rgba(28,61,94,.25);
}
.dd-wrap{position:relative;}
.dd-select{
  width:100%;padding:14px 40px 14px 16px;background:#fff;
  border:1.5px solid #e2e8f0;border-radius:14px;
  font-size:16px;font-family:inherit;color:#111;
  outline:none;appearance:none;-webkit-appearance:none;cursor:pointer;
}
.dd-arrow{
  position:absolute;right:16px;top:50%;transform:translateY(-50%);
  color:#1c3d5e;pointer-events:none;font-size:14px;font-weight:800;
}
.list-item{
  background:#fff;border:1.5px solid #e2e8f0;border-radius:14px;
  padding:8px 10px 8px 14px;display:flex;align-items:center;gap:8px;
  margin-bottom:8px;
}
.list-item input{
  flex:1;border:none;outline:none;background:transparent;
  font-size:15px;font-family:inherit;color:#111;padding:6px 0;min-width:0;
}
.list-rm{
  width:30px;height:30px;border:none;background:#fee;color:#c33;
  border-radius:8px;cursor:pointer;font-size:18px;font-weight:800;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.list-add{
  width:100%;padding:12px;background:#e8edf5;
  border:1.5px dashed #1c3d5e;color:#1c3d5e;
  border-radius:14px;font-size:14px;font-weight:700;
  cursor:pointer;font-family:inherit;margin-top:4px;
}
.empty-hint{
  text-align:center;color:#aaa;font-size:13px;padding:14px 0;
  font-style:italic;
}
.backup-row{
  margin:0 20px 16px;display:flex;gap:8px;
}
.backup-btn{
  flex:1;padding:10px 8px;background:#fff;border:1.5px solid #e2e8f0;
  border-radius:12px;font-size:12px;font-weight:700;color:#1c3d5e;
  cursor:pointer;font-family:inherit;
}
.backup-btn:active{background:#e8edf5;}
.save-toast{
  position:absolute;left:50%;bottom:90px;transform:translateX(-50%) translateY(20px);
  background:#1c3d5e;color:#fff;padding:10px 20px;border-radius:24px;
  font-size:13px;font-weight:700;opacity:0;pointer-events:none;
  transition:opacity .25s,transform .25s;z-index:80;
  box-shadow:0 4px 16px rgba(0,0,0,.25);
}
.save-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
.save-btn{
  width:100%;padding:16px;background:#1c3d5e;color:#fff;border:none;
  border-radius:14px;font-size:16px;font-weight:800;cursor:pointer;
  font-family:inherit;margin-top:14px;
  box-shadow:0 4px 16px rgba(28,61,94,.3);transition:opacity .15s;
}
.save-btn:active{opacity:.8;}
.yn-extra{margin-top:14px;}
.yn-extra.hidden{display:none;}

/* ── DOC UPLOAD ── */
.upload-card{
  margin:0 20px 14px;background:#fff;border:1.5px dashed #1c3d5e;
  border-radius:16px;padding:14px 16px;display:flex;align-items:center;gap:12px;
  cursor:pointer;transition:background .15s,transform .15s;
}
.upload-card:active{background:#e8edf5;transform:scale(.98);}
.upload-icon{
  width:42px;height:42px;background:#e8edf5;border-radius:12px;
  display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;
}
.upload-text{flex:1;}
.upload-title-t{font-size:15px;font-weight:700;color:#1c3d5e;}
.upload-sub{font-size:12px;color:#888;margin-top:2px;}
.upload-plus{color:#1c3d5e;font-size:24px;font-weight:800;flex-shrink:0;}
.doc-card{
  margin:0 20px 8px;background:#fff;border-radius:14px;
  padding:12px 14px;display:flex;align-items:center;gap:12px;
  box-shadow:0 2px 8px rgba(0,0,0,.05);
}
.doc-icon{
  width:36px;height:36px;background:#fff3e0;border-radius:10px;
  display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;
}
.doc-body{flex:1;min-width:0;}
.doc-name{
  font-size:14px;font-weight:700;color:#111;line-height:1.3;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.doc-meta{font-size:11px;color:#999;margin-top:2px;}
.doc-actions{display:flex;gap:6px;flex-shrink:0;}
.doc-act{
  width:30px;height:30px;border:none;border-radius:8px;
  background:#f0f3f7;color:#1c3d5e;cursor:pointer;font-size:14px;
  display:flex;align-items:center;justify-content:center;
}
.doc-act.del{background:#fee;color:#c33;}
.doc-act:active{opacity:.7;}
.docs-label{padding:2px 22px 8px;font-size:11px;color:#aaa;
  font-weight:700;text-transform:uppercase;letter-spacing:.5px;}
.import-meta{
  margin:0 20px 12px;padding:10px 14px;background:#e8f5e9;
  border-radius:12px;display:flex;align-items:center;gap:10px;
  font-size:12px;color:#2da44e;
}
.import-meta .reset-btn{
  margin-left:auto;background:transparent;border:1px solid #2da44e;
  color:#2da44e;padding:4px 10px;border-radius:8px;
  font-size:11px;font-weight:700;cursor:pointer;font-family:inherit;
}
.import-meta .reset-btn:active{opacity:.6;}
.import-meta strong{color:#1c3d5e;font-weight:700;}
</style>
</head>
<body>

<!-- ── DEMO PANEL (neben Handy) ── -->
<aside class="demo-panel">
  <div class="demo-title">n8n Workflows</div>
  <button class="demo-btn" id="demoBtn" onclick="triggerDemo()">▶ Demo starten</button>
  <button class="demo-btn" id="finalBtn" style="background:linear-gradient(135deg,#1c3d5e,#2a5580);box-shadow:0 6px 20px rgba(28,61,94,.4);" onclick="triggerFinal()">▶ Workflow 3 starten</button>
  <div class="demo-status" id="demoStatus">Bereit</div>
</aside>

<div class="phone">
<div class="screen">

<!-- STATUS BAR -->
<div class="statusbar">
  <span class="st-time">10:12</span>
  <div class="st-cam"></div>
  <div class="st-icons">
    <svg viewBox="0 0 24 24" width="16" height="16" fill="#111">
      <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
    </svg>
    <svg viewBox="0 0 24 24" width="14" height="14" fill="#111">
      <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/>
    </svg>
    <span style="font-size:12px;font-weight:700;color:#111;">78%</span>
  </div>
</div>

<!-- APP -->
<div class="app">

  <!-- TABS -->
  <div class="tabs-vp" id="vp">
    <div class="tabs-track" id="track">

      <!-- ══ HOME ══ -->
      <div class="tab-pane" id="pane0">

        <!-- CALENDAR OVERLAY (inside pane0) -->
        <div class="cal-overlay" id="calOverlay">
          <div class="cal-hdr">
            <button class="back-btn" onclick="closeCal()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
            </button>
            <span class="cal-hdr-title">Meine Termine</span>
          </div>
          <div class="cal-month-nav">
            <button class="cal-nav-btn" onclick="changeMonth(-1)">‹</button>
            <span class="cal-month-label" id="calMonthLabel"></span>
            <button class="cal-nav-btn" onclick="changeMonth(1)">›</button>
          </div>
          <div class="cal-grid-wrap">
            <div class="cal-daynames">
              <div class="cal-dayname">Mo</div><div class="cal-dayname">Di</div>
              <div class="cal-dayname">Mi</div><div class="cal-dayname">Do</div>
              <div class="cal-dayname">Fr</div><div class="cal-dayname">Sa</div>
              <div class="cal-dayname">So</div>
            </div>
            <div class="cal-days" id="calDays"></div>
          </div>
          <div class="cal-detail-area" id="calDetail">
            <div class="cal-hint">Tag mit Termin antippen für Details</div>
          </div>
        </div>

        <div class="home-pad">
          <div class="greeting" id="homeGreeting">Hallo!</div>
          <div class="apt-card" onclick="openCal()">
            <div class="apt-icon-wrap">📅</div>
            <div>
              <div class="apt-title">Nächster Termin</div>
              <div class="apt-time" id="aptTime">–</div>
            </div>
          </div>
          <div class="quick-grid">
            <button class="quick-btn" onclick="goTab(1);showSub('impfpass')">
              <span class="quick-btn-icon">💉</span>Impfpass
            </button>
            <button class="quick-btn" onclick="goTab(1);showSub('vorsorge')">
              <span class="quick-btn-icon">🫀</span>Vorsorge
            </button>
          </div>
          <button class="chat-btn" onclick="openChat()">
            <span style="font-size:26px">👨‍⚕️</span>Chat
          </button>
        </div>
      </div>

      <!-- ══ TERMINE ══ -->
      <div class="tab-pane" id="pane1">
        <div class="tab-header">Termine</div>
        <div class="pill-bar">
          <button class="pill-btn active" id="pill-impfpass" onclick="showSub('impfpass')">Impfpass</button>
          <button class="pill-btn" id="pill-vorsorge" onclick="showSub('vorsorge')">Vorsorge</button>
        </div>
        <div id="sec-impfpass" class="section-content visible">
          <div class="imp-summary">
            <span class="imp-icon">💉</span>
            <div>
              <div class="imp-num" id="vaccCount">0</div>
              <div class="imp-lbl">Dokumentierte Impfungen</div>
            </div>
          </div>
          <div class="upload-card" onclick="document.getElementById('upload-impfpass').click()">
            <div class="upload-icon">📄</div>
            <div class="upload-text">
              <div class="upload-title-t">Impfpass aus CSV importieren</div>
              <div class="upload-sub">Spalten: name, letzte_impfung, intervall_jahre, vollstaendig</div>
            </div>
            <div class="upload-plus">+</div>
          </div>
          <input type="file" id="upload-impfpass" style="display:none;"
                 accept=".csv,text/csv" onchange="handleUpload(event,'impfpass')">
          <div id="meta-impfpass"></div>
          <div id="vaccList"></div>
          <div class="pad-bottom"></div>
        </div>
        <div id="sec-vorsorge" class="section-content">
          <div class="upload-card" onclick="document.getElementById('upload-vorsorge').click()">
            <div class="upload-icon">📋</div>
            <div class="upload-text">
              <div class="upload-title-t">Vorsorge aus CSV importieren</div>
              <div class="upload-sub">Spalten: name, datum, uhrzeit, arzt, adresse</div>
            </div>
            <div class="upload-plus">+</div>
          </div>
          <input type="file" id="upload-vorsorge" style="display:none;"
                 accept=".csv,text/csv" onchange="handleUpload(event,'vorsorge')">
          <div id="meta-vorsorge"></div>
          <div id="vorsList"></div>
          <div class="past-label">Vergangene Vorsorgen:</div>
          <div id="pastList"></div>
          <div class="pad-bottom"></div>
        </div>
      </div>

      <!-- ══ PROFIL ══ -->
      <div class="tab-pane" id="pane2">

        <!-- SUB: Field detail (z:35) -->
        <div class="subpage" id="sp-field" style="z-index:35;">
          <div class="subpage-hdr">
            <button class="back-btn" onclick="closeSP('sp-field')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
            </button>
            <span class="subpage-title" id="sp-field-title"></span>
          </div>
          <div id="sp-field-content"></div>
        </div>

        <!-- SUB: Gesundheitsdaten (z:30) -->
        <div class="subpage" id="sp-gesundheit">
          <div class="subpage-hdr">
            <button class="back-btn" onclick="closeSP('sp-gesundheit')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
            </button>
            <span class="subpage-title">Gesundheitsdaten</span>
          </div>
          <div id="gesundheitContent"></div>
          <div class="pad-bottom"></div>
        </div>

        <!-- PROFIL MAIN -->
        <div class="profil-hero">
          <div class="profil-av">👤</div>
          <div class="profil-name" id="profilName">Alex</div>
          <div class="profil-tag">Mitglied seit 2024</div>
        </div>
        <div class="menu-section">
          <div class="menu-label">Gesundheit</div>
          <div class="menu-item" onclick="openSP('sp-gesundheit')">
            <div class="menu-icon">🏥</div>
            <div class="menu-text">
              <div class="menu-title">Gesundheitsdaten</div>
              <div class="menu-sub">Persönliche Daten, Biometrie, Lebensstil</div>
            </div>
            <div class="menu-arrow">›</div>
          </div>
        </div>
        <div class="pad-bottom"></div>
      </div>

    </div><!-- /track -->
  </div><!-- /vp -->

  <!-- BOTTOM NAV -->
  <nav class="bottom-nav">
    <button class="nav-btn active" id="nav0" onclick="goTab(0)">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
      </svg>
      <span class="nav-label">Home</span>
    </button>
    <button class="nav-btn" id="nav1" onclick="goTab(1)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <path d="M16 2v4M8 2v4M3 10h18"/>
      </svg>
      <span class="nav-label">Termine</span>
    </button>
    <button class="nav-btn" id="nav2" onclick="goTab(2)">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
      </svg>
      <span class="nav-label">Profil</span>
    </button>
  </nav>

</div><!-- /app -->

<!-- TOAST -->
<div class="save-toast" id="saveToast">Gespeichert ✓</div>

<!-- CHAT SHEET -->
<div class="sheet-overlay" id="sheetOverlay" onclick="closeChat()"></div>
<div class="chat-sheet" id="chatSheet">
  <div class="sheet-drag"></div>
  <div class="sheet-title">KI-Assistent Chat</div>
  <div class="chat-msgs" id="chatMsgs"></div>
  <div class="chat-input-row">
    <input class="chat-input" id="chatInput" type="text"
           placeholder="Symptome beschreiben..."
           onkeydown="if(event.key==='Enter'){event.preventDefault();sendChat();}">
    <button class="send-btn" id="chatSend" onclick="sendChat()">
      <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
      </svg>
    </button>
  </div>
</div>

</div><!-- /screen -->
</div><!-- /phone -->

<script>
const D = __DATA__;

// global util — überall benötigt
function escHtml(s){
  return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// ── state ──
let curTab = 0, curSub = 'impfpass';
let calYear, calMonth, calSelected = null;

// ── tab navigation ──
function goTab(i) {
  document.querySelectorAll('.subpage').forEach(el => el.classList.remove('open'));
  closeCal();
  closeChat();
  curTab = i;
  document.getElementById('track').style.transform = `translateX(-${i*33.3333}%)`;
  [0,1,2].forEach(j => document.getElementById('nav'+j).classList.toggle('active', j===i));
}

// ── sub-tabs ──
function showSub(name) {
  curSub = name;
  ['impfpass','vorsorge'].forEach(n => {
    document.getElementById('sec-'+n).classList.toggle('visible', n===name);
    document.getElementById('pill-'+n).classList.toggle('active', n===name);
  });
}

// ── sub-pages ──
function openSP(id)  { document.getElementById(id).classList.add('open'); }
function closeSP(id) { document.getElementById(id).classList.remove('open'); }

// ── chat ──
function openChat()  {
  document.getElementById('sheetOverlay').classList.add('open');
  document.getElementById('chatSheet').classList.add('open');
}
function closeChat() {
  document.getElementById('sheetOverlay').classList.remove('open');
  document.getElementById('chatSheet').classList.remove('open');
}

// ── swipe ──
const vp = document.getElementById('vp');
let tx=0, ty=0;
vp.addEventListener('touchstart', e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;},{passive:true});
vp.addEventListener('touchend', e=>{
  const dx=e.changedTouches[0].clientX-tx, dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)&&Math.abs(dx)>44){
    if(dx<0&&curTab<2) goTab(curTab+1);
    if(dx>0&&curTab>0) goTab(curTab-1);
  }
},{passive:true});
let mx=null;
vp.addEventListener('mousedown',e=>{mx=e.clientX;});
window.addEventListener('mouseup',e=>{
  if(mx===null)return;
  const dx=e.clientX-mx;
  if(Math.abs(dx)>44){
    if(dx<0&&curTab<2) goTab(curTab+1);
    if(dx>0&&curTab>0) goTab(curTab-1);
  }
  mx=null;
});

// ════ CALENDAR ════
const DE_MONTHS = ['Januar','Februar','März','April','Mai','Juni',
                   'Juli','August','September','Oktober','November','Dezember'];

// Build appointment map: "YYYY-M-D" → appointment object
let aptMap = {};
function rebuildAptMap(){
  aptMap = {};
  (D.appointments||[]).forEach(a => {
    const d = new Date(a.date);
    aptMap[`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`] = a;
  });
}
rebuildAptMap();

function openCal() {
  // open to month with next upcoming apt, fallback to current month
  const now = new Date(); now.setHours(0,0,0,0);
  const next = (D.appointments||[])
    .map(a=>new Date(a.date))
    .filter(d=>!isNaN(d) && d>=now)
    .sort((a,b)=>a-b)[0];
  const ref = next || new Date();
  calYear = ref.getFullYear(); calMonth = ref.getMonth();
  calSelected = null;
  renderCal();
  document.getElementById('calOverlay').classList.add('open');
}
function closeCal() {
  document.getElementById('calOverlay').classList.remove('open');
}
function changeMonth(delta) {
  calMonth += delta;
  if(calMonth > 11){calMonth=0;calYear++;}
  if(calMonth < 0) {calMonth=11;calYear--;}
  calSelected = null;
  renderCal();
}

function renderCal() {
  document.getElementById('calMonthLabel').textContent = `${DE_MONTHS[calMonth]} ${calYear}`;
  const today = new Date();
  // First day of month (0=Sun…6=Sat), convert to Mon-based (0=Mon)
  const firstDow = (new Date(calYear, calMonth, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(calYear, calMonth+1, 0).getDate();
  let html = '';
  for(let i=0;i<firstDow;i++) html += '<div class="cal-day empty"></div>';
  for(let d=1;d<=daysInMonth;d++){
    const key = `${calYear}-${calMonth}-${d}`;
    const apt = aptMap[key];
    const isToday = (d===today.getDate()&&calMonth===today.getMonth()&&calYear===today.getFullYear());
    const isSel = (calSelected===d);
    let cls = 'cal-day';
    if(isToday) cls += ' today';
    if(apt)     cls += ' has-apt';
    if(isSel)   cls += ' selected';
    const click = apt ? `onclick="selectDay(${d})"` : '';
    html += `<div class="${cls}" ${click}>${d}${apt?'<div class="cal-dot"></div>':''}</div>`;
  }
  document.getElementById('calDays').innerHTML = html;
  if(calSelected) showAptDetail(calSelected);
  else document.getElementById('calDetail').innerHTML =
    '<div class="cal-hint">Tag mit Termin antippen für Details</div>';
}

function selectDay(d) {
  calSelected = d;
  renderCal();
}

function showAptDetail(d) {
  const key = `${calYear}-${calMonth}-${d}`;
  const a = aptMap[key];
  if(!a) return;
  const dateObj = new Date(a.date);
  const dateStr = dateObj.toLocaleDateString('de-DE',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  document.getElementById('calDetail').innerHTML = `
    <div class="apt-detail-card">
      <div class="apt-detail-name">${a.title}</div>
      <div class="apt-detail-row">
        <span class="apt-detail-icon">🕐</span>
        <span class="apt-detail-text">${dateStr}, ${a.time} Uhr</span>
      </div>
      <div class="apt-detail-row">
        <span class="apt-detail-icon">👨‍⚕️</span>
        <span class="apt-detail-text">${a.doctor}</span>
      </div>
      <div class="apt-detail-row">
        <span class="apt-detail-icon">📍</span>
        <span class="apt-detail-text">${a.address}</span>
      </div>
      <div class="${a.confirmed?'apt-badge confirmed':'apt-badge unconfirmed'}">
        ${a.confirmed?'✓ Bestätigt':'⏳ Ausstehend'}
      </div>
    </div>`;
}

// ════ RENDER: next appointment label ════
function renderNextApt(){
  const now = new Date(); now.setHours(0,0,0,0);
  const next = (D.appointments||[])
    .map(a=>({...a,_d:new Date(a.date)}))
    .filter(a=>a._d>=now)
    .sort((a,b)=>a._d-b._d)[0];
  const el = document.getElementById('aptTime');
  if(next){
    const ds = next._d.toLocaleDateString('de-DE',{weekday:'short',day:'numeric',month:'short'});
    el.textContent = `${ds}, ${next.time} Uhr`;
  } else {
    el.textContent = 'Kein anstehender Termin';
  }
}
renderNextApt();

// ════ RENDER: profile name ════
document.getElementById('homeGreeting').textContent = `Hallo ${D.user.name}!`;
document.getElementById('profilName').textContent = D.user.name;

// ════ RENDER: vaccinations ════
function renderImpfpass(){
  document.getElementById('vaccCount').textContent = D.vaccinations.length;
  document.getElementById('vaccList').innerHTML = D.vaccinations.map(v=>{
    const done = v.status==='complete';
    let dueCls = '';
    if(v.status==='due_now')    dueCls = ' overdue';
    if(v.status==='incomplete') dueCls = ' overdue';
    if(v.status==='due_soon')   dueCls = ' soon';
    return `<div class="vacc-card">
      <div class="vacc-row">
        <span class="vacc-name${done?' grey':''}">${escHtml(v.name)}</span>
        ${v.due_text?`<span class="vacc-due${dueCls}">${escHtml(v.due_text)}</span>`:''}
      </div>
      <div class="vacc-sub${done?' grey':''}">${escHtml(v.subtitle||'')}${v.last?'<br>Letzte Impfung: '+escHtml(v.last):''}</div>
    </div>`;
  }).join('');
}
renderImpfpass();

// ════ RENDER: vorsorge ════
function renderVorsorge(){
  document.getElementById('vorsList').innerHTML = (D.vorsorge||[]).map(v=>`
    <div class="vors-card">
      <div class="vors-icon">${v.icon||'🩺'}</div>
      <div class="vors-body">
        <div class="vors-name">${escHtml(v.name)}</div>
        <div class="vors-meta">
          <span class="vors-date">Fällig: ${escHtml(v.due_date||'')}</span>
          <span class="vors-time">${escHtml(v.due_text||'')}</span>
        </div>
      </div>
      ${v.checked?'<div class="vors-check">✓</div>':''}
    </div>`).join('');
  document.getElementById('pastList').innerHTML = (D.vergangene_vorsorge||[]).map(v=>`
    <div class="past-card">
      <div class="past-name">${escHtml(v.name)}</div>
      <div class="past-date">Fällig: ${escHtml(v.due_date||'')}</div>
    </div>`).join('');
}
renderVorsorge();

// ════ CSV IMPORT (Impfpass / Vorsorge) ════
const DEFAULT_VACCS  = JSON.parse(JSON.stringify(D.vaccinations || []));
const DEFAULT_VORS   = JSON.parse(JSON.stringify(D.vorsorge || []));
const DEFAULT_APTS   = JSON.parse(JSON.stringify(D.appointments || []));
const DE_MONTHS_SH   = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];

// load from storage on init
(function loadImports(){
  try {
    const v = JSON.parse(localStorage.getItem('vc_imp_data')||'null');
    if(Array.isArray(v)) D.vaccinations = v;
  } catch(e){}
  try {
    const v = JSON.parse(localStorage.getItem('vc_vors_data')||'null');
    if(Array.isArray(v)) D.vorsorge = v;
    const a = JSON.parse(localStorage.getItem('vc_apts_data')||'null');
    if(Array.isArray(a)) D.appointments = a;
  } catch(e){}
})();
rebuildAptMap();
renderImpfpass();
renderVorsorge();
renderNextApt();
renderImportMeta();

// ── CSV parser ──
function detectDelim(text){
  const line = (text.split(/\r?\n/)[0] || '');
  const c = (line.match(/,/g)||[]).length;
  const s = (line.match(/;/g)||[]).length;
  const t = (line.match(/\t/g)||[]).length;
  if(s >= c && s >= t) return ';';
  if(t >= c) return '\t';
  return ',';
}
function parseCsv(text){
  text = text.replace(/^﻿/, '');
  const delim = detectDelim(text);
  const rows = [];
  let i = 0, field = '', row = [], inQ = false;
  while(i < text.length){
    const c = text[i];
    if(inQ){
      if(c === '"'){
        if(text[i+1] === '"'){ field += '"'; i += 2; continue; }
        inQ = false; i++; continue;
      }
      field += c; i++; continue;
    }
    if(c === '"'){ inQ = true; i++; continue; }
    if(c === delim){ row.push(field); field = ''; i++; continue; }
    if(c === '\r'){ i++; continue; }
    if(c === '\n'){ row.push(field); rows.push(row); row=[]; field=''; i++; continue; }
    field += c; i++;
  }
  if(field.length || row.length){ row.push(field); rows.push(row); }
  return rows.filter(r => r.some(c => (c||'').trim() !== ''));
}
function csvToObjects(text){
  const rows = parseCsv(text);
  if(rows.length < 2) return [];
  const headers = rows[0].map(h => h.trim().toLowerCase()
    .replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/ß/g,'ss')
    .replace(/[^a-z0-9_]/g,'_'));
  return rows.slice(1).map(r => {
    const o = {};
    headers.forEach((h,i)=> o[h] = ((r[i]==null?'':r[i])+'').trim());
    return o;
  });
}
function pick(o, ...keys){
  for(const k of keys){ if(o[k]!=null && o[k]!=='') return o[k]; }
  return '';
}
function parseDate(s){
  if(!s) return null;
  if(/^\d{4}-\d{2}-\d{2}/.test(s)) return new Date(s);
  let m = s.match(/^(\d{1,2})\.(\d{1,2})\.(\d{2,4})/);
  if(m){
    const yr = m[3].length===2 ? '20'+m[3] : m[3];
    return new Date(`${yr}-${m[2].padStart(2,'0')}-${m[1].padStart(2,'0')}`);
  }
  m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})/);
  if(m){
    const yr = m[3].length===2 ? '20'+m[3] : m[3];
    return new Date(`${yr}-${m[1].padStart(2,'0')}-${m[2].padStart(2,'0')}`);
  }
  return null;
}

// ── mappers ──
function fmtDueText(daysUntil){
  if(daysUntil < 0){
    const d = Math.abs(daysUntil);
    if(d < 31) return `überfällig seit ${d} Tag${d===1?'':'en'}`;
    const m = Math.round(d/30);
    if(m < 12) return `überfällig seit ${m} Monat${m===1?'':'en'}`;
    return `überfällig seit ${(d/365).toFixed(1)} Jahren`;
  }
  if(daysUntil < 14)  return `in ${daysUntil} Tag${daysUntil===1?'':'en'} fällig`;
  if(daysUntil < 60)  return `in ${Math.round(daysUntil/7)} Wochen fällig`;
  if(daysUntil < 365) return `in ${Math.round(daysUntil/30)} Monaten fällig`;
  return `in ${(daysUntil/365).toFixed(1)} Jahren fällig`;
}

function statusFromDays(daysUntil){
  if(daysUntil < 0)   return 'due_now';
  if(daysUntil < 90)  return 'due_soon';
  if(daysUntil < 365) return 'due_later';
  return 'complete';
}

function parseBool(s){
  if(s==null || s==='') return undefined;
  const v = String(s).trim().toLowerCase();
  if(['nein','no','false','0','unvollstaendig','unvollständig','incomplete'].includes(v)) return false;
  if(['ja','yes','true','1','vollstaendig','vollständig','complete','ok'].includes(v)) return true;
  return undefined;
}

function addInterval(date, years){
  // years kann dezimal sein (z.B. 0.5 = 6 monate)
  const next = new Date(date);
  const wholeYears = Math.floor(years);
  next.setFullYear(next.getFullYear() + wholeYears);
  const extraMonths = Math.round((years - wholeYears) * 12);
  if(extraMonths) next.setMonth(next.getMonth() + extraMonths);
  return next;
}

function mapImpfpass(rows){
  const today = new Date(); today.setHours(0,0,0,0);
  return rows.map(r => {
    const name = pick(r,'name','impfung','krankheit','vaccination','disease');
    if(!name) return null;

    const lastStr  = pick(r,'letzte_impfung','last','datum','date');
    const lastDate = parseDate(lastStr);

    const intervalRaw = pick(r,'intervall_jahre','intervall','auffrischung_jahre',
                                'interval_years','interval','jahre','years');
    const interval = parseFloat(String(intervalRaw||'').replace(',','.'));

    const vollst = parseBool(pick(r,'vollstaendig','vollständig','complete','complet','status'));

    let due_text = '';
    let status   = '';

    // 1. unvollständig hat priorität
    if(vollst === false){
      status   = 'incomplete';
      due_text = 'unvollständig';
    }
    // 2. letzte impfung + intervall → nächste fällig berechnen
    else if(lastDate && !isNaN(interval) && interval > 0){
      const next = addInterval(lastDate, interval);
      const days = Math.round((next - today) / (1000*60*60*24));
      due_text = fmtDueText(days);
      status   = statusFromDays(days);
    }
    // 3. kein intervall (= lebenslang vollständig)
    else {
      status = 'complete';
    }

    // subtitle: zeigt "vollständig" / "unvollständig" / Auffrischung
    let subtitle;
    if(status === 'incomplete'){
      subtitle = lastStr ? `letzte Impfung ${lastStr}, unvollständig` : 'unvollständig';
    } else if(status === 'complete'){
      subtitle = lastStr ? `letzte Impfung ${lastStr}, vollständig` : 'vollständig';
    } else {
      // due_now / due_soon / due_later → noch wirksam aber bald
      subtitle = lastStr ? `letzte Impfung ${lastStr}` : 'Auffrischung fällig';
    }

    const obj = { name, subtitle, status };
    if(lastStr && status !== 'complete') obj.last = lastStr;
    if(status !== 'complete' && due_text) obj.due_text = due_text;
    return obj;
  }).filter(Boolean);
}
function mapVorsorge(rows){
  const vors = [], apts = [];
  rows.forEach(r => {
    const name = pick(r,'name','title','titel');
    if(!name) return;
    const dateStr = pick(r,'datum','date');
    const time = pick(r,'uhrzeit','time') || '09:00';
    const doctor = pick(r,'arzt','doctor');
    const address = pick(r,'adresse','address');
    const dueText = pick(r,'faellig_text','due_text','faellig','due');
    const icon = pick(r,'icon') || '🩺';

    const d = parseDate(dateStr);
    const dueDate = d ? `${DE_MONTHS_SH[d.getMonth()]} ${d.getFullYear()}` : '';
    vors.push({ name, icon, due_date: dueDate, due_text: dueText, checked: false });
    if(d){
      apts.push({
        date: d.toISOString().slice(0,10),
        title: name,
        doctor: doctor || '',
        address: address || '',
        time,
        confirmed: true
      });
    }
  });
  return { vors, apts };
}

// ── upload handler ──
function handleUpload(ev, kind){
  const file = ev.target.files[0];
  if(!file) return;
  const isCsv = /\.csv$/i.test(file.name) || file.type === 'text/csv';
  if(!isCsv){
    showToast('Bitte CSV-Datei hochladen');
    ev.target.value = ''; return;
  }
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const rows = csvToObjects(e.target.result);
      console.log(`[CSV ${kind}] parsed ${rows.length} rows. headers:`, Object.keys(rows[0]||{}));
      console.log(`[CSV ${kind}] first row:`, rows[0]);
      if(!rows.length){
        showToast('CSV leer oder nur Header');
        ev.target.value = ''; return;
      }
      if(kind === 'impfpass'){
        const vaccs = mapImpfpass(rows);
        console.log(`[CSV impfpass] mapped ${vaccs.length} vaccs:`, vaccs);
        if(!vaccs.length){
          showToast('Keine gültigen Impfdaten gefunden');
          ev.target.value = ''; return;
        }
        D.vaccinations = vaccs;
        try {
          localStorage.setItem('vc_imp_data', JSON.stringify(vaccs));
          localStorage.setItem('vc_imp_meta', JSON.stringify(
            {filename: file.name, count: vaccs.length, when: new Date().toISOString()}));
        } catch(se){ console.warn('localStorage save failed:', se); }
        renderImpfpass();
        renderImportMeta();
        showToast(`${vaccs.length} Impfungen importiert`);
      } else {
        const {vors, apts} = mapVorsorge(rows);
        console.log(`[CSV vorsorge] mapped vors=${vors.length}, apts=${apts.length}`);
        console.log('[CSV vorsorge] vors:', vors);
        console.log('[CSV vorsorge] apts:', apts);
        if(!vors.length){
          showToast('Keine gültigen Vorsorge-Daten');
          ev.target.value = ''; return;
        }
        D.vorsorge = vors;
        D.appointments = apts;
        try {
          localStorage.setItem('vc_vors_data', JSON.stringify(vors));
          localStorage.setItem('vc_apts_data', JSON.stringify(apts));
          localStorage.setItem('vc_vors_meta', JSON.stringify(
            {filename: file.name, count: vors.length, when: new Date().toISOString()}));
        } catch(se){ console.warn('localStorage save failed:', se); }
        renderVorsorge();
        rebuildAptMap();
        renderNextApt();
        if(document.getElementById('calOverlay').classList.contains('open')) renderCal();
        renderImportMeta();
        showToast(`${vors.length} Termine importiert`);
      }
    } catch(err){
      console.error('[CSV] error:', err);
      showToast('CSV-Fehler: ' + (err.message || err));
    }
    ev.target.value = '';
  };
  reader.onerror = () => { showToast('Fehler beim Lesen der Datei'); ev.target.value=''; };
  reader.readAsText(file, 'UTF-8');
}

function resetImport(kind){
  if(!confirm('Import zurücksetzen und Standard-Daten wiederherstellen?')) return;
  if(kind === 'impfpass'){
    D.vaccinations = JSON.parse(JSON.stringify(DEFAULT_VACCS));
    localStorage.removeItem('vc_imp_data');
    localStorage.removeItem('vc_imp_meta');
    renderImpfpass();
  } else {
    D.vorsorge = JSON.parse(JSON.stringify(DEFAULT_VORS));
    D.appointments = JSON.parse(JSON.stringify(DEFAULT_APTS));
    localStorage.removeItem('vc_vors_data');
    localStorage.removeItem('vc_apts_data');
    localStorage.removeItem('vc_vors_meta');
    renderVorsorge();
    rebuildAptMap();
    renderNextApt();
    if(document.getElementById('calOverlay').classList.contains('open')) renderCal();
  }
  renderImportMeta();
  showToast('Zurückgesetzt');
}

function renderImportMeta(){
  ['impfpass','vorsorge'].forEach(kind=>{
    const box = document.getElementById('meta-'+kind);
    if(!box) return;
    const key = kind === 'impfpass' ? 'vc_imp_meta' : 'vc_vors_meta';
    let meta = null;
    try { meta = JSON.parse(localStorage.getItem(key)||'null'); } catch(e){}
    if(!meta){ box.innerHTML = ''; return; }
    const dt = new Date(meta.when).toLocaleDateString('de-DE',
      {day:'2-digit',month:'2-digit',year:'numeric'});
    box.innerHTML = `<div class="import-meta">
      <span>✓ Importiert: <strong>${escHtml(meta.filename)}</strong> · ${meta.count} Einträge · ${dt}</span>
      <button class="reset-btn" onclick="resetImport('${kind}')">Zurücksetzen</button>
    </div>`;
  });
}

// ════ RENDER: profile / gesundheitsdaten ════
const PROFILE_DEFAULT = D.profile;

function normalizeProfile(raw){
  const def = JSON.parse(JSON.stringify(PROFILE_DEFAULT));
  const p   = Object.assign(def, raw || {});
  // list fields must be arrays
  ['vorerkrankungen','allergien'].forEach(k=>{
    if(!Array.isArray(p[k])){
      if(typeof p[k]==='string' && p[k].trim() && p[k].trim().toLowerCase()!=='keine'){
        p[k] = p[k].split(',').map(s=>s.trim()).filter(Boolean);
      } else {
        p[k] = [];
      }
    }
  });
  if(!Array.isArray(p.familienanamnese)) p.familienanamnese = [];
  // yes-no fields: migrate old keys (raucht/trinkt) → ja
  ['rauchen','alkohol'].forEach(k=>{
    const v = p[k];
    if(!v || typeof v!=='object'){ p[k]={ja:false,haeufigkeit:''}; return; }
    if(v.ja===undefined){
      const ja = !!(v.raucht || v.trinkt);
      p[k] = { ja, haeufigkeit: v.haeufigkeit || '' };
    } else {
      p[k] = { ja: !!v.ja, haeufigkeit: v.haeufigkeit || '' };
    }
  });
  // strings
  ['geburtsdatum','geschlecht','sportverhalten','ernaehrung','gewicht','groesse'].forEach(k=>{
    if(p[k]==null) p[k]='';
    else p[k] = String(p[k]);
  });
  return p;
}

let P;
try {
  const s = localStorage.getItem('vc_profile');
  P = normalizeProfile(s ? JSON.parse(s) : D.profile);
} catch(e){
  console.warn('profile load failed, falling back to defaults:', e);
  P = normalizeProfile(D.profile);
}

function saveP(){
  try {
    localStorage.setItem('vc_profile', JSON.stringify(P));
    return true;
  } catch(e){
    console.error('saveP failed:', e);
    showToast('Fehler beim Speichern');
    return false;
  }
}
// persist normalized shape immediately (cleans up legacy data)
saveP();

function showToast(msg){
  const t = document.getElementById('saveToast');
  t.textContent = msg || 'Gespeichert ✓';
  t.classList.add('show');
  clearTimeout(showToast._t);
  showToast._t = setTimeout(()=>t.classList.remove('show'), 1600);
}


const SPORT_OPTS      = ['gar kein','wenig','mittel','viel','sehr viel'];
const ERNAEHRUNG_OPTS = ['vegan','vegetarisch','fleisch'];
const GESCHLECHT_OPTS = [['m','Männlich'],['w','Weiblich'],['d','Divers']];

const FIELDS = [
  {section:'Allgemeines',          key:'geburtsdatum',     label:'Geburtsdatum',                  icon:'🎂', type:'date'},
  {section:'Allgemeines',          key:'geschlecht',       label:'Geschlecht',                    icon:'🚻', type:'choice',    opts:GESCHLECHT_OPTS},
  {section:'Gesundheitsgeschichte',key:'vorerkrankungen',  label:'Vorerkrankungen',               icon:'🧬', type:'list-str',  ph:'z.B. Asthma'},
  {section:'Gesundheitsgeschichte',key:'familienanamnese', label:'Familiäre Vorerkrankungen',     icon:'👨‍👩‍👧', type:'list-pair', ph:['Verwandter','Erkrankung']},
  {section:'Gesundheitsgeschichte',key:'allergien',        label:'Allergien',                     icon:'⚠️', type:'list-str',  ph:'z.B. Pollen, Nüsse'},
  {section:'Lebensstil',           key:'sportverhalten',   label:'Sportverhalten',                icon:'🏃', type:'dropdown',  opts:SPORT_OPTS},
  {section:'Lebensstil',           key:'ernaehrung',       label:'Ernährung',                     icon:'🥗', type:'dropdown',  opts:ERNAEHRUNG_OPTS},
  {section:'Lebensstil',           key:'rauchen',          label:'Rauchverhalten',                icon:'🚭', type:'yesno',     extraLabel:'Wie häufig?'},
  {section:'Lebensstil',           key:'alkohol',          label:'Alkoholkonsum',                 icon:'🍷', type:'yesno',     extraLabel:'Wie häufig?'},
  {section:'Biometrie',            key:'gewicht',          label:'Gewicht',                       icon:'⚖️', type:'unit',      unit:'kg'},
  {section:'Biometrie',            key:'groesse',          label:'Größe',                         icon:'📏', type:'unit',      unit:'cm'}
];

const SECTION_ORDER = ['Allgemeines','Gesundheitsgeschichte','Lebensstil','Biometrie'];

function cap(s){ return s ? s.charAt(0).toUpperCase()+s.slice(1) : s; }
function esc(s){ return String(s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function fmtVal(f){
  try {
    const v = P[f.key];
    switch(f.type){
      case 'date':      return v || '—';
      case 'text':      return v || '—';
      case 'unit':      return (v!==''&&v!=null) ? `${v} ${f.unit}` : '—';
      case 'choice':    { const m=f.opts.find(o=>o[0]===v); return m?m[1]:'—'; }
      case 'dropdown':  return v ? cap(v) : '—';
      case 'list-str':  return (Array.isArray(v) && v.length) ? v.join(', ') : 'Keine Einträge';
      case 'list-pair': return (Array.isArray(v) && v.length)
                          ? v.map(x=>`${x&&x.verwandter||'?'}: ${x&&x.erkrankung||'?'}`).join(', ')
                          : 'Keine Einträge';
      case 'yesno':     return v && v.ja ? `Ja${v.haeufigkeit?', '+v.haeufigkeit:''}` : 'Nein';
    }
  } catch(e){ console.warn('fmtVal err:', f.key, e); }
  return '—';
}

function renderHealth(){
 try {
  let html = `
    <div class="epa-btn" onclick="showEpaInfo()">
      <span class="epa-icon">📋</span>
      <div class="epa-text">
        <div class="epa-title-t">EPA importieren</div>
        <div class="epa-sub">Elektronische Patientenakte verknüpfen</div>
      </div>
      <span class="epa-arrow">›</span>
    </div>
    `;
  SECTION_ORDER.forEach(sec=>{
    html += `<div class="health-card"><div class="health-card-title">${sec}</div>`;
    FIELDS.filter(f=>f.section===sec).forEach((f,i)=>{
      const fi = FIELDS.indexOf(f);
      html += `<div class="health-row" onclick="openField(${fi})">
        <div class="h-row-top">
          <span class="h-icon">${f.icon}</span>
          <span class="h-label">${f.label}</span>
          <span class="h-arrow">›</span>
        </div>
        <div class="h-val">${esc(fmtVal(f))}</div>
      </div>`;
    });
    html += `</div>`;
  });
  document.getElementById('gesundheitContent').innerHTML = html;
 } catch(e){
  console.error('renderHealth crash:', e);
  document.getElementById('gesundheitContent').innerHTML =
    `<div style="padding:30px 20px;text-align:center;color:#888;font-size:14px;">
       Fehler beim Laden der Daten.<br><br>
       <button class="backup-btn" style="margin-top:10px;" onclick="resetProfile()">Profil zurücksetzen</button>
     </div>`;
 }
}

function resetProfile(){
  if(!confirm('Profil-Daten wirklich zurücksetzen?')) return;
  P = normalizeProfile(null);
  const ok = saveP();
  renderHealth();
  if(ok) showToast('Zurückgesetzt');
}

// ── edit page ──
let editingIdx = -1;

function openField(i){
  editingIdx = i;
  const f = FIELDS[i];
  document.getElementById('sp-field-title').textContent = f.label;
  document.getElementById('sp-field-content').innerHTML = buildForm(f);
  if(f.type==='yesno') ynToggle(P[f.key] && P[f.key].ja);
  openSP('sp-field');
}

function buildForm(f){
  const v = P[f.key];
  let body = '';
  switch(f.type){
    case 'date':
      body = `
        <div class="form-row">
          <label class="form-label">Geburtsdatum (TT.MM.JJJJ)</label>
          <input class="form-input" id="fld" type="text" inputmode="numeric"
                 placeholder="TT.MM.JJJJ" maxlength="10" value="${esc(v||'')}"
                 oninput="dateMask(this)">
        </div>`;
      break;
    case 'text':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <textarea class="form-input form-textarea" id="fld"
                    placeholder="${esc(f.ph||'')}">${esc(v||'')}</textarea>
        </div>`;
      break;
    case 'unit':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div class="input-row">
            <input class="form-input" id="fld" type="number" inputmode="decimal"
                   step="0.1" value="${esc(v||'')}">
            <span class="input-suffix">${esc(f.unit)}</span>
          </div>
        </div>`;
      break;
    case 'choice':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div class="choice-grid" id="fld">
            ${f.opts.map(([key,lbl])=>`
              <button type="button" class="choice-chip ${v===key?'active':''}"
                      data-val="${esc(key)}" onclick="chipPick(this)">${esc(lbl)}</button>`).join('')}
          </div>
        </div>`;
      break;
    case 'dropdown':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div class="dd-wrap">
            <select class="dd-select" id="fld">
              ${f.opts.map(o=>`<option value="${esc(o)}" ${v===o?'selected':''}>${esc(cap(o))}</option>`).join('')}
            </select>
            <span class="dd-arrow">▾</span>
          </div>
        </div>`;
      break;
    case 'yesno': {
      const ja = !!(v && v.ja);
      const hf = (v && v.haeufigkeit) || '';
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div class="choice-grid">
            <button type="button" class="choice-chip ${!ja?'active':''}" id="yn-no"  onclick="ynToggle(false)">Nein</button>
            <button type="button" class="choice-chip ${ ja?'active':''}" id="yn-yes" onclick="ynToggle(true)">Ja</button>
          </div>
          <div class="yn-extra ${ja?'':'hidden'}" id="yn-extra">
            <label class="form-label" style="margin-top:14px;">${esc(f.extraLabel||'Wie häufig?')}</label>
            <input class="form-input" id="fld" type="text"
                   placeholder="z.B. 5 pro Woche" value="${esc(hf)}">
          </div>
        </div>`;
      break;
    }
    case 'list-str':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div id="list-box"></div>
          <button type="button" class="list-add" onclick="listAddStr()">+ Eintrag hinzufügen</button>
        </div>`;
      break;
    case 'list-pair':
      body = `
        <div class="form-row">
          <label class="form-label">${esc(f.label)}</label>
          <div id="list-box"></div>
          <button type="button" class="list-add" onclick="listAddPair()">+ Eintrag hinzufügen</button>
        </div>`;
      break;
  }
  const html = `
    <div class="form-pad">
      <div class="field-hero">
        <div class="field-big-icon">${f.icon}</div>
        <div class="field-big-label">${esc(f.label)}</div>
      </div>
      ${body}
      <button class="save-btn" onclick="saveField()">Speichern</button>
    </div>`;
  // post-mount list rendering
  setTimeout(()=>{
    if(f.type==='list-str')  renderListStr();
    if(f.type==='list-pair') renderListPair();
  },0);
  return html;
}

// ── chip / yes-no ──
function chipPick(btn){
  btn.parentElement.querySelectorAll('.choice-chip').forEach(c=>c.classList.remove('active'));
  btn.classList.add('active');
}
function ynToggle(yes){
  document.getElementById('yn-yes').classList.toggle('active', yes);
  document.getElementById('yn-no').classList.toggle('active', !yes);
  document.getElementById('yn-extra').classList.toggle('hidden', !yes);
}

// ── date input mask DD.MM.YYYY ──
function dateMask(el){
  let s = el.value.replace(/\D/g,'').slice(0,8);
  if(s.length>4) s = s.slice(0,2)+'.'+s.slice(2,4)+'.'+s.slice(4);
  else if(s.length>2) s = s.slice(0,2)+'.'+s.slice(2);
  el.value = s;
}

// ── list editors ──
let _listStr = [];
let _listPair = [];

function renderListStr(){
  _listStr = (P[FIELDS[editingIdx].key] || []).slice();
  const ph = FIELDS[editingIdx].ph || '';
  const box = document.getElementById('list-box');
  if(!_listStr.length){
    box.innerHTML = `<div class="empty-hint">Noch keine Einträge — füge unten welche hinzu</div>`;
    return;
  }
  box.innerHTML = _listStr.map((v,i)=>`
    <div class="list-item">
      <input type="text" placeholder="${esc(ph)}" value="${esc(v)}"
             oninput="_listStr[${i}]=this.value">
      <button type="button" class="list-rm" onclick="listRmStr(${i})">×</button>
    </div>`).join('');
}
function listAddStr(){ _listStr.push(''); _listRedrawStr(); }
function listRmStr(i){ _listStr.splice(i,1); _listRedrawStr(); }
function _listRedrawStr(){
  const ph = FIELDS[editingIdx].ph || '';
  const box = document.getElementById('list-box');
  if(!_listStr.length){
    box.innerHTML = `<div class="empty-hint">Noch keine Einträge — füge unten welche hinzu</div>`;
    return;
  }
  box.innerHTML = _listStr.map((v,i)=>`
    <div class="list-item">
      <input type="text" placeholder="${esc(ph)}" value="${esc(v)}"
             oninput="_listStr[${i}]=this.value">
      <button type="button" class="list-rm" onclick="listRmStr(${i})">×</button>
    </div>`).join('');
}

function renderListPair(){
  _listPair = (P[FIELDS[editingIdx].key] || []).map(x=>({...x}));
  _listRedrawPair();
}
function listAddPair(){ _listPair.push({verwandter:'',erkrankung:''}); _listRedrawPair(); }
function listRmPair(i){ _listPair.splice(i,1); _listRedrawPair(); }
function _listRedrawPair(){
  const [ph1,ph2] = FIELDS[editingIdx].ph || ['',''];
  const box = document.getElementById('list-box');
  if(!_listPair.length){
    box.innerHTML = `<div class="empty-hint">Noch keine Einträge — füge unten welche hinzu</div>`;
    return;
  }
  box.innerHTML = _listPair.map((x,i)=>`
    <div class="list-item">
      <input type="text" placeholder="${esc(ph1)}" value="${esc(x.verwandter)}"
             oninput="_listPair[${i}].verwandter=this.value" style="max-width:38%;">
      <input type="text" placeholder="${esc(ph2)}" value="${esc(x.erkrankung)}"
             oninput="_listPair[${i}].erkrankung=this.value">
      <button type="button" class="list-rm" onclick="listRmPair(${i})">×</button>
    </div>`).join('');
}

// ── save ──
function saveField(){
  const f = FIELDS[editingIdx];
  const fld = document.getElementById('fld');
  switch(f.type){
    case 'date':
    case 'text':
      P[f.key] = fld ? fld.value.trim() : '';
      break;
    case 'unit':
      P[f.key] = fld ? fld.value.trim() : '';
      break;
    case 'choice': {
      const a = document.querySelector('#fld .choice-chip.active');
      P[f.key] = a ? a.dataset.val : '';
      break;
    }
    case 'dropdown':
      P[f.key] = fld ? fld.value : '';
      break;
    case 'yesno': {
      const ja = document.getElementById('yn-yes').classList.contains('active');
      P[f.key] = { ja, haeufigkeit: ja && fld ? fld.value.trim() : '' };
      break;
    }
    case 'list-str':
      P[f.key] = _listStr.map(s=>s.trim()).filter(Boolean);
      break;
    case 'list-pair':
      P[f.key] = _listPair
        .map(x=>({verwandter:(x.verwandter||'').trim(),erkrankung:(x.erkrankung||'').trim()}))
        .filter(x=>x.verwandter||x.erkrankung);
      break;
  }
  const ok = saveP();
  renderHealth();
  closeSP('sp-field');
  if(ok) showToast('Gespeichert ✓');
}

function showEpaInfo(){
  document.getElementById('sp-field-title').textContent = 'EPA Import';
  document.getElementById('sp-field-content').innerHTML = `
    <div class="field-detail-inner">
      <div class="field-big-icon">📋</div>
      <div class="field-big-label">Elektronische Patientenakte</div>
      <div class="field-big-value" style="font-size:16px;font-weight:500;color:#555;padding-top:14px;">
        Verbinde deine EPA (gematik TI) um Gesundheitsdaten automatisch zu importieren.<br><br>
        <span style="color:#1c3d5e;font-weight:700;">Demnächst verfügbar</span>
      </div>
    </div>`;
  openSP('sp-field');
}

renderHealth();

// ════ N8N WEBHOOKS ════
const N8N_ENDPOINT       = 'https://n8n.docyet.com/webhook/39725f70-869a-46db-af4f-0849ace6af5c';      // demo-button → start
const N8N_CHAT_ENDPOINT  = 'https://n8n.docyet.com/webhook/vitalcheck-chat';                           // chat-reply → folgenachrichten
const N8N_FINAL_ENDPOINT = 'https://n8n.docyet.com/webhook/d4feaf85-29a4-4c5b-a10d-48f7a7e83f7d';      // letzter workflow

// ── LETZTER WORKFLOW (URL 3) ──
async function triggerFinal(){
  const btn    = document.getElementById('finalBtn');
  const status = document.getElementById('demoStatus');
  btn.disabled = true;
  status.className = 'demo-status';
  status.innerHTML = '<span class="demo-spinner"></span>Letzter Workflow läuft...';

  // bestehende session weiternutzen falls vorhanden, sonst neu
  if(!sessionId) sessionId = newSessionId();

  // typing in chat während wir warten — chat öffnen falls noch zu
  chatMessages.push({role:'typing'});
  renderChat();
  if(!document.getElementById('chatSheet').classList.contains('open')) openChat();

  try {
    const res = await fetch(N8N_FINAL_ENDPOINT, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        event: 'final_workflow',
        sessionId,
        timestamp: new Date().toISOString(),
        user: D.user,
        profile: P
      })
    });
    if(!res.ok) throw new Error('HTTP ' + res.status);

    const ct = (res.headers.get('content-type') || '').toLowerCase();
    let reply;
    if(ct.includes('application/json')){
      reply = extractReply(await res.json());
    } else {
      reply = (await res.text()).trim();
    }
    if(!reply) reply = '(leere Antwort vom Workflow)';

    chatMessages = chatMessages.filter(m => m.role !== 'typing');
    chatMessages.push({role:'bot', text: reply});
    renderChat();

    status.className = 'demo-status ok';
    status.innerHTML = `✓ Letzter Workflow fertig<br>
      <span style="font-size:10px;color:#888;font-weight:500;">
        session: …${sessionId.slice(-8)}</span>`;
  } catch(e){
    chatMessages = chatMessages.filter(m => m.role !== 'typing');
    chatMessages.push({role:'bot', text: '⚠ Workflow-Fehler: ' + (e.message || e)});
    renderChat();
    status.className = 'demo-status err';
    status.textContent = '⚠ ' + (e.message || e);
  } finally {
    btn.disabled = false;
  }
}

// extrahiert text aus n8n response — egal ob json {reply|...}, plain text, oder array
function extractReply(data){
  if(typeof data === 'string') return data.trim();
  if(Array.isArray(data) && data.length) return extractReply(data[0]);
  if(data && typeof data === 'object'){
    return data.reply || data.text || data.message || data.output
        || data.answer || data.content
        || JSON.stringify(data);
  }
  return String(data);
}

// ── DEMO BUTTON ──
async function triggerDemo(){
  const btn    = document.getElementById('demoBtn');
  const status = document.getElementById('demoStatus');
  btn.disabled = true;

  // neue session: chat-memory wird damit getrennt vom vorigen run
  sessionId = newSessionId();
  console.log('new sessionId:', sessionId);

  status.className = 'demo-status';
  status.innerHTML = '<span class="demo-spinner"></span>Workflow läuft...';

  // chat öffnen + typing zeigen, während wir auf n8n warten
  chatMessages = [{role:'typing'}];
  renderChat();
  openChat();

  try {
    const res = await fetch(N8N_ENDPOINT, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        event: 'demo_start',
        sessionId,
        timestamp: new Date().toISOString(),
        user: D.user,
        profile: P
      })
    });
    if(!res.ok) throw new Error('HTTP ' + res.status);

    // antwort kann json oder text sein
    const ct = (res.headers.get('content-type') || '').toLowerCase();
    let reply;
    if(ct.includes('application/json')){
      reply = extractReply(await res.json());
    } else {
      reply = (await res.text()).trim();
    }
    if(!reply) reply = '(leere Antwort vom Workflow)';

    // typing entfernen, bot-message setzen — chat ist gestartet
    chatMessages = [{role:'bot', text: reply}];
    renderChat();

    status.className = 'demo-status ok';
    status.innerHTML = `✓ Workflow fertig<br>
      <span style="font-size:10px;color:#888;font-weight:500;word-break:break-all;">
        session: …${sessionId.slice(-8)}</span>`;
  } catch(e){
    chatMessages = chatMessages.filter(m => m.role !== 'typing');
    chatMessages.push({role:'bot', text: '⚠ Workflow-Fehler: ' + (e.message || e)});
    renderChat();
    status.className = 'demo-status err';
    status.textContent = '⚠ ' + (e.message || e);
  } finally {
    btn.disabled = false;
  }
}

// chat startet leer — erste nachricht kommt vom n8n workflow (siehe triggerDemo)
let chatMessages = [];
let chatBusy = false;
let sessionId = null;   // wird bei jedem demo-start neu generiert

// menschenlesbare session-id, einmal pro demo-start generiert
// memory-continuity innerhalb einer session = alle chat-replies + triggerFinal nutzen dieselbe id
function newSessionId(){
  return 'vitalcheck-' + Date.now();
}

// minimaler markdown-renderer für bot-messages: **bold**, bullets, line breaks
function renderMd(text){
  let s = escHtml(String(text));
  // **bold**
  s = s.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');
  // line breaks
  s = s.replace(/\n/g, '<br>');
  // bullets "- " am zeilenanfang → •
  s = s.replace(/(^|<br>)\s*-\s+/g, '$1• ');
  return s;
}

function renderChat(){
  const box = document.getElementById('chatMsgs');
  if(!chatMessages.length){
    box.innerHTML = `<div style="text-align:center;color:#aaa;font-size:13px;
      padding:40px 24px;line-height:1.5;">
      Chat noch nicht gestartet.<br><br>
      Klicke <strong style="color:#1c3d5e;">▶ Demo starten</strong> neben dem Handy
      um den n8n-Workflow zu triggern.</div>`;
    return;
  }
  let html = '';
  chatMessages.forEach((m, idx)=>{
    if(m.role === 'user'){
      html += `<div class="cmsg user"><div class="mbubble">${escHtml(m.text)}</div></div>`;
    } else if(m.role === 'typing'){
      html += `<div class="cmsg bot"><div class="mavatar">🤖</div>
        <div class="mbubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>`;
    } else {
      html += `<div class="cmsg bot"><div class="mavatar">🤖</div>
        <div class="mbubble">${renderMd(m.text)}</div></div>`;
      if(m.choices && m.choices.length){
        html += `<div class="choices-box">
          <div class="choices-label">Single-Choice selection</div>
          <div class="choices-row">
            ${m.choices.map(c=>`<button class="choice-btn" onclick="pickChoice(${idx}, ${JSON.stringify(c).replace(/"/g,'&quot;')})">${escHtml(c)}</button>`).join('')}
          </div>
        </div>`;
      }
    }
  });
  box.innerHTML = html;
  box.scrollTop = box.scrollHeight;
}

function pickChoice(msgIdx, text){
  // freeze choices on the originating message so user can't double-click
  if(chatMessages[msgIdx]) chatMessages[msgIdx].choices = null;
  sendChat(text);
}

async function sendChat(forcedText){
  if(chatBusy) return;
  const input = document.getElementById('chatInput');
  const text = (forcedText !== undefined ? forcedText : input.value).trim();
  if(!text) return;

  chatBusy = true;
  document.getElementById('chatSend').disabled = true;
  if(forcedText === undefined) input.value = '';

  chatMessages.push({role:'user', text});
  chatMessages.push({role:'typing'});
  renderChat();

  try {
    const reply = await callBot(text);
    // remove typing
    chatMessages = chatMessages.filter(m => m.role !== 'typing');
    chatMessages.push({role:'bot', text: reply});
  } catch(e){
    chatMessages = chatMessages.filter(m => m.role !== 'typing');
    chatMessages.push({role:'bot', text: '⚠ Fehler: ' + (e.message || e)});
  } finally {
    chatBusy = false;
    document.getElementById('chatSend').disabled = false;
    renderChat();
    input.focus();
  }
}

async function callBot(userText){
  // build trimmed history (no typing markers)
  const history = chatMessages
    .filter(m => m.role==='user' || m.role==='bot')
    .map(m => ({role: m.role, text: m.text}));

  const res = await fetch(N8N_CHAT_ENDPOINT, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      message: userText,
      sessionId,
      history,
      profile: P,
      user: D.user
    })
  });
  if(!res.ok) throw new Error('HTTP ' + res.status);
  const ct = res.headers.get('content-type') || '';
  if(ct.includes('application/json')){
    const j = await res.json();
    return j.reply || j.text || j.message || j.output || JSON.stringify(j);
  }
  return await res.text();
}

renderChat();
</script>
</body>
</html>"""

def main():
    if not DATA_FILE.exists():
        print(f"✗ {DATA_FILE} nicht gefunden"); return
    data     = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    data_str = json.dumps(data, ensure_ascii=False)
    HTML_FILE.write_text(HTML.replace("__DATA__", data_str), encoding="utf-8")
    url = HTML_FILE.as_uri()
    print(f"✓ VitalCheck → {HTML_FILE}")
    print(f"  Link: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    main()
