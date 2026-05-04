"""用例评审路由：评审任务创建、审批流、历史记录。"""
from flask import Blueprint, request
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from app.models.models import db, TestSuite, TestSuiteReviewTask, TestCaseReviewDetail, TestCase, User, TestSuiteReviewHistory, TestCaseReviewHistory
from app.utils.helpers import success_response, error_response, get_pagination_params

LOCAL_TIMEZONE = timezone(timedelta(hours=8))

# 评审结果枚举值 -> 通知/展示用中文
REVIEW_STATUS_LABEL = {
    "approved": "已通过",
    "rejected": "已拒绝",
    "pending": "待审核",
    "completed": "已完成",
    "in_review": "评审中",
}

def _review_status_label(value):
    return REVIEW_STATUS_LABEL.get(value, value) if value else value

bp = Blueprint('review_tasks', __name__, url_prefix='/api/review-tasks')


@bp.route('/test-suites/<int:suite_id>/initiate-review', methods=['POST'])
@login_required
def initiate_review(suite_id):
    """发起用例集评审"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)

        if suite.type != 'suite':
            return error_response(400, '只有用例集才能发起评审')
        if suite.deleted_at is not None:
            return error_response(400, '该用例集已在回收站中，无法发起评审')
        if suite.creator_id != current_user.id:
            return error_response(403, '仅该用例集的创建人可以发起评审')

        data = request.get_json()
        reviewer_id = data.get('reviewer_id')
        
        if not reviewer_id:
            return error_response(400, '评审人不能为空')
        if reviewer_id == current_user.id:
            return error_response(400, '评审人不能为自己')
        
        reviewer = User.query.get(reviewer_id)
        if not reviewer:
            return error_response(400, '评审人不存在')
        
        cases = TestCase.query.filter_by(suite_id=suite_id).all()
        if not cases:
            return error_response(400, '用例集下没有测试用例，无法发起评审')
        
        review_task = TestSuiteReviewTask(
            suite_id=suite_id,
            initiator_id=current_user.id,
            reviewer_id=reviewer_id,
            status='pending'
            # start_time留空，在评审人开始评审时设置
        )
        db.session.add(review_task)
        db.session.flush()  # 获取review_task.id
        
        # 为每条用例创建评审详情记录（显式设置 created_at/updated_at 确保评审时间可显示）
        now = datetime.now(LOCAL_TIMEZONE)
        for case in cases:
            case_review = TestCaseReviewDetail(
                review_task_id=review_task.id,
                case_id=case.id,
                reviewer_id=reviewer_id,
                review_status='pending',
                created_at=now,
                updated_at=now
            )
            db.session.add(case_review)
        
        # 同步用例集列表的评审展示状态，便于列表筛选与展示
        suite.review_status = 'pending'
        db.session.commit()
        from app.services.notification_service import notify_users
        initiator_name = current_user.real_name or current_user.username
        notify_users(
            [reviewer_id], 'review_pending', '待评审',
            f'{initiator_name} 发起了用例集「{suite.suite_name}」的评审（共 {len(cases)} 条用例），请及时处理',
            'review_task', review_task.id, exclude_user_id=current_user.id
        )
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
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        if review_task.status != 'completed' and current_user.id != review_task.reviewer_id and current_user.id != review_task.initiator_id:
            return error_response(403, '没有权限查看该评审任务')
        
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        task_dict = review_task.to_dict()
        task_dict['case_reviews'] = [case_review.to_dict() for case_review in case_reviews]
        task_dict['suite'] = review_task.suite.to_dict()
        
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
        case_review = TestCaseReviewDetail.query.filter_by(
            review_task_id=task_id,
            case_id=case_id
        ).first_or_404()

        # 只有评审人本人且任务未完成时才能提交评审意见
        review_task = case_review.review_task
        if review_task.status in ('completed', 'rejected'):
            return error_response(400, '评审已完成或已拒绝，不能再修改评审意见')
        if current_user.id != review_task.reviewer_id:
            return error_response(403, '只有评审人才能提交评审意见')

        data = request.get_json()
        review_status = data.get('review_status')
        comments = data.get('comments', '')
        
        # 只有当review_status有效时才更新，否则保持原有状态
        if review_status and review_status in ['pending', 'approved', 'rejected']:
            case_review.review_status = review_status
        case_review.comments = comments
        case_review.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 如果评审任务状态是待评审，则更新为评审中并设置开始时间，并同步用例集展示状态
        if case_review.review_task.status == 'pending':
            case_review.review_task.status = 'in_review'
            case_review.review_task.start_time = datetime.now(LOCAL_TIMEZONE)
            suite = TestSuite.query.get(case_review.review_task.suite_id)
            if suite:
                suite.review_status = 'in_review'
        
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
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        
        # 如果没有用例，允许完成评审
        if case_reviews:
            pending_cases = [cr for cr in case_reviews if cr.review_status == 'pending']
            if pending_cases:
                return error_response(400, f'还有{len(pending_cases)}条用例未评审，请完成所有用例评审后再提交')
        
        data = request.get_json()
        overall_comments = data.get('overall_comments', '')
        
        has_rejected = any(cr.review_status == 'rejected' for cr in case_reviews)
        suite_review_status = 'rejected' if has_rejected else 'approved'
        
        max_version = db.session.query(db.func.max(TestSuiteReviewHistory.version))\
            .filter_by(review_task_id=task_id)\
            .scalar() or 0
        
        # 创建评审历史记录（显式设置 created_at/end_time 确保评审时间正确写入）
        now = datetime.now(LOCAL_TIMEZONE)
        review_history = TestSuiteReviewHistory(
            review_task_id=task_id,
            suite_id=review_task.suite_id,
            initiator_id=review_task.initiator_id,
            reviewer_id=review_task.reviewer_id,
            status=review_task.status,
            start_time=review_task.start_time,
            end_time=now,
            overall_comments=overall_comments,
            history_type='complete',
            created_at=now,
            created_by=current_user.id,
            version=max_version + 1
        )
        db.session.add(review_history)
        db.session.flush()  # 获取review_history.id
        
        for case_review in case_reviews:
            case = case_review.test_case
            
            case_review_history = TestCaseReviewHistory(
                review_history_id=review_history.id,
                review_task_id=task_id,
                case_id=case.id,
                reviewer_id=case_review.reviewer_id,
                review_status=case_review.review_status,
                comments=case_review.comments,
                # 用例属性快照
                case_number=case.case_number,
                case_name=case.case_name,
                priority=case.priority,
                test_data=case.test_data,
                preconditions=case.preconditions,
                steps=case.steps,
                expected_result=case.expected_result,
                actual_result=case.actual_result,
                created_by=current_user.id
            )
            db.session.add(case_review_history)
        
        review_task.status = 'rejected' if has_rejected else 'completed'
        review_task.end_time = now
        review_task.overall_comments = overall_comments
        review_task.updated_at = now
        
        # 同步用例集列表的评审展示状态（前端：completed=已通过，rejected=已拒绝）
        suite = TestSuite.query.get(review_task.suite_id)
        if suite:
            suite.review_status = 'completed' if suite_review_status == 'approved' else 'rejected'
        
        # 4. 更新每条用例的最终评审结果，并写入用例评审的评审时间
        for case_review in case_reviews:
            case = case_review.test_case
            case.reviewer_id = case_review.reviewer_id
            case.review_comments = case_review.comments
            case.last_reviewed_at = now
            case_review.updated_at = now  # 确保用例评审列表的“评审时间”有值
        db.session.commit()
        if review_task.initiator_id and review_task.initiator_id != current_user.id:
            from app.services.notification_service import notify_users
            reviewer_name = current_user.real_name or current_user.username
            suite_name = review_task.suite.suite_name if review_task.suite else '用例集'
            status_label = _review_status_label(suite_review_status)
            notify_users(
                [review_task.initiator_id], 'review_completed', '评审已完成',
                f'{reviewer_name} 已完成用例集「{suite_name}」的评审，结果：{status_label}',
                'review_task', task_id,
                extra={'suite_review_status': suite_review_status},
                exclude_user_id=current_user.id
            )
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
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        if review_task.status != 'completed' and current_user.id != review_task.reviewer_id and current_user.id != review_task.initiator_id:
            return error_response(403, '没有权限查看该评审任务')
        
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
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
        page, per_page = get_pagination_params()
        query = TestSuiteReviewTask.query.filter_by(reviewer_id=current_user.id)
        
        if request.args.get('task_id'):
            try:
                query = query.filter(TestSuiteReviewTask.id == int(request.args['task_id']))
            except (ValueError, TypeError):
                pass
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        if request.args.get('suite_name'):
            query = query.join(TestSuite).filter(TestSuite.suite_name.like(f'%{request.args["suite_name"].strip()}%'))
        if request.args.get('created_after'):
            try:
                t = datetime.strptime(request.args['created_after'], '%Y-%m-%d').replace(tzinfo=LOCAL_TIMEZONE)
                query = query.filter(TestSuiteReviewTask.created_at >= t)
            except ValueError:
                pass
        if request.args.get('created_before'):
            try:
                t = datetime.strptime(request.args['created_before'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=LOCAL_TIMEZONE)
                query = query.filter(TestSuiteReviewTask.created_at <= t)
            except ValueError:
                pass
        
        # locate_id：不做过滤，而是计算目标任务所在页并跳转到该页
        # 排序键为 (created_at DESC, id DESC)，count_before 同步考虑同时间戳但 id 更大（排更前）的记录
        if request.args.get('locate_id'):
            try:
                locate_id = int(request.args['locate_id'])
                target = query.filter(TestSuiteReviewTask.id == locate_id).first()
                if target:
                    count_before = query.filter(
                        db.or_(
                            TestSuiteReviewTask.created_at > target.created_at,
                            db.and_(
                                TestSuiteReviewTask.created_at == target.created_at,
                                TestSuiteReviewTask.id > target.id
                            )
                        )
                    ).count()
                    page = count_before // per_page + 1
            except (ValueError, TypeError):
                pass
        
        pagination = query.order_by(
            TestSuiteReviewTask.created_at.desc(),
            TestSuiteReviewTask.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for task in pagination.items:
            task_dict = task.to_dict()
            task_dict['suite_name'] = task.suite.suite_name
            task_dict['initiator_name'] = task.initiator.real_name if task.initiator else None
            task_dict['project_name'] = task.suite.project.project_name if task.suite.project else None
            task_dict['iteration_name'] = task.suite.iteration.iteration_name if task.suite.iteration else None
            task_dict['requirement_name'] = task.suite.version_requirement.requirement_name if task.suite.version_requirement else None
            
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
            'page': pagination.page,
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
        page, per_page = get_pagination_params()
        query = TestSuiteReviewTask.query.filter_by(initiator_id=current_user.id)
        
        if request.args.get('task_id'):
            try:
                query = query.filter(TestSuiteReviewTask.id == int(request.args['task_id']))
            except (ValueError, TypeError):
                pass
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        if request.args.get('suite_name'):
            query = query.join(TestSuite).filter(TestSuite.suite_name.like(f'%{request.args["suite_name"].strip()}%'))
        if request.args.get('created_after'):
            try:
                t = datetime.strptime(request.args['created_after'], '%Y-%m-%d').replace(tzinfo=LOCAL_TIMEZONE)
                query = query.filter(TestSuiteReviewTask.created_at >= t)
            except ValueError:
                pass
        if request.args.get('created_before'):
            try:
                t = datetime.strptime(request.args['created_before'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=LOCAL_TIMEZONE)
                query = query.filter(TestSuiteReviewTask.created_at <= t)
            except ValueError:
                pass
        
        # locate_id：不做过滤，而是计算目标任务所在页并跳转到该页
        # 排序键为 (created_at DESC, id DESC)，count_before 同步考虑同时间戳但 id 更大（排更前）的记录
        if request.args.get('locate_id'):
            try:
                locate_id = int(request.args['locate_id'])
                target = query.filter(TestSuiteReviewTask.id == locate_id).first()
                if target:
                    count_before = query.filter(
                        db.or_(
                            TestSuiteReviewTask.created_at > target.created_at,
                            db.and_(
                                TestSuiteReviewTask.created_at == target.created_at,
                                TestSuiteReviewTask.id > target.id
                            )
                        )
                    ).count()
                    page = count_before // per_page + 1
            except (ValueError, TypeError):
                pass
        
        pagination = query.order_by(
            TestSuiteReviewTask.created_at.desc(),
            TestSuiteReviewTask.id.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for task in pagination.items:
            task_dict = task.to_dict()
            task_dict['suite_name'] = task.suite.suite_name
            task_dict['reviewer_name'] = task.reviewer.real_name if task.reviewer else None
            task_dict['project_name'] = task.suite.project.project_name if task.suite.project else None
            task_dict['iteration_name'] = task.suite.iteration.iteration_name if task.suite.iteration else None
            task_dict['requirement_name'] = task.suite.version_requirement.requirement_name if task.suite.version_requirement else None
            
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
            'page': pagination.page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(500, f'获取我发起的评审失败: {str(e)}')


@bp.route('/<int:task_id>/restart-review', methods=['POST'])
@login_required
def restart_review(task_id):
    """重新评审：评审人修改已完成的评审"""
    try:
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        if current_user.id != review_task.reviewer_id:
            return error_response(403, '只有评审人可以重新评审')
        
        # 已完成或已拒绝的评审均可重新打开
        if review_task.status not in ('completed', 'rejected'):
            return error_response(400, '只有已完成或已拒绝的评审才能重新评审')
        
        review_task.status = 'in_review'
        review_task.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 同步用例集列表的评审展示状态
        suite = TestSuite.query.get(review_task.suite_id)
        if suite:
            suite.review_status = 'in_review'
        
        db.session.commit()
        
        if review_task.initiator_id and review_task.initiator_id != current_user.id:
            from app.services.notification_service import notify_users
            reviewer_name = current_user.real_name or current_user.username
            suite_name = review_task.suite.suite_name if review_task.suite else '用例集'
            notify_users(
                [review_task.initiator_id],
                'review_restarted',
                '重新评审',
                f'评审人 {reviewer_name} 已重新开始评审用例集「{suite_name}」',
                'review_task',
                task_id,
                exclude_user_id=current_user.id,
            )
        return success_response({
            'message': '重新评审成功',
            'review_task': review_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'重新评审失败: {str(e)}')


@bp.route('/<int:task_id>/reinitiate-review', methods=['POST'])
@login_required
def reinitiate_review(task_id):
    """重新发起评审：仅该用例集创建人可操作（与首次发起评审权限一致）"""
    try:
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)

        suite = TestSuite.query.get(review_task.suite_id)
        if not suite:
            return error_response(404, '用例集不存在')
        if suite.creator_id != current_user.id:
            return error_response(403, '仅该用例集的创建人可以重新发起评审')

        # 已完成或已拒绝的评审均可重新发起
        if review_task.status not in ('completed', 'rejected'):
            return error_response(400, '只有已完成或已拒绝的评审才能重新发起')
        
        review_task.status = 'pending'
        review_task.end_time = None
        review_task.updated_at = datetime.now(LOCAL_TIMEZONE)
        
        # 同步用例集列表的评审展示状态
        suite = TestSuite.query.get(review_task.suite_id)
        if suite:
            suite.review_status = 'pending'
        
        db.session.commit()
        
        if review_task.reviewer_id and review_task.reviewer_id != current_user.id:
            from app.services.notification_service import notify_users
            initiator_name = current_user.real_name or current_user.username
            suite_name = review_task.suite.suite_name if review_task.suite else '用例集'
            notify_users(
                [review_task.reviewer_id],
                'review_pending',
                '待评审',
                f'{initiator_name} 已重新发起用例集「{suite_name}」的评审，请及时处理',
                'review_task',
                task_id,
                exclude_user_id=current_user.id,
            )
        return success_response({
            'message': '重新发起评审成功',
            'review_task': review_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'重新发起评审失败: {str(e)}')


@bp.route('/<int:task_id>/reject-review', methods=['POST'])
@login_required
def reject_review(task_id):
    """打回评审"""
    try:
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        if current_user.id != review_task.reviewer_id:
            return error_response(403, '没有权限打回评审')
        
        if review_task.status not in ['in_review', 'completed']:
            return error_response(400, '只有评审中或已完成的评审才能被打回')
        
        data = request.get_json()
        overall_comments = data.get('overall_comments', review_task.overall_comments)
        
        max_version = db.session.query(db.func.max(TestSuiteReviewHistory.version))\
            .filter_by(review_task_id=task_id)\
            .scalar() or 0
        
        # 创建评审历史记录（显式设置 created_at/end_time 确保评审时间正确写入）
        now = datetime.now(LOCAL_TIMEZONE)
        review_history = TestSuiteReviewHistory(
            review_task_id=task_id,
            suite_id=review_task.suite_id,
            initiator_id=review_task.initiator_id,
            reviewer_id=review_task.reviewer_id,
            status=review_task.status,
            start_time=review_task.start_time,
            end_time=now,
            overall_comments=overall_comments,
            history_type='reject',
            created_at=now,
            created_by=current_user.id,
            version=max_version + 1
        )
        db.session.add(review_history)
        db.session.flush()  # 获取review_history.id
        
        case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=task_id).all()
        
        for case_review in case_reviews:
            case = case_review.test_case
            case_review_history = TestCaseReviewHistory(
                review_history_id=review_history.id,
                review_task_id=task_id,
                case_id=case.id,
                reviewer_id=case_review.reviewer_id,
                review_status=case_review.review_status,
                comments=case_review.comments,
                # 用例属性快照
                case_number=case.case_number,
                case_name=case.case_name,
                priority=case.priority,
                test_data=case.test_data,
                preconditions=case.preconditions,
                steps=case.steps,
                expected_result=case.expected_result,
                actual_result=case.actual_result,
                created_by=current_user.id
            )
            db.session.add(case_review_history)
        
        review_task.status = 'rejected'
        if not review_task.end_time:
            review_task.end_time = now
        review_task.overall_comments = overall_comments
        review_task.updated_at = now
        
        # 同步用例集列表的评审展示状态
        suite = TestSuite.query.get(review_task.suite_id)
        if suite:
            suite.review_status = 'rejected'
        
        db.session.commit()
        if review_task.initiator_id and review_task.initiator_id != current_user.id:
            from app.services.notification_service import notify_users
            reviewer_name = current_user.real_name or current_user.username
            suite_name = review_task.suite.suite_name if review_task.suite else '用例集'
            reject_reason = overall_comments or '无'
            notify_users(
                [review_task.initiator_id], 'review_rejected', '评审被打回',
                f'评审人 {reviewer_name} 打回了用例集「{suite_name}」的评审，原因：{reject_reason}',
                'review_task', task_id, exclude_user_id=current_user.id
            )
        return success_response({
            'message': '打回评审成功',
            'review_task': review_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'打回评审失败: {str(e)}')


@bp.route('/test-suites/<int:suite_id>/review-status', methods=['GET'])
@login_required
def get_suite_review_status(suite_id):
    """获取用例集的评审状态和历史"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        
        review_tasks = TestSuiteReviewTask.query.filter_by(suite_id=suite_id).all()
        task_ids = [task.id for task in review_tasks]
        
        all_review_histories = TestSuiteReviewHistory.query.filter(
            TestSuiteReviewHistory.review_task_id.in_(task_ids)
        ).order_by(
            TestSuiteReviewHistory.created_at.desc(),
            TestSuiteReviewHistory.version.desc()
        ).all()
        
        review_history = []
        for history in all_review_histories:
            history_dict = history.to_dict()
            
            history_dict['initiator_name'] = history.initiator.real_name if history.initiator else None
            history_dict['reviewer_name'] = history.reviewer.real_name if history.reviewer else None
            
            case_histories = TestCaseReviewHistory.query.filter_by(review_history_id=history.id).all()
            approved_count = sum(1 for ch in case_histories if ch.review_status == 'approved')
            rejected_count = sum(1 for ch in case_histories if ch.review_status == 'rejected')
            pending_count = sum(1 for ch in case_histories if ch.review_status == 'pending')
            
            history_dict['case_stats'] = {
                'total': len(case_histories),
                'approved': approved_count,
                'rejected': rejected_count,
                'pending': pending_count
            }
            
            if history.review_task:
                history_dict['task_id'] = history.review_task.id
                history_dict['task_status'] = history.review_task.status
            
            review_history.append(history_dict)
        
        # 获取最新的评审任务（created_at 可能为 None，避免 None 与 None 比较报错）
        latest_task = None
        if review_tasks:
            tasks_with_date = [t for t in review_tasks if t.created_at is not None]
            if tasks_with_date:
                latest_task = max(tasks_with_date, key=lambda x: x.created_at)
            else:
                latest_task = review_tasks[0]
        
        response_data = {
            'review_history': review_history
        }
        
        if latest_task:
            current_status = None
            if latest_task.status == 'completed':
                case_reviews = TestCaseReviewDetail.query.filter_by(review_task_id=latest_task.id).all()
                has_rejected = any(cr.review_status == 'rejected' for cr in case_reviews)
                current_status = 'rejected' if has_rejected else 'approved'
            elif latest_task.status == 'in_review':
                current_status = 'in_review'
            elif latest_task.status == 'pending':
                current_status = 'pending'
            elif latest_task.status == 'rejected':
                current_status = 'rejected'
            
            response_data.update({
                'current_status': current_status,
                'current_reviewer_id': latest_task.reviewer_id,
                'current_reviewer_name': latest_task.reviewer.real_name if latest_task.reviewer else None,
                'latest_task_id': latest_task.id,
            })
        else:
            response_data.update({
                'current_status': 'not_submitted',
                'current_reviewer_id': None,
                'current_reviewer_name': None,
                'latest_task_id': None,
            })
        
        return success_response(response_data)
    except Exception as e:
        return error_response(500, f'获取用例集评审状态失败: {str(e)}')


@bp.route('/<int:task_id>/review-history', methods=['GET'])
@login_required
def get_review_history_list(task_id):
    """获取评审任务的历史记录列表"""
    try:
        review_task = TestSuiteReviewTask.query.get_or_404(task_id)
        
        if current_user.id != review_task.reviewer_id and current_user.id != review_task.initiator_id:
            return error_response(403, '没有权限查看评审历史')
        
        review_history_list = TestSuiteReviewHistory.query.filter_by(review_task_id=task_id)\
            .order_by(TestSuiteReviewHistory.version.desc())\
            .all()
        
        history_list = [history.to_dict() for history in review_history_list]
        
        return success_response({
            'review_history': history_list
        })
    except Exception as e:
        return error_response(500, f'获取评审历史失败: {str(e)}')


@bp.route('/review-center/recent-history', methods=['GET'])
@login_required
def get_recent_review_history():
    """获取当前用户参与的全部最近评审历史（作为发起人或评审人），按时间倒序"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        query = TestSuiteReviewHistory.query.filter(
            (TestSuiteReviewHistory.initiator_id == current_user.id) |
            (TestSuiteReviewHistory.reviewer_id == current_user.id)
        ).order_by(TestSuiteReviewHistory.created_at.desc()).limit(limit)
        rows = query.all()
        result = []
        for h in rows:
            d = h.to_dict()
            case_histories = TestCaseReviewHistory.query.filter_by(review_history_id=h.id).all()
            d['case_stats'] = {
                'total': len(case_histories),
                'approved': sum(1 for c in case_histories if c.review_status == 'approved'),
                'rejected': sum(1 for c in case_histories if c.review_status == 'rejected'),
                'pending': sum(1 for c in case_histories if c.review_status == 'pending'),
            }
            if h.suite:
                d['suite_name'] = h.suite.suite_name
            else:
                d['suite_name'] = None
            if h.review_task:
                d['task_id'] = h.review_task.id
                d['task_status'] = h.review_task.status
            result.append(d)
        return success_response({'items': result})
    except Exception as e:
        return error_response(500, f'获取最近评审历史失败: {str(e)}')


@bp.route('/review-history/<int:history_id>', methods=['GET'])
@login_required
def get_review_history_detail(history_id):
    """获取评审历史详情"""
    try:
        review_history = TestSuiteReviewHistory.query.get_or_404(history_id)
        
        # 评审历史对所有登录用户公开，不做权限校验
        
        case_review_history_list = TestCaseReviewHistory.query.filter_by(review_history_id=history_id)\
            .order_by(TestCaseReviewHistory.case_number)\
            .all()
        
        history_dict = review_history.to_dict()
        
        if review_history.suite:
            history_dict['suite_name'] = review_history.suite.suite_name
            history_dict['suite'] = {
                'suite_name': review_history.suite.suite_name
            }
        
        history_dict['case_reviews'] = [case_history.to_dict() for case_history in case_review_history_list]
        
        return success_response(history_dict)
    except Exception as e:
        return error_response(500, f'获取评审历史详情失败: {str(e)}')
