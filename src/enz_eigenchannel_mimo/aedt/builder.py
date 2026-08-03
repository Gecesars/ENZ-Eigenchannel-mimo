from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..specifications import ErroEspecificacao, EspecificacaoGeometrica


class ErroConstrucaoAedt(RuntimeError):
    """Falha explícita durante a materialização da geometria declarativa."""


@dataclass(slots=True)
class ResultadoConstrucao:
    objetos: dict[str, Any]
    setup_name: str
    sweep_name: str | None
    sphere_name: str | None
    article_fields_sweep_name: str | None = None


class ConstrutorDeclarativoAedt:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.objetos: dict[str, Any] = {}

    def construir(
        self, spec: EspecificacaoGeometrica, etapa_nome: str
    ) -> ResultadoConstrucao:
        spec.exigir_pronta(etapa_nome)
        etapa = spec.etapa(etapa_nome)
        esperado_app = (
            "Modal" if etapa["solucao"] == "DrivenModal" else etapa["solucao"]
        )
        if str(self.app.solution_type) != esperado_app:
            raise ErroConstrucaoAedt(
                f"solution_type ativo {self.app.solution_type!r} != {esperado_app!r}"
            )

        for nome, expressao in spec.variaveis_aedt(etapa_nome).items():
            self.app[nome] = expressao

        for declaracao in etapa["objetos"]:
            self._criar_objeto(declaracao)
        for operacao in etapa["operacoes"]:
            self._aplicar_operacao(operacao)
        for fronteira in etapa["fronteiras"]:
            self._aplicar_fronteira(fronteira)
        for porta in etapa["portas"]:
            self._criar_porta(porta)

        # O AEDT 2024 R2 pode inserir ``Auto1`` ao inicializar um design HFSS.
        # Ele não pertence à especificação e tornaria ambígua a proveniência
        # científica da solução. A remoção ocorre somente no projeto novo do
        # worker, antes da criação do setup declarativo.
        for nome_setup in list(getattr(self.app, "setup_names", [])):
            if nome_setup.startswith("Auto") and not self.app.delete_setup(
                nome_setup
            ):
                raise ErroConstrucaoAedt(
                    f"falha ao remover setup automático {nome_setup}"
                )

        setup_dados = etapa["setup"]
        setup = self.app.create_setup(
            setup_dados["nome"], setup_type=setup_dados.get("tipo")
        )
        if not setup:
            raise ErroConstrucaoAedt(f"falha ao criar setup {setup_dados['nome']}")
        for chave, valor in setup_dados["propriedades"].items():
            setup.props[chave] = valor
        if not setup.update():
            raise ErroConstrucaoAedt(f"falha ao atualizar setup {setup_dados['nome']}")

        sweep_name: str | None = None
        if "varredura" in etapa:
            if etapa["solucao"] != "DrivenModal":
                raise ErroConstrucaoAedt("varredura de frequencia requer DrivenModal")
            dados_sweep = etapa["varredura"]
            sweep = self.app.create_linear_count_sweep(
                setup=setup_dados["nome"],
                unit=dados_sweep["unidade"],
                start_frequency=dados_sweep["inicio"],
                stop_frequency=dados_sweep["fim"],
                num_of_freq_points=dados_sweep["pontos"],
                name=dados_sweep["nome"],
                save_fields=dados_sweep.get("salvar_campos", True),
                save_rad_fields=dados_sweep.get("salvar_campos_radiados", False),
                sweep_type=dados_sweep.get("tipo", "Interpolating"),
                interpolation_tol=dados_sweep.get("tolerancia_interpolacao", 0.5),
                interpolation_max_solutions=dados_sweep.get("maximo_solucoes", 250),
            )
            if not sweep:
                raise ErroConstrucaoAedt(
                    f"falha ao criar varredura {dados_sweep['nome']}"
                )
            sweep_name = dados_sweep["nome"]

        article_fields_sweep_name: str | None = None
        if "varredura_campos_artigo" in etapa:
            if etapa["solucao"] != "DrivenModal":
                raise ErroConstrucaoAedt(
                    "varredura discreta de campos requer DrivenModal"
                )
            dados_campos = etapa["varredura_campos_artigo"]
            frequencias = list(dados_campos["frequencias"])
            sweep_campos = self.app.create_single_point_sweep(
                setup=setup_dados["nome"],
                unit=dados_campos["unidade"],
                freq=frequencias,
                name=dados_campos["nome"],
                save_single_field=[True] * len(frequencias),
                save_fields=dados_campos["salvar_campos"],
                save_rad_fields=dados_campos["salvar_campos_radiados"],
            )
            if not sweep_campos:
                raise ErroConstrucaoAedt(
                    f"falha ao criar varredura {dados_campos['nome']}"
                )
            article_fields_sweep_name = dados_campos["nome"]

        sphere_name: str | None = None
        if "farfield" in etapa:
            farfield = etapa["farfield"]
            esfera = self.app.insert_infinite_sphere(
                phi_start=farfield["phi"]["inicio"],
                phi_stop=farfield["phi"]["fim"],
                phi_step=farfield["phi"]["passo"],
                theta_start=farfield["theta"]["inicio"],
                theta_stop=farfield["theta"]["fim"],
                theta_step=farfield["theta"]["passo"],
                name=farfield["nome"],
            )
            if not esfera:
                raise ErroConstrucaoAedt("falha ao criar esfera de campo distante")
            sphere_name = farfield["nome"]

        return ResultadoConstrucao(
            objetos=dict(self.objetos),
            setup_name=setup_dados["nome"],
            sweep_name=sweep_name,
            sphere_name=sphere_name,
            article_fields_sweep_name=article_fields_sweep_name,
        )

    def _criar_objeto(self, dados: Mapping[str, Any]) -> None:
        nome = dados["nome"]
        if nome in self.objetos:
            raise ErroConstrucaoAedt(f"objeto duplicado: {nome}")
        tipo = dados["tipo"]
        if tipo == "box":
            objeto = self.app.modeler.create_box(
                dados["origem"],
                dados["tamanho"],
                name=nome,
                material=dados.get("material"),
            )
        elif tipo == "cylinder":
            objeto = self.app.modeler.create_cylinder(
                dados["orientacao"],
                dados["origem"],
                dados["raio"],
                dados["altura"],
                num_sides=dados.get("lados", 0),
                name=nome,
                material=dados.get("material"),
            )
        elif tipo == "rectangle":
            objeto = self.app.modeler.create_rectangle(
                dados["orientacao"],
                dados["origem"],
                dados["tamanho"],
                name=nome,
                material=dados.get("material"),
            )
        elif tipo == "polyline_prism":
            objeto = self.app.modeler.create_polyline(
                dados["pontos"],
                cover_surface=True,
                close_surface=True,
                name=nome,
                material=dados.get("material"),
            )
            if objeto:
                objeto = objeto.sweep_along_vector(dados["vetor_extrusao"])
        elif tipo == "air_region":
            margens = dados["margens_percentuais"]
            objeto = self.app.modeler.create_air_region(
                x_pos=margens[0],
                y_pos=margens[1],
                z_pos=margens[2],
                x_neg=margens[3],
                y_neg=margens[4],
                z_neg=margens[5],
                is_percentage=True,
            )
            if objeto and objeto.name != nome:
                objeto.name = nome
        else:  # protegido também pelo JSON Schema
            raise ErroEspecificacao(f"tipo de objeto não suportado: {tipo}")
        if not objeto:
            raise ErroConstrucaoAedt(f"AEDT não criou {nome}")
        self.objetos[nome] = objeto

    def _objeto(self, nome: str) -> Any:
        try:
            return self.objetos[nome]
        except KeyError as exc:
            raise ErroConstrucaoAedt(f"objeto não materializado: {nome}") from exc

    def _aplicar_operacao(self, dados: Mapping[str, Any]) -> None:
        alvo = self._objeto(dados["alvo"])
        ferramentas = [self._objeto(nome) for nome in dados["ferramentas"]]
        manter = dados.get("manter_ferramentas", False)
        if dados["tipo"] == "subtract":
            sucesso = self.app.modeler.subtract(
                alvo, ferramentas, keep_originals=manter
            )
        elif dados["tipo"] == "unite":
            sucesso = self.app.modeler.unite(
                [alvo, *ferramentas], keep_originals=manter
            )
        else:
            raise ErroConstrucaoAedt(f"operação não suportada: {dados['tipo']}")
        if not sucesso:
            raise ErroConstrucaoAedt(f"falha em {dados['tipo']} sobre {dados['alvo']}")

    def _aplicar_fronteira(self, dados: Mapping[str, Any]) -> None:
        alvo = self._objeto(dados["alvo"])
        todas_faces = dados["selecao"] == "todas_faces"
        faces_exceto_y_min = dados["selecao"] == "todas_faces_exceto_y_min"
        faces_selecionadas = None
        if faces_exceto_y_min:
            faces = list(alvo.faces)
            if len(faces) < 2:
                raise ErroConstrucaoAedt(
                    f"{dados['nome']}: objeto sem faces suficientes para exclusao"
                )
            face_y_min = min(faces, key=lambda face: float(face.center[1]))
            faces_selecionadas = [
                face for face in faces if face.id != face_y_min.id
            ]
        if dados["tipo"] == "perfect_e":
            atribuicao = (
                faces_selecionadas
                if faces_exceto_y_min
                else (alvo.faces if todas_faces else alvo)
            )
            fronteira = self.app.assign_perfect_e(atribuicao, name=dados["nome"])
        elif dados["tipo"] == "radiation":
            if todas_faces or faces_exceto_y_min:
                fronteira = self.app.assign_radiation_boundary_to_faces(
                    faces_selecionadas if faces_exceto_y_min else alvo.faces,
                    name=dados["nome"],
                )
            else:
                fronteira = self.app.assign_radiation_boundary_to_objects(
                    alvo, name=dados["nome"]
                )
        else:
            raise ErroConstrucaoAedt(f"fronteira não suportada: {dados['tipo']}")
        if not fronteira:
            raise ErroConstrucaoAedt(f"falha ao atribuir fronteira {dados['nome']}")

    def _criar_porta(self, dados: Mapping[str, Any]) -> None:
        porta = self.app.wave_port(
            assignment=self._objeto(dados["alvo"]),
            reference=[self._objeto(nome) for nome in dados["referencia"]],
            create_port_sheet=False,
            integration_line=dados.get("linha_integracao", 0),
            modes=dados.get("modos", 1),
            impedance=dados.get("impedancia", 50),
            name=dados["nome"],
            renormalize=dados.get("renormalizar", True),
            deembed=dados.get("deembed", 0),
        )
        if not porta:
            raise ErroConstrucaoAedt(f"falha ao criar porta {dados['nome']}")
