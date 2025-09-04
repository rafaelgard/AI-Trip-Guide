import pytest
import numpy as np
from src.utils import trata_temas

def test_trata_temas():
    # assert isinstance(blocos, list)
    # assert all(isinstance(b, str) for b in blocos)
    # assert "Frase" in blocos[0]

    assert trata_temas('Os temas são "gastronomia", \'transporte\' e "hospedagem".') == "gastronomia, transporte, hospedagem"