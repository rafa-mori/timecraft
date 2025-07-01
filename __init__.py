"""
TimeCraft AI - Root Package
==========================

Este arquivo permite importação direta da raiz do projeto
sem necessidade de instalar o package.

Exemplo:
    import sys
    sys.path.append('/path/to/timecraft')
    from timecraft_ai import TimeCraftAI
"""

import os
import sys

# Adicionar src ao path para importações diretas
_root_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_root_dir, "src")

if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Re-exportar as principais classes para conveniência
try:
    from .src.timecraft_ai import *
    from .src.timecraft_ai import __author__, __version__
except ImportError as e:
    import warnings

    warnings.warn(f"Não foi possível importar timecraft_ai: {e}")
    warnings.warn(
        "Certifique-se de que as dependências estão instaladas ou use 'make install-dev'"
    )

__all__ = [
    "TimeCraftAI",
    "DatabaseConnector",
    "LinearRegression",
    "RandomForestClassifier",
    "AudioProcessor",
    "ChatbotActions",
    "VoiceSynthesizer",
]
