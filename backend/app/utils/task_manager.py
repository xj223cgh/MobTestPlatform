"""
异步任务管理器
用于管理后台异步任务，支持任务状态查询和进度更新
"""
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional


class TaskStatus:
    """任务状态枚举"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class TaskManager:
    """任务管理器，用于管理后台异步任务"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}  # 存储所有任务的状态
        self.lock = threading.Lock()  # 线程锁，确保线程安全
    
    def create_task(self, task_name: str, task_func: Callable, *args, **kwargs) -> str:
        """
        创建一个新的异步任务
        
        Args:
            task_name: 任务名称
            task_func: 任务执行函数
            *args: 任务函数的位置参数
            **kwargs: 任务函数的关键字参数
            
        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.tasks[task_id] = {
                'task_id': task_id,
                'task_name': task_name,
                'status': TaskStatus.PENDING,
                'progress': 0,
                'total': 0,
                'current': 0,
                'message': '任务已创建，等待执行...',
                'result': None,
                'error': None,
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
            }
        
        # 创建并启动线程
        thread = threading.Thread(
            target=self._run_task,
            args=(task_id, task_func, args, kwargs)
        )
        thread.daemon = True  # 设置为守护线程
        thread.start()
        
        return task_id
    
    def _run_task(self, task_id: str, task_func: Callable, args: tuple, kwargs: dict):
        """
        在独立线程中运行任务
        
        Args:
            task_id: 任务ID
            task_func: 任务执行函数
            args: 任务函数的位置参数
            kwargs: 任务函数的关键字参数
        """
        try:
            # 更新任务状态为运行中
            self.update_task_status(
                task_id,
                status=TaskStatus.RUNNING,
                message='任务正在执行中...',
                started_at=datetime.now().isoformat()
            )
            
            # 将任务管理器传递给任务函数，让任务函数可以更新进度
            kwargs['task_manager'] = self
            kwargs['task_id'] = task_id
            
            # 执行任务函数
            result = task_func(*args, **kwargs)
            
            # 更新任务状态为完成
            self.update_task_status(
                task_id,
                status=TaskStatus.COMPLETED,
                message='任务执行成功',
                result=result,
                progress=100,
                completed_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            # 更新任务状态为失败
            self.update_task_status(
                task_id,
                status=TaskStatus.FAILED,
                message=f'任务执行失败: {str(e)}',
                error=str(e),
                completed_at=datetime.now().isoformat()
            )
    
    def update_task_status(self, task_id: str, **kwargs):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)
    
    def update_task_progress(self, task_id: str, current: int, total: int, message: str = None):
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            current: 当前进度
            total: 总进度
            message: 进度消息
        """
        progress = int((current / total * 100)) if total > 0 else 0
        update_data = {
            'current': current,
            'total': total,
            'progress': progress
        }
        if message:
            update_data['message'] = message
        
        self.update_task_status(task_id, **update_data)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态字典，如果任务不存在则返回None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def clear_completed_tasks(self, older_than_hours: int = 24):
        """
        清理已完成的任务
        
        Args:
            older_than_hours: 清理多少小时前的任务
        """
        from datetime import timedelta
        
        with self.lock:
            now = datetime.now()
            tasks_to_remove = []
            
            for task_id, task in self.tasks.items():
                if task['status'] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    completed_at = task.get('completed_at')
                    if completed_at:
                        completed_time = datetime.fromisoformat(completed_at)
                        if now - completed_time > timedelta(hours=older_than_hours):
                            tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]


# 全局任务管理器实例
task_manager = TaskManager()
