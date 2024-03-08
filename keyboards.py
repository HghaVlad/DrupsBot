from configparser import ConfigParser
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

config = ConfigParser()
config.read("config.ini")

MainMenu = InlineKeyboardMarkup(row_width=2)
button1 = InlineKeyboardButton("Что такое POIZON?🧐", callback_data="poizon_is")
button2 = InlineKeyboardButton("Почему Drups shipping?🤔", callback_data="drups_why")
button3 = InlineKeyboardButton("Отзывы📑", url=config['BUTTONS']['reviews_link'])
button4 = InlineKeyboardButton("Доставка📦", callback_data="shipping")
button5 = InlineKeyboardButton("Курс юаня💹", callback_data="yuan_rate")
button6 = InlineKeyboardButton("Связаться с менеджером👨‍💼", url=config['BUTTONS']['manager_link'])
button7 = InlineKeyboardButton("Калькулятор✖️", callback_data="calculator")
button8 = InlineKeyboardButton("Наши соц. сети🏠", callback_data="socials")
button9 = InlineKeyboardButton("Оформить заказ🛒", callback_data="purchase")
MainMenu.add(button1, button2, button3, button4, button5, button6, button7, button8, button9)

MainMenuAdmin = InlineKeyboardMarkup(row_width=2)
admin_panel_button = InlineKeyboardButton("Админ панель", callback_data="admin_panel_back")
MainMenuAdmin.add(button1, button2, button3, button4, button5, button6, button7, button8, button9)
MainMenuAdmin.row(admin_panel_button)


BackMenu = InlineKeyboardMarkup()
menu_back_button= InlineKeyboardButton("Вернутся в меню", callback_data="menu_back")
BackMenu.add(menu_back_button)

SocialsButtons = InlineKeyboardMarkup(row_width=2)
button1 = InlineKeyboardButton("Телеграм-канал", url=config['BUTTONS']['telegram_link'])
button2 = InlineKeyboardButton("YouTube", url=config['BUTTONS']['youtube_link'])
button3 = InlineKeyboardButton("Группа во ВКонтакте", url=config['BUTTONS']['vk_link'])
button4 = InlineKeyboardButton("Instagram", url=config['BUTTONS']['instagram_link'])
SocialsButtons.add(button1, button2, button3, button4, menu_back_button)

PurchaseBackMenu = InlineKeyboardMarkup()
PurchaseBackMenu.add(menu_back_button)

PurchaseBackStepMenu = InlineKeyboardMarkup(row_width=1)
back_step_button = InlineKeyboardButton(text="К прошлому этапу оформления", callback_data="backstep")
PurchaseBackStepMenu.add(back_step_button, menu_back_button)

PurchaseColoursMenu = InlineKeyboardMarkup( row_width=1)
blue_button = InlineKeyboardButton(text="Синий🔵", callback_data="colour_blue")
black_button = InlineKeyboardButton(text="Чёрный⚫️", callback_data="colour_black")
no_pozion_button = InlineKeyboardButton(text="Заказ не с Poizon", callback_data="colour_bo_poizon")
PurchaseColoursMenu.add(blue_button, black_button, no_pozion_button, back_step_button, menu_back_button)


PurchaseCategoryMenu = InlineKeyboardMarkup( row_width=1)
usual_good = InlineKeyboardButton(text="Обычный товар", callback_data="category_usual")
special_good = InlineKeyboardButton(text="Хрупкий товар(в том числе техника)", callback_data="category_special")
PurchaseCategoryMenu.add(usual_good, special_good, back_step_button, menu_back_button)


PurchaseShipMenu = InlineKeyboardMarkup(row_width=1)
car_button = InlineKeyboardButton(text="Автомобиль(800р/кг) 🚚", callback_data="ship_car")
plane_button = InlineKeyboardButton(text="Самолёт(2500р/кг) 🛫", callback_data="ship_plane")
PurchaseShipMenu.add(car_button, plane_button, back_step_button, menu_back_button)


PurchaseEndMenu = InlineKeyboardMarkup(row_width=1)
PurchaseEndMenu.add(button6, menu_back_button)

CalculatorBackMenu = InlineKeyboardMarkup(row_width=1)
CalculateButton = InlineKeyboardButton(text="Рассчитать еще", callback_data="calculator")
CalculatorBackMenu.add(CalculateButton, menu_back_button)

AdminPanelMenu = InlineKeyboardMarkup()
yuan_rate_button = InlineKeyboardButton(text="Курс юаня", callback_data="admin_yuan")
purchase_way_button = InlineKeyboardButton(text="Способ оплаты", callback_data="admin_way")
AdminPanelMenu.add(yuan_rate_button, purchase_way_button)
AdminPanelMenu.add(menu_back_button)

YuanEditMenu = InlineKeyboardMarkup()
yuan_edit = InlineKeyboardButton("Редактировать", callback_data="yuan_edit")
admin_panel_back = InlineKeyboardButton("Вернуться в админское меню", callback_data="admin_panel_back")
YuanEditMenu.add(yuan_edit, admin_panel_back)

PurchaseWayMenu = InlineKeyboardMarkup()
way_edit = InlineKeyboardButton("Редактировать", callback_data="way_edit")
PurchaseWayMenu.add(way_edit, admin_panel_back)
