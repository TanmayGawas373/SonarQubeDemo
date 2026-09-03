# dao/module_dao.py
"""DAO for Module model (class‑based)."""

from config.db import db
from models.module import Module


class ModuleDAO:
    """Encapsulates CRUD operations for Module."""

    def create_module(self, course_id, title, order=0):
        module = Module(course_id=course_id, title=title, order=order)
        db.session.add(module)
        db.session.commit()
        return module

    def get_module(self, module_id):
        return Module.query.get(module_id)

    def list_modules_by_course(self, course_id):
        return Module.query.filter_by(course_id=course_id).all()

    def update_module(self, module_id, **kwargs):
        module = self.get_module(module_id)
        if not module:
            raise ValueError("Module not found")
        for k, v in kwargs.items():
            setattr(module, k, v)
        db.session.commit()
        return module

    def delete_module(self, module_id):
        module = self.get_module(module_id)
        if not module:
            raise ValueError("Module not found")
        db.session.delete(module)
        db.session.commit()
        return True


# Module‑level singleton
module_dao = ModuleDAO()

# Backward‑compatible wrappers
def create_module(*args, **kwargs):
    return module_dao.create_module(*args, **kwargs)

def get_module(*args, **kwargs):
    return module_dao.get_module(*args, **kwargs)

def list_modules_by_course(*args, **kwargs):
    return module_dao.list_modules_by_course(*args, **kwargs)

def update_module(*args, **kwargs):
    return module_dao.update_module(*args, **kwargs)

def delete_module(*args, **kwargs):
    return module_dao.delete_module(*args, **kwargs)
