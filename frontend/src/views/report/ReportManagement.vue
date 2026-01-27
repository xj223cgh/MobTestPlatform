<template>
  <div class="report-management">
    <div class="page-header">
      <h2>报告管理</h2>
    </div>

    <!-- 报告列表区域 -->
    <div class="report-content">
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :model="filterForm" inline>
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
          <el-form-item label="任务类型">
            <el-select
              v-model="filterForm.taskType"
              placeholder="全部类型"
              clearable
              style="width: 150px"
              @change="handleFilter"
            >
              <el-option label="测试用例任务" value="test_case" />
              <el-option label="设备脚本任务" value="device_script" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filterForm.status"
              placeholder="全部状态"
              clearable
              style="width: 150px"
              @change="handleFilter"
            >
              <el-option label="已完成" value="completed" />
              <el-option label="执行中" value="executing" />
              <el-option label="待执行" value="pending" />
              <el-option label="已终止" value="terminated" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">
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

      <!-- 报告列表 -->
      <div class="table-section">
        <el-table
          v-loading="loading"
          :data="reportList"
          stripe
          border
          style="width: 100%"
          fit
        >
          <el-table-column prop="task_name" label="任务名称" min-width="180">
            <template #default="{ row }">
              <span>{{ row.task_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="task_type" label="任务类型" min-width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.task_type === 'test_case' ? 'primary' : 'success'">
                {{ row.task_type === 'test_case' ? '测试用例任务' : '设备脚本任务' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag
                :type="getStatusTagType(row.status)"
              >
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_by" label="创建人" min-width="100" align="center">
            <template #default="{ row }">
              {{ row.created_by || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160" align="center">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="completed_at" label="完成时间" min-width="160" align="center">
            <template #default="{ row }">
              {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="handleViewReport(row)"
              >
                <el-icon><View /></el-icon>
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            :current-page="pagination.page"
            :page-size="pagination.size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
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
          <div class="output-section" v-if="currentOutputDetail?.error_output">
            <h5>错误输出：</h5>
            <pre class="output-pre error">{{ currentOutputDetail?.error_output }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outputDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleCopyOutput">复制输出</el-button>
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
import { getTestTaskList } from '@/api/testTask';
import { getReportData } from '@/api/report';

// 路由相关
const router = useRouter();

// 响应式数据
const loading = ref(false);
const outputDialogVisible = ref(false);
const currentOutputDetail = ref(null);

// 筛选表单
const filterForm = reactive({
  taskName: '',
  taskType: '',
  status: ''
});

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
});

// 报告列表
const reportList = ref([]);

// 获取报告列表（基于任务列表）
const fetchReportList = async () => {
  try {
    loading.value = true;
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: filterForm.taskName,
      task_type: filterForm.taskType,
      status: filterForm.status
    };

    const response = await getTestTaskList(params);
    if (response.success) {
      reportList.value = response.data.test_tasks || [];
      pagination.total = response.data.pagination.total || 0;
    } else {
      ElMessage.error(response.message || '获取报告列表失败');
    }
  } catch (error) {
    ElMessage.error('获取报告列表失败');
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleFilter = () => {
  pagination.page = 1;
  fetchReportList();
};

// 重置
const handleReset = () => {
  Object.assign(filterForm, {
    taskName: '',
    taskType: '',
    status: ''
  });
  pagination.page = 1;
  fetchReportList();
};

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size;
  pagination.page = 1;
  fetchReportList();
};

const handleCurrentChange = (page) => {
  pagination.page = page;
  fetchReportList();
};

// 查看报告
const handleViewReport = (row) => {
  router.push(`/report/${row.id}`);
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
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;

  h2 {
    margin: 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;
  }
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.pagination-container {
  padding: 15px 20px;
  text-align: right;
  background: white;
  border-top: 1px solid #e4e7ed;
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
