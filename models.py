from dataclasses import dataclass


@dataclass
class Producto:
    id: int
    nombre: str
    categoria: str
    descripcion: str
    precio: float
    fecha_creacion: str


@dataclass
class Variante:
    id: int
    producto_id: int
    talla: str
    color: str
    stock_actual: int
    stock_minimo: int


@dataclass
class Movimiento:
    id: int
    variante_id: int
    tipo: str
    cantidad: int
    fecha: str
    detalle: str | None = None
