<template>
  <div class="help-center">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>帮助中心</h2>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索帮助文档..."
        prefix-icon="Search"
        class="search-input"
        @input="handleSearch"
      />
    </div>

    <!-- 帮助分类 -->
    <div class="help-categories">
      <el-card class="category-card" v-for="category in categories" :key="category.id">
        <div class="category-header" @click="toggleCategory(category.id)">
          <el-icon class="category-icon">
            <component :is="category.icon" />
          </el-icon>
          <h3>{{ category.name }}</h3>
          <el-icon class="expand-icon" :class="{ expanded: expandedCategories.includes(category.id) }">
            <ArrowDown />
          </el-icon>
        </div>
        
        <div class="category-content" v-show="expandedCategories.includes(category.id)">
          <div class="help-items">
            <div
              class="help-item"
              v-for="item in category.items"
              :key="item.id"
              @click="viewHelpItem(item)"
            >
              <h4>{{ item.title }}</h4>
              <p>{{ item.description }}</p>
              <div class="item-meta">
                <span class="category-tag">{{ item.category }}</span>
                <span class="update-time">{{ item.updateTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快速入门 -->
    <el-card class="quick-start">
      <template #header>
        <div class="card-header">
          <h3>快速入门</h3>
        </div>
      </template>
      
      <div class="quick-start-content">
        <div class="step-item" v-for="(step, index) in quickStartSteps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <h4>{{ step.title }}</h4>
            <p>{{ step.description }}</p>
            <el-button type="primary" size="small" @click="viewStepDetail(step)">
              查看详情
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 常见问题 -->
    <el-card class="faq">
      <template #header>
        <div class="card-header">
          <h3>常见问题</h3>
          <el-button type="text" @click="refreshFAQ">刷新</el-button>
        </div>
      </template>
      
      <div class="faq-content">
        <el-collapse v-model="activeFAQ">
          <el-collapse-item
            v-for="faq in faqList"
            :key="faq.id"
            :title="faq.question"
            :name="faq.id"
          >
            <div class="faq-answer" v-html="faq.answer"></div>
            <div class="faq-meta">
              <span class="helpful-count">有帮助 {{ faq.helpfulCount }} 次</span>
              <el-button type="text" size="small" @click="markHelpful(faq)">
                👍 有帮助
              </el-button>
              <el-button type="text" size="small" @click="markNotHelpful(faq)">
                👎 没帮助
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 视频教程 -->
    <el-card class="video-tutorials">
      <template #header>
        <div class="card-header">
          <h3>视频教程</h3>
          <el-button type="text" @click="viewAllVideos">查看全部</el-button>
        </div>
      </template>
      
      <div class="video-grid">
        <div
          class="video-item"
          v-for="video in videoList"
          :key="video.id"
          @click="playVideo(video)"
        >
          <div class="video-thumbnail">
            <img :src="video.thumbnail" :alt="video.title" />
            <div class="play-button">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <span class="video-duration">{{ video.duration }}</span>
          </div>
          <div class="video-info">
            <h4>{{ video.title }}</h4>
            <p>{{ video.description }}</p>
            <div class="video-meta">
              <span>{{ video.views }} 次观看</span>
              <span>{{ video.uploadTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 联系支持 -->
    <el-card class="contact-support">
      <template #header>
        <div class="card-header">
          <h3>联系支持</h3>
        </div>
      </template>
      
      <div class="support-options">
        <div class="support-option" @click="openTicketDialog">
          <el-icon class="support-icon"><Tickets /></el-icon>
          <h4>提交工单</h4>
          <p>创建技术支持工单，获得专业帮助</p>
        </div>
        
        <div class="support-option" @click="openChatDialog">
          <el-icon class="support-icon"><ChatDotRound /></el-icon>
          <h4>在线客服</h4>
          <p>与客服人员实时交流</p>
        </div>
        
        <div class="support-option" @click="callSupport">
          <el-icon class="support-icon"><Phone /></el-icon>
          <h4>电话支持</h4>
          <p>工作日 9:00-18:00</p>
        </div>
        
        <div class="support-option" @click="sendEmail">
          <el-icon class="support-icon"><Message /></el-icon>
          <h4>邮件支持</h4>
          <p>support@example.com</p>
        </div>
      </div>
    </el-card>

    <!-- 帮助详情对话框 -->
    <el-dialog
      v-model="helpDetailVisible"
      :title="currentHelpItem?.title"
      width="80%"
      class="help-detail-dialog"
    >
      <div class="help-detail-content" v-if="currentHelpItem">
        <div class="help-detail-header">
          <span class="help-category">{{ currentHelpItem.category }}</span>
          <span class="help-update-time">更新时间: {{ currentHelpItem.updateTime }}</span>
        </div>
        
        <div class="help-detail-body" v-html="currentHelpItem.content"></div>
        
        <div class="help-detail-actions">
          <el-button @click="likeHelpItem">
          <el-icon><Star /></el-icon>
          有帮助
        </el-button>
          <el-button @click="dislikeHelpItem">
          <el-icon><Close /></el-icon>
          没帮助
        </el-button>
          <el-button @click="shareHelpItem">
            <el-icon><Share /></el-icon>
            分享
          </el-button>
          <el-button @click="printHelpItem">
            <el-icon><Printer /></el-icon>
            打印
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 视频播放对话框 -->
    <el-dialog
      v-model="videoDialogVisible"
      :title="currentVideo?.title"
      width="80%"
      class="video-dialog"
    >
      <div class="video-player" v-if="currentVideo">
        <video
          ref="videoPlayer"
          :src="currentVideo.url"
          controls
          width="100%"
          height="400"
        ></video>
        <div class="video-description">
          <p>{{ currentVideo.description }}</p>
        </div>
      </div>
    </el-dialog>

    <!-- 工单提交对话框 -->
    <el-dialog
      v-model="ticketDialogVisible"
      title="提交技术支持工单"
      width="60%"
      class="ticket-dialog"
    >
      <el-form :model="ticketForm" label-width="100px">
        <el-form-item label="问题类型" required>
          <el-select v-model="ticketForm.type" placeholder="请选择问题类型">
            <el-option label="功能问题" value="feature" />
            <el-option label="技术问题" value="technical" />
            <el-option label="账户问题" value="account" />
            <el-option label="其他问题" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="问题标题" required>
          <el-input v-model="ticketForm.title" placeholder="请输入问题标题" />
        </el-form-item>
        
        <el-form-item label="问题描述" required>
          <el-input
            v-model="ticketForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您遇到的问题"
          />
        </el-form-item>
        
        <el-form-item label="附件">
          <el-upload
            :action="uploadUrl"
            :file-list="ticketForm.attachments"
            :on-success="handleUploadSuccess"
            :on-remove="handleUploadRemove"
            multiple
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传图片、文档等文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="联系方式">
          <el-input v-model="ticketForm.contact" placeholder="邮箱或电话" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="ticketDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTicket">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  ArrowDown,
  VideoPlay,
  Tickets,
  ChatDotRound,
  Phone,
  Message,
  Star,
  Close,
  Share,
  Printer,
  Document,
  Setting,
  Monitor,
  DataAnalysis,
  User,
  Lock
} from '@element-plus/icons-vue'

// 响应式数据
const searchKeyword = ref('')
const expandedCategories = ref(['getting-started'])
const activeFAQ = ref([])
const helpDetailVisible = ref(false)
const videoDialogVisible = ref(false)
const ticketDialogVisible = ref(false)
const currentHelpItem = ref(null)
const currentVideo = ref(null)
const uploadUrl = ref('/api/upload/help')

// 帮助分类
const categories = ref([
  {
    id: 'getting-started',
    name: '快速入门',
    icon: Document,
    items: [
      {
        id: 'gs-1',
        title: '平台介绍',
        description: '了解移动测试平台的基本功能和特点',
        category: '快速入门',
        updateTime: '2024-01-15',
        content: '<h2>平台介绍</h2><p>移动测试平台是一个专业的...</p>'
      },
      {
        id: 'gs-2',
        title: '注册登录',
        description: '如何注册账户和登录系统',
        category: '快速入门',
        updateTime: '2024-01-14',
        content: '<h2>注册登录</h2><p>注册流程如下...</p>'
      },
      {
        id: 'gs-3',
        title: '界面概览',
        description: '熟悉平台的主要界面和功能区域',
        category: '快速入门',
        updateTime: '2024-01-13',
        content: '<h2>界面概览</h2><p>平台界面包含...</p>'
      }
    ]
  },
  {
    id: 'device-management',
    name: '设备管理',
    icon: Monitor,
    items: [
      {
        id: 'dm-1',
        title: '添加设备',
        description: '如何连接和管理测试设备',
        category: '设备管理',
        updateTime: '2024-01-12',
        content: '<h2>添加设备</h2><p>设备连接方式...</p>'
      },
      {
        id: 'dm-2',
        title: '设备监控',
        description: '实时监控设备状态和性能',
        category: '设备管理',
        updateTime: '2024-01-11',
        content: '<h2>设备监控</h2><p>监控指标包括...</p>'
      }
    ]
  },
  {
    id: 'test-management',
    name: '测试管理',
    icon: DataAnalysis,
    items: [
      {
        id: 'tm-1',
        title: '创建测试用例',
        description: '编写和管理自动化测试用例',
        category: '测试管理',
        updateTime: '2024-01-10',
        content: '<h2>创建测试用例</h2><p>测试用例编写规范...</p>'
      },
      {
        id: 'tm-2',
        title: '执行测试任务',
        description: '配置和执行测试任务',
        category: '测试管理',
        updateTime: '2024-01-09',
        content: '<h2>执行测试任务</h2><p>任务执行流程...</p>'
      }
    ]
  },
  {
    id: 'user-management',
    name: '用户管理',
    icon: User,
    items: [
      {
        id: 'um-1',
        title: '用户权限',
        description: '管理用户账户和权限设置',
        category: '用户管理',
        updateTime: '2024-01-08',
        content: '<h2>用户权限</h2><p>权限管理说明...</p>'
      }
    ]
  },
  {
    id: 'system-settings',
    name: '系统设置',
    icon: Setting,
    items: [
      {
        id: 'ss-1',
        title: '基础配置',
        description: '系统基础参数配置',
        category: '系统设置',
        updateTime: '2024-01-07',
        content: '<h2>基础配置</h2><p>配置项说明...</p>'
      },
      {
        id: 'ss-2',
        title: '安全设置',
        description: '系统安全和访问控制配置',
        category: '系统设置',
        updateTime: '2024-01-06',
        content: '<h2>安全设置</h2><p>安全配置项...</p>'
      }
    ]
  }
])

// 快速入门步骤
const quickStartSteps = ref([
  {
    title: '注册账户',
    description: '创建您的测试平台账户，开始使用各项功能',
    detail: '注册流程...'
  },
  {
    title: '连接设备',
    description: '将您的移动设备连接到平台进行测试',
    detail: '设备连接指南...'
  },
  {
    title: '创建项目',
    description: '创建测试项目，组织您的测试工作',
    detail: '项目管理说明...'
  },
  {
    title: '编写用例',
    description: '编写自动化测试用例，定义测试逻辑',
    detail: '用例编写教程...'
  },
  {
    title: '执行测试',
    description: '运行测试任务，获取测试结果',
    detail: '测试执行指南...'
  }
])

// 常见问题
const faqList = ref([
  {
    id: 'faq-1',
    question: '如何连接Android设备？',
    answer: '连接Android设备的步骤如下：<br>1. 确保设备已开启USB调试模式<br>2. 使用USB线连接设备和电脑<br>3. 在设备管理中添加设备...',
    helpfulCount: 156
  },
  {
    id: 'faq-2',
    question: '测试用例支持哪些编程语言？',
    answer: '平台支持多种编程语言编写测试用例：<br>• Python<br>• JavaScript<br>• Java<br>• Kotlin...',
    helpfulCount: 89
  },
  {
    id: 'faq-3',
    question: '如何批量导入测试用例？',
    answer: '批量导入测试用例的方法：<br>1. 准备符合模板格式的Excel文件<br>2. 在测试用例管理页面点击导入按钮<br>3. 选择文件并确认导入...',
    helpfulCount: 67
  }
])

// 视频教程
const videoList = ref([
  {
    id: 'video-1',
    title: '平台快速入门教程',
    description: '10分钟快速了解平台基本操作',
    thumbnail: '/images/video-thumb-1.jpg',
    url: '/videos/quick-start.mp4',
    duration: '10:23',
    views: 1250,
    uploadTime: '2024-01-15'
  },
  {
    id: 'video-2',
    title: '设备连接详解',
    description: '详细介绍各种设备的连接方法',
    thumbnail: '/images/video-thumb-2.jpg',
    url: '/videos/device-connection.mp4',
    duration: '15:45',
    views: 890,
    uploadTime: '2024-01-14'
  },
  {
    id: 'video-3',
    title: '测试用例编写实战',
    description: '从零开始编写第一个测试用例',
    thumbnail: '/images/video-thumb-3.jpg',
    url: '/videos/test-case-writing.mp4',
    duration: '25:18',
    views: 756,
    uploadTime: '2024-01-13'
  }
])

// 工单表单
const ticketForm = reactive({
  type: '',
  title: '',
  description: '',
  attachments: [],
  contact: ''
})

// 方法
const handleSearch = () => {
  // 实现搜索逻辑
  console.log('搜索:', searchKeyword.value)
}

const toggleCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const viewHelpItem = (item) => {
  currentHelpItem.value = item
  helpDetailVisible.value = true
}

const viewStepDetail = (step) => {
  ElMessage.info(step.detail)
}

const refreshFAQ = () => {
  ElMessage.success('FAQ已刷新')
}

const markHelpful = (faq) => {
  faq.helpfulCount++
  ElMessage.success('感谢您的反馈！')
}

const markNotHelpful = (faq) => {
  ElMessage.info('我们会继续改进，感谢您的反馈！')
}

const playVideo = (video) => {
  currentVideo.value = video
  videoDialogVisible.value = true
}

const viewAllVideos = () => {
  ElMessage.info('跳转到视频教程页面')
}

const openTicketDialog = () => {
  ticketDialogVisible.value = true
}

const openChatDialog = () => {
  ElMessage.info('正在连接在线客服...')
}

const callSupport = () => {
  ElMessage.info('客服电话: 400-123-4567')
}

const sendEmail = () => {
  ElMessage.info('邮件地址: support@example.com')
}

const likeHelpItem = () => {
  ElMessage.success('感谢您的反馈！')
}

const dislikeHelpItem = () => {
  ElMessage.info('我们会继续改进，感谢您的反馈！')
}

const shareHelpItem = () => {
  ElMessage.success('分享链接已复制到剪贴板')
}

const printHelpItem = () => {
  window.print()
}

const handleUploadSuccess = (response, file) => {
  ticketForm.attachments.push({
    name: file.name,
    url: response.data.url
  })
}

const handleUploadRemove = (file, fileList) => {
  ticketForm.attachments = fileList
}

const submitTicket = () => {
  if (!ticketForm.type || !ticketForm.title || !ticketForm.description) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  // 提交工单逻辑
  ElMessage.success('工单提交成功，我们会尽快处理')
  ticketDialogVisible.value = false
  
  // 重置表单
  Object.assign(ticketForm, {
    type: '',
    title: '',
    description: '',
    attachments: [],
    contact: ''
  })
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.help-center {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-input {
  width: 300px;
}

.help-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.category-card {
  transition: transform 0.2s;
}

.category-card:hover {
  transform: translateY(-2px);
}

.category-header {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px 0;
}

.category-icon {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.category-header h3 {
  margin: 0;
  flex: 1;
  color: #303133;
}

.expand-icon {
  transition: transform 0.3s;
  color: #909399;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.category-content {
  padding-top: 10px;
}

.help-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.help-item {
  padding: 15px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.help-item:hover {
  border-color: #409EFF;
  background-color: #F5F7FA;
}

.help-item h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.help-item p {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-tag {
  background-color: #E1F3D8;
  color: #67C23A;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.update-time {
  color: #909399;
  font-size: 12px;
}

.quick-start,
.faq,
.video-tutorials,
.contact-support {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.quick-start-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.step-number {
  width: 30px;
  height: 30px;
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.step-content p {
  margin: 0 0 10px 0;
  color: #606266;
}

.faq-answer {
  margin-bottom: 15px;
  line-height: 1.6;
}

.faq-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #909399;
  font-size: 14px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.video-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.video-item:hover {
  transform: translateY(-2px);
}

.video-thumbnail {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.video-thumbnail img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.video-duration {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.video-info {
  padding: 10px 0;
}

.video-info h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.video-info p {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.video-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
}

.support-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.support-option {
  text-align: center;
  padding: 20px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.support-option:hover {
  border-color: #409EFF;
  background-color: #F5F7FA;
}

.support-icon {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 10px;
}

.support-option h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.support-option p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.help-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #EBEEF5;
}

.help-category {
  background-color: #E1F3D8;
  color: #67C23A;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.help-update-time {
  color: #909399;
  font-size: 14px;
}

.help-detail-body {
  line-height: 1.8;
  margin-bottom: 20px;
}

.help-detail-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

@media (max-width: 768px) {
  .help-center {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .help-categories {
    grid-template-columns: 1fr;
  }

  .video-grid {
    grid-template-columns: 1fr;
  }

  .support-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .help-detail-actions {
    flex-wrap: wrap;
  }
}
</style>