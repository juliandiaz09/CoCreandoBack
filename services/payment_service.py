import hashlib
import uuid

# Credenciales de sandbox
API_KEY = "4Vj8eK4rloUd272L48hsrarnUA"
MERCHANT_ID = "508029"
ACCOUNT_ID = "512321"
CURRENCY = "COP"
PAYU_URL = "https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu"

def generar_firma(api_key, merchant_id, reference_code, amount, currency):
    string = f"{api_key}~{merchant_id}~{reference_code}~{amount:.1f}~{currency}"
    return hashlib.md5(string.encode("utf-8")).hexdigest()

def generar_formulario_pago(id_proyecto, descripcion, valor, email_cliente):
    reference_code = f"proy_{id_proyecto}_{uuid.uuid4().hex[:6]}"
    amount = round(valor, 1)
    signature = generar_firma(API_KEY, MERCHANT_ID, reference_code, amount, CURRENCY)

    formulario = f"""
    <form method="post" action="{PAYU_URL}" id="payuForm">
      <input name="merchantId"    type="hidden"  value="{MERCHANT_ID}">
      <input name="accountId"     type="hidden"  value="{ACCOUNT_ID}">
      <input name="description"   type="hidden"  value="{descripcion}">
      <input name="referenceCode" type="hidden"  value="{reference_code}">
      <input name="amount"        type="hidden"  value="{amount}">
      <input name="tax"           type="hidden"  value="0">
      <input name="taxReturnBase" type="hidden"  value="0">
      <input name="currency"      type="hidden"  value="{CURRENCY}">
      <input name="signature"     type="hidden"  value="{signature}">
      <input name="buyerEmail"    type="hidden"  value="{email_cliente}">
      <input name="responseUrl"   type="hidden"  value="https://cocreandoback.onrender.com/pasarela/api/pagos/respuesta">
      <input name="confirmationUrl" type="hidden" value="https://cocreandoback.onrender.com/pasarela/api/pagos/respuesta">
      <input name="test"          type="hidden"  value="1">
      <input name="Submit"        type="submit"  value="Pagar con PayU">
    </form>
    <script>document.getElementById("payuForm").submit();</script>
    """
    return formulario
