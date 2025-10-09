"""
Módulo responsável pelo gerenciamento de cache
"""
import time
from typing import Dict, Tuple, Any


class CacheManager:
    """Classe responsável por gerenciar cache de verificação de câmeras"""
    
    def __init__(self):
        self.cache_verificacao: Dict[str, Tuple[bool, float]] = {}
        self.falhas_consecutivas: Dict[str, int] = {}
        self.CACHE_DURATION = 30  # segundos - não re-verifica a mesma câmera em menos de 30 segundos
        self.CACHE_DURATION_OFFLINE = 120  # segundos - câmeras offline ficam em cache por mais tempo
        self.ULTIMA_LIMPEZA_CACHE = time.time()
    
    def get_cached_result(self, chave_cache: str) -> Tuple[bool, bool]:
        """
        Obtém resultado do cache se ainda for válido
        Retorna: (resultado_encontrado, resultado_cache)
        """
        tempo_atual = time.time()
        
        if chave_cache in self.cache_verificacao:
            resultado_cache, timestamp = self.cache_verificacao[chave_cache]
            
            # Determina duração do cache baseado no status da câmera
            duracao_cache = self.CACHE_DURATION_OFFLINE if not resultado_cache else self.CACHE_DURATION
            
            # Para câmeras com muitas falhas consecutivas, aumenta ainda mais o cache
            if chave_cache in self.falhas_consecutivas and self.falhas_consecutivas[chave_cache] > 3:
                duracao_cache = self.CACHE_DURATION_OFFLINE * 2  # 4 minutos para câmeras com muitas falhas
            
            if tempo_atual - timestamp < duracao_cache:
                return True, resultado_cache
        
        return False, False
    
    def set_cached_result(self, chave_cache: str, resultado: bool):
        """Define resultado no cache"""
        self.cache_verificacao[chave_cache] = (resultado, time.time())
    
    def update_falhas_consecutivas(self, chave_falhas: str, online: bool):
        """Atualiza contador de falhas consecutivas"""
        if not online:
            self.falhas_consecutivas[chave_falhas] = self.falhas_consecutivas.get(chave_falhas, 0) + 1
        else:
            self.falhas_consecutivas[chave_falhas] = 0  # Reset contador se voltou online
    
    def limpar_cache_antigo(self):
        """Remove entradas antigas do cache para evitar vazamento de memória"""
        tempo_atual = time.time()
        
        # Limpa cache a cada 5 minutos
        if tempo_atual - self.ULTIMA_LIMPEZA_CACHE > 300:
            chaves_para_remover = []
            for chave, (_, timestamp) in self.cache_verificacao.items():
                if tempo_atual - timestamp > self.CACHE_DURATION * 2:  # Remove após 2x o tempo de cache
                    chaves_para_remover.append(chave)
            
            for chave in chaves_para_remover:
                del self.cache_verificacao[chave]
            
            if chaves_para_remover:
                print(f"[INFO] Limpeza de cache: {len(chaves_para_remover)} entradas removidas")
            
            self.ULTIMA_LIMPEZA_CACHE = tempo_atual 