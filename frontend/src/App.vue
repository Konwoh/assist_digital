<script setup>
import { ref } from "vue"

const messages = ref([])
const input = ref("")
const loading = ref(false)

async function sendFeedback(message, feedback) {
  if (message.feedbackSending) return

  message.feedbackSending = true
  message.feedbackError = false

  try {
    const response = await fetch("http://localhost:8000/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ feedback }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    message.feedback = feedback
  } catch (error) {
    message.feedbackError = true
  } finally {
    message.feedbackSending = false
  }
}

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

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    messages.value.push({
      role: "assistant",
      content: data.answer,
      sources: data.sources,
      confidenceScore: data.confidence_score,
      confidenceLabel: data.confidence_label,
      feedback: null,
      feedbackSending: false,
      feedbackError: false,
    })
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
          <p class="message-text">{{ message.content }}</p>
          <div v-if="message.sources" class="sources">
            <span class="sources-label">Quellen</span>
            <p>{{ message.sources }}</p>
          </div>
          <div
            v-if="message.confidenceScore !== undefined"
            class="message-confidence"
          >
            <span>Konfidenz</span>
            <strong>{{ message.confidenceScore.toFixed(2) }}</strong>
            <em>{{ message.confidenceLabel }}</em>
          </div>
          <div
            v-if="message.role === 'assistant' && message.confidenceScore !== undefined"
            class="feedback-row"
          >
            <button
              type="button"
              class="feedback-button"
              :class="{ active: message.feedback === true }"
              :disabled="message.feedbackSending"
              title="Daumen hoch"
              aria-label="Daumen hoch"
              @click="sendFeedback(message, true)"
            >
              <span class="feedback-icon" aria-hidden="true">👍</span>
            </button>
            <button
              type="button"
              class="feedback-button"
              :class="{ active: message.feedback === false }"
              :disabled="message.feedbackSending"
              title="Daumen runter"
              aria-label="Daumen runter"
              @click="sendFeedback(message, false)"
            >
              <span class="feedback-icon" aria-hidden="true">👎</span>
            </button>
            <span v-if="message.feedbackError" class="feedback-error">
              Feedback fehlgeschlagen
            </span>
          </div>
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
        <button class="send-button" type="submit" :disabled="loading">
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

.message-text {
  margin: 0;
}

.sources {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #3a4652;
  color: #c9d1d9;
  font-size: 0.9rem;
}

.sources p {
  margin: 4px 0 0;
}

.sources-label {
  color: #7ee787;
  font-weight: 700;
}

.message-confidence {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #3a4652;
  font-size: 0.9rem;
}

.message-confidence span {
  color: #c9d1d9;
}

.message-confidence strong {
  color: #7ee787;
}

.message-confidence em {
  color: #8b949e;
  font-style: normal;
}

.feedback-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #3a4652;
}

.feedback-button {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 1px solid #3a4652;
  border-radius: 6px;
  background: #1f2933;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.feedback-icon {
  display: block;
  line-height: 1;
  transform: translateY(-1px);
}

.feedback-button:hover:not(:disabled),
.feedback-button.active {
  border-color: #7ee787;
  background: #24362d;
}

.feedback-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.feedback-error {
  color: #ff7b72;
  font-size: 0.85rem;
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

.send-button {
  padding: 12px 18px;
  border-radius: 8px;
  border: none;
  background: #7ee787;
  color: #0d1117;
  font-weight: 600;
}
</style>
