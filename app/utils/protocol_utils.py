"""
Protocol utilities for camera verification

Provides utilities for handling different camera protocols (Hikvision ISAPI vs Intelbras CGI)
"""
from typing import Dict, Any


class ProtocolUtils:
    """Utility class for protocol detection and URL building"""

    @staticmethod
    def get_protocol_from_dvr(dvr: Dict[str, Any]) -> str:
        """
        Returns the protocol specified in DVR configuration
        
        Args:
            dvr: DVR configuration dictionary
            
        Returns:
            Protocol name ("hikvision" or "intelbras"), defaults to "hikvision"
        """
        return dvr.get("protocol", "hikvision").lower()

    @staticmethod
    def get_protocol_from_camera(cam: Dict[str, Any]) -> str:
        """
        Returns the protocol from camera (injected by condominio_service as _dvr_protocol)
        
        Args:
            cam: Camera configuration dictionary
            
        Returns:
            Protocol name ("hikvision" or "intelbras"), defaults to "hikvision"
        """
        return cam.get("_dvr_protocol", "hikvision").lower()

    @staticmethod
    def convert_channel_to_intelbras(canal: str) -> str:
        """
        Converts Hikvision channel format (101, 201) to Intelbras format (1, 2)
        
        Intelbras uses simple numeric channels: 1, 2, 3, 4...
        Hikvision uses format: 101, 201, 301, 401...
        
        Examples:
            "101" -> "1"
            "201" -> "2"
            "1501" -> "15"
            "1" -> "1" (already in Intelbras format)
            
        Args:
            canal: Channel number in either format
            
        Returns:
            Channel number in Intelbras format (simple numeric)
        """
        canal = str(canal).strip()
        
        # Check if it's in Hikvision format (ends with "01")
        if len(canal) >= 3 and canal.endswith("01"):
            try:
                # Extract the channel number: 101 -> 1, 201 -> 2, etc.
                return str(int(canal) // 100)
            except ValueError:
                return canal
        
        # Already in Intelbras format or other format
        return canal

    @staticmethod
    def build_snapshot_url(ip: str, porta: int, canal: str, protocol: str) -> str:
        """
        Builds snapshot URL based on protocol type
        
        Args:
            ip: Device IP address
            porta: Device port (typically 80)
            canal: Channel number
            protocol: Protocol type ("hikvision" or "intelbras")
            
        Returns:
            Complete snapshot URL
            
        Raises:
            ValueError: If protocol is not supported
            
        Examples:
            Hikvision: http://192.168.1.100:80/ISAPI/Streaming/channels/101/picture
            Intelbras: http://192.168.1.200:80/cgi-bin/snapshot.cgi?channel=1
        """
        if protocol == "intelbras":
            # Auto-convert channel if needed (101 -> 1)
            canal_convertido = ProtocolUtils.convert_channel_to_intelbras(canal)
            return f"http://{ip}:{porta}/cgi-bin/snapshot.cgi?channel={canal_convertido}"
        elif protocol == "hikvision":
            # Use channel as-is for Hikvision (101, 201, etc.)
            return f"http://{ip}:{porta}/ISAPI/Streaming/channels/{canal}/picture"
        else:
            raise ValueError(f"Unsupported protocol: {protocol}. Use 'hikvision' or 'intelbras'")
