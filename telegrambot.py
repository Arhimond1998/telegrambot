import telebot
import os
import subprocess
import sys
from PIL import Image
from PIL import ImageFilter
from PIL import ImageDraw
import PIL
import pathlib
photo_id = -1

def calculate_photo_id(path):
    res = 0
    for filename in os.listdir(path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            try:
                extension = filename[-4:]
                new_name = str(res) + extension
                res += 1
                os.rename(path + '/' + filename, path + '/' + new_name)
            except BaseException:
                print('Can not process file', filename)
    print('Founded value =', res)              
    return res

def darker_image(img, value):
    draw = ImageDraw.Draw(img)
    pix = img.load()
    width, height = img.size
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0] + value
            b = pix[i, j][1] + value
            c = pix[i, j][2] + value
            a = max(a, 0)
            b = max(b, 0)
            c = max(c, 0)
            a = min(255, a)
            b = min(255, b)
            c = min(255, c)
            draw.point((i, j), (a, b, c))
    del draw
    return img       

def resize_image(input_image_path, output_image_path, file_name):
    global photo_id
    if photo_id == -1:
        photo_id = calculate_photo_id(output_image_path)
    original_image = Image.open(input_image_path + '/' + file_name)
    width, height = original_image.size
    size = (max(width, height), max(width, height))
    print('The original image size is {wide} wide x {high} '
          'high'.format(wide=width, high=height))
    blured_size = (min(width, height), min(width, height))
    box_len = max(size)
    k = size[0] / blured_size[0] 
    blured_size = (int(width * k) , int(height * k))
    blured_image = Image.open(input_image_path + '/' + file_name)
    blured_image = blured_image.resize(blured_size, Image.BICUBIC)
    blured_image = blured_image.filter(ImageFilter.BoxBlur(int(box_len / 50)))
    blured_image = darker_image(blured_image, -100)

    blured_image.paste(original_image, (int((blured_size[0] - width) / 2), int((blured_size[1] - height) / 2)))
    top_left = (int((blured_size[0] - size[0]) / 2), int((blured_size[1] - size[1])/2))
    bot_right = (top_left[0] + box_len, top_left[1] + box_len)
    box = (top_left[0], top_left[1], bot_right[0], bot_right[1])
    blured_image = blured_image.crop(box)
    width, height = blured_image.size
    print('The resized image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))
    blured_image.save(output_image_path + '/' + str(photo_id) + '.jpg')

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def CreateDirectory(path):
    try:
        os.makedirs(path_output)
    except BaseException:
        print('Can not create directory', path)
    else:
        print('Creating directory', path)

path_to_main = str(os.getcwd())
info = dict()
f_info = open(path_to_main + '/info.txt')
try:
    for line in f_info:
        info[line[:line.find('=')]] = line[line.find('=') + 1:].rstrip()
finally:
    f_info.close()
path_output = info['path_output']
token = info['token']
CreateDirectory(path_output)
bot = telebot.TeleBot(token) #insert api token of your bot in ''

@bot.message_handler(content_types=['text'])
def message_handler_text(message):
    chatId = message.chat.id
    bot.send_message(chatId, 'Пришлите мне фотографии.')   

@bot.message_handler(content_types=['photo'])
def message_handler(message):
    global photo_id
    global path_output
    photo = message.photo[0]
    f = bot.get_file(photo.file_id)
    print(f.file_path)
    downloaded_file = bot.download_file(f.file_path)
    filename = f.file_path[f.file_path.rfind('/') + 1 if f.file_path[:f.file_path.rfind('/')] != -1 else 0 :]
    src = path_to_main + '/' + filename
    new_file = open(src, 'wb+')
    new_file.write(downloaded_file)
    resize_image(path_to_main, path_output, filename)#TODO DODO
    photo_id += 1
    new_file.close()
    try:
        print(new_file.name)
        os.remove(new_file.name)
    except:
        print('Cant remove', new_file.name)

print("its wednesday my dudes")

if __name__ == '__main__':
    bot.polling(none_stop=True,  timeout=123)