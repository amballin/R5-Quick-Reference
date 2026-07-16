const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const ICON_COLOR = "#8dc8ff";
const WIDTH = 393;
const HEIGHT = 852;

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function iconSvg(file, size = 18, color = ICON_COLOR) {
  if (!file || !fs.existsSync(file) || path.extname(file).toLowerCase() !== ".svg") {
    return "";
  }
  let text = fs.readFileSync(file, "utf8");
  text = text.replace(/<\?xml[^>]*>/g, "").replace(/<!DOCTYPE[^>]*>/g, "");
  text = text
    .replace(/width="[^"]*"/, `width="${size}"`)
    .replace(/height="[^"]*"/, `height="${size}"`)
    .replace(/<svg([^>]*)>/, `<svg$1 fill="${color}">`)
    .replace(/fill="#000"/g, `fill="${color}"`)
    .replace(/stroke="currentColor"/g, `stroke="${color}"`);
  return text;
}

function rasterIcon(file, index, size = 18, color = ICON_COLOR) {
  if (!file || !fs.existsSync(file)) {
    return "";
  }
  const ext = path.extname(file).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "";
  if (!mime) {
    return "";
  }
  const encoded = fs.readFileSync(file).toString("base64");
  const maskId = `row-icon-mask-${index}`;
  return `<mask id="${maskId}" mask-type="alpha"><image href="data:${mime};base64,${encoded}" width="${size}" height="${size}" preserveAspectRatio="xMidYMid meet"/></mask><rect width="${size}" height="${size}" fill="${color}" mask="url(#${maskId})"/>`;
}

function rasterImage(file, size) {
  if (!file || !fs.existsSync(file)) {
    return "";
  }
  const ext = path.extname(file).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "";
  if (!mime) {
    return "";
  }
  const encoded = fs.readFileSync(file).toString("base64");
  return `<image href="data:${mime};base64,${encoded}" width="${size}" height="${size}" preserveAspectRatio="xMidYMid meet"/>`;
}

function headerIcon(file) {
  if (!file) {
    return "";
  }
  if (path.extname(file).toLowerCase() === ".svg") {
    return iconSvg(file, 42, "#ffffff");
  }
  return rasterImage(file, 42);
}

function wrapText(value, maxChars) {
  const words = String(value).split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length <= maxChars || !current) {
      current = next;
    } else {
      lines.push(current);
      current = word;
    }
  }
  if (current) {
    lines.push(current);
  }
  return lines.length ? lines : [""];
}

function textBlock(value, x, y, className, maxChars, options = {}) {
  const lines = wrapText(value, maxChars);
  const lineHeight = options.lineHeight || 17;
  const anchor = options.anchor ? ` text-anchor="${options.anchor}"` : "";
  let out = "";
  for (let i = 0; i < lines.length; i++) {
    out += `<text x="${x}" y="${y + i * lineHeight}" class="${className}"${anchor}>${esc(lines[i])}</text>`;
  }
  return [out, y + lines.length * lineHeight];
}

function listItems(items, x, y) {
  let out = "";
  for (const item of items) {
    const rendered = textBlock(`• ${item}`, x, y, "li", 43, { lineHeight: 18 });
    out += rendered[0];
    y = rendered[1] + 2;
  }
  return [out, y];
}

function section(title, items, y) {
  let out = `<text x="22" y="${y}" class="h2">${esc(title)}</text><line x1="22" y1="${y + 8}" x2="371" y2="${y + 8}" class="rule"/>`;
  y += 28;
  const rendered = listItems(items, 32, y);
  return [out + rendered[0], rendered[1] + 8];
}

function cardContent(data) {
  let y = 36;
  const colors = Object.assign({ background: "#1e3553", text: "#ffffff" }, data.colors || {});
  let content = "";
  const leftIcon = headerIcon(data.header_icons && data.header_icons.left);
  const rightIcon = headerIcon(data.header_icons && data.header_icons.right);
  if (leftIcon) {
    content += `<g transform="translate(22 15)">${leftIcon}</g>`;
  }
  content += `<rect x="116" y="18" width="160" height="36" rx="20" fill="#000"/>`;
  if (rightIcon) {
    content += `<g transform="translate(329 15)">${rightIcon}</g>`;
  }
  y = 88;
  content += `<text x="196.5" y="${y}" class="title" text-anchor="middle">${esc(data.title)}</text>`;
  if (data.subtitle) {
    y += 28;
    content += `<text x="196.5" y="${y}" class="sub" text-anchor="middle">${esc(data.subtitle)}</text>`;
    y += 38;
  } else {
    y += 48;
  }
  if (data.rows.length) {
    content += `<text x="22" y="${y}" class="h2">Settings</text><line x1="22" y1="${y + 8}" x2="371" y2="${y + 8}" class="rule"/>`;
    y += 30;
  }
  for (const row of data.rows) {
    const icon = path.extname(row.icon || "").toLowerCase() === ".svg" ? iconSvg(row.icon) : rasterIcon(row.icon, y);
    if (icon) {
      content += `<g transform="translate(22 ${y - 15})">${icon}</g>`;
    }
    const renderedLabel = textBlock(row.label, 46, y, "label", 20, {
      lineHeight: 17,
    });
    content += renderedLabel[0];
    const renderedValue = textBlock(row.value, 371, y, "value", 22, {
      anchor: "end",
      lineHeight: 17,
    });
    content += renderedValue[0];
    y = Math.max(y + 24, renderedLabel[1] + 5, renderedValue[1] + 5);
  }
  y += data.rows.length ? 18 : 0;
  for (const [title, items] of [
    ["Checklist", data.checklist],
    ["Watch For", data.watch_for],
    ["Common Mistakes", data.common_mistakes],
    ["Notes", data.notes],
  ]) {
    const rendered = section(title, items, y);
    content += rendered[0];
    y = rendered[1];
  }
  return { colors, content, contentHeight: y };
}

function cardSvg(data, options = {}) {
  const layout = cardContent(data);
  const scaleToFit = options.scaleToFit !== false;
  const outputHeight = options.height || (scaleToFit ? HEIGHT : Math.max(HEIGHT, Math.ceil(layout.contentHeight + 14)));
  let body = `<rect width="${WIDTH}" height="${outputHeight}" fill="${esc(layout.colors.background)}"/>`;
  const scale = scaleToFit ? Math.min(1, (outputHeight - 14) / layout.contentHeight) : 1;
  const offsetX = (WIDTH - WIDTH * scale) / 2;
  body += `<g transform="translate(${offsetX} 0) scale(${scale})">${layout.content}</g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${outputHeight}" viewBox="0 0 ${WIDTH} ${outputHeight}">
  <style>
    .title{fill:${esc(layout.colors.text)};font:700 32px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .sub{fill:#b7d2e8;font:400 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .h2{fill:#8dc8ff;font:700 20px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .rule{stroke:#53738c;stroke-width:1}
    .label{fill:#b7d2e8;font:400 15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .value{fill:${esc(layout.colors.text)};font:700 15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    .li{fill:${esc(layout.colors.text)};font:400 15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
  </style>
  ${body}
</svg>`;
}

async function main() {
  const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const svg = cardSvg(payload, { height: HEIGHT, scaleToFit: true });
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  fs.mkdirSync(path.dirname(payload.png), { recursive: true });
  fs.writeFileSync(payload.png, png);

  if (payload.phone_png) {
    const phoneSvg = cardSvg(payload, { scaleToFit: false });
    const phonePng = await sharp(Buffer.from(phoneSvg)).png().toBuffer();
    fs.mkdirSync(path.dirname(payload.phone_png), { recursive: true });
    fs.writeFileSync(payload.phone_png, phonePng);
  }

  if (payload.pdf) {
    const { PDFDocument } = require("pdf-lib");
    fs.mkdirSync(path.dirname(payload.pdf), { recursive: true });
    const pdf = await PDFDocument.create();
    const page = pdf.addPage([WIDTH, HEIGHT]);
    const image = await pdf.embedPng(png);
    page.drawImage(image, { x: 0, y: 0, width: WIDTH, height: HEIGHT });
    fs.writeFileSync(payload.pdf, await pdf.save());
  }
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : error);
  process.exit(1);
});
