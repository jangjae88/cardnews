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


def rect(x, y, w, h):
    return fitz.Rect(x, y, x + w, y + h)


def center_rect(width, height, y):
    return rect((W - width) / 2, y, width, height)


def install_fonts(page):
    page.insert_font(fontname="PretBlack", fontfile=str(FONT_BLACK))
    page.insert_font(fontname="PretBold", fontfile=str(FONT_BOLD))
    page.insert_font(fontname="Pret", fontfile=str(FONT_REG))


def text(page, box, value, size, color=INK, font="Pret", align=0, lineheight=1.12):
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
    page.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None)
    page.draw_rect(rect(58, 1226, 964, 1), fill=c(LINE), color=None, fill_opacity=0.9)
    for y in [318, 640, 962]:
        page.draw_line((58, y), (1022, y), color=c(LINE), width=0.7, stroke_opacity=0.18)
    for x in [58, 1022]:
        page.draw_line((x, 128), (x, 1178), color=c(LINE), width=0.7, stroke_opacity=0.18)


def top(page, no, label):
    page.draw_rect(rect(56, 54, 44, 44), color=c(TAN), width=1)
    text(page, rect(56, 64, 44, 28), f"{no:02d}", 15, TAN, "PretBlack", align=1)
    text(page, rect(112, 59, 540, 34), label, 16, TAN, "PretBold")
    page.insert_image(rect(760, 57, 262, 32), filename=str(LOGO), keep_proportion=True)


def footer(page, note, no):
    text(page, rect(58, 1244, 778, 42), note, 13.6, MUTED, "Pret", lineheight=1.08)
    text(page, rect(930, 1244, 92, 42), f"{no:02d} / {TOTAL:02d}", 15, MUTED, "PretBold", align=2)


def panel(page, r, fill=PANEL, stroke=LINE, width=1, opacity=1):
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=width, fill_opacity=opacity)


def headline(page, lines, x=58, y=236, size=72, gap=0.95):
    cursor = y
    for line in lines:
        text_at(page, x, cursor, line, size, INK, "PretBlack")
        cursor += size * gap
    return cursor


def label(page, value, x=58, y=146):
    text(page, rect(x, y, 520, 34), value, 15, TAN, "PretBold")


def stat_box(page, x, y, w, h, value, title, desc, accent=TAN):
    panel(page, rect(x, y, w, h), fill=PANEL_2, stroke=LINE)
    text(page, rect(x + 24, y + 24, w - 48, 28), title, 17, MUTED, "PretBold")
    metric_number(page, x + 24, y + 104, value, 54, accent)
    text(page, rect(x + 24, y + 132, w - 48, 72), desc, 18, INK, "PretBold", lineheight=1.16)


def metric_number(page, x, y, value, size, color=INK, unit=None):
    if value.endswith("%"):
        number = value[:-1]
        text_at(page, x, y, number, size, color, "PretBlack")
        if unit:
            unit_x = x + max(74, len(number) * size * 0.48)
            text_at(page, unit_x, y - size * 0.06, unit, max(13, size * 0.28), color, "PretBold")
        return
    text_at(page, x, y, value, size, color, "PretBlack")


def bar_row(page, x, y, label_text, value, max_value=25, width=560, color=TAN, note=""):
    text(page, rect(x, y - 2, 158, 34), label_text, 22, INK, "PretBlack")
    page.draw_rect(rect(x + 170, y + 4, width, 22), fill=c(PANEL_2), color=c(LINE), width=1)
    page.draw_rect(rect(x + 170, y + 4, width * value / max_value, 22), fill=c(color), color=None)
    text(page, rect(x + 748, y - 2, 110, 34), f"{value:.1f}", 21, color, "PretBold", align=2)
    if note:
        text(page, rect(x + 170, y + 36, 640, 28), note, 14, MUTED, "Pret")


def compare_metric(page, x, y, value, title, desc, color=TAN):
    panel(page, rect(x, y, 438, 116), fill=PANEL_2)
    metric_number(page, x + 22, y + 66, value, 46, color)
    text(page, rect(x + 162, y + 28, 238, 28), title, 21, INK, "PretBlack")
    text(page, rect(x + 162, y + 62, 238, 38), desc, 16, MUTED, "Pret", lineheight=1.12)


def card1(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 1, "STOCK PERCEPTION 2026")
    label(p, "TREND FRAME")
    end = headline(p, ["2030은 주식을", "안 하는 세대가", "아니다"], y=248, size=76)
    text(
        p,
        rect(58, end + 26, 780, 98),
        "더 빨리 시작하고, 더 넓게 보고, 더 불안하게 판단하는 세대다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    stat_box(p, 58, 760, 300, 240, "1,456만", "상장주식 소유자", "2025년 말 기준, 국내 주식 보유자는 역대 최대권.", TAN)
    stat_box(p, 390, 760, 300, 240, "약 28", "2030 개인 주주", "20대와 30대는 개인 주주 수의 의미 있는 비중.", ORANGE)
    stat_box(p, 722, 760, 300, 240, "60.0%", "20대 해외 ETP", "보유금액 기준, 국내주식보다 해외 ETP 비중이 큼.", TAN)
    panel(p, rect(58, 1080, 964, 88), fill=BASE, stroke=TAN_DEEP)
    text(
        p,
        rect(88, 1102, 904, 40),
        "핵심은 열풍이 아니라 구조다: 참여, 선호, 정보 경로, 리스크를 따로 봐야 한다.",
        22,
        INK,
        "PretBold",
        align=1,
    )
    footer(p, "출처: 한국예탁결제원 보도 인용, 트렌드모니터 2026, 자본시장연구원 2026. 투자 권유 아님.", 1)


def card2(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 2, "PARTICIPATION")
    label(p, "WHO HOLDS K-STOCKS")
    end = headline(p, ["국장은 아직", "4050이 크다"], y=238, size=76)
    text(
        p,
        rect(58, end + 22, 760, 78),
        "그래도 30대는 개인 주주 수 기준 세 번째 축이다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    data = [
        ("50대", 23.1, TAN),
        ("40대", 21.8, TAN_DEEP),
        ("30대", 19.1, ORANGE),
        ("60대", 15.3, TAN_DEEP),
        ("20대", 8.8, ORANGE),
        ("70대", 5.5, MUTED),
        ("20대 미만", 5.3, MUTED),
    ]
    panel(p, rect(58, 585, 964, 540), fill=PANEL)
    text(p, rect(88, 620, 872, 36), "개인 주주 연령대별 비중", 28, INK, "PretBlack")
    text(p, rect(88, 660, 872, 30), "2025년 말 상장법인 주식 소유자 현황 보도 기준, 단위: 퍼센트", 17, MUTED, "Pret")
    y = 735
    for name, value, color in data:
        bar_row(p, 110, y, name, value, max_value=25, width=560, color=color)
        y += 58
    footer(p, "출처: 한국예탁결제원 2025년 12월 결산 상장법인 주식 소유자 현황 보도 인용.", 2)


def card3(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 3, "PERCEPTION")
    label(p, "EXPECTATION VS GUARDRAIL")
    end = headline(p, ["돈은 벌고 싶지만", "시장을 다 믿진", "않는다"], y=226, size=72)
    text(
        p,
        rect(58, end + 18, 740, 76),
        "2026년 투자 심리는 기대와 경계가 같은 화면에 뜬다. 단위는 퍼센트다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    panel(p, rect(58, 600, 964, 548), fill=PANEL, stroke=LINE)
    text(p, rect(88, 632, 360, 28), "응답 비율, 단위: 퍼센트", 18, MUTED, "PretBold")
    text_at(p, 88, 704, "기대", 38, TAN, "PretBlack")
    text_at(p, 588, 704, "경계", 38, WARN, "PretBlack")
    p.draw_line((540, 664), (540, 1068), color=c(LINE), width=1.1, stroke_opacity=0.65)

    left_rows = [
        ("49.0", "20대", "다양한 투자로\n자산 증식"),
        ("54.5", "30대", "다양한 투자로\n자산 증식"),
        ("76.4", "주식 의향", "여윳돈이 생기면\n주식 투자"),
    ]
    right_rows = [
        ("62.8", "체감 격차", "주식은 돈 있는 사람의\n경제활동"),
        ("50.2", "과열 인식", "시장 활성화가\n과열을 조장"),
        ("35.6", "기회 인식", "누구나 돈 벌 기회라는\n응답"),
    ]

    def survey_row(x, y, value, title, desc, color):
        panel(p, rect(x, y, 424, 96), fill=PANEL_2, stroke=LINE)
        text_at(p, x + 24, y + 63, value, 43, color, "PretBlack")
        text_at(p, x + 154, y + 38, title, 21, INK, "PretBlack")
        text(p, rect(x + 154, y + 48, 230, 44), desc, 16, MUTED, "PretBold", lineheight=1.1)

    for idx, row in enumerate(left_rows):
        survey_row(84, 742 + idx * 112, *row, TAN)
    for idx, row in enumerate(right_rows):
        survey_row(584, 742 + idx * 112, *row, WARN)

    panel(p, rect(84, 1092, 912, 54), fill=BASE, stroke=TAN_DEEP)
    text(
        p,
        rect(110, 1108, 860, 26),
        "읽는 법: 참여 의향은 높지만, 주식 시장을 완전히 신뢰하지는 않는다.",
        19,
        INK,
        "PretBold",
        align=1,
    )
    footer(p, "출처: 엠브레인 트렌드모니터, 2026 투자 전망 및 돈에 대한 인식 조사, 표본 1,000명.", 3)


def stack_bar(page, x, y, title, items, note):
    panel(page, rect(x, y, 900, 150), fill=PANEL_2)
    text(page, rect(x + 24, y + 24, 210, 36), title, 25, INK, "PretBlack")
    bar_x = x + 260
    bar_y = y + 38
    bar_w = 560
    page.draw_rect(rect(bar_x, bar_y, bar_w, 32), fill=c(BASE), color=c(LINE), width=1)
    cursor = bar_x
    for name, value, color in items:
        seg_w = bar_w * value / 100
        page.draw_rect(rect(cursor, bar_y, seg_w, 32), fill=c(color), color=None)
        if seg_w > 60:
            text(page, rect(cursor, bar_y + 6, seg_w, 24), f"{value:.1f}", 14, BASE, "PretBlack", align=1)
        cursor += seg_w
    text(page, rect(bar_x, y + 86, bar_w, 26), note, 15, MUTED, "Pret")
    lx = bar_x
    for name, value, color in items:
        page.draw_rect(rect(lx, y + 116, 12, 12), fill=c(color), color=None)
        text(page, rect(lx + 18, y + 109, 160, 24), name, 13, INK, "PretBold")
        lx += 170


def card4(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 4, "PORTFOLIO")
    label(p, "DOMESTIC VS OVERSEAS")
    end = headline(p, ["2030의 화면은", "국장 밖까지", "열려 있다"], y=226, size=72)
    text(
        p,
        rect(58, end + 18, 760, 76),
        "해외 ETF/ETP는 젊은 투자자의 기본 선택지에 가까워졌다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    stack_bar(
        p,
        90,
        610,
        "20대",
        [("해외 ETP", 60.0, ORANGE), ("국내주식", 30.8, TAN), ("기타", 9.2, MUTED)],
        "보유금액 기준: 해외 ETP가 국내주식의 거의 두 배.",
    )
    stack_bar(
        p,
        90,
        800,
        "30대",
        [("해외 ETP", 45.5, ORANGE), ("그 외", 54.5, TAN_DEEP)],
        "30대도 해외 ETP 비중이 높게 나타남.",
    )
    stack_bar(
        p,
        90,
        990,
        "60대",
        [("국내주식", 77.0, TAN), ("해외 ETP", 12.8, ORANGE), ("기타", 10.2, MUTED)],
        "연령대가 높을수록 국내주식 비중이 높아짐.",
    )
    footer(p, "출처: 자본시장연구원 2026 보고서 및 연합뉴스 보도. 계좌 분석 기간은 2020-2022년.", 4)


def card5(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 5, "CHANNEL RISK")
    label(p, "INFORMATION PATH")
    end = headline(p, ["공부는 빨라졌지만", "검증은 느릴 수", "있다"], y=226, size=72)
    text(
        p,
        rect(58, end + 18, 790, 78),
        "유튜브, SNS, 커뮤니티는 입문 장벽을 낮추지만 FOMO와 과신도 같이 키운다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    text(p, rect(70, 610, 500, 34), "콘텐츠가 투자 행동으로 이어지는 짧은 경로", 22, TAN, "PretBlack")
    steps = [("수익 인증", "성과 노출"), ("영상/요약", "빠른 학습"), ("커뮤니티", "신뢰 형성"), ("매수 버튼", "즉시 실행")]
    xs = [70, 320, 570, 820]
    for idx, ((head, desc), x) in enumerate(zip(steps, xs), start=1):
        panel(p, rect(x, 660, 190, 128), fill=PANEL_2)
        text(p, rect(x + 20, 686, 42, 30), f"0{idx}", 18, TAN, "PretBlack")
        text(p, rect(x + 62, 682, 108, 32), head, 22, INK, "PretBlack")
        text(p, rect(x + 62, 724, 108, 28), desc, 16, MUTED, "PretBold")
    for x in [268, 518, 768]:
        p.draw_line((x, 724), (x + 42, 724), color=c(TAN), width=1.8)
        p.draw_polyline([(x + 42, 724), (x + 30, 716), (x + 30, 732)], color=c(TAN), width=1.8)

    panel(p, rect(70, 845, 452, 230), fill=PANEL)
    text(p, rect(100, 880, 390, 30), "국내에서 보이는 신호 / 응답 비율", 22, TAN, "PretBlack")
    metric_number(p, 100, 966, "22.0%", 62, ORANGE)
    text(p, rect(100, 990, 360, 58), "20대는 SNS 수익 인증에 더 쉽게 자극받는다.", 19, INK, "PretBlack", lineheight=1.12)
    text(p, rect(100, 1050, 360, 34), "숫자는 관심 유입의 신호이지, 매수 근거가 아니다.", 16, MUTED, "PretBold")

    panel(p, rect(558, 845, 452, 230), fill=PANEL)
    text(p, rect(588, 880, 390, 30), "해외에서 보이는 경고 / 응답 비율", 22, TAN, "PretBlack")
    metric_number(p, 588, 966, "61.0%", 62, WARN)
    text(p, rect(588, 990, 360, 58), "35세 미만 투자자는 핀플루언서 추천을 실제 결정에 쓴다.", 19, INK, "PretBlack", lineheight=1.12)
    text(p, rect(588, 1050, 360, 34), "해외 수치는 국내 일반화보다 위험 구조를 보는 용도다.", 16, MUTED, "PretBold")

    panel(p, rect(70, 1115, 940, 70), fill=BASE, stroke=TAN_DEEP)
    text(p, rect(100, 1134, 880, 30), "검수 질문: 출처가 보이나? 손실도 말하나? 상품 구조를 설명하나?", 20, INK, "PretBold", align=1)
    footer(p, "출처: 오픈서베이 2026, FINRA Foundation 2025-2026. 해외 수치는 국내 일반화 금지.", 5)


def card6(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 6, "CHECKLIST")
    label(p, "SAVE THIS")
    end = headline(p, ["2030 주식 콘텐츠는", "검증 구조가", "먼저다"], y=226, size=72)
    text(
        p,
        rect(58, end + 18, 780, 76),
        "숫자보다 먼저 봐야 할 6가지. 수익보다 근거가 먼저다.",
        27,
        MUTED,
        "Pret",
        lineheight=1.22,
    )
    items = [
        ("출처 날짜", "언제 나온 자료인지 먼저 확인"),
        ("표본 대상", "전체 2030인지, 투자 경험자인지 구분"),
        ("국내·해외", "국장, 미장, ETF, ETP를 섞지 않기"),
        ("손실 표기", "수익률 옆에 변동성과 손실도 같이"),
        ("상품 구조", "레버리지·인버스·환율 노출 확인"),
        ("확정 표현 금지", "오른다, 벌 수 있다, 안전하다 금지"),
    ]
    for i, (head, desc) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 58 + col * 500
        y = 635 + row * 168
        panel(p, rect(x, y, 464, 138), fill=PANEL_2)
        p.draw_rect(rect(x + 26, y + 30, 28, 28), color=c(TAN), width=1.4)
        p.draw_line((x + 32, y + 44), (x + 40, y + 54), color=c(ORANGE), width=2)
        p.draw_line((x + 40, y + 54), (x + 56, y + 34), color=c(ORANGE), width=2)
        text(p, rect(x + 78, y + 26, 330, 32), head, 28, INK, "PretBlack")
        text(p, rect(x + 78, y + 72, 330, 42), desc, 18, MUTED, "Pret", lineheight=1.14)
    panel(p, rect(210, 1150, 660, 44), fill=BASE, stroke=TAN_DEEP)
    text(p, rect(210, 1161, 660, 26), "투자 판단은 개인 책임. 콘텐츠는 판단을 돕는 구조여야 한다.", 17, TAN, "PretBold", align=1)
    footer(p, "체크리스트는 카드뉴스 제작·검토용 기준이며 투자 자문이 아닙니다.", 6)


def card7(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    p.insert_image(center_rect(760, 90, 592), filename=str(LOGO), keep_proportion=True)
    text(p, rect(58, 738, 964, 42), "MARKET TREND CARDNEWS", 18, TAN, "PretBold", align=1)
    text(p, rect(58, 1244, 760, 42), "숫자보다 먼저 구조를 봅니다.", 14, MUTED, "Pret")
    text(p, rect(930, 1244, 92, 42), "07 / 07", 15, MUTED, "PretBold", align=2)


HTML_CARDS = [
    ("01", "STOCK PERCEPTION 2026", "2030은 주식을<br>안 하는 세대가<br>아니다", "더 빨리 시작하고, 더 넓게 보고, 더 불안하게 판단하는 세대다.", ["1,456만 주주", "2030 약 28%", "20대 해외 ETP 60%"]),
    ("02", "PARTICIPATION", "국장은 아직<br>4050이 크다", "그래도 30대는 개인 주주 수 기준 세 번째 축이다.", ["50대 23.1%", "40대 21.8%", "30대 19.1%", "20대 8.8%"]),
    ("03", "PERCEPTION", "돈은 벌고 싶지만<br>시장을 다 믿진 않는다", "투자 의향과 과열 경계가 같은 화면에 뜬다.", ["20대 49.0%", "30대 54.5%", "주식 의향 76.4%", "과열 인식 50.2%"]),
    ("04", "PORTFOLIO", "2030의 화면은<br>국장 밖까지<br>열려 있다", "해외 ETF/ETP는 젊은 투자자의 기본 선택지에 가까워졌다.", ["20대 해외 ETP 60.0%", "20대 국내주식 30.8%", "30대 해외 ETP 45.5%"]),
    ("05", "CHANNEL RISK", "공부는 빨라졌지만<br>검증은 느릴 수 있다", "유튜브, SNS, 커뮤니티는 입문 장벽을 낮추지만 FOMO와 과신도 같이 키운다.", ["수익 인증", "영상/요약", "커뮤니티", "매수 버튼"]),
    ("06", "CHECKLIST", "2030 주식 콘텐츠는<br>검증 구조가<br>먼저다", "숫자보다 먼저 봐야 할 6가지. 수익보다 근거가 먼저다.", ["출처 날짜", "표본 대상", "국내·해외", "손실 표기", "상품 구조", "확정 표현 금지"]),
]


def write_html():
    css = f"""
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Regular.otf'); }}
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Bold.otf'); font-weight: 700; }}
    @font-face {{ font-family: Pret; src: url('fonts/Pretendard-Black.otf'); font-weight: 900; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #211713; font-family: Pret, sans-serif; color: {INK}; }}
    main {{ display: grid; gap: 28px; justify-content: center; padding: 28px; }}
    .card {{ position: relative; width: 1080px; height: 1350px; overflow: hidden; background: {BASE}; padding: 58px; }}
    .card::before {{ content: ""; position: absolute; inset: 128px 58px 124px; border-left: 1px solid rgba(81,69,51,.3); border-right: 1px solid rgba(81,69,51,.3); pointer-events: none; }}
    .top {{ position: relative; display: flex; justify-content: space-between; align-items: center; z-index: 2; }}
    .kicker {{ color: {TAN}; font-weight: 800; letter-spacing: .16em; font-size: 16px; }}
    .kicker b {{ display: inline-flex; width: 44px; height: 44px; border: 1px solid {TAN}; align-items: center; justify-content: center; margin-right: 12px; letter-spacing: 0; }}
    .logo {{ width: 262px; height: auto; }}
    .body {{ position: relative; z-index: 2; margin-top: 78px; }}
    .label {{ color: {TAN}; font-size: 15px; font-weight: 800; letter-spacing: .22em; }}
    h1 {{ margin: 48px 0 34px; font-size: 74px; line-height: .98; letter-spacing: 0; max-width: 850px; }}
    p {{ color: {MUTED}; font-size: 27px; line-height: 1.35; max-width: 760px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 70px; max-width: 880px; }}
    .chip {{ border: 1px solid {LINE}; background: {PANEL}; padding: 14px 20px; font-size: 21px; font-weight: 800; color: {INK}; }}
    .footer {{ position: absolute; left: 58px; right: 58px; bottom: 78px; padding-top: 18px; border-top: 1px solid {LINE}; display: flex; justify-content: space-between; color: {MUTED}; font-size: 14px; z-index: 2; }}
    .ending {{ display: flex; align-items: center; justify-content: center; flex-direction: column; }}
    .ending img {{ width: 760px; }}
    .ending small {{ margin-top: 48px; color: {TAN}; letter-spacing: .24em; font-weight: 800; }}
    @page {{ size: 1080px 1350px; margin: 0; }}
    @media print {{ main {{ padding: 0; gap: 0; }} .card {{ break-after: page; }} }}
    """
    notes = [
        "출처: 한국예탁결제원 보도 인용, 트렌드모니터 2026, 자본시장연구원 2026. 투자 권유 아님.",
        "출처: 한국예탁결제원 2025년 12월 결산 상장법인 주식 소유자 현황 보도 인용.",
        "출처: 엠브레인 트렌드모니터, 2026 투자 전망 및 돈에 대한 인식 조사, n=1,000.",
        "출처: 자본시장연구원 2026 보고서 및 연합뉴스 보도. 계좌 분석 기간은 2020~2022년.",
        "출처: 오픈서베이 2026, FINRA Foundation 2025~2026. 해외 수치는 국내 일반화 금지.",
        "체크리스트는 카드뉴스 제작·검토용 기준이며 투자 자문이 아닙니다.",
    ]
    sections = []
    for idx, (no, label_text, title, sub, chips) in enumerate(HTML_CARDS, start=1):
        chip_html = "".join(f"<span class='chip'>{html.escape(ch)}</span>" for ch in chips)
        sections.append(
            f"""<section class="card"><div class="top"><span class="kicker"><b>{no}</b>{label_text}</span><img class="logo" src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"></div><div class="body"><span class="label">{label_text}</span><h1>{title}</h1><p>{html.escape(sub)}</p><div class="chips">{chip_html}</div></div><div class="footer"><span>{html.escape(notes[idx - 1])}</span><span>{no} / 07</span></div></section>"""
        )
    sections.append(
        """<section class="card ending"><img src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"><small>MARKET TREND CARDNEWS</small><div class="footer"><span>숫자보다 먼저 구조를 봅니다.</span><span>07 / 07</span></div></section>"""
    )
    html_text = "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>20~30대 주식 인식 및 참가실태 2026ver.</title><style>" + css + "</style></head><body><main>" + "\n".join(sections) + "</main></body></html>"
    (OUT / "stock-2030-2026-cardnews.html").write_text(html_text, encoding="utf-8")


def write_summary(pdf_filename="stock-2030-2026-cardnews.pdf"):
    summary = f"""# Packaging Summary: 20~30대 주식 인식 및 참가실태 2026ver.

결론:
1. 1080x1350 카드뉴스 PNG 7장, PDF, HTML, 렌더 체크 이미지를 생성했다.
2. 패키징 이후 `design-review` 서브에이전트가 P0/P1/P2 검수를 수행했고, 카드 5와 숫자 폰트 문제를 수정 반영했다.
3. 사용자의 요청대로 별도 장식 이미지 없이 숫자·막대·비교표·체크리스트 중심의 깔끔한 리포트형 스타일로 구현했다.

하위 에이전트 상태:
- [research / Rawls] 오류: 컨텍스트 초과 → team-lead가 국내 리서치 대체
- [overseas / Mendel] 완료: 미국·영국·일본 비교 축 제공
- [design / Nietzsche] 완료: 로고/7장 구조/PyMuPDF 패턴 확인
- [design-review / Dewey] 완료: 패키징 이후 디자인 검수 리포트 작성

산출물:
- HTML: `output/stock-2030-2026-cardnews.html`
- PDF: `output/{pdf_filename}`
- PNG: `output/cards/stock-2030-2026-card-01.png` ~ `output/cards/stock-2030-2026-card-07.png`
- 렌더 체크: `output/stock-2030-2026-render-check.png`
- 디자인 검수: `output/design-review-stock-2030-2026.md`
- 수정 반영 기록: `output/design-review-resolution-stock-2030-2026.md`
- 리서치: `output/research-stock-2030-2026.md`
- 분석: `output/analysis-stock-2030-2026.md`
- 구성: `output/writing-outline-stock-2030-2026.md`
- 디자인: `output/design-stock-2030-2026.md`
- 최종 문구: `output/writing-stock-2030-2026.md`

QA:
- 실제 EARLYSHINE 투명 로고 이미지를 모든 본문 카드 우상단과 엔딩 카드 중앙에 삽입했다.
- 총 7장을 PDF와 PNG에 모두 포함했다.
- 사진, 캐릭터, 오브, 블롭, 장식용 배경 패턴은 사용하지 않았다.
- 수익 보장 표현과 과장된 상승 표현은 제외했다.
- 주요 수치에는 출처 또는 기준 조사를 푸터로 표기했다.
- 카드 5는 `숫자만 있는 패널`에서 `정보 경로 + 국내 신호 + 해외 경고 + 검수 질문` 구조로 재설계했다.
- 큰 퍼센트 숫자는 `%` 기호 대신 차트/패널 제목에 단위를 올려 폰트 혼선을 줄였다.
"""
    (OUT / "packaging-summary-stock-2030-2026.md").write_text(summary, encoding="utf-8")
    (OUT / "packaging-summary.md").write_text(summary, encoding="utf-8")


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for fn in [card1, card2, card3, card4, card5, card6, card7]:
        fn(doc)

    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        pix.save(CARDS / f"stock-2030-2026-card-{i:02d}.png")

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
        cp.insert_image(thumb, filename=str(CARDS / f"stock-2030-2026-card-{idx:02d}.png"))
        text(cp, rect(x, y + 405, 320, 24), f"{idx:02d} / {TOTAL:02d}", 13, TAN, "PretBold", align=1)
    cpix = cp.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    cpix.save(OUT / "stock-2030-2026-render-check.png")
    check.close()

    pdf_path = OUT / "stock-2030-2026-cardnews.pdf"
    try:
        doc.save(pdf_path)
    except Exception:
        pdf_path = OUT / "stock-2030-2026-cardnews-design-reviewed.pdf"
        doc.save(pdf_path)
    doc.close()

    write_html()
    write_summary(pdf_path.name)
    print(f"wrote {pdf_path}")
    print("wrote 7 PNG cards")
    print("wrote stock-2030-2026-cardnews.html")
    print("wrote packaging summaries")


if __name__ == "__main__":
    main()
