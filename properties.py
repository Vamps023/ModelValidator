import bpy

from bpy.types import PropertyGroup

from bpy.props import (
    BoolProperty,
    PointerProperty
    )

from .model_validator import ModelValidator, ModelValidatorGPU


def enable_depsgraph_handler(self, context):
    if self.check_data:
        if context.object is None:
            self.check_data = False
        else:
            ModelValidator.set_mode(context.object.mode)
            ModelValidator.add_callback()
    else:
        ModelValidator.remove_callback()

def update_overlay(self, context):
    if self.show_overlay:
        ModelValidatorGPU.setup_handler()
    else:
        ModelValidatorGPU.remove_handler()

def mc_object_datas_updater(attr):
    def updater(self, context):
        if getattr(self, attr):
            ModelValidator.update_mc_object_datas(
                    attr
                    )
        return None

    return updater


class ModelValidatorProperties(PropertyGroup):

    check_data: BoolProperty(
            name="Check Data",
            default=False,
            update=enable_depsgraph_handler
            )

    show_overlay: BoolProperty(
            name="Show Overlay",
            default=False,
            update=update_overlay
            )

    non_manifold: BoolProperty(
            name="Non manifold",
            default=False,
            description="Display non manifold edges",
            update=mc_object_datas_updater("non_manifold")
            )

    triangles: BoolProperty(
            name="Triangles",
            default=True,
            description="Display triangles",
            update=mc_object_datas_updater("triangles")
            )

    ngons: BoolProperty(
            name="Ngons",
            default=False,
            description="Display ngons",
            update=mc_object_datas_updater("ngons")
            )

    e_poles: BoolProperty(
            name="E poles",
            default=False,
            description="Display E poles",
            update=mc_object_datas_updater("e_poles")
            )

    n_poles: BoolProperty(
            name="N poles",
            default=False,
            description="Display N poles",
            update=mc_object_datas_updater("n_poles")
            )

    more_poles: BoolProperty(
            name="Poles > 5",
            default=False,
            description="Display poles with more than 5 edges",
            update=mc_object_datas_updater("more_poles")
            )

    isolated_verts: BoolProperty(
            name="Isolated verts",
            default=False,
            description="Display isolated verts",
            update=mc_object_datas_updater("isolated_verts")
            )

    checker_options = ("non_manifold", "triangles", "ngons",
                       "n_poles", "e_poles", "more_poles", "isolated_verts"
                       )

    def draw_options(self, layout):
        layout.label(text="Items to check:")
        row = layout.row(align=True)
        split = row.split(factor=0.02)
        split.separator()
        col_1 = split.column()
        col_2 = split.column()

        for i, checker in enumerate(self.checker_options):
            col = col_1 if i <= 2 else col_2
            row = col.row()
            row.alignment = 'LEFT'
            icon = 'CHECKBOX_HLT' if getattr(self,
                                             checker) else 'CHECKBOX_DEHLT'
            row.prop(self, checker, icon=icon, emboss=False)


def register():
    bpy.utils.register_class(ModelValidatorProperties)
    bpy.types.WindowManager.model_validator_props = PointerProperty(
            type=ModelValidatorProperties)

def unregister():
    del bpy.types.WindowManager.model_validator_props
    bpy.utils.unregister_class(ModelValidatorProperties)
