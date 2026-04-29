<template>
  <div class="test-case-management">
    <div class="page-header">
      <div class="header-content">
        <h1>用例管理</h1>
      </div>
      <div class="header-actions">
        <el-button type="success" icon="MagicStick" :loading="isGeneratingAny" @click="handleGenerateCases">
          AI生成用例
        </el-button>
        <el-button type="primary" icon="Upload" @click="openImportSuiteDialog">
          导入用例集
        </el-button>
        <el-select
          v-model="filterProjectId"
          placeholder="所属项目"
          filterable
          class="header-project-select"
          @change="onProjectFilterChange"
        >
          <el-option
            v-for="p in projectOptions"
            :key="p.id"
            :label="p.project_name"
            :value="p.id"
          />
        </el-select>
      </div>
    </div>

    <div class="main-content">
      <!-- 收起状态下的展开按钮 -->
      <div v-if="isLeftPanelCollapsed" class="collapsed-expand-btn" @click="isLeftPanelCollapsed = false">
        <el-icon><DArrowRight /></el-icon>
      </div>

      <!-- 左侧：文件夹目录树 -->
      <div class="left-panel" :class="{ collapsed: isLeftPanelCollapsed }">
        <div class="panel-header">
          <el-input
            v-model="searchText"
            placeholder="搜索文件夹"
            prefix-icon="Search"
            clearable
            size="small"
          />
          <el-tooltip content="折叠面板">
            <el-button
              size="small"
              text
              icon="DArrowLeft"
              @click="isLeftPanelCollapsed = true"
            />
          </el-tooltip>
          </div>
        <div class="tree-container">
          <el-tree
            ref="folderTreeRef"
            :data="folderTree"
            :props="treeProps"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            :filter-node-method="filterNode"
            default-expand-all
            draggable
            :allow-drag="allowFolderDrag"
            :allow-drop="allowFolderDrop"
            @node-click="handleFolderClick"
            @node-contextmenu="handleFolderContextMenu"
            @node-drop="handleFolderDrop"
          >
            <template #default="{ node, data }">
              <span class="tree-node-label">
                <el-icon><Folder /></el-icon>
                <span>{{ data.suite_name }}{{ data._virtual ? '' : `（${data.suite_count ?? 0}）` }}</span>
              </span>
            </template>
          </el-tree>
        </div>
        <div class="recycle-trigger" @click="showRecycleDrawer = true">
          <el-icon><Delete /></el-icon>
          <span>回收站</span>
        </div>
      </div>

      <!-- 右侧：用例集列表  -->
      <div class="right-panel">
        <div v-if="selectedFolder" class="panel-content">
          <div class="table-toolbar">
            <div class="toolbar-left-area">
            <el-input
                v-model="caseSetSearch"
                placeholder="搜索用例集名称"
                prefix-icon="Search"
              clearable
                style="width: 260px"
                @clear="loadCaseSets"
                @keyup.enter="loadCaseSets"
              />
              <el-select
                v-model="reviewStatusFilter"
                placeholder="评审状态"
                clearable
                style="width: 140px; margin-left: 10px"
                @change="loadCaseSets"
              >
                <el-option label="未评审" value="not_reviewed" />
                <el-option label="待评审" value="pending" />
                <el-option label="评审中" value="in_review" />
                <el-option label="已通过" value="completed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </div>
        </div>

            <el-table
            ref="caseSetTableRef"
            :data="caseSets"
            v-loading="tableLoading"
              border
            stripe
            style="width: 100%"
            :row-class-name="getCaseSetRowClassName"
            @row-click="handleRowClick"
          >
            <el-table-column prop="suite_name" label="用例集名称" min-width="150" align="center">
                <template #default="{ row }">
                <div class="suite-name-cell" :class="{ 'suite-name-cell--editing': editingSuiteId === row.id }">
                  <template v-if="editingSuiteId === row.id">
                    <el-input
                      ref="suiteNameInputRef"
                      v-model="editingSuiteName"
                      size="small"
                      maxlength="30"
                      show-word-limit
                      placeholder="用例集名称"
                      @click.stop
                      @blur="saveSuiteNameEdit"
                      @keyup.enter="saveSuiteNameEdit"
                      @keyup.esc="cancelSuiteNameEdit"
                    />
                  </template>
                  <template v-else>
                    <el-link type="primary" :underline="false" @click.stop="openMindmap(row)">
                      {{ row.suite_name }}
                    </el-link>
                    <el-button
                      type="primary"
                      link
                      class="suite-name-edit-btn"
                      :disabled="!!generatingMap[row.id]"
                      @click.stop="startEditSuiteName(row)"
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                    <template v-if="generatingMap[row.id]">
                      <el-tooltip :content="generatingMap[row.id]?.message || '生成中'" placement="top">
                        <span class="generating-progress-badge">
                          <el-icon class="is-loading"><Loading /></el-icon>
                          <span class="generating-pct">{{ generatingMap[row.id]?.progress ?? 0 }}%</span>
                        </span>
                      </el-tooltip>
                    </template>
                  </template>
                </div>
                </template>
              </el-table-column>
            <el-table-column prop="case_count" label="用例数量" width="85" align="center" />
            <el-table-column prop="review_status" label="状态" width="85" align="center">
                <template #default="{ row }">
                <el-tag :type="reviewStatusType(row.review_status)" size="small">
                  {{ reviewStatusLabel(row.review_status) }}
                  </el-tag>
                </template>
              </el-table-column>
            <el-table-column prop="creator_name" label="创建人" width="95" align="center" />
            <el-table-column prop="updated_at" label="更新时间" width="110" sortable align="center">
                <template #default="{ row }">
                {{ formatTime(row.updated_at) }}
                </template>
              </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="110" sortable align="center">
                <template #default="{ row }">
                {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
            <el-table-column prop="version_requirement_name" label="所属需求" min-width="140" align="center">
                <template #default="{ row }">
                {{ row.version_requirement_name || '-' }}
                </template>
              </el-table-column>
            <el-table-column label="操作" width="195" fixed="right" align="center">
                <template #default="{ row }">
                <div class="action-btns">
                  <template v-if="generatingMap[row.id]">
                    <div class="generating-inline-progress">
                      <el-progress
                        :percentage="generatingMap[row.id]?.progress ?? 0"
                        :stroke-width="14"
                        :text-inside="true"
                        striped
                        striped-flow
                        style="flex: 1; min-width: 80px"
                      />
                      <el-button size="small" text type="danger" @click.stop="handleDeleteSuite(row)">删除</el-button>
                    </div>
                  </template>
                  <template v-else>
                    <el-tooltip :content="getReviewButtonTooltip(row)" placement="top">
                      <el-button size="small" text type="primary" @click.stop="handleReviewSuite(row)">评审</el-button>
                    </el-tooltip>
                    <el-button size="small" text type="primary" @click.stop="handleMoveSuite(row)">移动</el-button>
                    <el-button size="small" text type="success" @click.stop="handleCopySuite(row)">复制</el-button>
                    <el-button size="small" text type="danger" @click.stop="handleDeleteSuite(row)">删除</el-button>
                  </template>
                </div>
                </template>
              </el-table-column>
            </el-table>

          <div class="pagination-bar">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="pagination.total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadCaseSets"
              @current-change="loadCaseSets"
            />
          </div>
        </div>

        <div v-else class="empty-tip">
          <el-empty description="请在左侧选择一个文件夹" />
      </div>
    </div>
    </div>

    <!-- 新建文件夹对话框 -->
    <el-dialog v-model="folderDialogVisible" :title="folderDialogTitle" width="440px">
      <el-alert
        v-if="!folderForm.id && (folderForm.parentId || selectedFolder)"
        :title="`将在「${folderParentName}」下创建文件夹`"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-form :model="folderForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="folderForm.name" placeholder="请输入文件夹名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFolder">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新建用例集对话框 -->
    <el-dialog v-model="suiteDialogVisible" title="新建用例集" width="560px" @open="onSuiteDialogOpen">
      <el-form :model="suiteForm" label-width="100px">
        <el-form-item label="所属项目" required>
          <el-select
            v-model="suiteForm.project_id"
            placeholder="选择项目"
            filterable
            style="width: 100%"
            disabled
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="p.project_name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属文件夹" required>
          <el-tree-select
            v-model="suiteForm.parentId"
            :data="suiteFormFolderTree"
            :props="{ label: 'suite_name', value: 'id' }"
            node-key="id"
            placeholder="选择存放位置（默认当前选中文件夹）"
            style="width: 100%"
            check-strictly
            :render-after-expand="false"
            default-expand-all
            filterable
            clearable
          />
        </el-form-item>
        <el-form-item label="用例集名称" required>
          <el-input v-model="suiteForm.suite_name" placeholder="请输入用例集名称" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" :rows="3" placeholder="选填，用于说明用例集用途或范围" />
        </el-form-item>
        <el-form-item label="关联需求">
          <el-select
            v-model="suiteForm.version_requirement_id"
            placeholder="选择关联需求（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="r in requirementOptions"
              :key="r.id"
              :label="r.requirement_name"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSuite">确定</el-button>
      </template>
    </el-dialog>

    <!-- 移动用例集对话框：目录过多时树区域可滚动 -->
    <el-dialog v-model="moveDialogVisible" title="移动用例集" width="440px">
      <p style="margin-bottom: 12px">选择目标文件夹：</p>
      <div class="move-dialog-tree-wrap">
        <el-tree
          :data="folderTree"
          :props="treeProps"
          node-key="id"
          highlight-current
          default-expand-all
          @node-click="(data) => (moveTargetId = data.id)"
        >
          <template #default="{ data }">
            <span><el-icon><Folder /></el-icon> {{ data.suite_name }}</span>
          </template>
        </el-tree>
      </div>
      <template #footer>
        <el-button @click="moveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmMove">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI生成用例对话框 -->
    <el-dialog v-model="generateDialogVisible" title="AI 生成用例" width="600px" @open="onGenerateDialogOpen">
      <el-form :model="generateForm" label-width="110px">
        <el-form-item label="项目" required>
          <el-select
            v-model="generateForm.projectId"
            placeholder="请先选择项目"
            filterable
            style="width: 100%"
            @change="onGenerateProjectChange"
          >
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成方式" required>
          <el-radio-group v-model="generateForm.mode">
            <el-radio value="append">追加到已有用例集</el-radio>
            <el-radio value="new">创建新用例集并生成</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="目标文件夹" required>
          <el-tree-select
            v-model="generateForm.folderId"
            :data="generateFolderTree"
            :props="{ label: 'suite_name', value: 'id' }"
            node-key="id"
            :placeholder="generateForm.projectId ? '请选择文件夹' : '请先选择项目'"
            style="width: 100%"
            clearable
            check-strictly
            :render-after-expand="false"
            default-expand-all
            filterable
            :disabled="!generateForm.projectId"
            @change="onGenerateFolderChange"
          />
          <div v-if="generateForm.projectId && !generateFolderTree.length" class="form-tip">该项目下暂无文件夹，可先选择「创建新用例集并生成」</div>
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'append'" label="用例集选择" required>
          <el-select
            v-model="generateForm.suiteId"
            placeholder="选择该目录下的用例集"
            style="width: 100%"
            clearable
            filterable
            :disabled="generateForm.folderId == null"
          >
            <el-option
              v-for="s in generateSuiteOptions"
              :key="s.id"
              :label="s.suite_name"
              :value="s.id"
            />
          </el-select>
          <div v-if="generateForm.folderId != null && !generateSuiteOptions.length" class="form-tip">该目录下暂无用例集</div>
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'new'" label="新用例集名称" required>
          <el-input v-model="generateForm.newSuiteName" placeholder="请输入新用例集名称" maxlength="30" show-word-limit clearable />
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'new'" label="迭代">
          <el-select
            v-model="generateForm.iterationId"
            placeholder="请选择迭代（可选）"
            filterable
            clearable
            style="width: 100%"
            :disabled="!generateForm.projectId"
            @change="onGenerateIterationChange"
          >
            <el-option v-for="it in generateIterationOptions" :key="it.id" :label="it.iteration_name" :value="it.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'new'" label="所属需求" required>
          <el-select
            v-model="generateForm.requirementId"
            placeholder="请选择需求"
            filterable
            clearable
            style="width: 100%"
            :disabled="!generateForm.projectId"
          >
            <el-option v-for="r in generateRequirementOptions" :key="r.id" :label="r.requirement_name" :value="r.id" />
          </el-select>
          <div v-if="generateForm.projectId && !generateRequirementOptions.length" class="form-tip">该项目/迭代下暂无需求</div>
        </el-form-item>
        <el-form-item label="需求文档" required>
          <el-upload
            ref="generateUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".txt,.md,.doc,.docx"
            :on-change="onGenerateFileChange"
            :on-remove="onGenerateFileRemove"
            :on-exceed="onGenerateUploadExceed"
          >
            <el-button type="primary" plain>上传需求文档</el-button>
            <template #tip>
              <div class="upload-tip">支持 .txt、.md、.doc、.docx，上传后将读取文档内容用于生成用例</div>
            </template>
          </el-upload>
          <div v-if="generateForm.documentContent || generateDocxFile" class="document-preview">
            <template v-if="generateForm.documentContent">
              已加载 {{ (generateForm.documentContent || '').length }} 字，可重新上传替换
            </template>
            <template v-else>
              已选择 {{ generateDocxFile?.name }}，将在服务端解析正文与内嵌图，可重新上传替换
            </template>
          </div>
        </el-form-item>
      </el-form>
      <div class="debug-toggle-bar">
        <el-tooltip
          effect="dark"
          placement="top"
          :content="generateForm.debugMode
            ? '调试模式已开启：用例正常入库，但不会将需求文档存入知识库'
            : '正常模式：用例入库，需求文档自动存入知识库供后续生成参考'"
        >
          <div class="debug-toggle-inner">
            <el-switch
              v-model="generateForm.debugMode"
              active-text="调试模式"
              inactive-text=""
              inline-prompt
              style="--el-switch-on-color: #e6a23c;"
            />
            <el-tag v-if="generateForm.debugMode" type="warning" size="small" effect="plain" class="debug-tag">
              不存入知识库
            </el-tag>
          </div>
        </el-tooltip>
      </div>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="isGeneratingAny"
          :disabled="!canSubmitGenerate"
          @click="submitGenerate"
        >
          开始生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单遮罩：点击任意空白处关闭菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu-overlay"
      @click="hideContextMenu"
    />
    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="handleRenameFolder">重命名</div>
      <div class="context-menu-item" @click="handleCtxNewFolder">新建文件夹</div>
      <div class="context-menu-item" @click="handleCtxNewSuite">新建用例集</div>
      <div class="context-menu-item danger" @click="handleDeleteFolder">删除</div>
    </div>

    <!-- 右键新建文件夹对话框 -->
    <el-dialog v-model="ctxFolderDialogVisible" title="新建文件夹" width="440px">
      <el-form label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="ctxFolderName" placeholder="请输入文件夹名称" maxlength="30" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ctxFolderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCtxFolder">确定</el-button>
      </template>
    </el-dialog>

    <!-- 右键新建用例集对话框 -->
    <el-dialog v-model="ctxSuiteDialogVisible" title="新建用例集" width="520px">
      <el-form :model="ctxSuiteForm" label-width="100px">
        <el-form-item label="关联项目" required>
          <el-select v-model="ctxSuiteForm.project_id" placeholder="选择项目" filterable style="width: 100%" disabled>
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用例集名称" required>
          <el-input v-model="ctxSuiteForm.suite_name" placeholder="请输入用例集名称" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="ctxSuiteForm.description" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
        <el-form-item label="关联需求">
          <el-select v-model="ctxSuiteForm.version_requirement_id" placeholder="可选" clearable filterable style="width: 100%">
            <el-option v-for="r in requirementOptions" :key="r.id" :label="r.requirement_name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ctxSuiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCtxSuite">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入用例集对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入用例集" width="560px" @open="onImportDialogOpen">
      <el-form label-width="100px">
        <el-form-item label="关联项目">
          <el-select v-model="importForm.project_id" disabled style="width: 100%">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代">
          <el-select
            v-model="importForm.iteration_id"
            placeholder="请选择迭代（可选）"
            filterable
            clearable
            style="width: 100%"
            @change="onImportIterationChange"
          >
            <el-option v-for="it in importIterationOptions" :key="it.id" :label="it.iteration_name" :value="it.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属需求">
          <el-select
            v-model="importForm.requirement_id"
            placeholder="请选择需求（可选）"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option v-for="r in importRequirementOptions" :key="r.id" :label="r.requirement_name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件" required>
          <el-upload
            ref="importUploadRef"
            action=""
            :auto-upload="false"
            :limit="1"
            accept=".json,.xlsx,.xls,.csv"
            :on-change="onImportFileChange"
            :on-remove="() => (importForm.file = null)"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 JSON / Excel / CSV 格式，
                <el-link type="primary" :underline="false" @click="downloadImportTemplate">下载导入模板</el-link>
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="submitImport">确定导入</el-button>
      </template>
    </el-dialog>

    <!-- 回收站抽屉（仅用例集，按当前所属项目区分） -->
    <el-drawer v-model="showRecycleDrawer" :title="recycleDrawerTitle" size="960" direction="rtl" class="recycle-drawer">
      <div class="recycle-toolbar">
        <span class="recycle-toolbar-label">所属项目：</span>
        <el-select
          v-model="recycleFilterProjectId"
          placeholder="选择项目"
          clearable
          filterable
          class="recycle-project-select"
          @change="loadRecycled"
        >
          <el-option v-for="p in projectOptions" :key="p.id" :label="p.project_name" :value="p.id" />
        </el-select>
        <el-button
          type="danger"
          plain
          :disabled="!recycleSelectedIds.length"
          @click="batchPermanentDeleteRecycled"
        >
          全选删除
        </el-button>
      </div>
      <div v-loading="recycleLoading" class="recycle-list">
        <table class="recycle-table recycle-table-center" v-if="recycledList.length">
          <thead>
            <tr>
              <th class="col-check"><el-checkbox v-model="recycleSelectAll" @change="onRecycleSelectAllChange" /></th>
              <th class="col-path">文件夹路径</th>
              <th class="col-name">用例集名称</th>
              <th class="col-time">删除时间</th>
              <th class="col-operator">操作人</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in recycledList" :key="item.id">
              <td class="col-check">
                <el-checkbox :model-value="recycleSelectedIds.includes(item.id)" @update:model-value="(v) => toggleRecycleSelected(item.id, v)" />
              </td>
              <td class="col-path">
                <el-tooltip v-if="(item.parent_path || '').length" :content="item.parent_path" placement="top" :show-after="300">
                  <span class="cell-text">{{ item.parent_path || '—' }}</span>
                </el-tooltip>
                <span v-else class="cell-text">—</span>
              </td>
              <td class="col-name">
                <el-tooltip v-if="getRecycleRowTooltip(item)" :content="getRecycleRowTooltip(item)" placement="top" :show-after="300" popper-class="recycle-name-tooltip-multiline">
                  <span class="cell-text">{{ item.suite_name }}</span>
                </el-tooltip>
                <span v-else class="cell-text">{{ item.suite_name }}</span>
              </td>
              <td class="col-time">{{ item.deleted_at ? formatRecycleTimeFull(item.deleted_at) : '—' }}</td>
              <td class="col-operator">{{ item.creator_name || '—' }}</td>
              <td class="col-actions">
                <el-button size="small" type="primary" link @click="restoreRecycled(item.id)">恢复</el-button>
                <el-button size="small" type="danger" link @click="permanentDeleteRecycled(item)">彻底删除</el-button>
              </td>
            </tr>
          </tbody>
        </table>
        <el-empty v-if="!recycleLoading && !recycledList.length" description="回收站为空" />
      </div>
      <div v-if="recycledList.length || recyclePagination.total" class="recycle-pagination">
        <el-pagination
          v-model:current-page="recyclePagination.page"
          v-model:page-size="recyclePagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="recyclePagination.total"
          layout="total, sizes, prev, pager, next"
          @current-change="loadRecycled"
          @size-change="loadRecycled"
        />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
// 用例管理页：左侧目录树 + 右侧用例集列表，支持文件夹/用例集 CRUD、拖拽移动、回收站、AI 生成、导入导出
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Folder, DArrowRight, DArrowLeft, Loading, Delete, EditPen } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";
import {
  getFolderTree,
  getCaseSets,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  getRecycledSuites,
  restoreRecycledSuite,
  batchPermanentDeleteRecycledSuites,
  getTestSuiteDetail,
} from "@/api/testSuite";
import { moveTestSuite, copyTestSuite, importTestSuite } from "@/api/testSuite";
import { getProjects, getProjectVersionRequirements } from "@/api/project";
import { getProjectIterations } from "@/api/iteration";
import { createGenerateCasesTask, createGenerateCasesWithFiles, getTaskStatus } from "@/api/aiTasks";
import { genFileId } from "element-plus";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const folderTreeRef = ref(null);
const caseSetTableRef = ref(null);
const flashSuiteId = ref(null);
let flashClearTimer = null;
const searchText = ref("");
const isLeftPanelCollapsed = ref(false);
const selectedFolder = ref(null);
const folderTree = ref([]);

const treeProps = { children: "children", label: "suite_name" };

const caseSets = ref([]);
const tableLoading = ref(false);
const caseSetSearch = ref("");
const reviewStatusFilter = ref("");
const pagination = reactive({ page: 1, pageSize: 20, total: 0 });

const folderDialogVisible = ref(false);
const folderDialogTitle = ref("新建文件夹");
const folderForm = reactive({ name: "", id: null, parentId: null });

const suiteDialogVisible = ref(false);
const suiteFormFolderTree = ref([]);
const suiteForm = reactive({
  suite_name: "",
  description: "",
  version_requirement_id: null,
  project_id: null,
  parentId: null,
});

const moveDialogVisible = ref(false);
const moveTargetId = ref(null);
const movingSuite = ref(null);

const requirementOptions = ref([]);

const contextMenu = reactive({ visible: false, x: 0, y: 0, data: null });
const filterProjectId = ref(null);
const projectOptions = ref([]);
const showRecycleDrawer = ref(false);
/** 回收站内独立选择的所属项目，不受外层 filterProjectId 限制 */
const recycleFilterProjectId = ref(null);
const recycleLoading = ref(false);
const recycledList = ref([]);
const recyclePagination = reactive({ page: 1, pageSize: 10, total: 0 });
const recycleSelectedIds = ref([]);
const recycleSelectAll = ref(false);
/** 右键新建文件夹 */
const ctxFolderDialogVisible = ref(false);
const ctxFolderName = ref("");
let ctxFolderParentId = null;

/** 右键新建用例集 */
const ctxSuiteDialogVisible = ref(false);
const ctxSuiteForm = reactive({ project_id: null, suite_name: "", description: "", version_requirement_id: null });
let ctxSuiteParentId = null;

/** 导入用例集 */
const importDialogVisible = ref(false);
const importLoading = ref(false);
const importUploadRef = ref(null);
const importForm = reactive({ project_id: null, iteration_id: null, requirement_id: null, file: null });
const importIterationOptions = ref([]);
const importRequirementOptions = ref([]);
let importParentId = null;

const generateDialogVisible = ref(false);
const generateForm = reactive({
  projectId: null,
  iterationId: null,
  requirementId: null,
  mode: "append",
  folderId: null,
  suiteId: null,
  newSuiteName: "",
  documentContent: "",
  debugMode: false,
});
const generateFolderTree = ref([]);
const generateSuiteOptions = ref([]);
const generateIterationOptions = ref([]);
const generateRequirementOptions = ref([]);
const generateUploadRef = ref(null);
/** 选择了 .docx 时由服务端解析正文，此处保存待提交的 File */
const generateDocxFile = ref(null);
const editingSuiteId = ref(null);
const editingSuiteName = ref("");
const suiteNameInputRef = ref(null);

const canSubmitGenerate = computed(() => {
  if (!generateForm.projectId) return false;
  if (!generateForm.documentContent?.trim() && !generateDocxFile.value) return false;
  if (generateForm.mode === "append") return !!generateForm.suiteId;
  return generateForm.folderId != null && !!generateForm.newSuiteName?.trim() && !!generateForm.requirementId;
});

const generatingMap = reactive({});
const isGeneratingAny = computed(() => Object.keys(generatingMap).length > 0);

const folderParentName = computed(() => {
  if (folderForm.parentId) {
    const find = (nodes) => {
      for (const n of nodes) {
        if (n.id === folderForm.parentId) return n.suite_name;
        if (n.children?.length) { const r = find(n.children); if (r) return r; }
      }
      return null;
    };
    return find(folderTree.value) || '根目录';
  }
  return selectedFolder.value?.suite_name || '根目录';
});

const recycleDrawerTitle = computed(() => {
  if (!recycleFilterProjectId.value) return "回收站";
  const p = projectOptions.value?.find((x) => x.id === recycleFilterProjectId.value);
  return p ? `回收站（${p.project_name}）` : "回收站";
});

/** 为弹窗构建带「根」的树，便于选择「根目录」或某文件夹 */
function buildFolderTreeWithRoot() {
  const tree = folderTree.value || [];
  return [{ id: 0, suite_name: "根", type: "folder", parent_id: null, children: tree, _virtual: true }];
}

watch(searchText, (val) => {
  folderTreeRef.value?.filter(val);
});

function filterNode(value, data) {
  if (!value) return true;
  return data.suite_name?.toLowerCase().includes(value.toLowerCase());
}

async function loadFolderTree() {
  try {
    const params = filterProjectId.value ? { project_id: filterProjectId.value } : {};
    const res = await getFolderTree(params);
    const payload = res.data || {};
    const tree = payload.tree || payload || [];
    const rootSuiteCount = payload.root_suite_count || 0;

    const treeArr = Array.isArray(tree) ? tree : [];
    folderTree.value = treeArr;
  } catch {
    ElMessage.error("加载文件夹目录失败");
  }
}

/**
 * 加载用例集列表。
 * locateId 不为 null 时：全量拉取（size=10000），计算目标用例集所在分页并切片展示，
 * 实现分页定位；否则按当前分页参数正常加载。
 */
async function loadCaseSets(locateId = null) {
  if (!selectedFolder.value) return;
  tableLoading.value = true;
  try {
    const params = {
      page: locateId ? 1 : pagination.page,
      page_size: locateId ? 10000 : pagination.pageSize,
      search: caseSetSearch.value,
      review_status: reviewStatusFilter.value || undefined,
    };
    if (filterProjectId.value) params.project_id = filterProjectId.value;
    const res = await getCaseSets(selectedFolder.value.id, params);
    const d = res.data || {};
    pagination.total = d.total || 0;

    if (locateId && d.items?.length > 0) {
      const idx = d.items.findIndex((s) => s.id === locateId);
      if (idx >= 0) {
        const pageSize = pagination.pageSize;
        pagination.page = Math.floor(idx / pageSize) + 1;
        const start = (pagination.page - 1) * pageSize;
        caseSets.value = d.items.slice(start, start + pageSize);
      } else {
        caseSets.value = d.items.slice(0, pagination.pageSize);
        pagination.page = 1;
      }
    } else {
      caseSets.value = d.items || [];
    }
  } catch {
    ElMessage.error("加载用例集列表失败");
  } finally {
    tableLoading.value = false;
  }
}

async function loadProjects() {
  try {
    const res = await getProjects({ page: 1, size: 10000 });
    const list = res.data?.items ?? (Array.isArray(res.data) ? res.data : []) ?? [];
    list.sort((a, b) => {
      const ta = a.updated_at || a.created_at || '';
      const tb = b.updated_at || b.created_at || '';
      return tb.localeCompare(ta);
    });
    projectOptions.value = list;
    if (projectOptions.value.length && filterProjectId.value == null) {
      filterProjectId.value = projectOptions.value[0].id;
      loadFolderTree();
    }
  } catch {
    projectOptions.value = [];
  }
}

function onProjectFilterChange() {
  loadFolderTree();
  selectedFolder.value = null;
  caseSets.value = [];
}

async function loadRecycled() {
  recycleLoading.value = true;
  recycleSelectedIds.value = [];
  recycleSelectAll.value = false;
  try {
    const params = {
      page: recyclePagination.page,
      page_size: recyclePagination.pageSize,
      ...(recycleFilterProjectId.value ? { project_id: recycleFilterProjectId.value } : {}),
    };
    const res = await getRecycledSuites(params);
    const data = res.data || {};
    recycledList.value = data.items || [];
    recyclePagination.total = data.total ?? 0;
  } catch {
    recycledList.value = [];
    recyclePagination.total = 0;
  } finally {
    recycleLoading.value = false;
  }
}

function toggleRecycleSelected(id, checked) {
  if (checked) {
    if (!recycleSelectedIds.value.includes(id)) recycleSelectedIds.value = [...recycleSelectedIds.value, id];
  } else {
    recycleSelectedIds.value = recycleSelectedIds.value.filter((x) => x !== id);
  }
  recycleSelectAll.value = recycledList.value.length > 0 && recycleSelectedIds.value.length === recycledList.value.length;
}

function onRecycleSelectAllChange(checked) {
  if (checked) {
    recycleSelectedIds.value = recycledList.value.map((x) => x.id);
  } else {
    recycleSelectedIds.value = [];
  }
}

async function batchPermanentDeleteRecycled() {
  if (!recycleSelectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(
      `确定彻底删除选中的 ${recycleSelectedIds.value.length} 项吗？删除后不可恢复。`,
      "批量彻底删除",
      { type: "warning" }
    );
    await batchPermanentDeleteRecycledSuites(recycleSelectedIds.value);
    ElMessage.success("已彻底删除");
    await loadRecycled();
    await loadFolderTree();
  } catch (e) {
    if (e !== "cancel" && !e?._messageShown) {
      const msg = e?.response?.data?.message || e?.message || "批量彻底删除失败";
      ElMessage.error(msg);
    }
  }
}

async function restoreRecycled(id) {
  try {
    await restoreRecycledSuite(id);
    ElMessage.success("已恢复");
    await loadRecycled();
    await loadFolderTree();
    if (selectedFolder.value) await loadCaseSets();
  } catch (err) {
    if (!err?._messageShown) {
      const msg = err?.response?.data?.message || err?.message || "恢复失败";
      ElMessage.error(msg);
    }
  }
}

async function permanentDeleteRecycled(item) {
  try {
    await ElMessageBox.confirm(`确定彻底删除"${item.suite_name}"吗？删除后不可恢复。`, "确认彻底删除", { type: "warning" });
    await deleteTestSuite(item.id, { permanent: true });
    ElMessage.success("已彻底删除");
    await loadRecycled();
    await loadFolderTree();
  } catch { /* cancelled */ }
}

async function loadRequirements() {
  try {
    const { default: request } = await import("@/utils/request");
    const res = await request({ url: "/test-suites", method: "get", params: { all: true } });
    // Attempt to load requirements from a dedicated API if available
    try {
      const reqRes = await request({ url: "/iterations", method: "get", params: { page: 1, page_size: 1000 } });
      // We need version requirements - try to get them
      const vrRes = await request({ url: "/test-suites/options", method: "get" });
    } catch { /* ignore */ }
  } catch { /* ignore */ }
}

function handleFolderClick(data) {
  selectedFolder.value = data;
  pagination.page = 1;
  loadCaseSets();
}

function handleRowClick(row) {
  if (editingSuiteId.value != null) return;
  openMindmap(row);
}

function openMindmap(row) {
  const gen = generatingMap[row.id];
  let url = `/mindmap-editor?suite_id=${row.id}&suite_name=${encodeURIComponent(row.suite_name)}`;
  if (gen?.taskId) {
    url += `&generating=1&task_id=${encodeURIComponent(gen.taskId)}`;
  }
  window.open(url, "_blank");
}

function startEditSuiteName(row) {
  if (generatingMap[row.id]) return;
  editingSuiteId.value = row.id;
  editingSuiteName.value = row.suite_name || "";
  nextTick(() => suiteNameInputRef.value?.focus());
}

async function saveSuiteNameEdit() {
  const id = editingSuiteId.value;
  if (id == null) return;
  const name = (editingSuiteName.value || "").trim();
  editingSuiteId.value = null;
  editingSuiteName.value = "";
  if (name === "") return;
  const row = caseSets.value.find((r) => r.id === id);
  if (row && row.suite_name === name) return;
  try {
    await updateTestSuite(id, { suite_name: name });
    ElMessage.success("名称已更新");
    await loadCaseSets();
    await loadFolderTree();
  } catch (err) {
    editingSuiteId.value = id;
    editingSuiteName.value = name;
    const msg = err?.response?.data?.message || err?.message || "更新失败";
    ElMessage.error(msg);
  }
}

function cancelSuiteNameEdit() {
  editingSuiteId.value = null;
  editingSuiteName.value = "";
}

function handleAddFolder() {
  folderDialogTitle.value = "新建文件夹";
  folderForm.name = "";
  folderForm.id = null;
  folderForm.parentId = selectedFolder.value?.id || null;
  folderDialogVisible.value = true;
}

function handleAddSubFolder() {
  contextMenu.visible = false;
  folderDialogTitle.value = "新建子文件夹";
  folderForm.name = "";
  folderForm.id = null;
  folderForm.parentId = contextMenu.data?.id;
  folderDialogVisible.value = true;
}

function _ctxParentId() {
  const d = contextMenu.data;
  return (d?._virtual || d?.id === 0) ? null : (d?.id ?? null);
}

function handleCtxNewFolder() {
  contextMenu.visible = false;
  ctxFolderParentId = _ctxParentId();
  ctxFolderName.value = "";
  ctxFolderDialogVisible.value = true;
}

async function submitCtxFolder() {
  if (!ctxFolderName.value.trim()) { ElMessage.warning("文件夹名称不能为空"); return; }
  try {
    await createTestSuite({ suite_name: ctxFolderName.value.trim(), type: "folder", parent_id: ctxFolderParentId });
    ElMessage.success("文件夹创建成功");
    ctxFolderDialogVisible.value = false;
    await loadFolderTree();
  } catch { ElMessage.error("创建文件夹失败"); }
}

function handleCtxNewSuite() {
  contextMenu.visible = false;
  ctxSuiteParentId = _ctxParentId();
  ctxSuiteForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  ctxSuiteForm.suite_name = "";
  ctxSuiteForm.description = "";
  ctxSuiteForm.version_requirement_id = null;
  if (ctxSuiteForm.project_id) loadRequirementOptionsByProject(ctxSuiteForm.project_id);
  ctxSuiteDialogVisible.value = true;
}

async function submitCtxSuite() {
  if (!ctxSuiteForm.suite_name.trim()) { ElMessage.warning("用例集名称不能为空"); return; }
  if (!ctxSuiteForm.project_id) { ElMessage.warning("请选择关联项目"); return; }
  try {
    const res = await createTestSuite({
      suite_name: ctxSuiteForm.suite_name.trim(),
      description: ctxSuiteForm.description || "",
      type: "suite",
      parent_id: ctxSuiteParentId,
      status: "active",
      version_requirement_id: ctxSuiteForm.version_requirement_id || null,
      project_id: ctxSuiteForm.project_id,
    });
    ElMessage.success("用例集创建成功");
    ctxSuiteDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();
    if (res.data?.id) nextTick(() => openMindmap(res.data));
  } catch { ElMessage.error("创建用例集失败"); }
}

/** 顶部「导入用例集」按钮：导入到当前选中文件夹或项目根 */
function openImportSuiteDialog() {
  importParentId = selectedFolder.value?.id ?? null;
  importForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  importForm.iteration_id = null;
  importForm.requirement_id = null;
  importForm.file = null;
  importIterationOptions.value = [];
  importRequirementOptions.value = [];
  importUploadRef.value?.clearFiles();
  importDialogVisible.value = true;
}

function handleCtxImportSuite() {
  contextMenu.visible = false;
  importParentId = _ctxParentId();
  importForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  importForm.iteration_id = null;
  importForm.requirement_id = null;
  importForm.file = null;
  importIterationOptions.value = [];
  importRequirementOptions.value = [];
  importUploadRef.value?.clearFiles();
  importDialogVisible.value = true;
}

async function onImportDialogOpen() {
  if (importForm.project_id) {
    await loadImportIterations(importForm.project_id);
    await loadImportRequirements(importForm.project_id, null);
  }
}

async function loadImportIterations(projectId) {
  if (!projectId) { importIterationOptions.value = []; return; }
  try {
    const res = await getProjectIterations(projectId);
    importIterationOptions.value = res.data?.items || res.data || [];
  } catch { importIterationOptions.value = []; }
}

async function loadImportRequirements(projectId, iterationId) {
  if (!projectId) { importRequirementOptions.value = []; return; }
  try {
    const res = await getProjectVersionRequirements(projectId);
    let list = res.data?.items || res.data || [];
    if (iterationId) list = list.filter(r => r.iteration_id === iterationId);
    importRequirementOptions.value = list;
  } catch { importRequirementOptions.value = []; }
}

async function onImportIterationChange() {
  importForm.requirement_id = null;
  await loadImportRequirements(importForm.project_id, importForm.iteration_id);
}

function onImportFileChange(uploadFile) {
  importForm.file = uploadFile.raw;
}

function downloadImportTemplate() {
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';
  window.open(`${baseURL}/test-suites/import-template`, '_blank');
}

async function submitImport() {
  if (!importForm.file) { ElMessage.warning("请选择要导入的文件"); return; }
  importLoading.value = true;
  try {
    const fd = new FormData();
    fd.append("file", importForm.file);
    if (importParentId) fd.append("parent_id", importParentId);
    if (importForm.project_id) fd.append("project_id", importForm.project_id);
    if (importForm.iteration_id) fd.append("iteration_id", importForm.iteration_id);
    if (importForm.requirement_id) fd.append("requirement_id", importForm.requirement_id);
    const res = await importTestSuite(fd);
    ElMessage.success(res.data?.message || "导入成功");
    importDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();
  } catch { ElMessage.error("导入失败"); }
  finally { importLoading.value = false; }
}

function handleRenameFolder() {
  contextMenu.visible = false;
  if (contextMenu.data?._virtual || contextMenu.data?.id === 0) {
    ElMessage.warning("「根」不能重命名");
    return;
  }
  folderDialogTitle.value = "重命名文件夹";
  folderForm.name = contextMenu.data?.suite_name || "";
  folderForm.id = contextMenu.data?.id;
  folderForm.parentId = contextMenu.data?.parent_id;
  folderDialogVisible.value = true;
}

async function submitFolder() {
  if (!folderForm.name.trim()) {
    ElMessage.warning("文件夹名称不能为空");
    return;
  }
  try {
    if (folderForm.id) {
      await updateTestSuite(folderForm.id, { suite_name: folderForm.name.trim() });
      ElMessage.success("重命名成功");
    } else {
      await createTestSuite({
        suite_name: folderForm.name.trim(),
        type: "folder",
        parent_id: folderForm.parentId || null,
        project_id: folderForm.parentId ? undefined : (filterProjectId.value || undefined),
      });
      ElMessage.success("文件夹创建成功");
    }
    folderDialogVisible.value = false;
    await loadFolderTree();
  } catch {
    ElMessage.error("操作失败");
  }
}

async function handleDeleteFolder() {
  contextMenu.visible = false;
  const folder = contextMenu.data;
  if (!folder) return;
  if (folder._virtual || folder.id === 0) {
    ElMessage.warning("「根」不能删除");
    return;
  }
  try {
    await ElMessageBox.confirm(
      `确定删除文件夹"${folder.suite_name}"吗？其下用例集将移入回收站，文件夹将从目录中移除。`,
      "确认删除",
      { type: "warning" }
    );
    await deleteTestSuite(folder.id, { logical: true });
    ElMessage.success("已删除，其下用例集已移入回收站");
    if (selectedFolder.value?.id === folder.id) {
      selectedFolder.value = null;
      caseSets.value = [];
    }
    await loadFolderTree();
    if (showRecycleDrawer.value) await loadRecycled();
  } catch { /* cancelled */ }
}

function handleAddSuite() {
  suiteForm.suite_name = "";
  suiteForm.description = "";
  suiteForm.version_requirement_id = null;
  suiteForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  suiteForm.parentId = selectedFolder.value?.id !== undefined && selectedFolder.value?.id !== null ? selectedFolder.value.id : 0;
  suiteFormFolderTree.value = buildFolderTreeWithRoot();
  suiteDialogVisible.value = true;
}

async function onSuiteDialogOpen() {
  suiteForm.project_id = filterProjectId.value ?? projectOptions.value?.[0]?.id ?? null;
  suiteFormFolderTree.value = buildFolderTreeWithRoot();
  await loadRequirementOptionsByProject(suiteForm.project_id ?? filterProjectId.value);
}

async function onSuiteFormProjectChange(projectId) {
  loadRequirementOptionsByProject(projectId);
  if (projectId) {
    try {
      const res = await getFolderTree({ project_id: projectId });
      const payload = res.data || {};
      const tree = payload.tree || payload || [];
      const rootSuiteCount = payload.root_suite_count || 0;
      const treeArr = Array.isArray(tree) ? tree : [];
      suiteFormFolderTree.value = [
        { id: 0, suite_name: "根", type: "folder", parent_id: null, suite_count: rootSuiteCount, children: treeArr, _virtual: true },
      ];
    } catch {
      suiteFormFolderTree.value = [{ id: 0, suite_name: "根", type: "folder", children: [], _virtual: true }];
    }
  } else {
    suiteFormFolderTree.value = [];
  }
}

async function loadRequirementOptionsByProject(projectId) {
  if (!projectId) {
    requirementOptions.value = [];
    return;
  }
  try {
    const res = await getProjectVersionRequirements(projectId);
    const data = res.data || res;
    requirementOptions.value = data.items || data || [];
  } catch {
    requirementOptions.value = [];
  }
}

async function submitSuite() {
  if (!suiteForm.suite_name.trim()) {
    ElMessage.warning("用例集名称不能为空");
    return;
  }
  if (!suiteForm.project_id) {
    ElMessage.warning("请选择所属项目");
    return;
  }
  const parentId = (suiteForm.parentId === 0 || suiteForm.parentId === null || suiteForm.parentId === undefined) ? null : suiteForm.parentId;
  try {
    const res = await createTestSuite({
      suite_name: suiteForm.suite_name.trim(),
      description: suiteForm.description || "",
      type: "suite",
      parent_id: parentId,
      status: "active",
      version_requirement_id: suiteForm.version_requirement_id || null,
      project_id: suiteForm.project_id,
      iteration_id: null,
    });
    ElMessage.success("用例集创建成功");
    suiteDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();

    if (res.data?.id) {
      nextTick(() => openMindmap(res.data));
    }
  } catch {
    ElMessage.error("创建用例集失败");
  }
}

function handleMoveSuite(row) {
  movingSuite.value = row;
  moveTargetId.value = null;
  moveDialogVisible.value = true;
}

async function confirmMove() {
  if (!moveTargetId.value) {
    ElMessage.warning("请选择目标文件夹");
    return;
  }
  try {
    await moveTestSuite(movingSuite.value.id, { target_folder_id: moveTargetId.value });
    ElMessage.success("移动成功");
    moveDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();
  } catch {
    ElMessage.error("移动失败");
  }
}

async function handleCopySuite(row) {
  try {
    await ElMessageBox.confirm(`确定复制用例集"${row.suite_name}"吗？`, "确认复制");
    await copyTestSuite(row.id, { target_folder_id: selectedFolder.value?.id });
    ElMessage.success("复制成功");
    await loadFolderTree();
    await loadCaseSets();
  } catch { /* cancelled */ }
}

async function handleDeleteSuite(row) {
  const isGenerating = !!generatingMap[row.id];
  const message = isGenerating
    ? `用例集"${row.suite_name}"正在AI生成中。确定终止生成并移至回收站吗？`
    : `确定将用例集"${row.suite_name}"移至回收站吗？`;
  try {
    await ElMessageBox.confirm(message, "确认删除", { type: "warning" });
    await deleteTestSuite(row.id, { logical: true });
    delete generatingMap[row.id];
    ElMessage.success("已移至回收站");
    await loadFolderTree();
    await loadCaseSets();
    if (showRecycleDrawer.value) await loadRecycled();
  } catch { /* cancelled */ }
}

/** 评审按钮悬浮文案：按当前用户角色与用例集评审状态显示 */
function getReviewButtonTooltip(row) {
  const status = row.review_status || "not_reviewed";
  const me = userStore.userInfo?.id != null ? String(userStore.userInfo.id) : null;
  const creatorId = row.creator_id != null ? String(row.creator_id) : null;
  const initiatorId = row.review_initiator_id != null ? String(row.review_initiator_id) : null;
  const reviewerId = row.review_reviewer_id != null ? String(row.review_reviewer_id) : null;

  if (status === "not_reviewed") {
    return me === creatorId ? "创建者未发起评审" : "未发起评审";
  }
  if (status === "pending") {
    if (me === reviewerId) return "待我评审";
    if (me === initiatorId) return "待评审人评审";
    return "待评审";
  }
  if (status === "in_review") {
    if (me === reviewerId) return "我评审中";
    if (me === initiatorId) return "评审人评审中";
    return "评审人评审中";
  }
  if (status === "completed") return "评审已完成（已通过）";
  if (status === "rejected") return "评审已完成（已拒绝）";
  return "评审";
}

function handleReviewSuite(row) {
  router.push({ path: "/case-reviews", query: { suiteId: row.id } });
}

function handleGenerateCases() {
  generateForm.mode = "append";
  generateForm.projectId = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  generateForm.iterationId = null;
  generateForm.requirementId = null;
  generateForm.folderId = null;
  generateForm.suiteId = null;
  generateForm.newSuiteName = "";
  generateForm.documentContent = "";
  generateDocxFile.value = null;
  generateForm.debugMode = false;
  generateFolderTree.value = [];
  generateSuiteOptions.value = [];
  generateIterationOptions.value = [];
  generateRequirementOptions.value = [];
  generateDialogVisible.value = true;
}

async function onGenerateDialogOpen() {
  if (!generateForm.projectId && projectOptions.value.length) {
    generateForm.projectId = filterProjectId.value ?? projectOptions.value[0].id;
  }
  generateFolderTree.value = await loadGenerateFolderTree(generateForm.projectId);
  if (generateForm.projectId) {
    await loadGenerateIterations(generateForm.projectId);
    await loadGenerateRequirements(generateForm.projectId, generateForm.iterationId);
  }
  if (generateForm.projectId != null && (generateForm.folderId != null || generateForm.suiteId != null)) {
    try {
      const folderIdForApi = generateForm.folderId == null ? 0 : generateForm.folderId;
      const res = await getCaseSets(folderIdForApi, { project_id: generateForm.projectId });
      generateSuiteOptions.value = res.data?.items || [];
    } catch {
      generateSuiteOptions.value = [];
    }
  }
}

/** 项目变更时：清空目标文件夹、用例集、迭代、需求，重新加载 */
async function onGenerateProjectChange() {
  generateForm.iterationId = null;
  generateForm.requirementId = null;
  generateForm.folderId = null;
  generateForm.suiteId = null;
  generateSuiteOptions.value = [];
  generateIterationOptions.value = [];
  generateRequirementOptions.value = [];
  generateFolderTree.value = await loadGenerateFolderTree(generateForm.projectId);
  if (generateForm.projectId) {
    await loadGenerateIterations(generateForm.projectId);
    await loadGenerateRequirements(generateForm.projectId, null);
  }
}

/** 加载目录树（仅文件夹），按项目筛选，供 AI 生成用例「目标文件夹」使用；不显示根节点，直接展示项目下顶层文件夹 */
async function loadGenerateFolderTree(projectId) {
  if (projectId == null) return [];
  try {
    const res = await getFolderTree({ project_id: projectId });
    const payload = res.data || {};
    const tree = payload.tree || [];
    return Array.isArray(tree) ? tree : [];
  } catch (e) {
    console.error("加载目录失败", e);
    ElMessage.error("加载目录失败，请重试");
    return [];
  }
}

async function loadGenerateIterations(projectId) {
  if (!projectId) { generateIterationOptions.value = []; return; }
  try {
    const res = await getProjectIterations(projectId);
    generateIterationOptions.value = res.data?.items || res.data || [];
  } catch { generateIterationOptions.value = []; }
}

async function loadGenerateRequirements(projectId, iterationId) {
  if (!projectId) { generateRequirementOptions.value = []; return; }
  try {
    const res = await getProjectVersionRequirements(projectId);
    let list = res.data?.items || res.data || [];
    if (iterationId) {
      list = list.filter(r => r.iteration_id === iterationId);
    }
    generateRequirementOptions.value = list;
  } catch { generateRequirementOptions.value = []; }
}

async function onGenerateIterationChange() {
  generateForm.requirementId = null;
  await loadGenerateRequirements(generateForm.projectId, generateForm.iterationId);
}

/** 目录变更时加载该目录下用例集，并清空已选用例集 */
async function onGenerateFolderChange() {
  generateForm.suiteId = null;
  if (generateForm.folderId == null) {
    generateSuiteOptions.value = [];
    return;
  }
  if (!generateForm.projectId) {
    generateSuiteOptions.value = [];
    return;
  }
  try {
    const folderIdForApi = generateForm.folderId == null ? 0 : generateForm.folderId;
    const res = await getCaseSets(folderIdForApi, { project_id: generateForm.projectId });
    generateSuiteOptions.value = res.data?.items || [];
  } catch {
    generateSuiteOptions.value = [];
  }
}

function onGenerateFileChange(file) {
  const raw = file.raw;
  if (!raw) return;
  const ext = (raw.name || "").toLowerCase().split(".").pop();
  if (ext === "txt" || ext === "md") {
    generateDocxFile.value = null;
    const reader = new FileReader();
    reader.onload = () => {
      generateForm.documentContent = reader.result ?? "";
    };
    reader.readAsText(raw, "UTF-8");
  } else if (ext === "docx") {
    generateForm.documentContent = "";
    generateDocxFile.value = raw;
  } else if (ext === "doc") {
    generateDocxFile.value = null;
    generateForm.documentContent = "";
    ElMessage.warning("暂不支持旧版 .doc，请将文档另存为 .docx 或使用 .txt / .md");
  } else {
    generateDocxFile.value = null;
    ElMessage.warning("请上传 .txt、.md 或 .docx 格式的需求文档");
  }
}

function onGenerateUploadExceed(files) {
  const upload = generateUploadRef.value;
  if (!upload || !files?.length) return;
  upload.clearFiles();
  const raw = files[0];
  raw.uid = genFileId();
  upload.handleStart(raw);
}

function onGenerateFileRemove() {
  generateForm.documentContent = "";
  generateDocxFile.value = null;
}

function handleGenerateForSuite(row) {
  generateForm.projectId = row.project_id ?? filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  generateForm.iterationId = row.iteration_id ?? null;
  generateForm.requirementId = row.version_requirement_id ?? null;
  generateForm.folderId = row.parent_id ?? null;
  generateForm.suiteId = row.id;
  generateForm.documentContent = "";
  generateDocxFile.value = null;
  generateForm.debugMode = false;
  generateSuiteOptions.value = [];
  generateIterationOptions.value = [];
  generateRequirementOptions.value = [];
  generateDialogVisible.value = true;
}

async function submitGenerate() {
  if (!generateForm.documentContent?.trim() && !generateDocxFile.value) {
    ElMessage.warning("需求文档内容不能为空");
    return;
  }
  const pendingDocx = generateDocxFile.value;
  generateDialogVisible.value = false;
  if (generateForm.mode === "append") {
    if (!generateForm.suiteId) {
      ElMessage.warning("请选择目标用例集");
      return;
    }
    await startGenerateForSuite(generateForm.suiteId, generateForm.documentContent, generateForm.debugMode, pendingDocx);
    return;
  }
  // 创建新用例集并生成（未选文件夹或选根时 parent_id 为 null）
  const parentId = (generateForm.folderId == null || generateForm.folderId === 0) ? null : generateForm.folderId;
  try {
    const createRes = await createTestSuite({
      suite_name: generateForm.newSuiteName.trim(),
      description: "",
      type: "suite",
      parent_id: parentId,
      status: "active",
      version_requirement_id: generateForm.requirementId || null,
      project_id: generateForm.projectId,
      iteration_id: generateForm.iterationId || null,
    });
    const newSuite = createRes.data;
    if (!newSuite?.id) {
      ElMessage.error("创建用例集失败");
      return;
    }
    await startGenerateForSuite(newSuite.id, generateForm.documentContent, generateForm.debugMode, pendingDocx);
    selectFolderById(newSuite.parent_id ?? 0);
    await loadCaseSets();
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || "创建用例集失败");
  }
}

/** 在目录树中根据 id 选中文件夹（用于创建新用例集后定位） */
function selectFolderById(folderId) {
  const find = (nodes) => {
    for (const n of nodes) {
      if (n.id === folderId) return n;
      if (n.children?.length) { const r = find(n.children); if (r) return r; }
    }
    return null;
  };
  const node = find(folderTree.value);
  if (node) selectedFolder.value = node;
  else selectedFolder.value = null;
}

/** 通知跳转高亮：为对应用例集行附加闪烁 class */
function getCaseSetRowClassName({ row }) {
  if (flashSuiteId.value && row.id === flashSuiteId.value) return "notification-flash-row";
  return "";
}

/** 用例集列表或 flashSuiteId 变化时，自动滚动并触发闪烁计时 */
watch(
  () => [caseSets.value, flashSuiteId.value],
  () => {
    const sid = flashSuiteId.value;
    if (!sid || flashClearTimer) return;
    const inList = caseSets.value.some((r) => r.id === sid);
    if (!inList) return;

    nextTick(() => {
      const tableEl = caseSetTableRef.value?.$el;
      const row = tableEl?.querySelector("tr.notification-flash-row");
      if (row) row.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    flashClearTimer = setTimeout(() => {
      flashSuiteId.value = null;
      flashClearTimer = null;
      const q = { ...route.query };
      delete q.suite_id;
      router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
    }, 2600);
  },
  { flush: "post" }
);

async function startGenerateForSuite(suiteId, documentContent, debugMode = false, docxFile = null) {
  try {
    generatingMap[suiteId] = { taskId: null, progress: 0, message: '正在创建任务...' };
    const selectedProject = projectOptions.value.find(p => p.id === generateForm.projectId);
    const selectedIteration = generateIterationOptions.value.find(it => it.id === generateForm.iterationId);
    const selectedRequirement = generateRequirementOptions.value.find(r => r.id === generateForm.requirementId);
    const docx = docxFile;
    let res;
    if (docx) {
      const fd = new FormData();
      fd.append("suite_id", String(suiteId));
      fd.append("documentContent", documentContent || "");
      fd.append("debugMode", debugMode ? "true" : "false");
      fd.append("projectId", generateForm.projectId ?? "");
      fd.append("iterationId", generateForm.iterationId ?? "");
      fd.append("requirementId", generateForm.requirementId ?? "");
      fd.append("projectName", selectedProject?.project_name || "");
      fd.append("iterationName", selectedIteration?.iteration_name || "");
      fd.append("requirementName", selectedRequirement?.requirement_name || "");
      fd.append("document", docx, docx.name);
      res = await createGenerateCasesWithFiles(fd);
    } else {
      res = await createGenerateCasesTask({
        suite_id: suiteId,
        documentContent,
        debugMode,
        projectId: generateForm.projectId,
        iterationId: generateForm.iterationId,
        requirementId: generateForm.requirementId,
        projectName: selectedProject?.project_name || "",
        iterationName: selectedIteration?.iteration_name || "",
        requirementName: selectedRequirement?.requirement_name || "",
      });
    }
    const taskId = res.data?.task_id;
    if (taskId) {
      generatingMap[suiteId] = { taskId, progress: 0, message: '等待处理...' };
      ElMessage.success("任务已创建，正在后台生成用例...");
      pollTaskStatus(taskId, suiteId);
    } else {
      delete generatingMap[suiteId];
    }
  } catch (e) {
    delete generatingMap[suiteId];
    ElMessage.error("创建生成任务失败");
  }
}

// 跟踪所有轮询定时器，组件卸载时统一清理
const pollIntervalMap = new Map();

function pollTaskStatus(taskId, suiteId) {
  const interval = setInterval(async () => {
    try {
      const res = await getTaskStatus(taskId);
      const d = res.data || {};
      const status = d.status;
      const progress = d.progress ?? 0;
      const message = d.message || '';

      if (status === 'completed') {
        generatingMap[suiteId] = { taskId, progress: 100, message: message || '生成完成' };
        setTimeout(() => { delete generatingMap[suiteId]; }, 1500);
        clearInterval(interval);
        pollIntervalMap.delete(suiteId);
        ElMessage.success(message || '用例生成完成！');
        await loadFolderTree();
        await loadCaseSets();
      } else if (status === 'failed') {
        clearInterval(interval);
        pollIntervalMap.delete(suiteId);
        delete generatingMap[suiteId];
        ElMessage.error(d.error || message || "用例生成失败");
      } else if (generatingMap[suiteId]) {
        generatingMap[suiteId] = { taskId, progress, message };
      }
    } catch {
      clearInterval(interval);
      pollIntervalMap.delete(suiteId);
      delete generatingMap[suiteId];
    }
  }, 2000);
  pollIntervalMap.set(suiteId, interval);
}

function handleFolderContextMenu(event, data) {
  event.preventDefault();
  contextMenu.visible = true;
  contextMenu.x = event.clientX;
  contextMenu.y = event.clientY;
  contextMenu.data = data;
}

function hideContextMenu() {
  contextMenu.visible = false;
}

/** 仅允许拖拽真实文件夹节点，不允许拖拽「全部」虚拟节点 */
function allowFolderDrag(node) {
  const data = node.data;
  return data && !data._virtual && data.id !== 0;
}

/** 允许放入文件夹下或放在某节点前/后（type 为 prev/next/inner）；根层节点前/后即为根级 */
function allowFolderDrop(draggingNode, dropNode, type) {
  const dropData = dropNode.data;
  if (dropData.type !== "folder") return false;
  if (type === "inner") {
    let p = dropNode;
    while (p) {
      if (p.data && p.data.id === draggingNode.data.id) return false;
      p = p.parent;
    }
  }
  return true;
}

/**
 * 文件夹拖拽放下后同步到后端并刷新树。
 * 参数：draggingNode/dropNode 为 el-tree 的 Node，dropType 为 'before'|'after'|'inner'。
 * 根据 dropType 与 dropNode 计算新 parent_id 与 sort_order。
 */
async function handleFolderDrop(draggingNode, dropNode, dropType) {
  const dragData = draggingNode?.data;
  if (!dragData || dragData._virtual || dragData.id === 0) return;
  const dragId = dragData.id;

  let parentId = null;
  let sortOrder = 1;

  if (dropType === "inner") {
    const dropData = dropNode?.data;
    if (!dropData) return;
    parentId = dropData.id === 0 ? null : dropData.id;
    const childNodes = dropNode.childNodes || [];
    const idx = childNodes.findIndex((n) => n.data && n.data.id === dragId);
    sortOrder = idx >= 0 ? idx + 1 : childNodes.length || 1;
  } else {
    const parent = dropNode?.parent;
    const parentData = parent?.data;
    parentId =
      parentData != null && parentData.id != null && parentData.id !== 0
        ? parentData.id
        : null;
    const siblings = parent?.childNodes || [];
    const dropIdx = siblings.findIndex(
      (n) => n.data && n.data.id === dropNode?.data?.id
    );
    if (dropIdx >= 0) {
      sortOrder = dropType === "before" ? dropIdx + 1 : dropIdx + 2;
    }
  }

  try {
    await updateTestSuite(dragId, { parent_id: parentId, sort_order: sortOrder });
    ElMessage.success("排序已更新");
    await loadFolderTree();
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || "排序更新失败");
    await loadFolderTree();
  }
}

function reviewStatusLabel(status) {
  const map = {
    not_reviewed: "未评审",
    pending: "待评审",
    in_review: "评审中",
    completed: "已通过",
    rejected: "已拒绝",
  };
  return map[status] || "未评审";
}

function reviewStatusType(status) {
  const map = {
    not_reviewed: "info",    // 灰蓝 - 未评审
    pending: "warning",      // 橙黄 - 待评审
    in_review: "primary",   // 蓝色 - 评审中
    completed: "success",   // 绿色 - 已通过
    rejected: "danger",     // 红色 - 已拒绝
  };
  return map[status] || "info";
}

function formatTime(iso) {
  if (!iso) return "-";
  return iso.replace("T", " ").slice(0, 19);
}

/** 回收站列表：删除时间友好显示 */
function formatRecycleTime(iso) {
  if (!iso) return "-";
  const s = iso.replace("T", " ").slice(0, 19);
  const d = new Date(iso);
  const now = new Date();
  const today = now.getFullYear() === d.getFullYear() && now.getMonth() === d.getMonth() && now.getDate() === d.getDate();
  if (today) return `今天 ${s.slice(11, 16)}`;
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (d.getFullYear() === yesterday.getFullYear() && d.getMonth() === yesterday.getMonth() && d.getDate() === yesterday.getDate()) return `昨天 ${s.slice(11, 16)}`;
  return s.slice(0, 16);
}

/** 回收站删除时间完整显示：年月日 时分秒 */
function formatRecycleTimeFull(iso) {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

/** 回收站行悬浮提示：三行显示 所属项目、所属需求、用例数 */
function getRecycleRowTooltip(item) {
  const project = item.project_name != null && item.project_name !== "" ? item.project_name : "—";
  const requirement = item.version_requirement_name != null && item.version_requirement_name !== "" ? item.version_requirement_name : "—";
  const count = item.case_count != null ? item.case_count : "—";
  return `所属项目：${project}\n所属需求：${requirement}\n用例数：${count}`;
}

watch(showRecycleDrawer, (open) => {
  if (open) {
    recycleFilterProjectId.value = filterProjectId.value;
    recyclePagination.page = 1;
    loadRecycled();
  }
});

// 已在用例页时收到新通知跳转（suite_id 变化）→ 重新触发定位逻辑
watch(
  () => route.query?.suite_id,
  async (idVal, oldVal) => {
    if (!idVal || idVal === oldVal) return;
    const sid = Number(idVal);
    flashSuiteId.value = sid;
    try {
      const res = await getTestSuiteDetail(sid);
      const suite = res.data;
      if (suite.project_id) filterProjectId.value = suite.project_id;
      await loadFolderTree();
      if (suite.parent_id !== null && suite.parent_id !== undefined) selectFolderById(suite.parent_id);
      if (selectedFolder.value) await loadCaseSets(flashSuiteId.value);
    } catch {
      flashSuiteId.value = null;
    }
  }
);

onMounted(async () => {
  document.addEventListener("click", hideContextMenu);
  const suiteIdParam = route.query.suite_id;
  if (suiteIdParam) {
    const sid = Number(suiteIdParam);
    flashSuiteId.value = sid;
    try {
      // 获取用例集详情以确定所属项目和父文件夹
      const res = await getTestSuiteDetail(sid);
      const suite = res.data;
      // 加载项目列表
      const pRes = await getProjects({ page: 1, size: 10000 });
      projectOptions.value = pRes.data?.items ?? (Array.isArray(pRes.data) ? pRes.data : []) ?? [];
      // 切换到用例集所属项目
      if (suite.project_id) {
        filterProjectId.value = suite.project_id;
      } else if (projectOptions.value.length) {
        filterProjectId.value = projectOptions.value[0].id;
      }
      // 加载对应项目的文件夹树
      await loadFolderTree();
      // 选中用例集所在的父文件夹
      if (suite.parent_id !== null && suite.parent_id !== undefined) {
        selectFolderById(suite.parent_id);
      }
      // 加载该文件夹下的用例集，传入 flashSuiteId 以实现分页定位
      if (selectedFolder.value) {
        await loadCaseSets(flashSuiteId.value);
      }
      // 若用例集在目标文件夹中，watch 会触发高亮；否则兜底清理 URL
      await nextTick();
      if (flashSuiteId.value && !flashClearTimer) {
        flashSuiteId.value = null;
        const q = { ...route.query };
        delete q.suite_id;
        router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      }
    } catch {
      // 定位失败，回退为正常加载
      flashSuiteId.value = null;
      loadProjects();
    }
  } else {
    loadProjects();
  }
});

// 打开生成弹窗时清空上传列表
watch(generateDialogVisible, (visible) => {
  if (!visible && generateUploadRef.value) {
    generateUploadRef.value.clearFiles();
    generateDocxFile.value = null;
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", hideContextMenu);
  if (flashClearTimer) { clearTimeout(flashClearTimer); flashClearTimer = null; }
  // 清理所有 AI 生成轮询定时器，防止组件卸载后继续轮询
  pollIntervalMap.forEach((interval) => clearInterval(interval));
  pollIntervalMap.clear();
});
</script>

<style scoped>
.test-case-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.page-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  .el-button {
    margin-left: 0;
  }
}

.header-project-select {
  width: 180px;
  /* 与左侧「导入用例集」等按钮拉开一点，避免贴得过紧 */
  margin-left: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

  .left-panel {
  width: 220px;
  min-width: 220px;
  border-right: 1px solid #e4e7ed;
  background: #fafafa;
    display: flex;
    flex-direction: column;
  transition: width 0.2s;
}

.left-panel.collapsed {
  width: 0;
        min-width: 0;
  overflow: hidden;
  border-right: none;
}

.collapsed-expand-btn {
        display: flex;
        align-items: center;
        justify-content: center;
      width: 24px;
  min-width: 24px;
  cursor: pointer;
  background: #f0f2f5;
  border-right: 1px solid #e4e7ed;
  color: #606266;
  transition: background 0.2s;
}
.collapsed-expand-btn:hover {
  background: #e6f7ff;
  color: #409eff;
}

    .panel-header {
      display: flex;
      align-items: center;
  padding: 10px 12px;
  gap: 6px;
  border-bottom: 1px solid #e4e7ed;
}

.tree-container {
        flex: 1;
  overflow: auto;
  padding: 8px 4px;
}

.recycle-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-top: 1px solid #e4e7ed;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  background: #fafafa;
}
.recycle-trigger:hover {
  background: #f0f2f5;
  color: #409eff;
}

.tree-node-label {
        display: flex;
        align-items: center;
  gap: 6px;
  font-size: 13px;
}

.right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

.panel-content {
      flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
      overflow: auto;
}

.form-item-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  line-height: 1.4;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.toolbar-left-area {
  display: flex;
  align-items: center;
}

.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 0 1px;
}
.action-btns .el-button {
  margin-left: 0;
  padding-left: 6px;
  padding-right: 6px;
}
.action-btns .el-button + .el-button {
  margin-left: 0;
}

.suite-name-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.suite-name-cell--editing {
  width: 100%;
  min-width: 0;
  margin: 0 -6px;
  padding: 0 2px;
  justify-content: stretch;
}
.suite-name-cell--editing .el-input {
  width: 100%;
  min-width: 0;
}
.suite-name-cell--editing .el-input :deep(.el-input__wrapper) {
  padding: 4px 10px;
  border-radius: 4px;
}
.suite-name-cell .suite-name-edit-btn {
  padding: 2px 4px;
  margin-left: 2px;
  color: var(--el-text-color-secondary);
}
.suite-name-cell .suite-name-edit-btn:hover {
  color: var(--el-color-primary);
}
.generating-progress-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 6px;
  color: #e6a23c;
  font-size: 12px;
  cursor: default;
}
.generating-progress-badge .el-icon {
  font-size: 13px;
}
.generating-pct {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.generating-inline-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 12px 0 0;
}

.empty-tip {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.context-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: transparent;
}

.context-menu {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  min-width: 120px;
}

.context-menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
}

.context-menu-item:hover {
  background: #ecf5ff;
  color: #409eff;
}

.context-menu-item.danger:hover {
  background: #fef0f0;
  color: #f56c6c;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.upload-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.document-preview {
  font-size: 12px;
  color: var(--el-color-success);
  margin-top: 8px;
}

.debug-toggle-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 8px 0 0;
  border-top: 1px dashed var(--el-border-color-lighter);
  margin-top: 4px;
}

.debug-toggle-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.debug-tag {
  font-size: 11px;
}

.move-dialog-tree-wrap {
  max-height: 360px;
  overflow-y: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 8px;
}

.recycle-drawer :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding-bottom: 12px;
}
.recycle-drawer :deep(.el-drawer__body) {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 8px 16px 16px;
  box-sizing: border-box;
}
.recycle-list {
  padding: 0;
  min-height: 120px;
  overflow-x: hidden;
  overflow-y: auto;
  flex: 1;
  min-width: 0;
}
.recycle-table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  table-layout: fixed;
  box-sizing: border-box;
}
.recycle-table th,
.recycle-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}
.recycle-table-center th,
.recycle-table-center td {
  text-align: center;
}
.recycle-table th {
  color: var(--el-text-color-secondary);
  font-weight: 600;
  font-size: 12px;
  background: #f5f7fa;
  padding: 10px 8px;
}
.recycle-table tbody tr:hover {
  background: #fafafa;
}
.recycle-table .col-path {
  width: 24%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recycle-table .col-name {
  width: 22%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}
.recycle-table .col-time {
  width: 12%;
  white-space: nowrap;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.recycle-table .col-check {
  width: 40px;
  text-align: center;
}
.recycle-toolbar {
  margin-bottom: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.recycle-toolbar-label {
  color: var(--el-text-color-regular);
  white-space: nowrap;
}
.recycle-project-select {
  width: 220px;
}
.recycle-pagination {
  margin-top: 12px;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
}
.recycle-table .cell-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recycle-table .col-operator {
  width: 12%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
}
.recycle-table .col-actions {
  width: 22%;
  white-space: nowrap;
}
.recycle-table .col-actions .el-button {
  padding: 0 6px;
  margin-left: 0;
}
</style>

<style>
/* 回收站用例集名称 tooltip 多行显示（popper 挂载到 body，需非 scoped） */
.recycle-name-tooltip-multiline {
  white-space: pre-line;
}
</style>
