from dao.module_dao import (
    create_module,
    get_module,
    list_modules_by_course,
    update_module,
    delete_module,
)
from utils.role_check import _ensure_instructor


from utils.logger import log_instructor_action

class ModuleService:
    """Encapsulates module CRUD operations."""

    def create_module(self, course_id, data):
        _ensure_instructor()
        filtered = {k: v for k, v in data.items() if k in ("title", "order")}
        module = create_module(course_id=course_id, **filtered)
        log_instructor_action(f"Created module (id={module.id}) for course (id={course_id}): {filtered}", "info")
        return module

    def get_module(self, module_id):
        module = get_module(module_id)
        if not module:
            raise ValueError("Module not found")
        return module

    def list_modules(self, course_id):
        return list_modules_by_course(course_id)

    def update_module(self, module_id, data):
        _ensure_instructor()
        module = update_module(module_id, **data)
        log_instructor_action(f"Updated module (id={module_id}): {data}", "info")
        return module

    def delete_module(self, module_id):
        _ensure_instructor()
        module = delete_module(module_id)
        log_instructor_action(f"Deleted module (id={module_id})", "info")
        return module


module_service = ModuleService()

def create_module_service(*args, **kwargs):
    return module_service.create_module(*args, **kwargs)

def get_module_service(*args, **kwargs):
    return module_service.get_module(*args, **kwargs)

def list_modules_service(*args, **kwargs):
    return module_service.list_modules(*args, **kwargs)

def update_module_service(*args, **kwargs):
    return module_service.update_module(*args, **kwargs)

def delete_module_service(*args, **kwargs):
    return module_service.delete_module(*args, **kwargs)
