<template>
  <div class="ai-settings-page">
    <div class="page-title-row">
      <div>
        <h2 class="title">AI 算法引擎与大模型中枢配置</h2>
        <p class="subtitle">统一管理 LLM 模型接入端点、RAG 向量检索超参数及知识库全量索引重构</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- 大模型接入策略卡片 -->
      <div class="setting-card">
        <h3 class="card-title">🤖 大模型中立接入策略 (LLM Provider)</h3>
        <p class="card-desc">
          本系统设计遵循策略模式，支持零成本离线演示（Mock 模式），亦可无缝切换至 DeepSeek、Kimi、智谱或 OpenAI 商业大模型。
        </p>

        <el-form :model="configForm" label-position="top">
          <el-form-item label="模型接入商 (Provider)">
            <el-radio-group v-model="configForm.provider" size="large">
              <el-radio-button label="mock">本地智能 Mock (零API成本/稳定可靠)</el-radio-button>
              <el-radio-button label="deepseek">DeepSeek (V3/R1)</el-radio-button>
              <el-radio-button label="zhipu">智谱 GLM-4</el-radio-button>
              <el-radio-button label="openai">OpenAI 协议兼容</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="大模型 API Key">
            <el-input
              v-model="configForm.api_key"
              type="password"
              show-password
              placeholder="留空则自动降级为本地智能 RAG 算法推理..."
            />
          </el-form-item>

          <el-row :gutter="16">
            <el-col :span="14">
              <el-form-item label="API Base URL 端点">
                <el-input v-model="configForm.base_url" placeholder="例如：https://api.deepseek.com" />
              </el-form-item>
            </el-col>
            <el-col :span="10">
              <el-form-item label="Model 模型标识">
                <el-input v-model="configForm.model" placeholder="例如：deepseek-chat" />
              </el-form-item>
            </el-col>
          </el-row>

          <h4 class="sub-title">🎯 RAG 向量知识库检索超参数</h4>

          <el-form-item label="Top-K 召回切片数量 (推荐 3~6)">
            <el-slider v-model="configForm.top_k" :min="1" :max="10" show-input />
          </el-form-item>

          <el-form-item label="余弦相似度过滤阈值 (0.1 ~ 0.8)">
            <el-slider
              v-model="configForm.similarity_threshold"
              :min="0.1"
              :max="0.8"
              :step="0.05"
              show-input
            />
          </el-form-item>

          <div class="card-submit-row">
            <el-button type="primary" size="large" :loading="saving" @click="saveConfig">
              保存并热重载 AI 引擎配置
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 知识库向量重构操作卡片 -->
      <div class="setting-card">
        <h3 class="card-title">⚡ 知识库全量向量重构 (RAG Indexing)</h3>
        <p class="card-desc">
          当批量导入外部 Markdown 文档或调整分块大小（Chunk Size）后，点击下方按钮将全量重新切分博文并计算 128 维嵌入特征向量。
        </p>

        <div class="rag-pipeline-box">
          <h4 class="pipeline-title">知识库数据流管道 (Pipeline):</h4>
          <ol class="pipeline-steps">
            <li><strong>Markdown 解析</strong>：提取多级标题与段落边界</li>
            <li><strong>标题感知递归切块</strong>：保留 60 字符重叠步长防语义断裂</li>
            <li><strong>稠密特征哈希投影</strong>：生成 128 维 L2 归一化向量</li>
            <li><strong>持久化写入</strong>：保存至 MySQL <code>article_chunks</code> 表</li>
          </ol>
        </div>

        <div class="reindex-action-wrap">
          <el-button
            type="warning"
            size="large"
            :loading="reindexing"
            @click="triggerReindexAll"
          >
            ⚡ 一键全量重建所有博文向量索引
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAiConfigApi, updateAiConfigApi, reindexAllApi } from '@/api/ai'
import type { LlmConfig } from '@/types'

const saving = ref(false)
const reindexing = ref(false)

const configForm = ref<LlmConfig>({
  provider: 'mock',
  api_key: '',
  base_url: 'https://api.deepseek.com',
  model: 'deepseek-chat',
  top_k: 4,
  similarity_threshold: 0.30
})

const loadConfig = async () => {
  const conf = await getAiConfigApi()
  configForm.value = conf
}

const saveConfig = async () => {
  saving.value = true
  try {
    await updateAiConfigApi(configForm.value)
    ElMessage.success('大模型与 RAG 运行时配置已成功更新！')
  } finally {
    saving.value = false
  }
}

const triggerReindexAll = async () => {
  reindexing.value = true
  try {
    const res = await reindexAllApi()
    ElMessage.success(`全量重构完成！成功索引 ${res.articles_indexed} 篇博文，共生成 ${res.total_chunks} 个向量知识切片！`)
  } catch (e) {
    ElMessage.error('重构失败')
  } finally {
    reindexing.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.ai-settings-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 800;
  color: #18181b;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: #71717a;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 1.5rem;
}

.setting-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.75rem;
  border: 1px solid #e4e4e7;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #18181b;
}

.card-desc {
  font-size: 0.85rem;
  color: #71717a;
  line-height: 1.5;
  margin: 0 0 1.5rem 0;
}

.sub-title {
  margin: 1.5rem 0 1rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #18181b;
}

.card-submit-row {
  margin-top: 1.5rem;
}

.rag-pipeline-box {
  background: #f4f4f5;
  border: 1px dashed #e4e4e7;
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 2rem;
}

.pipeline-title {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: #18181b;
}

.pipeline-steps {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.82rem;
  color: #52525b;
}

.reindex-action-wrap {
  text-align: center;
  padding: 1rem 0;
}
</style>
