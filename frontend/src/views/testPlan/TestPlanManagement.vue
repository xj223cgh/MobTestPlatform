<template>
  <div class="test-plan-management">
    <div class="header-section">
      <h1>测试计划管理</h1>
      <div class="header-actions">
        <el-select v-model="currentProjectId" placeholder="选择项目" clearable @change="loadTestPlans">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.project_name"
            :value="project.id"
          />
        </el-select>
        <el-select v-model="currentIterationId" placeholder="选择迭代(可选)" clearable @change="loadTestPlans">
          <el-option
            v-for="iteration in iterations"
            :key="iteration.id"
            :label="iteration.iteration_name"
            :value="iteration.id"
          />
        </el-select>
        <el-button type="primary" @click="openCreatePlanDialog">创建测试计划</el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-filter-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索测试计划名称"
        prefix-icon="el-icon-search"
        clearable
        @input="handleSearch"
      />
      <el-select
        v-model="filterStatus"
        placeholder="按状态筛选"
        clearable
        @change="handleSearch"
      >
        <el-option label="草稿" value="draft" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleSearch"
      />
    </div>

    <!-- 测试计划列表 -->
    <div class="plan-list-section">
      <el-table
        :data="testPlansData"
        style="width: 100%"
        @row-click="viewPlanDetail"
        row-key="id"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="plan_name" label="测试计划名称" min-width="200">
          <template #default="scope">
            <div class="plan-name-container">
              <span class="plan-name">{{ scope.row.plan_name }}</span>
              <el-tag :type="getStatusType(scope.row.status)" class="status-tag">
                {{ scope.row.status }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="150" />
        <el-table-column prop="iteration_name" label="所属迭代" width="150" />
        <el-table-column prop="created_by_name" label="创建者" width="120" />
        <el-table-column prop="start_date" label="开始日期" width="150">
          <template #default="scope">
            {{ formatDate(scope.row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_date" label="结束日期" width="150">
          <template #default="scope">
            {{ formatDate(scope.row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="case_count" label="关联用例数" width="120" />
        <el-table-column prop="task_count" label="任务数" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click.stop="editTestPlan(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click.stop="addTestCasesToPlan(scope.row)">添加用例</el-button>
            <el-button size="small" type="danger" @click.stop="deleteTestPlan(scope.row)" :disabled="scope.row.status !== 'draft'"></el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 创建/编辑测试计划对话框 -->
    <el-dialog v-model="planDialogVisible" :title="isEdit ? '编辑测试计划' : '创建测试计划'" width="700px">
      <el-form
        ref="planFormRef"
        :model="planForm"
        :rules="planRules"
        label-width="100px"
      >
        <el-form-item label="测试计划名称" prop="plan_name">
          <el-input v-model="planForm.plan_name" placeholder="请输入测试计划名称" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="planForm.project_id" placeholder="请选择所属项目" disabled v-if="isEdit">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
          <el-select v-model="planForm.project_id" placeholder="请选择所属项目" v-else>
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属迭代">
          <el-select v-model="planForm.iteration_id" placeholder="请选择所属迭代(可选)">
            <el-option
              v-for="iteration in projectIterations"
              :key="iteration.id"
              :label="iteration.iteration_name"
              :value="iteration.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试范围" prop="scope">
          <el-input
            v-model="planForm.scope"
            type="textarea"
            rows="3"
            placeholder="请输入测试范围"
          />
        </el-form-item>
        <el-form-item label="测试环境" prop="test_environment">
          <el-input
            v-model="planForm.test_environment"
            type="textarea"
            rows="2"
            placeholder="请输入测试环境"
          />
        </el-form-item>
        <el-form-item label="风险评估">
          <el-input
            v-model="planForm.risk"
            type="textarea"
            rows="2"
            placeholder="请输入风险评估"
          />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="planForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="planForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-select v-model="planForm.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closePlanDialog">取消</el-button>
          <el-button type="primary" @click="submitPlanForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 测试计划详情对话框 -->
    <el-dialog v-model="planDetailVisible" title="测试计划详情" width="900px">
      <div class="plan-detail-container">
        <div class="detail-header">
          <h2>{{ selectedPlan.plan_name }}</h2>
          <el-tag :type="getStatusType(selectedPlan.status)">{{ selectedPlan.status }}</el-tag>
        </div>
        
        <div class="detail-content">
          <div class="detail-section">
            <h3>基本信息</h3>
            <el-descriptions :column="{ xs: 1, sm: 2, md: 2, lg: 2, xl: 2 }">
              <el-descriptions-item label="所属项目">{{ selectedPlan.project_name }}</el-descriptions-item>
              <el-descriptions-item label="所属迭代">{{ selectedPlan.iteration_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="创建者">{{ selectedPlan.created_by_name }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDateTime(selectedPlan.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="开始日期">{{ formatDate(selectedPlan.start_date) }}</el-descriptions-item>
              <el-descriptions-item label="结束日期">{{ formatDate(selectedPlan.end_date) }}</el-descriptions-item>
              <el-descriptions-item label="关联用例数" :span="2">{{ selectedPlan.case_count }}</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div class="detail-section">
            <h3>测试范围</h3>
            <div class="detail-text">{{ selectedPlan.scope || '-' }}</div>
          </div>
          
          <div class="detail-section">
            <h3>测试环境</h3>
            <div class="detail-text">{{ selectedPlan.test_environment || '-' }}</div>
          </div>
          
          <div class="detail-section">
            <h3>风险评估</h3>
            <div class="detail-text">{{ selectedPlan.risk || '-' }}</div>
          </div>
        </div>
        
        <div class="detail-footer">
          <el-button @click="addTestCasesToPlan(selectedPlan)">添加测试用例</el-button>
          <el-button type="primary" @click="exportTestPlan(selectedPlan)">导出测试计划</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 添加测试用例对话框 -->
    <el-dialog v-model="addCaseDialogVisible" title="添加测试用例" width="800px">
      <div class="add-case-dialog-content">
        <!-- 搜索和筛选 -->
        <div class="search-filter-section">
          <el-input
            v-model="availableCasesSearch"
            placeholder="搜索测试用例名称"
            prefix-icon="el-icon-search"
            clearable
            @input="handleAvailableCasesSearch"
          />
          <el-select
            v-model="availableCasesModule"
            placeholder="按模块筛选"
            clearable
            @change="handleAvailableCasesSearch"
          >
            <el-option
              v-for="module in projectModules"
              :key="module"
              :label="module"
              :value="module"
            />
          </el-select>
          <el-select
            v-model="availableCasesPriority"
            placeholder="按优先级筛选"
            clearable
            @change="handleAvailableCasesSearch"
          >
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </div>
        
        <!-- 可选测试用例列表 -->
        <div class="available-cases-section">
          <h4>可选测试用例 (点击添加)</h4>
          <el-table
            :data="availableCasesData"
            style="width: 100%"
            height="400px"
            @row-click="selectAvailableCase"
            :row-class-name="rowClassName"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="case_name" label="用例名称" min-width="250" />
            <el-table-column prop="module" label="模块" width="150" />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="scope">
                <el-tag :type="getPriorityType(scope.row.priority)">
                  {{ scope.row.priority }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            :current-page="availableCasesPage"
            :page-size="availableCasesPageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="availableCasesTotal"
            @size-change="handleAvailableCasesPageChange"
            @current-change="handleAvailableCasesPageChange"
          />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelAddCases">取消</el-button>
          <el-button type="primary" @click="confirmAddCases">确定添加</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import testPlanApi from '@/api/testPlan';
import projectApi from '@/api/project';
import iterationApi from '@/api/iteration';
import userApi from '@/api/user';

export default {
  name: 'TestPlanManagement',
  setup() {
    // 项目和迭代相关
    const projects = ref([]);
    const iterations = ref([]);
    const currentProjectId = ref('');
    const currentIterationId = ref('');
    const projectIterations = ref([]);
    const projectModules = ref([]);
    
    // 测试计划列表相关
    const testPlansData = ref([]);
    const currentPage = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    const searchKeyword = ref('');
    const filterStatus = ref('');
    const dateRange = ref([]);
    
    // 对话框相关
    const planDialogVisible = ref(false);
    const planDetailVisible = ref(false);
    const addCaseDialogVisible = ref(false);
    const isEdit = ref(false);
    const selectedPlan = ref({});
    
    // 测试计划表单
    const planForm = reactive({
      id: '',
      plan_name: '',
      project_id: '',
      iteration_id: '',
      scope: '',
      test_environment: '',
      risk: '',
      status: 'draft',
      start_date: '',
      end_date: ''
    });
    
    // 表单验证规则
    const planRules = reactive({
      plan_name: [
        { required: true, message: '请输入测试计划名称', trigger: 'blur' },
        { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
      ],
      project_id: [
        { required: true, message: '请选择所属项目', trigger: 'change' }
      ],
      scope: [
        { required: true, message: '请输入测试范围', trigger: 'blur' }
      ],
      test_environment: [
        { required: true, message: '请输入测试环境', trigger: 'blur' }
      ]
    });
    
    // 测试用例选择相关
    const availableCasesSearch = ref('');
    const availableCasesModule = ref('');
    const availableCasesPriority = ref('');
    const availableCasesPage = ref(1);
    const availableCasesPageSize = ref(10);
    const availableCasesData = ref([]);
    const availableCasesTotal = ref(0);
    const selectedCaseIds = ref([]);
    
    // 加载用户可访问的项目列表
    const loadProjects = async () => {
      try {
        const response = await userApi.getUserProjects();
        projects.value = response.data.projects;
        if (projects.value.length > 0 && !currentProjectId.value) {
          currentProjectId.value = projects.value[0].id;
          loadProjectIterations(projects.value[0].id);
          loadTestPlans();
        }
      } catch (error) {
        ElMessage.error('获取项目列表失败');
        console.error('获取项目列表失败:', error);
      }
    };
    
    // 加载项目迭代列表
    const loadProjectIterations = async (projectId) => {
      if (!projectId) {
        projectIterations.value = [];
        return;
      }
      try {
        const response = await iterationApi.getProjectIterations(projectId);
        projectIterations.value = response.data.iterations;
      } catch (error) {
        console.error('获取项目迭代列表失败:', error);
      }
    };
    
    // 加载测试计划列表
    const loadTestPlans = async () => {
      try {
        let response;
        if (currentIterationId.value) {
          // 按迭代获取测试计划
          response = await testPlanApi.getIterationTestPlans(currentIterationId.value);
        } else if (currentProjectId.value) {
          // 按项目获取测试计划
          response = await testPlanApi.getProjectTestPlans(currentProjectId.value);
        } else {
          return;
        }
        
        let plans = response.data.test_plans || [];
        
        // 应用搜索和筛选
        if (searchKeyword.value) {
          plans = plans.filter(plan => plan.plan_name.toLowerCase().includes(searchKeyword.value.toLowerCase()));
        }
        
        if (filterStatus.value) {
          plans = plans.filter(plan => plan.status === filterStatus.value);
        }
        
        if (dateRange.value && dateRange.value.length === 2) {
          plans = plans.filter(plan => {
            const planStartDate = plan.start_date ? new Date(plan.start_date) : null;
            return planStartDate >= dateRange.value[0] && planStartDate <= dateRange.value[1];
          });
        }
        
        // 分页处理
        total.value = plans.length;
        testPlansData.value = plans.slice(
          (currentPage.value - 1) * pageSize.value,
          currentPage.value * pageSize.value
        );
      } catch (error) {
        ElMessage.error('获取测试计划列表失败');
        console.error('获取测试计划列表失败:', error);
      }
    };
    
    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1;
      loadTestPlans();
    };
    
    // 分页处理
    const handleSizeChange = (newSize) => {
      pageSize.value = newSize;
      currentPage.value = 1;
      loadTestPlans();
    };
    
    const handleCurrentChange = (newCurrent) => {
      currentPage.value = newCurrent;
      loadTestPlans();
    };
    
    // 打开创建测试计划对话框
    const openCreatePlanDialog = () => {
      if (!currentProjectId.value) {
        ElMessage.warning('请先选择项目');
        return;
      }
      
      isEdit.value = false;
      Object.assign(planForm, {
        id: '',
        plan_name: '',
        project_id: currentProjectId.value,
        iteration_id: currentIterationId.value || '',
        scope: '',
        test_environment: '',
        risk: '',
        status: 'draft',
        start_date: '',
        end_date: ''
      });
      
      loadProjectIterations(currentProjectId.value);
      planDialogVisible.value = true;
    };
    
    // 编辑测试计划
    const editTestPlan = async (plan) => {
      isEdit.value = true;
      Object.assign(planForm, {
        id: plan.id,
        plan_name: plan.plan_name,
        project_id: plan.project_id,
        iteration_id: plan.iteration_id || '',
        scope: plan.scope || '',
        test_environment: plan.test_environment || '',
        risk: plan.risk || '',
        status: plan.status,
        start_date: plan.start_date ? new Date(plan.start_date) : '',
        end_date: plan.end_date ? new Date(plan.end_date) : ''
      });
      
      loadProjectIterations(plan.project_id);
      planDialogVisible.value = true;
    };
    
    // 关闭测试计划对话框
    const closePlanDialog = () => {
      planDialogVisible.value = false;
    };
    
    // 提交测试计划表单
    const submitPlanForm = async () => {
      try {
        if (isEdit.value) {
          await testPlanApi.updateTestPlan(planForm.id, planForm);
          ElMessage.success('测试计划更新成功');
        } else {
          await testPlanApi.createTestPlan(planForm);
          ElMessage.success('测试计划创建成功');
        }
        
        planDialogVisible.value = false;
        loadTestPlans();
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新测试计划失败' : '创建测试计划失败');
        console.error(isEdit.value ? '更新测试计划失败:' : '创建测试计划失败:', error);
      }
    };
    
    // 查看测试计划详情
    const viewPlanDetail = async (plan) => {
      try {
        const response = await testPlanApi.getTestPlanDetail(plan.id);
        selectedPlan.value = response.data.test_plan;
        planDetailVisible.value = true;
      } catch (error) {
        ElMessage.error('获取测试计划详情失败');
        console.error('获取测试计划详情失败:', error);
      }
    };
    
    // 删除测试计划
    const deleteTestPlan = async (plan) => {
      if (plan.status !== 'draft') {
        ElMessage.warning('只有草稿状态的测试计划可以删除');
        return;
      }
      
      try {
        await ElMessageBox.confirm(
          `确定要删除测试计划「${plan.plan_name}」吗？`,
          '删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );
        
        await testPlanApi.deleteTestPlan(plan.id);
        ElMessage.success('测试计划删除成功');
        loadTestPlans();
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除测试计划失败');
          console.error('删除测试计划失败:', error);
        }
      }
    };
    
    // 添加测试用例到测试计划
    const addTestCasesToPlan = (plan) => {
      selectedPlan.value = plan;
      addCaseDialogVisible.value = true;
      selectedCaseIds.value = [];
      availableCasesPage.value = 1;
      getAvailableTestCases();
      getProjectModules();
    };
    
    // 获取可用的测试用例
    const getAvailableTestCases = async () => {
      try {
        const params = {
          project_id: selectedPlan.value.project_id,
          plan_id: selectedPlan.value.id,
          search: availableCasesSearch.value,
          module: availableCasesModule.value,
          priority: availableCasesPriority.value,
          page: availableCasesPage.value,
          page_size: availableCasesPageSize.value
        };
        const response = await testPlanApi.getAvailableTestCases(selectedPlan.value.id, params);
        availableCasesData.value = response.data.items || [];
        availableCasesTotal.value = response.data.total || 0;
      } catch (error) {
        ElMessage.error('获取可用测试用例失败');
        console.error('获取可用测试用例失败:', error);
      }
    };
    
    // 获取项目模块列表
    const getProjectModules = async () => {
      try {
        const response = await projectApi.getProjectModules({ project_id: selectedPlan.value.project_id });
        projectModules.value = response.data.modules || [];
      } catch (error) {
        console.error('获取项目模块失败:', error);
      }
    };
    
    // 处理可用测试用例搜索
    const handleAvailableCasesSearch = () => {
      availableCasesPage.value = 1;
      getAvailableTestCases();
    };
    
    // 处理分页变化
    const handleAvailableCasesPageChange = () => {
      getAvailableTestCases();
    };
    
    // 选择可用的测试用例
    const selectAvailableCase = (row) => {
      const index = selectedCaseIds.value.indexOf(row.id);
      if (index > -1) {
        selectedCaseIds.value.splice(index, 1);
      } else {
        selectedCaseIds.value.push(row.id);
      }
    };
    
    // 行样式处理
    const rowClassName = ({ row }) => {
      return selectedCaseIds.value.includes(row.id) ? 'selected-row' : '';
    };
    
    // 取消添加测试用例
    const cancelAddCases = () => {
      addCaseDialogVisible.value = false;
      selectedCaseIds.value = [];
    };
    
    // 确认添加测试用例
    const confirmAddCases = async () => {
      if (selectedCaseIds.value.length === 0) {
        ElMessage.warning('请至少选择一个测试用例');
        return;
      }
      
      try {
        await testPlanApi.addTestCasesToPlan(selectedPlan.value.id, {
          test_case_ids: selectedCaseIds.value
        });
        ElMessage.success('添加测试用例成功');
        addCaseDialogVisible.value = false;
        selectedCaseIds.value = [];
        // 重新加载测试计划详情
        viewPlanDetail(selectedPlan.value);
      } catch (error) {
        ElMessage.error('添加测试用例失败');
        console.error('添加测试用例失败:', error);
      }
    };
    
    // 导出测试计划
    const exportTestPlan = async (plan) => {
      try {
        const response = await testPlanApi.exportTestPlan(plan.id, 'excel');
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const link = document.createElement('a');
        const url = window.URL.createObjectURL(blob);
        link.href = url;
        link.setAttribute('download', `${plan.plan_name}_测试计划.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        ElMessage.error('导出测试计划失败');
        console.error('导出测试计划失败:', error);
      }
    };
    
    // 获取状态标签类型
    const getStatusType = (status) => {
      const typeMap = {
        'draft': 'info',
        'active': 'primary',
        'completed': 'success',
        'cancelled': 'danger'
      };
      return typeMap[status] || 'default';
    };
    
    // 获取优先级标签类型
    const getPriorityType = (priority) => {
      const typeMap = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
      };
      return typeMap[priority] || 'primary';
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    };
    
    // 格式化日期时间
    const formatDateTime = (dateString) => {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
    };
    
    // 监听项目变化
    const handleProjectChange = () => {
      currentIterationId.value = '';
      loadProjectIterations(currentProjectId.value);
      loadTestPlans();
    };
    
    // 初始化
    onMounted(() => {
      loadProjects();
    });
    
    return {
      // 项目和迭代相关
      projects,
      iterations,
      currentProjectId,
      currentIterationId,
      projectIterations,
      projectModules,
      handleProjectChange,
      
      // 测试计划列表相关
      testPlansData,
      currentPage,
      pageSize,
      total,
      searchKeyword,
      filterStatus,
      dateRange,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      
      // 对话框相关
      planDialogVisible,
      planDetailVisible,
      addCaseDialogVisible,
      isEdit,
      selectedPlan,
      planForm,
      planRules,
      
      // 测试计划操作方法
      openCreatePlanDialog,
      editTestPlan,
      closePlanDialog,
      submitPlanForm,
      viewPlanDetail,
      deleteTestPlan,
      
      // 测试用例选择相关
      availableCasesSearch,
      availableCasesModule,
      availableCasesPriority,
      availableCasesPage,
      availableCasesPageSize,
      availableCasesData,
      availableCasesTotal,
      selectedCaseIds,
      addTestCasesToPlan,
      getAvailableTestCases,
      getProjectModules,
      handleAvailableCasesSearch,
      handleAvailableCasesPageChange,
      selectAvailableCase,
      rowClassName,
      cancelAddCases,
      confirmAddCases,
      exportTestPlan,
      
      // 辅助方法
      getStatusType,
      getPriorityType,
      formatDate,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.test-plan-management {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-filter-section .el-input {
  width: 250px;
}

.search-filter-section .el-select {
  width: 150px;
}

.search-filter-section .el-date-editor {
  width: 240px;
}

.plan-list-section {
  margin-bottom: 20px;
}

.plan-name-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-tag {
  margin-left: auto;
}

.pagination-section {
  margin-top: 20px;
  text-align: right;
}

/* 测试计划详情样式 */
.plan-detail-container {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h3 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #606266;
}

.detail-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

.detail-footer {
  margin-top: 30px;
  text-align: right;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

/* 测试用例对话框样式 */
.add-case-dialog-content {
  padding: 10px 0;
}

.available-cases-section {
  margin-bottom: 15px;
}

.available-cases-section h4 {
  margin-bottom: 10px;
  font-weight: 500;
  color: #606266;
}

.selected-row {
  background-color: #f5f7fa;
}

.dialog-footer {
  text-align: right;
}
</style>