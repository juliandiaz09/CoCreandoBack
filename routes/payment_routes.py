from flask import Blueprint, request, jsonify
from services.payment_service import generar_formulario_pago
from utils import firbase
from firebase_admin import firestore
from routes.project_routes import obtener_datos_proyecto
from sockets.notifications_socket import emitir_notificacion

payment_bp = Blueprint('payment_bp', __name__)
db = firestore.client()

#@payment_bp.route('/procesar-pago', methods=['POST'])
#def procesar_pago():
#    datos = request.json
#    respuesta_simulada = generar_formulario_pago(datos)
#    return jsonify(respuesta_simulada)

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
    data = request.args.to_dict()
    print("🔍 Datos de PayU recibidos:", data)

    # 1. Validar estado de la transacción
    if data.get("transactionState") != "4":
        return "<h2>Transacción no aprobada</h2>", 200

    try:
        referencia = data.get("referenceCode")
        id_proyecto = referencia.split("_")[1]
        valor = float(data.get("TX_VALUE"))
        email = data.get("buyerEmail")

        # 2. Obtener datos del proyecto y usuario
        proyecto = obtener_datos_proyecto(id_proyecto)
        if not proyecto:
            return "<h2>Proyecto no encontrado</h2>", 404

        uid_creator = proyecto.get("creator", {}).get("uid")
        usuarios_ref = db.collection("users")
        query = usuarios_ref.where("email", "==", email).limit(1).get()

        if not query:
            return "<h2>Usuario no encontrado</h2>", 404

        user_doc_id = query[0].id
        nombre_aportante = query[0].to_dict().get("name", "Un usuario")

        # 3. Validar que no sea el creador invirtiendo en su propio proyecto
        if uid_creator == user_doc_id:
            print("🔄 El creador está invirtiendo en su propio proyecto. No se notifica.")
        else:
            print(f"📢 Notificando al creador {uid_creator}. Inversor: {user_doc_id} no recibe notificación.")
            
            # 4. Evitar notificaciones duplicadas (verificar si ya existe)
            noti_ref = db.collection("notifications").document(uid_creator) \
                .collection("user_notifications") \
                .where("message", "==", f"{nombre_aportante} ha aportado ${valor:.2f}") \
                .limit(1).get()

            if not noti_ref:
                emitir_notificacion(
                    uid_creator,
                    "Aporte al proyecto",
                    "¡Nuevo aporte!",
                    f"{nombre_aportante} ha aportado ${valor:.2f} a tu proyecto."
                )
            else:
                print("⚠️ Notificación ya existente. No se envía duplicado.")

        # 5. Actualizar BD
        db.collection("proyectos").document(id_proyecto).update({
            "collected": firestore.Increment(valor)
        })

        db.collection("users").document(user_doc_id).update({
            "pagos": firestore.ArrayUnion([{
                "id_proyecto": id_proyecto,
                "valor": valor,
                "transaction_id": data.get("transactionId")
            }])
        })

        return """
            <h2>¡Transacción Exitosa!</h2>
            <a href="/">Volver al inicio</a>
        """, 200

    except Exception as e:
        print("❌ Error en confirmacion_pago:", str(e))
        return f"<h2>Error: {str(e)}</h2>", 500

# @payment_bp.route('/api/pagos/respuesta', methods=['GET'])
# def confirmacion_pago():
#     data = request.args.to_dict()
#     print("Datos de redirección (GET):", data)

#     if data.get("transactionState") != "4" and data.get("polTransactionState") != "4":
#         return """
#             <h2>Transacción Rechazada</h2>
#             <a href="/">Volver a la página principal</a>
#         """, 200

#     try:
#         referencia = data.get("referenceCode")
#         id_proyecto = referencia.split("_")[1]
#         valor = float(data.get("TX_VALUE"))
#         email = data.get("buyerEmail")

#         # Actualizar proyecto
#         db.collection("proyectos").document(id_proyecto).update({
#             "collected": firestore.Increment(valor)
#         })

#         # Buscar usuario por email
#         usuarios_ref = db.collection("users")
#         query = usuarios_ref.where("email", "==", email).limit(1).get()

#         if not query:
#             return "<h2>Usuario no encontrado</h2>", 404

#         user_doc_id = query[0].id

#         # Actualizar pagos del usuario
#         db.collection("users").document(user_doc_id).update({
#             "pagos": firestore.ArrayUnion([{
#                 "id_proyecto": id_proyecto,
#                 "valor": valor,
#                 "transaction_id": data.get("transactionId"),
#                 "authorization_code": data.get("authorizationCode"),
#                 "payment_method": data.get("lapPaymentMethod"),
#                 "currency": data.get("currency"),
#             }])
#         })

#         html_response = """
#         <h2>¡Transacción Exitosa!</h2>
#         """
#         aportante_doc = query[0].to_dict()
#         nombre_aportante = aportante_doc.get("name", "Un usuario")

#         proyecto = obtener_datos_proyecto(id_proyecto)
#         if proyecto:
#             uid_creator = proyecto.get("creator", {}).get("uid")

#         mensaje = f"Hola, {nombre_aportante} ha realizado un aporte de ${valor:.2f} a tu proyecto."
        
#         if uid_creator != user_doc_id:
#             emitir_notificacion(
#                 uid_creator,  # Solo al dueño del proyecto
#                 "Aporte al proyecto",
#                 "Se ha realizado un aporte al proyecto",
#                 mensaje
#             )
#         return html_response, 200
#     except Exception as e:
#         print("Error al procesar pago:", str(e))
#         return f"<h2>Error al procesar el pago: {str(e)}</h2>", 500
