import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "dtg8i6j9f", 
    api_key = "879614286768322", 
    api_secret = "n-ABqaA4p1TFHJAD-adFRvFdd1g", # Click 'View API Keys' above to copy your API secret
    secure=True
)

def subir_a_cloudinary(ruta_archivo):
    respuesta = cloudinary.uploader.upload(ruta_archivo)
    return respuesta['secure_url']  # Esta URL es la que guardarás en Firebase