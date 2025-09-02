#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置权重监控Web应用
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from fusion_evaluator import ConfigManager

app = Flask(__name__)

def get_config_data():
    """获取配置数据"""
    try:
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 维度中文翻译映射
        dimension_translations = {
            'privacy': '隐私保护',
            'functionality': '功能性',
            'infrastructure': '基础设施',
            'performance': '性能',
            'security': '安全性'
        }
        
        # 提取权重数据
        weights = config.get('evaluation_weights', {})
        
        # 转换为ECharts格式，使用中文名称
        pie_data = []
        for dimension, config_data in weights.items():
            weight = config_data.get('weight', 0)
            chinese_name = dimension_translations.get(dimension, dimension)
            pie_data.append({
                'name': chinese_name,
                'value': weight,
                'original_name': dimension  # 保留原始名称用于API调用
            })
        
        return {
            'weights': weights,
            'pie_data': pie_data,
            'total_weight': sum(item['value'] for item in pie_data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'weights': {},
            'pie_data': [],
            'total_weight': 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def get_folder_monitor_data():
    """获取文件夹监控数据"""
    try:
        # 监控配置文件列表
        target_folder = '/root/server/MCSM_Change/my_services/model_test/test_cfg'
        source_folder = '/root/server/MCSM_Change/my_services/Reports_mixed/output'
        
        target_files = []
        source_files = []
        
        # 获取配置文件列表内容
        if os.path.exists(target_folder):
            for item in os.listdir(target_folder):
                item_path = os.path.join(target_folder, item)
                if os.path.isfile(item_path):
                    stat = os.stat(item_path)
                    target_files.append({
                        'name': item,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%m-%d %H:%M:%S'),
                        'type': 'file'
                    })
                elif os.path.isdir(item_path):
                    target_files.append({
                        'name': item,
                        'size': 0,
                        'modified': '',
                        'type': 'directory'
                    })
        
        # 获取未挂载的配置文件列表内容
        if os.path.exists(source_folder):
            for item in os.listdir(source_folder):
                item_path = os.path.join(source_folder, item)
                if os.path.isfile(item_path):
                    stat = os.stat(item_path)
                    source_files.append({
                        'name': item,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%m-%d %H:%M:%S'),
                        'type': 'file'
                    })
                elif os.path.isdir(item_path):
                    source_files.append({
                        'name': item,
                        'size': 0,
                        'modified': '',
                        'type': 'directory'
                    })
        
        return {
            'target_folder': target_folder,
            'source_folder': source_folder,
            'target_files': target_files,
            'source_files': source_files,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'target_folder': '/root/server/MCSM_Change/my_services/model_test/test_cfg',
            'source_folder': '/root/server/MCSM_Change/my_services/Reports_mixed/output',
            'target_files': [],
            'source_files': [],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def index():
    """主页"""
    config_data = get_config_data()
    return render_template('index.html', config_data=config_data)

@app.route('/monitor')
def monitor():
    """文件夹监控页面"""
    monitor_data = get_folder_monitor_data()
    return render_template('monitor.html', monitor_data=monitor_data)

@app.route('/api/config')
def api_config():
    """API接口返回配置数据"""
    return jsonify(get_config_data())

@app.route('/api/monitor')
def api_monitor():
    """API接口返回监控数据"""
    return jsonify(get_folder_monitor_data())

@app.route('/api/rename_file', methods=['POST'])
def rename_file():
    """重命名文件"""
    try:
        data = request.get_json()
        folder_type = data.get('folder_type')  # 'source' 或 'target'
        old_name = data.get('old_name')
        new_name = data.get('new_name')
        
        if not all([folder_type, old_name, new_name]):
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 确定文件夹路径
        if folder_type == 'source':
            folder_path = '/root/server/MCSM_Change/my_services/Reports_mixed/output'
        elif folder_type == 'target':
            folder_path = '/root/server/MCSM_Change/my_services/model_test/test_cfg'
        else:
            return jsonify({'success': False, 'error': '无效的文件夹类型'})
        
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        
        # 检查文件是否存在
        if not os.path.exists(old_path):
            return jsonify({'success': False, 'error': f'文件 {old_name} 不存在'})
        
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            return jsonify({'success': False, 'error': f'文件 {new_name} 已存在'})
        
        # 执行重命名
        os.rename(old_path, new_path)
        
        return jsonify({'success': True, 'message': f'文件重命名成功: {old_name} -> {new_name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/transfer_file', methods=['POST'])
def transfer_file():
    """从未挂载的配置文件列表传输文件到配置文件列表"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        
        if not file_name:
            return jsonify({'success': False, 'error': '缺少文件名参数'})
        
        source_path = os.path.join('/root/server/MCSM_Change/my_services/Reports_mixed/output', file_name)
        target_path = os.path.join('/root/server/MCSM_Change/my_services/model_test/test_cfg', file_name)
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': f'源文件 {file_name} 不存在'})
        
        # 检查目标文件是否已存在
        if os.path.exists(target_path):
            return jsonify({'success': False, 'error': f'目标文件 {file_name} 已存在'})
        
        # 确保配置文件列表存在
        os.makedirs('/root/server/MCSM_Change/my_services/model_test/test_cfg', exist_ok=True)
        
        # 执行文件传输
        import shutil
        shutil.copy2(source_path, target_path)
        
        return jsonify({'success': True, 'message': f'文件传输成功: {file_name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    """删除配置文件列表中的文件"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        
        if not file_name:
            return jsonify({'success': False, 'error': '缺少文件名参数'})
        
        target_path = os.path.join('/root/server/MCSM_Change/my_services/model_test/test_cfg', file_name)
        
        # 检查文件是否存在
        if not os.path.exists(target_path):
            return jsonify({'success': False, 'error': f'文件 {file_name} 不存在'})
        
        # 执行删除
        if os.path.isfile(target_path):
            os.remove(target_path)
        elif os.path.isdir(target_path):
            import shutil
            shutil.rmtree(target_path)
        
        return jsonify({'success': True, 'message': f'文件删除成功: {file_name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_source_file', methods=['POST'])
def delete_source_file():
    """删除未挂载的配置文件列表中的文件"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        
        if not file_name:
            return jsonify({'success': False, 'error': '缺少文件名参数'})
        
        source_path = os.path.join('/root/server/MCSM_Change/my_services/Reports_mixed/output', file_name)
        
        # 检查文件是否存在
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': f'文件 {file_name} 不存在'})
        
        # 执行删除
        if os.path.isfile(source_path):
            os.remove(source_path)
        elif os.path.isdir(source_path):
            import shutil
            shutil.rmtree(source_path)
        
        return jsonify({'success': True, 'message': f'文件删除成功: {file_name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/run_fusion_evaluator', methods=['POST'])
def run_fusion_evaluator():
    """运行fusion_evaluator.py文件"""
    try:
        import subprocess
        import sys
        
        # 使用绝对路径
        script_path = '/root/server/MCSM_Change/my_services/Reports_mixed/fusion_evaluator.py'
        
        # 检查文件是否存在
        if not os.path.exists(script_path):
            return jsonify({'success': False, 'error': f'文件不存在: {script_path}'})
        
        # 运行Python脚本
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd='/root/server/MCSM_Change/my_services/Reports_mixed',
            timeout=60  # 设置60秒超时
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': 'fusion_evaluator.py 运行成功',
                'output': result.stdout,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({
                'success': False, 
                'error': f'运行失败，返回码: {result.returncode}',
                'stderr': result.stderr,
                'stdout': result.stdout
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': '运行超时（60秒）'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def update_fusion_evaluator_weights(dimension: str, new_weight: float):
    """直接更新fusion_evaluator.py文件中的权重配置"""
    try:
        # 读取fusion_evaluator.py文件
        script_path = '/root/server/MCSM_Change/my_services/Reports_mixed/fusion_evaluator.py'
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        # 构建更精确的正则表达式来匹配get_default_config方法中的权重
        # 匹配格式: "dimension": {"weight": value}
        pattern = rf'(\s*)"{dimension}":\s*\{{"weight":\s*([0-9.]+)\}}'
        replacement = rf'\1"{dimension}": {{"weight": {new_weight}}}'
        
        # 执行替换
        new_content = re.sub(pattern, replacement, content)
        
        # 检查是否成功替换
        if new_content == content:
            print(f"警告: 未找到维度 '{dimension}' 的权重配置")
            return False
        
        # 写回文件
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 成功更新 {dimension} 权重为 {new_weight}")
        return True
    except Exception as e:
        print(f"❌ 更新fusion_evaluator.py文件失败: {e}")
        return False

@app.route('/api/update_weight', methods=['POST'])
def update_weight():
    """更新权重配置"""
    try:
        data = request.get_json()
        dimension = data.get('dimension')
        new_weight = float(data.get('weight'))
        
        if not dimension or new_weight < 0:
            return jsonify({'success': False, 'error': '无效的参数'})
        
        # 直接更新fusion_evaluator.py文件中的权重
        if update_fusion_evaluator_weights(dimension, new_weight):
            return jsonify({'success': True, 'message': f'权重更新成功: {dimension} = {new_weight}'})
        else:
            return jsonify({'success': False, 'error': '更新fusion_evaluator.py文件失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 确保templates目录存在
    templates_dir = '/root/server/MCSM_Change/my_services/Reports_mixed/templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    print("🚀 启动配置权重监控Web应用...")
    print("📊 访问地址: http://localhost:5201")
    app.run(host='0.0.0.0', port=5201, debug=True)
