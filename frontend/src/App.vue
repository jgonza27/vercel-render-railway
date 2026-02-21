<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <nav class="bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-indigo-600">Vercel & Render</h1>
          </div>
          <div class="flex items-center space-x-4">
            <div v-if="backendStatus" class="flex items-center space-x-2">
              <span class="w-3 h-3 bg-green-500 rounded-full"></span>
              <span class="text-sm text-gray-600">Backend Online</span>
            </div>
            <div v-else class="flex items-center space-x-2">
              <span class="w-3 h-3 bg-red-500 rounded-full"></span>
              <span class="text-sm text-gray-600">Backend Offline</span>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Status Section -->
      <div class="bg-white rounded-lg shadow-xl p-8 mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">Backend Status</h2>
        <div v-if="loading" class="text-gray-600">Loading...</div>
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-red-900">Error: {{ error }}</p>
        </div>
        <div v-else-if="backendStatus" class="grid grid-cols-2 gap-4">
          <div class="bg-green-50 rounded-lg p-4">
            <p class="text-sm text-green-700 font-semibold">Status</p>
            <p class="text-lg text-green-900">{{ backendStatus.status }}</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-4">
            <p class="text-sm text-blue-700 font-semibold">Engine</p>
            <p class="text-lg text-blue-900">{{ backendEngine }}</p>
          </div>
          <div class="col-span-2 bg-indigo-50 rounded-lg p-4">
            <p class="text-sm text-indigo-700 font-semibold">Message</p>
            <p class="text-indigo-900">{{ backendStatus.message }}</p>
          </div>
        </div>
      </div>

      <!-- Todo List Section -->
      <div class="bg-white rounded-lg shadow-xl p-8 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-3xl font-bold text-gray-900">Todo List</h2>
          <button
            @click="loadItems"
            class="text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            Refresh
          </button>
        </div>

        <form @submit.prevent="addItem" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <input
            v-model="newItemName"
            type="text"
            placeholder="Nueva tarea"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            required
          />
          <select
            v-model="newItemStatus"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option>Pendiente</option>
            <option>En progreso</option>
            <option>Completado</option>
          </select>
          <button
            type="submit"
            class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
          >
            Agregar
          </button>
        </form>

        <div v-if="items.length === 0" class="text-gray-600">
          No hay tareas todavía.
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="item in items"
            :key="item.id"
            class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-4 border border-gray-200 rounded-lg hover:border-indigo-300 transition"
          >
            <div class="flex-1">
              <div v-if="editingId === item.id" class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <input
                  v-model="editName"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <select
                  v-model="editStatus"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option>Pendiente</option>
                  <option>En progreso</option>
                  <option>Completado</option>
                </select>
              </div>
              <div v-else>
                <p class="font-semibold text-gray-900">{{ item.name }}</p>
                <span
                  :class="{
                    'px-3 py-1 rounded-full text-sm font-medium inline-block mt-2': true,
                    'bg-green-100 text-green-800': item.status === 'Completado',
                    'bg-blue-100 text-blue-800': item.status === 'En progreso',
                    'bg-yellow-100 text-yellow-800': item.status === 'Pendiente'
                  }"
                >
                  {{ item.status }}
                </span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <template v-if="editingId === item.id">
                <button
                  @click="saveEdit(item.id)"
                  class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
                >
                  Guardar
                </button>
                <button
                  @click="cancelEdit"
                  class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded-lg transition duration-200"
                >
                  Cancelar
                </button>
              </template>
              <template v-else>
                <button
                  @click="startEdit(item)"
                  class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
                >
                  Editar
                </button>
                <button
                  @click="removeItem(item.id)"
                  class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
                >
                  Eliminar
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService } from './services/api'

const loading = ref(true)
const error = ref<string | null>(null)
const backendStatus = ref<any>(null)
const backendEngine = ref('FastAPI + MySQL')
const items = ref<Array<{ id: number; name: string; status: string }>>([])
const newItemName = ref('')
const newItemStatus = ref('Pendiente')
const editingId = ref<number | null>(null)
const editName = ref('')
const editStatus = ref('Pendiente')

const loadItems = async () => {
  const data = await apiService.listItems()
  items.value = data
}

const addItem = async () => {
  if (!newItemName.value.trim()) return
  await apiService.createItem({
    name: newItemName.value.trim(),
    status: newItemStatus.value,
  })
  newItemName.value = ''
  newItemStatus.value = 'Pendiente'
  await loadItems()
}

const startEdit = (item: { id: number; name: string; status: string }) => {
  editingId.value = item.id
  editName.value = item.name
  editStatus.value = item.status
}

const cancelEdit = () => {
  editingId.value = null
  editName.value = ''
  editStatus.value = 'Pendiente'
}

const saveEdit = async (itemId: number) => {
  await apiService.updateItem(itemId, {
    name: editName.value.trim(),
    status: editStatus.value,
  })
  cancelEdit()
  await loadItems()
}

const removeItem = async (itemId: number) => {
  await apiService.deleteItem(itemId)
  await loadItems()
}

onMounted(async () => {
  try {
    loading.value = true
    const [status, data] = await Promise.all([
      apiService.getStatus(),
      apiService.getData(),
    ])
    backendStatus.value = status
    backendEngine.value = data.backend_engine || 'FastAPI + MySQL'
    await loadItems()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error fetching data from backend'
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Deployed via CI/CD with GitHub Actions */
</style>
