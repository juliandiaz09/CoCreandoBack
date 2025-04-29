class Proyecto:
    def __init__(self, id, titulo, descripcion, categoria, meta_financiera, 
                 fondos_recaudados, fecha_limite, ciudad_desarrollo, id_creador, estado="pendiente"):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.categoria = categoria
        self.meta_financiera = meta_financiera
        self.fondos_recaudados = fondos_recaudados
        self.fecha_limite = fecha_limite
        self.ciudad_desarrollo = ciudad_desarrollo
        self.id_creador = id_creador
        self.estado = estado  # Estados: "pendiente", "activo", "finalizado", "cancelado"

    def to_json(self):
        return self.__dict__
    
