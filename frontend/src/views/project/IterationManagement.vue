<template>
  <div class="iteration-management">
    <div class="management-header">
      <div class="header-actions">
        <el-select
          v-model="selectedProjectId"
          placeholder="选择项目名称"
          filterable
          clearable
          style="width: 200px; margin-right: 15px"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.project_name || `项目 ${project.id}`"
            :value="project.id"
          />
        </el-select>
        <el-button
          type="primary"
          @click="showCreateIterationDialog"
        >
          <i class="el-icon-plus" /> 创建迭代
        </el-button>
      </div>
    </div>

    <!-- 迭代卡片列表 -->
    <div
      v-loading="pageLoading"
      class="iteration-timeline-container"
      element-loading-text="加载中..."
    >
      <div
        v-for="(iteration, index) in iterationsData"
        :key="iteration.id"
        class="iteration-timeline-item"
      >
        <!-- 左侧时间线 -->
        <div class="timeline-line">
          <div class="timeline-date">
            {{ formatDate(iteration.start_date) }}
          </div>
          <div
            class="timeline-dot"
            :class="`status-${iteration.status}`"
          />
          <div
            class="timeline-vertical-line"
            :class="{ last: index === iterationsData.length - 1 }"
          />
        </div>

        <!-- 右侧迭代卡片 -->
        <div
          class="iteration-card"
          :class="`status-${iteration.status}`"
        >
          <!-- 卡片头部 - 左侧区域 -->
          <div class="card-section card-main">
            <div class="card-title-section">
              <h3 class="iteration-title">
                {{ iteration.iteration_name }}
              </h3>
              <el-tag :type="getTagTypeByStatus(iteration.status)">
                {{ getStatusText(iteration.status) }}
              </el-tag>
            </div>
            <div class="iteration-goal">
              <i class="el-icon-data-line" />
              <div class="goal-content">
                <div class="goal-label">
                  迭代目标:
                </div>
                <div class="goal-value">
                  {{ iteration.goal || "无迭代目标" }}
                </div>
              </div>
            </div>
            <div class="iteration-description">
              <i class="el-icon-document" />
              <div class="desc-content">
                <div class="desc-label">
                  迭代描述:
                </div>
                <div class="desc-value">
                  {{ iteration.description || "无迭代描述" }}
                </div>
              </div>
            </div>
          </div>

          <!-- 卡片中部 - 中间区域 -->
          <div class="card-section card-meta">
            <div class="meta-item">
              <i class="el-icon-calendar" />
              <div class="meta-content">
                <div class="meta-label">
                  时间范围
                </div>
                <div class="meta-value">
                  {{ formatDateTime(iteration.start_date) }} -
                  {{ formatDateTime(iteration.end_date) }}
                </div>
              </div>
            </div>
            <div class="meta-item">
              <i class="el-icon-office-building" />
              <div class="meta-content">
                <div class="meta-label">
                  所属项目
                </div>
                <div class="meta-value">
                  {{ iteration.project_name }}
                </div>
              </div>
            </div>
            <div class="meta-item">
              <i class="el-icon-success" />
              <div class="meta-content">
                <div class="meta-label">
                  需求进度
                </div>
                <div class="meta-value">
                  <el-progress
                    :percentage="
                      calculateRequirementProgress(iteration.requirement_stats)
                    "
                    :stroke-width="8"
                    :show-text="false"
                    :color="getProgressColor(iteration.status)"
                    class="progress-bar"
                  />
                  <span class="progress-text">{{
                    calculateRequirementProgress(iteration.requirement_stats)
                  }}%</span>
                </div>
              </div>
            </div>
            <div class="meta-item">
              <i class="el-icon-user" />
              <div class="meta-content">
                <div class="meta-label">
                  创建人
                </div>
                <div class="meta-value">
                  {{ iteration.created_by_name || "未知" }}
                </div>
              </div>
            </div>
          </div>

          <!-- 卡片尾部 - 右侧区域 -->
          <div class="card-section card-actions">
            <el-button
              type="primary"
              size="small"
              @click="showIterationDetail(iteration)"
            >
              <i class="el-icon-view" />
              详情
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="editIteration(iteration)"
            >
              <i class="el-icon-edit" />
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteIteration(iteration)"
            >
              <i class="el-icon-delete" />
              删除
            </el-button>
          </div>
        </div>
      </div>
      <div
        v-if="iterationsData.length === 0"
        class="empty-state"
      >
        <el-empty description="暂无迭代数据" />
      </div>
    </div>

    <!-- 创建/编辑迭代对话框 -->
    <el-dialog
      v-model="iterationDialogVisible"
      :title="iterationDialogTitle"
      width="500px"
      @close="resetIterationForm"
    >
      <el-form
        ref="iterationForm"
        :model="iterationForm"
        :rules="iterationRules"
        label-width="100px"
      >
        <el-form-item
          label="迭代名称"
          prop="iteration_name"
          required
        >
          <el-input
            v-model="iterationForm.iteration_name"
            placeholder="请输入迭代名称"
          />
        </el-form-item>
        <el-form-item
          label="迭代目标"
          prop="goal"
          required
        >
          <el-input
            v-model="iterationForm.goal"
            type="textarea"
            placeholder="请输入迭代目标"
            :rows="2"
          />
        </el-form-item>
        <el-form-item
          label="测试版本"
          prop="version"
          required
        >
          <el-input
            v-model="iterationForm.version"
            placeholder="请输入测试版本"
          />
        </el-form-item>
        <el-form-item
          label="开始日期"
          prop="start_date"
          required
        >
          <el-date-picker
            v-model="iterationForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="结束日期"
          prop="end_date"
          required
        >
          <el-date-picker
            v-model="iterationForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="状态"
          prop="status"
          required
        >
          <el-select
            v-model="iterationForm.status"
            placeholder="选择状态"
          >
            <el-option
              label="待开始"
              value="planning"
            />
            <el-option
              label="进行中"
              value="active"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="已取消"
              value="cancelled"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="备注"
          prop="description"
        >
          <el-input
            v-model="iterationForm.description"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeIterationDialog">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="submitIterationForm"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {
  getProjectIterations,
  createIteration,
  updateIteration,
  deleteIteration as deleteIterationApi,
} from "@/api/iteration";
import { getProjects } from "@/api/project";
import { ElLoading, ElMessage, ElMessageBox } from "element-plus";

export default {
  name: "IterationManagement",
  data() {
    return {
      // 项目相关
      projects: [],
      selectedProjectId: null,

      // 迭代列表数据
      iterations: [],
      iterationsData: [],

      // 页面初始加载状态，避免进入页面时数据延迟出现
      pageLoading: true,

      // 创建/编辑迭代表单
      iterationDialogVisible: false,
      iterationDialogTitle: "创建迭代",
      iterationForm: {
        id: null,
        project_id: null,
        iteration_name: "",
        goal: "",
        version: "",
        start_date: "",
        end_date: "",
        status: "planning",
        description: "",
      },
      iterationRules: {
        project_id: [
          { required: true, message: "请选择项目", trigger: "blur" },
        ],
        iteration_name: [
          { required: true, message: "请输入迭代名称", trigger: "blur" },
          {
            min: 2,
            max: 50,
            message: "迭代名称长度在 2 到 50 个字符",
            trigger: "blur",
          },
        ],
        goal: [
          { required: true, message: "请输入迭代目标", trigger: "blur" },
          {
            min: 5,
            max: 200,
            message: "迭代目标长度在 5 到 200 个字符",
            trigger: "blur",
          },
        ],
        version: [
          { required: true, message: "请输入测试版本", trigger: "blur" },
          {
            min: 1,
            max: 30,
            message: "测试版本长度在 1 到 30 个字符",
            trigger: "blur",
          },
        ],
        start_date: [
          { required: true, message: "请选择开始日期", trigger: "change" },
        ],
        end_date: [
          { required: true, message: "请选择结束日期", trigger: "change" },
          {
            validator: (rule, value, callback) => {
              if (
                this.iterationForm.start_date &&
                value < this.iterationForm.start_date
              ) {
                callback(new Error("结束日期不能早于开始日期"));
              } else {
                callback();
              }
            },
            trigger: "change",
          },
        ],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  mounted() {
    this.initProjects();
  },
  methods: {
    // 初始化项目列表
    async initProjects() {
      try {
        const response = await getProjects();
        this.projects = response.data?.items || [];
        if (this.projects.length > 0) {
          this.selectedProjectId = this.projects[0].id;
          await this.loadIterations();
        } else {
          this.pageLoading = false;
        }
      } catch (error) {
        console.error("获取项目列表失败:", error);
        this.pageLoading = false;
        ElMessage.error(
          "获取项目列表失败: " + (error?.message || "未知错误"),
        );
      }
    },

    // 加载迭代列表
    async loadIterations() {
      if (!this.selectedProjectId) {
        this.pageLoading = false;
        return;
      }

      try {
        const response = await getProjectIterations(this.selectedProjectId);
        if (response && response.code === 200 && response.data) {
          this.iterations = response.data?.items || [];
          this.iterationsData = [...this.iterations].sort((a, b) => {
            return new Date(a.start_date) - new Date(b.start_date);
          });
        } else {
          this.iterations = [];
          this.iterationsData = [];
        }
      } catch (error) {
        console.error("获取迭代列表失败:", error);
        ElMessage.error(
          "获取迭代列表失败: " + (error?.message || "未知错误"),
        );
        this.iterations = [];
        this.iterationsData = [];
      } finally {
        this.pageLoading = false;
      }
    },

    // 处理项目变更
    handleProjectChange() {
      this.pageLoading = true;
      this.loadIterations();
    },

    // 显示创建迭代对话框
    showCreateIterationDialog() {
      this.iterationDialogTitle = "创建迭代";
      this.resetIterationForm();
      this.iterationForm.project_id = this.selectedProjectId;
      this.iterationDialogVisible = true;
    },

    // 重置迭代表单
    resetIterationForm() {
      this.iterationForm = {
        id: null,
        project_id: this.selectedProjectId,
        iteration_name: "",
        goal: "",
        version: "",
        start_date: "",
        end_date: "",
        status: "planning",
        description: "",
      };
      if (this.$refs.iterationForm) {
        this.$refs.iterationForm.resetFields();
      }
    },

    // 关闭迭代对话框
    closeIterationDialog() {
      this.iterationDialogVisible = false;
      this.resetIterationForm();
    },

    // 将日期格式化为 YYYY-MM-DD，后端只接受该格式
    formatDateForApi(value) {
      if (!value) return "";
      if (typeof value === "string") {
        return value.slice(0, 10);
      }
      if (value instanceof Date) {
        return value.toISOString().slice(0, 10);
      }
      return "";
    },

    // 提交迭代表单
    async submitIterationForm() {
      if (!this.$refs.iterationForm) return;

      try {
        await this.$refs.iterationForm.validate();

        const iterationData = {
          project_id: this.iterationForm.project_id,
          iteration_name: this.iterationForm.iteration_name,
          goal: this.iterationForm.goal,
          version: this.iterationForm.version,
          start_date: this.formatDateForApi(this.iterationForm.start_date),
          end_date: this.formatDateForApi(this.iterationForm.end_date),
          status: this.iterationForm.status,
          description: this.iterationForm.description ?? "",
        };

        if (this.iterationForm.id) {
          // 更新迭代
          await updateIteration(this.iterationForm.id, iterationData);
          ElMessage.success("迭代更新成功");
        } else {
          // 创建迭代
          await createIteration(iterationData);
          ElMessage.success("迭代创建成功");
        }

        this.closeIterationDialog();
        this.loadIterations();
      } catch (error) {
        console.error("提交迭代表单失败:", error);
        ElMessage.error("操作失败: " + (error?.message || "未知错误"));
      }
    },

    // 编辑迭代
    editIteration(iteration) {
      this.iterationDialogTitle = "编辑迭代";
      this.iterationForm = {
        ...iteration,
        start_date: iteration.start_date ? iteration.start_date : "",
        end_date: iteration.end_date ? iteration.end_date : "",
        version: iteration.version || "",
        description: iteration.description || "",
      };
      this.iterationDialogVisible = true;
    },

    // 删除迭代
    async deleteIteration(iteration) {
      try {
        await ElMessageBox.confirm("确定要删除这个迭代吗？", "警告", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        });

        await deleteIterationApi(iteration.id);
        ElMessage.success("迭代删除成功");
        this.loadIterations();
      } catch (error) {
        if (error !== "cancel") {
          console.error("删除迭代失败:", error);
          ElMessage.error("删除失败: " + (error?.message || "未知错误"));
        }
      }
    },

    // 显示迭代详情
    showIterationDetail(iteration) {
      console.log("点击了详情按钮，跳转到迭代详情页面:", iteration.id);
      this.$router.push(`/iterations/${iteration.id}`);
    },

    // 根据状态获取标签类型
    getTagTypeByStatus(status) {
      const statusMap = {
        planning: "info",
        active: "primary",
        completed: "success",
        cancelled: "danger",
      };
      return statusMap[status] || "info";
    },

    // 根据状态获取文本
    getStatusText(status) {
      const statusMap = {
        planning: "待开始",
        active: "进行中",
        completed: "已完成",
        cancelled: "已取消",
      };
      return statusMap[status] || status;
    },

    // 根据状态获取进度条颜色
    getProgressColor(status) {
      const colorMap = {
        planning: "#909399",
        active: "#409eff",
        completed: "#67c23a",
        cancelled: "#f56c6c",
      };
      return colorMap[status] || "#409eff";
    },

    // 格式化完整时间，将ISO格式中的T替换为空格
    formatDateTime(dateTime) {
      if (!dateTime) return "";
      return dateTime.replace("T", " ");
    },

    // 格式化日期，只显示年月日
    formatDate(dateTime) {
      if (!dateTime) return "";
      // 提取年月日部分
      const dateStr = dateTime.split("T")[0];
      return dateStr;
    },

    // 计算需求进度百分比
    calculateRequirementProgress(requirementStats) {
      if (!requirementStats || !requirementStats.total) return 0;

      const total = requirementStats.total;
      const completed = requirementStats.completed || 0;
      const progress = Math.round((completed / total) * 100);

      return Math.min(progress, 100);
    },
  },
};
</script>

<style scoped>
.iteration-management {
  padding: 20px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.management-header h2 {
  margin: 0;
  font-size: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.iteration-timeline-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-left: 20px;
}

.iteration-timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

/* 时间线样式 */
.timeline-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  position: relative;
}

.timeline-date {
  font-size: 17px;
  color: #606266;
  font-weight: 600;
  white-space: nowrap;
  margin-bottom: 4px;
  text-align: center;
}

.timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid #e4e7ed;
  background: #fff;
  z-index: 1;
  transition: all 0.3s ease;
}

.timeline-dot.status-planning {
  background: #909399;
  border-color: #dcdfe6;
}

.timeline-dot.status-active {
  background: #409eff;
  border-color: #c6e2ff;
}

.timeline-dot.status-completed {
  background: #67c23a;
  border-color: #e1f3d8;
}

.timeline-dot.status-cancelled {
  background: #f56c6c;
  border-color: #fbc4c4;
}

.timeline-vertical-line {
  width: 2px;
  background: #e4e7ed;
  flex: 1;
  min-height: 40px;
  margin-top: 4px;
}

.timeline-vertical-line.last {
  display: none;
}

.iteration-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  overflow: hidden;
  min-height: 120px;
  flex: 1;
}

.iteration-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.iteration-card.status-planning {
  border-left: 4px solid #909399;
}

.iteration-card.status-active {
  border-left: 4px solid #409eff;
}

.iteration-card.status-completed {
  border-left: 4px solid #67c23a;
}

.iteration-card.status-cancelled {
  border-left: 4px solid #f56c6c;
}

/* 卡片三区域布局 */
.card-section {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 12px;
}

/* 左侧主信息区 - 35%宽度 */
.card-main {
  flex: 1 1 35%;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  border-right: 1px solid #f0f0f0;
  gap: 10px;
}

.card-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  flex-wrap: wrap;
}

.iteration-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 120px;
}

/* 迭代目标样式 */
.iteration-goal {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  font-size: 14px;
}

.iteration-goal i {
  margin-top: 2px;
  color: #909399;
  font-size: 16px;
  flex-shrink: 0;
}

.goal-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.goal-label {
  color: #909399;
  font-weight: 500;
  font-size: 12px;
}

.goal-value {
  color: #606266;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

/* 迭代描述样式 */
.iteration-description {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  font-size: 14px;
}

.iteration-description i {
  margin-top: 2px;
  color: #909399;
  font-size: 16px;
  flex-shrink: 0;
}

.desc-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.desc-label {
  color: #909399;
  font-weight: 500;
  font-size: 12px;
}

.desc-value {
  color: #606266;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

/* 中间元数据区 - 40%宽度 */
.card-meta {
  flex: 1 1 40%;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  border-right: 1px solid #f0f0f0;
  padding-right: 8px;
}

.card-meta .meta-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  margin: 0;
}

.card-meta .meta-item i {
  font-size: 16px;
  color: #409eff;
  margin-top: 2px;
  flex-shrink: 0;
}

.meta-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.meta-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 500;
}

.meta-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 进度条样式 */
.progress-bar {
  flex: 1;
  margin: 0;
  min-width: 80px;
}

.progress-text {
  font-size: 13px;
  color: #606266;
  font-weight: 600;
  min-width: 35px;
  text-align: right;
}

/* 右侧操作区 - 25%宽度 */
.card-actions {
  flex: 1 1 25%;
  justify-content: flex-end;
  gap: 8px;
  padding-right: 16px;
  flex-direction: column;
  align-items: flex-end;
}

.card-actions .el-button {
  font-size: 14px;
  padding: 8px 20px;
  height: auto;
  font-weight: 500;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
  border: 1px dashed #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .card-section {
    padding: 16px;
  }

  .iteration-card {
    min-height: 100px;
  }

  .card-actions .el-button {
    padding: 4px 12px;
    font-size: 12px;
  }
}

@media (max-width: 992px) {
  .iteration-card {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .card-section {
    width: auto;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    justify-content: center;
  }

  .card-main {
    border-right: none;
    align-items: center;
  }

  .card-title-section {
    justify-content: center;
  }

  .card-meta {
    border-right: none;
    align-items: center;
    gap: 12px;
  }

  .card-actions {
    justify-content: center;
  }

  .card-section:last-child {
    border-bottom: none;
  }
}

@media (max-width: 576px) {
  .iteration-management {
    padding: 10px;
  }

  .management-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }

  .card-section {
    padding: 12px;
  }

  .card-actions {
    gap: 8px;
  }
}
</style>
