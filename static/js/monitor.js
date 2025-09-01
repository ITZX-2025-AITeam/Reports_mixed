// 全局变量
let currentRenameData = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeFileOperations();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 传输文件按钮
    document.querySelectorAll('.transfer-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileName = this.dataset.name;
            transferFile(fileName);
        });
    });
    
    // 重命名文件按钮
    document.querySelectorAll('.rename-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const folderType = this.dataset.folder;
            const fileName = this.dataset.name;
            showRenameModal(folderType, fileName);
        });
    });
    
    // 删除文件按钮
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const folderType = this.dataset.folder;
            const fileName = this.dataset.name;
            deleteFile(folderType, fileName);
        });
    });
    
    // 模态框事件
    document.getElementById('confirmRename')?.addEventListener('click', confirmRename);
    document.getElementById('cancelRename')?.addEventListener('click', hideRenameModal);
    
    // 点击模态框外部关闭
    document.getElementById('renameModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            hideRenameModal();
        }
    });
}

// 初始化文件操作
function initializeFileOperations() {
    // 添加文件拖拽功能
    addDragAndDropSupport();
    
    // 添加文件搜索功能
    addSearchFunctionality();
}

// 传输文件
async function transferFile(fileName) {
    if (!confirm(`确定要传输文件 "${fileName}" 到配置文件列表吗？`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/transfer_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_name: fileName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            // 刷新页面数据
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(`传输失败: ${result.error}`, 'error');
        }
        
    } catch (error) {
        showNotification(`传输失败: ${error.message}`, 'error');
    }
}

// 显示重命名模态框
function showRenameModal(folderType, fileName) {
    currentRenameData = { folderType, fileName };
    
    const modal = document.getElementById('renameModal');
    const input = document.getElementById('newFileName');
    
    if (modal && input) {
        input.value = fileName;
        modal.style.display = 'block';
        input.focus();
        input.select();
    }
}

// 隐藏重命名模态框
function hideRenameModal() {
    const modal = document.getElementById('renameModal');
    if (modal) {
        modal.style.display = 'none';
        currentRenameData = null;
    }
}

// 确认重命名
async function confirmRename() {
    if (!currentRenameData) return;
    
    const newFileName = document.getElementById('newFileName').value.trim();
    
    if (!newFileName) {
        showNotification('请输入新文件名', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/rename_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                folder_type: currentRenameData.folderType,
                old_name: currentRenameData.fileName,
                new_name: newFileName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            hideRenameModal();
            // 刷新页面数据
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(`重命名失败: ${result.error}`, 'error');
        }
        
    } catch (error) {
        showNotification(`重命名失败: ${error.message}`, 'error');
    }
}

// 删除文件
async function deleteFile(folderType, fileName) {
    const folderName = folderType === 'source' ? '未挂载配置文件列表' : '配置文件列表';
    
    if (!confirm(`确定要删除 ${folderName} 中的文件 "${fileName}" 吗？此操作不可恢复！`)) {
        return;
    }
    
    try {
        const endpoint = folderType === 'source' ? '/api/delete_source_file' : '/api/delete_file';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_name: fileName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            // 刷新页面数据
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(`删除失败: ${result.error}`, 'error');
        }
        
    } catch (error) {
        showNotification(`删除失败: ${error.message}`, 'error');
    }
}

// 添加拖拽支持
function addDragAndDropSupport() {
    const fileLists = document.querySelectorAll('.file-list');
    
    fileLists.forEach(list => {
        list.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        list.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        list.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                showNotification(`拖拽了 ${files.length} 个文件`, 'info');
                // 这里可以添加文件上传逻辑
            }
        });
    });
}

// 添加搜索功能
function addSearchFunctionality() {
    // 为每个文件列表添加搜索框
    const fileLists = document.querySelectorAll('.file-list');
    
    fileLists.forEach((list, index) => {
        const searchBox = document.createElement('div');
        searchBox.className = 'search-box';
        searchBox.innerHTML = `
            <input type="text" placeholder="搜索文件..." class="search-input">
            <button class="search-btn">🔍</button>
        `;
        
        list.parentElement.insertBefore(searchBox, list);
        
        const searchInput = searchBox.querySelector('.search-input');
        const searchBtn = searchBox.querySelector('.search-btn');
        
        // 搜索功能
        const performSearch = () => {
            const query = searchInput.value.toLowerCase();
            const fileItems = list.querySelectorAll('.file-item');
            
            fileItems.forEach(item => {
                const fileName = item.querySelector('.file-name').textContent.toLowerCase();
                if (fileName.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        };
        
        searchInput.addEventListener('input', performSearch);
        searchBtn.addEventListener('click', performSearch);
    });
}

// 显示通知
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

// 添加搜索框样式
const searchStyle = document.createElement('style');
searchStyle.textContent = `
    .search-box {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        align-items: center;
    }
    
    .search-input {
        flex: 1;
        padding: 8px 12px;
        border: 2px solid #ddd;
        border-radius: 6px;
        font-size: 0.9rem;
        transition: border-color 0.3s ease;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .search-btn {
        padding: 8px 12px;
        background: #0969da;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .search-btn:hover {
        background: #0858b9;
    }
    
    .drag-over {
        background: rgba(9, 105, 218, 0.1);
        border: 2px dashed #0969da;
    }
    
    .file-item {
        transition: all 0.3s ease;
    }
    
    .file-item:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(searchStyle);
