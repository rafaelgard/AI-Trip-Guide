# import os
# import json
# import pytest
# from src.mistral_llm import llm_traveller

# @pytest.fixture
# def traveller_local(monkeypatch):
#     """Instância da classe simulando modo local, com mocks leves."""
#     monkeypatch.setenv("MODO", "local")
#     t = llm_traveller(habilitar_correcao_gramatical=False,
#                       habilitar_geracao_de_metadados=False)

#     # Mockar dependências pesadas
#     t.llm_metadados = lambda texto, candidate_labels=None: {"labels": ["passeios"]}
#     class DummyResp: text = "Resumo teste"
#     t.llm_resumo = type("LLM", (), {"complete": lambda self, p: DummyResp()})()
#     return t


# def test_dividir_texto_em_blocos(traveller_local):
#     texto = "Frase 1. Frase 2. Frase 3."
#     blocos = traveller_local.dividir_texto_em_blocos(texto, max_chars=10)
#     assert isinstance(blocos, list)
#     assert all(isinstance(b, str) for b in blocos)
#     assert "Frase" in blocos[0]


# def test_checa_se_o_indice_existe_local(traveller_local, tmp_path, monkeypatch):
#     monkeypatch.setattr("os.path.exists", lambda _: True)
#     assert traveller_local.checa_se_o_indice_existe() is True


# def test_ler_metadados_json(tmp_path, traveller_local):
#     caminho = tmp_path / "meta.json"
#     json.dump({"duration": 120}, open(caminho, "w", encoding="utf-8"))
#     minutos = traveller_local.ler_metadados_json(str(caminho))
#     assert pytest.approx(minutos, 0.1) == 2.0


# def test_ler_metadados_json_invalido(tmp_path, traveller_local):
#     caminho = tmp_path / "meta.json"
#     caminho.write_text("{invalid json}")
#     minutos = traveller_local.ler_metadados_json(str(caminho))
#     assert minutos == 0


# def test_gerar_resumo(traveller_local):
#     resultado = traveller_local.gerar_resumo("Faça um resumo")
#     assert isinstance(resultado, str)
#     assert "Resumo" in resultado


# def test_gerar_metadados_local(traveller_local):
#     resultado = traveller_local.gerar_metadados("O texto fala de comida.")
#     assert isinstance(resultado, dict)
#     assert "tema" in resultado
#     assert resultado["tema"] == "passeios" or resultado["tema"] in [
#         "gastronomia", "transporte", "hospedagem", "clima", "dinheiro", "segurança", "outros"
#     ]


# def test_pre_processa_textos(traveller_local):
#     data = {
#         "textos": ["Texto sobre comida e viagem."],
#         "nomes_arquivos": ["arquivo1.txt"],
#         "duracao_minutos": [2.0],
#     }
#     docs = traveller_local.pre_processa_textos(data)
#     assert isinstance(docs, list)
#     assert docs and hasattr(docs[0], "text")
#     assert "tema" in docs[0].metadata
