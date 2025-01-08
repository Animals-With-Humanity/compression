from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
import numpy as np
import cv2

app = FastAPI()

def compress_image(file: UploadFile, quality: int = 50) -> io.BytesIO:
    """
    Compress an image using OpenCV and return it as a file-like object.
    """
    # Read the uploaded file content
    file_content = file.file.read()

    # Convert file content to numpy array
    nparr = np.frombuffer(file_content, np.uint8)

    # Decode image from the numpy array
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode the image. Ensure it's a valid image format.")

    # Compress the image using OpenCV's imencode
    success, encoded_image = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

    if not success:
        raise ValueError("Failed to encode image")

    # Convert the compressed image to a file-like object
    return io.BytesIO(encoded_image.tobytes())

@app.post("/compress/")
async def compress_image_endpoint(file: UploadFile, quality: int = 50):
    """
    Endpoint to compress an image.
    Args:
    - file (UploadFile): The image file to compress.
    - quality (int): The compression quality (default: 50).

    Returns:
    - Compressed image as a response.
    """
    try:
        # Compress the image
        compressed_image = compress_image(file, quality)

        # Return the compressed image as a response
        return StreamingResponse(
            compressed_image,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image compression failed: {str(e)}")
