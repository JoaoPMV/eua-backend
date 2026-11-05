import cloudinary
import cloudinary.uploader

cloudinary.config(secure=True)


def upload_audio(file_path, public_id):
    """Envia um MP3 ao Cloudinary e devolve a URL https."""
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video",  # o Cloudinary trata áudio como "video"
        folder="audio",
        public_id=public_id,
        overwrite=True,
    )
    return result["secure_url"]