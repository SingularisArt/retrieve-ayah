import argparse
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont
import convert_numbers
import requests


def draw_text(draw, x_loc, y_loc, text, fill, font):
    draw.text((x_loc, y_loc), text, fill=fill, font=font)


def get_image(data, args, verse_num):
    # Get the Quranic text from the response JSON
    try:
        quranic_text = data["ayahs"][verse_num]["text"]
    except IndexError:
        return

    # Add the verse ending mark with number to the bottom right corner
    verse_num_arabic = convert_numbers.english_to_arabic(verse_num)
    ending_mark = "\u06DD" + verse_num_arabic

    quranic_text += ending_mark
    paragraphs = textwrap.wrap(quranic_text, width=80)
    y_text = 50

    # Set up the image and font
    image_width = 750
    image_height = len(paragraphs) * 200
    font_size = 40
    font_path = "/usr/share/fonts/truetype/Scheherazade-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)
    text_color = (0, 0, 0)
    background_color = (255, 255, 255)

    # Create the image
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    # Draw the text
    for para in paragraphs:
        text_bbox = draw.textbbox((0, 0), para, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x_text = (image_width - text_width) // 2

        draw_text(draw, x_text, y_text, para, text_color, font)
        y_text += text_height + 10

    # Format the surah and verse numbers
    out_surah_num = str(args.surah_num).zfill(3)
    out_surah_verse = str(verse_num).zfill(3)

    # Save the image to a file
    dir = f"surah-{out_surah_num}"

    image.save(f"{dir}/surah-{out_surah_num}-verse-{out_surah_verse}.png")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("surah_num", type=int, help="The surah number (1-114)")
    parser.add_argument("--verse-num", "-v", type=int, help="The verse number")

    args = parser.parse_args()

    dir = f"surah-{str(args.surah_num).zfill(3)}"

    if not os.path.exists(f"{dir}"):
        os.makedirs(f"{dir}")

    # Set the API endpoint URL
    url = f"http://api.alquran.cloud/v1/surah/{args.surah_num}"

    # Make an HTTP GET request to the API endpoint
    response = requests.get(url)
    data = response.json()["data"]

    if args.verse_num and (
        args.verse_num < 0 or args.verse_num > int(data["numberOfAyahs"]) + 1
    ):
        print("Verse number is out of range")
        print(
            "For the surah, the verse number should be between 1 and",
            data["numberOfAyahs"] + 1,
        )
        return

    if args.verse_num or args.verse_num == 0:
        get_image(data, args, args.verse_num)
    else:
        for verse_num in range(1, data["numberOfAyahs"] + 1):
            get_image(data, args, verse_num)


if __name__ == "__main__":
    main()
