from PIL import Image, ImageDraw

def modify_photo(path):
    photo_size = (200, 200)
    im = Image.open(path)
    width, height = im.size
    if width - height  > 0:
        im = im.crop((int((width - height) / 2), 0, int((width + height) / 2), height)) # Горизонтальное изображение
    elif width -height < 0:
        im = im.crop((0, int((height - width) / 2), width, int((height + width) / 2)))  # Вертикальное изображение
    im = im.resize(photo_size)
    template = Image.new('L', photo_size, 0)
    ImageDraw.Draw(template).ellipse((0, 0)+template.size, fill=255)
    im.putalpha(template)
    im.save(path[:-4]+'_upd.png')

if __name__ == "__main__":
    modify_photo('Pics//pizdolizi.jpg')