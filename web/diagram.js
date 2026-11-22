/* Standalone browser view for the computed project report. */
window.drawProjectView = function (host, report, input) {
  "use strict";
  function el(tag, text, css) {
    const item = document.createElement(tag);
    if (text != null) item.textContent = String(text);
    if (css) item.style.cssText = css;
    return item;
  }
  const figure = el("figure", null, "box-sizing:border-box;margin:12px 0 16px;padding:12px 14px;border-radius:9px;background:#172329;color:#f4f5f2;max-height:210px;overflow:auto;font:13px/1.35 system-ui,sans-serif;text-align:left");
  const head = el("figcaption", "Where each opening makes its case", "font-size:15px;font-weight:700;letter-spacing:-.015em;color:#f5be94;margin-bottom:7px");
  figure.append(head);
  host.replaceChildren(figure);
  const rows = Array.isArray(report && report.rows) ? report.rows : [];
  if (!rows.length) {
    figure.append(el("p", "No findings to display.", "margin:0"));
    return;
  }

  const windowSeconds = Number(report.metrics["Window (s)"]);
  if (!(windowSeconds > 0)) return;
  const legend = el("div", "Teal = product on screen · P = first promise · ● = first proof", "font-size:11px;color:#d0dddc;margin-bottom:6px");
  figure.append(legend);
  const variants = new Map((input.variants || []).map(v => [v.name.trim(), v]));
  for (const row of rows.slice(0, 4)) {
    const lane = el("div", null, "display:grid;grid-template-columns:minmax(64px,22%) minmax(0,1fr);gap:8px;align-items:center;margin:4px 0");
    const name = el("span", row.Opening, "font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis");
    name.title = row.Opening;
    const rail = el("div", null, "position:relative;height:18px;background:#34434b;border-radius:3px;overflow:hidden");
    const intervals = (variants.get(row.Opening)?.beats || []).filter(b => b.features.some(f => f.trim().toLowerCase() === "product"))
      .map(b => [Math.max(0, b.start), Math.min(windowSeconds, b.end)]).filter(([a,b]) => a < b).sort((a,b) => a[0]-b[0]);
    const merged = [];
    for (const [a,b] of intervals) {
      const last = merged[merged.length - 1];
      if (last && a <= last[1]) last[1] = Math.max(last[1], b);
      else merged.push([a,b]);
    }
    for (const [a,b] of merged.slice(0,100)) {
      rail.append(el("span", null, "position:absolute;bottom:2px;height:4px;background:#74cbb4;left:" + (100*a/windowSeconds) + "%;width:" + (100*(b-a)/windowSeconds) + "%"));
    }
    for (const [key,symbol,color] of [["First promise (s)","P","#f7d084"],["First proof (s)","●","#ffac99"]]) {
      const time = row[key];
      if (typeof time !== "number") continue;
      const mark = el("span", symbol, "position:absolute;top:-1px;font:700 11px/13px system-ui;color:"+color+";left:min(calc(100% - 10px),"+(100*time/windowSeconds)+"%)");
      mark.title = key + ": " + time;
      rail.append(mark);
    }
    rail.setAttribute("aria-label", row["Product visible (s)"] + " seconds of product. Promise: " + row["First promise (s)"] + ". Proof: " + row["First proof (s)"] + ".");
    lane.append(name,rail); figure.append(lane);
  }
  figure.append(el("div", "Timeline 0–" + windowSeconds + " s · first " + Math.min(4,rows.length) + " openings · up to 100 product spans per row", "font-size:10px;color:#c5d1ce"));

};
