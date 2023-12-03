import bpy
import bmesh
import gpu

from gpu_extras.batch import batch_for_shader

from .core import *


class ModelValidatorObject:

    MESH_DATAS = ('verts', 'edges', 'faces')
    GEO_CHECKER = ('non_manifold', 'triangles', 'ngons')
    VERTS_CHECKER = ('n_poles', 'e_poles', 'more_poles', 'isolated_verts')

    def __init__(self, obj):

        self._object = obj
        self._bm_object = None

        self._verts = 0
        self._edges = 0
        self._faces = 0
        self._tris = 0

        self._triangles = Triangles(self)
        self._ngons = Ngons(self)
        self._non_manifold = NonManifold(self)

        self._poles = Poles(self)

        self._init_object()

    def _init_object(self):
        bm = self.set_bm_object()
        self.update_datas(bm)

    def set_bm_object(self):
        me = self._object.data
        if me.is_editmode:
            self._bm_object = bmesh.from_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)
            self._bm_object = bm
        return self._bm_object

    def update_datas(self, bm):
        for data in self.MESH_DATAS:
            setattr(self, f"_{data}", len(getattr(bm, data)))
            self._tris = len(bm.calc_loop_triangles())

        model_validator = bpy.context.window_manager.model_validator_props
        for check in self.GEO_CHECKER:
            if getattr(model_validator, check):
                exec(f"self._{check}.set_datas()")

        if any(getattr(model_validator, check) for check in self.VERTS_CHECKER):
            self._poles.set_datas()

    @property
    def bm_object(self):
        if self._bm_object is None or not self._bm_object.is_valid:
            self.update_bm_object()
        return self._bm_object

    def update_bm_object(self):
        bm = self.set_bm_object()
        self.update_datas(bm)
        return bm

    def is_updated_datas(self, bm):
        return any([getattr(self, f"_{data}") != len(getattr(bm, data))
                    for data in self.MESH_DATAS])


class ModelValidatorGPU:

    _handler = None

    @classmethod
    def setup_handler(cls):
        cls._handler = bpy.types.SpaceView3D.draw_handler_add(
                cls.draw, (), 'WINDOW', 'POST_VIEW'
                )

    @classmethod
    def remove_handler(cls):
        bpy.types.SpaceView3D.draw_handler_remove(cls._handler, 'WINDOW')

    @staticmethod
    def draw_edges(coords, line_width, color):
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')  # Fixed shader type
        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        shader.bind()
        shader.uniform_float("color", color)
        gpu.state.blend_set("ALPHA")
        gpu.state.line_width_set(line_width)
        batch.draw(shader)

    @staticmethod
    def draw_faces(coords, indices, color):
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')  # Fixed shader type
        batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=indices)
        shader.bind()
        shader.uniform_float("color", color)
        gpu.state.blend_set("ALPHA")
        batch.draw(shader)

    @staticmethod
    def draw_points(coords, point_size, color):
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')  # Fixed shader type
        batch = batch_for_shader(shader, 'POINTS', {"pos": coords})
        shader.bind()
        shader.uniform_float("color", color)
        gpu.state.point_size_set(point_size)
        batch.draw(shader)

    @classmethod
    def draw(cls):
        context = bpy.context
        if context.object is not None:
            if not bpy.context.space_data.shading.show_xray:
                gpu.state.depth_test_set('LESS')

            model_validator = context.window_manager.model_validator_props
            addon_prefs = context.preferences.addons[
                __name__.split(".")[0]].preferences

            for check in model_validator.checker_options:
                if getattr(model_validator, check):
                    for mc_object in ModelValidator.objects.values():
                        if check in ('non_manifold', 'triangles', 'ngons'):
                            edges_offset = getattr(addon_prefs, 'edges_offset')
                            coords = getattr(mc_object,
                                             f"_{check}").get_edges(edges_offset)

                            ModelValidatorGPU.draw_edges(
                                    coords,
                                    addon_prefs.line_width,
                                    getattr(addon_prefs, f"{check}_color")
                                    )

                        if check in ('triangles', 'ngons'):
                            face_offset = getattr(addon_prefs, 'edges_offset')
                            coords, indices = getattr(mc_object,
                                             f"_{check}").get_faces(face_offset)
                            ModelValidatorGPU.draw_faces(
                                    coords,
                                    indices,
                                    getattr(addon_prefs, f"{check}_color")
                                    )

                        if check in ('n_poles', 'e_poles', 'more_poles',
                                     'isolated_verts'):
                            point_offset = getattr(addon_prefs,
                                                   'points_offset')
                            coords = mc_object._poles.get_poles(
                                    point_offset,
                                    check
                                    )

                            ModelValidatorGPU.draw_points(
                                    coords,
                                    addon_prefs.point_size,
                                    getattr(addon_prefs, f"{check}_color")
                                    )

            gpu.state.depth_test_set('NONE')


class ModelValidator:

    _mode = ""
    objects = {}

    @staticmethod
    def poll():
        model_validator = bpy.context.window_manager.model_validator_props
        props = ("non_manifold", "triangles", "ngons",
                 "n_poles", "e_poles", "more_poles", "isolated_verts")
        return model_validator.check_data and \
               any([getattr(model_validator, prop) for prop in props])

    @classmethod
    def reset_model_validator(cls):
        cls.set_mode("")
        for mc_object in cls.objects.values():
            del mc_object
        cls.objects.clear()

    @classmethod
    def mode(cls):
        return cls._mode

    @classmethod
    def set_mode(cls, states):
        cls._mode = states

    @classmethod
    def add_model_validator_object(cls):
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH" or cls.objects.get(obj):
                continue
            cls.objects[obj] = ModelValidatorObject(obj)

    @classmethod
    def remove_model_validator_object(cls, obj):
        mc_object = cls.objects.get(obj)
        if mc_object:
            del mc_object
            del cls.objects[obj]

    @classmethod
    def reset_mc_objects(cls):
        for mc_object in cls.objects.values():
            del mc_object
        cls.objects.clear()
        cls.add_model_validator_object()

    @classmethod
    def add_callback(cls):
        if cls.callback not in bpy.app.handlers.depsgraph_update_post:
            cls.add_model_validator_object()
            bpy.app.handlers.depsgraph_update_post.append(cls.callback)

    @classmethod
    def remove_callback(cls):
        if cls.callback in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(cls.callback)
            cls.reset_model_validator()

    @classmethod
    def update_mc_object_datas(cls, checker_type):
        """
        :param checker_type: string,
        :return:
        """
        if checker_type in {'e_poles', 'n_poles', 'more_poles',
                            'isolated_verts'}:
            for mc_object in cls.objects.values():
                mc_object._poles.set_datas()

        else:
            for mc_object in cls.objects.values():
                getattr(mc_object, f"_{checker_type}").set_datas()

    @staticmethod
    def callback(scene):
        """
        Before doing anything, we check that the mode haven't changed.
        If this is the case and we are in EDIT mode, we check the validity
        of registered ModelValidatorObject instances. For each instance,
        we update its bmesh representation.
        """
        if bpy.context.object is not None:
            object_mode = bpy.context.object.mode
            if object_mode != ModelValidator.mode():
                ModelValidator.set_mode(object_mode)
                ModelValidator.reset_mc_objects()

            if object_mode == "OBJECT":
                for obj in bpy.context.selected_objects:
                    if not ModelValidator.objects.get(obj):
                        ModelValidator.add_model_validator_object()

                mc_objects = list(ModelValidator.objects.keys())
                for obj in mc_objects:
                    if obj not in list(bpy.data.objects) or not obj.select_get():
                        ModelValidator.remove_model_validator_object(obj)

            if object_mode == "EDIT" and  ModelValidator.poll():
                depsgraph = bpy.context.evaluated_depsgraph_get()
                for obj, mc_object in ModelValidator.objects.items():
                    bm = mc_object.bm_object
                    for update in depsgraph.updates:
                        if update.id.original == obj and \
                                mc_object.is_updated_datas(bm):
                            mc_object.update_datas(bm)

        else:
            model_validator = bpy.context.window_manager.model_validator_props
            model_validator.check_data = False
