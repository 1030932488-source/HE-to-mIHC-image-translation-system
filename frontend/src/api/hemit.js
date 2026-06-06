/**
 * HEMIT API 客户端
 */
import axios from 'axios'

const apiClient = axios.create({
    baseURL: '/api/v1',
    timeout: 120000,  // 2分钟超时 (模型推理可能较慢)
    headers: {
        'Content-Type': 'multipart/form-data'
    }
})

/**
 * 转换 H&E 图像为 mIHC 图像
 * @param {File} file - H&E 图像文件
 * @param {string} resolution - 分辨率 ('high' 或 'low')
 * @returns {Promise} API 响应
 */
export const convertImage = async (file, resolution = 'high') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('resolution', resolution)

    const response = await apiClient.post('/convert', formData)
    return response.data
}

/**
 * 健康检查
 * @returns {Promise} API 响应
 */
export const healthCheck = async () => {
    const response = await axios.get('/api/health')
    return response.data
}
