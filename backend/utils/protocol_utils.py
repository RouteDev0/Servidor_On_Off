"""
Protocol utilities for camera verification.
(Copiado do serviço original – sem alterações)
"""

from typing import Dict, Any


class ProtocolUtils:
    """Utility class for protocol detection and URL building"""

    @staticmethod
    def get_protocol_from_dvr(dvr: Dict[str, Any]) -> str:
        return dvr.get("protocol", "hikvision").lower()

    @staticmethod
    def get_protocol_from_camera(cam: Dict[str, Any]) -> str:
        return cam.get("_dvr_protocol", "hikvision").lower()

    @staticmethod
    def convert_channel_to_intelbras(canal: str) -> str:
        canal = str(canal).strip()
        if len(canal) >= 3 and canal.endswith("01"):
            try:
                return str(int(canal) // 100)
            except ValueError:
                return canal
        return canal

    @staticmethod
    def build_snapshot_url(ip: str, porta: int, canal: str, protocol: str) -> str:
        if protocol == "intelbras":
            canal_convertido = ProtocolUtils.convert_channel_to_intelbras(canal)
            return f"http://{ip}:{porta}/cgi-bin/snapshot.cgi?channel={canal_convertido}"
        elif protocol == "hikvision":
            return f"http://{ip}:{porta}/ISAPI/Streaming/channels/{canal}/picture"
        else:
            raise ValueError(
                f"Unsupported protocol: {protocol}. Use 'hikvision' or 'intelbras'"
            )
