<template>
  <div class="categories-page">
    <Navbar />

    <main class="page-container">
      <div class="page-header">
        <h1 class="title">📚 分类与技术标签体系</h1>
        <p class="subtitle">涵盖大语言模型、深度学习核心算法与高并发软件工程架构</p>
      </div>

      <!-- 分类卡片网格 -->
      <section class="categories-grid">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="category-card"
          @click="selectCategory(cat.id)"
        >
          <div class="cat-header">
            <span class="cat-icon">📁</span>
            <h3 class="cat-title">{{ cat.name }}</h3>
            <span class="cat-count-badge">{{ cat.article_count || 0 }} 篇</span>
          </div>
          <p class="cat-desc">{{ cat.description || '暂无分类详细描述' }}</p>
        </div>
      </section>

      <!-- 标签聚合云 -->
      <section class="tags-section">
        <h2 class="section-title">🏷️ 技术标签索引</h2>
        <div class="tags-container">
          <span
            v-for="tag in tags"
            :key="tag.id"
            class="tag-badge"
            :style="{ borderColor: tag.color, color: tag.color }"
            @click="selectTag(tag.id)"
          >
            {{ tag.name }} ({{ tag.article_count || 0 }})
          </span>
        </div>
      </section>

      <!-- 筛选结果列表 -->
      <section class="filtered-articles-section">
        <h2 class="section-title">
          <span>{{ currentFilterTitle }}</span>
          <el-button v-if="activeFilter" size="small" text @click="resetFilter">重置筛选</el-button>
        </h2>

        <div v-if="loading" class="loading-box">
          <el-skeleton :rows="4" animated />
        </div>

        <div v-else-if="articles.length > 0" class="articles-list">
          <div
            v-for="art in articles"
            :key="art.id"
            class="article-row-card"
            @click="$router.push(`/article/${art.slug}`)"
          >
            <span class="art-title">{{ art.title }}</span>
            <span class="art-date">{{ formatDate(art.created_at) }}</span>
          </div>
        </div>

        <div v-else class="empty-box">
          <el-empty description="该标签或分类下暂无文章" />
        </div>
      </section>
    </main>

    <AiChatDrawer />
    <SemanticSearchModal />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Navbar from '@/components/Navbar.vue'
import AiChatDrawer from '@/components/AiChatDrawer.vue'
import SemanticSearchModal from '@/components/SemanticSearchModal.vue'
import { getCategoriesApi } from '@/api/category'
import { getTagsApi } from '@/api/tag'
import { getArticlesApi } from '@/api/article'
import type { Category, Tag, ArticleListItem } from '@/types'

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])
const articles = ref<ArticleListItem[]>([])
const loading = ref(false)

const selectedCatId = ref<number | null>(null)
const selectedTagId = ref<number | null>(null)

const activeFilter = computed(() => selectedCatId.value !== null || selectedTagId.value !== null)

const currentFilterTitle = computed(() => {
  if (selectedCatId.value) {
    const c = categories.value.find(x => x.id === selectedCatId.value)
    return `分类：${c ? c.name : ''} 下的文章`
  }
  if (selectedTagId.value) {
    const t = tags.value.find(x => x.id === selectedTagId.value)
    return `标签：${t ? t.name : ''} 下的文章`
  }
  return '全部文章归档'
})

const loadMeta = async () => {
  const [cats, tgs] = await Promise.all([getCategoriesApi(), getTagsApi()])
  categories.value = cats
  tags.value = tgs
  loadArticles()
}

const loadArticles = async () => {
  loading.value = true
  try {
    const res = await getArticlesApi({
      category_id: selectedCatId.value || undefined,
      tag_id: selectedTagId.value || undefined,
      size: 50
    })
    articles.value = res.list
  } finally {
    loading.value = false
  }
}

const selectCategory = (id: number) => {
  selectedCatId.value = id
  selectedTagId.value = null
  loadArticles()
}

const selectTag = (id: number) => {
  selectedTagId.value = id
  selectedCatId.value = null
  loadArticles()
}

const resetFilter = () => {
  selectedCatId.value = null
  selectedTagId.value = null
  loadArticles()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  loadMeta()
})
</script>

<style scoped>
.categories-page {
  min-height: 100vh;
  background: transparent;
}

.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 2.5rem 2.5rem 5rem 2.5rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  color: #18181b;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  font-size: 0.95rem;
  color: #71717a;
  margin: 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 3rem;
}

.category-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.5rem;
  border: 1px solid #e4e4e7;
  cursor: pointer;
  transition: all 0.2s;
}

.category-card:hover {
  transform: translateY(-2px);
  border-color: #10b981;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.cat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.cat-icon {
  font-size: 1.4rem;
}

.cat-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #18181b;
}

.cat-count-badge {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 700;
  background: #ecfdf5;
  color: #059669;
  padding: 2px 8px;
  border-radius: 6px;
}

.cat-desc {
  font-size: 0.85rem;
  color: #71717a;
  margin: 0;
  line-height: 1.5;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #18181b;
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tags-section {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.75rem;
  border: 1px solid #e4e4e7;
  margin-bottom: 3rem;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-badge {
  border: 1px solid;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-badge:hover {
  transform: scale(1.05);
  background: #f4f4f5;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.article-row-card {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 10px;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s;
}

.article-row-card:hover {
  border-color: #10b981;
  transform: translateX(4px);
}

.art-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #18181b;
}

.art-date {
  font-size: 0.82rem;
  color: #71717a;
}
</style>
