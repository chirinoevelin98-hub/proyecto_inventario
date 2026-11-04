from flask import Flask, flash, redirect, render_template, request, url_for, jsonify

from database import init_db
from services import InventarioService

app = Flask(__name__)
app.config["SECRET_KEY"] = "inventario-secret-key"

init_db()
service = InventarioService()


@app.route("/")
def index():
    resumen = service.resumen_general()
    return render_template("index.html", resumen=resumen)


@app.route("/productos", methods=["GET", "POST"])
def productos():
    if request.method == "POST":
        tipo = request.form.get("tipo")

        if tipo == "producto":
            nombre = request.form.get("nombre", "").strip()
            categoria = request.form.get("categoria", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            precio = request.form.get("precio", "").strip()

            try:
                service.crear_producto(nombre, categoria, descripcion, precio)
                flash("Producto registrado correctamente.", "success")
            except ValueError as exc:
                flash(str(exc), "error")

        elif tipo == "variante":
            producto_id = request.form.get("producto_id", "").strip()
            talla = request.form.get("talla", "").strip()
            color = request.form.get("color", "").strip()
            cantidad_inicial = request.form.get("cantidad_inicial", "").strip()
            stock_minimo = request.form.get("stock_minimo", "0").strip()

            try:
                service.registrar_variante(
                    producto_id=producto_id,
                    talla=talla,
                    color=color,
                    cantidad_inicial=cantidad_inicial,
                    stock_minimo=stock_minimo,
                )
                flash("Variante registrada correctamente.", "success")
            except ValueError as exc:
                flash(str(exc), "error")

        return redirect(url_for("productos"))

    productos_list = service.listar_productos()
    return render_template("productos.html", productos=productos_list)


@app.route("/inventario")
def inventario():
    stock = service.listar_inventario()
    alertas = service.listar_alertas()
    return render_template("inventario.html", stock=stock, alertas=alertas)


@app.route("/movimientos", methods=["GET", "POST"])
def movimientos():
    if request.method == "POST":
        variante_id = request.form.get("variante_id", "").strip()
        tipo = request.form.get("tipo", "").strip().lower()
        cantidad = request.form.get("cantidad", "").strip()
        motivo = request.form.get("motivo", "").strip()

        try:
            service.registrar_movimiento(
                variante_id=variante_id,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
            )
            flash("Movimiento registrado correctamente.", "success")
        except ValueError as exc:
            flash(str(exc), "error")

        return redirect(url_for("movimientos"))

    variantes = service.get_variantes_para_movimiento()
    historial = service.listar_movimientos()
    alertas = service.listar_alertas()
    return render_template("movimientos.html", variantes=variantes, historial=historial, alertas=alertas)


@app.route("/api/productos")
def api_productos():
    return jsonify({"productos": service.get_productos_json()})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)

