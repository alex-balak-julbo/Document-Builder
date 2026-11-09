export async function api(path, method = 'GET', body) {
  const r = await fetch('/api' + path, { method, credentials: 'same-origin',
    headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined })
  const d = await r.json().catch(() => ({}))
  if (!r.ok) { const e = new Error(d.error || 'Request failed'); e.status = r.status; throw e }
  return d
}
export const ph = h => (h || '').replace(/\{\{([A-Z0-9_]+)\}\}/g, '<span class="ph">{{$1}}</span>')
export const unph = h => h.replace(/<span class="ph">([^<]*)<\/span>/g, '$1')
export const COMP = {
  Title: '<h1>Document title</h1>', Subtitle: '<h2>Section title</h2>', Text: '<p>Write your text here.</p>',
  Table: '<table><tr><th>Item</th><th>Quantity</th><th>Amount</th></tr><tr><td>{{ITEM}}</td><td>{{QTY}}</td><td>{{AMOUNT}}</td></tr></table>',
  Logo: '<div style="width:40mm;height:14mm;border:1px dashed #9aa8b4;text-align:center">{{COMPANY_LOGO}}</div>',
  Divider: '<hr>', Signature: '<div style="height:22mm;border:1px dashed #9aa8b4">Signature</div>', Placeholder: '<span>{{CURRENT_DATE}}</span>' }
