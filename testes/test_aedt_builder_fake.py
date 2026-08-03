from pathlib import Path

from enz_eigenchannel_mimo.aedt.builder import AedtGeometryBuilder
from enz_eigenchannel_mimo.geometry import VarianteModelo, build_geometry_plan, engineering_smoke_seed


class FakeEdge:
    def chamfer(self, **kwargs):
        return True


class FakeObject:
    def __init__(self, name):
        self.name = name
        self.edges = [FakeEdge() for _ in range(24)]


class FakeModeler:
    def __init__(self):
        self.model_units = None
        self.objects = {}
        self.non_model = set()

    @property
    def object_names(self):
        return list(self.objects)

    def _create(self, name):
        obj = FakeObject(name)
        self.objects[name] = obj
        return obj

    def create_box(self, origin, sizes, name, material):
        return self._create(name)

    def create_rectangle(self, plane, origin, sizes, name, material):
        return self._create(name)

    def create_cylinder(self, axis, position, radius, height, name, material):
        return self._create(name)

    def set_object_model_state(self, assignment, model=False):
        names = [assignment] if isinstance(assignment, str) else list(assignment)
        self.non_model.update(names)
        return True

    def subtract(self, target, tools, keep_originals=False):
        if not keep_originals:
            for tool in tools:
                self.objects.pop(tool, None)
        return True

    def unite(self, names):
        for tool in names[1:]:
            self.objects.pop(tool, None)
        return True

    def __getitem__(self, name):
        return self.objects[name]


class FakeVariableManager:
    def __init__(self):
        self.variables = {}

    def set_variable(self, name, expression, **kwargs):
        self.variables[name] = expression
        return True


class FakeNamed:
    def __init__(self, name):
        self.name = name


class FakeSweep(FakeNamed):
    def __init__(self, name):
        super().__init__(name)
        self.props = {}

    def update(self):
        return True


class FakeSetup(FakeNamed):
    def __init__(self, name):
        super().__init__(name)
        self.props = {}

    def update(self):
        return True

    def add_sweep(self, name):
        return FakeSweep(name)


class FakeMesh:
    def assign_length_mesh(self, **kwargs):
        return FakeNamed(kwargs["name"])


class FakeApp:
    def __init__(self):
        self.modeler = FakeModeler()
        self.variable_manager = FakeVariableManager()
        self.mesh = FakeMesh()
        self.design_name = "HFSS_ENZ_G0_M4"
        self.ports = []
        self.setup_names = []
        self.auto_open = False

    def wave_port(self, **kwargs):
        self.ports.append(kwargs["name"])
        return FakeNamed(kwargs["name"])

    def set_auto_open(self, enable, opening_type="Radiation"):
        self.auto_open = bool(enable)
        return True

    def create_setup(self, name, **kwargs):
        self.setup_names.append(name)
        return FakeSetup(name)

    def save_project(self, path=None):
        if path:
            Path(path).write_text("fake-aedt", encoding="utf-8")
        return True


def test_builder_m4_executa_cadeia_cad_sem_importar_pyaedt(tmp_path):
    plan = build_geometry_plan(engineering_smoke_seed(VarianteModelo.M4_FABRICAVEL))
    app = FakeApp()
    artifacts = AedtGeometryBuilder(app).build(
        plan,
        project_path=tmp_path / "m4.aedt",
        configure_analysis=True,
    )
    assert artifacts.port_names == ("P1_WR28",)
    assert artifacts.setup_names == ("Setup_Driven_25p87GHz",)
    assert app.auto_open
    assert "Cavity_Metal" in app.modeler.object_names
    assert "Photonic_Dopant" in app.modeler.object_names
    assert (tmp_path / "m4.aedt").exists()
