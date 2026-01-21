from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': ThreadPoolExecutor(20)
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, timezone='Asia/Shanghai')


def init_scheduler():
    """初始化定时任务调度器"""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("定时任务调度器已启动")
    except Exception as e:
        logger.error(f"定时任务调度器启动失败: {e}")


def shutdown_scheduler():
    """关闭定时任务调度器"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("定时任务调度器已关闭")
    except Exception as e:
        logger.error(f"定时任务调度器关闭失败: {e}")


def add_scheduled_task(task_id, func, run_date, args=None, kwargs=None):
    """添加定时任务"""
    try:
        job = scheduler.add_job(
            func=func,
            trigger=DateTrigger(run_date=run_date, timezone='Asia/Shanghai'),
            id=str(task_id),
            args=args or [],
            kwargs=kwargs or {},
            replace_existing=True
        )
        logger.info(f"定时任务已添加: {task_id}, 执行时间: {run_date}")
        return job
    except Exception as e:
        logger.error(f"添加定时任务失败: {e}")
        raise


def remove_scheduled_task(task_id):
    """移除定时任务"""
    try:
        scheduler.remove_job(str(task_id))
        logger.info(f"定时任务已移除: {task_id}")
        return True
    except Exception as e:
        logger.error(f"移除定时任务失败: {e}")
        return False


def get_scheduled_tasks():
    """获取所有定时任务"""
    try:
        jobs = scheduler.get_jobs()
        tasks = []
        for job in jobs:
            tasks.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'args': job.args,
                'kwargs': job.kwargs
            })
        return tasks
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        return []


def get_task_status(task_id):
    """获取定时任务状态"""
    try:
        job = scheduler.get_job(str(task_id))
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'status': 'scheduled'
            }
        return None
    except Exception as e:
        logger.error(f"获取定时任务状态失败: {e}")
        return None
