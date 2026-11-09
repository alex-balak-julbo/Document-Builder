<script setup>
import { ref, onMounted, computed } from 'vue'
import { api, ph, unph } from '../api.js'
const list = ref([]), blocks = ref([]), cur = ref(null), q = ref(''), arch = ref(false), toast = ref('')
const load = async () => { list.value = await api(`/templates?q=${encodeURIComponent(q.value)}&archived=${arch.value ? 1 : 0}`); blocks.value = await api('/blocks') }
onMounted(load)
const uid = () => Math.random().toString(36).slice(2, 9)
const bhtml = id => blocks.value.find(b => b.id === id)?.html
const newTpl = () => cur.value = { id: null, name: 'Untitled template', category: 'General', description: '', header_id: null, first_header_id: null, footer_id: null, items: [], version: 0 }
const edit = t => { cur.value = JSON.parse(JSON.stringify(t)) }
const add = (bid, at) => { const b = blocks.value.find(x => x.id === bid); cur.value.items.splice(at ?? cur.value.items.length, 0, { uid: uid(), block_id: bid, html: b.html, w: 100 }) }
const move = (i, d) => { const a = cur.value.items; if (a[i + d]) [a[i], a[i + d]] = [a[i + d], a[i]] }
const resize = i => { const w = prompt('Width (%)', cur.value.items[i].w); if (w) cur.value.items[i].w = Math.min(100, Math.max(10, +w || 100)) }
const dragNew = (e, id) => e.dataTransfer.setData('text/plain', 'new:' + id)
const dragMv = (e, i) => e.dataTransfer.setData('text/plain', 'mv:' + i)
function drop(e, at) {
  e.preventDefault(); const d = e.dataTransfer.getData('text/plain'), a = cur.value.items
  if (d.startsWith('new:')) add(+d.slice(4), at)
  else if (d.startsWith('mv:')) { const i = +d.slice(3), [it] = a.splice(i, 1); a.splice(at > i ? at - 1 : at, 0, it) }
}
const pages = computed(() => Math.max(1, Math.ceil((cur.value?.items.length || 0) / 8)))
async function save() {
  const t = cur.value, r = t.id ? await api('/templates/' + t.id, 'PUT', t) : await api('/templates', 'POST', t)
  cur.value = r; toast.value = `Saved as v${r.version}`; setTimeout(() => toast.value = '', 2000); load()
}
async function act(t, a) { a === 'dup' ? await api(`/templates/${t.id}/duplicate`, 'POST') : await api(`/templates/${t.id}/archive`, 'PATCH'); load() }
async function loadVersion(t, e) {
  const v = (await api(`/templates/${t.id}/versions`)).find(x => x.version === +e.target.value); e.target.value = ''
  if (v) { cur.value = { ...t, ...v.data, id: t.id, version: t.version }; toast.value = `Loaded v${v.version} as a draft. Save to keep it.` }
}
const printIt = () => window.print()
</script>
<template>
  <div v-if="!cur">
    <div class="mb-3 flex flex-wrap items-center gap-2">
      <input v-model="q" @input="load" class="inp w-72" placeholder="Search templates"><label class="text-sm"><input type="checkbox" v-model="arch" @change="load"> Show archived</label>
      <span class="flex-1" /><button class="btn btn-p" @click="newTpl">New template</button>
    </div>
    <div class="space-y-2">
      <div v-for="t in list" :key="t.id" class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-300 bg-white p-3">
        <b>{{ t.name }}</b><span class="rounded-full border px-2 text-xs">{{ t.category }}</span><span class="rounded-full border px-2 text-xs">v{{ t.version }}</span>
        <span class="text-sm text-slate-500">{{ t.items.length }} blocks</span><span class="flex-1" />
        <button class="btn" @click="edit(t)">Edit</button><button class="btn" @click="act(t,'dup')">Duplicate</button><button class="btn" @click="act(t,'arch')">{{ t.archived ? 'Restore' : 'Archive' }}</button>
      </div>
      <p v-if="!list.length" class="rounded-lg border-2 border-dashed border-slate-300 p-6 text-center text-slate-500">No templates yet. Create your first template to design on an A4 page.</p>
    </div>
  </div>
  <div v-else>
    <div class="noprint mb-3 flex flex-wrap items-center gap-2">
      <button class="btn" @click="cur=null;load()">Back</button><input v-model="cur.name" class="inp font-semibold" aria-label="Template name"><input v-model="cur.category" class="inp w-32" aria-label="Category">
      <span class="text-sm text-slate-500">v{{ cur.version || 'new' }}</span><span class="flex-1" />
      <label class="text-sm">Header <select v-model="cur.header_id" class="inp"><option :value="null">None</option><option v-for="b in blocks" :key="b.id" :value="b.id">{{ b.name }}</option></select></label>
      <label class="text-sm">First page <select v-model="cur.first_header_id" class="inp"><option :value="null">None</option><option v-for="b in blocks" :key="b.id" :value="b.id">{{ b.name }}</option></select></label>
      <label class="text-sm">Footer <select v-model="cur.footer_id" class="inp"><option :value="null">None</option><option v-for="b in blocks" :key="b.id" :value="b.id">{{ b.name }}</option></select></label>
      <select v-if="cur.id" class="inp" @change="loadVersion(cur,$event)"><option value="">Versions</option><option v-for="v in cur.version" :key="v" :value="v" v-show="v<cur.version">v{{ v }}</option></select>
      <button class="btn" @click="printIt">Print preview</button><button class="btn btn-p" @click="save">Save version</button>
    </div>
    <p v-if="toast" class="noprint mb-2 text-sm text-brand" role="status">{{ toast }}</p>
    <div class="grid gap-4 md:grid-cols-[240px_1fr]">
      <aside class="noprint space-y-2 self-start rounded-lg border border-slate-300 bg-slate-50 p-2">
        <b>Blocks</b><p class="text-xs text-slate-500">Drag onto the page or click to add.</p>
        <div v-for="b in blocks" :key="b.id" draggable="true" @dragstart="dragNew($event,b.id)" @click="add(b.id)" class="cursor-grab rounded border border-dashed border-slate-300 bg-white p-2 text-sm hover:border-brand">{{ b.name }}<div class="text-xs text-slate-500">{{ b.category }}</div></div>
      </aside>
      <div class="overflow-x-auto pb-6">
        <div class="sheet mx-auto text-ink shadow-lg" :style="{ minHeight: pages * 297 + 'mm' }">
          <div class="min-h-[18mm] border-b border-dashed border-slate-300 px-[14mm] py-[8mm]"><span v-html="ph(bhtml(cur.first_header_id || cur.header_id)) || '<i class=noprint>No header selected</i>'" /></div>
          <div class="px-[14mm] pb-[30mm] pt-[8mm]" @dragover.prevent @drop="drop($event, cur.items.length)">
            <div v-for="(it,i) in cur.items" :key="it.uid" draggable="true" @dragstart="dragMv($event,i)" @dragover.prevent @drop.stop="drop($event,i)" class="group relative my-0.5 rounded border border-transparent px-1 hover:border-brand" :style="{ width: it.w + '%' }">
              <div class="noprint absolute -top-3.5 right-0 z-10 hidden gap-1 rounded bg-brand px-1 text-white group-hover:flex">
                <button @click="move(i,-1)" title="Move up">↑</button><button @click="move(i,1)" title="Move down">↓</button><button @click="resize(i)" title="Resize">↔</button>
                <button @click="cur.items.splice(i+1,0,{...it,uid:uid()})" title="Clone">⧉</button><button @click="cur.items.splice(i,1)" title="Remove">✕</button></div>
              <div contenteditable @blur="it.html = unph($event.target.innerHTML)" v-html="ph(it.html)" />
            </div>
            <p v-if="!cur.items.length" class="noprint rounded-lg border-2 border-dashed border-slate-300 p-6 text-center text-slate-500">Drag a block here to start the document.</p>
          </div>
          <div class="absolute inset-x-0 bottom-0 border-t border-dashed border-slate-300 bg-white px-[14mm] py-[8mm]"><span v-html="ph(bhtml(cur.footer_id)) || '<i class=noprint>No footer selected</i>'" /></div>
        </div>
      </div>
    </div>
  </div>
</template>
