from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.models import db, Project, ProjectMember, Iteration, TestPlan, TestCase, plan_case_relation
from datetime import datetime
import json

bp = Blueprint('test_plans', __name__)

@bp.route('/api/projects/<int:project_id>/test-plans', methods=['POST'])
@login_required
def create_test_plan(project_id):
    """创建测试计划"""
    try:
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager', 'tester']:
            return jsonify({'error': '无权在该项目中创建测试计划'}), 403
        
        # 获取项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 验证必要字段
        data = request.get_json()
        required_fields = ['plan_name', 'scope', 'environment']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 如果指定了迭代，验证迭代是否属于该项目
        iteration_id = data.get('iteration_id')
        if iteration_id:
            iteration = Iteration.query.get(iteration_id)
            if not iteration:
                return jsonify({'error': '指定的迭代不存在'}), 404
            if iteration.project_id != project_id:
                return jsonify({'error': '指定的迭代不属于该项目'}), 400
        
        # 创建测试计划
        new_test_plan = TestPlan(
            project_id=project_id,
            iteration_id=iteration_id,
            plan_name=data['plan_name'],
            scope=data['scope'],
            environment=data['environment'],
            risk=data.get('risk', ''),
            status=data.get('status', 'draft'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_test_plan)
        db.session.flush()  # 获取测试计划ID
        
        # 添加关联的测试用例
        if 'test_case_ids' in data:
            for case_id in data['test_case_ids']:
                # 检查测试用例是否存在
                test_case = TestCase.query.get(case_id)
                if test_case:
                    # 插入关联表
                    stmt = plan_case_relation.insert().values(
                        plan_id=new_test_plan.id,
                        case_id=case_id
                    )
                    db.session.execute(stmt)
        
        db.session.commit()
        
        return jsonify({'message': '测试计划创建成功', 'test_plan': new_test_plan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建测试计划失败: {str(e)}'}), 500

@bp.route('/api/projects/<int:project_id>/test-plans', methods=['GET'])
@login_required
def get_test_plans(project_id):
    """获取项目的测试计划列表"""
    try:
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member:
            return jsonify({'error': '无权访问该项目'}), 403
        
        # 获取测试计划列表
        test_plans = TestPlan.query.filter_by(project_id=project_id).order_by(TestPlan.created_at.desc()).all()
        
        # 转换为字典列表
        test_plan_list = [test_plan.to_dict() for test_plan in test_plans]
        
        return jsonify({'test_plans': test_plan_list}), 200
    except Exception as e:
        return jsonify({'error': f'获取测试计划列表失败: {str(e)}'}), 500

@bp.route('/api/test-plans/<int:plan_id>', methods=['GET'])
@login_required
def get_test_plan(plan_id):
    """获取测试计划详情"""
    try:
        # 获取测试计划
        test_plan = TestPlan.query.get(plan_id)
        if not test_plan:
            return jsonify({'error': '测试计划不存在'}), 404
        
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=test_plan.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member:
            return jsonify({'error': '无权访问该测试计划'}), 403
        
        # 获取测试计划详情，包括关联的测试用例
        plan_data = test_plan.to_dict()
        
        # 获取关联的测试用例
        case_ids = db.session.query(plan_case_relation.c.case_id).filter(
            plan_case_relation.c.plan_id == plan_id
        ).all()
        case_ids = [case_id[0] for case_id in case_ids]
        
        if case_ids:
            test_cases = TestCase.query.filter(TestCase.id.in_(case_ids)).all()
            plan_data['test_cases'] = [test_case.to_dict() for test_case in test_cases]
        else:
            plan_data['test_cases'] = []
        
        return jsonify({'test_plan': plan_data}), 200
    except Exception as e:
        return jsonify({'error': f'获取测试计划详情失败: {str(e)}'}), 500

@bp.route('/api/test-plans/<int:plan_id>', methods=['PUT'])
@login_required
def update_test_plan(plan_id):
    """更新测试计划信息"""
    try:
        # 获取测试计划
        test_plan = TestPlan.query.get(plan_id)
        if not test_plan:
            return jsonify({'error': '测试计划不存在'}), 404
        
        # 检查用户是否有权限更新该测试计划
        project_member = ProjectMember.query.filter_by(
            project_id=test_plan.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager', 'tester']:
            return jsonify({'error': '无权更新该测试计划'}), 403
        
        # 更新测试计划信息
        data = request.get_json()
        if 'plan_name' in data:
            test_plan.plan_name = data['plan_name']
        if 'scope' in data:
            test_plan.scope = data['scope']
        if 'environment' in data:
            test_plan.environment = data['environment']
        if 'risk' in data:
            test_plan.risk = data['risk']
        if 'status' in data:
            test_plan.status = data['status']
        if 'iteration_id' in data:
            # 验证迭代是否属于该项目
            if data['iteration_id']:
                iteration = Iteration.query.get(data['iteration_id'])
                if not iteration:
                    return jsonify({'error': '指定的迭代不存在'}), 404
                if iteration.project_id != test_plan.project_id:
                    return jsonify({'error': '指定的迭代不属于该项目'}), 400
            test_plan.iteration_id = data['iteration_id']
        
        test_plan.updated_by = current_user.id
        test_plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': '测试计划更新成功', 'test_plan': test_plan.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新测试计划失败: {str(e)}'}), 500

@bp.route('/api/test-plans/<int:plan_id>/test-cases', methods=['POST'])
@login_required
def add_test_cases_to_plan(plan_id):
    """向测试计划添加测试用例"""
    try:
        # 获取测试计划
        test_plan = TestPlan.query.get(plan_id)
        if not test_plan:
            return jsonify({'error': '测试计划不存在'}), 404
        
        # 检查用户是否有权限更新该测试计划
        project_member = ProjectMember.query.filter_by(
            project_id=test_plan.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager', 'tester']:
            return jsonify({'error': '无权更新该测试计划'}), 403
        
        # 添加测试用例
        data = request.get_json()
        if 'test_case_ids' not in data:
            return jsonify({'error': '缺少必要字段: test_case_ids'}), 400
        
        added_count = 0
        for case_id in data['test_case_ids']:
            # 检查测试用例是否存在
            test_case = TestCase.query.get(case_id)
            if test_case:
                # 检查是否已经关联
                existing = db.session.query(plan_case_relation).filter(
                    plan_case_relation.c.plan_id == plan_id,
                    plan_case_relation.c.case_id == case_id
                ).first()
                
                if not existing:
                    # 插入关联表
                    stmt = plan_case_relation.insert().values(
                        plan_id=plan_id,
                        case_id=case_id
                    )
                    db.session.execute(stmt)
                    added_count += 1
        
        test_plan.updated_by = current_user.id
        test_plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': f'成功添加{added_count}个测试用例'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'添加测试用例失败: {str(e)}'}), 500

@bp.route('/api/test-plans/<int:plan_id>/test-cases/<int:case_id>', methods=['DELETE'])
@login_required
def remove_test_case_from_plan(plan_id, case_id):
    """从测试计划移除测试用例"""
    try:
        # 获取测试计划
        test_plan = TestPlan.query.get(plan_id)
        if not test_plan:
            return jsonify({'error': '测试计划不存在'}), 404
        
        # 检查用户是否有权限更新该测试计划
        project_member = ProjectMember.query.filter_by(
            project_id=test_plan.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager', 'tester']:
            return jsonify({'error': '无权更新该测试计划'}), 403
        
        # 移除测试用例
        stmt = plan_case_relation.delete().where(
            plan_case_relation.c.plan_id == plan_id,
            plan_case_relation.c.case_id == case_id
        )
        result = db.session.execute(stmt)
        
        if result.rowcount == 0:
            return jsonify({'error': '测试用例未关联到该测试计划'}), 404
        
        test_plan.updated_by = current_user.id
        test_plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': '测试用例移除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'移除测试用例失败: {str(e)}'}), 500

@bp.route('/api/test-plans/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_test_plan(plan_id):
    """删除测试计划"""
    try:
        # 获取测试计划
        test_plan = TestPlan.query.get(plan_id)
        if not test_plan:
            return jsonify({'error': '测试计划不存在'}), 404
        
        # 检查用户是否有权限删除该测试计划
        project_member = ProjectMember.query.filter_by(
            project_id=test_plan.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权删除该测试计划'}), 403
        
        # 检查测试计划是否有相关的测试任务
        if test_plan.test_tasks:
            return jsonify({'error': '该测试计划下存在测试任务，无法删除'}), 400
        
        # 先删除关联的测试用例
        stmt = plan_case_relation.delete().where(
            plan_case_relation.c.plan_id == plan_id
        )
        db.session.execute(stmt)
        
        # 删除测试计划
        db.session.delete(test_plan)
        db.session.commit()
        
        return jsonify({'message': '测试计划删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除测试计划失败: {str(e)}'}), 500