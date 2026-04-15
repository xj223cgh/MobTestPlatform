"""异步任务管理器：线程池驱动，支持任务创建、状态查询、进度更新与过期清理。"""
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    """异步任务管理器：每个任务在独立守护线程中执行，通过 task_id 查询状态和进度。"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def create_task(self, task_name: str, task_func: Callable, *args, **kwargs) -> str:
        """创建异步任务并在守护线程中启动执行，返回 task_id。"""
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
        
        thread = threading.Thread(
            target=self._run_task,
            args=(task_id, task_func, args, kwargs)
        )
        thread.daemon = True
        thread.start()
        
        return task_id
    
    def _run_task(self, task_id: str, task_func: Callable, args: tuple, kwargs: dict):
        """在独立线程中运行任务，自动注入 task_manager 和 task_id 到 kwargs。"""
        try:
            self.update_task_status(
                task_id,
                status=TaskStatus.RUNNING,
                message='任务正在执行中...',
                started_at=datetime.now().isoformat()
            )
            
            # 将任务管理器传递给任务函数，让任务函数可以更新进度
            kwargs['task_manager'] = self
            kwargs['task_id'] = task_id
            
            result = task_func(*args, **kwargs)
            
            self.update_task_status(
                task_id,
                status=TaskStatus.COMPLETED,
                message='任务执行成功',
                result=result,
                progress=100,
                completed_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.update_task_status(
                task_id,
                status=TaskStatus.FAILED,
                message=f'任务执行失败: {str(e)}',
                error=str(e),
                completed_at=datetime.now().isoformat()
            )
    
    def update_task_status(self, task_id: str, **kwargs):
        """更新任务状态字段（线程安全）。"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)
    
    def update_task_progress(self, task_id: str, current: int, total: int, message: str = None):
        """更新任务进度百分比（current/total），可选附带消息。"""
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
        """获取任务状态字典，任务不存在返回 None。"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def clear_completed_tasks(self, older_than_hours: int = 24):
        """清理已完成/失败超过指定小时数的任务记录，释放内存。"""
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


task_manager = TaskManager()
