<template>
  <div class="test-case-management">
    <div class="page-header">
      <div class="header-content">
        <h1>测试用例管理</h1>
        <p class="description">管理和执行测试用例</p>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧树形组件 -->
      <div class="left-panel">
        <div class="panel-header">
          <el-input
            v-model="searchText"
            placeholder="搜索测试套件"
            prefix-icon="Search"
            clearable
            size="small"
          />
          <div class="header-actions">
            <el-button
              size="small"
              icon="RefreshRight"
              @click="handleRefresh"
              circle
              title="刷新"
            />
            <el-button
              type="primary"
              size="small"
              icon="Plus"
              @click="handleAddSuite"
              circle
              title="新增套件"
            />
          </div>
        </div>
        
        <div class="tree-container">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="defaultProps"
            :filter-node-method="filterNode"
            :draggable="isDraggable"
            :allow-drop="allowDrop"
            :allow-drag="allowDrag"
            :default-expanded-keys="expandedKeys"
            @node-click="handleNodeClick"
            @node-drop="handleNodeDrop"
            @node-contextmenu="handleContextMenu"
            @node-expand="handleNodeExpand"
            @node-collapse="handleNodeCollapse"
            node-key="id"
          >
            <template #default="{ node, data }">
              <span class="tree-node-content">
                <el-icon class="node-icon">
                  <Folder v-if="data.type === 'folder'" />
                  <Document v-else />
                </el-icon>
                <span v-if="!editingNodeId || editingNodeId !== data.id" @dblclick="startEdit(data)">
                  {{ node.label }}
                </span>
                <el-input
                  v-else
                  v-model="editingNodeName"
                  ref="editInputRef"
                  size="small"
                  @blur="saveEdit(data)"
                  @keyup.enter="saveEdit(data)"
                  @keyup.esc="cancelEdit"
                  autofocus
                />
                <span class="case-count" v-if="data.type === 'suite'">({{ data.cases_count }})</span>
              </span>
            </template>
          </el-tree>
        </div>

        <!-- 右键菜单 -->
        <div
          ref="contextMenuRef"
          v-show="contextMenuVisible"
          :style="contextMenuStyle"
          class="context-menu"
        >
          <div class="menu-item" @click="handleAddSuiteFromMenu">
            <el-icon><Plus /></el-icon> 新增套件
          </div>
          <div class="menu-item" @click="handleEditSuite">
            <el-icon><Edit /></el-icon> 编辑套件
          </div>
          <div class="menu-item" @click="handleDeleteSuite">
            <el-icon><Delete /></el-icon> 删除套件
          </div>
          <div class="menu-item" @click="handleMoveSuite">
            <el-icon><Rank /></el-icon> 移动套件
          </div>
        </div>
      </div>

      <!-- 右侧用例列表 -->
      <div class="right-panel">
        <div class="panel-header">
          <div class="header-content">
            <h3>{{ selectedSuite ? selectedSuite.suite_name : '用例列表' }}</h3>
            <div class="suite-info" v-if="selectedSuite">
              <div class="info-item">
                <span class="label">项目:</span>
                <span class="value">{{ selectedSuite.project_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">迭代:</span>
                <span class="value">{{ selectedSuite.iteration_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">需求:</span>
                <span class="value">{{ selectedSuite.version_requirement_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建人:</span>
                <span class="value">{{ selectedSuite.creator_name || '-' }}</span>
              </div>
            </div>
          </div>
          <div class="header-actions">
            <el-button
              type="danger"
              icon="Delete"
              @click="toggleSelectionMode"
              v-if="!showSelection"
            >
              选中删除
            </el-button>
            <el-button
              type="danger"
              icon="Delete"
              @click="handleDeleteSelection"
              v-else
            >
              点击删除
            </el-button>
            <el-button
              type="primary"
              icon="Plus"
              @click="handleAddCase"
            >
              新增用例
            </el-button>
            <el-button
              type="success"
              icon="View"
              @click="toggleViewMode"
            >
              {{ viewMode === 'list' ? '脑图视图' : '列表视图' }}
            </el-button>
          </div>
        </div>

        <!-- 用例列表 -->
        <div v-if="viewMode === 'list'" class="case-list">
          <el-table
            :data="testCases"
            style="width: 100%"
            border
            height="calc(100vh - 250px)"
            :row-style="{height: 'auto'}"
            :cell-style="{padding: '10px', whiteSpace: 'normal', wordBreak: 'break-word'}"
            @cell-click="handleCellClick"
            ref="caseTableRef"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" v-if="showSelection" />
            <el-table-column prop="case_number" label="编号" width="120">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'case_number'">
                  <el-input v-model="editingValue" @blur="saveCaseEdit(row)" @keyup.enter="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'case_number')">{{ row.case_number || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="case_name" label="用例名称" min-width="120">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'case_name'">
                  <el-input v-model="editingValue" @blur="saveCaseEdit(row)" @keyup.enter="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'case_name')">{{ row.case_name }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'priority'">
                  <el-select v-model="editingValue" @change="saveCaseEdit(row)" style="width: 100%">
                    <el-option label="P0" value="P0" />
                    <el-option label="P1" value="P1" />
                    <el-option label="P2" value="P2" />
                    <el-option label="P3" value="P3" />
                    <el-option label="P4" value="P4" />
                  </el-select>
                </template>
                <el-tag
                  v-else
                  :type="row.priority === 'P0' ? 'danger' : row.priority === 'P1' ? 'danger' : row.priority === 'P2' ? 'warning' : row.priority === 'P3' ? 'info' : 'success'"
                  size="small"
                  @dblclick="startCaseEdit(row, 'priority')"
                >
                  {{ row.priority }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="85">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'status'">
                  <el-select v-model="editingValue" @change="saveCaseEdit(row)" style="width: 100%">
                    <el-option label="" value="" />
                    <el-option label="通过" value="pass" />
                    <el-option label="失败" value="fail" />
                    <el-option label="阻塞" value="blocked" />
                    <el-option label="不适用" value="not_applicable" />
                  </el-select>
                </template>
                <template v-else>
                  <el-tag
                    v-if="row.status"
                    :type="row.status === 'pass' ? 'success' : row.status === 'fail' ? 'danger' : row.status === 'blocked' ? 'warning' : 'info'"
                    size="small"
                    @dblclick="startCaseEdit(row, 'status')"
                  >
                    {{ row.status === 'pass' ? '通过' : row.status === 'fail' ? '失败' : row.status === 'blocked' ? '阻塞' : '不适用' }}
                  </el-tag>
                  <el-tag v-else size="small" type="info" @dblclick="startCaseEdit(row, 'status')">
                    未设置
                  </el-tag>
                </template>
              </template>
            </el-table-column>
            <!-- 创建人信息已移至顶部标题区域 -->
            <el-table-column prop="preconditions" label="前置条件" min-width="180">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'preconditions'">
                  <el-input v-model="editingValue" type="textarea" :rows="3" @blur="saveCaseEdit(row)" @keyup.enter.ctrl="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'preconditions')">{{ row.preconditions || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="steps" label="操作步骤" min-width="180">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'steps'">
                  <el-input v-model="editingValue" type="textarea" :rows="5" @blur="saveCaseEdit(row)" @keyup.enter.ctrl="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'steps')">{{ row.steps || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="expected_result" label="预期结果" min-width="180">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'expected_result'">
                  <el-input v-model="editingValue" type="textarea" :rows="3" @blur="saveCaseEdit(row)" @keyup.enter.ctrl="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'expected_result')">{{ row.expected_result || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="actual_result" label="实际结果" min-width="180">
              <template #default="{ row }">
                <template v-if="editingCaseId === row.id && editingField === 'actual_result'">
                  <el-input v-model="editingValue" type="textarea" :rows="3" @blur="saveCaseEdit(row)" @keyup.enter.ctrl="saveCaseEdit(row)" @keyup.esc="cancelCaseEdit" autofocus />
                </template>
                <div v-else @dblclick="startCaseEdit(row, 'actual_result')">{{ row.actual_result || '-' }}</div>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalCases"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <!-- 脑图视图（暂不实现） -->
        <div v-else class="mindmap-view">
          <el-empty description="脑图视图功能暂未实现" />
        </div>
      </div>
    </div>

    <!-- 新增/编辑套件对话框 -->
    <el-dialog
      v-model="suiteDialogVisible"
      :title="isEditSuite ? '编辑测试套件' : '新增测试套件'"
      width="750px"
    >
      <el-form :model="suiteForm" label-width="80px">
        <el-form-item label="套件名称" required>
          <el-input v-model="suiteForm.suite_name" placeholder="请输入测试套件名称" />
        </el-form-item>
        <el-form-item label="套件类型" required v-if="!isEditSuite">
          <el-select v-model="suiteForm.type" placeholder="请选择套件类型">
            <el-option label="用例文件夹" value="folder" />
            <el-option label="用例集" value="suite" />
          </el-select>
        </el-form-item>
        <el-form-item label="父套件">
          <div class="parent-suite-selector">
            <!-- 显示当前选中的父套件路径 -->
            <el-popover
              visible="parentSuitePopoverVisible"
              placement="bottom-start"
              trigger="click"
              width="auto"
            >
              <template #reference>
                <el-input
                  v-model="selectedParentSuitePath"
                  placeholder="点击选择父套件（默认根套件）"
                  readonly
                  style="width: 100%; min-width: 640px;"
                  @click="parentSuitePopoverVisible = true"
                />
              </template>
              <!-- 弹出的套件树 -->
              <div class="suite-tree-popover" style="width: 100%; min-width: 615px;">
                <el-tree
                  :current-node-key="suiteForm.parent_id"
                  :data="getFolderTreeData()"
                  :props="defaultProps"
                  node-key="id"
                  @node-click="(data) => {
                    suiteForm.parent_id = data.id;
                    selectedParentSuitePath.value = getSelectedParentPath();
                    parentSuitePopoverVisible = false;
                  }"
                  style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                >
                  <template #default="{ node }">
                    <span class="tree-node-content" :class="{'current-node': node.key === suiteForm.parent_id}">
                      <el-icon class="node-icon">
                        <Folder />
                      </el-icon>
                      <span>{{ node.label }}</span>
                    </span>
                  </template>
                </el-tree>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        <el-form-item label="项目" v-if="suiteForm.type === 'suite'">
          <el-select v-model="suiteForm.project_id" placeholder="请选择所属项目">
            <!-- 实际应用中应该从API获取项目列表 -->
            <el-option label="示例项目" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="需求" v-if="suiteForm.type === 'suite'">
          <el-select v-model="suiteForm.version_requirement_id" placeholder="请选择关联需求">
            <!-- 实际应用中应该根据选择的项目动态加载需求列表 -->
            <el-option label="需求1" value="1" />
            <el-option label="需求2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代" v-if="suiteForm.type === 'suite'">
          <el-select v-model="suiteForm.iteration_id" placeholder="请选择所属迭代">
            <!-- 实际应用中应该根据选择的项目动态加载迭代列表 -->
            <el-option label="迭代1" value="1" />
            <el-option label="迭代2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="suiteForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入测试套件描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="suiteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveSuite">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增/编辑用例对话框 -->
    <el-dialog
      v-model="caseDialogVisible"
      :title="isEditCase ? '编辑测试用例' : '新增测试用例'"
      width="700px"
    >
      <el-form :model="caseForm" label-width="100px">
        <el-form-item label="用例名称" required>
          <el-input v-model="caseForm.case_name" placeholder="请输入测试用例名称" />
        </el-form-item>
        <el-form-item label="用例编号">
          <el-input v-model="caseForm.case_number" placeholder="请输入测试用例编号" />
        </el-form-item>
        <el-form-item label="所属套件" required>
          <el-select
            v-model="caseForm.suite_id"
            placeholder="请选择所属套件"
          >
            <el-option
              v-for="item in treeData"
              :key="item.id"
              :label="item.suite_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" required>
          <el-select v-model="caseForm.priority" placeholder="请选择优先级">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
            <el-option label="P4" value="P4" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="caseForm.status" placeholder="请选择状态">
            <el-option label="" value="" />
            <el-option label="通过" value="pass" />
            <el-option label="失败" value="fail" />
            <el-option label="阻塞" value="blocked" />
            <el-option label="不适用" value="not_applicable" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input
            v-model="caseForm.preconditions"
            type="textarea"
            :rows="3"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input
            v-model="caseForm.steps"
            type="textarea"
            :rows="5"
            placeholder="请输入测试步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input
            v-model="caseForm.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="caseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveCase">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import { getTestSuiteTree, getSuiteCases, createTestSuite, updateTestSuite, deleteTestSuite } from '@/api/testSuite'

// API导入
import { updateTestCase, createTestCase, deleteTestCase, batchDeleteTestCases } from '@/api/testCase'

// 树形组件相关
const treeRef = ref(null)
const treeData = ref([])
const searchText = ref('')
const defaultProps = {
  children: 'children',
  label: 'suite_name'
}
const isDraggable = ref(true) // 控制树组件拖拽功能

// 存储用户手动展开的节点ID
const expandedKeys = ref([])

// 编辑节点相关
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)

// 右键菜单相关
const contextMenuRef = ref(null)
const contextMenuVisible = ref(false)
const contextMenuStyle = reactive({
  position: 'fixed',
  zIndex: 1000
})
const selectedNode = ref(null)

// 父套件选择器相关
const parentSuitePopoverVisible = ref(false)
const selectedParentSuitePath = ref('')

// 对话框相关
const suiteDialogVisible = ref(false)
const caseDialogVisible = ref(false)
const isEditSuite = ref(false)
const isEditCase = ref(false)

// 表单数据
const suiteForm = reactive({
  id: null,
  suite_name: '',
  description: '',
  type: 'folder', // 默认类型为文件夹
  parent_id: null,
  project_id: 1, // 默认项目ID，实际应从上下文获取
  version_requirement_id: null,
  iteration_id: null
})

// 存储套件选项，用于父级套件选择
const suiteOptions = ref([])

const caseForm = reactive({
  id: null,
  case_number: '',
  case_name: '',
  case_description: '',
  priority: 'P1',
  status: '',
  suite_id: null,
  preconditions: '',
  steps: '',
  expected_result: ''
})

// 用例列表相关
const selectedSuite = ref(null)
const testCases = ref([])
const totalCases = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const viewMode = ref('list')

// 用例内联编辑相关
const editingCaseId = ref(null)
const editingField = ref(null)
const editingValue = ref('')

// 选中删除相关
const showSelection = ref(false)
const selectedCases = ref([])
const caseTableRef = ref(null)

// 过滤节点方法
const filterNode = (value, data) => {
  if (!value) return true
  return data.suite_name.includes(value)
}

// 监听搜索文本变化
watch(searchText, (newVal) => {
  if (treeRef.value) {
    treeRef.value.filter(newVal)
  }
})

// 允许拖拽
const allowDrag = (node) => {
  // 可以根据需要限制某些节点不能拖拽
  return true
}

// 允许放置
const allowDrop = (draggingNode, dropNode, type) => {
  // 限制5级深度
  if (type === 'inner') {
    const level = dropNode.level
    if (level >= 5) {
      return false
    }
  }
  return true
}

// 节点展开事件处理
const handleNodeExpand = (data) => {
  if (!expandedKeys.value.includes(data.id)) {
    expandedKeys.value.push(data.id)
  }
}

// 节点折叠事件处理
const handleNodeCollapse = (data) => {
  const index = expandedKeys.value.indexOf(data.id)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  }
}

// 节点点击事件
const handleNodeClick = (data) => {
  selectedSuite.value = data
  if (data.type === 'suite') {
    // 只有用例集才能加载测试用例
    loadTestCases(data.id)
  } else {
    // 文件夹清空测试用例列表
    testCases.value = []
    totalCases.value = 0
  }
}

// 开始编辑节点名称
const startEdit = (data) => {
  isDraggable.value = false // 禁用拖拽功能
  editingNodeId.value = data.id
  editingNodeName.value = data.suite_name
  // 延迟聚焦，确保输入框已渲染
  setTimeout(() => {
    if (editInputRef.value) {
      editInputRef.value.focus()
    }
  }, 100)
}

// 保存编辑
const saveEdit = async (data) => {
  if (!editingNodeName.value.trim()) {
    ElMessage.warning('套件名称不能为空')
    return
  }
  
  try {
    await updateTestSuite(data.id, {
      suite_name: editingNodeName.value.trim()
    })
    data.suite_name = editingNodeName.value.trim()
    ElMessage.success('套件名称已更新')
    editingNodeId.value = null
    isDraggable.value = true // 恢复拖拽功能
  } catch (error) {
    console.error('更新套件名称失败:', error)
    ElMessage.error('更新套件名称失败')
  }
}

// 取消编辑
const cancelEdit = () => {
  editingNodeId.value = null
  isDraggable.value = true // 恢复拖拽功能
}

// 节点拖拽事件
const handleNodeDrop = async (draggingNode, dropNode, dropType) => {
  // 处理拖拽逻辑，更新节点位置
  console.log('Node dropped:', draggingNode, dropNode, dropType)
  
  try {
    let parentId = null
    let sortOrder = 0
    
    if (dropType === 'inner') {
      // 拖入节点内部，设置parent_id为dropNode的id
      parentId = dropNode.data.id
      // 计算新的sort_order，添加到尾部
      // 获取该文件夹下最大的sort_order值，确保新节点排序到末尾
      const lastChild = dropNode.data.children && dropNode.data.children.length > 0 ? 
                        [...dropNode.data.children].sort((a, b) => b.sort_order - a.sort_order)[0] : null
      sortOrder = lastChild ? lastChild.sort_order + 1 : 1
    } else if (dropType === 'before') {
      // 拖到节点前面，设置parent_id与dropNode相同
      parentId = dropNode.data.parent_id
      // 对于'before'类型，我们希望当前节点被放置在dropNode之前
      // 所以设置sort_order为dropNode的sort_order
      sortOrder = dropNode.data.sort_order
    } else if (dropType === 'after') {
      // 拖到节点后面，设置parent_id与dropNode相同
      parentId = dropNode.data.parent_id
      // 对于'after'类型，我们希望当前节点被放置在dropNode之后
      // 所以设置sort_order为dropNode的sort_order + 1
      sortOrder = dropNode.data.sort_order + 1
    }
    
    // 调用API更新父级节点ID和排序
    await updateTestSuite(draggingNode.data.id, {
      parent_id: parentId,
      sort_order: sortOrder
    })
    
    // 重新加载树形数据
    await loadTreeData()
    
    ElMessage.success('套件位置已更新')
  } catch (error) {
    console.error('更新套件位置失败:', error)
    ElMessage.error('更新套件位置失败，请稍后重试')
  }
}

// 右键菜单事件
const handleContextMenu = (event, node) => {
  event.preventDefault()
  selectedNode.value = node
  contextMenuStyle.left = `${event.clientX}px`
  contextMenuStyle.top = `${event.clientY}px`
  contextMenuVisible.value = true
}

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
}

// 点击页面其他地方关闭右键菜单
onMounted(() => {
  document.addEventListener('click', closeContextMenu)
  loadTreeData()
})

// 加载树形数据
const loadTreeData = async () => {
  try {
    const response = await getTestSuiteTree()
    treeData.value = response.data
    
    // 更新套件选项
    suiteOptions.value = buildSuiteOptions()
    
    // 数据更新后，Element Plus Tree 会自动使用 default-expanded-keys 恢复展开状态
  } catch (error) {
    ElMessage.error('加载测试套件失败')
    console.error('Failed to load test suites:', error)
  }
}

// 加载测试用例
const loadTestCases = async (suiteId) => {
  try {
    const response = await getSuiteCases(suiteId, {
      page: currentPage.value,
      page_size: pageSize.value
    })
    testCases.value = response.data.items
    totalCases.value = response.data.total
  } catch (error) {
    ElMessage.error('加载测试用例失败')
    console.error('Failed to load test cases:', error)
  }
}

// 新增套件
const handleAddSuite = () => {
  isEditSuite.value = false
  resetSuiteForm()
  suiteDialogVisible.value = true
}

// 从右键菜单新增套件
const handleAddSuiteFromMenu = () => {
  isEditSuite.value = false
  resetSuiteForm()
  if (selectedNode.value) {
    suiteForm.parent_id = selectedNode.value.data.id
  }
  suiteDialogVisible.value = true
  closeContextMenu()
}

// 编辑套件
const handleEditSuite = () => {
  if (!selectedNode.value) return
  startEdit(selectedNode.value.data)
  closeContextMenu()
}

// 删除套件
const handleDeleteSuite = async () => {
  if (!selectedNode.value) return
  ElMessageBox.confirm('确定要删除该测试套件吗？删除后将无法恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTestSuite(selectedNode.value.data.id)
      ElMessage.success('测试套件已删除')
      loadTreeData()
    } catch (error) {
      console.error('删除测试套件失败:', error)
      ElMessage.error('删除测试套件失败')
    } finally {
      closeContextMenu()
    }
  }).catch(() => {
    // 取消删除
    closeContextMenu()
  })
}

// 移动套件
const handleMoveSuite = () => {
  ElMessage.info('移动套件功能开发中')
  closeContextMenu()
}

// 保存套件
const handleSaveSuite = async () => {
  try {
    if (isEditSuite.value) {
      // 编辑套件
      await updateTestSuite(suiteForm.id, suiteForm)
      ElMessage.success('测试套件已更新')
    } else {
      // 新增套件
      await createTestSuite(suiteForm)
      ElMessage.success('测试套件已创建')
    }
    suiteDialogVisible.value = false
    loadTreeData()
  } catch (error) {
    console.error('保存测试套件失败:', error)
    ElMessage.error(isEditSuite.value ? '更新测试套件失败' : '创建测试套件失败')
  }
}

// 重置套件表单
const resetSuiteForm = () => {
  suiteForm.id = null
  suiteForm.suite_name = ''
  suiteForm.description = ''
  suiteForm.parent_id = null
}

// 刷新树形数据
const handleRefresh = () => {
  loadTreeData()
  ElMessage.info('已刷新测试套件')
}

// 过滤只显示文件夹类型的节点
const getFolderTreeData = () => {
  const filterFolderNodes = (nodes) => {
    return nodes
      .filter(node => node.type === 'folder')
      .map(node => ({
        ...node,
        children: node.children ? filterFolderNodes(node.children) : []
      }))
  }
  return filterFolderNodes(treeData.value)
}

// 获取选中的父套件路径
const getSelectedParentPath = () => {
  if (!suiteForm.parent_id) return ''
  
  const findNodePath = (nodes, id, path = []) => {
    for (const node of nodes) {
      if (node.id === id) {
        return [...path, node.suite_name]
      }
      if (node.children) {
        const result = findNodePath(node.children, id, [...path, node.suite_name])
        if (result) return result
      }
    }
    return null
  }
  
  const path = findNodePath(treeData.value, suiteForm.parent_id)
  return path ? path.join(' / ') : ''
}

// 监听父套件ID变化，更新显示路径
watch(() => suiteForm.parent_id, () => {
  selectedParentSuitePath.value = getSelectedParentPath()
})



// 清除父套件选择
const clearParentSuiteSelection = () => {
  suiteForm.parent_id = null
  selectedParentSuitePath.value = ''
}

// 原函数保留，确保兼容性
const handleParentSuiteSelect = (data) => {
  suiteForm.parent_id = data.id
  selectedParentSuitePath.value = getSelectedParentPath()
}

// 构建嵌套的套件选项
const buildSuiteOptions = () => {
  const options = []
  
  const traverse = (nodes, level = 0) => {
    nodes.forEach(node => {
      if (node.type === 'folder') {
        // 只有文件夹可以包含子套件
        const indent = level > 0 ? ''.padStart(level, ' ') + '└ ' : '';
        options.push({
          value: node.id,
          label: `${indent}${node.suite_name}`,
          level
        })
        
        if (node.children && node.children.length > 0) {
          traverse(node.children, level + 1)
        }
      }
    })
  }
  
  traverse(treeData.value)
  return options
}

// 新增用例
const handleAddCase = () => {
  if (!selectedSuite.value) {
    ElMessage.warning('请先选择一个测试套件')
    return
  }
  if (selectedSuite.value.type !== 'suite') {
    ElMessage.warning('只能在测试用例集中添加测试用例')
    return
  }
  isEditCase.value = false
  resetCaseForm()
  caseForm.suite_id = selectedSuite.value.id
  caseDialogVisible.value = true
}

// 编辑用例
const handleEditCase = (row) => {
  isEditCase.value = true
  Object.assign(caseForm, row)
  caseDialogVisible.value = true
}

// 删除用例
const handleDeleteCase = async (row) => {
  ElMessageBox.confirm('确定要删除该测试用例吗？删除后将无法恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 调用删除API
      await deleteTestCase(row.id)
      ElMessage.success('测试用例已删除')
      loadTestCases(selectedSuite.value?.id)
    } catch (error) {
      console.error('删除测试用例失败:', error)
      ElMessage.error('删除测试用例失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 保存用例
const handleSaveCase = async () => {
  try {
    // 从caseForm中移除项目相关字段，这些字段将从所属套件继承
    const { project_id, version_requirement_id, iteration_id, ...caseData } = caseForm
    
    if (isEditCase.value) {
      // 编辑用例
      await updateTestCase(caseForm.id, caseData)
      ElMessage.success('测试用例已更新')
    } else {
      // 新增用例
      await createTestCase(caseData)
      ElMessage.success('测试用例已创建')
    }
    caseDialogVisible.value = false
    loadTestCases(selectedSuite.value?.id)
  } catch (error) {
    console.error('保存测试用例失败:', error)
    ElMessage.error(isEditCase.value ? '更新测试用例失败' : '创建测试用例失败')
  }
}

// 重置用例表单
const resetCaseForm = () => {
  caseForm.id = null
  caseForm.case_number = ''
  caseForm.case_name = ''
  caseForm.case_description = ''
  caseForm.priority = 'P1'
  caseForm.status = ''
  caseForm.suite_id = null
  caseForm.preconditions = ''
  caseForm.steps = ''
  caseForm.expected_result = ''
}

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'list' ? 'mindmap' : 'list'
}

// 用例内联编辑相关方法
const startCaseEdit = (row, field) => {
  editingCaseId.value = row.id
  editingField.value = field
  editingValue.value = row[field] || ''
}

const saveCaseEdit = async (row) => {
  try {
    const updatedData = {
      [editingField.value]: editingValue.value
    }
    
    // 调用实际的API更新测试用例
    await updateTestCase(row.id, updatedData)
    
    // 更新本地数据
    Object.assign(row, updatedData)
    
    ElMessage.success('测试用例已更新')
    
    // 重置编辑状态
    editingCaseId.value = null
    editingField.value = null
    editingValue.value = ''
  } catch (error) {
    console.error('更新测试用例失败:', error)
    ElMessage.error('更新测试用例失败')
  }
}

const cancelCaseEdit = () => {
  editingCaseId.value = null
  editingField.value = null
  editingValue.value = ''
}

const handleCellClick = () => {
  // 点击单元格时关闭编辑状态
  cancelCaseEdit()
}

// 切换选择模式
const toggleSelectionMode = () => {
  showSelection.value = true
  selectedCases.value = []
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

// 删除选中的用例
const handleDeleteSelection = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要删除的测试用例')
    return
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${selectedCases.value.length} 个测试用例吗？删除后将无法恢复。`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 批量删除用例
      const caseIds = selectedCases.value.map(caseItem => caseItem.id)
      await batchDeleteTestCases(caseIds)
      ElMessage.success('测试用例已删除')
      loadTestCases(selectedSuite.value?.id)
      showSelection.value = false
      selectedCases.value = []
    } catch (error) {
      console.error('删除测试用例失败:', error)
      ElMessage.error('删除测试用例失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 分页相关
const handleSizeChange = (size) => {
  pageSize.value = size
  loadTestCases(selectedSuite.value?.id)
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadTestCases(selectedSuite.value?.id)
}
</script>

<style lang="scss" scoped>
.test-case-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
  overflow-x: auto;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  
  .header-content {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
    
    .description {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
}

.main-content {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    flex-wrap: nowrap;
    min-width: 900px;
    
    .left-panel {
      min-width: 280px;
      max-width: 70%;
      width: fit-content;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
      transition: all 0.3s ease;
      flex-shrink: 0;
      
      .panel-header {
          padding: 12px 15px;
          border-bottom: 1px solid #f0f2f5;
          display: flex;
          align-items: center;
          gap: 8px;
          background-color: #fafafa;
          border-radius: 8px 8px 0 0;
          
          .el-input {
            flex: 1;
            min-width: 0;
            
            /* 增大搜索框 */
            --el-input-height: 32px;
          }
          
          .el-input__wrapper {
            font-size: 14px;
          }
          
          .el-input__inner {
            font-size: 14px;
            height: 32px;
            line-height: 32px;
          }
          
          .header-actions {
            display: flex;
            gap: 0px;
            align-items: center;
            flex-shrink: 0;
            width: fit-content;
          }
          
          .header-actions .el-button {
            padding: 4px;
            min-width: 28px;
            height: 28px;
            font-size: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
          }
        }
    
    .tree-container {
      flex: 1;
      padding: 15px 15px 15px 20px;
      overflow: auto;
      max-height: calc(100vh - 150px);
      background-color: #ffffff;
      width: fit-content;
      min-width: 100%;
    }
    
    /* 确保树节点内容不被截断 */
    :deep(.el-tree) {
      width: fit-content;
      min-width: 100%;
      font-size: 14px;
    }
    
    :deep(.el-tree-node) {
      white-space: nowrap;
    }
    
    :deep(.el-tree-node__content) {
      white-space: nowrap;
      height: 36px;
      line-height: 36px;
    }
    
    /* 增大展开收起图标 */
    :deep(.el-tree-node__expand-icon) {
      font-size: 16px;
      width: 24px;
      height: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    
    /* 增大节点图标 */
    .node-icon {
      font-size: 18px;
      margin-right: 8px;
    }
  }
  
  /* 父套件选择器样式 */
  .parent-suite-selector {
    .suite-tree-popover {
      .pop-footer {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #ebeef5;
      }
    }
  }
  
  .right-panel {
    flex: 1;
    min-width: 400px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    flex-shrink: 1;
    
    .panel-header {
      padding: 15px;
      border-bottom: 1px solid #e4e7ed;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      
      .header-content {
        flex: 1;
      }
      
      h3 {
        margin: 0 0 10px 0;
        font-size: 16px;
        font-weight: 600;
      }
      
      .suite-info {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 8px;
      }
      
      .info-item {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 14px;
      }
      
      .label {
        color: #909399;
        font-weight: 400;
      }
      
      .value {
        color: #303133;
        font-weight: 500;
      }
    }
    
    .case-list {
      flex: 1;
      padding: 15px;
      overflow: auto;
      
      .pagination {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
    
    .mindmap-view {
      flex: 1;
      padding: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }
}

/* 树形节点样式 */
.tree-node-content {
  display: flex;
  align-items: center;
  
  .node-icon {
    margin-right: 5px;
    font-size: 16px;
    color: #606266;
  }
  
  .case-count {
    margin-left: 5px;
    font-size: 12px;
    color: #909399;
  }
}

/* 选中节点样式 */
.tree-node-content.current-node {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 0 -8px;
}

.tree-node-content.current-node .node-icon {
  color: #409eff;
}

/* 右键菜单样式 */
.context-menu {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  
  .menu-item {
    padding: 8px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    
    &:hover {
      background-color: #f5f7fa;
    }
  }
}
</style>