# 配置权重监控Web应用

一个基于Flask的现代化Web应用，用于监控和管理配置权重，以及文件系统操作。

## 🚀 功能特性

### 权重配置管理
- **可视化权重分布**: 使用ECharts饼图展示各维度权重分布
- **实时权重调整**: 通过滑块调整各维度权重值
- **权重更新**: 直接更新fusion_evaluator.py文件中的权重配置
- **系统操作**: 运行融合评估器脚本

### 文件监控管理
- **双文件夹监控**: 监控配置文件列表和未挂载配置文件列表
- **文件操作**: 支持文件传输、重命名、删除等操作

- **拖拽支持**: 支持文件拖拽操作

## 🛠️ 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **图表**: ECharts 5.4.3
- **样式**: 现代化CSS，支持响应式设计
- **交互**: 原生JavaScript，无框架依赖

## 📁 项目结构

```
Reports_mixed/
├── main.py                 # Flask主应用
├── fusion_evaluator.py     # 融合评估器脚本
├── templates/              # HTML模板
│   ├── index.html         # 主页模板
│   └── monitor.html       # 文件监控模板
├── static/                 # 静态文件
│   ├── css/
│   │   └── style.css      # 主样式文件
│   └── js/
│       ├── main.js        # 主页JavaScript
│       └── monitor.js     # 监控页面JavaScript
├── output/                 # 未挂载配置文件列表
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 运行应用

```bash
python main.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:5201

## 📊 主要页面

### 主页 (/)
- **权重分布图表**: 显示各维度权重的饼图
- **权重调整控制**: 通过滑块调整各维度权重
- **系统操作**: 运行评估器、刷新数据等

### 文件监控页 (/monitor)
- **配置文件列表**: 显示已挂载的配置文件
- **未挂载配置文件列表**: 显示待处理的配置文件
- **文件操作**: 传输、重命名、删除文件

## 🔧 API接口

### 配置相关
- `GET /api/config` - 获取配置数据
- `POST /api/update_weight` - 更新权重配置

### 监控相关
- `GET /api/monitor` - 获取监控数据
- `POST /api/transfer_file` - 传输文件
- `POST /api/rename_file` - 重命名文件
- `POST /api/delete_file` - 删除文件
- `POST /api/delete_source_file` - 删除源文件

### 系统操作
- `POST /api/run_fusion_evaluator` - 运行融合评估器

## 🎨 界面特性

- **现代化设计**: 使用渐变背景和毛玻璃效果
- **响应式布局**: 支持各种屏幕尺寸
- **交互动画**: 平滑的过渡和悬停效果
- **直观操作**: 清晰的按钮和控件设计
- **实时反馈**: 操作结果即时显示

## 🔒 安全特性

- **输入验证**: 所有用户输入都经过验证
- **错误处理**: 完善的异常处理机制
- **权限控制**: 文件操作权限检查
- **超时保护**: API调用超时保护

## 📱 响应式支持

- **桌面端**: 完整功能，多列布局
- **平板端**: 适配中等屏幕
- **移动端**: 单列布局，触摸友好

## 🚀 部署说明

### 生产环境部署

1. 修改Flask配置
```python
app.run(host='0.0.0.0', port=5201, debug=False)
```

2. 使用生产级WSGI服务器
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5201 main:app
```

3. 配置反向代理 (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5201;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   - 修改main.py中的端口号
   - 或使用 `lsof -i :5201` 查看占用进程

2. **模板文件未找到**
   - 确保templates目录存在
   - 检查文件权限

3. **静态文件未加载**
   - 确保static目录结构正确
   - 检查CSS/JS文件路径

### 日志查看

应用运行时会输出详细日志，包括：
- 启动信息
- 请求处理
- 错误详情

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**享受使用配置权重监控Web应用！** 🎉