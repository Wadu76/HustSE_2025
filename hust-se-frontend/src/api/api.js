//src/api/api.js

import axios from 'axios';

//1. 创建一个新的 axios 实例
const apiClient = axios.create({
    //后端API“厨房”的地址
    baseURL: 'http://127.0.0.1:5000',

    // ！！！！！！【最重要】！！！！！！
    // 允许跨域请求携带 Cookie (Session ID)
    withCredentials: true
});

//2. 默认导出这个配置好的实例
export default apiClient;