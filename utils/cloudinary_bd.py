import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os

# Configuration       
cloudinary.config( 
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

def subir_a_cloudinary(ruta_archivo):
    respuesta = cloudinary.uploader.upload(ruta_archivo)
    return respuesta['secure_url']  # Esta URL es la que guardarás en Firebase