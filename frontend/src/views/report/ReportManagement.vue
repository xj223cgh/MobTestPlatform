<template>
  <div class="report-management">
    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-form
        :model="filterForm"
        inline
        class="filter-form"
      >
        <el-form-item label="任务名称">
          <el-input
            v-model="filterForm.taskName"
            placeholder="请输入任务名称"
            clearable
            style="width: 200px"
            @clear="handleFilter"
            @keyup.enter="handleFilter"
          />
        </el-form-item>

        <el-form-item label="任务状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>

        <el-form-item label="创建人">
          <el-input
            v-model="filterForm.creator"
            placeholder="请输入创建人"
            clearable
            style="width: 150px"
            @clear="handleFilter"
            @keyup.enter="handleFilter"
          />
        </el-form-item>

        <el-form-item class="filter-buttons">
          <el-button
            type="primary"
            @click="handleFilter"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 报告类型选项卡 -->
    <div class="report-tabs-section">
      <el-tabs
        v-model="activeTab"
        class="report-tabs"
        @tab-change="handleTabChange"
      >
        <!-- 测试用例报告 -->
        <el-tab-pane
          label="用例执行报告"
          name="test_case"
        >
          <div class="table-section">
            <div class="table-scroll-viewport">
              <el-table
                v-loading="loading.testCase"
                :data="reportList.testCase"
              stripe
              border
              style="width: 100%"
              fit
            >
              <el-table-column
                prop="task_name"
                label="任务名称"
                min-width="180"
                align="center"
              >
                <template #default="{ row }">
                  <span>{{ row.task_name }}</span>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="状态"
                min-width="100"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusTagType(row.status)"
                  >
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="created_by"
                label="创建人"
                min-width="100"
                align="center"
              >
                <template #default="{ row }">
                  {{ row.created_by || '-' }}
                </template>
              </el-table-column>
              <el-table-column
                prop="created_at"
                label="创建时间"
                min-width="160"
                align="center"
              >
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="completed_at"
                label="完成时间"
                min-width="160"
                align="center"
              >
                <template #default="{ row }">
                  {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="150"
                fixed="right"
                align="center"
              >
                <template #default="{ row }">
                  <div class="operation-buttons">
                    <el-button
                      type="primary"
                      size="small"
                      class="op-btn"
                      @click="handleViewReport(row)"
                    >
                      查看
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      class="op-btn"
                      @click="handleDeleteReport(row, 'test_case')"
                    >
                      删除
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- 脚本执行报告 -->
        <el-tab-pane
          label="脚本执行报告"
          name="device_script"
        >
          <div class="table-section">
            <div class="table-scroll-viewport">
              <el-table
                v-loading="loading.deviceScript"
                :data="reportList.deviceScript"
              stripe
              border
              style="width: 100%"
              fit
            >
              <el-table-column
                prop="task_name"
                label="任务名称"
                min-width="180"
                align="center"
              >
                <template #default="{ row }">
                  <span>{{ row.task_name }}</span>
                </template>
              </el-table-column>
              <el-table-column
                prop="script_file"
                label="脚本文件"
                min-width="140"
                align="center"
              >
                <template #default="{ row }">
                  <span>{{ row.script_file || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="状态"
                min-width="100"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusTagType(row.status)"
                  >
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="created_by"
                label="创建人"
                min-width="100"
                align="center"
              >
                <template #default="{ row }">
                  {{ row.created_by || '-' }}
                </template>
              </el-table-column>
              <el-table-column
                prop="created_at"
                label="创建时间"
                min-width="160"
                align="center"
              >
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="completed_at"
                label="完成时间"
                min-width="160"
                align="center"
              >
                <template #default="{ row }">
                  {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="150"
                fixed="right"
                align="center"
              >
                <template #default="{ row }">
                  <div class="operation-buttons">
                    <el-button
                      type="primary"
                      size="small"
                      class="op-btn"
                      @click="handleViewReport(row)"
                    >
                      查看
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      class="op-btn"
                      @click="handleDeleteReport(row, 'device_script')"
                    >
                      删除
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-if="activeTab === 'test_case'"
        :current-page="pagination.testCase.page"
        :page-size="pagination.testCase.size"
        :total="pagination.testCase.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="(size) => handleSizeChange(size, 'testCase')"
        @current-change="(page) => handleCurrentChange(page, 'testCase')"
      />
      <el-pagination
        v-else
        :current-page="pagination.deviceScript.page"
        :page-size="pagination.deviceScript.size"
        :total="pagination.deviceScript.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="(size) => handleSizeChange(size, 'deviceScript')"
        @current-change="(page) => handleCurrentChange(page, 'deviceScript')"
      />
    </div>

    <!-- 执行输出弹窗 -->
    <el-dialog
      v-model="outputDialogVisible"
      :title="`执行输出 - ${currentOutputDetail?.device_name || ''}`"
      width="80%"
    >
      <div class="output-dialog">
        <div class="output-header">
          <div class="info-item">
            <span class="label">设备ID：</span>
            <span class="value">{{ currentOutputDetail?.device_id }}</span>
          </div>
          <div class="info-item">
            <span class="label">设备名称：</span>
            <span class="value">{{ currentOutputDetail?.device_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">退出码：</span>
            <span class="value">{{ currentOutputDetail?.exit_code }}</span>
          </div>
        </div>
        <div class="output-content">
          <div class="output-section">
            <h5>标准输出：</h5>
            <pre class="output-pre">{{ currentOutputDetail?.output || '无输出' }}</pre>
          </div>
          <div
            v-if="currentOutputDetail?.error_output"
            class="output-section"
          >
            <h5>错误输出：</h5>
            <pre class="output-pre error">{{ currentOutputDetail?.error_output }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outputDialogVisible = false">关闭</el-button>
          <el-button
            type="primary"
            @click="handleCopyOutput"
          >复制输出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh, View, Download, Document } from '@element-plus/icons-vue';
import dayjs from 'dayjs';
import { getReportList, getReportData, deleteReport } from '@/api/report';

// 路由相关
const router = useRouter();

// 响应式数据
const activeTab = ref('test_case');
const loading = reactive({
  testCase: false,
  deviceScript: false
});
const outputDialogVisible = ref(false);
const currentOutputDetail = ref(null);

// 筛选表单
const filterForm = reactive({
  taskName: '',
  status: '',
  creator: ''
});

// 分页
const pagination = reactive({
  testCase: {
    page: 1,
    size: 10,
    total: 0
  },
  deviceScript: {
    page: 1,
    size: 10,
    total: 0
  }
});

// 报告列表
const reportList = reactive({
  testCase: [],
  deviceScript: []
});

// 获取报告列表（从 reports 表）
const fetchReportList = async () => {
  // 加载测试用例报告
  loading.testCase = true;
  try {
    const testCaseParams = {
      page: pagination.testCase.page,
      size: pagination.testCase.size,
      report_type: 'test_case',
      search: filterForm.taskName,
      status: filterForm.status,
      creator: filterForm.creator
    };

    const testCaseResponse = await getReportList(testCaseParams);
    if (testCaseResponse.code === 200 || testCaseResponse.success) {
      reportList.testCase = testCaseResponse.data.reports || [];
      pagination.testCase.total = testCaseResponse.data.pagination.total || 0;
    } else {
      ElMessage.error(testCaseResponse.message || '获取测试用例报告列表失败');
    }
  } catch (error) {
    ElMessage.error('获取测试用例报告列表失败');
  } finally {
    loading.testCase = false;
  }

  // 加载设备脚本报告
  loading.deviceScript = true;
  try {
    const deviceScriptParams = {
      page: pagination.deviceScript.page,
      size: pagination.deviceScript.size,
      report_type: 'device_script',
      search: filterForm.taskName,
      status: filterForm.status,
      creator: filterForm.creator
    };

    const deviceScriptResponse = await getReportList(deviceScriptParams);
    if (deviceScriptResponse.code === 200 || deviceScriptResponse.success) {
      reportList.deviceScript = deviceScriptResponse.data.reports || [];
      pagination.deviceScript.total = deviceScriptResponse.data.pagination.total || 0;
    } else {
      ElMessage.error(deviceScriptResponse.message || '获取设备脚本报告列表失败');
    }
  } catch (error) {
    ElMessage.error('获取设备脚本报告列表失败');
  } finally {
    loading.deviceScript = false;
  }
};

// 搜索
const handleFilter = () => {
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  fetchReportList();
};

// 重置
const handleReset = () => {
  Object.assign(filterForm, {
    taskName: '',
    status: '',
    creator: ''
  });
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  fetchReportList();
};

// 分页处理
const handleSizeChange = (size, tab) => {
  pagination[tab].size = size;
  pagination[tab].page = 1;
  fetchReportList();
};

const handleCurrentChange = (page, tab) => {
  pagination[tab].page = page;
  fetchReportList();
};

// 标签页切换
const handleTabChange = () => {
  // 切换标签页时不需要重新加载，因为已经在fetchReportList中加载了所有数据
};

// 查看报告
const handleViewReport = (row) => {
  router.push(`/report/${row.id}`);
};

// 删除报告
const handleDeleteReport = async (row, tab) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告「${row.task_name || row.id}」吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    await deleteReport(row.id);
    ElMessage.success('删除成功');
    fetchReportList();
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err?.message || '删除失败');
    }
  }
};

// 查看设备执行输出
const handleViewOutput = (row) => {
  currentOutputDetail.value = row;
  outputDialogVisible.value = true;
};

// 复制输出
const handleCopyOutput = () => {
  if (!currentOutputDetail.value) return;
  
  const output = `${currentOutputDetail.value.output || ''}\n${currentOutputDetail.value.error_output || ''}`;
  navigator.clipboard.writeText(output)
    .then(() => {
      ElMessage.success('输出已复制到剪贴板');
    })
    .catch(() => {
      ElMessage.error('复制失败');
    });
};

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-';
};

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    'pending': 'info',
    'executing': 'warning',
    'completed': 'success',
    'terminated': 'danger'
  };
  return typeMap[status] || 'info';
};

// 获取状态标签文本
const getStatusLabel = (status) => {
  const labelMap = {
    'pending': '待执行',
    'executing': '执行中',
    'completed': '已完成',
    'terminated': '已终止'
  };
  return labelMap[status] || status;
};

// 页面加载时获取报告列表
onMounted(() => {
  fetchReportList();
});
</script>

<style lang="scss" scoped>
.report-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fa;
}

.filter-section {
  flex-shrink: 0;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  
  .filter-form {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
  
  :deep(.filter-buttons) {
    margin-left: auto;
  }
}

.report-tabs-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 70px;
}

.report-tabs-section :deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.report-tabs-section :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.report-tabs-section :deep(.el-tabs__panel) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.report-tabs-section :deep(.el-tab-pane) {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.report-tabs {
  margin-bottom: 0;

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }

  :deep(.el-tabs__content) {
    padding: 0;
  }
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 16px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 标签页表格不显示横向滚动条，仅垂直滚动；表体区域出现垂直滚动条 */
.table-section .table-scroll-viewport {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

.table-section .table-scroll-viewport :deep(.el-table) {
  min-width: 0 !important;
}

/* 操作列：与需求管理页面一致，紧凑按钮样式 */
.operation-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  padding: 2px 0;
}

.operation-buttons :deep(.el-button.op-btn),
.operation-buttons :deep(.el-button) {
  flex: none;
  min-width: 0;
  padding: 2px 6px;
  font-size: 12px;
  margin: 0;
  white-space: nowrap;
}

.pagination-container {
  position: fixed;
  bottom: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.pagination-container .el-pagination {
  margin: 0;
  text-align: center;
}

/* 输出弹窗样式 */
.output-dialog {
  padding: 10px 0;
}

.output-header {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.output-content {
  max-height: 500px;
  overflow-y: auto;
}

.output-section {
  margin-bottom: 15px;
}

.output-section h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.output-pre {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.output-pre.error {
  background: #fef0f0;
  border-color: #fbc4ab;
  color: #f56c6c;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;

  .label {
    font-weight: 500;
    color: #606266;
    min-width: 80px;
  }

  .value {
    color: #303133;
    word-break: break-word;
  }
}
</style>
