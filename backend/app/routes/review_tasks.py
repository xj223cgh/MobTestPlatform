from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from app.models.models import db, TestSuite, TestSuiteReviewTask, TestCaseReviewDetail, TestCase, User
from app.utils.helpers import success_response, error_response, get_pagination_params

# 设置本地时区
LOCAL_TIMEZONE = timezone(timedelta(hours=8))

# 创建Blueprint
bp = Blueprint('review_tasks', __name__, url_prefix='/api/review-tasks')


@bp.route('/test-suites/<int:suite_id>/initiate-review', methods=['POST'])
@login_required
def initiate_review(suite_id):
    """发起用例集评审"""
    try:
        # 获取用例集
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 验证用例集类型
        if suite.type != 'suite':
            return error_response(400, '只有用例集才能发起评审')
        
        # 获取请求数据
        data = request.get_json()
        reviewer_id = data.get('reviewer_id')
        
        # 验证评审人
        if not reviewer_id:
            return error_response(400, '评审人不能为空')
        
        reviewer = User.query.get(reviewer_id)
        if not reviewer:
            return error_response(400, '评审人不存在')
        
        # 获取用例集下的所有用例
        cases = TestCase.query.filter_by(suite_id=suite_id).all()
        if not cases:
            return error_response(400, '用例集下没有测试用例，无法发起评审')
        
        # 创建评审任务，初始状态为待评审
        review_task = TestSuiteReviewTask(
            suite_id=suite_id,
            initiator_id=current_user.id,
            reviewer_id=reviewer_id,
            status='pending'
            # start_time留空，在评审人开始评审时设置
        )
        db.session.add(review_task)
        db.session.flush()  # 获取review_task.id
        
        # 为每条用例创建评审详情记录
        for case in cases:
            case_review = TestCaseReviewDetail(
                review_task_id=review_task.id,
                case_id=case.id,
                reviewer_id=reviewer_id,
                review_status='pending'
            )
            db.session.add(case_review)
        
        # 不需要更新用例集状态，评审状态由评审任务管理
        
        db.session.commit()
        
        return success_response({
            'message': f'成功发起评审，共{len(cases)}条用例待评审',
            'review_task_id': review_task.id,
            'review_task': review_task.to_dict()
        }, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'发起评审失败: {str(e)}')


@bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_review_task(task_id):
    """获取评审任务详情"""
    try:
        # 获取评审任务
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        

        
        # 获取该任务下的所有用例评审详情
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        
        # 构建响应数据
        task_dict = review_task.to_dict()
        task_dict['case_reviews'] = [case_review.to_dict() for case_review in case_reviews]
        task_dict['suite'] = review_task.suite.to_dict()
        
        # 计算评审进度
        total_cases = len(case_reviews)
        reviewed_cases = sum(1 for cr in case_reviews if cr.review_status != 'pending')
        task_dict['review_progress'] = {
            'total': total_cases,
            'reviewed': reviewed_cases,
            'pending': total_cases - reviewed_cases,
            'progress_percent': round(reviewed_cases / total_cases * 100, 2) if total_cases > 0 else 0
        }
        
        return success_response(task_dict)
    except Exception as e:
        return error_response(500, f'获取评审任务失败: {str(e)}')


@bp.route('/<int:task_id>/case-reviews/<int:case_id>', methods=['PUT'])
@login_required
def update_case_review(task_id, case_id):
    """更新单条用例评审意见"""
    try:
        # 获取评审详情
        case_review = TestCaseReviewDetail.query.filter_by(
            review_task_id=task_id,
            case_id=case_id
        ).first_or_404()
        

        
        # 获取请求数据
        data = request.get_json()
        review_status = data.get('review_status')
        comments = data.get('comments', '')
        
        # 更新评审详情
        # 只有当review_status有效时才更新，否则保持原有状态
        if review_status and review_status in ['pending', 'approved', 'rejected']:
            case_review.review_status = review_status
        case_review.comments = comments
        case_review.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 如果评审任务状态是待评审，则更新为评审中并设置开始时间
        if case_review.review_task.status == 'pending':
            case_review.review_task.status = 'in_review'
            case_review.review_task.start_time = datetime.now(LOCAL_TIMEZONE)
        
        # 更新评审任务的更新时间
        case_review.review_task.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        db.session.commit()
        
        return success_response(case_review.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新用例评审失败: {str(e)}')


@bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_review(task_id):
    """完成用例集评审"""
    try:
        # 获取评审任务
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        

        
        # 获取该任务下的所有用例评审详情
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        
        # 检查是否所有用例都已评审
        # 如果没有用例，允许完成评审
        if case_reviews:
            pending_cases = [cr for cr in case_reviews if cr.review_status == 'pending']
            if pending_cases:
                return error_response(400, f'还有{len(pending_cases)}条用例未评审，请完成所有用例评审后再提交')
        
        # 获取请求数据
        data = request.get_json()
        overall_comments = data.get('overall_comments', '')
        
        # 计算用例集评审结果
        has_rejected = any(cr.review_status == 'rejected' for cr in case_reviews)
        suite_review_status = 'rejected' if has_rejected else 'approved'
        
        # 更新评审任务
        review_task.status = 'completed'
        review_task.end_time = datetime.now(LOCAL_TIMEZONE)
        review_task.overall_comments = overall_comments
        review_task.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 不需要更新用例集状态，评审状态由评审任务管理
        
        # 更新每条用例的最终评审结果
        for case_review in case_reviews:
            case = case_review.test_case
            case.reviewer_id = case_review.reviewer_id
            case.review_comments = case_review.comments
            case.last_reviewed_at = datetime.now(LOCAL_TIMEZONE)
        
        db.session.commit()
        
        return success_response({
            'message': '评审已完成',
            'review_task': review_task.to_dict(),
            'suite_review_status': suite_review_status
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'完成评审失败: {str(e)}')


@bp.route('/<int:task_id>/case-reviews', methods=['GET'])
@login_required
def get_case_reviews(task_id):
    """获取评审任务下的所有用例评审详情"""
    try:
        # 获取评审任务
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        # 验证权限
        if current_user.id != review_task.reviewer_id and current_user.id != review_task.initiator_id:
            return error_response(403, '没有权限查看该评审任务')
        
        # 获取该任务下的所有用例评审详情
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        
        # 构建响应数据
        case_reviews_list = []
        for case_review in case_reviews:
            cr_dict = case_review.to_dict()
            cr_dict['test_case'] = case_review.test_case.to_dict()
            case_reviews_list.append(cr_dict)
        
        return success_response({
            'total': len(case_reviews_list),
            'case_reviews': case_reviews_list
        })
    except Exception as e:
        return error_response(500, f'获取用例评审详情失败: {str(e)}')


@bp.route('/review-center/my-tasks', methods=['GET'])
@login_required
def get_my_review_tasks():
    """获取当前用户的评审任务"""
    try:
        # 解析分页参数
        page, per_page = get_pagination_params()
        
        # 查询当前用户作为评审人的任务
        query = TestSuiteReviewTask.query.filter_by(reviewer_id=current_user.id)
        
        # 处理筛选条件
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        
        # 执行分页查询
        pagination = query.order_by(TestSuiteReviewTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构造响应数据
        items = []
        for task in pagination.items:
            task_dict = task.to_dict()
            task_dict['suite_name'] = task.suite.suite_name
            task_dict['initiator_name'] = task.initiator.real_name
            # 添加项目、迭代和需求信息
            task_dict['project_name'] = task.suite.project.project_name if task.suite.project else None
            task_dict['iteration_name'] = task.suite.iteration.iteration_name if task.suite.iteration else None
            task_dict['requirement_name'] = task.suite.version_requirement.requirement_name if task.suite.version_requirement else None
            
            # 计算评审进度
            case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task.id).all()
            total_cases = len(case_reviews)
            reviewed_cases = sum(1 for cr in case_reviews if cr.review_status != 'pending')
            task_dict['review_progress'] = {
                'total': total_cases,
                'reviewed': reviewed_cases,
                'pending': total_cases - reviewed_cases,
                'progress_percent': round(reviewed_cases / total_cases * 100, 2) if total_cases > 0 else 0
            }
            
            items.append(task_dict)
        
        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(500, f'获取我的评审任务失败: {str(e)}')


@bp.route('/review-center/my-initiated', methods=['GET'])
@login_required
def get_my_initiated_reviews():
    """获取当前用户发起的评审"""
    try:
        # 解析分页参数
        page, per_page = get_pagination_params()
        
        # 查询当前用户作为发起人的任务
        query = TestSuiteReviewTask.query.filter_by(initiator_id=current_user.id)
        
        # 处理筛选条件
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        
        # 执行分页查询
        pagination = query.order_by(TestSuiteReviewTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构造响应数据
        items = []
        for task in pagination.items:
            task_dict = task.to_dict()
            task_dict['suite_name'] = task.suite.suite_name
            task_dict['reviewer_name'] = task.reviewer.real_name
            # 添加项目、迭代和需求信息
            task_dict['project_name'] = task.suite.project.project_name if task.suite.project else None
            task_dict['iteration_name'] = task.suite.iteration.iteration_name if task.suite.iteration else None
            task_dict['requirement_name'] = task.suite.version_requirement.requirement_name if task.suite.version_requirement else None
            
            # 计算评审进度
            case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task.id).all()
            total_cases = len(case_reviews)
            reviewed_cases = sum(1 for cr in case_reviews if cr.review_status != 'pending')
            task_dict['review_progress'] = {
                'total': total_cases,
                'reviewed': reviewed_cases,
                'pending': total_cases - reviewed_cases,
                'progress_percent': round(reviewed_cases / total_cases * 100, 2) if total_cases > 0 else 0
            }
            
            items.append(task_dict)
        
        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(500, f'获取我发起的评审失败: {str(e)}')


@bp.route('/<int:task_id>/reinitiate-review', methods=['POST'])
@login_required
def reinitiate_review(task_id):
    """重新发起评审"""
    try:
        # 获取评审任务
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        # 验证权限：只有评审人或发起人可以重新发起评审
        if current_user.id != review_task.reviewer_id and current_user.id != review_task.initiator_id:
            return error_response(403, '没有权限重新发起评审')
        
        # 重新发起评审，初始状态为待评审
        review_task.status = 'pending'
        review_task.end_time = None
        review_task.overall_comments = None
        review_task.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 不需要更新用例集状态，评审状态由评审任务管理
        
        db.session.commit()
        
        return success_response({
            'message': '重新发起评审成功',
            'review_task': review_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'重新发起评审失败: {str(e)}')


@bp.route('/test-suites/<int:suite_id>/review-status', methods=['GET'])
@login_required
def get_suite_review_status(suite_id):
    """获取用例集的评审状态和历史"""
    try:
        # 获取用例集
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 获取该用例集的所有评审任务
        review_tasks = TestSuiteReviewTask.query.filter_by(suite_id=suite_id).order_by(TestSuiteReviewTask.created_at.desc()).all()
        
        # 构建响应数据
        review_history = []
        for task in review_tasks:
            task_dict = task.to_dict()
            task_dict['initiator_name'] = task.initiator.real_name
            task_dict['reviewer_name'] = task.reviewer.real_name
            
            # 获取该任务下的用例评审结果统计
            case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task.id).all()
            approved_count = sum(1 for cr in case_reviews if cr.review_status == 'approved')
            rejected_count = sum(1 for cr in case_reviews if cr.review_status == 'rejected')
            
            task_dict['case_stats'] = {
                'total': len(case_reviews),
                'approved': approved_count,
                'rejected': rejected_count
            }
            
            review_history.append(task_dict)
        
        # 获取最新的评审任务
        latest_task = review_tasks[0] if review_tasks else None
        
        # 构建响应数据，从最新评审任务中获取当前状态和评审人
        response_data = {
            'review_history': review_history
        }
        
        if latest_task:
            # 根据最新评审任务状态确定用例集当前状态
            current_status = None
            if latest_task.status == 'completed':
                # 评审完成，检查是否有拒绝的用例
                case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=latest_task.id).all()
                has_rejected = any(cr.review_status == 'rejected' for cr in case_reviews)
                current_status = 'rejected' if has_rejected else 'approved'
            elif latest_task.status == 'in_review':
                current_status = 'pending'
            elif latest_task.status == 'pending':
                current_status = 'pending'
            
            response_data.update({
                'current_status': current_status,
                'current_reviewer_id': latest_task.reviewer_id,
                'current_reviewer_name': latest_task.reviewer.real_name if latest_task.reviewer else None
            })
        else:
            # 如果没有评审任务，返回默认状态
            response_data.update({
                'current_status': 'not_submitted',
                'current_reviewer_id': None,
                'current_reviewer_name': None
            })
        
        return success_response(response_data)
    except Exception as e:
        return error_response(500, f'获取用例集评审状态失败: {str(e)}')
