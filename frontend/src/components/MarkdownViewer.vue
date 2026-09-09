<template>
  <div class="markdown-body" v-html="renderedHtml"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

const props = defineProps<{
  content: string
}>()

// 配置 marked 与 highlight.js 代码高亮
marked.setOptions({
  gfm: true,
  breaks: true,
  // @ts-ignore
  highlight: function (code: string, lang: string) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  }
})

const renderedHtml = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content) as string
})
</script>

<style>
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  word-break: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  color: #1a1a1a;
  margin-top: 1.6em;
  margin-bottom: 0.8em;
  font-weight: 700;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 0.3em;
}

.markdown-body h1 { font-size: 2rem; border-bottom: 2px solid #18181b; }
.markdown-body h2 { font-size: 1.5rem; }
.markdown-body h3 { font-size: 1.25rem; border-bottom: none; }

.markdown-body p {
  margin-bottom: 1.2em;
}

.markdown-body blockquote {
  margin: 1.2em 0;
  padding: 0.8em 1.2em;
  color: #52525b;
  background-color: #f4f4f5;
  border-left: 4px solid #10b981;
  border-radius: 4px;
}

.markdown-body pre {
  background-color: #282c34;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2em 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.markdown-body pre code {
  background: transparent;
  padding: 0;
  color: #abb2bf;
  font-family: "Fira Code", Consolas, Monaco, "Courier New", Courier, monospace;
  font-size: 0.92rem;
}

.markdown-body :not(pre) > code {
  background-color: #f2f4f7;
  color: #e03997;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: monospace;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid #dcdfe6;
  padding: 10px 14px;
  text-align: left;
}

.markdown-body th {
  background-color: #f5f7fa;
  font-weight: 600;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 24px;
  margin-bottom: 1.2em;
}

.markdown-body li {
  margin-bottom: 0.4em;
}
</style>
