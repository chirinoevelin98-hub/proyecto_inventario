from database import get_connection


class InventarioService:
    def crear_producto(self, nombre, categoria, descripcion, precio):
        nombre = (nombre or "").strip()
        categoria = (categoria or "").strip()
        descripcion = (descripcion or "").strip()

        if not nombre:
            raise ValueError("El nombre del producto es obligatorio.")
        if not categoria:
            raise ValueError("La categoría del producto es obligatoria.")
        if not descripcion:
            raise ValueError("La descripción del producto es obligatoria.")

        try:
            precio_num = float(precio)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número válido.")

        if precio_num <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO productos (nombre, categoria, descripcion, precio)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, categoria, descripcion, precio_num),
            )
            return cursor.lastrowid

    def registrar_variante(self, producto_id, talla, color, cantidad_inicial, stock_minimo=0):
        producto_id = str(producto_id).strip() if producto_id is not None else ""
        talla = (talla or "").strip()
        color = (color or "").strip()

        if not producto_id:
            raise ValueError("Debe seleccionar un producto.")

        try:
            producto_id_int = int(producto_id)
        except ValueError:
            raise ValueError("El producto seleccionado no es válido.")

        if not talla:
            raise ValueError("La talla es obligatoria.")
        if not color:
            raise ValueError("El color es obligatorio.")

        try:
            cantidad = int(cantidad_inicial)
        except (TypeError, ValueError):
            raise ValueError("La cantidad inicial debe ser un número entero.")

        if cantidad < 0:
            raise ValueError("La cantidad inicial no puede ser negativa.")

        try:
            minimo = int(stock_minimo)
        except (TypeError, ValueError):
            minimo = 0

        if minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")

        with get_connection() as conn:
            producto = conn.execute(
                "SELECT id FROM productos WHERE id = ?",
                (producto_id_int,),
            ).fetchone()

            if not producto:
                raise ValueError("No existe el producto seleccionado.")

            cursor = conn.execute(
                """
                INSERT INTO variantes (producto_id, talla, color, stock_actual, stock_minimo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (producto_id_int, talla, color, cantidad, minimo),
            )

            variante_id = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO movimientos (variante_id, tipo, cantidad, detalle)
                VALUES (?, ?, ?, ?)
                """,
                (variante_id, "inicial", cantidad, "Stock inicial"),
            )

            return variante_id

    def listar_productos(self):
        with get_connection() as conn:
            productos = conn.execute(
                """
                SELECT p.id, p.nombre, p.categoria, p.descripcion, p.precio, p.fecha_creacion,
                       COALESCE(SUM(v.stock_actual), 0) AS stock_total,
                       COUNT(v.id) AS total_variantes
                FROM productos p
                LEFT JOIN variantes v ON v.producto_id = p.id
                GROUP BY p.id, p.nombre, p.categoria, p.descripcion, p.precio, p.fecha_creacion
                ORDER BY p.nombre ASC
                """
            ).fetchall()

            resultado = []
            for producto in productos:
                variantes = conn.execute(
                    """
                    SELECT id, producto_id, talla, color, stock_actual, stock_minimo
                    FROM variantes
                    WHERE producto_id = ?
                    ORDER BY talla, color
                    """,
                    (producto["id"],),
                ).fetchall()

                resultado.append(
                    {
                        "id": producto["id"],
                        "nombre": producto["nombre"],
                        "categoria": producto["categoria"],
                        "descripcion": producto["descripcion"],
                        "precio": producto["precio"],
                        "fecha_creacion": producto["fecha_creacion"],
                        "stock_total": producto["stock_total"],
                        "total_variantes": producto["total_variantes"],
                        "variantes": [dict(variante) for variante in variantes],
                    }
                )

            return resultado

    def listar_inventario(self):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT p.id AS producto_id, v.id AS variante_id, p.nombre, p.categoria, v.talla,
                       v.color, v.stock_actual, v.stock_minimo,
                       CASE WHEN v.stock_actual <= v.stock_minimo THEN 1 ELSE 0 END AS alerta
                FROM variantes v
                INNER JOIN productos p ON p.id = v.producto_id
                ORDER BY p.nombre ASC, v.talla ASC, v.color ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def get_variantes_para_movimiento(self):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT v.id, p.nombre AS producto, v.talla, v.color, v.stock_actual, v.stock_minimo
                FROM variantes v
                INNER JOIN productos p ON p.id = v.producto_id
                ORDER BY p.nombre ASC, v.talla ASC, v.color ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def registrar_movimiento(self, variante_id, tipo, cantidad, motivo):
        variante_id = (variante_id or "").strip()
        tipo = (tipo or "").strip().lower()
        motivo = (motivo or "").strip()

        if not variante_id:
            raise ValueError("Debe seleccionar una variante.")

        try:
            variante_id_int = int(variante_id)
        except ValueError:
            raise ValueError("La variante seleccionada no es válida.")

        if tipo not in {"entrada", "salida"}:
            raise ValueError("El tipo de movimiento debe ser entrada o salida.")

        try:
            cantidad_int = int(cantidad)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un número entero válido.")

        if cantidad_int <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        with get_connection() as conn:
            variante = conn.execute(
                "SELECT * FROM variantes WHERE id = ?",
                (variante_id_int,),
            ).fetchone()

            if not variante:
                raise ValueError("La variante seleccionada no existe.")

            stock_actual = int(variante["stock_actual"])

            if tipo == "salida" and cantidad_int > stock_actual:
                raise ValueError(
                    f"No puedes retirar {cantidad_int} unidades porque solo hay {stock_actual} disponibles."
                )

            nuevo_stock = stock_actual + cantidad_int if tipo == "entrada" else stock_actual - cantidad_int

            conn.execute(
                "UPDATE variantes SET stock_actual = ? WHERE id = ?",
                (nuevo_stock, variante_id_int),
            )

            conn.execute(
                """
                INSERT INTO movimientos (variante_id, tipo, cantidad, detalle)
                VALUES (?, ?, ?, ?)
                """,
                (variante_id_int, tipo, cantidad_int, motivo or "Sin motivo especificado"),
            )

            return nuevo_stock

    def listar_movimientos(self):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.tipo, m.cantidad, m.fecha, m.detalle,
                       p.nombre AS producto, v.talla, v.color, v.stock_actual
                FROM movimientos m
                INNER JOIN variantes v ON v.id = m.variante_id
                INNER JOIN productos p ON p.id = v.producto_id
                ORDER BY m.fecha DESC, m.id DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def listar_alertas(self):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT p.nombre, p.categoria, v.talla, v.color, v.stock_actual, v.stock_minimo
                FROM variantes v
                INNER JOIN productos p ON p.id = v.producto_id
                WHERE v.stock_actual <= v.stock_minimo
                ORDER BY p.nombre ASC, v.talla ASC, v.color ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def resumen_general(self):
        with get_connection() as conn:
            total_productos = conn.execute("SELECT COUNT(*) AS total FROM productos").fetchone()["total"]
            total_variantes = conn.execute("SELECT COUNT(*) AS total FROM variantes").fetchone()["total"]
            stock_total = conn.execute("SELECT COALESCE(SUM(stock_actual), 0) AS total FROM variantes").fetchone()["total"]
            return {
                "total_productos": total_productos,
                "total_variantes": total_variantes,
                "stock_total": stock_total,
            }

    def get_productos_json(self):
        productos = self.listar_productos()
        json_productos = []

        for producto in productos:
            json_productos.append(
                {
                    "id": producto["id"],
                    "nombre": producto["nombre"],
                    "categoria": producto["categoria"],
                    "descripcion": producto["descripcion"],
                    "precio": producto["precio"],
                    "stock_total": producto["stock_total"],
                    "variantes": producto["variantes"],
                }
            )

        return json_productos
