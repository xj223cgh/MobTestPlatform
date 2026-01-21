<template>
  <div class="test-suite-management">
    <div class="page-header">
      <h1>测试套件管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateSuiteDialog">
          <el-icon><Plus /></el-icon>
          新建测试套件
        </el-button>
        <el-button @click="refreshTree">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧树形结构 -->
      <div class="tree-container">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索测试套件"
          prefix-icon="el-icon-search"
          clearable
          class="search-input"
          @input="filterTree"
        />
        <el-tree
          ref="treeRef"
          :data="filteredTreeData"
          :props="defaultProps"
          :expand-on-click-node="false"
          :default-expand-all="true"
          :allow-drop="allowDrop"
          :allow-drag="allowDrag"
          @node-click="handleNodeClick"
          @node-contextmenu="handleContextMenu"
          @node-drop="handleNodeDrop"
        >
          <template #default="{ data }">
            <div class="tree-node-content">
              <span :class="{ 'text-primary': data.id === selectedNodeId }">
                {{ data.name }}
              </span>
              <div class="node-actions">
                <el-icon
                  class="action-icon"
                  @click.stop="showEditSuiteDialog(data)"
                >
                  <Edit />
                </el-icon>
                <el-icon class="action-icon" @click.stop="deleteSuite(data.id)">
                  <Delete />
                </el-icon>
              </div>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-container">
        <div v-if="!selectedNode" class="empty-state">
          <el-icon class="empty-icon">
            <Folder />
          </el-icon>
          <p>请选择或创建一个测试套件</p>
        </div>
        <div v-else class="suite-details">
          <div class="suite-header">
            <h2>{{ selectedNode.name }}</h2>
            <div class="suite-actions">
              <el-button type="primary" @click="createTestCase">
                <el-icon><Plus /></el-icon>
                新建测试用例
              </el-button>
            </div>
          </div>

          <!-- 测试用例表格 -->
          <div class="test-cases-section">
            <h3>测试用例列表</h3>
            <el-table :data="testCasesData" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column
                prop="case_name"
                label="用例名称"
                min-width="200"
              />
              <el-table-column prop="module" label="模块" width="150" />
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="scope">
                  <el-tag :type="getPriorityType(scope.row.priority)">
                    {{ scope.row.priority }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="editTestCase(scope.row)">
                    编辑
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="deleteTestCase(scope.row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建测试套件对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建测试套件" width="500px">
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="套件名称" prop="name">
          <el-input
            v-model="createForm.name"
            placeholder="请输入测试套件名称"
          />
        </el-form-item>
        <el-form-item label="父级套件">
          <el-select v-model="createForm.parent_id" placeholder="选择父级套件">
            <el-option
              v-for="option in suiteOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目">
          <el-select
            v-model="createForm.project_id"
            placeholder="请选择所属项目"
          >
            <!-- 实际应用中应该从API获取项目列表 -->
            <el-option label="示例项目" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="需求">
          <el-select
            v-model="createForm.version_requirement_id"
            placeholder="请选择关联需求"
          >
            <!-- 实际应用中应该根据选择的项目动态加载需求列表 -->
            <el-option label="需求1" value="1" />
            <el-option label="需求2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代">
          <el-select
            v-model="createForm.iteration_id"
            placeholder="请选择所属迭代"
          >
            <!-- 实际应用中应该根据选择的项目动态加载迭代列表 -->
            <el-option label="迭代1" value="1" />
            <el-option label="迭代2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入测试套件描述"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateSuite">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑测试套件对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑测试套件" width="500px">
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入测试套件名称" />
        </el-form-item>
        <el-form-item label="项目">
          <el-select v-model="editForm.project_id" placeholder="请选择所属项目">
            <!-- 实际应用中应该从API获取项目列表 -->
            <el-option label="示例项目" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="需求">
          <el-select
            v-model="editForm.version_requirement_id"
            placeholder="请选择关联需求"
          >
            <!-- 实际应用中应该根据选择的项目动态加载需求列表 -->
            <el-option label="需求1" value="1" />
            <el-option label="需求2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代">
          <el-select
            v-model="editForm.iteration_id"
            placeholder="请选择所属迭代"
          >
            <!-- 实际应用中应该根据选择的项目动态加载迭代列表 -->
            <el-option label="迭代1" value="1" />
            <el-option label="迭代2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入测试套件描述"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSuite">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <el-dropdown-menu
      ref="contextMenuRef"
      v-model="contextMenuVisible"
      trigger="manual"
    >
      <el-dropdown-item @click="showCreateSuiteDialog">
        新建测试套件
      </el-dropdown-item>
      <el-dropdown-item @click="showEditSuiteDialog(selectedNode)">
        编辑测试套件
      </el-dropdown-item>
      <el-dropdown-item type="danger" @click="deleteSuite(selectedNode.id)">
        删除测试套件
      </el-dropdown-item>
    </el-dropdown-menu>

    <el-dialog v-model="importDialogVisible" title="导入Xmind" width="500px">
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        :action="''"
        :auto-upload="false"
        :on-change="handleXmindFileChange"
        :show-file-list="true"
        accept=".xmind"
      >
        <el-button type="primary"> 选择Xmind文件 </el-button>
        <template #tip>
          <div class="el-upload__tip">请上传.xmind格式的文件</div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleImportXmind"
            >确定导入</el-button
          >
        </span>
      </template>
    </el-dialog>

    <!-- 添加测试用例对话框 -->
    <el-dialog
      v-model="addCaseDialogVisible"
      title="添加测试用例"
      width="800px"
    >
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
            height="300px"
            :row-class-name="rowClassName"
            @row-click="selectAvailableCase"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column
              prop="case_name"
              label="用例名称"
              min-width="250"
            />
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
          <el-button type="primary" @click="confirmAddCases"
            >确定添加</el-button
          >
        </span>
      </template>
    </el-dialog>

    <!-- 移动测试用例对话框 -->
    <el-dialog
      v-model="moveCaseDialogVisible"
      title="移动测试用例"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="选择目标套件">
          <el-select
            v-model="targetSuiteId"
            placeholder="请选择目标测试套件"
            filterable
          >
            <el-option
              v-for="option in projectSuiteOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <div class="move-case-info">
            <p>
              将移动 <strong>{{ selectedCaseIds.length }}</strong> 个测试用例
            </p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="moveCaseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmMoveCases"
            >确认移动</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox, ElLoading } from "element-plus";
import { Plus, Refresh, Edit, Delete, Folder } from "@element-plus/icons-vue";
import { testSuiteApi } from "@/api/testSuite";
import { getTestCasesBySuite } from "@/api/testCase";

export default {
  name: "TestSuiteManagement",
  components: {
    Plus,
    Refresh,
    Edit,
    Delete,
    Folder,
  },
  setup() {
    // 状态管理
    const treeData = ref([]);
    const searchKeyword = ref("");
    const selectedNode = ref(null);
    const selectedNodeId = ref(null);
    const testCasesData = ref([]);
    const suiteOptions = ref([]);
    // 测试用例关联相关变量
    const addCaseDialogVisible = ref(false);
    const moveCaseDialogVisible = ref(false);
    const availableCasesSearch = ref("");
    const availableCasesModule = ref("");
    const availableCasesPriority = ref("");
    const availableCasesPage = ref(1);
    const availableCasesPageSize = ref(10);
    const availableCasesData = ref([]);
    const availableCasesTotal = ref(0);
    const selectedCaseIds = ref([]);
    const targetSuiteId = ref("");
    const projectModules = ref([]);
    const projectSuiteOptions = ref([]);

    // 对话框状态
    const createDialogVisible = ref(false);
    const editDialogVisible = ref(false);
    const contextMenuVisible = ref(false);

    // 表单数据
    const createForm = reactive({
      name: "",
      parent_id: null,
      project_id: null,
      version_requirement_id: null,
      iteration_id: null,
      description: "",
    });

    const editForm = reactive({
      id: "",
      name: "",
      project_id: null,
      version_requirement_id: null,
      iteration_id: null,
      description: "",
    });

    // 表单规则
    const createRules = {
      name: [
        { required: true, message: "请输入测试套件名称", trigger: "blur" },
      ],
    };

    const editRules = {
      name: [
        { required: true, message: "请输入测试套件名称", trigger: "blur" },
      ],
    };

    // 引用
    const treeRef = ref(null);
    const createFormRef = ref(null);
    const editFormRef = ref(null);
    const contextMenuRef = ref(null);

    // 树结构配置
    const defaultProps = {
      children: "children",
      label: "name",
    };

    // 计算属性：过滤后的树数据
    const filteredTreeData = computed(() => {
      if (!searchKeyword.value) return treeData.value;

      const filterNode = (nodes) => {
        return nodes
          .map((node) => {
            const newNode = { ...node };
            if (node.children && node.children.length > 0) {
              newNode.children = filterNode(node.children);
            }
            return newNode;
          })
          .filter((node) => {
            const matchSelf = node.name
              .toLowerCase()
              .includes(searchKeyword.value.toLowerCase());
            const matchChildren = node.children && node.children.length > 0;
            return matchSelf || matchChildren;
          });
      };

      return filterNode(treeData.value);
    });

    // 计算属性：是否全选
    const isAllSelected = computed(() => {
      return (
        testCasesData.value.length > 0 &&
        selectedCaseIds.value.length === testCasesData.value.length
      );
    });

    // 方法
    const loadTreeData = async () => {
      try {
        const response = await testSuiteApi.getTestSuiteTree();
        treeData.value = response.data;
      } catch (error) {
        ElMessage.error("加载测试套件树失败");
      }
    };

    const loadSuiteOptions = async () => {
      try {
        const response = await testSuiteApi.getTestSuiteOptions();
        suiteOptions.value = response.data.options;
      } catch (error) {
        ElMessage.error("加载测试套件选项失败");
      }
    };

    const loadTestCases = async (suiteId) => {
      try {
        const response = await getTestCasesBySuite(suiteId);
        testCasesData.value = response.data;
      } catch (error) {
        ElMessage.error("加载测试用例失败");
      }
    };

    const handleNodeClick = (data) => {
      selectedNode.value = data;
      selectedNodeId.value = data.id;
      loadTestCases(data.id);
    };

    const handleContextMenu = (event, data) => {
      event.preventDefault();
      selectedNode.value = data;
      selectedNodeId.value = data.id;
      contextMenuVisible.value = true;

      // 计算右键菜单位置
      const menu = contextMenuRef.value.$el;
      menu.style.left = `${event.pageX}px`;
      menu.style.top = `${event.pageY}px`;
    };

    const showCreateSuiteDialog = () => {
      // 完全重置表单所有属性
      Object.assign(createForm, {
        name: "",
        parent_id: selectedNode.value?.id || null,
        project_id: null,
        version_requirement_id: null,
        iteration_id: null,
        description: "",
      });
      // 不调用resetFields()，避免将字段重置为可能被污染的初始值
      createDialogVisible.value = true;
    };

    const handleCreateSuite = async () => {
      try {
        await createFormRef.value.validate();
        const loading = ElLoading.service({ text: "创建中..." });
        await testSuiteApi.createTestSuite({
          name: createForm.name,
          parent_id: createForm.parent_id,
          project_id: createForm.project_id,
          version_requirement_id: createForm.version_requirement_id,
          iteration_id: createForm.iteration_id,
          description: createForm.description,
        });
        loading.close();
        ElMessage.success("创建成功");
        createDialogVisible.value = false;
        loadTreeData();
      } catch (error) {
        if (error.name !== "Error") return;
        ElMessage.error("创建失败");
      }
    };

    const showEditSuiteDialog = (data) => {
      // 为编辑表单赋值，确保不会影响新增表单
      Object.assign(editForm, {
        id: data.id,
        name: data.name,
        project_id: data.project_id || null,
        version_requirement_id: data.version_requirement_id || null,
        iteration_id: data.iteration_id || null,
        description: data.description || "",
      });
      // 移除resetFields()调用，避免将字段重置为初始值
      editDialogVisible.value = true;
    };

    const handleEditSuite = async () => {
      try {
        await editFormRef.value.validate();
        const loading = ElLoading.service({ text: "更新中..." });
        await testSuiteApi.updateTestSuite(editForm.id, {
          name: editForm.name,
          project_id: editForm.project_id,
          version_requirement_id: editForm.version_requirement_id,
          iteration_id: editForm.iteration_id,
          description: editForm.description,
        });
        loading.close();
        ElMessage.success("更新成功");
        editDialogVisible.value = false;
        loadTreeData();

        // 如果编辑的是当前选中的节点，更新选中节点数据
        if (selectedNode.value && selectedNode.value.id === editForm.id) {
          selectedNode.value.name = editForm.name;
          selectedNode.value.project_id = editForm.project_id;
          selectedNode.value.version_requirement_id =
            editForm.version_requirement_id;
          selectedNode.value.iteration_id = editForm.iteration_id;
          selectedNode.value.description = editForm.description;
        }
      } catch (error) {
        if (error.name !== "Error") return;
        ElMessage.error("更新失败");
      }
    };

    const deleteSuite = async (id) => {
      try {
        await ElMessageBox.confirm(
          "确定要删除此测试套件吗？这将同时删除所有子套件和相关测试用例。",
          "确认删除",
          {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning",
          },
        );

        const loading = ElLoading.service({ text: "删除中..." });
        await testSuiteApi.deleteTestSuite(id);
        loading.close();
        ElMessage.success("删除成功");
        loadTreeData();

        // 如果删除的是当前选中的节点，清空选中状态
        if (selectedNode.value && selectedNode.value.id === id) {
          selectedNode.value = null;
          selectedNodeId.value = null;
          testCasesData.value = [];
        }
      } catch (error) {
        if (error.name !== "Error") return;
        ElMessage.error("删除失败");
      }
    };

    const createTestCase = () => {
      // 此处跳转到测试用例创建页面，并传入当前套件ID
      // 这里简单实现，实际应该使用路由跳转
      ElMessage.info(
        `跳转到测试用例创建页面，套件ID: ${selectedNode.value.id}`,
      );
    };

    const editTestCase = (testCase) => {
      // 此处跳转到测试用例编辑页面
      ElMessage.info(`跳转到测试用例编辑页面，ID: ${testCase.id}`);
    };

    const deleteTestCase = async (id) => {
      try {
        await ElMessageBox.confirm("确定要删除此测试用例吗？", "确认删除", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        });

        // 调用删除API
        // 这里简化处理，实际应该调用对应的API
        ElMessage.success("删除成功");
        loadTestCases(selectedNode.value.id);
      } catch (error) {
        if (error.name !== "Error") return;
        ElMessage.error("删除失败");
      }
    };

    const refreshTree = () => {
      loadTreeData();
    };

    const getPriorityType = (priority) => {
      const typeMap = {
        high: "danger",
        medium: "warning",
        low: "success",
      };
      return typeMap[priority] || "info";
    };

    const getStatusType = (status) => {
      const typeMap = {
        active: "success",
        inactive: "info",
        deprecated: "danger",
      };
      return typeMap[status] || "info";
    };

    // 打开添加测试用例对话框
    const openAddCaseDialog = () => {
      if (!selectedNode.value) {
        ElMessage.warning("请先选择一个测试套件");
        return;
      }
      addCaseDialogVisible.value = true;
      selectedCaseIds.value = [];
      availableCasesPage.value = 1;
      getAvailableCases();
      getProjectModules();
    };

    // 获取可用的测试用例
    const getAvailableCases = async () => {
      try {
        // 实际应用中需要从API获取数据
        // 这里模拟数据
        availableCasesData.value = [];
        availableCasesTotal.value = 0;
      } catch (error) {
        ElMessage.error("获取可用测试用例失败");
        console.error("获取可用测试用例失败:", error);
      }
    };

    // 获取项目模块列表
    const getProjectModules = async () => {
      try {
        // 实际应用中需要从API获取数据
        // 这里模拟数据
        projectModules.value = [];
      } catch (error) {
        console.error("获取项目模块失败:", error);
      }
    };

    // 处理可用测试用例搜索
    const handleAvailableCasesSearch = () => {
      availableCasesPage.value = 1;
      getAvailableCases();
    };

    // 处理分页变化
    const handleAvailableCasesPageChange = () => {
      getAvailableCases();
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
      return selectedCaseIds.value.includes(row.id) ? "selected-row" : "";
    };

    // 取消添加测试用例
    const cancelAddCases = () => {
      addCaseDialogVisible.value = false;
      selectedCaseIds.value = [];
    };

    // 确认添加测试用例
    const confirmAddCases = async () => {
      if (selectedCaseIds.value.length === 0) {
        ElMessage.warning("请至少选择一个测试用例");
        return;
      }

      try {
        // 实际应用中需要调用API
        ElMessage.success("添加测试用例成功");
        addCaseDialogVisible.value = false;
        loadTestCases(selectedNode.value.id); // 重新加载套件用例
        selectedCaseIds.value = [];
      } catch (error) {
        ElMessage.error("添加测试用例失败");
        console.error("添加测试用例失败:", error);
      }
    };

    // 打开移动测试用例对话框
    const openMoveCaseDialog = async () => {
      if (testCasesData.value.length === 0) {
        ElMessage.warning("请先选择要移动的测试用例");
        return;
      }

      try {
        // 实际应用中需要从API获取数据
        // 这里模拟数据
        projectSuiteOptions.value = [];

        moveCaseDialogVisible.value = true;
        targetSuiteId.value = "";
      } catch (error) {
        ElMessage.error("获取测试套件选项失败");
        console.error("获取测试套件选项失败:", error);
      }
    };

    // 确认移动测试用例
    const confirmMoveCases = async () => {
      if (!targetSuiteId.value) {
        ElMessage.warning("请选择目标测试套件");
        return;
      }

      try {
        // 实际应用中需要调用API
        ElMessage.success("移动测试用例成功");
        moveCaseDialogVisible.value = false;
        loadTestCases(selectedNode.value.id); // 重新加载套件用例
        selectedCaseIds.value = [];
      } catch (error) {
        ElMessage.error("移动测试用例失败");
        console.error("移动测试用例失败:", error);
      }
    };

    // 拖拽相关方法
    const allowDrag = (draggingNode) => {
      // 允许所有节点拖拽
      return true;
    };

    const allowDrop = (draggingNode, dropNode, type) => {
      // 允许拖拽到任意节点的下方或内部
      // 这里可以根据业务需求添加限制
      return ["before", "after", "inner"].includes(type);
    };

    const handleNodeDrop = async (draggingNode, dropNode, dropType, ev) => {
      try {
        const loading = ElLoading.service({ text: "保存排序中..." });

        // 准备更新数据
        const updateData = {
          id: draggingNode.data.id,
          parent_id:
            dropType === "inner" ? dropNode.data.id : dropNode.data.parent_id,
          sort_order: 0, // 后端会根据新的位置重新计算sort_order
        };

        // 调用后端API更新测试套件的位置
        await testSuiteApi.updateTestSuite(updateData.id, updateData);

        // 重新加载树数据
        await loadTreeData();

        loading.close();
        ElMessage.success("排序更新成功");
      } catch (error) {
        ElMessage.error("排序更新失败");
        console.error("排序更新失败:", error);
      }
    };

    // 初始化
    onMounted(() => {
      loadTreeData();
      loadSuiteOptions();

      // 点击其他地方关闭右键菜单
      document.addEventListener("click", () => {
        contextMenuVisible.value = false;
      });
    });

    return {
      // 状态
      treeData,
      searchKeyword,
      selectedNode,
      selectedNodeId,
      testCasesData,
      suiteOptions,
      createDialogVisible,
      editDialogVisible,
      contextMenuVisible,
      createForm,
      editForm,
      createRules,
      editRules,
      // 测试用例关联相关状态
      addCaseDialogVisible,
      moveCaseDialogVisible,
      availableCasesSearch,
      availableCasesModule,
      availableCasesPriority,
      availableCasesPage,
      availableCasesPageSize,
      availableCasesData,
      availableCasesTotal,
      selectedCaseIds,
      targetSuiteId,
      projectModules,
      projectSuiteOptions,
      // 引用
      treeRef,
      createFormRef,
      editFormRef,
      contextMenuRef,
      // 配置
      defaultProps,
      filteredTreeData,
      // 方法
      handleNodeClick,
      handleContextMenu,
      showCreateSuiteDialog,
      handleCreateSuite,
      showEditSuiteDialog,
      handleEditSuite,
      deleteSuite,

      createTestCase,
      editTestCase,
      deleteTestCase,
      refreshTree,
      getPriorityType,
      getStatusType,
      // 拖拽相关方法
      allowDrag,
      allowDrop,
      handleNodeDrop,
      // 测试用例关联相关方法
      openAddCaseDialog,
      getAvailableCases,
      getProjectModules,
      handleAvailableCasesSearch,
      handleAvailableCasesPageChange,
      selectAvailableCase,
      rowClassName,
      cancelAddCases,
      confirmAddCases,
      openMoveCaseDialog,
      confirmMoveCases,
    };
  },
};
</script>

<style scoped>
.test-suite-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
}

.tree-container {
  width: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.search-input {
  margin: 10px;
}

.el-tree {
  flex: 1;
  overflow: auto;
}

.tree-node-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.node-actions {
  display: none;
}

.tree-node-content:hover .node-actions {
  display: flex;
  gap: 5px;
}

.action-icon {
  cursor: pointer;
  font-size: 16px;
  padding: 2px;
}

.action-icon:hover {
  color: #409eff;
}

.content-container {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.suite-details {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.suite-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suite-actions {
  display: flex;
  gap: 10px;
}

.test-cases-section {
  padding: 20px;
  flex: 1;
  overflow: auto;
}

.test-cases-section h3 {
  margin-bottom: 16px;
}
/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.upload-demo {
  margin-bottom: 20px;
}

/* 测试用例对话框样式 */
.add-case-dialog-content {
  padding: 10px 0;
}

.search-filter-section {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.search-filter-section .el-input {
  width: 250px;
}

.search-filter-section .el-select {
  width: 150px;
}

.available-cases-section {
  margin-bottom: 15px;
}

.available-cases-section h4 {
  margin-bottom: 10px;
  font-weight: 500;
}

.pagination-section {
  margin-top: 10px;
  text-align: right;
}

.selected-row {
  background-color: #f5f7fa;
}

.move-case-info {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.move-case-info strong {
  color: #409eff;
}
</style>
