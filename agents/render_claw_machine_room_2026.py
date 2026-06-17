import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".deps" / "pymupdf"))

import fitz  # noqa: E402


W, H = 1080, 1350
OUT = ROOT / "output"
CARDS = OUT / "cards"
FONTS = OUT / "fonts"
LOGO = ROOT / "assets" / "logo" / "main_a_transparent.png"
SLUG = "claw-machine-room-2026"
TOTAL = 7

BASE = "#0F0E0C"
PANEL = "#16140F"
PANEL_2 = "#1E1812"
INK = "#F3EDDE"
MUTED = "#9F927A"
TAN = "#D4B896"
TAN_DEEP = "#B79A6E"
ORANGE = "#D96035"
WARN = "#C36A5C"
LINE = "#514533"
CREAM = "#EEE6D7"

FONT_BLACK = FONTS / "Pretendard-Black.otf"
FONT_BOLD = FONTS / "Pretendard-Bold.otf"
FONT_REG = FONTS / "Pretendard-Regular.otf"


def c(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = c(a), c(b)
    return tuple(ca[i] + (cb[i] - ca[i]) * t for i in range(3))


def rect(x, y, w, h):
    return fitz.Rect(x, y, x + w, y + h)


def center_rect(width, height, y):
    return rect((W - width) / 2, y, width, height)


def install_fonts(page):
    page.insert_font(fontname="PretBlack", fontfile=str(FONT_BLACK))
    page.insert_font(fontname="PretBold", fontfile=str(FONT_BOLD))
    page.insert_font(fontname="Pret", fontfile=str(FONT_REG))


def text(page, box, value, size, color=INK, font="Pret", align=0, lineheight=1.16):
    page.insert_textbox(
        box,
        value,
        fontsize=size,
        fontname=font,
        color=c(color),
        align=align,
        lineheight=lineheight,
    )


def text_at(page, x, y, value, size, color=INK, font="Pret"):
    page.insert_text((x, y), value, fontsize=size, fontname=font, color=c(color))


def draw_bg(page):
    bands = 20
    for i in range(bands):
        y0 = H * i / bands
        y1 = H * (i + 1) / bands
        t = i / (bands - 1)
        fill = mix("#13110E", BASE, t)
        page.draw_rect(fitz.Rect(0, y0, W, y1 + 1), fill=fill, color=None)
    for y in (308, 638, 965):
        page.draw_line((58, y), (1022, y - 96), color=c(LINE), width=0.8, stroke_opacity=0.22)
    page.draw_line((58, 1225), (1022, 1225), color=c(LINE), width=1)


def top(page, no, label):
    page.draw_rect(rect(56, 54, 44, 44), color=c(TAN), width=1)
    text(page, rect(56, 64, 44, 28), f"{no:02d}", 15, TAN, "PretBlack", align=1)
    text(page, rect(112, 59, 560, 34), label, 16, TAN, "PretBold")
    page.insert_image(rect(760, 57, 262, 32), filename=str(LOGO), keep_proportion=True)


def footer(page, note, no):
    text(page, rect(58, 1240, 770, 50), note, 14.2, MUTED, "Pret", lineheight=1.14)
    text(page, rect(928, 1244, 94, 42), f"{no:02d} / {TOTAL:02d}", 15, MUTED, "PretBold", align=2)


def panel(page, r, fill=PANEL, stroke=LINE, width=1, opacity=1):
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=width, fill_opacity=opacity)


def pill(page, x, y, label, width, fill=PANEL, color=INK, stroke=LINE, size=18):
    r = rect(x, y, width, 42)
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=1)
    text(page, rect(x, y + 8, width, 30), label, size, color, "PretBold", align=1)


def label(page, x, y, value, width=220):
    text(page, rect(x, y, width, 26), value, 14.5, TAN, "PretBold")


def title_lines(page, lines, x, y, size=76, gap=0.96, color=INK):
    yy = y
    for line in lines:
        text_at(page, x, yy, line, size, color, "PretBlack")
        yy += size * gap
    return yy


def capsule(page, x, y, r=22, fill=PANEL_2, stroke=TAN_DEEP, opacity=0.72):
    page.draw_circle((x, y), r, fill=c(fill), color=c(stroke), width=1, fill_opacity=opacity)
    page.draw_line((x - r + 4, y), (x + r - 4, y), color=c(stroke), width=0.8, stroke_opacity=0.6)
    page.draw_circle((x - r * 0.34, y - r * 0.32), r * 0.22, fill=c(INK), color=None, fill_opacity=0.12)


def box_prize(page, x, y, w=46, h=38):
    page.draw_rect(rect(x, y, w, h), fill=c(PANEL_2), color=c(TAN_DEEP), width=1, fill_opacity=0.82)
    page.draw_line((x + w * 0.5, y), (x + w * 0.5, y + h), color=c(LINE), width=0.8)
    page.draw_line((x, y + h * 0.42), (x + w, y + h * 0.42), color=c(LINE), width=0.8)


def arrow(page, start, end, color=TAN, width=2.2):
    page.draw_line(start, end, color=c(color), width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    left = (end[0] - ux * 18 - uy * 8, end[1] - uy * 18 + ux * 8)
    right = (end[0] - ux * 18 + uy * 8, end[1] - uy * 18 - ux * 8)
    page.draw_polyline([left, end, right], color=c(color), width=width)


def glass_panel(page, r):
    panel(page, r, fill=PANEL, stroke=TAN_DEEP, width=1.2, opacity=0.92)
    page.draw_line((r.x0 + 28, r.y0 + 30), (r.x1 - 38, r.y0 + 4), color=c(INK), width=1.1, stroke_opacity=0.12)
    page.draw_line((r.x0 + 52, r.y0 + 84), (r.x1 - 74, r.y0 + 42), color=c(INK), width=1, stroke_opacity=0.08)
    page.draw_line((r.x0 + 22, r.y1 - 54), (r.x1 - 30, r.y1 - 92), color=c(INK), width=0.9, stroke_opacity=0.08)


def draw_claw(page, cx, top_y, scale=1.0):
    page.draw_line((cx, top_y), (cx, top_y + 96 * scale), color=c(TAN), width=2)
    page.draw_circle((cx, top_y + 110 * scale), 20 * scale, fill=c(PANEL_2), color=c(TAN), width=1.4)
    joint = (cx, top_y + 134 * scale)
    for sign in (-1, 1):
        p1 = (joint[0] + sign * 18 * scale, joint[1] + 22 * scale)
        p2 = (joint[0] + sign * 42 * scale, joint[1] + 58 * scale)
        page.draw_polyline([joint, p1, p2], color=c(TAN), width=2)


def store_icon(page, x, y, s=1.0, color=TAN_DEEP):
    page.draw_rect(rect(x, y + 24 * s, 46 * s, 34 * s), fill=c(PANEL_2), color=c(color), width=0.9)
    page.draw_polyline([(x, y + 24 * s), (x + 23 * s, y), (x + 46 * s, y + 24 * s)], color=c(color), width=0.9)
    page.draw_rect(rect(x + 18 * s, y + 38 * s, 12 * s, 20 * s), fill=c(BASE), color=c(color), width=0.7)


def card_terminal(page, x, y, s=1.0):
    page.draw_rect(rect(x, y, 56 * s, 82 * s), fill=c(PANEL_2), color=c(TAN_DEEP), width=1.2)
    page.draw_rect(rect(x + 10 * s, y + 12 * s, 36 * s, 20 * s), fill=c(BASE), color=c(LINE), width=0.8)
    for i in range(3):
        page.draw_line((x + 14 * s, y + (48 + i * 10) * s), (x + 42 * s, y + (48 + i * 10) * s), color=c(TAN), width=0.8, stroke_opacity=0.55)


def warning_triangle(page, x, y, s=1.0):
    pts = [(x + 32 * s, y), (x + 64 * s, y + 58 * s), (x, y + 58 * s), (x + 32 * s, y)]
    page.draw_polyline(pts, color=c(WARN), width=1.4)
    text(page, rect(x + 19 * s, y + 20 * s, 26 * s, 30 * s), "!", 20 * s, WARN, "PretBlack", align=1)


def card1(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 1, "CLAW ROOM SIGNAL")
    label(p, 58, 146, "TREND FRAME")
    title_lines(p, ["뽑기방은", "왜 다시", "눈에 띌까?"], 58, 250, size=88, gap=0.94)
    text(p, rect(58, 560, 720, 82), "큰 소비보다 작은 돈으로,\n바로 확인하고 손에 쥘 수 있는 재미.", 28, MUTED, "Pret", lineheight=1.28)

    machine = rect(58, 700, 964, 430)
    glass_panel(p, machine)
    draw_claw(p, 540, 728, 1.15)
    for i in range(30):
        row, col = divmod(i, 10)
        capsule(p, 176 + col * 78 + (row % 2) * 24, 902 + row * 60, r=21, fill=PANEL_2 if i % 3 else "#211911")
    for x in (214, 408, 620, 808):
        box_prize(p, x, 1050, 58, 42)
    steps = [("작은 시도", 94), ("바로 확인", 390), ("손에 잡히는 보상", 686)]
    for i, (txt, x) in enumerate(steps):
        panel(p, rect(x, 1148, 236, 54), fill=BASE, stroke=TAN_DEEP, opacity=0.92)
        text(p, rect(x, 1163, 236, 30), txt, 19, TAN if i == 2 else INK, "PretBlack", align=1)
        if i < 2:
            arrow(p, (x + 246, 1175), (x + 286, 1175), color=TAN_DEEP, width=1.8)
    footer(p, "모든 지역·연령의 유행으로 일반화하지 않고, 관찰된 소비 흐름으로 봅니다.", 1)


def card2(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 2, "EXPERIENCE LOOP")
    label(p, 58, 146, "EXPERIENCE")
    title_lines(p, ["핵심은", "운 하나가", "아닙니다"], 58, 245, size=82, gap=0.96)
    text(p, rect(58, 540, 470, 118), "한 번 더 해볼 만한 가격,\n바로 보이는 결과,\n끝나고 남는 물건이 함께 작동합니다.", 26, MUTED, "Pret", lineheight=1.26)
    panel(p, rect(58, 884, 430, 164), fill=PANEL_2, stroke=TAN_DEEP)
    text(p, rect(84, 920, 380, 46), "운보다 경험 설계", 35, TAN, "PretBlack", align=1)
    text(p, rect(86, 982, 374, 34), "PRICE  RESULT  COLLECT", 16, MUTED, "PretBold", align=1)

    items = [
        ("가격", "부담이 낮아야\n첫 시도가 생깁니다", "COIN"),
        ("결과 확인", "기다리지 않아야\n재미가 끊기지 않습니다", "NOW"),
        ("소장품", "끝나고도 남는\n물건이 있어야 기억됩니다", "KEEP"),
    ]
    for i, (head, desc, meta) in enumerate(items):
        y = 210 + i * 280
        panel(p, rect(560, y, 462, 218), fill=PANEL_2, stroke=TAN_DEEP if i == 2 else LINE, width=1.2)
        p.draw_circle((616, y + 66), 33, fill=c(BASE), color=c(TAN_DEEP), width=1.1)
        if i == 0:
            text(p, rect(595, y + 49, 42, 34), "₩", 23, TAN, "PretBlack", align=1)
        elif i == 1:
            page_r = rect(594, y + 43, 44, 44)
            p.draw_rect(page_r, fill=c(BASE), color=c(TAN), width=1)
            p.draw_line((604, y + 65), (627, y + 65), color=c(TAN), width=1.2)
        else:
            capsule(p, 616, y + 66, r=24)
        text_at(p, 672, y + 72, head, 34, INK, "PretBlack")
        text(p, rect(672, y + 94, 292, 76), desc, 23, MUTED, "Pret", lineheight=1.22)
        pill(p, 858, y + 160, meta, 124, fill=BASE, color=TAN, size=15)
    footer(p, "심리 효과를 과도하게 해석하지 않습니다. 보상 구조를 설명하는 카드입니다.", 2)


def card3(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 3, "DOMESTIC ACCESS")
    label(p, 58, 146, "DOMESTIC")
    title_lines(p, ["국내에선", "문턱이", "낮아졌습니다"], 58, 236, size=76, gap=0.96)
    text(p, rect(58, 505, 520, 88), "매장 수 증가, 무인 운영,\n카드 결제가 가벼운 놀이 소비를 더 쉽게 만들었습니다.", 25, MUTED, "Pret", lineheight=1.22)

    panel(p, rect(58, 664, 452, 300), fill=PANEL_2, stroke=TAN_DEEP, width=1.4)
    text(p, rect(88, 694, 392, 34), "2025년 3분기 전국 인형뽑기방", 18, TAN, "PretBold", align=1)
    text_at(p, 138, 834, "6,144", 104, TAN, "PretBlack")
    text_at(p, 432, 852, "곳", 25, TAN, "PretBlack")
    pill(p, 92, 886, "전년 동기 5,028곳", 190, fill=BASE, color=INK, size=15)
    pill(p, 300, 886, "1,116곳 증가", 150, fill=BASE, color=TAN, stroke=TAN_DEEP, size=16)

    for i, txt in enumerate(["무인 운영", "카드 결제", "가성비 놀이문화"]):
        y = 664 + i * 104
        panel(p, rect(560, y, 462, 76), fill=PANEL_2, stroke=LINE)
        text_at(p, 604, y + 50, txt, 30, INK, "PretBlack")
        if i == 0:
            store_icon(p, 934, y + 14, 0.72, color=TAN)
        elif i == 1:
            card_terminal(p, 946, y + 14, 0.56)
        else:
            text(p, rect(928, y + 19, 70, 32), "LOW", 19, TAN, "PretBlack", align=1)
    panel(p, rect(560, 1000, 462, 96), fill=BASE, stroke=TAN_DEEP)
    text_at(p, 660, 1048, "청소년게임제공업소 5,957곳", 21, TAN, "PretBlack")
    text_at(p, 674, 1080, "최근 2년 20퍼센트 가까이 증가 보도", 17, MUTED, "PretBold")

    for row in range(2):
        for col in range(6):
            store_icon(p, 88 + col * 66, 996 + row * 66, 0.7, color=TAN_DEEP if row or col < 4 else ORANGE)
    footer(p, "출처: 경기일보/Daum, 연합뉴스. 증가 수치는 업소 수 기준이며 수요 증가를 뜻하지 않습니다.", 3)


def card4(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 4, "GLOBAL COLLECTING")
    label(p, 58, 146, "GLOBAL")
    title_lines(p, ["해외에선", "랜덤이", "수집 시장이", "됐습니다"], 58, 232, size=72, gap=0.94)
    text(p, rect(58, 548, 720, 78), "일본 캡슐토이와 Pop Mart 흐름은\n사람들이 취향을 모으는 방식을 보여줍니다.", 25, MUTED, "Pret", lineheight=1.24)

    panel(p, rect(408, 632, 264, 48), fill=BASE, stroke=TAN_DEEP, opacity=0.94)
    text_at(p, 493, 663, "취향 수집", 20, TAN, "PretBlack")

    left = rect(58, 710, 442, 340)
    right = rect(580, 710, 442, 340)
    for r, head, big, sub in [
        (left, "일본 캡슐토이 시장", "1,960억 엔", "2025년 시장 규모 / 2024년 대비 39.0 퍼센트 증가"),
        (right, "Pop Mart 매출", "371.2억 위안", "2025년 매출 / 전년 대비 184.7 퍼센트 증가"),
    ]:
        panel(p, r, fill=PANEL_2, stroke=TAN_DEEP, width=1.3)
        text_at(p, r.x0 + 28, r.y0 + 64, head, 26, TAN, "PretBlack")
        text(p, rect(r.x0 + 26, r.y0 + 104, r.width - 52, 78), big, 50, INK, "PretBlack")
        text(p, rect(r.x0 + 28, r.y0 + 190, r.width - 56, 66), sub, 19, MUTED, "Pret", lineheight=1.18)
    for i in range(12):
        capsule(p, 126 + (i % 6) * 56, 958 + (i // 6) * 46, r=16, fill=BASE if i % 2 else PANEL)
    for i in range(12):
        box_prize(p, 628 + (i % 4) * 78, 930 + (i // 4) * 42, 44, 30)
    panel(p, rect(116, 1092, 848, 62), fill=BASE, stroke=LINE)
    text(p, rect(138, 1108, 804, 38), "관심도 신호: 2025년 가챠 언급량 810,583건 / 전년 대비 약 82 퍼센트 증가", 19, TAN, "PretBlack", align=1)
    footer(p, "출처: JACTA, Pop Mart, 제일기획 매거진. 해외 사례를 국내 시장과 직접 동일시하지 않습니다.", 4)


def card5(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 5, "GUARDRAIL")
    label(p, 58, 146, "GUARDRAIL")
    title_lines(p, ["재미가", "커질수록", "선이 필요합니다"], 58, 236, size=78, gap=0.96)
    text(p, rect(58, 520, 740, 82), "공정성, 경품 기준, 민원 대응이 빠지면\n작은 재미가 운영 리스크가 됩니다.", 26, MUTED, "Pret", lineheight=1.22)

    gates = [
        ("공정성", "확률·난이도 오해를\n줄일 것"),
        ("경품 기준", "허용 기준을\n확인할 것"),
        ("민원 리스크", "기계·결제·환불 문의를\n관리할 것"),
    ]
    for i, (head, desc) in enumerate(gates):
        x = 58 + i * 326
        panel(p, rect(x, 672, 300, 276), fill=PANEL_2, stroke=TAN_DEEP if i == 1 else LINE, width=1.2)
        if i == 0:
            page = rect(x + 114, 710, 72, 62)
            p.draw_rect(page, fill=c(BASE), color=c(TAN), width=1.2)
            p.draw_line((x + 128, 740), (x + 172, 740), color=c(TAN), width=1)
        elif i == 1:
            text(p, rect(x + 86, 720, 128, 48), "10,000", 28, TAN, "PretBlack", align=1)
            text(p, rect(x + 102, 762, 96, 28), "원 기준", 16, MUTED, "PretBold", align=1)
        else:
            warning_triangle(p, x + 118, 710, 0.86)
        text_at(p, x + 94, 836, head, 29, INK, "PretBlack")
        text(p, rect(x + 26, 858, 248, 64), desc, 20, MUTED, "Pret", align=1, lineheight=1.18)
    panel(p, rect(168, 984, 744, 60), fill=BASE, stroke=TAN_DEEP)
    text_at(p, 318, 1023, "경품 기준 10,000원 / 2020년 시행령 개정", 20, TAN, "PretBlack")
    warnings = ["경품기준 위반 보도", "기계 개조 의혹 보도", "민원 증가 보도"]
    for i, item in enumerate(warnings):
        pill(p, 122 + i * 284, 1084, item, 250, fill=PANEL_2, color=INK, stroke=WARN, size=16)
    footer(p, "출처: 정책브리핑, 연합뉴스. 위반·개조는 전체 업소 단정이 아니라 보도된 리스크입니다.", 5)


def card6(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 6, "TAKEAWAY")
    label(p, 58, 146, "TAKEAWAY")
    title_lines(p, ["따라 할 건", "랜덤이 아니라", "보상 설계"], 58, 232, size=80, gap=0.96)
    text(p, rect(58, 518, 760, 82), "작은 브랜드라면 뽑기보다,\n고객이 다시 참여할 이유를 작고 투명하게 만들어야 합니다.", 26, MUTED, "Pret", lineheight=1.22)

    for x, title, items, stroke in [
        (58, "그대로 따라 하면 위험", ["랜덤만 강조", "규칙 불명확", "보상 매력 부족"], WARN),
        (560, "가져올 것은 설계", ["낮은 진입가", "모으고 싶은 보상", "바로 공유할 장면"], TAN_DEEP),
    ]:
        panel(p, rect(x, 668, 462, 276), fill=PANEL_2, stroke=stroke, width=1.2)
        text(p, rect(x + 28, 700, 406, 36), title, 27, TAN if stroke == TAN_DEEP else WARN, "PretBlack", align=1)
        for i, item in enumerate(items):
            y = 762 + i * 54
            if stroke == WARN:
                p.draw_line((x + 48, y + 16), (x + 70, y + 38), color=c(WARN), width=1.6)
                p.draw_line((x + 70, y + 16), (x + 48, y + 38), color=c(WARN), width=1.6)
            else:
                p.draw_polyline([(x + 48, y + 28), (x + 60, y + 40), (x + 78, y + 16)], color=c(TAN), width=1.8)
            text(p, rect(x + 96, y + 10, 310, 34), item, 23, INK, "PretBold")

    checks = [
        "진입 가격이 가벼운가",
        "보상이 소장할 만한가",
        "규칙과 조건이 투명한가",
        "재방문할 이유가 있는가",
    ]
    for i, item in enumerate(checks):
        col, row = i % 2, i // 2
        x = 58 + col * 502
        y = 990 + row * 76
        panel(p, rect(x, y, 462, 54), fill=BASE, stroke=LINE)
        p.draw_rect(rect(x + 22, y + 16, 22, 22), fill=c(PANEL), color=c(TAN_DEEP), width=1)
        p.draw_polyline([(x + 27, y + 28), (x + 34, y + 35), (x + 45, y + 20)], color=c(TAN), width=1.6)
        text_at(p, x + 64, y + 37, item, 20, INK, "PretBold")
    panel(p, rect(338, 1144, 404, 54), fill=PANEL_2, stroke=TAN_DEEP)
    text(p, rect(358, 1159, 364, 28), "SAVE THIS  /  REWARD DESIGN CHECK", 16, TAN, "PretBlack", align=1)
    footer(p, "랜덤 방식은 성과를 약속하지 않습니다. 업종별 법규, 고지, 환불·교환 기준 확인이 필요합니다.", 6)


def card7(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    p.draw_rect(rect(150, 560, 780, 160), color=c(TAN_DEEP), width=1, fill=None, stroke_opacity=0.35)
    page_line_y = 638
    p.draw_line((180, page_line_y), (900, page_line_y - 42), color=c(INK), width=1, stroke_opacity=0.08)
    p.insert_image(center_rect(760, 90, 592), filename=str(LOGO), keep_proportion=True)
    text(p, rect(58, 738, 964, 42), "TREND CARDNEWS BY EARLYSHINE", 18, TAN, "PretBold", align=1)
    text(p, rect(930, 1244, 92, 42), "07 / 07", 15, MUTED, "PretBold", align=2)


HTML_CARDS = [
    ("01", "HOOK", "뽑기방은 왜 다시 눈에 띌까?", "큰 소비보다 작은 돈으로, 바로 확인하고 손에 쥘 수 있는 재미가 있습니다.", ["작은 시도", "바로 확인", "손에 잡히는 보상"]),
    ("02", "EXPERIENCE", "핵심은 운 하나가 아닙니다", "한 번 더 해볼 만한 가격, 바로 보이는 결과, 남는 물건이 함께 작동합니다.", ["가격", "결과 확인", "소장품"]),
    ("03", "DOMESTIC", "국내에선 문턱이 낮아졌습니다", "매장 수 증가, 무인 운영, 카드 결제가 가벼운 놀이 소비를 더 쉽게 만들었습니다.", ["6,144곳", "전년 동기 5,028곳", "+1,116곳"]),
    ("04", "GLOBAL", "해외에선 랜덤이 수집 시장이 됐습니다", "일본 캡슐토이와 Pop Mart 흐름은 사람들이 취향을 모으는 방식을 보여줍니다.", ["1,960억 엔", "371.2억 위안", "가챠 언급량 810,583건"]),
    ("05", "GUARDRAIL", "재미가 커질수록 선이 필요합니다", "공정성, 경품 기준, 민원 대응이 빠지면 작은 재미가 운영 리스크가 됩니다.", ["공정성", "경품 기준", "민원 리스크"]),
    ("06", "TAKEAWAY", "따라 할 건 랜덤이 아니라 보상 설계", "작은 브랜드라면 고객이 다시 참여할 이유를 작고 투명하게 만들어야 합니다.", ["낮은 진입가", "소장 보상", "투명한 규칙", "재방문 이유"]),
]


def write_html():
    css = f"""
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Regular.otf'); }}
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Bold.otf'); font-weight: 700; }}
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Black.otf'); font-weight: 900; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: {BASE}; color: {INK}; font-family: Pret, sans-serif; }}
    main {{ display: grid; gap: 28px; justify-content: center; padding: 28px; }}
    .card {{ position: relative; width: 1080px; height: 1350px; overflow: hidden; padding: 58px; background: linear-gradient(180deg, #13110e 0%, {BASE} 70%, #11100d 100%); break-after: page; }}
    .top {{ display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 2; }}
    .kicker {{ color: {TAN}; font-weight: 800; letter-spacing: .18em; font-size: 16px; }}
    .kicker b {{ display: inline-flex; width: 44px; height: 44px; border: 1px solid {TAN}; align-items: center; justify-content: center; margin-right: 12px; letter-spacing: 0; }}
    .logo {{ width: 262px; height: auto; }}
    .body {{ margin-top: 86px; position: relative; z-index: 2; }}
    .label {{ color: {TAN}; font-size: 15px; font-weight: 800; letter-spacing: .26em; }}
    h1 {{ margin: 54px 0 30px; max-width: 830px; font-size: 82px; line-height: 1.03; font-weight: 900; word-break: keep-all; }}
    p {{ margin: 0; max-width: 760px; color: {MUTED}; font-size: 27px; line-height: 1.35; word-break: keep-all; }}
    .glass {{ margin-top: 56px; min-height: 320px; border: 1px solid {TAN_DEEP}; background: {PANEL}; padding: 34px; display: grid; align-content: end; }}
    .capsules {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; opacity: .9; margin-bottom: 28px; }}
    .capsules i {{ display: block; aspect-ratio: 1; border-radius: 50%; border: 1px solid {TAN_DEEP}; background: {PANEL_2}; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 12px; }}
    .chip {{ border: 1px solid {LINE}; background: {BASE}; color: {INK}; padding: 12px 18px; font-size: 20px; font-weight: 800; }}
    .footer {{ position: absolute; left: 58px; right: 58px; bottom: 78px; padding-top: 18px; border-top: 1px solid {LINE}; display: flex; justify-content: space-between; color: {MUTED}; font-size: 14px; }}
    .ending {{ display: flex; align-items: center; justify-content: center; flex-direction: column; }}
    .ending img {{ width: 760px; }}
    @page {{ size: 1080px 1350px; margin: 0; }}
    @media print {{ main {{ padding: 0; gap: 0; }} }}
    """
    notes = [
        "모든 지역·연령의 유행으로 일반화하지 않고, 관찰된 소비 흐름으로 봅니다.",
        "심리 효과를 과도하게 해석하지 않습니다. 보상 구조를 설명하는 카드입니다.",
        "출처: 경기일보/Daum, 연합뉴스. 증가 수치는 업소 수 기준이며 수요 증가를 뜻하지 않습니다.",
        "출처: JACTA, Pop Mart, 제일기획 매거진. 해외 사례를 국내 시장과 직접 동일시하지 않습니다.",
        "출처: 정책브리핑, 연합뉴스. 위반·개조는 전체 업소 단정이 아니라 보도된 리스크입니다.",
        "랜덤 방식은 성과를 약속하지 않습니다. 업종별 법규, 고지, 환불·교환 기준 확인이 필요합니다.",
    ]
    sections = []
    for idx, (no, label_text, title, sub, chips) in enumerate(HTML_CARDS, start=1):
        chip_html = "".join(f"<span class='chip'>{html.escape(ch)}</span>" for ch in chips)
        caps = "".join("<i></i>" for _ in range(36))
        sections.append(
            f"<section class='card'><div class='top'><span class='kicker'><b>{no}</b>{label_text}</span><img class='logo' src='../assets/logo/main_a_transparent.png' alt='EARLYSHINE'></div>"
            f"<div class='body'><span class='label'>{label_text}</span><h1>{html.escape(title)}</h1><p>{html.escape(sub)}</p><div class='glass'><div class='capsules'>{caps}</div><div class='chips'>{chip_html}</div></div></div>"
            f"<div class='footer'><span>{html.escape(notes[idx-1])}</span><span>{no} / 07</span></div></section>"
        )
    sections.append(
        "<section class='card ending'><img src='../assets/logo/main_a_transparent.png' alt='EARLYSHINE'><div class='footer'><span></span><span>07 / 07</span></div></section>"
    )
    html_text = "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>뽑기방이 인기있는 이유 카드뉴스</title><style>" + css + "</style></head><body><main>" + "\n".join(sections) + "</main></body></html>"
    (OUT / f"{SLUG}-cardnews.html").write_text(html_text, encoding="utf-8")


def write_summary():
    summary = f"""# Packaging Summary: 뽑기방이 인기있는 이유 카드뉴스 2026

결론:
1. HTML, PDF, PNG 7장, 렌더 확인 이미지를 생성했다.
2. 본문 6장은 Hook, Experience, Domestic, Global, Guardrail, Takeaway 흐름으로 구성했고 7장은 EARLYSHINE 로고 엔딩으로 마감했다.
3. 사진 대신 코드 기반 캡슐·유리·집게·데이터 라인워크를 사용해 IP/캐릭터 모사 리스크를 낮췄다.

산출물:
- HTML: `output/{SLUG}-cardnews.html`
- PDF: `output/{SLUG}-cardnews.pdf`
- PNG: `output/cards/{SLUG}-card-01.png` ~ `output/cards/{SLUG}-card-07.png`
- 렌더 확인 이미지: `output/{SLUG}-render-check.png`

에이전트 진행:
- research / Anscombe: 국내외 근거 수집 완료
- analysis / Hume: 핵심 프레임 확정 완료
- writing-outline / Volta: `output/writing-outline-arendt.md`
- design / McClintock: `output/design-claw-machine-popularity-2026.md`
- writing / Kepler: `output/writing-claw-machine-popularity-2026.md`
- image / Hegel: 코드네이티브 라인워크 권장, PNG/JPG 불필요
- packaging / team-lead 대체: 구현 및 출력 완료

QA:
- 모든 PNG는 1080 x 1350으로 생성했다.
- 본문 6장 우상단에 실제 `assets/logo/main_a_transparent.png`를 삽입했다.
- 엔딩 카드 중앙에도 실제 로고를 삽입했다.
- 중독, 도박, 조작 단정, 매출 보장 표현은 제외했다.
- 해외 사례는 국내 시장과 직접 동일시하지 않는다는 주의 문구를 넣었다.
- 추가 시각 QA에서 카드 04의 패널 경계 침범을 발견해 브리지 라벨과 아이콘 좌표를 재정리했고, 최종 PDF/PNG/렌더 체크를 다시 생성했다.
- `output/design-review-claw-machine-room-2026.md` 기준 최종 통과.
"""
    (OUT / f"packaging-summary-{SLUG}.md").write_text(summary, encoding="utf-8")


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for fn in [card1, card2, card3, card4, card5, card6, card7]:
        fn(doc)
    pdf_path = OUT / f"{SLUG}-cardnews.pdf"
    doc.save(pdf_path)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        pix.save(CARDS / f"{SLUG}-card-{i:02d}.png")
    check = fitz.open()
    cp = check.new_page(width=W, height=H)
    install_fonts(cp)
    cp.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None)
    for idx in range(1, TOTAL + 1):
        col = (idx - 1) % 3
        row = (idx - 1) // 3
        x = 30 + col * 350
        y = 42 + row * 430
        thumb = rect(x, y, 320, 400)
        cp.insert_image(thumb, filename=str(CARDS / f"{SLUG}-card-{idx:02d}.png"))
        text(cp, rect(x, y + 405, 320, 24), f"{idx:02d} / {TOTAL:02d}", 13, TAN, "PretBold", align=1)
    cpix = cp.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    cpix.save(OUT / f"{SLUG}-render-check.png")
    check.close()
    doc.close()
    write_html()
    write_summary()
    print(f"wrote {pdf_path}")
    print("wrote 7 PNG cards")
    print(f"wrote {SLUG}-cardnews.html")
    print(f"wrote packaging-summary-{SLUG}.md")


if __name__ == "__main__":
    main()
