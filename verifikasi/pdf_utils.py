import os
import tempfile
import fitz 


def pdf_to_images(pdf_path):
    temp_dir = tempfile.mkdtemp()
    images = []

    try:
        doc = fitz.open(pdf_path)

        for i, page in enumerate(doc):
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)

            output_path = os.path.join(temp_dir, f"page_{i + 1}.png")
            pix.save(output_path)
            images.append(output_path)

        doc.close()

    except Exception as e:
        print("PDF TO IMAGE ERROR:", e)

    return images