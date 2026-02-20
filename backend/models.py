"""
SQLAlchemy ORM models – espelho do schema MySQL fornecido
"""

from sqlalchemy import (
    Column, Integer, String, DECIMAL, TIMESTAMP, Enum, ForeignKey, Text, func
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Empresa(Base):
    __tablename__ = "empresa"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    logo_arquivo = Column(String(255))
    cor_primaria = Column(String(7))
    cor_secundaria = Column(String(7))
    empresa_moni = Column(Integer)

    # Relationships
    clientes = relationship("Cliente", back_populates="empresa", lazy="selectin")
    usuarios = relationship("Usuario", back_populates="empresa", lazy="selectin")


class Cliente(Base):
    __tablename__ = "clientes"

    codigo_moni = Column(String(50), primary_key=True)
    nome = Column(String(255), nullable=False)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    uf = Column(String(2))
    gateway_uuid_id = Column(Integer)
    empresa_id = Column(Integer, ForeignKey("empresa.id"))

    # Relationships
    empresa = relationship("Empresa", back_populates="clientes")
    dispositivos = relationship("Dispositivo", back_populates="cliente", lazy="selectin")


class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id = Column(String(36), primary_key=True)
    tipo_dispositivo = Column(String(50))
    identificador_externo = Column(String(100))
    marca = Column(String(50))
    ip = Column(String(50))
    porta = Column(Integer)
    usuario = Column(String(50))
    senha = Column(String(50))
    codigo_moni = Column(String(50), ForeignKey("clientes.codigo_moni"))
    servicos = Column(String(255))

    # Relationships
    cliente = relationship("Cliente", back_populates="dispositivos")
    pontos_monitoramento = relationship(
        "PontoMonitoramento", back_populates="dispositivo", lazy="selectin"
    )


class PontoMonitoramento(Base):
    __tablename__ = "pontos_monitoramento"

    uuid_camera = Column(String(36), primary_key=True)
    dispositivo_id = Column(String(36), ForeignKey("dispositivos.id"))
    numero_setor = Column(Integer)
    canal_fisico = Column(Integer)
    complemento = Column(String(255))

    # Relationships
    dispositivo = relationship("Dispositivo", back_populates="pontos_monitoramento")
    eventos = relationship("HistoricoEvento", back_populates="ponto", lazy="select")


class HistoricoEvento(Base):
    __tablename__ = "historico_eventos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ponto_id = Column(String(36), ForeignKey("pontos_monitoramento.uuid_camera"))
    tipo_evento = Column(String(50))
    data_hora = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    ponto = relationship("PontoMonitoramento", back_populates="eventos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100))
    login = Column(String(50))
    senha = Column(String(255))
    empresa_id = Column(Integer, ForeignKey("empresa.id"))
    nivel_acesso = Column(Enum("admin", "operador", name="nivel_acesso_enum"))

    # Relationships
    empresa = relationship("Empresa", back_populates="usuarios")


class ClienteServicoGateway(Base):
    __tablename__ = "cliente_servico_gateway"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid_gateway = Column(String(100))
