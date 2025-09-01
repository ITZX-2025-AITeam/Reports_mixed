// 全局变量
let weightChart = null;
let currentWeights = {};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeWeightChart();
    initializeWeightControls();
    initializeEventListeners();
    loadConfigData();
});

// 初始化权重图表
function initializeWeightChart() {
    const chartDom = document.getElementById('weightChart');
    if (!chartDom) return;
    
    weightChart = echarts.init(chartDom);
    
    // 设置图表配置
    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            textStyle: {
                color: '#333'
            }
        },
        series: [
            {
                name: '权重分布',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '18',
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: []
            }
        ],
        color: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    };
    
    weightChart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        weightChart.resize();
    });
}

// 初始化权重控制
function initializeWeightControls() {
    const sliders = document.querySelectorAll('.weight-slider');
    const values = document.querySelectorAll('.weight-value');
    
    sliders.forEach((slider, index) => {
        slider.addEventListener('input', function() {
            values[index].textContent = parseFloat(this.value).toFixed(1);
        });
    });
}

// 初始化事件监听器
function initializeEventListeners() {
    // 权重更新按钮
    document.querySelectorAll('.update-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const dimension = this.dataset.dimension;
            const slider = this.parentElement.querySelector('.weight-slider');
            const weight = parseFloat(slider.value);
            
            updateWeight(dimension, weight);
        });
    });
    
    // 运行评估器按钮
    document.getElementById('runEvaluator')?.addEventListener('click', runFusionEvaluator);
    
    // 刷新数据按钮
    document.getElementById('refreshData')?.addEventListener('click', loadConfigData);
}

// 加载配置数据
async function loadConfigData() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.error) {
            showActionResult('error', `加载配置失败: ${data.error}`);
            return;
        }
        
        // 更新图表
        updateWeightChart(data.pie_data);
        
        // 更新权重控制
        updateWeightControls(data.weights);
        
        // 更新显示信息
        updateDisplayInfo(data);
        
        // 保存当前权重
        currentWeights = data.weights;
        
    } catch (error) {
        showActionResult('error', `加载配置失败: ${error.message}`);
    }
}

// 更新权重图表
function updateWeightChart(pieData) {
    if (!weightChart || !pieData) return;
    
    const option = {
        series: [{
            data: pieData
        }]
    };
    
    weightChart.setOption(option);
}

// 更新权重控制
function updateWeightControls(weights) {
    Object.keys(weights).forEach(dimension => {
        const control = document.getElementById(`${dimension}-control`);
        if (control) {
            const slider = control.querySelector('.weight-slider');
            const value = control.querySelector('.weight-value');
            
            if (slider && value) {
                slider.value = weights[dimension].weight;
                value.textContent = parseFloat(weights[dimension].weight).toFixed(1);
            }
        }
    });
}

// 更新显示信息
function updateDisplayInfo(data) {
    const totalWeight = document.getElementById('totalWeight');
    const lastUpdated = document.getElementById('lastUpdated');
    
    if (totalWeight) totalWeight.textContent = data.total_weight;
    if (lastUpdated) lastUpdated.textContent = data.last_updated;
}

// 更新权重
async function updateWeight(dimension, newWeight) {
    try {
        const response = await fetch('/api/update_weight', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dimension: dimension,
                weight: newWeight
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showActionResult('success', result.message);
            // 重新加载数据
            setTimeout(loadConfigData, 1000);
        } else {
            showActionResult('error', result.error);
        }
        
    } catch (error) {
        showActionResult('error', `更新权重失败: ${error.message}`);
    }
}

// 运行融合评估器
async function runFusionEvaluator() {
    const btn = document.getElementById('runEvaluator');
    const originalText = btn.textContent;
    
    try {
        btn.textContent = '运行中...';
        btn.disabled = true;
        
        const response = await fetch('/api/run_fusion_evaluator', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showActionResult('success', `${result.message}<br>输出: ${result.output}<br>时间: ${result.timestamp}`);
        } else {
            showActionResult('error', `运行失败: ${result.error}<br>错误输出: ${result.stderr || '无'}`);
        }
        
    } catch (error) {
        showActionResult('error', `运行评估器失败: ${error.message}`);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// 显示操作结果
function showActionResult(type, message) {
    const resultDiv = document.getElementById('actionResult');
    if (!resultDiv) return;
    
    resultDiv.className = `action-result ${type}`;
    resultDiv.innerHTML = message;
    
    // 5秒后自动隐藏
    setTimeout(() => {
        resultDiv.style.display = 'none';
    }, 5000);
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函数：格式化时间
function formatDateTime(timestamp) {
    if (!timestamp) return '未知';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

// 工具函数：显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 添加通知样式
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.info {
        background: #0969da;
    }
    
    .notification.success {
        background: #2da44e;
    }
    
    .notification.warning {
        background: #d97706;
        color: white;
    }
    
    .notification.error {
        background: #cf222e;
    }
`;
document.head.appendChild(style);
