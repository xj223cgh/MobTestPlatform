<template>
  <div class="test-case-management">
    <div class="page-header">
      <div class="header-content">
        <h1>测试用例管理</h1>
      </div>
      <div class="header-actions">
        <el-button
          v-if="!showSelection && viewMode === 'list'"
          type="danger"
          icon="Delete"
          @click="toggleSelectionMode"
        >
          选中删除
        </el-button>
        <el-button
          v-else-if="viewMode === 'list'"
          type="danger"
          icon="Delete"
          @click="handleDeleteSelection"
        >
          点击删除
        </el-button>
        <el-button
          v-if="showSelection && viewMode === 'list'"
          @click="cancelSelectionMode"
        >
          取消
        </el-button>
        
        <!-- 脑图视图切换按钮 -->
        <el-button
          type="success"
          icon="View"
          style="margin-right: 10px;"
          @click="toggleViewMode"
        >
          {{ viewMode === 'list' ? '脑图视图' : '列表视图' }}
        </el-button>
        
        <!-- 新增用例按钮 -->
        <el-button
          type="primary"
          icon="Plus"
          @click="handleAddCase"
        >
          新增用例
        </el-button>
        
        <!-- 评审按钮 -->
        <el-button
          v-if="selectedSuite && selectedSuite.type === 'suite'"
          type="warning"
          icon="Message"
          @click="handleReviewButtonClick"
        >
          {{ reviewButtonText }}
        </el-button>
        
        <!-- 导入/导出用例按钮 -->
        <el-button
          type="primary"
          icon="Download"
          @click="showImportExportDialog"
        >
          导入/导出
        </el-button>
      </div>
    </div>



    <div class="main-content">
      <!-- 左侧树形组件 -->
      <div
        class="left-panel"
        :class="{ collapsed: isLeftPanelCollapsed }"
      >
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
              circle
              title="刷新"
              @click="handleRefresh"
            />
            <el-button
              type="primary"
              size="small"
              icon="Plus"
              circle
              title="新增套件"
              @click="handleAddSuite"
            />
            <el-button
              size="small"
              :icon="isLeftPanelCollapsed ? 'ArrowRight' : 'ArrowLeft'"
              circle
              :title="isLeftPanelCollapsed ? '展开套件树' : '收起套件树'"
              @click="toggleLeftPanel"
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
            node-key="id"
            @node-click="handleNodeClick"
            @node-drop="handleNodeDrop"
            @node-contextmenu="handleContextMenu"
            @node-expand="handleNodeExpand"
            @node-collapse="handleNodeCollapse"
          >
            <template #default="{ node, data }">
              <span class="tree-node-content">
                <el-icon class="node-icon">
                  <Folder v-if="data.type === 'folder'" />
                  <Document v-else />
                </el-icon>
                <span
                  v-if="!editingNodeId || editingNodeId !== data.id"
                  @dblclick="startEdit(data)"
                >
                  {{ node.label }}
                </span>
                <el-input
                  v-else
                  ref="editInputRef"
                  v-model="editingNodeName"
                  size="small"
                  autofocus
                  @blur="saveEdit(data)"
                  @keyup.enter="saveEdit(data)"
                  @keyup.esc="cancelEdit"
                />

              </span>
            </template>
          </el-tree>
        </div>

        <!-- 右键菜单 -->
        <div
          v-show="contextMenuVisible"
          ref="contextMenuRef"
          :style="contextMenuStyle"
          class="context-menu"
        >
          <!-- 新增套件：只有在右键用例文件夹时才显示 -->
          <div
            v-if="selectedNode && selectedNode.type === 'folder'"
            class="menu-item"
            @click="handleAddSuiteFromMenu"
          >
            <el-icon><Plus /></el-icon> 新增套件
          </div>
          <!-- 编辑套件：只有在右键用例集时才显示 -->
          <div
            v-if="selectedNode && selectedNode.type === 'suite'"
            class="menu-item"
            @click="handleEditSuite"
          >
            <el-icon><Edit /></el-icon> 编辑套件
          </div>
          <!-- 删除套件：始终显示 -->
          <div
            class="menu-item"
            @click="handleDeleteSuite"
          >
            <el-icon><Delete /></el-icon> 删除套件
          </div>
        </div>
      </div>

      <!-- 右侧用例列表 -->
      <div class="right-panel">
        <div class="panel-header">
          <div class="header-content">
            <h3>
              {{ selectedSuite ? selectedSuite.suite_name : '用例列表' }} <span
                v-if="selectedSuite && selectedSuite.type === 'suite' && totalCases > 0"
                class="case-count-title"
              >(用例数: {{ totalCases }}条)</span>
            </h3>
            <div
              v-if="selectedSuite"
              class="suite-info"
            >
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
          
          <!-- 用例进度条 -->
          <div
            v-if="selectedSuite && selectedSuite.type === 'suite'"
            class="case-progress-container"
          >
            <div class="progress-wrapper">
              <!-- 进度条上方显示执行情况 -->
              <div class="progress-execution-info">
                用例执行进度：{{ executionRate }}%
              </div>
              <div class="progress-bar">
                <div
                  v-for="item in statusProgress"
                  :key="item.status"
                  class="progress-segment"
                  :class="`status-${item.status}`"
                  :style="{ width: `${item.percentage}%` }"
                  :title="`${item.label}: ${item.count}条 (${item.percentage}%)`"
                />
              </div>
              <!-- 进度数据显示在右侧末尾 -->
              <div class="progress-data-right">
                {{ notExecutedCount }}/{{ totalCases }}
              </div>
              <!-- 水平分布的属性标签 -->
              <div class="progress-labels-horizontal">
                <span
                  v-for="item in positionedLabels"
                  :key="item.status"
                  class="stat-item horizontal"
                  :class="`status-${item.status}`"
                >
                  {{ item.label }}: {{ item.count }} ({{ item.percentage }}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 用例列表 -->
        <div
          v-if="viewMode === 'list'"
          class="case-list"
        >
          <div class="table-wrapper">
            <el-table
              ref="caseTableRef"
              :data="testCases"
              style="width: 100%"
              border
              :row-style="{height: 'auto', textAlign: 'center'}"
              :cell-style="{padding: '10px', whiteSpace: 'normal', wordBreak: 'break-word', textAlign: 'center'}"
              :header-cell-style="{textAlign: 'center'}"
              row-key="id"
              @selection-change="handleSelectionChange"
              @select="handleSelect"
              @select-all="handleSelectAll"
            >
              <el-table-column
                v-if="showSelection"
                type="selection"
                width="55"
              />
              <el-table-column
                prop="case_number"
                label="编号"
                width="110"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'case_number'">
                    <el-input
                      v-model="editingValue"
                      autofocus
                      style="width: 100%"
                      @blur="saveCaseEdit(row)"
                      @keyup.enter="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    @dblclick="startCaseEdit(row, 'case_number')"
                  >
                    {{ row.case_number || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="case_name"
                label="用例名称"
                min-width="110"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'case_name'">
                    <el-input
                      v-model="editingValue"
                      autofocus
                      style="width: 100%"
                      @blur="saveCaseEdit(row)"
                      @keyup.enter="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    @dblclick="startCaseEdit(row, 'case_name')"
                  >
                    {{ row.case_name }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="priority"
                label="优先级"
                width="100"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'priority'">
                    <el-select
                      v-model="editingValue"
                      style="width: 100%"
                      @change="saveCaseEdit(row)"
                    >
                      <el-option
                        label="P0"
                        value="P0"
                      />
                      <el-option
                        label="P1"
                        value="P1"
                      />
                      <el-option
                        label="P2"
                        value="P2"
                      />
                      <el-option
                        label="P3"
                        value="P3"
                      />
                      <el-option
                        label="P4"
                        value="P4"
                      />
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
              <el-table-column
                prop="test_data"
                label="测试数据"
                min-width="90"
                align="left"
                header-align="left"
                :cell-style="{ textAlign: 'left' }"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'test_data'">
                    <el-input
                      v-model="editingValue"
                      type="textarea"
                      :rows="3"
                      autofocus
                      @blur="saveCaseEdit(row)"
                      @keyup.enter.ctrl="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    style="text-align: left"
                    @dblclick="startCaseEdit(row, 'test_data')"
                  >
                    {{ row.test_data || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="preconditions"
                label="前置条件"
                min-width="130"
                align="left"
                header-align="left"
                :cell-style="{ textAlign: 'left' }"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'preconditions'">
                    <el-input
                      v-model="editingValue"
                      type="textarea"
                      :rows="3"
                      autofocus
                      @blur="saveCaseEdit(row)"
                      @keyup.enter.ctrl="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    style="text-align: left"
                    @dblclick="startCaseEdit(row, 'preconditions')"
                  >
                    {{ row.preconditions || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="steps"
                label="操作步骤"
                min-width="140"
                align="left"
                header-align="left"
                :cell-style="{ textAlign: 'left' }"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'steps'">
                    <el-input
                      v-model="editingValue"
                      type="textarea"
                      :rows="5"
                      autofocus
                      @blur="saveCaseEdit(row)"
                      @keyup.enter.ctrl="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    style="text-align: left"
                    @dblclick="startCaseEdit(row, 'steps')"
                  >
                    {{ row.steps || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="expected_result"
                label="预期结果"
                min-width="130"
                align="left"
                header-align="left"
                :cell-style="{ textAlign: 'left' }"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'expected_result'">
                    <el-input
                      v-model="editingValue"
                      type="textarea"
                      :rows="3"
                      autofocus
                      @blur="saveCaseEdit(row)"
                      @keyup.enter.ctrl="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    style="text-align: left"
                    @dblclick="startCaseEdit(row, 'expected_result')"
                  >
                    {{ row.expected_result || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="actual_result"
                label="实际结果"
                min-width="130"
                align="left"
                header-align="left"
                :cell-style="{ textAlign: 'left' }"
              >
                <template #default="{ row }">
                  <template v-if="editingCaseId === row.id && editingField === 'actual_result'">
                    <el-input
                      v-model="editingValue"
                      type="textarea"
                      :rows="3"
                      autofocus
                      @blur="saveCaseEdit(row)"
                      @keyup.enter.ctrl="saveCaseEdit(row)"
                      @keyup.esc="cancelCaseEdit"
                    />
                  </template>
                  <div
                    v-else
                    style="text-align: left"
                    @dblclick="startCaseEdit(row, 'actual_result')"
                  >
                    {{ row.actual_result || '-' }}
                  </div>
                </template>
              </el-table-column>

              <el-table-column
                prop="status"
                label="状态"
                width="150"
              >
                <template #default="{ row }">
                  <div class="status-cell">
                    <el-select 
                      v-model="row.status" 
                      size="small" 
                      style="width: 90%"
                      :popper-class="'status-select-popper'"
                      placeholder="未执行"
                      @change="handleStatusChange(row)"
                    >
                      <template #prefix>
                        <span
                          class="status-color-indicator"
                          :class="'status-' + (row.status || 'none')"
                        />
                      </template>
                      <el-option 
                        v-for="option in statusOptions" 
                        :key="option.value" 
                        :label="option.label" 
                        :value="option.value"
                      >
                        <div class="status-option-content">
                          <span
                            class="status-color-indicator"
                            :class="'status-' + (option.value || 'none')"
                          />
                          <span class="status-option-text">{{ option.label }}</span>
                        </div>
                      </el-option>
                    </el-select>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 脑图视图（缺省页面） -->
        <div
          v-else
          class="mindmap-view"
        >
          <div class="mindmap-default-page">
            <el-empty
              description="脑图功能正在开发中，敬请期待"
              :image-size="200"
            >
              <el-button
                type="primary"
                @click="toggleViewMode"
              >
                返回列表视图
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
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

    <!-- 新增/编辑套件对话框 -->
    <el-dialog
      v-model="suiteDialogVisible"
      :title="isEditSuite ? '编辑测试套件' : '新增测试套件'"
      width="750px"
      @close="parentSuitePopoverVisible = false"
    >
      <el-form
        ref="suiteFormRef"
        :model="suiteForm"
        :rules="suiteFormRules"
        label-width="80px"
      >
        <el-form-item
          label="套件名称"
          prop="suite_name"
        >
          <el-input
            v-model="suiteForm.suite_name"
            placeholder="请输入测试套件名称"
          />
        </el-form-item>
        <el-form-item
          v-if="!isEditSuite"
          label="套件类型"
          prop="type"
        >
          <el-select
            v-model="suiteForm.type"
            placeholder="请选择套件类型"
          >
            <el-option
              label="用例文件夹"
              value="folder"
            />
            <el-option
              label="用例集"
              value="suite"
            />
          </el-select>
        </el-form-item>
        <!-- 父套件字段：只有非右键菜单操作时显示 -->
        <el-form-item
          v-if="!isContextMenuAction"
          label="父套件"
        >
          <div class="parent-suite-selector">
            <!-- 显示当前选中的父套件路径 -->
            <el-popover
              :visible="parentSuitePopoverVisible"
              placement="bottom-start"
              trigger="manual"
              width="auto"
              teleport="body"
              @clickoutside="parentSuitePopoverVisible = false"
            >
              <template #reference>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-input
                    v-model="selectedParentSuitePath"
                    placeholder="点击选择父套件（默认根套件）"
                    readonly
                    style="flex: 1; min-width: 568px;"
                    @click="parentSuitePopoverVisible = !parentSuitePopoverVisible"
                  />
                  <el-button
                    size="small"
                    style="height: 32px; margin-left: -2px;"
                    icon="Refresh"
                    title="重置选择"
                    @click.stop="clearParentSuiteSelection"
                  >
                    重置
                  </el-button>
                </div>
              </template>
              <!-- 弹出的套件树 -->
              <div
                class="suite-tree-popover"
                style="width: 100%; min-width: 543px;"
              >
                <el-tree
                  :current-node-key="suiteForm.parent_id"
                  :data="getFolderTreeData()"
                  :props="defaultProps"
                  node-key="id"
                  style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                  expand-on-click-node="false"
                  @node-click="handleParentSuiteSelect"
                >
                  <template #default="{ node, data }">
                    <span
                      class="tree-node-content"
                      :class="{'current-node': node.key === suiteForm.parent_id}"
                    >
                      <el-icon
                        class="node-icon"
                        @click.stop="handleParentSuiteSelect(data)"
                      >
                        <Folder />
                      </el-icon>
                      <span @click.stop="handleParentSuiteSelect(data)">{{ node.label }}</span>
                    </span>
                  </template>
                </el-tree>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        <el-form-item
          v-if="suiteForm.type === 'suite'"
          label="项目"
          prop="project_id"
        >
          <el-select
            v-model="suiteForm.project_id"
            placeholder="请选择所属项目"
            filterable
          >
            <template #empty>
              <div v-if="projects.length === 0">
                <span>暂无项目数据</span>
                <el-button
                  type="text"
                  size="small"
                  @click="loadProjects"
                >
                  重新加载
                </el-button>
              </div>
              <div v-else>
                未找到匹配的项目
              </div>
            </template>
            <el-option
              v-for="project in filteredProjects"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="suiteForm.type === 'suite'"
          label="迭代"
          prop="iteration_id"
        >
          <el-select
            v-model="suiteForm.iteration_id"
            placeholder="请选择所属迭代"
            :disabled="!suiteForm.project_id"
            filterable
          >
            <template #empty>
              <div v-if="!suiteForm.project_id">
                请先选择项目
              </div>
              <div v-else-if="iterations.length === 0">
                <span>暂无迭代数据</span>
                <el-button
                  type="text"
                  size="small"
                  @click="loadIterations(suiteForm.project_id)"
                >
                  重新加载
                </el-button>
              </div>
              <div v-else>
                未找到匹配的迭代
              </div>
            </template>
            <el-option
              v-for="iteration in filteredIterations"
              :key="iteration.id"
              :label="iteration.iteration_name"
              :value="iteration.id"
            />
          </el-select>
        </el-form-item> 
        <el-form-item
          v-if="suiteForm.type === 'suite'"
          label="需求"
          prop="version_requirement_id"
        >
          <el-select
            v-model="suiteForm.version_requirement_id"
            placeholder="请选择关联需求"
            :disabled="!suiteForm.iteration_id"
            filterable
          >
            <template #empty>
              <div v-if="!suiteForm.iteration_id">
                请先选择迭代
              </div>
              <div v-else-if="requirements.length === 0">
                <span>暂无需求数据</span>
                <el-button
                  type="text"
                  size="small"
                  @click="loadRequirements(suiteForm.project_id, suiteForm.iteration_id)"
                >
                  重新加载
                </el-button>
              </div>
              <div v-else>
                未找到匹配的需求
              </div>
            </template>
            <el-option
              v-for="requirement in filteredRequirements"
              :key="requirement.id"
              :label="requirement.requirement_name"
              :value="requirement.id"
            />
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
          <el-button @click="handleCancelSuite">取消</el-button>
          <el-button
            type="primary"
            @click="handleSaveSuite"
          >确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增/编辑用例对话框 -->
    <el-dialog
      v-model="caseDialogVisible"
      :title="isEditCase ? '编辑测试用例' : '新增测试用例'"
      width="700px"
      @close="caseSuitePopoverVisible = false"
    >
      <!-- 新增：创建方式选择 -->
      <div
        v-if="!isEditCase"
        class="create-type-selector"
      >
        <el-radio-group
          v-model="createCaseType"
          style="margin-bottom: 20px; display: flex; justify-content: center; gap: 20px;"
        >
          <el-radio label="manual">
            手动创建
          </el-radio>
          <el-radio label="auto">
            自动生成
          </el-radio>
        </el-radio-group>
      </div>
      
      <!-- 手动创建表单 -->
      <el-form
        v-if="isEditCase || createCaseType === 'manual'"
        ref="caseFormRef"
        :model="caseForm"
        :rules="caseFormRules"
        label-width="100px"
      >
        <el-form-item
          label="用例名称"
          prop="case_name"
          required
        >
          <el-input
            v-model="caseForm.case_name"
            placeholder="请输入测试用例名称"
          />
        </el-form-item>
        <el-form-item
          label="用例编号"
          prop="case_number"
        >
          <div class="case-number-input-group">
            <el-input
              v-model="caseNumberParts.part1"
              placeholder="编号前缀1"
              class="case-number-part"
              @input="updateCaseNumber"
            />
            <span class="case-number-separator">-</span>
            <el-input
              v-model="caseNumberParts.part2"
              placeholder="编号前缀2"
              class="case-number-part"
              @input="updateCaseNumber"
            />
            <span class="case-number-separator">-</span>
            <el-input
              v-model="caseNumberParts.part3"
              placeholder="编号前缀3"
              class="case-number-part"
              @input="updateCaseNumber"
            />
            <el-input
              v-model="caseNumberParts.part4"
              placeholder="001"
              class="case-number-part number-part"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              maxlength="3"
              @input="handleNumberInput"
            />
          </div>
        </el-form-item>
        <el-form-item
          label="所属用例集"
          prop="suite_id"
          required
        >
          <div class="case-suite-selector">
            <!-- 显示当前选中的用例集路径 -->
            <el-popover
              :visible="caseSuitePopoverVisible"
              placement="bottom-start"
              trigger="manual"
              width="auto"
              teleport="body"
              @clickoutside="caseSuitePopoverVisible = false"
            >
              <template #reference>
                <el-input
                  v-model="selectedCaseSuitePath"
                  placeholder="点击选择所属用例集"
                  readonly
                  style="width: 100%; min-width: 568px;"
                  @click="caseSuitePopoverVisible = !caseSuitePopoverVisible"
                />
              </template>
              <!-- 弹出的套件树 -->
              <div
                class="suite-tree-popover"
                style="width: 100%; min-width: 540px;"
              >
                <el-tree
                  :current-node-key="caseForm.suite_id"
                  :data="getSuiteTreeData()"
                  :props="defaultProps"
                  node-key="id"
                  style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                  expand-on-click-node="false"
                  @node-click="handleCaseSuiteSelect"
                >
                  <template #default="{ node, data }">
                    <span
                      class="tree-node-content"
                      :class="{'current-node': node.key === caseForm.suite_id}"
                    >
                      <el-icon
                        class="node-icon"
                        @click.stop="handleCaseSuiteSelect(data)"
                      >
                        <Document v-if="data.type === 'suite'" />
                        <Folder v-else />
                      </el-icon>
                      <span @click.stop="handleCaseSuiteSelect(data)">{{ node.label }}</span>
                      <span
                        v-if="data.type === 'suite' && data.cases_count > 0"
                        class="case-count"
                      >({{ data.cases_count }})</span>
                    </span>
                  </template>
                </el-tree>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        <el-form-item
          label="优先级"
          required
        >
          <el-select
            v-model="caseForm.priority"
            placeholder="请选择优先级"
          >
            <el-option
              label="P0"
              value="P0"
            />
            <el-option
              label="P1"
              value="P1"
            />
            <el-option
              label="P2"
              value="P2"
            />
            <el-option
              label="P3"
              value="P3"
            />
            <el-option
              label="P4"
              value="P4"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="caseForm.status"
            placeholder="默认未执行"
          >
            <el-option
              label="未执行"
              value=""
            />
            <el-option
              label="通过"
              value="pass"
            />
            <el-option
              label="失败"
              value="fail"
            />
            <el-option
              label="阻塞"
              value="blocked"
            />
            <el-option
              label="不适用"
              value="not_applicable"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试数据">
          <el-input
            v-model="caseForm.test_data"
            type="textarea"
            :rows="2"
            placeholder="请输入测试数据"
          />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input
            v-model="caseForm.preconditions"
            type="textarea"
            :rows="2"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input
            v-model="caseForm.steps"
            type="textarea"
            :rows="4"
            placeholder="请输入测试步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input
            v-model="caseForm.expected_result"
            type="textarea"
            :rows="2"
            placeholder="请输入预期结果"
          />
        </el-form-item>
        <el-form-item label="实际结果">
          <el-input
            v-model="caseForm.actual_result"
            type="textarea"
            :rows="2"
            placeholder="请输入实际结果"
          />
        </el-form-item>
      </el-form>
      
      <!-- 自动生成表单 -->
      <el-form
        v-else-if="createCaseType === 'auto'"
        ref="autoCaseFormRef"
        :model="autoCaseForm"
        :rules="autoCaseFormRules"
        label-width="100px"
      >
        <el-form-item
          label="用例名称"
          prop="case_name"
          required
        >
          <el-input
            v-model="autoCaseForm.case_name"
            placeholder="请输入测试用例名称"
          />
        </el-form-item>
        
        <el-form-item
          label="所属用例集"
          prop="suite_id"
          required
        >
          <div class="case-suite-selector">
            <!-- 显示当前选中的用例集路径 -->
            <el-popover
              :visible="caseSuitePopoverVisible"
              placement="bottom-start"
              trigger="manual"
              width="auto"
              teleport="body"
              @clickoutside="caseSuitePopoverVisible = false"
            >
              <template #reference>
                <el-input
                  v-model="selectedCaseSuitePath"
                  placeholder="点击选择所属用例集"
                  readonly
                  style="width: 100%; min-width: 568px;"
                  @click="caseSuitePopoverVisible = !caseSuitePopoverVisible"
                />
              </template>
              <!-- 弹出的套件树 -->
              <div
                class="suite-tree-popover"
                style="width: 100%; min-width: 540px;"
              >
                <el-tree
                  :current-node-key="autoCaseForm.suite_id"
                  :data="getSuiteTreeData()"
                  :props="defaultProps"
                  node-key="id"
                  style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                  expand-on-click-node="false"
                  @node-click="handleAutoCaseSuiteSelect"
                >
                  <template #default="{ node, data }">
                    <span
                      class="tree-node-content"
                      :class="{'current-node': node.key === autoCaseForm.suite_id}"
                    >
                      <el-icon
                        class="node-icon"
                        @click.stop="handleAutoCaseSuiteSelect(data)"
                      >
                        <Document v-if="data.type === 'suite'" />
                        <Folder v-else />
                      </el-icon>
                      <span @click.stop="handleAutoCaseSuiteSelect(data)">{{ node.label }}</span>
                      <span
                        v-if="data.type === 'suite' && data.cases_count > 0"
                        class="case-count"
                      >({{ data.cases_count }})</span>
                    </span>
                  </template>
                </el-tree>
              </div>
            </el-popover>
          </div>
        </el-form-item>
        
        <el-form-item
          label="需求描述"
          prop="requirement_desc"
        >
          <el-input
            v-model="autoCaseForm.requirement_desc"
            type="textarea"
            :rows="4"
            placeholder="请输入需求描述"
          />
        </el-form-item>
        
        <el-form-item
          label="需求文档上传"
        >
          <el-upload
            ref="requirementUploadRef"
            :auto-upload="false"
            :headers="{ 'Content-Type': 'multipart/form-data' }"
            accept=".docx,.pdf,.txt"
            :on-change="handleRequirementFileChange"
            :file-list="requirementFileList"
            :on-remove="handleRequirementFileRemove"
            :limit="1"
            :on-exceed="handleRequirementFileExceed"
          >
            <el-button type="primary">
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传.docx、.pdf和.txt格式的文件，大小不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCancelCase">取消</el-button>
          <el-button
            v-if="createCaseType === 'auto'"
            type="primary"
            @click="handleGenerateCase"
          >生成用例</el-button>
          <el-button
            v-if="isEditCase || createCaseType === 'manual'"
            type="primary"
            @click="handleSaveCase"
          >确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 导入/导出用例对话框 -->
    <el-dialog
      v-model="importExportVisible"
      title="导入/导出用例"
      width="800px"
    >
      <el-form
        ref="importExportFormRef"
        :model="importExportForm"
        label-width="100px"
      >
        <!-- 类型选择 -->
        <el-form-item label="操作类型">
          <el-radio-group v-model="importExportForm.type">
            <el-radio label="import">
              导入
            </el-radio>
            <el-radio label="export">
              导出
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 导入选项 -->
        <template v-if="importExportForm.type === 'import'">
          <!-- 本地文件上传 -->
          <el-form-item label="本地文件">
            <el-upload
              ref="importUploadRef"
              :auto-upload="false"
              :headers="{ 'Content-Type': 'multipart/form-data' }"
              accept=".xlsx, .xls"
              :on-change="handleFileChange"
              :file-list="fileList"
              :on-remove="handleFileRemove"
              :limit="1"
              :on-exceed="handleFileExceed"
              class="upload-with-clear"
            >
              <el-button type="primary">
                选择文件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传.xlsx和.xls格式的文件，大小不超过10MB
                </div>
                <div class="form-help-text">
                  注意：导入的用例需要手动编辑以关联所属项目、迭代和需求
                </div>
              </template>
            </el-upload>
          </el-form-item>
          
          <!-- 目标位置 -->
          <el-form-item label="目标位置">
            <div class="parent-suite-selector">
              <!-- 显示当前选中的父套件路径 -->
              <el-popover
                :visible="importParentSuiteVisible"
                placement="bottom-start"
                trigger="manual"
                width="auto"
                teleport="body"
                @clickoutside="importParentSuiteVisible = false"
              >
                <template #reference>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-input
                      v-model="importSelectedParentSuitePath"
                      placeholder="点击选择父套件（默认根套件）"
                      readonly
                      style="flex: 1; min-width: 568px;"
                      @click="importParentSuiteVisible = !importParentSuiteVisible"
                    />
                    <el-button
                      size="small"
                      style="height: 32px; margin-left: -2px;"
                      icon="Refresh"
                      title="重置选择"
                      @click.stop="clearImportParentSuiteSelection"
                    >
                      重置
                    </el-button>
                  </div>
                </template>
                <!-- 弹出的套件树 -->
                <div
                  class="suite-tree-popover"
                  style="width: 100%; min-width: 543px;"
                >
                  <el-tree
                    :current-node-key="importExportForm.parent_id"
                    :data="getFolderTreeData()"
                    :props="defaultProps"
                    node-key="id"
                    expand-on-click-node="false"
                    @node-click="handleImportParentSuiteSelect"
                  >
                    <template #default="{ node, data }">
                      <span class="tree-node-content">
                        <el-icon class="node-icon">
                          <Folder />
                        </el-icon>
                        <span @click.stop="handleImportParentSuiteSelect(data)">{{ node.label }}</span>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-popover>
            </div>
          </el-form-item>
        </template>
        
        <!-- 导出选项 -->
        <template v-else-if="importExportForm.type === 'export'">
          <!-- 导出的用例集 -->
          <el-form-item label="导出的用例集">
            <div class="case-suite-selector">
              <!-- 显示当前选中的用例集路径 -->
              <el-popover
                :visible="exportCaseSuiteVisible"
                placement="bottom-start"
                trigger="manual"
                width="auto"
                teleport="body"
                @clickoutside="exportCaseSuiteVisible = false"
              >
                <template #reference>
                  <el-input
                    v-model="exportSelectedCaseSuitePath"
                    placeholder="点击选择所属用例集"
                    readonly
                    style="width: 100%; min-width: 568px;"
                    @click="exportCaseSuiteVisible = !exportCaseSuiteVisible"
                  />
                </template>
                <!-- 弹出的套件树 -->
                <div
                  class="suite-tree-popover"
                  style="width: 100%; min-width: 543px;"
                >
                  <el-tree
                    :current-node-key="importExportForm.suite_id"
                    :data="treeData"
                    :props="defaultProps"
                    node-key="id"
                    expand-on-click-node="false"
                    @node-click="handleExportCaseSuiteSelect"
                  >
                    <template #default="{ node, data }">
                      <span class="tree-node-content">
                        <el-icon class="node-icon">
                          <Folder v-if="data.type === 'folder'" />
                          <Document v-else />
                        </el-icon>
                        <span @click.stop="handleExportCaseSuiteSelect(data)">{{ node.label }}</span>
                        <span
                          v-if="data.type === 'suite' && data.cases_count > 0"
                          class="case-count"
                        >({{ data.cases_count }})</span>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-popover>
            </div>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importExportVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="isImporting"
            :disabled="isImporting"
            @click="handleImportExportAction"
          >
            {{ importExportForm.type === 'import' ? '导入' : '导出' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 发起评审对话框 -->
    <el-dialog
      v-model="initiateReviewVisible"
      title="发起用例集评审"
      width="650px"
    >
      <el-form
        ref="reviewFormRef"
        :model="reviewForm"
        :rules="reviewFormRules"
        label-width="100px"
      >
        <el-form-item
          label="所属用例集"
          prop="suite_id"
        >
          <div class="case-suite-selector">
            <!-- 显示当前选中的用例集路径 -->
            <el-popover
              :visible="reviewSuitePopoverVisible"
              placement="bottom-start"
              trigger="manual"
              width="auto"
              teleport="body"
              @clickoutside="reviewSuitePopoverVisible = false"
            >
              <template #reference>
                <el-input
                  v-model="reviewSuitePath"
                  placeholder="点击选择所属用例集"
                  readonly
                  style="width: 518px;"
                  @click="reviewSuitePopoverVisible = !reviewSuitePopoverVisible"
                />
              </template>
              <!-- 弹出的套件树 -->
              <div
                class="suite-tree-popover"
                style="width: 100%; min-width: 490px;"
              >
                <el-tree
                  :current-node-key="reviewForm.suite_id"
                  :data="getSuiteTreeData()"
                  :props="defaultProps"
                  node-key="id"
                  style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                  expand-on-click-node="false"
                  @node-click="handleReviewSuiteSelect"
                >
                  <template #default="{ node, data }">
                    <span
                      class="tree-node-content"
                      :class="{'current-node': node.key === reviewForm.suite_id}"
                    >
                      <el-icon
                        class="node-icon"
                        @click.stop="handleReviewSuiteSelect(data)"
                      >
                        <Document v-if="data.type === 'suite'" />
                        <Folder v-else />
                      </el-icon>
                      <span @click.stop="handleReviewSuiteSelect(data)">{{ node.label }}</span>
                      <span
                        v-if="data.type === 'suite' && data.cases_count > 0"
                        class="case-count"
                      >({{ data.cases_count }})</span>
                    </span>
                  </template>
                </el-tree>
              </div>
            </el-popover>
          </div>
        </el-form-item>

        <el-form-item
          label="评审人"
          prop="reviewer_id"
        >
          <el-select
            v-model="reviewForm.reviewer_id"
            placeholder="请选择评审人"
            filterable
          >
            <el-option
              v-for="user in reviewerOptions"
              :key="user.id"
              :label="user.real_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="initiateReviewVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleInitiateReview"
          >发起评审</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 评审详情/提示对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewDialogTitle"
      width="90%"
      :fullscreen="false"
    >
      <!-- 提示消息类型 -->
      <div
        v-if="reviewDialogType === 'message'"
        class="review-message-content"
      >
        <el-icon
          size="48"
          class="message-icon"
        >
          <InfoFilled />
        </el-icon>
        <p class="message-text">
          {{ reviewDialogContent }}
        </p>
      </div>
      <!-- 详情页面类型 -->
      <div
        v-else-if="currentReviewTask"
        class="review-detail-content"
      >
        <!-- 评审任务基本信息 -->
        <div class="dialog-section">
          <h4>评审任务信息</h4>
          <el-descriptions
            :column="2"
            border
          >
            <el-descriptions-item label="用例集名称">
              {{ currentReviewTask?.suite?.suite_name || currentReviewTask?.suite_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="发起人">
              {{ currentReviewTask?.initiator_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="评审人">
              {{ currentReviewTask?.reviewer_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(currentReviewTask?.created_at) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatDate(currentReviewTask?.start_time) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ formatDate(currentReviewTask?.end_time) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item
              label="评审状态"
              :span="2"
            >
              <el-tag :type="getStatusTagType(currentReviewTask?.status)">
                {{ getStatusText(currentReviewTask?.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 用例评审列表 -->
        <div class="dialog-section">
          <h4>用例评审列表</h4>
          <el-table 
            v-if="currentReviewTask.case_reviews && currentReviewTask.case_reviews.length > 0"
            :data="currentReviewTask.case_reviews"
            style="width: 100%"
            row-key="id"
            max-height="400"
            :row-style="{ height: 'auto' }"
            :cell-style="{ 'white-space': 'pre-wrap', 'word-break': 'break-word', 'line-height': '1.5' }"
          >
            <el-table-column
              label="用例编号"
              min-width="130"
            >
              <template #default="scope">
                {{ scope.row.case_number || scope.row.test_case?.case_number || '-' }}
              </template>
            </el-table-column>
            <el-table-column
              label="用例名称"
              min-width="140"
            >
              <template #default="scope">
                {{ scope.row.case_name || scope.row.test_case?.case_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column
              label="优先级"
              width="90"
            >
              <template #default="scope">
                <el-tag 
                  :type="getPriorityTagType(scope.row.priority || scope.row.test_case?.priority || 'P3')"
                  size="small"
                >
                  {{ scope.row.priority || scope.row.test_case?.priority || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="评审状态"
              width="100"
            >
              <template #default="scope">
                <el-tag 
                  :type="getCaseReviewStatusTagType(scope.row.review_status)"
                >
                  {{ getCaseReviewStatusText(scope.row.review_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="测试数据"
              min-width="150"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.test_case?.test_data || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="前置条件"
              min-width="150"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.test_case?.preconditions || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="测试步骤"
              min-width="200"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.test_case?.steps || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="预期结果"
              min-width="150"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.test_case?.expected_result || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="实际结果"
              min-width="150"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.test_case?.actual_result || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="评审意见"
              min-width="200"
            >
              <template #default="scope">
                <div class="read-only-comments">
                  {{ scope.row.comments || '-' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="评审时间"
              width="150"
            >
              <template #default="scope">
                {{ formatDate(scope.row.updated_at) || '-' }}
              </template>
            </el-table-column>
          </el-table>
          <div
            v-else
            class="no-data"
          >
            <p>暂无评审数据</p>
          </div>
        </div>
        
        <!-- 整体评审意见 -->
        <div class="dialog-section">
          <h4>整体评审意见</h4>
          <div class="read-only-comments">
            {{ currentReviewTask.overall_comments || '暂无整体评审意见' }}
          </div>
        </div>
      </div>
      <div
        v-else
        class="review-detail-content"
      >
        <p>正在加载评审详情...</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 隐藏的文件上传组件 -->
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :headers="{ 'Content-Type': 'multipart/form-data' }"
      accept=".xlsx, .xls"
      :before-upload="(file) => {
        const isExcel = file.type === 'application/vnd.ms-excel' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        const isLt10M = file.size / 1024 / 1024 < 10
        
        if (!isExcel) {
          ElMessage.error('只能上传Excel文件！')
          return false
        }
        if (!isLt10M) {
          ElMessage.error('上传文件大小不能超过 10MB！')
          return false
        }
        
        excelFile.value = file
        // 手动处理文件
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            const data = new Uint8Array(e.target.result)
            const workbook = XLSX.read(data, { type: 'array' })
            const sheetName = workbook.SheetNames[0]
            const worksheet = workbook.Sheets[sheetName]
            
            // 解析Excel数据
            const excelData = XLSX.utils.sheet_to_json(worksheet)
            
            if (excelData.length === 0) {
              ElMessage.warning('Excel文件中没有测试用例数据')
              return
            }
            
            // 获取目标用例集详情，获取项目相关信息
            if (!importExportForm.parent_id) {
              ElMessage.error('请选择导入的目标位置')
              return
            }
            
            const suiteDetail = await getTestSuiteDetail(importExportForm.parent_id)
            
            // 处理导入的数据
            let importedCount = 0
            let errorCount = 0
            
            // 遍历处理每条数据
            for (const item of excelData) {
              try {
                // 将中文状态转换为对应的状态值
                const statusValue = statusOptions.find(option => option.label === item['状态'])?.value || ''
                
                // 构建完整的用例数据
                const caseData = {
                  case_number: item['用例编号'] || '',
                  case_name: item['用例名称'] || '',
                  priority: item['优先级'] || 'P1',
                  status: statusValue,
                  preconditions: item['前置条件'] || '',
                  test_data: item['测试数据'] || '',
                  steps: item['操作步骤'] || '',
                  expected_result: item['预期结果'] || '',
                  actual_result: item['实际结果'] || '',
                  suite_id: importExportForm.parent_id,
                  project_id: suiteDetail.data.project_id,
                  version_requirement_id: suiteDetail.data.version_requirement_id,
                  iteration_id: suiteDetail.data.iteration_id,
                  // 其他字段根据实际需求添加
                  // 评审人id和时间属性会由后端自动处理，这里可以根据实际情况添加
                  // reviewer_id: ...,
                  // created_at: new Date().toISOString(),
                  // updated_at: new Date().toISOString()
                }
                
                // 调用API创建测试用例
                await createTestCase(caseData)
                importedCount++
              } catch (error) {
                console.error('导入单条测试用例失败:', error)
                errorCount++
              }
            }
            
            // 显示导入结果
            ElMessage.success(`成功导入 ${importedCount} 条测试用例，失败 ${errorCount} 条`)
            
            // 刷新用例列表
            if (selectedSuite.value && selectedSuite.value.type === 'suite') {
              loadTestCases(selectedSuite.value.id)
            }
            
            // 关闭对话框
            importExportVisible.value = false
          } catch (error) {
            console.error('导入测试用例失败:', error)
            ElMessage.error('导入测试用例失败，请检查文件格式和内容')
          }
        }
        reader.readAsArrayBuffer(file.raw)
        
        return false // 阻止自动上传
      }"
      style="display: none"
    >
      <el-button
        ref="uploadBtnRef"
        type="primary"
      >
        上传
      </el-button>
    </el-upload>
  </div>
</template>



<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElUpload, ElButton, ElLoading } from 'element-plus'
import { Folder, Document, ArrowDown, ArrowUp, Download, Upload, DocumentCopy } from '@element-plus/icons-vue'
import { getTestSuiteTree, getSuiteCases, createTestSuite, updateTestSuite, deleteTestSuite } from '@/api/testSuite'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { useUserStore } from '@/stores/user'

// API导入
import { updateTestCase, createTestCase, deleteTestCase, batchDeleteTestCases } from '@/api/testCase'
import { getTestSuiteDetail } from '@/api/testSuite'
import { getProjects, getProjectIterations, getProjectVersionRequirements } from '@/api/project'
import { initiateReview, getSuiteReviewStatus, getReviewTask, getCaseReviews } from '@/api/reviewTask'
import { getUserList } from '@/api/user'

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
// 标识是否是从右键菜单触发的操作
const isContextMenuAction = ref(false)

// 表单数据
const suiteForm = reactive({
  id: null,
  suite_name: '',
  description: '',
  type: 'folder', // 默认类型为文件夹
  parent_id: null,
  project_id: null, // 默认项目ID，实际应从上下文获取
  version_requirement_id: null,
  iteration_id: null
})

// 存储套件选项，用于父级套件选择
const suiteOptions = ref([])

// 套件表单引用和验证规则
const suiteFormRef = ref(null)

// 标记是否正在初始化表单，用于控制观察者行为
const isInitializingForm = ref(false)
const suiteFormRules = reactive({
  suite_name: [
    { required: true, message: '请输入测试套件名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择套件类型', trigger: 'change' }
  ],
  project_id: [
    {
      required: (rule, value, callback) => {
        // 只有用例集类型才需要选择项目
        return suiteForm.type === 'suite'
      },
      message: '请选择所属项目',
      trigger: 'change'
    }
  ],
  iteration_id: [
    {
      required: (rule, value, callback) => {
        // 只有用例集类型才需要选择迭代
        return suiteForm.type === 'suite'
      },
      message: '请选择所属迭代',
      trigger: 'change'
    }
  ],
  version_requirement_id: [
    {
      required: (rule, value, callback) => {
        // 只有用例集类型才需要选择需求
        return suiteForm.type === 'suite'
      },
      message: '请选择关联需求',
      trigger: 'change'
    }
  ]
})

// 项目、迭代、需求列表
const projects = ref([])
const iterations = ref([])
const requirements = ref([])

// 搜索关键词
const searchKeywords = reactive({
  project: '',
  iteration: '',
  requirement: ''
})

// 过滤后的列表（计算属性）
const filteredProjects = computed(() => {
  if (!searchKeywords.project) {
    return projects.value
  }
  return projects.value.filter(project => 
    project.project_name.includes(searchKeywords.project)
  )
})

const filteredIterations = computed(() => {
  if (!searchKeywords.iteration) {
    return iterations.value
  }
  return iterations.value.filter(iteration => 
    iteration.iteration_name.includes(searchKeywords.iteration)
  )
})

const filteredRequirements = computed(() => {
  if (!searchKeywords.requirement) {
    return requirements.value
  }
  return requirements.value.filter(requirement => 
    requirement.requirement_name.includes(searchKeywords.requirement)
  )
})

// 用例集选择相关
const caseSuitePopoverVisible = ref(false)
const selectedCaseSuitePath = ref('')
const caseFormRef = ref(null)

// 新增：创建方式选择
const createCaseType = ref('manual')

// 自动生成用例表单相关
const autoCaseFormRef = ref(null)
const autoCaseForm = reactive({
  case_name: '',
  suite_id: null,
  requirement_desc: '',
  file: null
})

const autoCaseFormRules = reactive({
  case_name: [
    { required: true, message: '请输入测试用例名称', trigger: 'blur' }
  ],
  suite_id: [
    { required: true, message: '请选择所属用例集', trigger: 'change' }
  ]
})

// 需求文档上传相关
const requirementUploadRef = ref(null)
const requirementFileList = ref([])

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
  expected_result: '',
  test_data: '',
  actual_result: ''
})

// 用例编号分段输入
const caseNumberParts = reactive({
  part1: '',
  part2: '',
  part3: '',
  part4: ''
})

// 更新用例编号
const updateCaseNumber = () => {
  // 确保数字部分是1-999之间的整数
  let numberPart = caseNumberParts.part4 ? parseInt(caseNumberParts.part4) : 1
  // 确保数字在1-999之间
  if (isNaN(numberPart) || numberPart < 1) {
    numberPart = 1
  } else if (numberPart > 999) {
    numberPart = 999
  }
  // 确保数字部分是3位格式
  const formattedNumber = numberPart.toString().padStart(3, '0')
  
  // 生成用例编号，确保格式正确
  // 如果三个前缀都为空，使用默认格式
  if (!caseNumberParts.part1 && !caseNumberParts.part2 && !caseNumberParts.part3) {
    // 默认格式：CASE-001-001
    caseForm.case_number = `CASE-001-${formattedNumber}`
  } else {
    // 正常格式：xxx-xxx-xxx001
    caseForm.case_number = `${caseNumberParts.part1}-${caseNumberParts.part2}-${caseNumberParts.part3}${formattedNumber}`
  }
}

// 处理数字输入框输入
const handleNumberInput = () => {
  // 过滤掉非数字字符
  let inputValue = caseNumberParts.part4.replace(/[^0-9]/g, '')
  
  // 限制输入长度为3位
  if (inputValue.length > 3) {
    inputValue = inputValue.slice(0, 3)
  }
  
  // 确保输入的是数字，且在1-999之间
  let num = parseInt(inputValue) || 1
  if (num < 1) {
    num = 1
  } else if (num > 999) {
    num = 999
  }
  
  // 格式化为3位数字，前面补0
  caseNumberParts.part4 = num.toString().padStart(3, '0')
  
  // 更新用例编号
  updateCaseNumber()
}

// 表单验证规则
const caseFormRules = reactive({
  case_name: [
    { required: true, message: '请输入测试用例名称', trigger: 'blur' }
  ],
  case_number: [
    { required: true, message: '请输入测试用例编号', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        // 验证用例编号格式: XXX-XXX-XXX001~XXX-XXX-XXX999
        const regex = /^.+-.+-.+\d{3}$/
        if (!regex.test(value)) {
          callback(new Error('用例编号格式不正确，应为: XXX-XXX-XXX001~XXX-XXX-XXX999'))
        } else {
          // 验证数字部分在1-999之间
          const numRegex = /\d{3}$/
          const match = value.match(numRegex)
          if (match) {
            const num = parseInt(match[0])
            if (num < 1 || num > 999) {
              callback(new Error('用例编号数字部分必须在001-999之间'))
            } else {
              callback()
            }
          } else {
            callback(new Error('用例编号格式不正确，应为：xxx-xxx-xxx001~xxx-xxx-xxx999'))
          }
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  suite_id: [
    { required: true, message: '请选择所属用例集', trigger: 'change' }
  ]
})

// 用例列表相关
const selectedSuite = ref(null)
const testCases = ref([]) // 当前页数据
const allTestCases = ref([]) // 所有数据
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
// 使用Set存储选中的用例ID，实现跨分页选择
const selectedCaseIds = ref(new Set())

// 发起评审相关
const initiateReviewVisible = ref(false)
const reviewFormRef = ref(null)
const reviewSuitePopoverVisible = ref(false)
const reviewSuitePath = ref('')
const reviewForm = reactive({
  suite_id: null,
  suite_name: '',
  reviewer_id: null
})
const reviewFormRules = reactive({
  suite_id: [
    { required: true, message: '请选择所属用例集', trigger: 'change' }
  ],
  reviewer_id: [
    { required: true, message: '请选择评审人', trigger: 'change' }
  ]
})
// 评审人选项，从API获取
const reviewerOptions = ref([])

// 评审状态相关
const userStore = useUserStore()
const router = useRouter()
const suiteReviewStatus = ref(null)
const isLoadingReviewStatus = ref(false)
const reviewButtonText = ref('发起评审')
const reviewDialogVisible = ref(false)
const reviewDialogTitle = ref('')
const reviewDialogContent = ref('')
const reviewDialogType = ref('detail') // detail: 详情页面, message: 提示消息
const currentReviewTask = ref(null)

// 获取评审人列表
const loadReviewers = async () => {
  try {
    const response = await getUserList()
    reviewerOptions.value = response.data.users || []
  } catch (error) {
    console.error('获取评审人列表失败:', error)
    ElMessage.error('获取评审人列表失败，请稍后重试')
  }
}

// 获取用例集路径
const getSuitePath = (suiteId, separator = ' / ') => {
  let path = ''
  let currentId = suiteId
  const findPath = (node, id) => {
    if (node.id === id) {
      path = node.suite_name + (path ? separator + path : '')
      return true
    }
    if (node.children && node.children.length > 0) {
      for (const child of node.children) {
        if (findPath(child, id)) {
          path = node.suite_name + separator + path
          return true
        }
      }
    }
    return false
  }
  
  // 遍历所有根节点
  for (const root of treeData.value) {
    if (findPath(root, currentId)) {
      break
    }
  }
  
  return path
}

// 处理评审用例集选择
const handleReviewSuiteSelect = (data) => {
  if (data.type === 'suite') {
    reviewForm.suite_id = data.id
    reviewForm.suite_name = data.suite_name
    reviewSuitePath.value = getSuitePath(data.id)
    reviewSuitePopoverVisible.value = false
  }
}

// 显示发起评审对话框
const showInitiateReviewDialog = () => {
  if (selectedSuite.value && selectedSuite.value.type === 'suite') {
    reviewForm.suite_id = selectedSuite.value.id
    reviewForm.suite_name = selectedSuite.value.suite_name
    reviewSuitePath.value = getSuitePath(selectedSuite.value.id)
    reviewForm.reviewer_id = null
    initiateReviewVisible.value = true
  }
}

// 处理发起评审
const handleInitiateReview = async () => {
  if (!reviewFormRef.value) return
  
  await reviewFormRef.value.validate()
  
  try {
    // 调用发起评审API（不需要description参数）
    await initiateReview(reviewForm.suite_id, {
      reviewer_id: reviewForm.reviewer_id
    })
    
    ElMessage.success('发起评审成功')
    initiateReviewVisible.value = false
    
    // 刷新用例集信息，可能需要更新评审状态
    loadTreeData()
  } catch (error) {
    console.error('发起评审失败:', error)
    ElMessage.error('发起评审失败，请稍后重试')
  }
}

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

// 获取用例集评审状态
const getSuiteReviewStatusData = async (suiteId) => {
  isLoadingReviewStatus.value = true
  try {
    const response = await getSuiteReviewStatus(suiteId)
    suiteReviewStatus.value = response.data
    updateReviewButtonText()
  } catch (error) {
    console.error('获取用例集评审状态失败:', error)
    suiteReviewStatus.value = null
    updateReviewButtonText()
  } finally {
    isLoadingReviewStatus.value = false
  }
}

// 更新评审按钮文本
const updateReviewButtonText = () => {
  if (!selectedSuite.value || selectedSuite.value.type !== 'suite') {
    reviewButtonText.value = '发起评审'
    return
  }
  
  // 获取评审状态和相关信息
  const status = suiteReviewStatus.value?.current_status || 'not_submitted'
  const reviewerId = suiteReviewStatus.value?.current_reviewer_id
  const isCreator = userStore.userInfo && userStore.userInfo.id === selectedSuite.value.creator_id
  const isReviewer = userStore.userInfo && userStore.userInfo.id === reviewerId
  
  // 根据用户角色和评审状态更新按钮文本
  if (isCreator) {
    // 作为评审发起人
    if (status === 'not_submitted') {
      reviewButtonText.value = '发起评审'
    } else if (status === 'pending') {
      reviewButtonText.value = '评审待处理'
    } else if (status === 'in_review') {
      reviewButtonText.value = '等待评审中'
    } else if (status === 'approved' || status === 'completed') {
      reviewButtonText.value = '查看评审'
    } else if (status === 'rejected') {
      reviewButtonText.value = '重新发起评审'
    }
  } else if (isReviewer) {
    // 作为评审人
    if (status === 'not_submitted') {
      reviewButtonText.value = '暂未发起评审'
    } else if (status === 'pending') {
      reviewButtonText.value = '开始评审'
    } else if (status === 'in_review') {
      reviewButtonText.value = '继续评审'
    } else if (status === 'approved' || status === 'completed' || status === 'rejected') {
      reviewButtonText.value = '查看评审'
    }
  } else {
    // 作为其他用户
    if (status === 'not_submitted') {
      reviewButtonText.value = '暂未发起评审'
    } else if (status === 'pending') {
      reviewButtonText.value = '评审待处理'
    } else if (status === 'in_review') {
      reviewButtonText.value = '等待评审中'
    } else {
      reviewButtonText.value = '查看评审'
    }
  }
}

// 获取评审详情数据
// 辅助方法：格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 辅助方法：获取评审任务状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'warning',
    in_review: 'primary',
    completed: 'success',
    rejected: 'danger',
    not_submitted: 'info'
  }
  return typeMap[status] || 'info'
}

// 辅助方法：获取评审任务状态文本
const getStatusText = (status) => {
  const textMap = {
    pending: '待评审',
    in_review: '评审中',
    completed: '已完成',
    rejected: '已拒绝',
    not_submitted: '未提交'
  }
  return textMap[status] || '未知状态'
}

// 辅助方法：获取优先级标签类型
const getPriorityTagType = (priority) => {
  const typeMap = {
    P0: 'danger',
    P1: 'danger',
    P2: 'warning',
    P3: 'info',
    P4: 'success'
  }
  return typeMap[priority] || 'info'
}

// 辅助方法：获取用例评审状态标签类型
const getCaseReviewStatusTagType = (status) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    pending: 'warning',
    in_review: 'primary',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

// 辅助方法：获取用例评审状态文本
const getCaseReviewStatusText = (status) => {
  const textMap = {
    passed: '通过',
    failed: '拒绝',
    pending: '待评审',
    in_review: '评审中',
    approved: '通过',
    rejected: '拒绝'
  }
  return textMap[status] || '未知状态'
}

const fetchReviewDetail = async (taskId) => {
  try {
    // 获取评审任务详情
    const taskResponse = await getReviewTask(taskId)
    currentReviewTask.value = taskResponse.data
    
    // 获取用例评审详情
    const casesResponse = await getCaseReviews(taskId)
    currentReviewTask.value.case_reviews = casesResponse.data.case_reviews || []
  } catch (error) {
    console.error('获取评审详情失败:', error)
    ElMessage.error('获取评审详情失败')
  }
}

// 处理评审按钮点击
const handleReviewButtonClick = async () => {
  if (!selectedSuite.value || selectedSuite.value.type !== 'suite') {
    return
  }
  
  // 获取评审状态和相关信息
  const status = suiteReviewStatus.value?.current_status || 'not_submitted'
  const reviewerId = suiteReviewStatus.value?.current_reviewer_id
  const isCreator = userStore.userInfo && userStore.userInfo.id === selectedSuite.value.creator_id
  const isReviewer = userStore.userInfo && userStore.userInfo.id === reviewerId
  
  if (isCreator) {
    // 作为评审发起人
    if (status === 'not_submitted') {
      // 发起评审
      showInitiateReviewDialog()
    } else if (status === 'pending') {
      // 显示悬浮提示信息
      ElMessage.info('等待评审人处理...')
    } else if (status === 'in_review') {
      // 显示悬浮提示信息
      ElMessage.info('等待评审人完成评审...')
    } else if (status === 'approved' || status === 'completed' || status === 'rejected') {
      // 跳转到我发起的评审标签页
      router.push({ path: '/case-reviews', query: { activeTab: 'my-initiated' } })
    }
  } else if (isReviewer) {
    // 作为评审人
    if (status === 'not_submitted') {
      // 显示悬浮提示信息
      ElMessage.info('该用例集创建者暂未发起评审...')
    } else if (status === 'pending') {
      // 跳转到待我评审标签页
      router.push({ path: '/case-reviews', query: { activeTab: 'my-tasks' } })
    } else if (status === 'in_review') {
      // 跳转到待我评审标签页
      router.push({ path: '/case-reviews', query: { activeTab: 'my-tasks' } })
    } else if (status === 'approved' || status === 'completed' || status === 'rejected') {
      // 跳转到待我评审标签页
      router.push({ path: '/case-reviews', query: { activeTab: 'my-tasks' } })
    }
  } else {
    // 作为其他用户
    if (status === 'not_submitted') {
      // 显示悬浮提示信息
      ElMessage.info('该用例集创建者暂未发起评审...')
    } else if (status === 'pending') {
      // 显示悬浮提示信息
      ElMessage.info('等待评审人处理...')
    } else if (status === 'in_review') {
      // 显示悬浮提示信息
      ElMessage.info('等待评审人完成评审...')
    } else {
      // 先获取最新的评审任务ID
      const reviewStatusResponse = await getSuiteReviewStatus(selectedSuite.value.id)
      
      // 获取最新的评审任务
      let latestTaskId = null
      if (reviewStatusResponse.data.review_history && reviewStatusResponse.data.review_history.length > 0) {
        // 从评审历史中获取最新的评审任务ID
        latestTaskId = reviewStatusResponse.data.review_history[0].task_id
      }
      
      if (latestTaskId) {
        // 获取评审详情
        await fetchReviewDetail(latestTaskId)
        
        // 显示评审详情页面
        reviewDialogType.value = 'detail'
        reviewDialogTitle.value = '评审详情'
        reviewDialogVisible.value = true
      } else {
        // 如果没有找到评审任务，显示提示
        ElMessage.error('未找到评审任务详情')
      }
    }
  }
}

// 节点点击事件
const handleNodeClick = (data) => {
  selectedSuite.value = data
  if (data.type === 'suite') {
    // 只有用例集才能加载测试用例
    loadTestCases(data.id)
    // 获取用例集评审状态
    getSuiteReviewStatusData(data.id)
  } else {
    // 文件夹清空测试用例列表
    testCases.value = []
    totalCases.value = 0
    suiteReviewStatus.value = null
    reviewButtonText.value = '发起评审'
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
const handleContextMenu = (event, data, node) => {
  // 阻止默认的右键菜单
  event.preventDefault()
  
  // 保存选中的节点数据
  selectedNode.value = data
  
  // 设置右键菜单位置
  // 考虑页面滚动和视口边界
  const x = event.clientX + window.scrollX
  const y = event.clientY + window.scrollY
  
  // 设置菜单位置
  contextMenuStyle.left = `${x}px`
  contextMenuStyle.top = `${y}px`
  
  // 强制显示菜单
  contextMenuVisible.value = true
  
  // 确保菜单在最顶层
  contextMenuStyle.zIndex = 10000
}

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
}

// 点击页面其他地方关闭右键菜单
onMounted(() => {
  // 使用mousedown事件而不是click事件，因为contextmenu事件会在mousedown事件之后，click事件之前触发
  // 这样可以避免右键点击时立即关闭菜单
  document.addEventListener('mousedown', (event) => {
    // 只有左键点击才关闭菜单
    if (event.button === 0) {
      // 检查点击的不是右键菜单本身
      if (contextMenuRef.value && !contextMenuRef.value.contains(event.target)) {
        closeContextMenu()
      }
    }
  })
  loadTreeData()
  // 加载评审人列表
  loadReviewers()
})

// 组件销毁时移除事件监听器
onUnmounted(() => {
  // 移除mousedown事件监听器，注意这里不能直接传递closeContextMenu函数
  // 因为添加的是一个匿名函数，需要重新获取并移除
  // 或者使用命名函数来处理
  document.removeEventListener('click', handleGlobalClick)
})

// 递归获取所有节点ID
const getAllNodeIds = (nodes) => {
  let ids = []
  if (!nodes || !nodes.length) return ids
  
  for (const node of nodes) {
    ids.push(node.id)
    if (node.children && node.children.length) {
      ids = [...ids, ...getAllNodeIds(node.children)]
    }
  }
  return ids
}

// 加载树形数据
const loadTreeData = async () => {
  try {
    const response = await getTestSuiteTree()
    treeData.value = response.data
    
    // 更新套件选项
    suiteOptions.value = buildSuiteOptions()
    
    // 获取所有节点ID并设置为默认展开
    expandedKeys.value = getAllNodeIds(treeData.value)
    
    // 数据更新后，Element Plus Tree 会自动使用 default-expanded-keys 恢复展开状态
  } catch (error) {
    ElMessage.error('加载测试套件失败')
    console.error('Failed to load test suites:', error)
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getProjects()
    // 检查API返回的数据结构
    console.log('Projects API response:', response)
    if (response && response.code === 200 && response.data && response.data.items) {
      projects.value = response.data.items
    } else if (response && response.data && Array.isArray(response.data)) {
      // 兼容旧版API返回格式
      projects.value = response.data
    } else {
      projects.value = []
      console.error('Projects API returned invalid data structure')
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    console.error('Failed to load projects:', error)
    // 确保projects是数组
    projects.value = []
  }
}

// 加载迭代列表
const loadIterations = async (projectId) => {
  if (!projectId) {
    iterations.value = []
    return
  }
  
  try {
    const response = await getProjectIterations(projectId)
    let allIterations = []
    
    // 处理API返回的数据格式
    if (response && response.code === 200 && response.data && response.data.items) {
      allIterations = response.data.items
    } else if (response && response.data && Array.isArray(response.data)) {
      // 兼容旧版API返回格式
      allIterations = response.data
    }
    
    // 获取当前选中的迭代ID
    const currentIterationId = suiteForm.iteration_id
    
    // 如果当前有选中的迭代，但不在结果中，尝试添加到列表中
    if (currentIterationId) {
      const isIterationInList = allIterations.some(iter => iter.id === currentIterationId)
      if (!isIterationInList) {
        // 检查selectedNode中是否有当前迭代的完整信息
        if (selectedNode.value && selectedNode.value.iteration_name) {
          // 将当前迭代添加到列表中，确保它能显示在下拉列表中
          allIterations.push({
            id: currentIterationId,
            iteration_name: selectedNode.value.iteration_name
          })
        }
      }
    }
    
    iterations.value = allIterations
  } catch (error) {
    ElMessage.error('加载迭代列表失败')
    console.error('Failed to load iterations:', error)
    
    // 即使API调用失败，也要确保当前选中的迭代能显示
    const currentIterationId = suiteForm.iteration_id
    if (currentIterationId) {
      // 创建一个包含当前选中迭代的临时列表
      iterations.value = [{
        id: currentIterationId,
        iteration_name: selectedNode.value?.iteration_name || '当前选中迭代'
      }]
    } else {
      iterations.value = []
    }
  }
}

// 加载需求列表
const loadRequirements = async (projectId, iterationId) => {
  if (!projectId || !iterationId) {
    requirements.value = []
    return
  }
  
  try {
    const response = await getProjectVersionRequirements(projectId)
    let allRequirements = []
    
    // 处理API返回的数据格式
    if (response && response.code === 200 && response.data && response.data.items) {
      allRequirements = response.data.items
    } else if (response && response.data && Array.isArray(response.data)) {
      // 兼容旧版API返回格式
      allRequirements = response.data
    }
    
    // 根据迭代筛选需求
    const filteredRequirements = allRequirements.filter(req => req.iteration_id === iterationId)
    
    // 获取当前选中的需求ID
    const currentRequirementId = suiteForm.version_requirement_id
    
    // 如果当前有选中的需求，但不在筛选结果中，尝试添加到列表中
    if (currentRequirementId) {
      const isRequirementInList = filteredRequirements.some(req => req.id === currentRequirementId)
      if (!isRequirementInList) {
        // 从所有需求中查找当前选中的需求
        let currentRequirement = allRequirements.find(req => req.id === currentRequirementId)
        
        // 如果在所有需求中找不到当前需求，使用selectedNode中的信息创建一个
        if (!currentRequirement && selectedNode.value && selectedNode.value.version_requirement_name) {
          currentRequirement = {
            id: currentRequirementId,
            requirement_name: selectedNode.value.version_requirement_name,
            iteration_id: iterationId
          }
        }
        
        // 将当前需求添加到筛选结果中，确保它能显示在下拉列表中
        if (currentRequirement) {
          filteredRequirements.push(currentRequirement)
        }
      }
    }
    
    requirements.value = filteredRequirements
  } catch (error) {
    ElMessage.error('加载需求列表失败')
    console.error('Failed to load requirements:', error)
    
    // 即使API调用失败，也要确保当前选中的需求能显示
    const currentRequirementId = suiteForm.version_requirement_id
    if (currentRequirementId) {
      // 创建一个包含当前选中需求的临时列表，使用真实需求名称
      requirements.value = [{ 
        id: currentRequirementId, 
        requirement_name: selectedNode.value?.version_requirement_name || '当前选中需求' 
      }]
    } else {
      requirements.value = []
    }
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
    
    // 延迟执行，确保表格已渲染
    setTimeout(() => {
      if (showSelection.value && caseTableRef.value) {
        // 遍历当前页的用例，根据selectedCaseIds设置选中状态
        testCases.value.forEach(caseItem => {
          if (selectedCaseIds.value.has(caseItem.id)) {
            caseTableRef.value.toggleRowSelection(caseItem, true)
          } else {
            caseTableRef.value.toggleRowSelection(caseItem, false)
          }
        })
      }
    }, 100)
    
    // 加载所有测试用例用于统计
    loadAllTestCases(suiteId)
  } catch (error) {
    ElMessage.error('加载测试用例失败')
    console.error('Failed to load test cases:', error)
  }
}

// 加载所有测试用例用于统计
const loadAllTestCases = async (suiteId) => {
  try {
    // 加载所有数据，page_size设置为较大值
    const response = await getSuiteCases(suiteId, {
      page: 1,
      page_size: 10000 // 足够大的值，确保获取所有数据
    })
    allTestCases.value = response.data.items
  } catch (error) {
    console.error('Failed to load all test cases:', error)
    // 失败时使用当前页数据作为备选
    allTestCases.value = [...testCases.value]
  }
}

// 新增套件
const handleAddSuite = () => {
  isEditSuite.value = false
  isContextMenuAction.value = false
  resetSuiteForm()
  
  // 确保项目、迭代、需求参数为空
  suiteForm.project_id = null
  suiteForm.iteration_id = null
  suiteForm.version_requirement_id = null
  
  suiteDialogVisible.value = true
  // 加载项目列表
  loadProjects()
}

// 从右键菜单新增套件
const handleAddSuiteFromMenu = () => {
  isEditSuite.value = false
  isContextMenuAction.value = true
  resetSuiteForm()
  
  // 在重置表单后设置parent_id，避免被重置
  if (selectedNode.value) {
    suiteForm.parent_id = selectedNode.value.id
  }
  
  // 确保项目、迭代、需求参数为空
  suiteForm.project_id = null
  suiteForm.iteration_id = null
  suiteForm.version_requirement_id = null
  
  suiteDialogVisible.value = true
  closeContextMenu()
  
  // 加载项目列表
  loadProjects()
}

// 编辑套件
const handleEditSuite = () => {
  if (!selectedNode.value) return
  isEditSuite.value = true
  isContextMenuAction.value = true
  
  const suiteData = selectedNode.value
  
  // 设置初始化标志，跳过观察者触发的字段重置
  isInitializingForm.value = true
  
  // 直接填充套件表单数据，不等待API调用
  suiteForm.id = suiteData.id
  suiteForm.suite_name = suiteData.suite_name
  suiteForm.description = suiteData.description || ''
  suiteForm.type = suiteData.type
  suiteForm.parent_id = suiteData.parent_id
  suiteForm.project_id = suiteData.project_id
  suiteForm.iteration_id = suiteData.iteration_id || null
  suiteForm.version_requirement_id = suiteData.version_requirement_id || null
  
  // 立即显示对话框，避免用户等待
  suiteDialogVisible.value = true
  closeContextMenu()
  
  // 异步加载数据，不阻塞UI
  const loadDataAsync = async () => {
    try {
      // 加载项目列表
      await loadProjects()
      
      // 如果有项目ID，加载对应的迭代和需求
      if (suiteData.project_id) {
        await loadIterations(suiteData.project_id)
        // 如果有迭代ID，加载对应的需求
        if (suiteData.iteration_id) {
          await loadRequirements(suiteData.project_id, suiteData.iteration_id)
        }
      }
    } catch (error) {
      console.error('加载套件数据失败:', error)
      ElMessage.error('加载套件数据失败，请刷新重试')
    } finally {
      // 初始化完成，恢复观察者功能
      isInitializingForm.value = false
    }
  }
  
  // 启动异步加载
  loadDataAsync()
}

// 删除套件
const handleDeleteSuite = async () => {
  if (!selectedNode.value) return
  
  // 根据套件类型生成带套件名称的确认提示
  let confirmMessage = ''
  if (selectedNode.value.type === 'folder') {
    // 文件夹删除提示，带套件名称
    confirmMessage = `确定删除文件夹"${selectedNode.value.suite_name}"及其文件夹下所有内容吗？`
  } else {
    // 用例集删除提示，带套件名称
    confirmMessage = `确定删除用例集"${selectedNode.value.suite_name}"吗？`
  }
  
  ElMessageBox.confirm(confirmMessage, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTestSuite(selectedNode.value.id)
      ElMessage.success(selectedNode.value.type === 'folder' ? `文件夹"${selectedNode.value.suite_name}"及其文件夹下所有内容已成功删除` : `用例集"${selectedNode.value.suite_name}"已成功删除`)
      loadTreeData()
    } catch (error) {
      console.error('删除测试套件失败:', error)
      // 根据后端返回的错误信息给出友好提示
      const errorMsg = error.response?.data?.message || '删除测试套件失败'
      ElMessage.error(errorMsg)
    } finally {
      closeContextMenu()
    }
  }).catch(() => {
    // 取消删除
    closeContextMenu()
  })
}

// 取消套件操作
const handleCancelSuite = () => {
  suiteDialogVisible.value = false
  parentSuitePopoverVisible.value = false
  // 重置右键菜单操作标志
  isContextMenuAction.value = false
}

// 保存套件
const handleSaveSuite = async () => {
  try {
    // 表单验证
    await suiteFormRef.value.validate()
    
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
    parentSuitePopoverVisible.value = false
    // 重置右键菜单操作标志
    isContextMenuAction.value = false
    loadTreeData()
  } catch (error) {
    console.error('保存测试套件失败:', error)
    // 表单验证失败时，Element Plus会自动显示错误信息，不需要额外提示
    // 只有当API请求失败时，才显示错误信息
    if (error.response || error.message && !error.name.includes('Validate')) {
      ElMessage.error(isEditSuite.value ? '更新测试套件失败' : '创建测试套件失败')
    }
  }
}

// 重置套件表单
const resetSuiteForm = () => {
  suiteForm.id = null
  suiteForm.suite_name = ''
  suiteForm.description = ''
  suiteForm.type = 'folder' // 默认类型为文件夹
  suiteForm.parent_id = null
  suiteForm.project_id = null // 默认项目ID，实际应从上下文获取
  suiteForm.version_requirement_id = null
  suiteForm.iteration_id = null
  
  // 重置表单验证状态
  if (suiteFormRef.value) {
    suiteFormRef.value.resetFields()
  }
}

// 刷新树形数据
const handleRefresh = () => {
  loadTreeData()
  ElMessage.success('已刷新测试套件')
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

// 获取选中的用例集路径
const getSelectedCaseSuitePath = () => {
  // 获取当前选中的suite_id，根据创建方式选择从哪个表单获取
  const suiteId = createCaseType.value === 'manual' || isEditCase.value 
    ? caseForm.suite_id 
    : autoCaseForm.suite_id
  
  if (!suiteId) return ''
  
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
  
  const path = findNodePath(treeData.value, suiteId)
  return path ? path.join(' / ') : ''
}

// 获取用例集树数据
const getSuiteTreeData = () => {
  // 返回完整的树形数据，让前端模板来过滤显示
  return treeData.value
}

// 监听父套件ID变化，更新显示路径
watch(() => suiteForm.parent_id, () => {
  selectedParentSuitePath.value = getSelectedParentPath()
})

// 监听用例集ID变化，更新显示路径
watch(() => caseForm.suite_id, () => {
  selectedCaseSuitePath.value = getSelectedCaseSuitePath()
})

// 监听项目ID变化，加载迭代列表
watch(() => suiteForm.project_id, (newProjectId, oldProjectId) => {
  // 初始化表单时跳过观察者
  if (isInitializingForm.value) return
  
  if (newProjectId !== oldProjectId && newProjectId !== undefined) {
    // 重置迭代和需求列表
    iterations.value = []
    requirements.value = []
    
    // 重置迭代和需求ID
    suiteForm.iteration_id = null
    suiteForm.version_requirement_id = null
    
    // 加载新的迭代列表
    if (newProjectId) {
      loadIterations(newProjectId)
    }
  }
})

// 监听迭代ID变化，加载需求列表
watch(() => suiteForm.iteration_id, (newIterationId, oldIterationId) => {
  // 初始化表单时跳过观察者
  if (isInitializingForm.value) return
  
  if (newIterationId !== oldIterationId && newIterationId !== undefined) {
    // 重置需求列表
    requirements.value = []
    
    // 重置需求ID
    suiteForm.version_requirement_id = null
    
    // 加载新的需求列表
    if (suiteForm.project_id && newIterationId) {
      loadRequirements(suiteForm.project_id, newIterationId)
    }
  }
})

// 监听父套件弹出层可见性变化，添加或移除全局点击事件监听器
watch(() => parentSuitePopoverVisible, (newValue) => {
  if (newValue) {
    // 添加全局点击事件监听器
    document.addEventListener('click', handleGlobalClick)
  } else if (!caseSuitePopoverVisible.value) {
    // 只有当所有弹出层都关闭时，才移除监听器
    document.removeEventListener('click', handleGlobalClick)
  }
})

// 监听用例集弹出层可见性变化，添加或移除全局点击事件监听器
watch(() => caseSuitePopoverVisible, (newValue) => {
  if (newValue) {
    // 添加全局点击事件监听器
    document.addEventListener('click', handleGlobalClick)
  } else if (!parentSuitePopoverVisible.value) {
    // 只有当所有弹出层都关闭时，才移除监听器
    document.removeEventListener('click', handleGlobalClick)
  }
})

// 全局点击事件处理函数
const handleGlobalClick = (event) => {
  // 检查父套件选择器
  const parentSuiteSelector = document.querySelector('.parent-suite-selector')
  const parentPopover = document.querySelector('.el-popover')
  
  // 检查用例集选择器
  const caseSuiteSelector = document.querySelector('.case-suite-selector')
  const casePopover = document.querySelectorAll('.el-popover')[1] // 获取第二个popover
  
  // 关闭父套件弹出层
  if (parentSuiteSelector && !parentSuiteSelector.contains(event.target) && 
      parentPopover && !parentPopover.contains(event.target)) {
    parentSuitePopoverVisible.value = false
  }
  
  // 关闭用例集弹出层
  if (caseSuiteSelector && !caseSuiteSelector.contains(event.target) && 
      casePopover && !casePopover.contains(event.target)) {
    caseSuitePopoverVisible.value = false
  }
}

// 清除父套件选择
const clearParentSuiteSelection = () => {
  suiteForm.parent_id = null
  selectedParentSuitePath.value = ''
  // 关闭弹出的下拉页面
  parentSuitePopoverVisible.value = false
}

// 清除用例集选择
const clearCaseSuiteSelection = () => {
  caseForm.suite_id = null
  selectedCaseSuitePath.value = ''
}

// 处理父套件选择
const handleParentSuiteSelect = (data) => {
  suiteForm.parent_id = data.id
  selectedParentSuitePath.value = getSelectedParentPath()
  // 选择后关闭弹出框
  parentSuitePopoverVisible.value = false
}

// 处理用例集选择
const handleCaseSuiteSelect = (data) => {
  // 只有类型为suite的节点才能被选择
  if (data.type === 'suite') {
    // 根据当前创建方式选择设置哪个表单的suite_id
    if (createCaseType.value === 'manual' || isEditCase.value) {
      caseForm.suite_id = data.id
    } else {
      autoCaseForm.suite_id = data.id
    }
    // 更新选中路径显示
    selectedCaseSuitePath.value = getSelectedCaseSuitePath()
    // 选择后关闭弹出框
    caseSuitePopoverVisible.value = false
  }
}

// 新增：处理自动生成用例的用例集选择
const handleAutoCaseSuiteSelect = (data) => {
  handleCaseSuiteSelect(data)
}

// 新增：处理需求文档文件变化
const handleRequirementFileChange = (file) => {
  autoCaseForm.file = file.raw
  requirementFileList.value = [file]
}

// 新增：处理需求文档文件移除
const handleRequirementFileRemove = () => {
  autoCaseForm.file = null
  requirementFileList.value = []
}

// 新增：处理需求文档文件超出限制
const handleRequirementFileExceed = () => {
  ElMessage.warning('只能上传一个需求文档文件')
}

// 新增：生成用例按钮点击事件
const handleGenerateCase = async () => {
  try {
    await autoCaseFormRef.value.validate()
    
    // 这里暂不实现具体生成用例功能，只给出提示
    ElMessage.success('用例生成功能暂未实现，点击生成用例成功')
  } catch (error) {
    ElMessage.error('请填写必填字段')
  }
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
  isEditCase.value = false
  resetCaseForm()
  
  // 新增：重置创建方式为手动创建
  createCaseType.value = 'manual'
  
  // 新增：重置自动生成用例表单
  Object.assign(autoCaseForm, {
    case_name: '',
    suite_id: null,
    requirement_desc: '',
    file: null
  })
  
  // 新增：重置需求文档文件列表
  requirementFileList.value = []
  
  // 如果有选中的套件且类型为用例集，设置为默认值
  if (selectedSuite.value && selectedSuite.value.type === 'suite') {
    caseForm.suite_id = selectedSuite.value.id
    autoCaseForm.suite_id = selectedSuite.value.id
    
    // 自动生成下一个用例编号
    generateNextCaseNumber(selectedSuite.value.id)
  } else {
    autoCaseForm.suite_id = null
  }
  
  caseDialogVisible.value = true
}

// 自动生成下一个用例编号
const generateNextCaseNumber = async (suiteId) => {
  try {
    // 加载所有用例以获取最新编号
    const response = await getSuiteCases(suiteId, {
      page: 1,
      page_size: 10000
    })
    
    const cases = response.data.items
    if (cases.length === 0) {
      // 没有用例，设置默认值，直接从001开始
      caseNumberParts.part1 = 'Proj'
      caseNumberParts.part2 = 'Iter'
      caseNumberParts.part3 = 'Req'
      caseNumberParts.part4 = '001'
      updateCaseNumber()
      return
    }
    
    // 找到最新的用例编号
    let latestNumber = 0
    let prefix1 = ''
    let prefix2 = ''
    let prefix3 = ''
    
    cases.forEach(caseItem => {
      const caseNumber = caseItem.case_number
      if (!caseNumber) return
      
      // 解析用例编号格式：xxx-xxx-xxx001
      const regex = /^(.*?)-(.*?)-(.*?)(\d{3})$/g
      const match = regex.exec(caseNumber)
      if (match) {
        const num = parseInt(match[4])
        if (num > latestNumber) {
          latestNumber = num
          prefix1 = match[1]
          prefix2 = match[2]
          prefix3 = match[3]
        }
      }
    })
    
    // 设置下一个编号，格式化为3位
    caseNumberParts.part1 = prefix1
    caseNumberParts.part2 = prefix2
    caseNumberParts.part3 = prefix3
    caseNumberParts.part4 = (latestNumber + 1).toString().padStart(3, '0')
    updateCaseNumber()
  } catch (error) {
    console.error('生成用例编号失败:', error)
    // 失败时设置默认值
    caseNumberParts.part1 = ''
    caseNumberParts.part2 = ''
    caseNumberParts.part3 = ''
    caseNumberParts.part4 = '001'
    updateCaseNumber()
  }
}

// 编辑用例
const handleEditCase = (row) => {
  isEditCase.value = true
  Object.assign(caseForm, row)
  
  // 解析用例编号到分段输入框
  parseCaseNumber(row.case_number)
  
  caseDialogVisible.value = true
}

// 解析用例编号到分段输入框
const parseCaseNumber = (caseNumber) => {
  if (!caseNumber) {
    caseNumberParts.part1 = ''
    caseNumberParts.part2 = ''
    caseNumberParts.part3 = ''
    caseNumberParts.part4 = ''
    return
  }
  
  // 解析用例编号格式：xxx-xxx-xxx001
  const regex = /^(.*?)-(.*?)-(.*?)(\d{3})$/g
  const match = regex.exec(caseNumber)
  if (match) {
    caseNumberParts.part1 = match[1]
    caseNumberParts.part2 = match[2]
    caseNumberParts.part3 = match[3]
    // 保持数字部分为3位格式
    caseNumberParts.part4 = match[4]
  } else {
    // 解析失败，设置默认值
    caseNumberParts.part1 = ''
    caseNumberParts.part2 = ''
    caseNumberParts.part3 = ''
    caseNumberParts.part4 = ''
  }
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

// 取消用例操作
const handleCancelCase = () => {
  caseDialogVisible.value = false
  caseSuitePopoverVisible.value = false
}

// 保存用例
const handleSaveCase = async () => {
  try {
    // 表单验证
    await caseFormRef.value.validate()
    
    // 获取测试套件详情，获取项目相关信息
    const suiteDetail = await getTestSuiteDetail(caseForm.suite_id)
    
    // 创建完整的caseData对象，包含从测试套件获取的项目相关信息
    const caseData = {
      ...caseForm,
      project_id: suiteDetail.data.project_id,
      version_requirement_id: suiteDetail.data.version_requirement_id,
      iteration_id: suiteDetail.data.iteration_id
    }
    
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
    caseSuitePopoverVisible.value = false
    loadTestCases(selectedSuite.value?.id)
  } catch (error) {
    // 表单验证失败时，Element Plus会自动显示错误信息，不需要额外提示
    // 只有当API请求失败时，才显示错误信息
    if (error.response || error.message && !error.name.includes('Validate')) {
      console.error('保存测试用例失败:', error)
      ElMessage.error(isEditCase.value ? '更新测试用例失败' : '创建测试用例失败')
    }
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
  caseForm.test_data = ''
  caseForm.actual_result = ''
  
  // 重置用例编号分段输入
  caseNumberParts.part1 = ''
  caseNumberParts.part2 = ''
  caseNumberParts.part3 = ''
  caseNumberParts.part4 = ''
  
  // 重置表单验证状态
  if (caseFormRef.value) {
    caseFormRef.value.resetFields()
  }
}

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'list' ? 'mindmap' : 'list'
}

// 左侧面板收起/展开状态
const isLeftPanelCollapsed = ref(false)

// 切换左侧面板显示状态
const toggleLeftPanel = () => {
  isLeftPanelCollapsed.value = !isLeftPanelCollapsed.value
}

// 文件上传相关
const uploadRef = ref(null)
const excelFile = ref(null)

// 导出Excel
const handleExportExcel = async () => {
  try {
    // 如果是从导入导出对话框调用，使用选择的用例集ID
    let suiteId = importExportForm.suite_id
    
    // 如果没有选择用例集ID（直接调用），使用当前选中的套件ID
    if (!suiteId && selectedSuite.value && selectedSuite.value.type === 'suite') {
      suiteId = selectedSuite.value.id
    }
    
    if (!suiteId) {
      ElMessage.error('请选择要导出的用例集')
      return
    }
    
    // 准备导出数据
    ElMessage.info('正在准备导出数据，请稍候...')
    
    // 加载所有测试用例数据
    const response = await getSuiteCases(suiteId, {
      page: 1,
      page_size: 10000 // 足够大的值，确保获取所有数据
    })
    
    const cases = response.data.items
    if (cases.length === 0) {
      ElMessage.warning('该用例集下没有测试用例')
      return
    }
    
    // 获取测试套件详情，获取项目相关信息
    const suiteDetail = await getTestSuiteDetail(suiteId)
    
    // 准备导出数据
    const exportData = cases.map(caseItem => {
      // 将状态值转换为中文显示
      const statusLabel = statusOptions.find(option => option.value === caseItem.status)?.label || '未执行'
      return {
        '用例编号': caseItem.case_number || '',
        '用例名称': caseItem.case_name || '',
        '所属项目': suiteDetail.data.project_name || '',
        '所属迭代': suiteDetail.data.iteration_name || '',
        '关联需求': suiteDetail.data.version_requirement_name || '',
        '优先级': caseItem.priority || '',
        '状态': statusLabel,
        '前置条件': caseItem.preconditions || '',
        '测试数据': caseItem.test_data || '',
        '操作步骤': caseItem.steps || '',
        '预期结果': caseItem.expected_result || '',
        '实际结果': caseItem.actual_result || ''
      }
    })
    
    // 创建工作簿和工作表
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '测试用例')
    
    // 设置样式
    ws['!cols'] = [
      { wch: 20 }, // 用例编号
      { wch: 30 }, // 用例名称
      { wch: 20 }, // 所属项目
      { wch: 20 }, // 所属迭代
      { wch: 20 }, // 关联需求
      { wch: 10 }, // 优先级
      { wch: 15 }, // 状态
      { wch: 25 }, // 前置条件
      { wch: 25 }, // 测试数据
      { wch: 40 }, // 操作步骤
      { wch: 30 }, // 预期结果
      { wch: 30 }  // 实际结果
    ]
    
    // 生成Excel文件并下载
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    saveAs(blob, `测试用例_${new Date().toISOString().slice(0, 10)}.xlsx`)
    
    ElMessage.success('Excel导出成功')
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败，请重试')
  }
}

// 导入Excel
const handleImportExcel = () => {
  // 直接触发隐藏的上传按钮点击
  if (uploadBtnRef.value) {
    uploadBtnRef.value.click()
  }
}

// 下载Excel模板
const downloadExcelTemplate = () => {
  try {
    // 准备模板数据
    const templateData = [
      {
        '用例编号': '示例-需求-功能001',
        '用例名称': '示例用例',
        '优先级': 'P1',
        '状态': '',
        '前置条件': '前置条件示例',
        '测试数据': '测试数据示例',
        '操作步骤': '操作步骤示例\n步骤1\n步骤2\n步骤3',
        '预期结果': '预期结果示例',
        '实际结果': ''
      }
    ]
    
    // 创建工作簿和工作表
    const ws = XLSX.utils.json_to_sheet(templateData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '测试用例模板')
    
    // 设置样式
    ws['!cols'] = [
      { wch: 20 }, // 用例编号
      { wch: 30 }, // 用例名称
      { wch: 10 }, // 优先级
      { wch: 15 }, // 状态
      { wch: 25 }, // 前置条件
      { wch: 25 }, // 测试数据
      { wch: 40 }, // 操作步骤
      { wch: 30 }, // 预期结果
      { wch: 30 }  // 实际结果
    ]
    
    // 生成Excel文件并下载
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    saveAs(blob, '测试用例模板.xlsx')
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

// 计算无状态用例数量
const notExecutedCount = computed(() => {
  return allTestCases.value.filter(caseItem => !caseItem.status || caseItem.status === '' || caseItem.status === 'none').length
})

// 计算已执行用例数量
const executedCount = computed(() => {
  return allTestCases.value.filter(caseItem => caseItem.status && caseItem.status !== '' && caseItem.status !== 'none').length
})

// 计算执行率
const executionRate = computed(() => {
  if (totalCases.value === 0) return 0
  return Math.round((executedCount.value / totalCases.value) * 100)
})

// 状态进度计算
const statusProgress = computed(() => {
  // 统计各状态数量
  const statusCount = {
    pass: 0,
    fail: 0,
    blocked: 0,
    not_applicable: 0,
    none: 0
  }
  
  // 统计测试用例状态
  allTestCases.value.forEach(caseItem => {
    const status = caseItem.status === '' ? 'none' : (caseItem.status || 'none')
    statusCount[status]++
  })
  
  // 计算百分比
  const total = totalCases.value || 1 // 避免除以0
  const progress = [
    { status: 'pass', label: '通过', count: statusCount.pass, percentage: Math.round((statusCount.pass / total) * 100) },
    { status: 'fail', label: '失败', count: statusCount.fail, percentage: Math.round((statusCount.fail / total) * 100) },
    { status: 'blocked', label: '阻塞', count: statusCount.blocked, percentage: Math.round((statusCount.blocked / total) * 100) },
    { status: 'not_applicable', label: '不适用', count: statusCount.not_applicable, percentage: Math.round((statusCount.not_applicable / total) * 100) },
    { status: 'none', label: '未执行', count: statusCount.none, percentage: Math.round((statusCount.none / total) * 100) }
  ]
  
  // 过滤掉数量为0的状态
  return progress.filter(item => item.count > 0)
})

// 计算标签位置，确保不重叠
const positionedLabels = computed(() => {
  if (!statusProgress.value.length) return []
  
  const labels = [...statusProgress.value]
  const positioned = []
  let currentPosition = 0
  
  // 先计算每个标签的初始位置
  const initialPositions = labels.map((item, index) => {
    const segmentStart = currentPosition
    const segmentEnd = segmentStart + item.percentage
    const middlePosition = segmentStart + item.percentage / 2
    
    // 更新当前位置
    currentPosition = segmentEnd
    
    return {
      ...item,
      position: middlePosition,
      originalPosition: middlePosition
    }
  })
  
  // 碰撞检测和位置调整
  const labelWidth = 120 // 估算每个标签的宽度，单位：百分比
  const minDistance = 2 // 标签之间的最小距离，单位：百分比
  
  // 第一次调整：从左到右
  for (let i = 1; i < initialPositions.length; i++) {
    const prevLabel = initialPositions[i - 1]
    const currentLabel = initialPositions[i]
    const distance = currentLabel.position - prevLabel.position
    
    if (distance < labelWidth + minDistance) {
      // 调整当前标签位置
      currentLabel.position = prevLabel.position + labelWidth + minDistance
      
      // 确保不超过总宽度
      if (currentLabel.position > 100) {
        currentLabel.position = 100 - labelWidth / 2
      }
    }
  }
  
  // 第二次调整：从右到左，确保不超过边界
  for (let i = initialPositions.length - 2; i >= 0; i--) {
    const nextLabel = initialPositions[i + 1]
    const currentLabel = initialPositions[i]
    const distance = nextLabel.position - currentLabel.position
    
    if (distance < labelWidth + minDistance) {
      // 调整当前标签位置
      currentLabel.position = nextLabel.position - (labelWidth + minDistance)
      
      // 确保不小于0
      if (currentLabel.position < 0) {
        currentLabel.position = labelWidth / 2
      }
    }
  }
  
  // 第三次调整：特殊处理短状态段
  initialPositions.forEach((label, index) => {
    const segmentStart = label.originalPosition - (label.percentage / 2)
    const segmentEnd = label.originalPosition + (label.percentage / 2)
    
    // 如果标签位置超出了对应状态段太多，则调整到状态段边缘
    if (label.position < segmentStart - 5) {
      label.position = segmentStart + minDistance
    } else if (label.position > segmentEnd + 5) {
      label.position = segmentEnd - minDistance
    }
    
    // 确保最终位置在合理范围内
    label.position = Math.max(0, Math.min(100, label.position))
  })
  
  return initialPositions
})

// 导入/导出用例对话框相关
const importExportVisible = ref(false)
const importExportFormRef = ref(null)
const importParentSuiteVisible = ref(false)
const importSelectedParentSuitePath = ref('')
const exportCaseSuiteVisible = ref(false)
const exportSelectedCaseSuitePath = ref('')
const importUploadRef = ref(null)
const uploadBtnRef = ref(null)

// 导入状态管理
const isImporting = ref(false)

// 存储导入的文件数据
const importedFile = ref(null)

// 文件列表
const fileList = ref([])

// 导入导出表单数据
const importExportForm = reactive({
  type: 'import', // 默认导入
  fileName: '',
  parent_id: null,
  suite_id: null,
  targetPath: ''
})

// 显示导入导出对话框
const showImportExportDialog = () => {
  importExportVisible.value = true
}

// 处理文件选择变化
const handleFileChange = (file, fileList) => {
  // on-change事件传递的file参数直接是文件对象
  const isExcel = file.raw.type === 'application/vnd.ms-excel' || file.raw.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  const isLt10M = file.raw.size / 1024 / 1024 < 10
  
  if (!isExcel) {
    ElMessage.error('只能上传Excel文件！')
    return
  }
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB！')
    return
  }
  
  // 保存文件和文件名
  importedFile.value = file.raw
  importExportForm.fileName = file.name
  // 更新文件列表，只保留最新选择的文件
  fileList.value = fileList.slice(-1)
}

// 处理文件移除
const handleFileRemove = () => {
  importedFile.value = null
  importExportForm.fileName = ''
  fileList.value = []
}

// 处理文件超出限制
const handleFileExceed = () => {
  ElMessage.error('一次只能导入一个文件')
}

// 清除导入父套件选择
const clearImportParentSuiteSelection = () => {
  importExportForm.parent_id = null
  importSelectedParentSuitePath.value = ''
  importParentSuiteVisible.value = false
}

// 处理导入父套件选择
const handleImportParentSuiteSelect = (data) => {
  importExportForm.parent_id = data.id
  // 更新显示路径
  const findPath = (nodes, id, path = []) => {
    for (const node of nodes) {
      if (node.id === id) {
        return [...path, node.suite_name]
      }
      if (node.children && node.children.length) {
        const result = findPath(node.children, id, [...path, node.suite_name])
        if (result) return result
      }
    }
    return null
  }
  const path = findPath(treeData.value, data.id)
  importSelectedParentSuitePath.value = path ? path.join(' / ') : ''
  importParentSuiteVisible.value = false
}

// 处理导出用例集选择
const handleExportCaseSuiteSelect = (data) => {
  if (data.type === 'suite') {
    importExportForm.suite_id = data.id
    // 更新显示路径
    const findPath = (nodes, id, path = []) => {
      for (const node of nodes) {
        if (node.id === id) {
          return [...path, node.suite_name]
        }
        if (node.children && node.children.length) {
          const result = findPath(node.children, id, [...path, node.suite_name])
          if (result) return result
        }
      }
      return null
    }
    const path = findPath(treeData.value, data.id)
    exportSelectedCaseSuitePath.value = path ? path.join(' / ') : ''
    exportCaseSuiteVisible.value = false
  }
}

// 选择导出路径
const selectExportPath = () => {
  // 在实际应用中，这里应该调用系统文件选择对话框
  // 由于浏览器限制，我们可以模拟一个路径选择
  const defaultPath = `D:/测试用例_${new Date().toISOString().slice(0, 10)}.xlsx`
  importExportForm.targetPath = defaultPath
  ElMessage.success(`已设置默认导出路径：${defaultPath}`)
}

// 处理导入导出操作
const handleImportExportAction = async () => {
  try {
    if (importExportForm.type === 'import') {
      // 处理导入逻辑
      if (!importExportForm.fileName) {
        ElMessage.error('请选择要导入的文件')
        return
      }
      if (!importExportForm.parent_id) {
        ElMessage.error('请选择导入的目标位置')
        return
      }
      if (!importedFile.value) {
        ElMessage.error('请选择要导入的文件')
        return
      }
      
      // 设置导入状态为true
      isImporting.value = true
      
      // 显示导入进度提示
      const loading = ElLoading.service({
        lock: true,
        text: '正在导入测试用例，请稍候...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      // 处理导入的文件
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const sheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[sheetName]
          
          // 解析Excel数据
          const excelData = XLSX.utils.sheet_to_json(worksheet)
          
          if (excelData.length === 0) {
            ElMessage.warning('Excel文件中没有测试用例数据')
            // 关闭加载提示和重置状态
            loading.close()
            isImporting.value = false
            return
          }
          
          // 获取当前登录用户信息
          const { userInfo } = useUserStore()
          
          // 从Excel数据中获取项目、迭代、需求信息（取第一条数据的值，因为同一Excel中值相同）
          const firstItem = excelData[0]
          const projectName = firstItem['所属项目'] || ''
          const iterationName = firstItem['迭代'] || ''
          const requirementName = firstItem['需求'] || ''
          
          // 创建测试套件名称（使用文件名，去掉后缀）
          const suiteName = importExportForm.fileName.replace(/\.(xlsx|xls)$/, '')
          
          // 创建测试套件
          const suiteData = {
            suite_name: suiteName,
            type: 'suite', // 用例集类型
            parent_id: importExportForm.parent_id,
            // 项目相关字段：暂时使用空值，后续可扩展为从名称映射到ID
            project_id: null,
            version_requirement_id: null,
            iteration_id: null
          }
          
          const createSuiteResponse = await createTestSuite(suiteData)
          const newSuiteId = createSuiteResponse.data.id
          
          // 处理导入的用例数据
          let importedCount = 0
          let errorCount = 0
          
          // 遍历处理每条数据
          for (const item of excelData) {
            try {
              // 将中文状态转换为对应的状态值
              const statusValue = statusOptions.find(option => option.label === item['状态'])?.value || ''
              
              // 构建完整的用例数据
              const caseData = {
                case_number: item['用例编号'] || '',
                case_name: item['用例名称'] || '',
                case_description: item['用例描述'] || '', // 添加用例描述字段
                priority: item['优先级'] || 'P1',
                status: statusValue,
                preconditions: item['前置条件'] || '',
                test_data: item['测试数据'] || '',
                steps: item['操作步骤'] || '',
                expected_result: item['预期结果'] || '',
                actual_result: item['实际结果'] || '',
                suite_id: newSuiteId,
                // 项目相关字段：暂时使用空值，后续可扩展为从名称映射到ID
                project_id: null,
                version_requirement_id: null,
                iteration_id: null
              }
              
              // 调用API创建测试用例
              await createTestCase(caseData)
              importedCount++
              // 添加延迟，避免请求过于频繁
              await new Promise(resolve => setTimeout(resolve, 100))
            } catch (error) {
              console.error('导入单条测试用例失败:', error)
              errorCount++
            }
          }
          
          // 刷新用例树
          await loadTreeData()
          
          // 关闭加载提示和重置状态
          loading.close()
          isImporting.value = false
          
          // 显示导入结果
          ElMessage.success(`成功导入 ${importedCount} 条测试用例，失败 ${errorCount} 条`)
          
          // 关闭对话框
          importExportVisible.value = false
        } catch (error) {
          console.error('导入测试用例失败:', error)
          // 关闭加载提示和重置状态
          loading.close()
          isImporting.value = false
          ElMessage.error('导入测试用例失败，请检查文件格式和内容')
        }
      }
      reader.readAsArrayBuffer(importedFile.value)
    } else if (importExportForm.type === 'export') {
      // 处理导出逻辑
      if (!importExportForm.suite_id) {
        ElMessage.error('请选择要导出的用例集')
        return
      }
      
      // 调用现有的导出Excel函数
      handleExportExcel()
      importExportVisible.value = false
    }
  } catch (error) {
    console.error('导入导出操作失败:', error)
    ElMessage.error('操作失败，请重试')
  }
}

// 用例内联编辑相关方法
const startCaseEdit = (row, field) => {
  editingCaseId.value = row.id
  editingField.value = field
  editingValue.value = row[field] || ''
  
  // 跟踪是否正在进行拖动选择操作
  let isDragging = false
  
  // 添加鼠标按下事件监听，检测是否在编辑区域内开始拖动
  const handleMouseDown = (event) => {
    const editInputs = document.querySelectorAll('.el-table__cell .el-input, .el-table__cell .el-textarea, .el-table__cell .el-select')
    const isInside = Array.from(editInputs).some(input => input.contains(event.target))
    if (isInside) {
      isDragging = true
    }
  }
  
  // 添加鼠标释放事件监听，重置拖动状态
  const handleMouseUp = () => {
    isDragging = false
  }
  
  // 添加点击外部区域取消编辑的事件监听
  const handleClickOutside = (event) => {
    // 如果是拖动选择操作，不取消编辑
    if (isDragging) {
      return
    }
    
    const editInputs = document.querySelectorAll('.el-table__cell .el-input, .el-table__cell .el-textarea, .el-table__cell .el-select')
    const isClickInside = Array.from(editInputs).some(input => input.contains(event.target))
    
    if (!isClickInside) {
      cancelCaseEdit()
      // 移除所有事件监听器
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('mousedown', handleMouseDown)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }
  
  // 延迟添加事件监听，避免触发当前点击事件
  setTimeout(() => {
    document.addEventListener('click', handleClickOutside)
    document.addEventListener('mousedown', handleMouseDown)
    document.addEventListener('mouseup', handleMouseUp)
  }, 0)
  
  // 保存事件监听器引用，以便后续移除
  window.__editClickOutsideHandler = handleClickOutside
  window.__editMouseDownHandler = handleMouseDown
  window.__editMouseUpHandler = handleMouseUp
}

const saveCaseEdit = async (row) => {
  try {
    // 如果编辑的是用例编号，验证格式
    if (editingField.value === 'case_number') {
      const value = editingValue.value.trim()
      const regex = /^.+-.+-.+\d{3}$/
      if (!regex.test(value)) {
        ElMessage.error('用例编号格式不正确，应为：xxx-xxx-xxx001~xxx-xxx-xxx999')
        return
      } else {
        // 验证数字部分在1-999之间
        const numRegex = /\d{3}$/
        const match = value.match(numRegex)
        if (match) {
          const num = parseInt(match[0])
          if (num < 1 || num > 999) {
            ElMessage.error('用例编号数字部分必须在001-999之间')
            return
          }
        } else {
          ElMessage.error('用例编号格式不正确，应为：xxx-xxx-xxx001~xxx-xxx-xxx999')
          return
        }
      }
    }
    
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
    
    // 移除所有事件监听器
    if (window.__editClickOutsideHandler) {
      document.removeEventListener('click', window.__editClickOutsideHandler)
      window.__editClickOutsideHandler = null
    }
    if (window.__editMouseDownHandler) {
      document.removeEventListener('mousedown', window.__editMouseDownHandler)
      window.__editMouseDownHandler = null
    }
    if (window.__editMouseUpHandler) {
      document.removeEventListener('mouseup', window.__editMouseUpHandler)
      window.__editMouseUpHandler = null
    }
  } catch (error) {
    console.error('更新测试用例失败:', error)
    ElMessage.error('更新测试用例失败')
  }
}

// 取消用例编辑
const cancelCaseEdit = () => {
  editingCaseId.value = null
  editingField.value = ''
  editingValue.value = ''
  
  // 移除所有事件监听器
  if (window.__editClickOutsideHandler) {
    document.removeEventListener('click', window.__editClickOutsideHandler)
    window.__editClickOutsideHandler = null
  }
  if (window.__editMouseDownHandler) {
    document.removeEventListener('mousedown', window.__editMouseDownHandler)
    window.__editMouseDownHandler = null
  }
  if (window.__editMouseUpHandler) {
    document.removeEventListener('mouseup', window.__editMouseUpHandler)
    window.__editMouseUpHandler = null
  }
}

// 状态选项
const statusOptions = [
  { label: '未执行', value: '' },
  { label: '通过', value: 'pass' },
  { label: '失败', value: 'fail' },
  { label: '阻塞', value: 'blocked' },
  { label: '不适用', value: 'not_applicable' }
]

// 处理状态变化
const handleStatusChange = async (row) => {
  try {
    await updateTestCase(row.id, { status: row.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('状态更新失败')
  }
}

const handleCellClick = () => {
  // 点击单元格时关闭编辑状态
  cancelCaseEdit()
}

// 切换选择模式
const toggleSelectionMode = () => {
  showSelection.value = true
  selectedCases.value = []
  // 重置选中ID集合
  selectedCaseIds.value = new Set()
}

// 取消选择模式
const cancelSelectionMode = () => {
  showSelection.value = false
  selectedCases.value = []
  selectedCaseIds.value = new Set()
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  // 更新选中的用例数组（当前页）
  selectedCases.value = selection
}

// 处理单个用例选中状态变化
const handleSelect = (selection, row) => {
  if (selection.includes(row)) {
    // 选中，添加到集合
    selectedCaseIds.value.add(row.id)
  } else {
    // 取消选中，从集合移除
    selectedCaseIds.value.delete(row.id)
  }
}

// 获取所有测试用例ID
const getAllCaseIds = async (suiteId) => {
  if (!suiteId) return []
  
  let allIds = []
  let page = 1
  const pageSize = 1000 // 每次查询1000条
  
  try {
    while (true) {
      const response = await getSuiteCases(suiteId, {
        page: page,
        page_size: pageSize
      })
      
      const currentIds = response.data.items.map(item => item.id)
      allIds = [...allIds, ...currentIds]
      
      if (currentIds.length < pageSize) {
        // 已经获取到所有数据
        break
      }
      
      page++
    }
  } catch (error) {
    console.error('获取所有测试用例ID失败:', error)
    ElMessage.error('获取测试用例数据失败')
  }
  
  return allIds
}

// 处理全选状态变化
const handleSelectAll = async (selection) => {
  if (!selectedSuite.value || selectedSuite.value.type !== 'suite') {
    return
  }
  
  const currentPageIds = new Set(testCases.value.map(item => item.id))
  
  if (selection.length >= currentPageIds.size) {
    // 全选，获取所有分页的测试用例ID
    const allIds = await getAllCaseIds(selectedSuite.value.id)
    selectedCaseIds.value = new Set(allIds)
    
    // 更新当前页的选中状态
    nextTick(() => {
      if (caseTableRef.value) {
        testCases.value.forEach(caseItem => {
          caseTableRef.value.toggleRowSelection(caseItem, true)
        })
      }
    })
  } else {
    // 取消全选，清空所有选中的ID
    selectedCaseIds.value.clear()
    
    // 更新当前页的选中状态
    nextTick(() => {
      if (caseTableRef.value) {
        testCases.value.forEach(caseItem => {
          caseTableRef.value.toggleRowSelection(caseItem, false)
        })
      }
    })
  }
}

// 删除选中的用例
const handleDeleteSelection = async () => {
  if (selectedCaseIds.value.size === 0) {
    ElMessage.warning('请先选择要删除的测试用例')
    return
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${selectedCaseIds.value.size} 个测试用例吗？删除后将无法恢复。`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 批量删除用例
      const caseIds = Array.from(selectedCaseIds.value)
      await batchDeleteTestCases(caseIds)
      ElMessage.success('测试用例已删除')
      
      // 清空选中集合
      selectedCaseIds.value.clear()
      
      // 重新加载测试用例
      loadTestCases(selectedSuite.value?.id)
      
      // 重置选择模式
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

<style scoped>
  .case-number-input-group {
    display: flex;
    align-items: center;
    width: 100%;
  }
  
  .case-number-part {
    flex: 1;
    margin: 0;
    min-width: 0;
  }
  
  .case-number-part.number-part {
    width: 100px;
    flex: none;
  }
  
  .case-number-separator {
    margin: 0 5px;
    color: #606266;
    width: 10px;
    text-align: center;
  }
</style>

<style lang="scss" scoped>
/* 内联编辑输入框样式优化 */
:deep(.el-table__cell) {
  position: relative;
  
  /* 普通输入框样式 - 与文本域保持一致 */
  .el-input:not(.el-input--textarea) {
    width: 100%;
    margin: 0;
    
    .el-input__wrapper {
      box-shadow: none;
      border: 1px solid #ebeef5;
      border-radius: 0;
      padding: 10px;
      background-color: transparent;
      min-height: auto;
      
      &:hover,
      &.is-focus {
        box-shadow: none;
        border-color: #409eff;
      }
    }
    
    .el-input__inner {
      border: none;
      box-shadow: none;
      background: transparent;
      padding: 0;
      height: auto;
      line-height: 1.5;
      font-size: inherit;
      color: inherit;
      text-align: center;
      resize: none;
    }
  }
  
  /* 文本域样式 */
  .el-textarea,
  .el-input--textarea {
    width: 100%;
    margin: 0;
    
    .el-textarea__wrapper,
    .el-input__wrapper {
      box-shadow: none;
      border: 1px solid #ebeef5;
      border-radius: 0;
      padding: 10px;
      min-height: auto;
      background-color: transparent;
      
      &:hover,
      &.is-focus {
        box-shadow: none;
        border-color: #409eff;
      }
    }
    
    .el-textarea__inner,
    .el-input__inner {
      border: none;
      box-shadow: none;
      background: transparent;
      padding: 0;
      resize: none;
      font-size: inherit;
      color: inherit;
      line-height: 1.5;
      text-align: center;
      min-height: auto;
    }
  }
  
  /* 下拉选择框样式 */
  .el-select {
    width: 100%;
    margin: 0;
    
    .el-select__wrapper {
      box-shadow: none;
      border: 1px solid #ebeef5;
      border-radius: 0;
      padding: 10px;
      background-color: transparent;
      min-height: auto;
      
      &:hover,
      &.is-focus {
        box-shadow: none;
        border-color: #409eff;
      }
    }
    
    .el-select__input {
      font-size: inherit;
      color: inherit;
      height: auto;
      line-height: 1.5;
    }
  }
  
  /* 确保非编辑状态下的文本与编辑状态一致 */
  > div {
    padding: 10px;
    text-align: center;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
  }
  
  /* 确保编辑状态下的文本也居中显示 */
  .el-input__inner,
  .el-textarea__inner {
    text-align: center;
  }
}

.test-case-management {
  padding: 0;
  background-color: white;
  min-height: 100vh;
  overflow-x: auto;
}

/* 进度条样式 */
.panel-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.case-progress-container {
  flex: 1;
  min-width: 300px;
  background-color: transparent;
  border-radius: 4px;
  padding: 5px 0;
  box-sizing: border-box;
  position: relative;
}

.progress-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  font-size: 14px;
  color: #303133;
}

.progress-title {
  font-weight: 500;
}

.progress-percentage {
  color: #606266;
  font-size: 12px;
}

.progress-wrapper {
  position: relative;
  margin: 20px 0 20px 0; /* 增加上方空白，为执行情况文字预留空间 */
  height: 30px; /* 固定高度 */
  display: flex;
  align-items: center;
}

/* 执行情况文字样式 */
.progress-execution-info {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  background-color: transparent;
  z-index: 10;
}

.progress-bar {
  flex: 1;
  margin-right: 35px; /* 右侧间隔 */
  display: flex;
  height: 9px; /* 进度条高度 */
  border-radius: 6px;
  overflow: hidden;
  background-color: #e4e7ed;
  transition: height 0.2s ease;
  position: relative;
  z-index: 1;
  
  &:hover {
    height: 11px; /* 悬停高度 */
  }
}

/* 右侧进度数据 */
.progress-data-right {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: #606266;
  margin-left: 5px; /* 减小与进度条的间隔 */
  white-space: nowrap;
  pointer-events: auto;
}

.progress-segment {
  height: 100%;
  transition: width 0.3s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.1) 0%, transparent 100%);
  }
}

/* 水平分布的属性标签 */
.progress-labels-horizontal {
  position: absolute;
  left: 0;
  right: 10px; /* 右侧预留空间，与进度条保持一致 */
  top: 100%;
  margin-top: 8px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  z-index: 2;
}

/* 水平分布的状态项 */
:deep(.stat-item.horizontal) {
  margin: 0;
  padding: 2px 5px;
  border-radius: 3px;
  background-color: #f5f7fa !important;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #ecf5ff !important;
    color: #409eff;
  }
}

.label-text {
  pointer-events: auto;
}

/* 状态颜色 */
.progress-segment.status-pass {
  background-color: #67c23a;
}

.progress-segment.status-fail {
  background-color: #f56c6c;
}

.progress-segment.status-blocked {
  background-color: #e6a23c;
}

.progress-segment.status-not_applicable {
  background-color: #9370db;
}

.progress-segment.status-none {
  background-color: #e4e7ed;
}

.progress-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 12px;
  color: #606266;
  justify-content: flex-end;
}

:deep(.stat-item) {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 1px 0;
  background-color: transparent !important;
  border-radius: 0 !important;
  transition: all 0.2s ease;
  cursor: pointer;
  box-shadow: none !important;
  font-size: 12px;
  line-height: 1;
  
  &:hover {
    background-color: transparent !important;
    transform: none !important;
    box-shadow: none !important;
    color: #409eff;
  }
}

:deep(.stat-item::before) {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
}

:deep(.stat-item.status-pass::before) {
  background-color: #67c23a;
}

:deep(.stat-item.status-fail::before) {
  background-color: #f56c6c;
}

:deep(.stat-item.status-blocked::before) {
  background-color: #e6a23c;
}

:deep(.stat-item.status-not_applicable::before) {
  background-color: #9370db;
}

:deep(.stat-item.status-none::before) {
  background-color: #e4e7ed;
}

.page-header {
  margin-bottom: 0;
  padding: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
  
  .header-content {
    h1 {
      margin: 0 0 2px 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
    // 描述删掉了
    .description {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
}

.main-content {
    display: flex;
    align-items: stretch;
    flex-wrap: nowrap;
    min-width: 900px;
    height: calc(100vh - 100px);
    margin-bottom: 0;
    
    .left-panel {
      min-width: 280px;
      max-width: 70%;
      width: fit-content;
      height: 100%;
      background: white;
      box-shadow: none;
      border-right: 1px solid #e4e7ed;
      display: flex;
      flex-direction: column;
      transition: all 0.3s ease;
      flex-shrink: 0;
      
      /* 收起状态 */
      &.collapsed {
        min-width: 50px;
        width: 50px;
        
        .panel-header {
          justify-content: center;
          
          .el-input {
            display: none;
          }
          
          .header-actions {
            .el-button:not(:last-child) {
              display: none; /* 隐藏除了最后一个按钮（展开按钮）外的所有按钮 */
            }
          }
        }
        
        .tree-container {
          display: none;
        }
      }
      
      .panel-header {
          padding: 12px 15px;
          border-bottom: 1px solid #f0f2f5;
          display: flex;
          align-items: center;
          gap: 8px;
          background-color: white;
          flex-shrink: 0;
          
          .el-input {
            flex: 1;
            min-width: 0;
            
            /* 增大搜索框 */
            --el-input-height: 32px;
            transition: all 0.3s ease;
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
            align-items: center;
            flex-shrink: 0;
            width: fit-content;
          }
          
          .header-actions .el-button {
            padding: 2px;
            min-width: 26px; /* 按钮大小 */
            height: 26px; /* 按钮高度 */
            font-size: 16px; /* 图标大小 */
            display: flex;
            justify-content: center;
            align-items: center;
          }
        }
    
    .tree-container {
      flex: 1;
      padding: 15px 15px 15px 20px;
      overflow: auto;
      background-color: #ffffff;
      width: fit-content;
      min-width: 100%;
      transition: all 0.3s ease;
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
    height: 100%;
    background: white;
    box-shadow: none;
    display: flex;
    flex-direction: column;
    flex-shrink: 1;
    position: relative;
    
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
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    
    .table-wrapper {
      flex: 1;
      overflow: auto;
      margin-bottom: 15px;
    }
    
    .table-wrapper :deep(.el-table) {
  width: 100%;
}

/* 为特定属性列添加左对齐样式 */
/* 测试数据列 */
.table-wrapper :deep(.el-table__header-wrapper th[aria-label='测试数据']),
.table-wrapper :deep(.el-table__body-wrapper td:nth-child(7)) {
  text-align: left !important;
}

/* 前置条件列 */
.table-wrapper :deep(.el-table__header-wrapper th[aria-label='前置条件']),
.table-wrapper :deep(.el-table__body-wrapper td:nth-child(8)) {
  text-align: left !important;
}

/* 操作步骤列 */
.table-wrapper :deep(.el-table__header-wrapper th[aria-label='操作步骤']),
.table-wrapper :deep(.el-table__body-wrapper td:nth-child(9)) {
  text-align: left !important;
}

/* 预期结果列 */
.table-wrapper :deep(.el-table__header-wrapper th[aria-label='预期结果']),
.table-wrapper :deep(.el-table__body-wrapper td:nth-child(10)) {
  text-align: left !important;
}

/* 实际结果列 */
.table-wrapper :deep(.el-table__header-wrapper th[aria-label='实际结果']),
.table-wrapper :deep(.el-table__body-wrapper td:nth-child(11)) {
  text-align: left !important;
}
    
    .table-wrapper :deep(.el-table__body-wrapper) {
      overflow: auto;
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

/* 状态下拉列表样式 */
.status-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-color-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

/* 不同状态的颜色 */
.status-pass {
  background-color: #67c23a;
}

.status-fail {
  background-color: #f56c6c;
}

.status-blocked {
  background-color: #e6a23c;
}

.status-not_applicable {
  background-color: #9370db;
}

.status-none {
  background-color: #e4e7ed;
}

/* 状态选项内容 */
.status-option-content {
  display: flex;
  align-items: center;
}

.status-option-text {
  flex: 1;
}

/* 下拉列表样式 */
.status-select-popper {
  min-width: 120px;
}

/* 标题用例数量样式 */
.case-count-title {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
  margin-left: 8px;
}

/* 分页组件样式 */
.pagination-container {
  position: fixed;
  bottom: 0;
  left: 230px; /* 与左侧菜单栏实际宽度对齐 */
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

/* 为固定分页留出空间 */
.main-content {
  margin-bottom: 70px;
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

/* 表单帮助文本样式 */
.form-help-text {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* 脑图缺省页面样式 */
.mindmap-view {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.mindmap-default-page {
  width: 100%;
  max-width: 600px;
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>