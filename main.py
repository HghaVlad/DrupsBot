from telebot import TeleBot

from uuid import uuid4

from configparser import ConfigParser
from keyboards import Message, CallbackQuery, MainMenu, SocialsButtons, BackMenu, PurchaseBackMenu, \
    PurchaseBackStepMenu, PurchaseColoursMenu, PurchaseCategoryMenu, PurchaseEndMenu, PurchaseShipMenu, \
    MainMenuAdmin, AdminPanelMenu, YuanEditMenu, PurchaseWayMenu, InputMediaPhoto, LinkPreviewOptions
from db import add_purchase, db_request, get_admins, new_value

config = ConfigParser()
config.read("config.ini")
user_data = {}

bot = TeleBot(config['BOT']['bot_token'])


@bot.message_handler(commands=['start'])
@bot.message_handler(regexp="Вернутся в меню")
def start_command(message: Message):
    admins = get_admins()
    print(admins)
    if str(message.chat.id) in admins:
        with open(config['PHOTO']['welcome_photo'], "rb") as photo:
            bot.send_photo(message.chat.id, photo, config['MESSAGES']['welcome_message'].format(
                first_name=message.from_user.username), parse_mode="HTML", reply_markup=MainMenuAdmin)
    else:
        with open(config['PHOTO']['welcome_photo'], "rb") as photo:
            bot.send_photo(message.chat.id, photo, config['MESSAGES']['welcome_message'].format(
                first_name=message.from_user.username), parse_mode="HTML", reply_markup=MainMenu)

    if message.chat.id in user_data:
        user_data[message.chat.id]['step'] = -1


def calculator_yuan(message: Message):
    if message.text.isdigit() and user_data[message.chat.id]['step'] == 10:
        price = int(message.text) * float(db_request("yuan_rate"))
        bot.send_message(message.chat.id, f"Цена товара без учёта доставки: {price}", reply_markup=BackMenu)
    elif user_data[message.chat.id]['step'] == 10:
        bot.send_message(message.chat.id, "Введите цену целым числом", reply_markup=BackMenu)
        bot.register_next_step_handler(message, calculator_yuan)
def admin_mailing(user_id, ship_price, first_name):
    for admin in get_admins():
        message_text = config['MESSAGES']['mail_admin_message'].format(userid=user_id, first_name=first_name, telegram=user_data[user_id]['telegram'],
                        link=user_data[user_id]['link'], quantity=user_data[user_id]['quantity'],
                        size=user_data[user_id]['size'], colour=user_data[user_id]['colour'],
                        category=user_data[user_id]['category'], ship=user_data[user_id]['ship'],
                        price=user_data[user_id]['price'], ship_price=ship_price)
        bot.send_message(admin, message_text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(False))
        if user_data[user_id]['is_photo']:
            with open(user_data[user_id]['photo_path'], "rb") as photo:
                bot.send_photo(user_id, photo, parse_mode="HTML")

    add_purchase(user_id, first_name,user_data[user_id], ship_price)


def purchase_start(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)

    else:
        user_data.update({message.chat.id: {}})
        user_data[message.chat.id]['step'] = 1
        user_data[message.chat.id]['telegram'] = message.text
        with open(config['PHOTO']['purchase1_photo'], "rb") as photo:
            photo1 = InputMediaPhoto(photo)
            with open(config['PHOTO']['purchase2_photo'], "rb") as photo:
                photo2 = InputMediaPhoto(photo)
                bot.send_media_group(message.chat.id, media=[photo1, photo2])
                bot.send_message(message.chat.id, config['MESSAGES']['purchase2_message'], parse_mode="HTML",
                                 reply_markup=PurchaseBackStepMenu)

        bot.register_next_step_handler(message, purchase_goods_links)


def purchase_goods_links(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)
    elif "К прошлому этапу оформления" in message.text:
        bot.send_message(message.chat.id, config['MESSAGES']['purchase1_message'], parse_mode="HTML",
                         reply_markup=PurchaseBackMenu)
        bot.register_next_step_handler(message, purchase_start)
    elif user_data[message.chat.id]['step'] == 1:
        user_data[message.chat.id]['step'] = 2
        user_data[message.chat.id]['link'] = message.text
        bot.send_message(message.chat.id, config['MESSAGES']['purchase3_message'], parse_mode='HTML',
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_quantity)


def purchase_goods_quantity(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)

    elif "К прошлому этапу оформления" in message.text:
        with open(config['PHOTO']['purchase1_photo'], "rb") as photo:
            photo1 = InputMediaPhoto(photo)
            with open(config['PHOTO']['purchase2_photo'], "rb") as photo:
                photo2 = InputMediaPhoto(photo)
                bot.send_media_group(message.chat.id, media=[photo1, photo2])
                bot.send_message(message.chat.id, config['MESSAGES']['purchase2_message'], parse_mode="HTML",
                                 reply_markup=PurchaseBackStepMenu)

        bot.register_next_step_handler(message, purchase_goods_links)

    elif user_data[message.chat.id]['step'] == 2:
        user_data[message.chat.id]['step'] = 3
        user_data[message.chat.id]['quantity'] = message.text
        bot.send_message(message.chat.id, config['MESSAGES']['purchase4_message'], parse_mode='HTML',
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_size)


def purchase_goods_size(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)

    elif "К прошлому этапу оформления" in message.text:
        bot.send_message(message.chat.id, config['MESSAGES']['purchase3_message'], parse_mode='HTML',
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_quantity)

    elif user_data[message.chat.id]['step'] == 3:
        user_data[message.chat.id]['step'] = 4
        user_data[message.chat.id]['size'] = message.text
        bot.send_message(message.chat.id, config['MESSAGES']['purchase5_message'], parse_mode='HTML',
                         reply_markup=PurchaseColoursMenu)
        bot.register_next_step_handler(message, purchase_goods_photo)


def purchase_goods_colours(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)

    elif "К прошлому этапу оформления" in message.text:
        bot.send_message(message.chat.id, config['MESSAGES']['purchase4_message'], parse_mode='HTML',
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_size)

    elif message.text in ["Синий🔵", "Чёрный⚫️", "Заказ не с Poizon"] and user_data[message.chat.id]['step'] == 4:
        user_data[message.chat.id]['is_photo'] = False
        user_data[message.chat.id]['photo_path'] = ''
        user_data[message.chat.id]['colour'] = message.text
        with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
            bot.send_photo(message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                           reply_markup=PurchaseCategoryMenu)
        bot.register_next_step_handler(message, purchase_goods_category)

    elif "Прислать фотографию" in message.text and user_data[message.chat.id]['step'] == 4:
        bot.send_message(message.chat.id, "Пришлите фотографию в виде файла", parse_mode="HTML",
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_photo)

    elif user_data[message.chat.id]['step'] == 4:
        bot.send_message(message.chat.id, "Пожалуйста выберите из предложенного списка", parse_mode='HTML',
                         reply_markup=PurchaseColoursMenu)
        bot.register_next_step_handler(message, purchase_goods_colours)


def purchase_goods_photo(message: Message):
    print(message.content_type)
    if message.content_type == 'text':
        if "Вернутся в меню" in message.text:
            start_command(message)
        elif "К прошлому этапу оформления" in message.text:
            bot.send_message(message.chat.id, config['MESSAGES']['purchase5_message'], parse_mode='HTML',
                             reply_markup=PurchaseColoursMenu)
            bot.register_next_step_handler(message, purchase_goods_colours)
        elif user_data[message.chat.id]['step'] == 4:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте фото файлом", parse_mode="HTML",
                             reply_markup=PurchaseBackStepMenu)
            bot.register_next_step_handler(message, purchase_goods_photo)

    elif message.content_type == 'document' and user_data[message.chat.id]['step'] == 4:
        try:
            file_path = bot.get_file(message.document.file_id).file_path
            file = bot.download_file(file_path)
            photo_path = config['BOT']['photo_folder'].format(str(uuid4()))
            with open(photo_path, "wb") as img:
                img.write(file)
            user_data[message.chat.id]['step'] = 5
            user_data[message.chat.id]['is_photo'] = True
            user_data[message.chat.id]['colour'] = "фото выше"
            user_data[message.chat.id]['photo_path'] = photo_path
            with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
                bot.send_photo(message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                               reply_markup=PurchaseCategoryMenu)
            bot.register_next_step_handler(message, purchase_goods_category)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "Пожалуйста, отправьте фото файлом", parse_mode="HTML",
                             reply_markup=PurchaseColoursMenu)
            bot.register_next_step_handler(message, purchase_goods_photo)
    elif user_data[message.chat.id]['step'] == 4:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фото файлом", parse_mode="HTML",
                         reply_markup=PurchaseColoursMenu)
        bot.register_next_step_handler(message, purchase_goods_photo)


def purchase_goods_category(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)
    elif "К прошлому этапу оформления" in message.text:
        bot.send_message(message.chat.id, config['MESSAGES']['purchase5_message'], parse_mode='HTML',
                         reply_markup=PurchaseColoursMenu)
        bot.register_next_step_handler(message, purchase_goods_colours)
    elif message.text in ["Обычный товар", "Хрупкий товар(в том числе техника)"] and user_data[message.chat.id]['step'] == 5:
        user_data[message.chat.id]['step'] = 6
        user_data[message.chat.id]['category'] = message.text
        bot.send_message(message.chat.id, config['MESSAGES']['purchase7_message'], parse_mode="HTML",
                         reply_markup=PurchaseShipMenu)
        bot.register_next_step_handler(message, purchase_goods_ship)
    elif user_data[message.chat.id]['step'] == 5:
        bot.send_message(message.chat.id, "Пожалуйста выберите из предложенного списка", parse_mode='HTML',
                         reply_markup=PurchaseCategoryMenu)
        bot.register_next_step_handler(message, purchase_goods_category)


def purchase_goods_ship(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)
    elif "К прошлому этапу оформления" in message.text:
        with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
            bot.send_photo(message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                           reply_markup=PurchaseCategoryMenu)
        bot.register_next_step_handler(message, purchase_goods_category)
    elif message.text in ["Автомобиль(800р/кг) 🚚", "Самолёт(2500р/кг) 🛫"] and user_data[message.chat.id]['step'] == 6:
        user_data[message.chat.id]['step'] = 7
        user_data[message.chat.id]['ship'] = message.text
        bot.send_message(message.chat.id, config['MESSAGES']['purchase8_message'], parse_mode="HTML",
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_price)
    elif user_data[message.chat.id]['step'] == 6:
        bot.send_message(message.chat.id, "Пожалуйста выберите из предложенного списка", parse_mode='HTML',
                         reply_markup=PurchaseShipMenu)
        bot.register_next_step_handler(message, purchase_goods_ship)


def purchase_goods_price(message: Message):
    if "Вернутся в меню" in message.text:
        start_command(message)
    elif "К прошлому этапу оформления" in message.text:
        bot.send_message(message.chat.id, config['MESSAGES']['purchase7_message'], parse_mode="HTML",
                         reply_markup=PurchaseShipMenu)
        bot.register_next_step_handler(message, purchase_goods_ship)
    elif message.text.isdigit() is False:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте цену целым числом", reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(message, purchase_goods_price)
    else:
        user_data[message.chat.id]['price'] = int(message.text)
        print(user_data[message.chat.id])

        ship_price = user_data[message.chat.id]['price'] * float(db_request("yuan_rate"))
        # if user_data[message.chat.id]['category'] == 'Обычный товар' and user_data[message.chat.id]['ship'] == 'Автомобиль(800р/кг) 🚚':
        #     ship_price = db_request("car_standard_price")
        # elif user_data[message.chat.id]['category'] == 'Хрупкий товар(в том числе техника)' and user_data[message.chat.id]['ship'] == 'Автомобиль(800р/кг) 🚚':
        #     ship_price = db_request("car_special_price")
        # elif user_data[message.chat.id]['category'] == 'Обычный товар' and user_data[message.chat.id]['ship'] == 'Самолёт(2500р/кг) 🛫':
        #     ship_price = db_request("plane_standard_price") * db_request("yuan_rate")
        # elif user_data[message.chat.id]['category'] == 'Хрупкий товар(в том числе техника)' and user_data[message.chat.id]['ship'] == 'Самолёт(2500р/кг) 🛫':
        #     ship_price =  * db_request("yuan_rate")
        message_text = config['MESSAGES']['purchase9_message'].format(telegram=user_data[message.chat.id]['telegram'],
                        link=user_data[message.chat.id]['link'], quantity=user_data[message.chat.id]['quantity'],
                        size=user_data[message.chat.id]['size'], colour=user_data[message.chat.id]['colour'],
                        category=user_data[message.chat.id]['category'], ship=user_data[message.chat.id]['ship'],
                        price=user_data[message.chat.id]['price'], ship_price=ship_price, purchase_way=db_request("purchase_way"))
        if user_data[message.chat.id]['is_photo']:
            with open(user_data[message.chat.id]['photo_path'], "rb") as photo:
                bot.send_photo(message.chat.id, photo, parse_mode="HTML")

        bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=PurchaseEndMenu)
        admin_mailing(message.chat.id, ship_price, message.from_user.first_name)


@bot.message_handler(commands=['admin'])
@bot.message_handler(regexp="Админ панель")
def admin_panel(message: Message):
    admins = get_admins()
    if str(message.chat.id) in admins:
        bot.send_message(message.chat.id, "Что редактируем?", reply_markup=AdminPanelMenu)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа")

def yuan_edit(message: Message):
    new_value("yuan_rate", message.text)
    bot.send_message(message.chat.id, "Что редактируем?", reply_markup=AdminPanelMenu)

def way_edit(message: Message):
    new_value("purchase_way", message.text)
    bot.send_message(message.chat.id, "Что редактируем?", reply_markup=AdminPanelMenu)

@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    if call.data == "poizon_is":
        with open(config['PHOTO']['poizon_is_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['poizon_is_message'], parse_mode="HTML",
            reply_markup=BackMenu)
            #bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "drups_why":
        with open(config['PHOTO']['drups_why_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['drups_why_message'], parse_mode="HTML",
                           reply_markup=BackMenu)
            #bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "shipping":
        with open(config['PHOTO']['drups_ship_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['shipping_message'], parse_mode="HTML",
                           reply_markup=BackMenu)
            #bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "yuan_rate":
        with open(config['PHOTO']['yuan_rate_photo'], "rb") as photo:
            yuan = db_request("yuan_rate")
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['yuan_message'].format(
                yuan_rate=yuan), parse_mode="HTML", reply_markup=BackMenu)
            #bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "socials":
        with open(config['PHOTO']['socials_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['socials_message'], parse_mode="HTML",
                           reply_markup=SocialsButtons)
            #bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == 'calculator':
        user_data.update({call.message.chat.id: {"step": 10}})
        bot.send_message(call.message.chat.id, "Ввдеите количество юаней, чтобы посчитать цену товара", reply_markup=BackMenu)
        bot.register_next_step_handler(call.message, calculator_yuan)

    elif call.data == "purchase":
        bot.send_message(call.message.chat.id, config['MESSAGES']['purchase1_message'], parse_mode="HTML",
                         reply_markup=PurchaseBackMenu)
        #bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, purchase_start)

    elif call.data == 'backstep':
        step = user_data[call.message.chat.id]['step']
        print(step)
        if step == 1:
            user_data[call.message.chat.id]['step'] = 0
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase1_message'], parse_mode="HTML",
                             reply_markup=PurchaseBackMenu)
            bot.register_next_step_handler(call.message, purchase_start)
        elif step == 2:
            user_data[call.message.chat.id]['step'] = 1
            with open(config['PHOTO']['purchase1_photo'], "rb") as photo:
                photo1 = InputMediaPhoto(photo)
                with open(config['PHOTO']['purchase2_photo'], "rb") as photo:
                    photo2 = InputMediaPhoto(photo)
                    bot.send_media_group(call.message.chat.id, media=[photo1, photo2])
                    bot.send_message(call.message.chat.id, config['MESSAGES']['purchase2_message'], parse_mode="HTML",
                                     reply_markup=PurchaseBackStepMenu)
            bot.register_next_step_handler(call.message, purchase_goods_links)
        elif step == 3:
            user_data[call.message.chat.id]['step'] = 2
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase3_message'], parse_mode='HTML',
                             reply_markup=PurchaseBackStepMenu)
            bot.register_next_step_handler(call.message, purchase_goods_quantity)
        elif step == 4:
            user_data[call.message.chat.id]['step'] = 3
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase4_message'], parse_mode='HTML',
                             reply_markup=PurchaseBackStepMenu)
            bot.register_next_step_handler(call.message, purchase_goods_size)
        elif step == 5:
            user_data[call.message.chat.id]['step'] = 4
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase5_message'], parse_mode='HTML',
                             reply_markup=PurchaseColoursMenu)
            bot.register_next_step_handler(call.message, purchase_goods_photo)
        elif step == 6:
            user_data[call.message.chat.id]['step'] = 5
            with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
                bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                               reply_markup=PurchaseCategoryMenu)
            bot.register_next_step_handler(call.message, purchase_goods_category)
        elif step == 7:
            user_data[call.message.chat.id]['step'] = 6
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase7_message'], parse_mode="HTML",
                             reply_markup=PurchaseShipMenu)
            bot.register_next_step_handler(call.message, purchase_goods_ship)
        elif step == 8:
            user_data[call.message.chat.id]['step'] = 7
            bot.send_message(call.message.chat.id, config['MESSAGES']['purchase8_message'], parse_mode="HTML",
                             reply_markup=PurchaseBackStepMenu)
            bot.register_next_step_handler(call.message, purchase_goods_price)

    elif call.data == "colour_blue":
        user_data[call.message.chat.id]['step'] = 5
        user_data[call.message.chat.id]['is_photo'] = False
        user_data[call.message.chat.id]['photo_path'] = ''
        user_data[call.message.chat.id]['colour'] = "Синий🔵"
        with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                           reply_markup=PurchaseCategoryMenu)
        #bot.register_next_step_handler(call.message, purchase_goods_category)
    elif call.data == 'colour_black':
        user_data[call.message.chat.id]['step'] = 5
        user_data[call.message.chat.id]['is_photo'] = False
        user_data[call.message.chat.id]['photo_path'] = ''
        user_data[call.message.chat.id]['colour'] = "Чёрный⚫️"
        with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                           reply_markup=PurchaseCategoryMenu)
    elif call.data == "colour_bo_poizon":
        user_data[call.message.chat.id]['step'] = 5
        user_data[call.message.chat.id]['is_photo'] = False
        user_data[call.message.chat.id]['photo_path'] = ''
        user_data[call.message.chat.id]['colour'] = "Заказ не с Poizon️"
        with open(config['PHOTO']['purchase3_photo'], "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, config['MESSAGES']['purchase6_message'], parse_mode="HTML",
                           reply_markup=PurchaseCategoryMenu)

    elif call.data == "category_usual":
        user_data[call.message.chat.id]['step'] = 6
        user_data[call.message.chat.id]['category'] = "Обычный товар"
        bot.send_message(call.message.chat.id, config['MESSAGES']['purchase7_message'], parse_mode="HTML",
                         reply_markup=PurchaseShipMenu)

    elif call.data == "category_special":
        user_data[call.message.chat.id]['step'] = 6
        user_data[call.message.chat.id]['category'] = "Хрупкий товар(в том числе техника)"
        bot.send_message(call.message.chat.id, config['MESSAGES']['purchase7_message'], parse_mode="HTML",
                         reply_markup=PurchaseShipMenu)


    elif call.data == "ship_car":
        user_data[call.message.chat.id]['step'] = 7
        user_data[call.message.chat.id]['ship'] = "Автомобиль(800р/кг) 🚚"
        bot.send_message(call.message.chat.id, config['MESSAGES']['purchase8_message'], parse_mode="HTML",
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(call.message, purchase_goods_price)
    elif call.data == "ship_plane":
        user_data[call.message.chat.id]['step'] = 7
        user_data[call.message.chat.id]['ship'] = "Самолёт(2500р/кг) 🛫"
        bot.send_message(call.message.chat.id, config['MESSAGES']['purchase8_message'], parse_mode="HTML",
                         reply_markup=PurchaseBackStepMenu)
        bot.register_next_step_handler(call.message, purchase_goods_price)

    elif call.data == "menu_back":
        if call.message.chat.id in user_data:
            user_data[call.message.chat.id]['step'] = -1
        start_command(call.message)

    elif call.data == "admin_yuan":
        yuan_rate = db_request("yuan_rate")
        bot.send_message(call.message.chat.id, f"Текущий курс юаня: {yuan_rate}", reply_markup=YuanEditMenu)

    elif call.data == "admin_way":
        purchase_way = db_request("purchase_way")
        bot.send_message(call.message.chat.id, f"Текущий способ оплаты: { purchase_way }", reply_markup=PurchaseWayMenu)

    elif call.data == "yuan_edit":
        bot.send_message(call.message.chat.id, "Введите актуальный курс:")
        bot.register_next_step_handler(call.message, yuan_edit)

    elif call.data == "way_edit":
        bot.send_message(call.message.chat.id, "Введите актуальный способ оплаты:")
        bot.register_next_step_handler(call.message, way_edit)

    elif call.data == "admin_panel_back":
        admins = get_admins()
        if str(call.message.chat.id) in admins:
            bot.send_message(call.message.chat.id, "Что редактируем?", reply_markup=AdminPanelMenu)

bot.infinity_polling()