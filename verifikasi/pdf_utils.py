import os
import subprocess
import tempfile

def pdf_to_images(pdf_path):
    temp_dir = tempfile.mkdtemp()
    output_prefix = os.path.join(temp_dir, "page")

    subprocess.run([
        "pdftoppm",
        "-r", "300",
        "-png",
        pdf_path,
        output_prefix
    ], check=True)

    images = []
    for file in sorted(os.listdir(temp_dir)):
        if file.endswith(".png"):
            images.append(os.path.join(temp_dir, file))

    return images
