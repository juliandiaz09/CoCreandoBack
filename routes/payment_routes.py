from flask import Blueprint, request, jsonify
from utils.payu_config import generar_formulario_pago
from utils import firbase


payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/procesar-pago', methods=['POST'])
def procesar_pago():
    datos = request.json
    respuesta_simulada = generar_formulario_pago(datos)
    return jsonify(respuesta_simulada)

@payment_bp.route('/crear-pago', methods=['POST'])
def crear_pago():
    data = request.get_json()
    id_proyecto = data.get("id_proyecto")
    descripcion = data.get("descripcion", "Aporte al proyecto")
    valor = data.get("valor")
    email = data.get("email")

    if not all([id_proyecto, valor, email]):
        return jsonify({"error": "Datos incompletos"}), 400

    html_form = generar_formulario_pago(id_proyecto, descripcion, float(valor), email)
    return html_form  # esto genera y devuelve el formulario HTML que redirige a PayU


@payment_bp.route('/confirmacion-pago', methods=['POST'])
def confirmacion_pago():
    data = request.form.to_dict()
    
    # Solo procesamos pagos aprobados
    estado = data.get("state_pol")
    if estado != "4":  # "4" significa pago aprobado en PayU
        return jsonify({"mensaje": "Pago no aprobado"}), 200

    # Obtenemos valores necesarios del callback de PayU
    valor_pagado = float(data.get("value", 0))
    referencia_venta = data.get("reference_sale")  # aquí deberías haber guardado el ID del proyecto

    if not referencia_venta:
        return jsonify({"error": "Referencia de venta faltante"}), 400

    # Buscar proyecto por ID y sumar fondos
    doc_ref = firbase.db.collection("proyectos").document(referencia_venta)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "Proyecto no encontrado"}), 404

    proyecto = doc.to_dict()
    recaudado_actual = float(proyecto.get("fondos_recaudados", 0))
    nuevo_monto = recaudado_actual + valor_pagado

    doc_ref.update({"fondos_recaudados": nuevo_monto})

    return jsonify({"mensaje": "Fondo actualizado exitosamente"}), 200
