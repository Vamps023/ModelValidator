import bpy

from bpy.types import AddonPreferences
from bpy.props import (
    FloatVectorProperty,
    FloatProperty)


class ModelValidatorPreferences(AddonPreferences):
    bl_idname = __name__.split(".")[0]

    line_width: FloatProperty(
            name="Edges Width",
            default=3.0,
            min=1.0, max=10.0,
            subtype="PIXEL",
            description="Edges width in pixels"
            )

    point_size: FloatProperty(
            name="Vertex Size",
            default=10.0,
            min=1.0, max=20.0,
            subtype="PIXEL",
            description="Vertex size in pixels"
            )

    points_offset: FloatProperty(
            name="Points Offset",
            default=0.15,
            min=0.1, max=5.0,
            precision=3,
            description="Offset of the colored points"
            )

    edges_offset: FloatProperty(
            name="Edges Offset",
            default=0.1,
            min=0.1, max=5.0,
            precision=3,
            description="Offset of the colored edges and faces"
            )

    non_manifold_color: FloatVectorProperty(
            name="Non manifold",
            default=(0.5, 1.0, 0.5, 1.0),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for non manifold edges"
            )

    triangles_color: FloatVectorProperty(
            name="Triangles",
            default=(0.7, 0.7, 0.05, 0.4),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for triangles"
            )

    ngons_color: FloatVectorProperty(
            name="Ngons",
            default=(0.7, 0.07, 0.06, 0.4),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for ngons"
            )

    e_poles_color: FloatVectorProperty(
            name="E poles",
            default=(0.5, 0.625, 1.0, 1.0),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for E poles"
            )

    n_poles_color: FloatVectorProperty(
            name="N poles",
            default=(0.5, 1.0, 0.5, 1.0),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for N poles"
            )

    more_poles_color: FloatVectorProperty(
            name="Poles > 5",
            default=(1.0, 0.145, 0.145, 1.0),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for poles with more than 5 edges"
            )

    isolated_verts_color: FloatVectorProperty(
            name="Isolated verts",
            default=(1.0, 00.5, 0.5, 1.0),
            min=0.0, max=1.0, size=4,
            subtype="COLOR",
            description="Custom color for isolated verts "
            )

    def draw(self, context):
        layout = self.layout
        # --- FACES BOX --- #
        box = layout.box()
        box.label(text="Faces settings", icon="FACESEL")
        box.prop(self, "line_width")
        box.prop(self, "edges_offset")
        box.separator()
        row = box.row(align=True)
        split_name = row.split(factor=0.3)
        col_names = split_name.column()
        split_props = split_name.split(factor=0.5)
        col_props = split_props.column()

        col_names.label(text="Triangles:")
        col_names.label(text="Ngons:")
        col_names.label(text="Non Manifold:")

        col_props.prop(self, "triangles_color", text="")
        col_props.prop(self, "ngons_color", text="")
        col_props.prop(self, "non_manifold_color", text="")

        # --- POINTS BOX --- #
        box = layout.box()
        box.label(text="Points settings", icon="VERTEXSEL")
        box.prop(self, "point_size")
        box.prop(self, "points_offset")
        box.separator()
        row = box.row(align=True)
        split_name = row.split(factor=0.3)
        col_names = split_name.column()
        split_props = split_name.split(factor=0.5)
        col_props = split_props.column()

        col_names.label(text="E Poles:")
        col_names.label(text="N Poles:")
        col_names.label(text="Poles more tha 5:")
        col_names.label(text="Isolated_verts:")

        col_props.prop(self, "e_poles_color", text="")
        col_props.prop(self, "n_poles_color", text="")
        col_props.prop(self, "more_poles_color", text="")
        col_props.prop(self, "isolated_verts_color", text="")


def register():
    bpy.utils.register_class(ModelValidatorPreferences)

def unregister():
    bpy.utils.unregister_class(ModelValidatorPreferences)
