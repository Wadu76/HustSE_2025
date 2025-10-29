<template>
  <div class="order-list-container">

    <el-radio-group v-model="currentRole" @change="fetchOrders" style="margin-bottom: 20px;">
      <el-radio-button label="buyer">我买的</el-radio-button>
      <el-radio-button label="seller">我卖的</el-radio-button>
    </el-radio-group>

    <el-alert v-if="!userStore.user" title="请先登录查看您的订单" type="warning" show-icon :closable="false">
      <router-link to="/login">
        <el-button type="primary" plain size="small">去登录</el-button>
      </router-link>
    </el-alert>

    <el-table 
      v-else 
      :data="orders" 
      v-loading="loading" 
      style="width: 100%"
      empty-text="暂无订单"
    >
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column prop="book_title" label="书籍" />

      <el-table-column v-if="currentRole === 'buyer'" prop="seller_name" label="卖家" />
      <el-table-column v-if="currentRole === 'seller'" prop="buyer_name" label="买家" />

      <el-table-column prop="price" label="价格">
        <template #default="scope">
          ¥ {{ scope.row.price.toFixed(2) }}
        </template>
      </el-table-column>

      <el-table-column prop="status_text" label="订单状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ scope.row.status_text }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="create_time" label="创建时间" width="160" />

      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <div v-if="currentRole === 'buyer'">
            <el-button
              v-if="scope.row.status === 1"
              type="primary"
              size="small"
              @click="handleUpdateStatus(scope.row.id, 2, '支付')"
            >
              去支付
            </el-button>

            <el-button
              v-if="scope.row.status === 3"
              type="success"
              size="small"
              @click="handleUpdateStatus(scope.row.id, 4, '确认收货')"
            >
              确认收货
            </el-button>
          </div>

          <span v-if="currentRole === 'seller' && (scope.row.status === 1 || scope.row.status === 3)">
            等待买家操作
          </span>

          <el-button
            v-if="currentRole === 'seller' && scope.row.status === 2"
            type="primary"
            size="small"
            @click="handleUpdateStatus(scope.row.id, 3, '发货')"
          >
            发货
          </el-button>

        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore';
import { ElMessage, ElMessageBox } from 'element-plus'; // 导入提示框

const orders = ref([]);
const loading = ref(false);
const currentRole = ref('buyer');
const userStore = useUserStore();

// 1. 获取订单 (不变，但 @change 会自动传入新 role)
async function fetchOrders(role = currentRole.value) {
  if (!userStore.user) return;
  loading.value = true;
  try {
    const response = await apiClient.get('/order/list', {
      params: { role: role }
    });
    if (response.data.code === 200) {
      orders.value = response.data.data.orders;
    } else {
      ElMessage.error(response.data.msg);
    }
  } catch (err) {
    ElMessage.error('无法加载订单列表');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchOrders();
});

// 2. 【新增】处理订单状态更新的函数
async function handleUpdateStatus(orderId, newStatus, actionName) {
  // 2.1 弹出确认框
  try {
    await ElMessageBox.confirm(
      `您确定要"${actionName}"吗？`,
      '操作确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
  } catch (cancel) {
    return ElMessage.info('操作已取消');
  }

  // 2.2 调用后端 API (即 order_routes.py 中的 update_order_status)
  try {
    const response = await apiClient.post(`/order/${orderId}/update`, {
      status: newStatus
    });

    if (response.data.code === 200) {
      ElMessage.success(`操作成功：${actionName}`);
      // 2.3 【重要】更新成功后，刷新订单列表
      fetchOrders(currentRole.value);
    } else {
      ElMessage.error(`操作失败: ${response.data.msg}`);
    }
  } catch (err) {
    ElMessage.error('请求失败，请检查网络');
  }
}

// 3. 【新增】辅助函数，用于 el-tag 颜色
function getStatusTagType(status) {
  switch (status) {
    case 1: return 'warning'; // 待支付
    case 2: return 'info';    // 已支付
    case 3: return 'primary'; // 已发货
    case 4: return 'success'; // 已收货
    case 5: return 'success'; // 已完成
    default: return 'danger';
  }
}
</script>

<style scoped>
/* 样式已由 Element Plus 处理，保持简洁 */
.order-list-container {
  max-width: 100%;
  margin: 20px auto;
}
</style>