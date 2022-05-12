import numpy as np
from emoji import UNICODE_EMOJI
from matplotlib import rcParams


def get_emoji_list(text):
    texto = text.replace('\u200e', '')
    rcParams['font.family'] = 'serif'
    emojis_used = np.array([i if i in texto else None for i in UNICODE_EMOJI['en']])
    emojis_used = emojis_used[emojis_used != None]

    numero = np.array([])
    # Number of emojis
    for i in emojis_used:
        count = texto.count(i)
        numero = np.append(numero, count)

    # Ordered list
    orden = np.argsort(numero)
    lista = [[i] * int(n) for i, n in zip(emojis_used[orden], numero[orden])]

    # Join all the emojis
    flat_list = [i for sublista in lista for i in sublista]
    flat_list.reverse()
    final = ''.join(flat_list)

    return flat_list


