import json
import re


def callback_for_action(action, params=None):
    """
    Generates an uglified JSON representation to use in ``callback_data`` of ``InlineKeyboardButton``.
    :param action: The identifier for your action.
    :param params: A dict of additional parameters.
    :return:
    """

    if params is None:
        params = dict()

    callback_data = {'a': action}
    if params:
        for key, value in params.items():
            callback_data[key] = value
    return callback_str_from_dict(callback_data)


def callback_data_from_update(update):
    try:
        data = update.callback_query.data
        return json.loads(data)
    except:
        return {}


def callback_str_from_dict(d):
    dumped = json.dumps(d, separators=(',', ':'))
    assert len(dumped) <= 64
    return dumped


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
