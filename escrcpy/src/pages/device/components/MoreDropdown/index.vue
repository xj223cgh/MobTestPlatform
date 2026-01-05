<template>
  <el-tooltip
    effect="light"
    placement="top"
    :offset="1"
    :content="$t('device.actions.more.name')"
  >
    <el-dropdown :hide-on-click="false" toggle="click">
      <el-button
        type="primary"
        text
        :disabled="['unauthorized', 'offline'].includes(row.status)"
        icon="CirclePlus"
      >
      </el-button>

      <template #dropdown>
        <el-dropdown-menu>
          <component
            :is="item.component"
            v-for="(item, index) of options"
            :key="index"
            v-bind="{
              ...$props,
              ...(item.props || {}),
            }"
            v-slot="{ loading, trigger }"
          >
            <el-dropdown-item :disabled="loading" @click="trigger">
              <template v-if="loading">
                <el-icon class="is-loading">
                  <Loading />
                </el-icon>
                {{ $t('common.starting') }}
              </template>
              <template v-else>
                {{ $t(item.label) }}
              </template>
            </el-dropdown-item>
          </component>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </el-tooltip>
</template>

<script>
import Otg from './components/Otg/index.vue'

export default {
  components: {
    Otg,
  },
  props: {
    ...Otg.props,
  },
  data() {
    return {
      options: [
        {
          label: 'device.actions.more.otg.name',
          component: 'Otg',
        },
      ],
    }
  },
}
</script>

<style></style>
