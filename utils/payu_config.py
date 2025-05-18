def generar_formulario_pago(datos_pago):
    """
    Simula la generación de un formulario de pago para pruebas.
    Devuelve datos ficticios sin conectar con PayU real.
    """
    return {
        "success": True,
        "simulacion": True,  # Indica que es una simulación
        "url_pago": "https://sandbox.pagos-simulados.com/checkout",  # URL ficticia
        "datos": {
            "referencia": datos_pago.get("referencia", "TEST-123"),
            "monto": datos_pago.get("monto", 100000),
            "moneda": "COP",
            "estado": "PENDIENTE",
            "mensaje": "Pago simulado correctamente. No se realizó ninguna transacción real."
        }
    }