
import bpy


bl_info = {
    "name": "Model Validator",
    "description": "",
    "author": "Game Dev (Vamps)",
    "version": (0, 4, 0),
    "blender": (2, 83, 0),
    "location": "View3D => Header => Overlays",
    "wiki_url": "",
    "category": "Object"}


modules = (
    "preferences",
    "properties",
    "ui"
)

for mod in modules:
    exec(f"from . import {mod}")


def cleanse_modules():
    """search for persistent modules of the plugin in blender python sys.modules and remove them"""

    import sys

    all_modules = sys.modules
    all_modules = dict(
        sorted(all_modules.items(), key=lambda x: x[0]))  # sort them

    for k in all_modules.keys():
        if k.startswith(__name__):
            del sys.modules[k]

    return None


def register():

    for mod in modules:
        exec(f"{mod}.register()")

    bpy.types.Object.mesh_check_statistics = bpy.props.BoolProperty(
            name="Toggle Visibility",
            default=False)


def unregister():
    del bpy.types.Object.mesh_check_statistics

    for mod in reversed(modules):
        exec(f"{mod}.unregister()")

    cleanse_modules()
