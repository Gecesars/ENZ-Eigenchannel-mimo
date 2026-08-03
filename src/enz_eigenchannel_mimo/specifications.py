from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_GEOMETRIA = "enz-eigenchannel-mimo/geometry-spec/v3"
SCHEMA_CLAIM = "enz-eigenchannel-mimo/claim-record/v1"
SCHEMA_MANIFESTO_V1 = "enz-eigenchannel-mimo/run-manifest/v1"
SCHEMA_MANIFESTO = "enz-eigenchannel-mimo/run-manifest/v2"

_SCHEMA_FILES = {
    SCHEMA_GEOMETRIA: "geometry-spec-v3.schema.json",
    SCHEMA_CLAIM: "claim-record-v1.schema.json",
    SCHEMA_MANIFESTO_V1: "run-manifest-v1.schema.json",
    SCHEMA_MANIFESTO: "run-manifest-v2.schema.json",
}


class ErroEspecificacao(ValueError):
    """Erro estrutural ou semântico em uma especificação científica."""


class EspecificacaoIncompleta(ErroEspecificacao):
    """A etapa solicitada depende de parâmetros desconhecidos."""


def sha256_arquivo(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def carregar_yaml(caminho: str | Path) -> dict[str, Any]:
    origem = Path(caminho).resolve()
    with origem.open("r", encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)
    if not isinstance(dados, dict):
        raise ErroEspecificacao(f"{origem}: documento YAML deve ser um objeto")
    return dados


def carregar_schema(schema_id: str) -> dict[str, Any]:
    try:
        nome = _SCHEMA_FILES[schema_id]
    except KeyError as exc:
        raise ErroEspecificacao(f"schema desconhecido: {schema_id}") from exc
    recurso = resources.files("enz_eigenchannel_mimo.schemas").joinpath(nome)
    import json

    with recurso.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def validar_documento(dados: Mapping[str, Any], schema_id: str | None = None) -> None:
    identificador = schema_id or str(dados.get("schema", ""))
    schema = carregar_schema(identificador)
    validador = Draft202012Validator(schema, format_checker=FormatChecker())
    erros = sorted(validador.iter_errors(dict(dados)), key=lambda erro: list(erro.path))
    if erros:
        mensagens = []
        for erro in erros:
            local = ".".join(str(item) for item in erro.absolute_path) or "<raiz>"
            mensagens.append(f"{local}: {erro.message}")
        raise ErroEspecificacao("documento inválido:\n- " + "\n- ".join(mensagens))


@dataclass(frozen=True, slots=True)
class ProntidaoEtapa:
    etapa: str
    pronta: bool
    ausentes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EspecificacaoGeometrica:
    dados: Mapping[str, Any]
    caminho: Path
    sha256: str

    @classmethod
    def carregar(cls, caminho: str | Path) -> EspecificacaoGeometrica:
        origem = Path(caminho).resolve()
        dados = carregar_yaml(origem)
        validar_documento(dados, SCHEMA_GEOMETRIA)
        spec = cls(dados=dados, caminho=origem, sha256=sha256_arquivo(origem))
        spec.validar_semantica()
        return spec

    @property
    def modelo(self) -> str:
        return str(self.dados["modelo"])

    @property
    def parametros(self) -> Mapping[str, Mapping[str, Any]]:
        return self.dados["parametros"]

    @property
    def etapas(self) -> Mapping[str, Mapping[str, Any]]:
        return self.dados["etapas"]

    def parametro(self, nome: str) -> Mapping[str, Any]:
        try:
            return self.parametros[nome]
        except KeyError as exc:
            raise ErroEspecificacao(f"parâmetro inexistente: {nome}") from exc

    def valor(self, nome: str) -> Any:
        return self.parametro(nome)["valor"]

    def expressao_aedt(self, nome: str) -> str:
        parametro = self.parametro(nome)
        valor = parametro["valor"]
        if valor is None:
            raise EspecificacaoIncompleta(f"{nome}: valor DESCONHECIDO")
        if isinstance(valor, (list, dict)):
            raise ErroEspecificacao(
                f"{nome}: valor não escalar não pode ser variável AEDT"
            )
        unidade = str(parametro["unidade"])
        if unidade == "1":
            return str(valor)
        return f"{valor}{unidade}"

    def etapa(self, nome: str) -> Mapping[str, Any]:
        try:
            return self.etapas[nome]
        except KeyError as exc:
            raise ErroEspecificacao(f"etapa inexistente: {nome}") from exc

    def prontidao(self, etapa: str) -> ProntidaoEtapa:
        dados_etapa = self.etapa(etapa)
        ausentes_parametros = tuple(
            nome
            for nome in dados_etapa["requer"]
            if self.parametro(nome)["valor"] is None
            or self.parametro(nome)["classificacao"] == "DESCONHECIDO"
        )
        bloqueio_estado = (
            ("__estado_documental_bloqueado__",)
            if dados_etapa["estado"] != "executavel"
            else ()
        )
        ausentes = bloqueio_estado + ausentes_parametros
        return ProntidaoEtapa(etapa=etapa, pronta=not ausentes, ausentes=ausentes)

    def exigir_pronta(self, etapa: str) -> None:
        prontidao = self.prontidao(etapa)
        if not prontidao.pronta:
            raise EspecificacaoIncompleta(
                f"{self.modelo}/{etapa} bloqueada por: {', '.join(prontidao.ausentes)}"
            )

    def variaveis_aedt(self, etapa: str) -> dict[str, str]:
        self.exigir_pronta(etapa)
        requeridos = self.etapa(etapa)["requer"]
        return {nome: self.expressao_aedt(nome) for nome in requeridos}

    def validar_semantica(self) -> None:
        parametros = set(self.parametros)
        for nome_etapa, etapa in self.etapas.items():
            inexistentes = sorted(set(etapa["requer"]) - parametros)
            if inexistentes:
                raise ErroEspecificacao(
                    f"{nome_etapa}: parâmetros requeridos inexistentes: {inexistentes}"
                )

            objetos = [objeto["nome"] for objeto in etapa["objetos"]]
            if len(objetos) != len(set(objetos)):
                raise ErroEspecificacao(f"{nome_etapa}: nomes de objetos duplicados")
            conhecidos = set(objetos)

            for operacao in etapa["operacoes"]:
                referencias = {operacao["alvo"], *operacao["ferramentas"]}
                faltantes = sorted(referencias - conhecidos)
                if faltantes:
                    raise ErroEspecificacao(
                        f"{nome_etapa}: operação referencia objetos ausentes: {faltantes}"
                    )
            for fronteira in etapa["fronteiras"]:
                if fronteira["alvo"] not in conhecidos:
                    raise ErroEspecificacao(
                        f"{nome_etapa}: fronteira {fronteira['nome']} sem objeto alvo"
                    )
            for porta in etapa["portas"]:
                referencias = {porta["alvo"], *porta["referencia"]}
                faltantes = sorted(referencias - conhecidos)
                if faltantes:
                    raise ErroEspecificacao(
                        f"{nome_etapa}: porta {porta['nome']} referencia {faltantes}"
                    )
            if etapa["solucao"] == "Eigenmode" and etapa["portas"]:
                raise ErroEspecificacao(
                    f"{nome_etapa}: Eigenmode não deve declarar portas"
                )
            if etapa["estado"] == "executavel" and not etapa["objetos"]:
                raise ErroEspecificacao(f"{nome_etapa}: etapa executável sem objetos")

        pos = self.dados.get("posprocessamento")
        if pos:
            cortes = [corte["nome"] for corte in pos["cortes"]]
            if len(cortes) != len(set(cortes)):
                raise ErroEspecificacao("posprocessamento: nomes de cortes duplicados")
            conhecidos = set(cortes)
            plots = [plot["nome"] for plot in pos["plots_campo"]]
            if len(plots) != len(set(plots)):
                raise ErroEspecificacao("posprocessamento: nomes de plots duplicados")
            faltantes = sorted(
                {plot["corte"] for plot in pos["plots_campo"]} - conhecidos
            )
            if faltantes:
                raise ErroEspecificacao(
                    f"posprocessamento: plots referenciam cortes ausentes: {faltantes}"
                )
            relatorios = [relatorio["nome"] for relatorio in pos["relatorios"]]
            if len(relatorios) != len(set(relatorios)):
                raise ErroEspecificacao(
                    "posprocessamento: nomes de relatórios duplicados"
                )


def validar_arquivo(caminho: str | Path) -> EspecificacaoGeometrica:
    return EspecificacaoGeometrica.carregar(caminho)
