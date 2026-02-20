"""
Módulo responsável pelo gerenciamento de cache de verificação.
(Copiado do serviço original – sem alterações na lógica)
"""

import time
from typing import Dict, Tuple


class CacheManager:
    """Classe responsável por gerenciar cache de verificação de câmeras"""

    def __init__(self):
        self.cache_verificacao: Dict[str, Tuple[bool, float]] = {}
        self.falhas_consecutivas: Dict[str, int] = {}
        self.CACHE_DURATION = 30       # segundos
        self.CACHE_DURATION_OFFLINE = 120
        self.ULTIMA_LIMPEZA_CACHE = time.time()

    def get_cached_result(self, chave_cache: str) -> Tuple[bool, bool]:
        """Obtém resultado do cache se ainda for válido."""
        tempo_atual = time.time()

        if chave_cache in self.cache_verificacao:
            resultado_cache, timestamp = self.cache_verificacao[chave_cache]
            duracao_cache = (
                self.CACHE_DURATION_OFFLINE if not resultado_cache else self.CACHE_DURATION
            )
            if (
                chave_cache in self.falhas_consecutivas
                and self.falhas_consecutivas[chave_cache] > 3
            ):
                duracao_cache = self.CACHE_DURATION_OFFLINE * 2

            if tempo_atual - timestamp < duracao_cache:
                return True, resultado_cache

        return False, False

    def set_cached_result(self, chave_cache: str, resultado: bool):
        self.cache_verificacao[chave_cache] = (resultado, time.time())

    def update_falhas_consecutivas(self, chave_falhas: str, online: bool):
        if not online:
            self.falhas_consecutivas[chave_falhas] = (
                self.falhas_consecutivas.get(chave_falhas, 0) + 1
            )
        else:
            self.falhas_consecutivas[chave_falhas] = 0

    def limpar_cache_antigo(self):
        tempo_atual = time.time()
        if tempo_atual - self.ULTIMA_LIMPEZA_CACHE > 300:
            chaves_para_remover = [
                chave
                for chave, (_, timestamp) in self.cache_verificacao.items()
                if tempo_atual - timestamp > self.CACHE_DURATION * 2
            ]
            for chave in chaves_para_remover:
                del self.cache_verificacao[chave]
            if chaves_para_remover:
                print(
                    f"[INFO] Limpeza de cache: {len(chaves_para_remover)} entradas removidas"
                )
            self.ULTIMA_LIMPEZA_CACHE = tempo_atual
