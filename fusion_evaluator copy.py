#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型评估融合程序
"""

import asyncio
import json
import logging
import time
import psutil
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保输出目录存在
def ensure_output_directory():
    """确保输出目录存在，如果不存在则创建"""
    output_dir = "/root/server/MCSM_Change/my_services/Reports_mixed/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"✅ 创建输出目录: {output_dir}")
    return output_dir

@dataclass
class EvaluationResult:
    dimension: str
    score: float
    max_score: float
    weight: float
    weighted_score: float
    details: Dict[str, Any]
    timestamp: str

class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 确保输出目录存在
            output_dir = ensure_output_directory()
            self.config_path = os.path.join(output_dir, "evaluation_config.json")
        else:
            self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.validate_config(config)
            logger.info(f"✅ 配置文件加载成功: {self.config_path}")
            return config
        except FileNotFoundError:
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"❌ 配置文件格式错误: {e}")
            return self.get_default_config()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置文件格式"""
        required_keys = ['evaluation_weights', 'test_configuration', 'output_settings']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"配置文件缺少必需字段: {key}")
        
        # 验证权重总和
        weights = config['evaluation_weights']
        total_weight = sum(weights[dim]['weight'] for dim in weights)
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"⚠️ 权重总和不等于1.0: {total_weight}")
        
        return True
    
    def get_default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "evaluation_weights": {
                "privacy": {"weight": 0.8},
                "functionality": {"weight": 0.7},
                "infrastructure": {"weight": 0.1},
                "performance": {"weight": 0.3},
                "security": {"weight": 0.2}
            },
            "test_configuration": {
                "target_url": "192.168.1.103:5011"
            },
            "output_settings": {
                "generate_report": True
            }
        }
    
    def get_weight(self, dimension: str) -> float:
        """获取指定维度的权重"""
        return self.config['evaluation_weights'].get(dimension, {}).get('weight', 0.0)
    
    def get_target_url(self) -> str:
        """获取目标URL"""
        return self.config['test_configuration'].get('target_url', '192.168.1.103:5011')

class FusionEvaluator:
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.results: List[EvaluationResult] = []
        self.start_time = None
        self.end_time = None
    
    def log(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        
        if level.lower() == "error":
            logger.error(formatted_message)
        elif level.lower() == "warning":
            logger.warning(formatted_message)
        else:
            logger.info(formatted_message)

    
    #### 安全维度检查
    def security_dimension_check(self):
        
        cpu_percent = psutil.cpu_percent(interval = 1)
        memory = psutil.virtual_memory()

        data_sample = "user_data_123456"
        
        
        
        return {
            'infrastructure': {'cpu_percent': cpu_percent, 'memory_percent': memory.percent},
            'data_security': {'hash': data_hash[:16], 'encrypted': True},
            'model_algorithm': {'input_safe': True, 'response_time': model_response_time},
            'application_system': {'processes': system_processes, 'connections': network_connections}
        }
    
    def check_similarity_and_update(self, new_data: List[Dict], existing_data: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """相似度检查并更新数据"""
        for new_item in new_data:
            for j, old_item in enumerate(existing_data):
                if self.calculate_similarity(new_item, old_item) > threshold:
                    existing_data[j] = new_item; break
        return existing_data

    async def simulate_privacy_evaluation(self) -> EvaluationResult:
        self.log("开始隐私保护评估")
        await asyncio.sleep(1)
        
        # 详细子测试项目
        sub_tests = {
            "data_encryption": {"score": 90, "weight": 0.3, "description": "数据加密强度测试"},
            "data_masking": {"score": 85, "weight": 0.25, "description": "数据脱敏效果测试"},
            "access_control": {"score": 80, "weight": 0.2, "description": "访问控制机制测试"},
            "data_lifecycle": {"score": 85, "weight": 0.15, "description": "数据生命周期管理测试"},
            "privacy_compliance": {"score": 88, "weight": 0.1, "description": "隐私法规合规性测试"}
        }
        
        # 计算加权平均分
        weighted_sum = sum(test["score"] * test["weight"] for test in sub_tests.values())
        score = weighted_sum
        max_score = 100.0
        weight = self.config_manager.get_weight('privacy')
        
        result = EvaluationResult(
            dimension="privacy",
            score=score,
            max_score=max_score,
            weight=weight,
            weighted_score=score * weight,
            details={
                "sub_tests": sub_tests,
                "dimension_weight": weight,
                "evaluation_method": "加权平均法"
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.log(f"隐私评估完成，得分: {score:.2f}/{max_score}")
        return result
    
    async def simulate_functionality_evaluation(self) -> EvaluationResult:
        self.log("开始功能性评估")
        await asyncio.sleep(1.2)
        
        # 详细子测试项目
        sub_tests = {
            "robustness": {"score": 90, "weight": 0.35, "description": "系统鲁棒性测试"},
            "accuracy": {"score": 85, "weight": 0.3, "description": "功能准确性测试"},
            "response_quality": {"score": 89, "weight": 0.2, "description": "响应质量测试"},
            "compatibility": {"score": 87, "weight": 0.1, "description": "兼容性测试"},
            "usability": {"score": 92, "weight": 0.05, "description": "易用性测试"}
        }
        
        # 计算加权平均分
        weighted_sum = sum(test["score"] * test["weight"] for test in sub_tests.values())
        score = weighted_sum
        max_score = 100.0
        weight = self.config_manager.get_weight('functionality')
        
        result = EvaluationResult(
            dimension="functionality",
            score=score,
            max_score=max_score,
            weight=weight,
            weighted_score=score * weight,
            details={
                "sub_tests": sub_tests,
                "dimension_weight": weight,
                "evaluation_method": "加权平均法"
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.log(f"功能性评估完成，得分: {score:.2f}/{max_score}")
        return result
    
    async def simulate_infrastructure_evaluation(self) -> EvaluationResult:
        self.log("开始基础设施评估")
        await asyncio.sleep(0.8)
        
        # 获取实际系统信息
        security_data = self.security_dimension_check()
        
        # 详细子测试项目
        sub_tests = {
            "system_stability": {"score": 95, "weight": 0.3, "description": "系统稳定性测试"},
            "resource_management": {"score": 90, "weight": 0.25, "description": "资源管理效率测试"},
            "load_balancing": {"score": 91, "weight": 0.2, "description": "负载均衡测试"},
            "cpu_performance": {"score": min(100, 100 - security_data['infrastructure']['cpu_percent']), "weight": 0.15, "description": "CPU性能测试"},
            "memory_efficiency": {"score": min(100, 100 - security_data['infrastructure']['memory_percent']), "weight": 0.1, "description": "内存使用效率测试"}
        }
        
        # 计算加权平均分
        weighted_sum = sum(test["score"] * test["weight"] for test in sub_tests.values())
        score = weighted_sum
        max_score = 100.0
        weight = self.config_manager.get_weight('infrastructure')
        
        result = EvaluationResult(
            dimension="infrastructure",
            score=score,
            max_score=max_score,
            weight=weight,
            weighted_score=score * weight,
            details={
                "sub_tests": sub_tests,
                "dimension_weight": weight,
                "evaluation_method": "加权平均法",
                "real_time_data": security_data['infrastructure']
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.log(f"基础设施评估完成，得分: {score:.2f}/{max_score}")
        return result
    
    async def simulate_performance_evaluation(self) -> EvaluationResult:
        self.log("开始性能评估")
        await asyncio.sleep(1.5)
        
        # 获取实际系统信息
        security_data = self.security_dimension_check()
        
        # 详细子测试项目
        sub_tests = {
            "response_speed": {"score": 85, "weight": 0.3, "description": "响应速度测试"},
            "resource_consumption": {"score": 90, "weight": 0.25, "description": "资源消耗测试"},
            "throughput": {"score": 86, "weight": 0.2, "description": "吞吐量测试"},
            "concurrent_processing": {"score": 88, "weight": 0.15, "description": "并发处理能力测试"},
            "scalability": {"score": 84, "weight": 0.1, "description": "可扩展性测试"}
        }
        
        # 计算加权平均分
        weighted_sum = sum(test["score"] * test["weight"] for test in sub_tests.values())
        score = weighted_sum
        max_score = 100.0
        weight = self.config_manager.get_weight('performance')
        
        result = EvaluationResult(
            dimension="performance",
            score=score,
            max_score=max_score,
            weight=weight,
            weighted_score=score * weight,
            details={
                "sub_tests": sub_tests,
                "dimension_weight": weight,
                "evaluation_method": "加权平均法",
                "real_time_data": {
                    "model_response_time": security_data['model_algorithm']['response_time']
                }
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.log(f"性能评估完成，得分: {score:.2f}/{max_score}")
        return result
    
    async def simulate_security_evaluation(self) -> EvaluationResult:
        self.log("开始安全性评估")
        await asyncio.sleep(1.3)
        
        # 获取实际系统信息
        security_data = self.security_dimension_check()
        
        # 详细子测试项目
        sub_tests = {
            "infrastructure_security": {
                "score": 88, "weight": 0.25, "description": "基础设施安全测试",
                "sub_items": {
                    "cpu_monitoring": security_data['infrastructure']['cpu_percent'],
                    "memory_monitoring": security_data['infrastructure']['memory_percent']
                }
            },
            "data_security": {
                "score": 90, "weight": 0.25, "description": "数据安全测试",
                "sub_items": {
                    "data_hash": security_data['data_security']['hash'],
                    "encryption_status": security_data['data_security']['encrypted']
                }
            },
            "model_algorithm_security": {
                "score": 89, "weight": 0.25, "description": "模型算法安全测试",
                "sub_items": {
                    "input_safety": security_data['model_algorithm']['input_safe'],
                    "response_time": security_data['model_algorithm']['response_time']
                }
            },
            "application_system_security": {
                "score": 87, "weight": 0.25, "description": "应用系统安全测试",
                "sub_items": {
                    "process_count": security_data['application_system']['processes'],
                    "network_connections": security_data['application_system']['connections']
                }
            }
        }
        
        # 计算加权平均分
        weighted_sum = sum(test["score"] * test["weight"] for test in sub_tests.values())
        score = weighted_sum
        max_score = 100.0
        weight = self.config_manager.get_weight('security')
        
        result = EvaluationResult(
            dimension="security",
            score=score,
            max_score=max_score,
            weight=weight,
            weighted_score=score * weight,
            details={
                "sub_tests": sub_tests,
                "dimension_weight": weight,
                "evaluation_method": "加权平均法",
                "real_time_data": security_data
            },
            timestamp=datetime.now().isoformat()
        )
        
        self.log(f"安全性评估完成，得分: {score:.2f}/{max_score}")
        return result
    
    async def run_comprehensive_evaluation(self):
        self.log("开始综合模型评估")
        self.start_time = time.time()
        
        tasks = [
            self.simulate_privacy_evaluation(),
            self.simulate_functionality_evaluation(),
            self.simulate_infrastructure_evaluation(),
            self.simulate_performance_evaluation(),
            self.simulate_security_evaluation()
        ]
        
        self.results = await asyncio.gather(*tasks)
        self.end_time = time.time()
        
        total_weighted_score = sum(result.weighted_score for result in self.results)
        total_weight = sum(result.weight for result in self.results)
        
        self.log(f"评估完成! 综合得分: {total_weighted_score:.2f}/{total_weight*100:.0f}")
        self.log(f"总耗时: {self.end_time - self.start_time:.2f}秒")
        
        return self.generate_summary_report()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """生成评估总结报告"""
        if not self.results:
            return {"error": "没有评估结果"}
        
        # 确保输出目录存在
        output_dir = ensure_output_directory()
        
        # 生成报告数据
        report = {
            "metadata": {
                "report_type": "model_evaluation_summary",
                "generated_timestamp": datetime.now().isoformat(),
                "evaluation_duration": self.end_time - self.start_time if self.end_time and self.start_time else 0
            },
            "summary": {
                "total_dimensions": len(self.results),
                "total_weighted_score": sum(result.weighted_score for result in self.results),
                "total_weight": sum(result.weight for result in self.results),
                "overall_score": sum(result.weighted_score for result in self.results) / sum(result.weight for result in self.results) if sum(result.weight for result in self.results) > 0 else 0
            },
            "detailed_results": [
                {
                    "dimension": result.dimension,
                    "score": result.score,
                    "max_score": result.max_score,
                    "weight": result.weight,
                    "weighted_score": result.weighted_score,
                    "details": result.details,
                    "timestamp": result.timestamp
                }
                for result in self.results
            ]
        }
        
        # 保存报告到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = os.path.join(output_dir, f"evaluation_report_{timestamp}.json")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ 评估报告已保存: {report_filename}")
        
        return report
    
    def generate_test_configuration(self) -> Dict[str, Any]:
        """生成测试配置文件"""
        
        # 获取实际系统信息用于配置参考
        security_data = self.security_dimension_check()
        
        config = {
            "test_configuration": {
                "metadata": {
                    "config_version": "1.0",
                    "created_timestamp": datetime.now().isoformat(),
                    "description": "模型评估测试配置文件"
                },
                "evaluation_dimensions": {
                    "privacy": {
                        "weight": self.config_manager.get_weight('privacy'),
                        "enabled": True,
                        "sub_tests": {
                            "data_encryption": {
                                "weight": 0.3,
                                "description": "数据加密强度测试",
                                "test_parameters": {
                                    "encryption_algorithms": ["AES-256", "RSA-2048"],
                                    "key_rotation_interval": "30d",
                                    "min_encryption_strength": 256
                                }
                            },
                            "data_masking": {
                                "weight": 0.25,
                                "description": "数据脱敏效果测试",
                                "test_parameters": {
                                    "masking_methods": ["tokenization", "pseudonymization"],
                                    "sensitive_fields": ["email", "phone", "id_number"],
                                    "masking_ratio": 0.8
                                }
                            },
                            "access_control": {
                                "weight": 0.2,
                                "description": "访问控制机制测试",
                                "test_parameters": {
                                    "authentication_methods": ["OAuth2", "JWT"],
                                    "session_timeout": 3600,
                                    "max_failed_attempts": 3
                                }
                            },
                            "data_lifecycle": {
                                "weight": 0.15,
                                "description": "数据生命周期管理测试",
                                "test_parameters": {
                                    "retention_period": "7y",
                                    "deletion_methods": ["secure_wipe", "cryptographic_erasure"],
                                    "backup_encryption": True
                                }
                            },
                            "privacy_compliance": {
                                "weight": 0.1,
                                "description": "隐私法规合规性测试",
                                "test_parameters": {
                                    "regulations": ["GDPR", "CCPA", "PIPL"],
                                    "consent_management": True,
                                    "data_portability": True
                                }
                            }
                        }
                    },
                    "functionality": {
                        "weight": self.config_manager.get_weight('functionality'),
                        "enabled": True,
                        "sub_tests": {
                            "robustness": {
                                "weight": 0.35,
                                "description": "系统鲁棒性测试",
                                "test_parameters": {
                                    "error_injection_rate": 0.1,
                                    "fault_tolerance_threshold": 0.95,
                                    "recovery_time_limit": 30
                                }
                            },
                            "accuracy": {
                                "weight": 0.3,
                                "description": "功能准确性测试",
                                "test_parameters": {
                                    "test_dataset_size": 1000,
                                    "accuracy_threshold": 0.9,
                                    "cross_validation_folds": 5
                                }
                            },
                            "response_quality": {
                                "weight": 0.2,
                                "description": "响应质量测试",
                                "test_parameters": {
                                    "quality_metrics": ["relevance", "coherence", "completeness"],
                                    "human_evaluation_samples": 100,
                                    "automated_scoring": True
                                }
                            },
                            "compatibility": {
                                "weight": 0.1,
                                "description": "兼容性测试",
                                "test_parameters": {
                                    "supported_formats": ["json", "xml", "csv"],
                                    "api_versions": ["v1", "v2"],
                                    "browser_compatibility": ["chrome", "firefox", "safari"]
                                }
                            },
                            "usability": {
                                "weight": 0.05,
                                "description": "易用性测试",
                                "test_parameters": {
                                    "user_task_completion_rate": 0.9,
                                    "average_task_time": 120,
                                    "user_satisfaction_score": 4.0
                                }
                            }
                        }
                    },
                    "infrastructure": {
                        "weight": self.config_manager.get_weight('infrastructure'),
                        "enabled": True,
                        "sub_tests": {
                            "system_stability": {
                                "weight": 0.3,
                                "description": "系统稳定性测试",
                                "test_parameters": {
                                    "uptime_requirement": 0.999,
                                    "max_downtime_per_month": 43.2,
                                    "health_check_interval": 30
                                }
                            },
                            "resource_management": {
                                "weight": 0.25,
                                "description": "资源管理效率测试",
                                "test_parameters": {
                                    "cpu_utilization_threshold": 0.8,
                                    "memory_utilization_threshold": 0.85,
                                    "disk_space_threshold": 0.9
                                }
                            },
                            "load_balancing": {
                                "weight": 0.2,
                                "description": "负载均衡测试",
                                "test_parameters": {
                                    "max_requests_per_second": 1000,
                                    "load_distribution_algorithm": "round_robin",
                                    "health_check_enabled": True
                                }
                            },
                            "cpu_performance": {
                                "weight": 0.15,
                                "description": "CPU性能测试",
                                "test_parameters": {
                                    "benchmark_duration": 300,
                                    "cpu_stress_test": True,
                                    "current_cpu_usage": security_data['infrastructure']['cpu_percent']
                                }
                            },
                            "memory_efficiency": {
                                "weight": 0.1,
                                "description": "内存使用效率测试",
                                "test_parameters": {
                                    "memory_leak_detection": True,
                                    "gc_optimization": True,
                                    "current_memory_usage": security_data['infrastructure']['memory_percent']
                                }
                            }
                        }
                    },
                    "performance": {
                        "weight": self.config_manager.get_weight('performance'),
                        "enabled": True,
                        "sub_tests": {
                            "response_speed": {
                                "weight": 0.3,
                                "description": "响应速度测试",
                                "test_parameters": {
                                    "max_response_time": 2000,
                                    "percentile_95_threshold": 1500,
                                    "concurrent_users": 100
                                }
                            },
                            "resource_consumption": {
                                "weight": 0.25,
                                "description": "资源消耗测试",
                                "test_parameters": {
                                    "max_cpu_usage": 0.8,
                                    "max_memory_usage": 0.85,
                                    "max_disk_io": 1000
                                }
                            },
                            "throughput": {
                                "weight": 0.2,
                                "description": "吞吐量测试",
                                "test_parameters": {
                                    "min_requests_per_second": 500,
                                    "test_duration": 600,
                                    "ramp_up_time": 60
                                }
                            },
                            "concurrent_processing": {
                                "weight": 0.15,
                                "description": "并发处理能力测试",
                                "test_parameters": {
                                    "max_concurrent_requests": 1000,
                                    "queue_size_limit": 10000,
                                    "timeout_threshold": 30
                                }
                            },
                            "scalability": {
                                "weight": 0.1,
                                "description": "可扩展性测试",
                                "test_parameters": {
                                    "auto_scaling_enabled": True,
                                    "min_instances": 2,
                                    "max_instances": 10
                                }
                            }
                        }
                    },
                    "security": {
                        "weight": self.config_manager.get_weight('security'),
                        "enabled": True,
                        "sub_tests": {
                            "infrastructure_security": {
                                "weight": 0.25,
                                "description": "基础设施安全测试",
                                "test_parameters": {
                                    "vulnerability_scanning": True,
                                    "penetration_testing": True,
                                    "security_monitoring": {
                                        "cpu_monitoring": True,
                                        "memory_monitoring": True,
                                        "current_cpu_usage": security_data['infrastructure']['cpu_percent'],
                                        "current_memory_usage": security_data['infrastructure']['memory_percent']
                                    }
                                }
                            },
                            "data_security": {
                                "weight": 0.25,
                                "description": "数据安全测试",
                                "test_parameters": {
                                    "data_integrity_check": True,
                                    "hash_verification": True,
                                    "encryption_at_rest": True,
                                    "encryption_in_transit": True,
                                    "sample_data_hash": security_data['data_security']['hash']
                                }
                            },
                            "model_algorithm_security": {
                                "weight": 0.25,
                                "description": "模型算法安全测试",
                                "test_parameters": {
                                    "adversarial_testing": True,
                                    "input_validation": True,
                                    "output_sanitization": True,
                                    "model_poisoning_detection": True,
                                    "response_time_monitoring": True
                                }
                            },
                            "application_system_security": {
                                "weight": 0.25,
                                "description": "应用系统安全测试",
                                "test_parameters": {
                                    "authentication_testing": True,
                                    "authorization_testing": True,
                                    "session_management": True,
                                    "input_sanitization": True,
                                    "system_monitoring": {
                                        "process_monitoring": True,
                                        "network_monitoring": True,
                                        "current_processes": security_data['application_system']['processes'],
                                        "current_connections": security_data['application_system']['connections']
                                    }
                                }
                            }
                        }
                    }
                },
                "test_execution_settings": {
                    "timeout_seconds": 30,
                    "retry_attempts": 3,
                    "parallel_execution": True,
                    "log_level": "INFO",
                    "report_format": "json"
                },
                "environment_requirements": {
                    "python_version": ">=3.8",
                    "required_packages": ["psutil", "hashlib", "asyncio", "json"],
                    "system_requirements": {
                        "min_memory_gb": 4,
                        "min_cpu_cores": 2,
                        "min_disk_space_gb": 10
                    }
                }
            }
        }
        
        return config

if __name__ == "__main__":
    # 确保输出目录存在
    output_dir = ensure_output_directory()
    
    evaluator = FusionEvaluator()
    
    # 生成测试配置文件
    config = evaluator.generate_test_configuration()
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"config_{timestamp}.json")
    
    # 保存测试配置到JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"测试配置文件已生成: {filename}")
    print(f"配置版本: {config['test_configuration']['metadata']['config_version']}")
    print("\n评估维度配置:")
    for dimension, data in config['test_configuration']['evaluation_dimensions'].items():
        sub_tests_count = len(data['sub_tests'])
        print(f"  {dimension}: 权重 {data['weight']}, 子测试项 {sub_tests_count}个")