import base64
from datetime import datetime
from io import BytesIO
from math import floor, ceil
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import numpy as np
from emoji import UNICODE_EMOJI
from matplotlib import rcParams
from dateutil.parser import parse
import re

rcParams['font.family'] = 'serif'


def get_date_time(s):
    date_time = re.search('\d+/\d+/\d+(,\s+)\d+:\d+:\d+', s)
    if date_time is None:
        date_time = re.search('\d+/\d+/\d+(,\s+)\d+:\d+\s+(PM|AM|a.m.|p.m.)', s)
    if date_time is None:
        date_time = re.search('\d+/\d+/\d+\s+\d+:\d+:\d+\s+(a.m.|AM|PM|p.m.)', s)
    if date_time:
        return date_time.group()
    else:
        return None


def get_name(s):
    name = re.search('\].*?:', s)

    if name is None:
        name = re.search('-.*?:', s)
    #     if name is None:
    #         name = re.search(r'\ [a-zA-Z]+:?',s)

    if name:
        return name.group().replace('-', '').replace(']', '').replace(':', '').strip()


def get_uniqe_name(split_list):
    name_list = [get_name(s) for s in split_list if get_name(s)]
    return list(set(name_list))


def get_involved_people_messages(split_list):
    name1, name2 = get_uniqe_name(split_list)
    return np.array([s for s in split_list if get_name(s) == name1]), np.array(
        [s for s in split_list if get_name(s) == name2])


def raplace_am_pm(x):
    replaced = x.replace('[', '').replace(']', '').replace('a.m.', 'AM').replace('p.m.', 'PM').replace('a.m',
                                                                                                       'AM').replace(
        'p.m', 'PM')
    if replaced:
        return replaced
    else:
        return x


def analyse_messages(text):
    try:
        texto = text.replace('\u200e', '')
        mensajes = np.array(texto.split('\n'))
        mensajes = np.array([s for s in mensajes if get_date_time(raplace_am_pm(s))])

        # Obtain dates
        fechas = np.array([get_date_time(raplace_am_pm(i)) for i in mensajes if get_date_time(raplace_am_pm(i))])
        #
        # # Convert to datetime object
        fechas_obj = np.array([parse(fecha) for fecha in fechas])


        delta_datetime = fechas_obj[-1] - fechas_obj[0]
        delta_days = delta_datetime.days

        # delta_datetime = relativedelta(fechas_obj[-1], fechas_obj[0])
        total_days =  f'{ceil((delta_days * 60 ) / 1440)} days' #f'{delta_datetime.years} years, {delta_datetime.months} months, {delta_datetime.days} days'

        # People involved
        name1, name2 = get_uniqe_name(mensajes)

        name1_message_list = np.array([name1 in i for i in mensajes])
        name2_message_list = np.array([name2 in i for i in mensajes])

        # Number of messages
        messages = {'total': len(mensajes), 'name1': len(mensajes[name1_message_list]),
                    'name2': len(mensajes[name2_message_list])}

        # Number of messages per day
        print('Numero Total de mensajes =', len(mensajes))
        print(f'Mensajes de {name1} =', len(mensajes[name1_message_list]))
        print(f'Mensajes de {name2} =', len(mensajes[name2_message_list]))

        emojis_used = np.array([i if i in texto else None for i in UNICODE_EMOJI['en']])
        emojis_used = emojis_used[emojis_used != None]

        # Numero de Emojis
        emojis_list = [f'{i} = {texto.count(i)} veces' for i in emojis_used if texto.count(i) > 5]
        # emojis_count_list = [(i, texto.count(i)) for i in emojis_used if texto.count(i) > 5]
        emojis_count_list = [i * texto.count(i) if texto.count(i) <= 10 else i * 10 for i in emojis_used if texto.count(i) > 5]

        # Search for this keywords
        terminos = [['te quiero', 'tqm'],
                    ['te amo', 'love you'],
                    ['te extraño'],
                    ['perdon', 'perdón', 'sorry'],
                    ['estas bien', 'estás bien', 'estas bien?'],
                    ['feliz', 'happy'],
                    ['triste', 'sad'],
                    ['enojado', 'enojada']]

        share_word = []
        for term in terminos:
            count = 0
            for version in term:
                count += texto.count(version)
            if count == 0:
                share_word.append({'word': version, 'count': ' veces'})
            elif count == 1:
                share_word.append({'word': version, 'count': f'{count} veces'})
            else:
                share_word.append({'word': version, 'count': f'{count} veces'})

        # Messages with pictures
        fotos = ['-PHOTO-' in i for i in mensajes]

        time_of_day_buf = BytesIO()

        # Messages per day
        # plt.hist(fechas_obj[name1_message_list], color='g', bins=100, label=name1, alpha=0.5)
        # plt.hist(fechas_obj[name2_message_list], color='b', bins=100, label=name2, alpha=0.5)
        # plt.hist(fechas_obj[fotos], color='r', bins=100, label='Fotos', alpha=0.5)
        # plt.legend(loc='upper left')
        # plt.xticks(rotation=30)
        # plt.ylabel('Messages / Bin')
        # plt.savefig('mensajes.pdf', bbox_inches='tight')
        # plt.clf()
        # plt.close('all')

        # Time of the day
        hours = np.array([i.hour + i.minute / 60 + i.second / 3600 for i in fechas_obj])

        unique, counts = np.unique(hours, return_counts=True)
        hours_per_massage = dict(zip(unique, counts))
        prefer_time = max(hours_per_massage, key=hours_per_massage.get)

        prefer_time = datetime.strptime(f'{floor(prefer_time)}:00', "%H:%M").strftime("%I %p"), datetime.strptime(f'{ceil(prefer_time)}:00', "%H:%M").strftime("%I %p")


        # if prefer_time < 12:
        #     prefer_time = (f'{floor(prefer_time)} AM', f'{ceil(prefer_time)} AM')
        # elif prefer_time > 12 and prefer_time < 13:
        #     prefer_time = (f'{floor(prefer_time)} PM', f'{ceil(prefer_time) - 12} PM')
        # else:
        #     prefer_time = (f'{floor(prefer_time) - 12} PM', f'{ceil(prefer_time) - 12} PM')

        plt.ylabel("Messages / Hour")
        plt.xlabel("Time of Day [24hr]")
        plt.hist(hours, bins=24, color='#FF278E', histtype='bar', ec='black')
        plt.tick_params(left=False)
        plt.box(False)
        plt.xlim(0, 24)
        plt.savefig(time_of_day_buf, format='png')
        # plt.savefig('hours.jpg', bbox_inches = 'tight', dpi = 250)
        plt.close('all')

        time_of_day_buf.seek(0)

        plot_url = base64.b64encode(time_of_day_buf.getvalue()).decode()

        img_str = 'data:image/png;base64,{}'.format(plot_url)



        return {
            'total_days': ceil(len(mensajes) / 24), #total_days,
            'prefer_time': prefer_time,
            'name1': {'name': name1, 'total_massages': len(mensajes[name1_message_list])},
            'name2': {'name': name2, 'total_massages': len(mensajes[name2_message_list])},
            'total_message': len(mensajes),
            'emojis': emojis_list,
            'emojis_count': emojis_count_list,
            'share_word': share_word,
            'img_str': img_str,

        }
    except Exception as e:
        print(e)
        return None


#
#
# # Folder with conversations
# Folder = 'kami_cecy'
#
# # Read full text
# with open(f'{Folder}/chat.txt',encoding="utf8") as f:
#     texto = f.read()
# # texto = texto.replace('\u200e', '')
#
# print(analyse_messages(texto))
#
# # Read individual messages
# mensajes = np.array(texto.split('\n'))
# mensajes = np.array([s for s in mensajes if get_date_time(raplace_am_pm(s))])
#
#
#
# #Obtain dates
# fechas = np.array([get_date_time(raplace_am_pm(i)) for i in mensajes if get_date_time(raplace_am_pm(i))])
# #
# # # Convert to datetime object
# fechas_obj = np.array([parse(fecha) for fecha in fechas])
#
# # People involved
# name1, name2 = get_uniqe_name(mensajes)
#
# name1_message_list = np.array([name1 in i for i in mensajes])
# name2_message_list = np.array([name2 in i for i in mensajes])
#
# # Number of messages
# messages = { 'total': len(mensajes),'name1':len(mensajes[name1_message_list]),'name2':len(mensajes[name2_message_list])}
#
# print('Numero Total de mensajes =', len(mensajes))
# print(f'Mensajes de {name1} =', len(mensajes[name1_message_list]))
# print(f'Mensajes de {name2} =', len(mensajes[name2_message_list]))
#
# # Search emojis
# emojis_used = np.array([i if i in texto else None for i in UNICODE_EMOJI['en']])
# emojis_used = emojis_used[emojis_used != None]
#
# # Numero de Emojis
# for i in emojis_used:
#     count = texto.count(i)
#     if count > 5:
#         print(f'{i} = {count} veces')
#
# emojis_count_list = {i:texto.count(i) for i in emojis_used if texto.count(i) > 5}
#
# # Search for this keywords
# terminos = [['te quiero', 'tqm'],
#             ['te amo', 'love you'],
#             ['te extraño'],
#             ['perdon', 'perdón', 'sorry'],
#             ['estas bien', 'estás bien', 'estas bien?'],
#             ['wey', 'Wey'],
#             ['feliz', 'happy'],
#             ['triste', 'sad'],
#             ['enojado', 'enojada']]
#
# for term in terminos:
#     count = 0
#     for version in term:
#         count += texto.count(version)
#     if count == 0:
#         print(f'{version} = Ninguna vez')
#     elif count == 1:
#         print(f'{version} = {count} vez')
#     else:
#         print(f'{version} = {count} veces')
#
# # Messages with pictures
# fotos = ['-PHOTO-' in i for i in mensajes]
#
# # Messages per day
# plt.hist(fechas_obj[name1_message_list], color = 'g',  label = name1, alpha = 0.5)
# plt.hist(fechas_obj[name2_message_list], color = 'g',  label = name2, alpha = 0.5)
# plt.hist(fechas_obj[fotos], color = 'red', label = 'Fotos', alpha = 0.5)
# plt.legend(loc = 'upper left')
# plt.xticks(rotation = 30)
# plt.ylabel('Messages / Bin')
# plt.savefig('mensajes.pdf', bbox_inches = 'tight')
# plt.clf(); plt.close('all')
#
# # Time of the day
# hours = np.array([i.hour for i in fechas_obj])
# unique, counts = np.unique(hours, return_counts=True)
# d = dict(zip(unique, counts))
# max_key = max(d, key=d.get)
# print(max_key, d[max_key])
#
# plt.ylabel("Messages / Hour")
# plt.xlabel("Time of Day [24hr]")
# plt.hist(hours, bins = 24, color = 'pink', histtype='bar', ec='black')
# plt.xlim(0,23.9)
# plt.savefig('Horas.jpg', bbox_inches = 'tight', dpi = 250)
# plt.clf();plt.close('all')
# print(hours)
#
#
# from matplotlib.font_manager import FontProperties
# import mplcairo
# font0 = FontProperties()
# family = ['Apple Color Emoji', 'Apple Color Emoji', 'Apple Color Emoji', 'Apple Color Emoji', 'Apple Color Emoji']
# alignment = {'horizontalalignment':'center', 'verticalalignment':'baseline'}
# font1 = font0.copy()
# font1.set_size('large')
#
# t = plt.text(-0.8, 0.9, 'family', fontproperties=font1,**alignment)
#
#
# # plt.hist(emojis_count_list.values(), labels=emojis_count_list.keys(), autopct='%1.1f%%', shadow=True, startangle=140)
# plt.hist(emojis_count_list.keys(), bins = 24, color = 'pink', histtype='bar', ec='black')
# plt.xlim(0,max(emojis_count_list.values()))
# plt.savefig('emoji.jpg', bbox_inches = 'tight', dpi = 250)
# plt.clf()
