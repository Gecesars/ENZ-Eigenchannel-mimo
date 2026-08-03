from pathlib import Path

from enz_eigenchannel_mimo.aedt.builder import (
    ConstrutorDeclarativoAedt,
    ResultadoConstrucao,
)
from enz_eigenchannel_mimo.aedt.exports import exportar_resultados
from enz_eigenchannel_mimo.aedt.runtime import AedtRuntimeSpec
from enz_eigenchannel_mimo.specifications import EspecificacaoGeometrica

ROOT = Path(__file__).resolve().parents[1]
SMOKE = (
    ROOT
    / "modelos"
    / "especificacoes"
    / "m0_cavidade_retangular_smoke.hipotese.v1.yaml"
)


def test_runtime_aedt_usa_14_cores_por_padrao():
    runtime = AedtRuntimeSpec()
    assert runtime.cores == 14
    assert runtime.tasks == 1
    assert runtime.gpus == 0


class ObjetoFalso:
    def __init__(self, nome: str):
        self.name = nome
        self.faces = [1, 2, 3, 4, 5, 6]


class ModeladorFalso:
    def create_box(self, origem, tamanho, *, name, material):
        self.ultima_caixa = (origem, tamanho, name, material)
        return ObjetoFalso(name)


class SetupFalso:
    def __init__(self):
        self.props = {}

    def update(self):
        return True


class AppEigenFalso:
    solution_type = "Eigenmode"

    def __init__(self):
        self.modeler = ModeladorFalso()
        self.variaveis = {}
        self.setup = SetupFalso()
        self.setup_names = []

    def __setitem__(self, chave, valor):
        self.variaveis[chave] = valor

    def assign_perfect_e(self, faces, *, name):
        self.pec = (faces, name)
        return True

    def create_setup(self, name, setup_type=None):
        self.setup_name = (name, setup_type)
        return self.setup

    def delete_setup(self, name):
        self.setup_names.remove(name)
        return True


def _diretorios_run(base: Path) -> None:
    for nome in ("metrics", "plots", "network", "farfield"):
        (base / nome).mkdir()


def test_builder_materializa_m0_com_nomes_deterministicos():
    spec = EspecificacaoGeometrica.carregar(SMOKE)
    app = AppEigenFalso()
    resultado = ConstrutorDeclarativoAedt(app).construir(spec, "M0")
    assert set(resultado.objetos) == {"Cavity_Air"}
    assert app.variaveis["cavidade_altura"] == "7.7143mm"
    assert app.modeler.ultima_caixa[2:] == ("Cavity_Air", "vacuum")
    assert app.pec[1] == "PEC_Cavity"
    assert app.setup.props["NumModes"] == 4


def test_builder_remove_setup_auto_antes_do_setup_declarado():
    spec = EspecificacaoGeometrica.carregar(SMOKE)
    app = AppEigenFalso()
    app.setup_names = ["Auto1"]
    ConstrutorDeclarativoAedt(app).construir(spec, "M0")
    assert app.setup_names == []


class PosEigenFalso:
    def available_report_quantities(self, *, quantities_category):
        if quantities_category == "Eigen Q":
            return ["Q(1)", "Q(2)"]
        if quantities_category == "Eigen Modes":
            return ["Mode(1)", "Mode(2)"]
        return []

    def get_solution_data(self, *, expressions, report_category):
        self.report_category = report_category
        valores = {"Q(1)": 0.0, "Q(2)": 0.0, "Mode(1)": 20.1e9, "Mode(2)": 24.2e9}
        valor = valores[expressions]
        return type(
            "DadosFalsos",
            (),
            {"get_expression_data": lambda self: (None, [valor])},
        )()


class AppExportEigenFalso:
    def __init__(self):
        self.post = PosEigenFalso()

    def export_convergence(self, setup, *, output_file):
        Path(output_file).write_text("Converged : Yes\n", encoding="utf-8")
        return output_file

    def export_mesh_stats(self, setup, *, output_file):
        Path(output_file).write_text(
            "Total number of mesh elements: 42\n", encoding="utf-8"
        )
        return output_file

    def export_profile(self, setup, *, output_file):
        return False

    def export_design_preview_to_jpg(self, caminho):
        return False


def test_export_eigenmode_usa_categorias_oficiais_e_unidades_si(tmp_path):
    _diretorios_run(tmp_path)
    app = AppExportEigenFalso()
    etapa = {
        "solucao": "Eigenmode",
        "setup": {"propriedades": {"NumModes": 2}},
    }
    construcao = ResultadoConstrucao({}, "Setup1", None, None)
    artefatos = exportar_resultados(app, etapa, construcao, tmp_path)
    assert tmp_path / "metrics" / "eigenmodes.csv" in artefatos
    assert app.post.report_category == "Eigenmode"
    linhas = (tmp_path / "metrics" / "eigenmodes.csv").read_text(encoding="utf-8")
    assert "frequency_hz" in linhas
    assert "20100000000.0" in linhas


class AppExportDrivenFalso(AppExportEigenFalso):
    def __init__(self):
        super().__init__()
        self.excitation_names = ["P1", "P2"]

    def export_touchstone(self, *, setup, output_file):
        Path(output_file).write_text("# Hz S RI R 50\n", encoding="ascii")
        self.touchstone = (setup, output_file)
        return output_file

    def export_antenna_metadata(self, **kwargs):
        pasta = Path(kwargs["output_dir"])
        pasta.mkdir(exist_ok=True)
        (pasta / "metadata.json").write_text("{}\n", encoding="utf-8")
        self.metadata = kwargs
        return True


def test_export_driven_usa_touchstone_s2p_e_padroes_embarcados_complexos(tmp_path):
    _diretorios_run(tmp_path)
    app = AppExportDrivenFalso()
    etapa = {
        "solucao": "DrivenModal",
        "setup": {"propriedades": {}},
        "frequencias_exportacao_hz": [25.87e9],
    }
    construcao = ResultadoConstrucao({}, "Setup1", "Sweep1", "Sphere1")
    artefatos = exportar_resultados(app, etapa, construcao, tmp_path)
    assert tmp_path / "network" / "sparameters.s2p" in artefatos
    assert app.metadata["export_element_pattern"] is True
    assert app.metadata["export_power"] is True
    assert app.metadata["variations"] == {}
