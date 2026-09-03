# dao/material_dao.py
"""DAO for Material model (class‑based)."""

from config.db import db
from models.material import Material


class MaterialDAO:
    """Encapsulates CRUD operations for Material."""

    def create_material(self, module_id, file_path, file_type, uploaded_by):
        material = Material(
            module_id=module_id,
            file_path=file_path,
            file_type=file_type,
            uploaded_by=uploaded_by,
        )
        db.session.add(material)
        db.session.commit()
        return material

    def get_material(self, material_id):
        return Material.query.get(material_id)

    def list_materials_by_module(self, module_id):
        return Material.query.filter_by(module_id=module_id).all()

    def delete_material(self, material_id):
        material = self.get_material(material_id)
        if not material:
            raise ValueError("Material not found")
        db.session.delete(material)
        db.session.commit()
        return True


# Module‑level singleton
material_dao = MaterialDAO()

# Backward‑compatible wrappers
def create_material(*args, **kwargs):
    return material_dao.create_material(*args, **kwargs)

def get_material(*args, **kwargs):
    return material_dao.get_material(*args, **kwargs)

def list_materials_by_module(*args, **kwargs):
    return material_dao.list_materials_by_module(*args, **kwargs)

def delete_material(*args, **kwargs):
    return material_dao.delete_material(*args, **kwargs)
