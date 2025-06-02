from flask import Blueprint, request, jsonify
from services.payment_service import generar_formulario_pago
from utils import firbase
from firebase_admin import firestore
from routes.project_routes import obtener_datos_proyecto
from sockets.notifications_socket import emitir_notificacion
from pytz import timezone

payment_bp = Blueprint('payment_bp', __name__)
db = firestore.client()


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

@payment_bp.route('/api/pagos/respuesta', methods=['GET'])
def confirmacion_pago():
    from datetime import datetime
    from pytz import timezone

    data = request.args.to_dict()
    print("Datos de redirección (GET):", data)

    # Validar estado de la transacción
    if data.get("transactionState") != "4" and data.get("polTransactionState") != "4":
        return """
            <h2>Transacción Rechazada</h2>
            <a href="/">Volver a la página principal</a>
        """, 200

    try:
        referencia = data.get("referenceCode", "")
        if "_" not in referencia:
            raise ValueError("El referenceCode no contiene un ID de proyecto válido.")

        id_proyecto = referencia.split("_")[1]
        print("ID del proyecto extraído:", id_proyecto)

        try:
            valor = float(data.get("TX_VALUE", "0"))
        except ValueError:
            raise ValueError("TX_VALUE inválido o ausente.")

        email = data.get("buyerEmail", "")
        if not email:
            raise ValueError("Correo del comprador no proporcionado.")

        # Actualizar el monto recaudado del proyecto
        proyecto_ref = db.collection("proyectos").document(id_proyecto)
        proyecto_ref.update({
            "collected": firestore.Increment(valor)
        })

        # Buscar el usuario que aportó
        usuarios_ref = db.collection("users")
        query = usuarios_ref.where("email", "==", email).limit(1).get()
        if not query:
            return "<h2>Usuario no encontrado</h2>", 404

        usuario_doc = query[0]
        user_doc_id = usuario_doc.id
        nombre_aportante = usuario_doc.to_dict().get("name", "Un usuario")

        # Registrar el pago en el perfil del usuario
        db.collection("users").document(user_doc_id).update({
            "pagos": firestore.ArrayUnion([{
                "id_proyecto": id_proyecto,
                "valor": valor,
                "transaction_id": data.get("transactionId"),
                "authorization_code": data.get("authorizationCode"),
                "payment_method": data.get("lapPaymentMethod"),
                "currency": data.get("currency"),
            }])
        })

        # Obtener datos del proyecto
        proyecto = obtener_datos_proyecto(id_proyecto)
        if not proyecto:
            raise ValueError("Proyecto no encontrado.")

        uid_creator = proyecto.get("creator", {}).get("uid")

        # Agregar el nuevo aporte a los supporters
        fecha_local = datetime.now(timezone("America/Bogota")).isoformat()
        nuevo_aporte = {
            "amount": valor,
            "date": fecha_local,
            "name": nombre_aportante
        }
        proyecto_ref.update({
            "supporters": firestore.ArrayUnion([nuevo_aporte])
        })

        # Notificar al creador si no es el mismo usuario que aportó
        if uid_creator != user_doc_id:
            mensaje = f"Hola, {nombre_aportante} ha realizado un aporte de ${valor:.2f} a tu proyecto."
            emitir_notificacion(
                uid_creator,
                "Aporte al proyecto",
                "Se ha realizado un aporte al proyecto",
                mensaje
            )

        return """
            <h2>¡Transacción Exitosa!</h2>
            <a href="/">Volver a la página principal</a>
        """, 200

    except Exception as e:
        import traceback
        print("Error al procesar pago:", str(e))
        traceback.print_exc()
        return f"<h2>Error al procesar el pago: {str(e)}</h2>", 500
