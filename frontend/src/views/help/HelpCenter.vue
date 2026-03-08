<template>
  <div class="help-center">
    <div class="page-header">
      <div class="header-content">
        <h1>帮助中心</h1>
       
      </div>
      <div class="header-actions">
        <div class="search-area">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索帮助文档..."
            prefix-icon="Search"
            class="search-input"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-button
            type="primary"
            @click="handleSearch"
          >
            搜索
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </div>
      </div>
    </div>

    <el-card class="video-tutorials">
      <template #header>
        <div class="card-header">
          <h3>视频教程</h3>
          <el-button
            type="text"
            @click="viewAllVideos"
          >
            查看全部
          </el-button>
        </div>
      </template>

      <div class="video-grid">
        <div
          v-for="video in filteredVideoList"
          :key="video.id"
          class="video-item"
          @click="playVideo(video)"
        >
          <div class="video-thumbnail">
            <img
              v-if="video.thumbnail"
              :src="video.thumbnail"
              :alt="video.title"
            >
            <div
              v-else
              class="video-thumbnail-placeholder"
            >
              <el-icon class="placeholder-icon"><VideoPlay /></el-icon>
              <span class="placeholder-text">视频教程</span>
            </div>
            <div class="play-button">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <span class="video-duration">{{ video.duration }}</span>
            <span
              v-if="video.tag"
              class="video-tag"
            >{{ video.tag }}</span>
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

    <div class="help-categories">
      <div class="help-categories-column">
        <el-card
          v-for="category in filteredLeftCategories"
          :key="category.id"
          class="category-card"
        >
          <div
            class="category-header"
            @click="toggleCategory(category.id)"
          >
            <el-icon class="category-icon">
              <component :is="category.icon" />
            </el-icon>
            <h3>{{ category.name }}</h3>
            <el-icon
              class="expand-icon"
              :class="{ expanded: expandedCategories.includes(category.id) }"
            >
              <ArrowDown />
            </el-icon>
          </div>

          <div
            v-show="expandedCategories.includes(category.id)"
            class="category-content"
          >
            <div class="help-items">
              <div
                v-for="item in category.items"
                :key="item.id"
                class="help-item"
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
      <div class="help-categories-column">
        <el-card
          v-for="category in filteredRightCategories"
          :key="category.id"
          class="category-card"
        >
          <div
            class="category-header"
            @click="toggleCategory(category.id)"
          >
            <el-icon class="category-icon">
              <component :is="category.icon" />
            </el-icon>
            <h3>{{ category.name }}</h3>
            <el-icon
              class="expand-icon"
              :class="{ expanded: expandedCategories.includes(category.id) }"
            >
              <ArrowDown />
            </el-icon>
          </div>

          <div
            v-show="expandedCategories.includes(category.id)"
            class="category-content"
          >
            <div class="help-items">
              <div
                v-for="item in category.items"
                :key="item.id"
                class="help-item"
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
    </div>

    <el-card class="faq">
      <template #header>
        <div class="card-header">
          <h3>常见问题</h3>
          <el-button
            type="text"
            @click="refreshFAQ"
          >
            刷新
          </el-button>
        </div>
      </template>

      <div class="faq-content">
        <el-collapse v-model="activeFAQ">
          <el-collapse-item
            v-for="faq in filteredFaqList"
            :key="faq.id"
            :title="faq.question"
            :name="faq.id"
          >
            <div
              class="faq-answer"
              v-html="faq.answer"
            />
            <div class="faq-meta">
              <span class="helpful-count">有帮助 {{ faq.helpfulCount }} 次</span>
              <el-button
                type="text"
                size="small"
                @click="markHelpful(faq)"
              >
                👍 有帮助
              </el-button>
              <el-button
                type="text"
                size="small"
                @click="markNotHelpful(faq)"
              >
                👎 没帮助
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <el-card class="developer-contact">
      <template #header>
        <div class="card-header">
          <h3>开发者联系</h3>
        </div>
      </template>

      <div class="developer-contact-content">
        <p class="developer-desc">
          本平台由企业内部人员开发与持续维护。如在使用过程中遇到问题或有宝贵建议，请通过公司内部渠道联系
          <a href="mailto:s_chenguohui@wps.cn" class="developer-link" style="color:#409EFF; " target="_blank">
            @陈国慧（s_chenguohui@wps.cn）
          </a>
        </p>
      </div>
    </el-card>

    <el-dialog
      v-model="helpDetailVisible"
      :title="currentHelpItem?.title"
      width="80%"
      class="help-detail-dialog"
    >
      <div
        v-if="currentHelpItem"
        class="help-detail-content"
      >
        <div class="help-detail-header">
          <span class="help-category">{{ currentHelpItem.category }}</span>
          <span class="help-update-time">更新时间: {{ currentHelpItem.updateTime }}</span>
        </div>

        <div
          class="help-detail-body"
          v-html="currentHelpItem.content"
        />

        <div class="help-detail-actions">
          <el-button @click="likeHelpItem">
            <el-icon><Star /></el-icon>
            有帮助
          </el-button>
          <el-button @click="dislikeHelpItem">
            <el-icon><Close /></el-icon>
            没帮助
          </el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="videoDialogVisible"
      :title="currentVideo?.title"
      width="80%"
      class="video-dialog"
    >
      <div
        v-if="currentVideo"
        class="video-player"
      >
        <video
          ref="videoPlayer"
          :src="currentVideo.url"
          controls
          width="100%"
          height="400"
        />
        <div class="video-description">
          <p>{{ currentVideo.description }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Search,
  ArrowDown,
  VideoPlay,
  ChatDotRound,
  Star,
  Close,
  Document,
  Setting,
  Monitor,
  User,
  Briefcase,
  Calendar,
  List,
  Odometer,
  Key,
} from "@element-plus/icons-vue";

const searchKeyword = ref("");
/** 实际参与过滤的关键字（点击搜索后生效） */
const appliedSearchKeyword = ref("");
const expandedCategories = ref([]);
const activeFAQ = ref([]);
const helpDetailVisible = ref(false);
const videoDialogVisible = ref(false);
const currentHelpItem = ref(null);
const currentVideo = ref(null);

// 帮助分类（按用户流程排序：规划阶段 → 准备阶段 → 执行阶段 → 管理配置；左右两列均分，展开互不影响）
const categories = ref([
  {
    id: "projects",
    name: "项目管理",
    icon: Briefcase,
    items: [
      {
        id: "proj-1",
        title: "创建与编辑项目",
        description: "在项目管理中新建项目、填写名称与描述，并编辑项目信息",
        category: "项目管理",
        updateTime: "2024-01-15",
        content: "<h2>创建与编辑项目</h2><p>进入「项目管理」页面，点击「新建项目」填写项目名称、描述等；在列表中可对已有项目进行编辑、删除等操作。</p>",
      },
      {
        id: "proj-2",
        title: "项目详情与成员",
        description: "查看项目详情、管理项目成员与权限",
        category: "项目管理",
        updateTime: "2024-01-14",
        content: "<h2>项目详情与成员</h2><p>点击项目名称进入项目详情页，可查看关联的迭代、需求、设备等；在成员管理中可添加或移除成员并分配角色。</p>",
      },
    ],
  },
  {
    id: "iterations",
    name: "迭代管理",
    icon: Calendar,
    items: [
      {
        id: "iter-1",
        title: "创建迭代",
        description: "为项目创建迭代版本，规划测试周期",
        category: "迭代管理",
        updateTime: "2024-01-13",
        content: "<h2>创建迭代</h2><p>在「迭代管理」中按项目筛选后点击「新建迭代」，填写迭代名称、计划开始/结束时间等，便于按版本组织用例与执行记录。</p>",
      },
      {
        id: "iter-2",
        title: "迭代与需求关联",
        description: "将需求关联到迭代，跟踪版本范围",
        category: "迭代管理",
        updateTime: "2024-01-12",
        content: "<h2>迭代与需求关联</h2><p>在迭代详情或需求管理中，可将需求关联到指定迭代，便于按迭代统计需求覆盖与测试进度。</p>",
      },
    ],
  },
  {
    id: "requirements",
    name: "需求管理",
    icon: Document,
    items: [
      {
        id: "req-1",
        title: "需求的创建与编辑",
        description: "新建需求、填写标题与描述，并关联到项目与迭代",
        category: "需求管理",
        updateTime: "2024-01-11",
        content: "<h2>需求的创建与编辑</h2><p>在「需求管理」中可新建需求，填写标题、描述、优先级等，并选择所属项目和迭代；支持对需求进行编辑、状态变更等操作。</p>",
      },
      {
        id: "req-2",
        title: "需求与用例关联",
        description: "将测试用例关联到需求，实现需求覆盖追溯",
        category: "需求管理",
        updateTime: "2024-01-10",
        content: "<h2>需求与用例关联</h2><p>在需求详情或用例管理中，可将测试用例关联到需求，用于跟踪需求对应的测试覆盖情况。</p>",
      },
    ],
  },
  {
    id: "devices",
    name: "设备管理",
    icon: Monitor,
    items: [
      {
        id: "dev-1",
        title: "设备连接与列表",
        description: "通过 USB 或无线连接设备，在设备列表中查看与管理",
        category: "设备管理",
        updateTime: "2024-01-09",
        content: "<h2>设备连接与列表</h2><p>在「设备管理」中可查看已连接设备列表；通过 USB 连接并开启调试后刷新列表，或使用无线连接功能将设备加入平台。</p>",
      },
      {
        id: "dev-2",
        title: "设备详情与任务",
        description: "查看设备详情、为设备分配或执行测试任务",
        category: "设备管理",
        updateTime: "2024-01-08",
        content: "<h2>设备详情与任务</h2><p>点击设备进入设备详情页，可查看设备信息、状态及历史任务；可为该设备创建或分配测试任务并执行。</p>",
      },
    ],
  },
  {
    id: "test-cases",
    name: "用例管理",
    icon: Document,
    items: [
      {
        id: "tc-1",
        title: "用例的创建与编辑",
        description: "新建用例、填写步骤与预期结果，支持脑图与树形结构",
        category: "用例管理",
        updateTime: "2024-01-07",
        content: "<h2>用例的创建与编辑</h2><p>在「用例管理」中可新建测试用例，填写用例名称、前置条件、步骤与预期结果；支持测试套件树形组织及脑图视图。</p>",
      },
      {
        id: "tc-2",
        title: "测试套件与导入导出",
        description: "使用测试套件组织用例，支持批量导入与导出",
        category: "用例管理",
        updateTime: "2024-01-06",
        content: "<h2>测试套件与导入导出</h2><p>通过测试套件对用例进行分组管理；支持按模板批量导入用例，或导出用例数据便于备份与迁移。</p>",
      },
    ],
  },
  {
    id: "case-reviews",
    name: "用例评审",
    icon: ChatDotRound,
    items: [
      {
        id: "cr-1",
        title: "评审任务与流程",
        description: "创建评审任务、分配评审人，完成用例评审流程",
        category: "用例评审",
        updateTime: "2024-01-05",
        content: "<h2>评审任务与流程</h2><p>在「用例评审」中可创建评审任务，选择待评审用例并指定评审人；评审人可对用例提出意见，通过后完成评审流程。</p>",
      },
    ],
  },
  {
    id: "test-tasks",
    name: "测试任务",
    icon: List,
    items: [
      {
        id: "tt-1",
        title: "创建测试任务",
        description: "选择设备与用例/套件，配置任务参数并保存",
        category: "测试任务",
        updateTime: "2024-01-04",
        content: "<h2>创建测试任务</h2><p>在「测试任务」中点击新建，选择目标设备（或设备组）、要执行的用例或测试套件，配置超时等参数后保存任务。</p>",
      },
      {
        id: "tt-2",
        title: "执行与查看日志",
        description: "执行任务并实时查看执行日志与用例结果",
        category: "测试任务",
        updateTime: "2024-01-03",
        content: "<h2>执行与查看日志</h2><p>在任务列表中点击「执行」启动任务，可进入执行页查看实时日志与每个用例的通过/失败状态，执行完成后可跳转至报告详情。</p>",
      },
    ],
  },
  {
    id: "report",
    name: "报告管理",
    icon: Odometer,
    items: [
      {
        id: "rpt-1",
        title: "报告列表与筛选",
        description: "按类型、项目、时间筛选并查看测试报告列表",
        category: "报告管理",
        updateTime: "2024-01-02",
        content: "<h2>报告列表与筛选</h2><p>在「报告管理」中可按用例测试/设备脚本等类型、项目、时间范围筛选报告，查看历史执行记录与统计概览。</p>",
      },
      {
        id: "rpt-2",
        title: "报告详情与导出",
        description: "查看单次执行详情、通过率与失败原因，支持导出",
        category: "报告管理",
        updateTime: "2024-01-01",
        content: "<h2>报告详情与导出</h2><p>点击报告进入详情页，可查看通过率、失败用例及日志；支持将报告导出为文件便于归档或分享。</p>",
      },
    ],
  },
  {
    id: "users",
    name: "用户管理",
    icon: User,
    items: [
      {
        id: "usr-1",
        title: "用户与角色",
        description: "管理平台用户账户、角色与权限",
        category: "用户管理",
        updateTime: "2023-12-31",
        content: "<h2>用户与角色</h2><p>在「用户管理」中可查看用户列表、新建或编辑用户，并为用户分配角色（如管理员、测试、只读等），不同角色拥有不同的功能权限。</p>",
      },
    ],
  },
  {
    id: "permission-config",
    name: "权限配置",
    icon: Key,
    items: [
      {
        id: "perm-1",
        title: "角色与权限配置入口",
        description: "进入权限配置页、选择角色并查看当前已勾选的功能权限",
        category: "权限配置",
        updateTime: "2024-01-16",
        content: "<h2>角色与权限配置入口</h2><p>拥有「权限配置」权限的用户可在系统设置或侧栏进入「角色权限配置」页。页面上方选择角色（管理员、测试人员、普通用户），即可查看该角色当前已勾选的功能埋点。超管权限不可修改。</p>",
      },
      {
        id: "perm-2",
        title: "为角色勾选功能权限",
        description: "按模块为角色勾选或取消功能点，保存后立即生效",
        category: "权限配置",
        updateTime: "2024-01-16",
        content: "<h2>为角色勾选功能权限</h2><p>权限按 5 个模块展示：项目管理、迭代管理、需求管理、权限配置、用户管理。每个模块下可勾选「入口（列表/查看）」及增删改等操作。勾选后点击「保存配置」即可生效，该角色下所有用户将仅拥有已勾选的功能。</p>",
      },
    ],
  },
  {
    id: "profile",
    name: "个人中心",
    icon: User,
    items: [
      {
        id: "profile-1",
        title: "个人资料与修改",
        description: "查看与编辑真实姓名、性别、手机号、部门等个人信息",
        category: "个人中心",
        updateTime: "2024-01-16",
        content: "<h2>个人资料与修改</h2><p>在「个人中心」可查看当前登录账号的基本信息；点击「编辑」可修改真实姓名、性别、手机号、部门等，修改后保存即可生效。</p>",
      },
      {
        id: "profile-2",
        title: "修改密码",
        description: "修改当前账号的登录密码，修改成功后需重新登录",
        category: "个人中心",
        updateTime: "2024-01-16",
        content: "<h2>修改密码</h2><p>在个人中心「修改密码」区域填写原密码与新密码，提交后系统会校验原密码并更新。为保障安全，修改成功后将退出登录，需使用新密码重新登录。</p>",
      },
    ],
  },
  {
    id: "settings",
    name: "系统设置",
    icon: Setting,
    items: [
      {
        id: "set-1",
        title: "基础与安全配置",
        description: "系统名称、Logo、登录失败锁定、会话超时等安全与访问控制",
        category: "系统设置",
        updateTime: "2024-01-16",
        content: "<h2>基础与安全配置</h2><p>在「系统设置」→「基础设置」中可配置系统名称、简称、Logo 等；在「安全设置」中可配置登录失败锁定次数、会话超时时间等，提升账号与访问安全。</p>",
      },
      {
        id: "set-2",
        title: "消息通知与功能设置",
        description: "消息通知方式、报告自动生成等功能开关",
        category: "系统设置",
        updateTime: "2024-01-16",
        content: "<h2>消息通知与功能设置</h2><p>在「消息通知」中可配置站内消息、邮件等通知方式；在「功能设置」中可配置如「任务完成后是否自动生成报告」等开关，满足不同团队使用习惯。</p>",
      },
    ],
  },
]);

const leftCategories = computed(() => {
  const list = categories.value;
  const mid = Math.ceil(list.length / 2);
  return list.slice(0, mid);
});

const rightCategories = computed(() => {
  const list = categories.value;
  const mid = Math.ceil(list.length / 2);
  return list.slice(mid);
});

function stripHtml(html) {
  if (!html) return "";
  return String(html).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

function matchKeyword(text, keyword) {
  if (!keyword || !text) return false;
  return stripHtml(String(text)).toLowerCase().includes(keyword.toLowerCase());
}

const filteredCategories = computed(() => {
  const kw = appliedSearchKeyword.value.trim();
  const list = categories.value;
  if (!kw) return list;

  return list
    .map((cat) => {
      const filteredItems = cat.items.filter(
        (item) =>
          matchKeyword(item.title, kw) ||
          matchKeyword(item.description, kw) ||
          matchKeyword(item.content, kw),
      );
      if (filteredItems.length === 0) return null;
      return { ...cat, items: filteredItems };
    })
    .filter(Boolean);
});

const filteredLeftCategories = computed(() => {
  const list = filteredCategories.value;
  const mid = Math.ceil(list.length / 2);
  return list.slice(0, mid);
});

const filteredRightCategories = computed(() => {
  const list = filteredCategories.value;
  const mid = Math.ceil(list.length / 2);
  return list.slice(mid);
});

const filteredVideoList = computed(() => {
  const kw = appliedSearchKeyword.value.trim();
  const list = videoList.value;
  if (!kw) return list;
  return list.filter(
    (v) =>
      matchKeyword(v.title, kw) ||
      matchKeyword(v.description, kw) ||
      matchKeyword(v.tag, kw),
  );
});

const filteredFaqList = computed(() => {
  const kw = appliedSearchKeyword.value.trim();
  const list = faqList.value;
  if (!kw) return list;
  return list.filter(
    (f) => matchKeyword(f.question, kw) || matchKeyword(f.answer, kw),
  );
});

const faqList = ref([
  {
    id: "faq-1",
    question: "如何连接 Android 设备？",
    answer:
      "连接 Android 设备请按以下步骤操作：<br>1. 在设备「设置」→「开发者选项」中开启 <strong>USB 调试</strong><br>2. 使用 USB 数据线将设备与电脑连接，并在设备上允许 USB 调试授权<br>3. 打开平台「设备管理」页面，点击「添加设备」或「刷新设备列表」<br>4. 若设备未识别，请检查 USB 线是否支持数据传输、是否已安装对应机型驱动，或尝试更换 USB 端口",
    helpfulCount: 256,
  },
  {
    id: "faq-2",
    question: "测试用例支持哪些编写方式？",
    answer:
      "平台支持多种方式编写与管理测试用例：<br>• <strong>脚本</strong>：支持 Python、JavaScript 等常见语言<br>• <strong>用例库</strong>：在「测试用例」中新建，填写步骤、预期结果等<br>• <strong>导入</strong>：支持从 Excel 模板批量导入，在「测试用例」页面使用「导入」功能下载模板后按格式填写并上传<br>具体支持的脚本语言与模板格式可在「测试管理」帮助文档中查看。",
    helpfulCount: 189,
  },
  {
    id: "faq-3",
    question: "如何批量导入测试用例？",
    answer:
      "批量导入步骤：<br>1. 在「测试用例」页面点击「导入」或「批量导入」<br>2. 下载平台提供的 Excel 模板，按列填写用例名称、步骤、预期结果、优先级等<br>3. 保存 Excel 后，在导入弹窗中选择该文件并上传<br>4. 系统会校验格式并预览，确认后执行导入。若存在重复或格式错误，会提示具体行号便于修改后重新导入。",
    helpfulCount: 167,
  },
  {
    id: "faq-4",
    question: "设备显示离线或无法连接怎么办？",
    answer:
      "可依次排查：<br>1. <strong>USB</strong>：重新插拔数据线，确认设备端弹出「允许 USB 调试」时勾选「始终允许」并确定<br>2. <strong>驱动</strong>：在电脑设备管理器中查看是否有未识别设备或叹号，安装或更新对应 ADB/厂商驱动<br>3. <strong>端口占用</strong>：关闭其他占用 ADB 的工具（如其他自动化工具、手机助手）后重试<br>4. <strong>无线连接</strong>：若使用 WiFi 连接，确认设备与电脑在同一网段，且 ADB 无线调试已开启并配对成功。",
    helpfulCount: 142,
  },
  {
    id: "faq-5",
    question: "如何创建与执行测试任务？",
    answer:
      "创建与执行流程：<br>1. 在「测试任务」中点击「新建任务」，选择所属项目与设备（或设备组）<br>2. 选择要执行的测试用例或测试套件，可设置执行顺序、重试次数等<br>3. 配置环境参数（如包名、超时时间等），保存任务<br>4. 在任务列表中点击「执行」，系统会调度设备并依次执行用例，执行过程中可在「测试任务」或「设备详情」中查看实时日志与结果。",
    helpfulCount: 198,
  },
  {
    id: "faq-6",
    question: "测试报告在哪里查看？",
    answer:
      "测试报告查看方式：<br>• <strong>单次任务</strong>：在「测试任务」列表中点击某次执行记录，进入执行详情即可查看通过/失败统计、用例明细及日志<br>• <strong>汇总报告</strong>：在「报告」或「测试报告」模块可按项目、时间范围筛选，查看多轮执行的汇总与趋势<br>报告支持导出为 PDF 或 Excel，便于归档与分享。",
    helpfulCount: 134,
  },
  {
    id: "faq-7",
    question: "如何管理项目与迭代？",
    answer:
      "项目与迭代管理：<br>• <strong>项目</strong>：在「项目管理」中新建项目，填写名称、描述等，后续设备、用例、任务均可关联到项目<br>• <strong>迭代</strong>：在项目下创建迭代（如 V1.0、Sprint1），执行任务时可选择迭代，便于按版本统计与追溯<br>在「迭代管理」中可查看各迭代下的用例与执行情况。",
    helpfulCount: 98,
  },
  {
    id: "faq-8",
    question: "忘记登录密码怎么办？",
    answer:
      "若忘记密码：<br>1. 在登录页点击「忘记密码」<br>2. 输入注册时使用的邮箱或手机号，获取验证码后设置新密码<br>若账号由管理员创建，可联系管理员在「用户管理」中为您重置密码；管理员可在「系统设置」中配置是否开启自助找回密码。",
    helpfulCount: 87,
  },
  {
    id: "faq-9",
    question: "如何分配设备与权限？",
    answer:
      "设备与权限由管理员配置：<br>• <strong>设备</strong>：在「设备管理」中可将设备分配到指定项目或池，并设置使用权限（如仅某角色可操作）<br>• <strong>用户与角色</strong>：在「用户管理」中为用户分配角色（如管理员、测试、只读），不同角色对设备、用例、任务的可见与操作范围不同<br>具体权限说明见「系统设置」→「权限说明」。",
    helpfulCount: 76,
  },
  {
    id: "faq-10",
    question: "支持 iOS 设备吗？",
    answer:
      "当前版本主要支持 Android 设备的连接与自动化测试。iOS 支持取决于平台配置与许可证：若已开通 iOS 能力，需使用 Mac 环境并配置相关代理/证书，在「设备管理」中可看到 iOS 设备的连接入口。具体支持范围与配置方式请以当前版本说明或联系管理员为准。",
    helpfulCount: 203,
  },
]);

// 视频教程（项目管理 → 设备管理 → 用例管理 → 任务管理 → 报告管理 → 用户管理 → 权限配置 → 个人中心 → 系统设置）
const videoList = ref([
  {
    id: "video-1",
    title: "项目与迭代管理",
    description: "创建项目、规划迭代，并将用例与任务按版本归类管理。",
    thumbnail: "",
    url: "/videos/project-iteration.mp4",
    duration: "09:50",
    views: 756,
    uploadTime: "2024-01-11",
    tag: "项目管理",
  },
  {
    id: "video-2",
    title: "设备连接与调试入门",
    description: "从 USB 连接、驱动检查到设备列表刷新，手把手完成首台设备接入。",
    thumbnail: "",
    url: "/videos/device-connection.mp4",
    duration: "08:32",
    views: 2150,
    uploadTime: "2024-01-15",
    tag: "设备管理",
  },
  {
    id: "video-3",
    title: "测试用例的创建与编辑",
    description: "在平台中新建用例、填写步骤与预期结果，并关联到测试套件。",
    thumbnail: "",
    url: "/videos/test-case-create.mp4",
    duration: "12:18",
    views: 1680,
    uploadTime: "2024-01-14",
    tag: "用例管理",
  },
  {
    id: "video-4",
    title: "测试任务配置与执行",
    description: "创建任务、选择设备与用例、设置参数，并查看执行日志与结果。",
    thumbnail: "",
    url: "/videos/test-task-run.mp4",
    duration: "15:42",
    views: 1420,
    uploadTime: "2024-01-13",
    tag: "任务管理",
  },
  {
    id: "video-5",
    title: "测试报告解读与导出",
    description: "如何查看通过率、失败原因，以及导出 PDF/Excel 报告。",
    thumbnail: "",
    url: "/videos/report-export.mp4",
    duration: "06:25",
    views: 980,
    uploadTime: "2024-01-12",
    tag: "报告管理",
  },
  {
    id: "video-6",
    title: "用户管理",
    description: "用户列表、新建与编辑用户、分配角色及禁用/启用账号。",
    thumbnail: "",
    url: "/videos/user-management.mp4",
    duration: "06:20",
    views: 620,
    uploadTime: "2024-01-10",
    tag: "用户管理",
  },
  {
    id: "video-7",
    title: "权限配置",
    description: "进入角色权限配置、为管理员/测试人员/普通用户勾选功能权限并保存。",
    thumbnail: "",
    url: "/videos/permission-config.mp4",
    duration: "05:50",
    views: 480,
    uploadTime: "2024-01-16",
    tag: "权限配置",
  },
  {
    id: "video-8",
    title: "个人中心",
    description: "修改个人资料与登录密码，修改密码后重新登录。",
    thumbnail: "",
    url: "/videos/profile.mp4",
    duration: "04:30",
    views: 520,
    uploadTime: "2024-01-16",
    tag: "个人中心",
  },
  {
    id: "video-9",
    title: "系统设置",
    description: "基础与安全配置、消息通知、功能设置（如报告自动生成）等。",
    thumbnail: "",
    url: "/videos/system-settings.mp4",
    duration: "06:10",
    views: 410,
    uploadTime: "2024-01-16",
    tag: "系统设置",
  },
]);

const handleSearch = () => {
  appliedSearchKeyword.value = searchKeyword.value.trim();
};

const handleReset = () => {
  searchKeyword.value = "";
  appliedSearchKeyword.value = "";
};

const toggleCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId);
  if (index > -1) {
    expandedCategories.value.splice(index, 1);
  } else {
    expandedCategories.value.push(categoryId);
  }
};

const viewHelpItem = (item) => {
  currentHelpItem.value = item;
  helpDetailVisible.value = true;
};

const refreshFAQ = () => {
  ElMessage.success("FAQ已刷新");
};

const markHelpful = (faq) => {
  faq.helpfulCount++;
  ElMessage.success("感谢您的反馈！");
};

const markNotHelpful = (faq) => {
  ElMessage.info("我们会继续改进，感谢您的反馈！");
};

const playVideo = (video) => {
  currentVideo.value = video;
  videoDialogVisible.value = true;
};

const viewAllVideos = () => {
  ElMessage.info("跳转到视频教程页面");
};

const likeHelpItem = () => {
  ElMessage.success("感谢您的反馈！");
};

const dislikeHelpItem = () => {
  ElMessage.info("我们会继续改进，感谢您的反馈！");
};

onMounted(() => {});
</script>

<style scoped>
.help-center {
  padding: 20px;
}

.page-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: var(--el-bg-color, #fff);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.page-header .header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.page-header .header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: var(--el-text-color-primary, #303133);
}

.page-header .description {
  margin: 0;
  color: var(--el-text-color-regular, #606266);
  font-size: 14px;
}

.page-header .header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.search-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 280px;
}

.help-categories {
  display: flex;
  gap: 24px;
  margin-bottom: 30px;
  align-items: flex-start;
}

.help-categories-column {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  color: #409eff;
  margin-right: 10px;
}

.category-header h3 {
  margin: 0;
  flex: 1;
  color: var(--el-text-color-primary, #303133);
}

.expand-icon {
  transition: transform 0.3s;
  color: var(--el-text-color-secondary, #909399);
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
  border: 1px solid var(--el-border-color-light, #ebeef5);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.help-item:hover {
  border-color: #409eff;
  background-color: var(--el-fill-color-light, #f5f7fa);
}

.help-item h4 {
  margin: 0 0 5px 0;
  color: var(--el-text-color-primary, #303133);
}

.help-item p {
  margin: 0 0 10px 0;
  color: var(--el-text-color-regular, #606266);
  font-size: 14px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-tag {
  background-color: #e1f3d8;
  color: #67c23a;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.update-time {
  color: var(--el-text-color-secondary, #909399);
  font-size: 12px;
}

.faq,
.video-tutorials,
.developer-contact {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: var(--el-text-color-primary, #303133);
}

.faq-content {
  max-height: 560px;
  overflow-y: auto;
}

.faq-content :deep(.el-collapse-item__header) {
  font-size: 15px;
  color: var(--el-text-color-primary, #303133);
}

.faq-content :deep(.el-collapse-item__content) {
  padding-bottom: 16px;
}

.faq-answer {
  margin-bottom: 15px;
  line-height: 1.7;
  color: var(--el-text-color-regular, #606266);
  font-size: 14px;
}

.faq-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: var(--el-text-color-secondary, #909399);
  font-size: 14px;
}

.video-tutorials :deep(.el-card__body) {
  padding: 24px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.video-item {
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-light, #ebeef5);
  transition: all 0.25s ease;
}

.video-item:hover {
  border-color: #409eff;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
  transform: translateY(-4px);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 160px;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e8ff 100%);
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #e8f4ff 0%, #cce0ff 50%, #b3d1ff 100%);
  color: #409eff;
}

.placeholder-icon {
  font-size: 40px;
  opacity: 0.9;
}

.placeholder-text {
  font-size: 13px;
  color: var(--el-text-color-regular, #606266);
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 56px;
  height: 56px;
  background-color: rgba(64, 158, 255, 0.92);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 26px;
  transition: transform 0.2s;
}

.video-item:hover .play-button {
  transform: translate(-50%, -50%) scale(1.08);
}

.video-duration {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.65);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.video-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(64, 158, 255, 0.9);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.video-info {
  padding: 16px;
}

.video-info h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary, #303133);
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-info p {
  margin: 0 0 12px 0;
  color: var(--el-text-color-regular, #606266);
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--el-text-color-secondary, #909399);
  font-size: 12px;
}

.developer-contact-content {
  padding: 4px 0;
}

.developer-desc {
  margin: 0;
  color: var(--el-text-color-regular, #606266);
  font-size: 14px;
  line-height: 1.7;
}

.developer-link {
  text-decoration: none;
}

.developer-link:hover {
  text-decoration: none;
}

.help-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color-light, #ebeef5);
}

.help-category {
  background-color: #e1f3d8;
  color: #67c23a;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.help-update-time {
  color: var(--el-text-color-secondary, #909399);
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
  border-top: 1px solid var(--el-border-color-light, #ebeef5);
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

  .page-header .header-actions {
    width: 100%;
  }

  .search-area {
    flex-wrap: wrap;
    width: 100%;
  }

  .search-input {
    width: 100%;
    min-width: 0;
  }

  .help-categories {
    flex-direction: column;
  }

  .video-grid {
    grid-template-columns: 1fr;
  }

  .help-detail-actions {
    flex-wrap: wrap;
  }
}
</style>
