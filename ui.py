import bpy

from .model_validator import ModelValidator as MC


def model_validator_panel(self, context):
    model_validator = context.window_manager.model_validator_props
    addon_prefs = context.preferences.addons[
        __name__.split(".")[0]].preferences
    layout = self.layout
    row = layout.row(align=True)
    row.active = context.object is not None
    check_icon = "PLAY" if model_validator.check_data else "SNAP_FACE"
    overlay_icon = "OUTLINER_OB_LIGHT" if model_validator.show_overlay else \
        "LIGHT"
    row.prop(model_validator, "check_data",
             text="Check Data",
             icon=check_icon)
    row.prop(model_validator, "show_overlay",
             text="Show Overlay",
             icon=overlay_icon)
    box = layout.box()
    model_validator.draw_options(box)

    box.prop(addon_prefs, 'edges_offset')
    box.prop(addon_prefs, 'points_offset')

    for obj, mc_object in MC.objects.items():
        ob_box = layout.box()
        row_name = ob_box.row()
        row_name.alignment = 'LEFT'
        icon = 'TRIA_DOWN' if obj.model_validator_statistics else \
            'TRIA_RIGHT'
        row_name.prop(obj, 'model_validator_statistics',
                      text=obj.name,
                      icon=icon,
                      emboss=False)
        if obj.model_validator_statistics:
            checker_options = (("non_manifold", "Non manifold"),
                               ("triangles", "Triangles"),
                               ("ngons", "Ngons"),
                               ("n_poles", "N poles"),
                               ("e_poles", "E poles"),
                               ("more_poles", "Poles > 5"),
                               ("isolated_verts", "Isolated verts")
                               )

            row = ob_box.row()
            row.label(text=f"Verts: {mc_object._verts} -- Faces: "
                           f"{mc_object._faces} -- Triangles: "
                           f"{mc_object._tris} ")

            row_stats = ob_box.row()
            split = row_stats.split(factor=0.02)
            split.separator()
            col_1 = split.column()
            col_2 = split.column()

            for i, checker in enumerate(checker_options):
                identifier, name = checker
                col = col_1 if i<=2 else col_2
                if getattr(model_validator, identifier):
                    if hasattr(mc_object, f'_{identifier}'):
                        count = getattr(mc_object, f'_{identifier}').count
                    else:
                        count = mc_object._poles.count(identifier)
                    col.label(
                            text=f"{name}: {count}")


def register():
    bpy.types.VIEW3D_PT_overlay.append(model_validator_panel)

def unregister():
    bpy.types.VIEW3D_PT_overlay.remove(model_validator_panel)
