import { defineStore } from 'pinia'
import { ref } from 'vue'

//1. 定义并导出一个 store
//'useUserStore' 是这个 store 的“名字”
export const useUserStore = defineStore('user', () => {
    //2. 定义 "State" (全局状态)
    const user = ref(null) // 存放用户信息 (例如 { id: 1, username: '...' })

    //3. 定义 "Actions" (修改状态的方法)

    //登录成功时，调用这个方法来存储用户信息
    function setUser(userInfo) {
        user.value = userInfo
    }

    //退出登录时，调用这个方法来清空用户信息
    function clearUser() {
        user.value = null
    }

    //4. 返回 state 和 actions
    return {
        user,
        setUser,
        clearUser
    }
})