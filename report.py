from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import os

def draw_round_image(c, img_path, x, y, size):
    img = ImageReader(img_path)

    # Save graphics state
    c.saveState()

    # Create a path with a circle
    path = c.beginPath()
    path.circle(x + size/2, y + size/2, size/2)

    # Apply clipping path
    c.clipPath(path, stroke=0, fill=0)

    # Draw image inside clipped area
    c.drawImage(img, x, y, size, size, mask='auto')

    # Restore graphics state
    c.restoreState()


def generate_portfolio(user, email, about, profile_pic, artworks):
    filename = f"{user}_portfolio.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFillColor(colors.black)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    if profile_pic and os.path.exists(profile_pic):
        draw_round_image(c, profile_pic, 50, height - 150, 100)


    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(200, height - 80, f"{user} Artworks")

    c.setFont("Helvetica", 14)
    c.drawString(200, height - 110, about)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 140, f"Contact: {email}")

    y = height - 250
    x_positions = [50, width / 2 + 20]  # Left col start, Right col start
    col = 0  # Track current column

    if artworks == {}:
        c.save()
        return filename

    for art in artworks:
        if os.path.exists(art["path"]):
            x = x_positions[col]

            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, art['title'])
            y -= 20

            c.setFillColor(colors.grey)
            c.setFont("Helvetica", 10)
            c.drawString(x, y, art['desc'])
            y -= 30


            img = ImageReader(art["path"])
            c.drawImage(img, x, y - 100, width=200, height=100, preserveAspectRatio=True, mask='auto')
            y -= 130


            if col == 0:
                col = 1
                y += 180
            else:
                col = 0
                y -= 50


            if y < 200:
                c.showPage()
                c.setFillColor(colors.black)
                c.rect(0, 0, width, height, fill=True, stroke=False)
                y = height - 250
                col = 0

    c.save()
    return filename
