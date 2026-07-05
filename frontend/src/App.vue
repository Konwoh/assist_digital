<script setup>
import { ref } from "vue"

const messages = ref([])
const input = ref("")
const loading = ref(false)

async function sendMessage() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: "user", content: text })
  input.value = ""
  loading.value = true

  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    })

    const data = await response.json()
    messages.value.push({ role: "assistant", content: data.answer })
  } catch (error) {
    messages.value.push({
      role: "assistant",
      content: "Fehler beim Abrufen der Antwort.",
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page">
    <section class="chat">
      <h1>Rick and Morty RAG Chat</h1>

      <div class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          {{ message.content }}
        </div>

        <div v-if="loading" class="message assistant">
          Suche im RAG-Kontext...
        </div>
      </div>

      <form class="input-row" @submit.prevent="sendMessage">
        <input
          v-model="input"
          placeholder="Frage zu Rick and Morty stellen..."
        />
        <button type="submit" :disabled="loading">
          Senden
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #101418;
  color: white;
  font-family: system-ui, sans-serif;
}

.chat {
  width: min(900px, 92vw);
  height: 80vh;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #171d23;
  border: 1px solid #2a333d;
}

.message {
  max-width: 75%;
  padding: 12px 14px;
  border-radius: 8px;
  white-space: pre-wrap;
  line-height: 1.4;
}

.message.user {
  align-self: flex-end;
  background: #2f6feb;
}

.message.assistant {
  align-self: flex-start;
  background: #26313b;
}

.input-row {
  display: flex;
  gap: 8px;
}

input {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #2a333d;
  background: #171d23;
  color: white;
}

button {
  padding: 12px 18px;
  border-radius: 8px;
  border: none;
  background: #7ee787;
  color: #0d1117;
  font-weight: 600;
}
</style>
