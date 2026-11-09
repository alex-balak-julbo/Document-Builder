<script setup>
import { ref, onMounted } from 'vue'
import { api } from './api.js'
import BlocksView from './views/BlocksView.vue'
import TemplatesView from './views/TemplatesView.vue'
const user = ref(null), ready = ref(false), tab = ref('tpl'), form = ref({ email: '', password: '' }), err = ref('')
onMounted(async () => { try { user.value = (await api('/auth/me')).email } catch {} ready.value = true })
async function login() { err.value = ''; try { user.value = (await api('/auth/login', 'POST', form.value)).email; form.value.password = '' } catch (e) { err.value = e.message } }
async function logout() { await api('/auth/logout', 'POST'); user.value = null }
</script>
<template>
  <div v-if="!ready" />
  <form v-else-if="!user" @submit.prevent="login" class="mx-auto mt-24 w-80 space-y-3 rounded-lg bg-white p-6 shadow">
    <h1 class="text-xl font-semibold">Sign in to Document Builder</h1>
    <input v-model="form.email" type="email" required placeholder="Email" class="inp w-full" autocomplete="username">
    <input v-model="form.password" type="password" required placeholder="Password" class="inp w-full" autocomplete="current-password">
    <p v-if="err" class="text-sm text-red-700" role="alert">{{ err }}</p>
    <button class="btn btn-p w-full">Sign in</button>
  </form>
  <template v-else>
    <header class="noprint sticky top-0 z-10 flex items-center gap-2 border-b border-slate-300 bg-slate-50 px-4 py-2">
      <b class="mr-4 text-lg">Document Builder</b>
      <button v-for="t in [['tpl','Template library'],['blk','Block library']]" :key="t[0]" @click="tab=t[0]" class="btn" :class="tab===t[0]&&'btn-p'">{{ t[1] }}</button>
      <span class="flex-1" /><span class="text-sm text-slate-500">{{ user }}</span><button class="btn" @click="logout">Sign out</button>
    </header>
    <main class="mx-auto max-w-7xl p-4"><BlocksView v-if="tab==='blk'" /><TemplatesView v-else /></main>
  </template>
</template>
