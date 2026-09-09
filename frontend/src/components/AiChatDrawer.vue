<template>
  <div>
    <!-- 右下角常驻悬浮 AI 按钮 -->
    <div class="floating-ai-trigger" @click="openDrawer">
      <div class="ai-button-glow"></div>
      <div class="ai-button-inner">
        <span class="ai-icon">🤖</span>
      </div>
      <div class="ai-badge-label">
        <span>AI 分身问答</span>
      </div>
    </div>

    <!-- AI 对话抽屉 -->
    <el-drawer
      v-model="aiChatStore.isChatOpen"
      direction="rtl"
      size="480px"
      :show-close="true"
      custom-class="ai-chat-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <div class="header-avatar-box">
            <el-avatar :size="40" src="https://api.dicebear.com/7.x/bottts/svg?seed=admin" />
            <span class="online-indicator"></span>
          </div>
          <div class="header-info">
            <h3 class="header-title">博主 AI 数字分身</h3>
            <p class="header-subtitle">基于 RAG 知识库与大模型驱动 · 实时语义对齐</p>
          </div>
          <el-button size="small" text type="danger" @click="clearHistory">清空对话</el-button>
        </div>
      </template>

      <!-- 对话消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 初始欢迎问候卡片 -->
        <div class="welcome-card">
          <div class="welcome-badge">🚀 RAG 知识库问答助手</div>
          <p class="welcome-text">
            你好！我是博主的 AI 数字分身 🤖。我已全面索引了博主关于 <strong>Transformer 架构、LoRA 微调、RAG 向量检索</strong> 等领域的深度技术博文。
          </p>
          <p class="welcome-hint">你可以随时直接向我提问，或点击下方推荐问题：</p>
          
          <div class="quick-questions">
            <button
              v-for="(q, idx) in quickPrompts"
              :key="idx"
              class="quick-tag"
              @click="sendQuickQuestion(q)"
            >
              {{ q }}
            </button>
          </div>
        </div>

        <!-- 历史消息列表 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-row', msg.role === 'user' ? 'row-user' : 'row-assistant']"
        >
          <div class="message-avatar">
            <el-avatar
              :size="32"
              :src="msg.role === 'user' ? (userStore.user?.avatar || 'https://api.dicebear.com/7.x/bottts/svg?seed=user') : 'https://api.dicebear.com/7.x/bottts/svg?seed=admin'"
            />
          </div>

          <div class="message-bubble-wrapper">
            <div class="message-bubble">
              <MarkdownViewer :content="msg.content" />
              <span v-if="isStreaming && index === messages.length - 1" class="cursor-blink">|</span>
            </div>

            <!-- 溯源引用卡片 (RAG 核心亮点) -->
            <div v-if="msg.citations && msg.citations.length > 0" class="citations-container">
              <div class="citation-header">
                <span>📚 知识库溯源引用 ({{ msg.citations.length }} 处)</span>
              </div>
              <div
                v-for="c in msg.citations"
                :key="c.chunk_id"
                class="citation-card"
                @click="jumpToArticle(c.article_slug)"
              >
                <div class="citation-title">
                  <span class="citation-num">#{{ c.citation_index }}</span>
                  <span class="citation-name">《{{ c.article_title }}》</span>
                  <span class="similarity-badge">{{ (c.similarity * 100).toFixed(1) }}% 相关度</span>
                </div>
                <div class="citation-snippet">{{ c.snippet }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入框 -->
      <template #footer>
        <div class="chat-input-wrapper">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="3"
            placeholder="输入你的技术问题... (Enter 发送, Shift+Enter 换行)"
            resize="none"
            :disabled="isStreaming"
            @keydown.enter.prevent="handleEnter"
          />
          <div class="input-actions">
            <span class="model-tag">当前接入: {{ llmModelLabel }}</span>
            <el-button
              type="primary"
              :loading="isStreaming"
              :disabled="!inputText.trim()"
              @click="handleSend"
            >
              发送提问
            </el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAiChatStore } from '@/stores/aiChat'
import { useUserStore } from '@/stores/user'
import { streamRagChat } from '@/api/ai'
import type { CitationItem } from '@/types'
import MarkdownViewer from './MarkdownViewer.vue'

const router = useRouter()
const aiChatStore = useAiChatStore()
const userStore = useUserStore()

const inputText = ref('')
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const llmModelLabel = ref('自研轻量RAG / DeepSeek')

interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
  citations?: CitationItem[]
}

const messages = ref<ChatMsg[]>([])

const quickPrompts = [
  'Transformer 自注意力为什么要除以 sqrt(d_k)？',
  '显存不够怎么微调大语言模型？',
  '多路召回相比单一向量检索有什么优势？',
  'LoRA 微调为什么在推理阶段零延迟？'
]

// 监听外界传入的问题触发自动提问
watch(() => aiChatStore.pendingQuestion, (newQ) => {
  if (newQ) {
    inputText.value = newQ
    aiChatStore.pendingQuestion = ''
    handleSend()
  }
})

const openDrawer = () => {
  aiChatStore.openChat()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const clearHistory = () => {
  messages.value = []
}

const sendQuickQuestion = (q: string) => {
  inputText.value = q
  handleSend()
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    handleSend()
  }
}

const jumpToArticle = (slug: string) => {
  aiChatStore.closeChat()
  router.push(`/article/${slug}`)
}

const handleSend = async () => {
  const query = inputText.value.trim()
  if (!query || isStreaming.value) return

  // 追加用户消息
  messages.value.push({ role: 'user', content: query })
  inputText.value = ''
  scrollToBottom()

  // 准备 Assistant 占位消息
  const assistantMsgIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: '', citations: [] })
  isStreaming.value = true
  scrollToBottom()

  const historyPayload = messages.value
    .slice(0, -2)
    .map(m => ({ role: m.role, content: m.content }))

  await streamRagChat(
    query,
    historyPayload,
    (token) => {
      messages.value[assistantMsgIndex].content += token
      scrollToBottom()
    },
    (citations) => {
      messages.value[assistantMsgIndex].citations = citations
      scrollToBottom()
    },
    () => {
      isStreaming.value = false
      scrollToBottom()
    },
    (err) => {
      console.error(err)
      messages.value[assistantMsgIndex].content += '\n\n*(网络连接出现异常，请重试)*'
      isStreaming.value = false
      scrollToBottom()
    }
  )
}
</script>

<style scoped>
.floating-ai-trigger {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 999;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-button-glow {
  position: absolute;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.35) 0%, rgba(16, 185, 129, 0) 70%);
  animation: glow-pulse 2s infinite;
}

@keyframes glow-pulse {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 0.3; }
  100% { transform: scale(0.9); opacity: 0.8; }
}

.ai-button-inner {
  position: relative;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #18181b;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(24, 24, 27, 0.35);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.floating-ai-trigger:hover .ai-button-inner {
  transform: scale(1.1) rotate(5deg);
}

.ai-icon {
  font-size: 1.8rem;
}

.ai-badge-label {
  background: #ffffff;
  padding: 6px 14px;
  border-radius: 20px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
  font-size: 0.85rem;
  font-weight: 600;
  color: #18181b;
  border: 1px solid #e4e4e7;
}

/* 抽屉样式 */
.drawer-header {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.header-avatar-box {
  position: relative;
}

.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #10b981;
  border: 2px solid #ffffff;
  border-radius: 50%;
}

.header-info {
  flex: 1;
}

.header-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #18181b;
}

.header-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.75rem;
  color: #71717a;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.welcome-card {
  background: #f4f4f5;
  border: 1px solid #e4e4e7;
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 0.5rem;
}

.welcome-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  background: #18181b;
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.welcome-text {
  font-size: 0.88rem;
  color: #3f3f46;
  line-height: 1.6;
  margin: 0 0 8px 0;
}

.welcome-hint {
  font-size: 0.8rem;
  color: #71717a;
  margin: 0 0 10px 0;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quick-tag {
  text-align: left;
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 0.82rem;
  color: #18181b;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: #18181b;
  color: #ffffff;
  border-color: #18181b;
  transform: translateX(4px);
}

.message-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.row-user {
  flex-direction: row-reverse;
}

.message-bubble-wrapper {
  max-width: 82%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.row-user .message-bubble {
  background: #18181b;
  color: #ffffff;
  border-radius: 16px 4px 16px 16px;
  padding: 10px 14px;
  box-shadow: 0 2px 8px rgba(24, 24, 27, 0.25);
}

.row-user .message-bubble :deep(*) {
  color: #ffffff !important;
}

.row-assistant .message-bubble {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 4px 16px 16px 16px;
  padding: 12px 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}

.cursor-blink {
  display: inline-block;
  font-weight: bold;
  animation: blink 0.8s infinite;
  color: #10b981;
  margin-left: 2px;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 引用溯源卡片 */
.citations-container {
  background: #fafafa;
  border: 1px dashed #e4e4e7;
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.citation-header {
  font-size: 0.78rem;
  font-weight: 700;
  color: #52525b;
}

.citation-card {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.citation-card:hover {
  border-color: #10b981;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.citation-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #18181b;
  margin-bottom: 4px;
}

.citation-num {
  color: #059669;
  font-weight: 800;
}

.similarity-badge {
  margin-left: auto;
  font-size: 0.7rem;
  background: #ecfdf5;
  color: #059669;
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid #a7f3d0;
}

.citation-snippet {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chat-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 8px;
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.model-tag {
  font-size: 0.75rem;
  color: #9ca3af;
}
</style>
