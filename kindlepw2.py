# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
import itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from connect_calendar import Calendar


def get_font(font_symbol: str, font_size: int):
    return ImageFont.truetype(font_files[font_symbol], font_size)


def get_width(text: str, font_symbol: str, font_size: int):
    bbox = draw.multiline_textbbox(
        (0, 0), text,
        font=get_font(font_symbol, font_size)
    )
    return bbox[2] - bbox[0]


def padding_width(width: int, text: str, font_symbol: str, font_size: int):
    return (width - get_width(text, font_symbol, font_size)) // 2


# for mac only
font_files = dict(
    en='./Fonts/SourceHanSerif-Bold.otf',
    title='./Fonts/Chancery Bold.ttf',
    weekendfont='./Fonts/SourceHanSerif-Heavy.ttc',
    eventfont='./Fonts/SarasaFixedHC-Bold.ttf'
)
# grey scale
grey = np.linspace(0, 255, 16, dtype=int).tolist()
# image size
SIZE = (768, 1024)
# create a new image
img = Image.new('L', SIZE, '#FFF')

today = date.today()
year = today.year
month = today.month

# get my schedule and holidays
events, event_days, holidays = Calendar.get_events(today)

draw = ImageDraw.Draw(img)

# show year
draw.multiline_text(
    (15, 10),
    str(year),
    fill=grey[2],
    font=get_font('title', 24)
)
# show month
draw.multiline_text(
    (padding_width(SIZE[0], today.strftime("%B"), 'title', 30), 28),
    today.strftime("%B"),
    fill=grey[1],
    font=get_font('title', 32)
)

draw.line(((10, 110), (SIZE[0] - 10, 110)), fill=grey[0], width=2)

# labels of weekday
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# get the date of this month
calendar_eu = calendar.monthcalendar(year, month)
# formatted = list(itertools.chain.from_iterable(calendar_eu))+[0 for i in range(7)]
calendar = np.array(calendar_eu).reshape(-1, 7).tolist()

w_day = 768 // 7
x_start = np.arange(7) * w_day

# calendar
# show the label of weekday
for i, text in enumerate(days):
    w_pad = padding_width(w_day, text, 'en', 20)
    if i == 5 or i == 6:
        font_symbol = 'weekendfont'
    else:
        font_symbol = 'en'
    color = grey[7] if (i == 5 or i == 6) else grey[0]
    draw.multiline_text((x_start[i] + w_pad, 120),
                        text, font=get_font(font_symbol, 20), fill=color)

draw.line(((10, 150), (SIZE[0] - 10, 150)), fill=grey[10], width=1)

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue

        if text in event_days:
            # 计算圆的位置和大小
            cx = x_start[i] + w_day // 2 - 1 # 圆心x坐标，并向左移动1像素
            cy = 170 + 60 * h + 24  # 圆心y坐标，向下偏移一些距离
            r = 24  # 半径
            # 在日期下方画一个实心圆
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=grey[14], outline=grey[14])

        # 绘制日期文字
        w_pad = padding_width(w_day, str(text), 'en', 30)
        if i == 5 or i == 6:
            font_symbol = 'weekendfont'
        else:
            font_symbol = 'en'
        color = grey[7] if (i == 5 or i == 6) or text in holidays else grey[0]
        draw.multiline_text((x_start[i] + w_pad, 170 + 60 * h),
                            str(text), font=get_font(font_symbol, 30), fill=color)

# 自适应日期区域的底部
total_height = 170 + 60 * len(calendar)  # 170 是初始 y，60 是每一行的高度
draw.line(((10, total_height), (SIZE[0] - 10, total_height)), fill=grey[1], width=2)

# show the schedule
for h, event in enumerate(events[:8]):

    # 提取日期、时间和事件标题，然后拼接文本
    date_part = f'{event[1][0].split("-")[1]}/{event[1][0].split("-")[2]}'  # MM/DD
    time_part = event[1][1][:5] if len(event[1]) > 1 else '  -  '           # 5 个空格
    title_part = event[0]  # 事件的标题
    text = f'{date_part}  {time_part}  {title_part}'

    # 计算文字的 y 位置，使文字在 50px 高度的行中垂直居中
    text_y = total_height + 50 * h + 25 // 2 # h后面加的数字高度越大越靠下
    draw.multiline_text((30, text_y),
                        text, font=get_font('eventfont', 22), fill=grey[2])
    # 在每一行的底部绘制下划线
    draw.line(
        ((16, total_height + 50 * (h + 1) - 2), (SIZE[0] - 16, total_height + 50 * (h + 1) - 2)), fill=grey[9], width=1)

# 动态调整更新时间的 y 位置
updated_at_y = total_height + 50 * len(events[:8]) + 10  # 60 是每一行的高度，+10 是空隙
dt = datetime.now().isoformat(sep=' ')[:16].replace('-', '.')
draw.multiline_text((10, SIZE[1] - 30), f'Updated at {dt}',
                    font=get_font('en', 16), fill=grey[10])

# to bmp
file_name = './image_1024x768.png'
img.save(file_name, 'png')