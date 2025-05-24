def obtener_chat_id(user1_id: str, user2_id: str) -> str:
    """Genera un ID único para un chat privado entre dos usuarios"""
    return "_".join(sorted([user1_id, user2_id]))