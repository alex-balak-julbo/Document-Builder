<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { api, ph, unph, COMP } from '../api.js'
const list = ref([]), q = ref(''), arch = ref(false), ed = ref(null), area = ref(null), msg = ref('')
const load = async () => list.value = await api(`/blocks?q=${encodeURIComponent(q.value)}&archived=${arch.value ? 1 : 0}`)
onMounted(load)
const open = b => { ed.value = { id: null, name: 'New block', category: 'General', tags: [], html: '<p>Write your text here.</p>', ...b, tagsText: (b?.tags || []).join(', ') }; nextTick(() => area.value.innerHTML = ph(ed.value.html)) }
const insert = k => { area.value.focus(); area.value.insertAdjacentHTML('beforeend', ph(COMP[k])) }
async function save() {
  const e = ed.value, body = { name: e.name, category: e.category, html: unph(area.value.innerHTML), tags: e.tagsText.split(',').map(s => s.trim()).filter(Boolean) }
  e.id ? await api('/blocks/' + e.id, 'PUT', body) : await api('/blocks', 'POST', body)
  ed.value = null; msg.value = 'Block saved'; load()
}
const act = async (b, a) => { a === 'dup' ? await api(`/blocks/${b.id}/duplicate`, 'POST') : await api(`/blocks/${b.id}/archive`, 'PATCH'); load() }
</script>
<template>
  <div class="mb-3 flex flex-wrap items-center gap-2">
    <input v-model="q" @input="load" class="inp w-72" placeholder="Search by name, category or tag">
    <label class="text-sm"><input type="checkbox" v-model="arch" @change="load"> Show archived</label>
    <span class="flex-1" /><button class="btn btn-p" @click="open()">New block</button>
  </div>
  <div class="grid gap-4 md:grid-cols-[320px_1fr]">
    <div class="space-y-2">
      <div v-for="b in list" :key="b.id" class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-300 bg-white p-3">
        <div class="flex-1"><b>{{ b.name }}</b><div class="text-xs text-slate-500">{{ b.category }} · v{{ b.version }}<span v-if="b.archived"> · archived</span></div></div>
        <button class="btn" @click="open(b)">Edit</button><button class="btn" @click="act(b,'dup')">Duplicate</button><button class="btn" @click="act(b,'arch')">{{ b.archived ? 'Restore' : 'Archive' }}</button>
      </div>
      <p v-if="!list.length" class="rounded-lg border-2 border-dashed border-slate-300 p-6 text-center text-slate-500">No blocks yet. Create one to reuse it across templates.</p>
    </div>
    <div v-if="ed" class="space-y-2 rounded-lg border border-slate-300 bg-white p-3">
      <div class="flex flex-wrap gap-2"><input v-model="ed.name" class="inp" aria-label="Name"><input v-model="ed.category" class="inp w-32" aria-label="Category"><input v-model="ed.tagsText" class="inp w-40" placeholder="tags, comma separated"></div>
      <div class="flex flex-wrap gap-1"><button v-for="(v,k) in COMP" :key="k" class="btn" @click="insert(k)">{{ k }}</button></div>
      <div ref="area" contenteditable class="sheet min-h-[240px] w-full border border-slate-300 p-4" />
      <div class="flex justify-end gap-2"><button class="btn" @click="ed=null">Close</button><button class="btn btn-p" @click="save">Save block</button></div>
    </div>
  </div>
</template>
