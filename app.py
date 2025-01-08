from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

def compress_image(file, quality=50):
    """
    Compress an image using OpenCV and return it as a file-like object.
    """
    # Read the uploaded file content
    file_content = file.read()

    # Convert file content to numpy array
    nparr = np.frombuffer(file_content, np.uint8)

    # Decode image from the numpy array
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Compress the image using OpenCV's imencode
    success, encoded_image = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])

    if not success:
        raise ValueError("Failed to encode image")

    # Convert the compressed image to a file-like object
    return io.BytesIO(encoded_image.tobytes())

@app.route('/compress', methods=['POST'])
def compress():
    """
    Endpoint to compress an uploaded image.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    try:
        quality = int(request.form.get('quality', 50))  # Default quality is 50
        compressed_image = compress_image(file, quality)
        compressed_image.seek(0)
        return send_file(
            compressed_image,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f"compressed_{secure_filename(file.filename)}"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
