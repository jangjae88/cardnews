import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".deps" / "pymupdf"))

import fitz  # noqa: E402


W, H = 1080, 1350
OUT = ROOT / "output"
CARDS = OUT / "cards"
PHOTOS = OUT / "photos"
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
LINE = "#514533"
WARN = "#C36A5C"

FONT_BLACK = FONTS / "Pretendard-Black.otf"
FONT_BOLD = FONTS / "Pretendard-Bold.otf"
FONT_REG = FONTS / "Pretendard-Regular.otf"


def c(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def rect(x, y, w, h):
    return fitz.Rect(x, y, x + w, y + h)


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
    page.draw_rect(rect(0, 0, W, H), fill=c("#120F0B"), color=None, fill_opacity=0.28)
    for y in [338, 642, 946]:
        page.draw_line((58, y), (1022, y - 96), color=c(LINE), width=0.8, stroke_opacity=0.28)
    page.draw_line((58, 1225), (1022, 1225), color=c(LINE), width=1)


def top(page, no, label):
    page.draw_circle((78, 76), 22, color=c(TAN), width=1)
    text(page, rect(62, 59, 32, 34), f"{no:02d}", 15, TAN, "PretBlack", align=1)
    text(page, rect(112, 59, 520, 34), label, 16, TAN, "PretBold")
    page.insert_image(rect(760, 57, 262, 32), filename=str(LOGO), keep_proportion=True)


def footer(page, note, no):
    text(page, rect(58, 1244, 770, 42), note, 14, MUTED, "Pret")
    text(page, rect(930, 1244, 92, 42), f"{no:02d} / {TOTAL:02d}", 15, MUTED, "PretBold", align=2)


def panel(page, r, fill=PANEL, stroke=LINE, width=1):
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=width)


def pill(page, x, y, label, width, fill=PANEL, color=INK, stroke=LINE, size=18):
    r = rect(x, y, width, 42)
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=1)
    text(page, rect(x, y + 8, width, 30), label, size, color, "PretBold", align=1)


def image_panel(page, filename, r, label, opacity=0.16, pos_label=True):
    page.draw_rect(r, fill=c(PANEL), color=c(TAN_DEEP), width=1)
    page.insert_image(r, filename=str(PHOTOS / filename), keep_proportion=False)
    page.draw_rect(r, fill=c(BASE), color=None, fill_opacity=opacity)
    if pos_label:
        lab = rect(r.x0 + 18, r.y1 - 56, 290, 38)
        page.draw_rect(lab, fill=c(BASE), color=c(LINE), width=1, fill_opacity=0.88)
        text(page, lab + (0, 8, 0, 0), label, 14, TAN, "PretBold", align=1)


def title_block(page, kicker, title, sub, x=58, y=144, w=650, title_size=74):
    text(page, rect(x, y, 430, 36), kicker, 15, TAN, "PretBold")
    baseline = y + 124
    for line in title.split("\n"):
        text_at(page, x, baseline, line, title_size, INK, "PretBlack")
        baseline += title_size * 0.95
    text(page, rect(x, baseline + 32, min(w, 650), 100), sub, 27, MUTED, "Pret", lineheight=1.24)


def card1(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    image_panel(p, "running-korea-2026-night.png", rect(0, 0, W, H), "", opacity=0.58, pos_label=False)
    p.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None, fill_opacity=0.18)
    top(p, 1, "RUNNING KOREA 2026")
    title_block(
        p,
        "TREND FRAME",
        "러닝은\n무료지만\n길목엔 시장이\n붙는다",
        "러닝크루, 대회, 앱, 매장, 회복제품이\n러너의 하루 동선 안으로 들어옵니다.",
        w=690,
        title_size=78,
    )
    points = [
        (132, 830, "러닝크루"),
        (305, 760, "대회"),
        (478, 830, "앱"),
        (650, 760, "매장"),
        (820, 830, "회복제품"),
    ]
    path = [(90, 980), (220, 835), (390, 900), (540, 790), (720, 910), (940, 760)]
    for a, b in zip(path, path[1:]):
        p.draw_line(a, b, color=c(TAN), width=3)
    for x, y, label in points:
        p.draw_circle((x, y), 30, fill=c(ORANGE), color=c(TAN), width=1, fill_opacity=0.35)
        pill(p, x - 70, y + 42, label, 140, fill=PANEL_2, color=INK, size=17)
    panel(p, rect(58, 1070, 520, 82), fill="#0F0E0C")
    text_at(p, 84, 1104, "핵심은 러닝 인구 숫자가 아니라", 20, INK, "PretBold")
    text_at(p, 84, 1132, "반복되는 동선에서 생기는 접점입니다.", 20, INK, "PretBold")
    footer(p, "프레임 카드입니다. 공식 확인이 어려운 러닝 인구·시장 규모 추정치는 제외했습니다.", 1)


def card2(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 2, "CULTURE")
    title_block(
        p,
        "CULTURE SHIFT",
        "혼자 뛰던\n러닝이\n모이는 경험이\n됐다",
        "생활체육 안으로 들어온 러닝크루와\n대회 접수 경쟁이 참여 경험을 키웁니다.",
        w=610,
        title_size=74,
    )
    image_panel(p, "running-korea-2026-crew.png", rect(662, 145, 360, 520), "AI 생성 이미지 / 러닝크루", opacity=0.1)
    items = [
        ("생활체육", "참여율 62.9퍼센트"),
        ("러닝크루", "봄철 생활체육"),
        ("대회 접수", "참가 경험 자체"),
        ("참여 문화", "함께 뛰는 이유"),
    ]
    for i, (head, desc) in enumerate(items):
        x = 58 + (i % 2) * 300
        y = 720 + (i // 2) * 176
        panel(p, rect(x, y, 276, 140))
        text(p, rect(x + 22, y + 24, 230, 40), head, 30, INK, "PretBlack")
        text(p, rect(x + 22, y + 78, 230, 34), desc, 22, TAN, "PretBold")
    panel(p, rect(662, 724, 360, 312), fill=PANEL_2)
    text(p, rect(690, 750, 310, 42), "확인된 근거 칩", 24, TAN, "PretBlack")
    for i, stat in enumerate(["생활체육 참여율 62.9퍼센트", "전년 대비 2.2p 상승", "JTBC 서울마라톤 30,000명", "대구마라톤 약 41,254명"]):
        pill(p, 690, 820 + i * 50, stat, 292, fill=BASE, color=INK, size=16)
    footer(p, "출처: 정책브리핑 2025 국민생활체육조사, JTBC 서울마라톤, 스포츠Q 대구마라톤 보도.", 2)


def card3(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 3, "PLATFORM")
    title_block(
        p,
        "PLATFORM",
        "기록은\n러너의\n소속감 카드가\n된다",
        "운동 로그가 접수, 인증, 커뮤니티를 잇는\n작은 신분증처럼 쓰이기 시작했습니다.",
        w=720,
        title_size=76,
    )
    steps = [
        ("러닝 기록", "뛰었다는 데이터"),
        ("디지털 카드", "보여줄 수 있는 인증"),
        ("접수/인증", "대회와 연결"),
        ("커뮤니티", "다음 참여 이유"),
    ]
    xs = [82, 325, 568, 811]
    for i, ((head, desc), x) in enumerate(zip(steps, xs)):
        panel(p, rect(x, 720, 188, 230), fill=PANEL_2)
        p.draw_circle((x + 94, 770), 28, fill=c(ORANGE), color=c(TAN), width=1, fill_opacity=0.35)
        text(p, rect(x + 80, 753, 28, 34), str(i + 1), 18, TAN, "PretBlack", align=1)
        text(p, rect(x + 18, 828, 152, 38), head, 25, INK, "PretBlack", align=1)
        text(p, rect(x + 20, 882, 148, 44), desc, 16, MUTED, "Pret", align=1, lineheight=1.2)
    for x in [276, 519, 762]:
        p.draw_line((x, 832), (x + 42, 832), color=c(TAN), width=2)
        p.draw_polyline([(x + 42, 832), (x + 30, 824), (x + 30, 840)], color=c(TAN), fill=c(TAN))
    panel(p, rect(90, 1035, 900, 90), fill=BASE)
    text(p, rect(120, 1054, 840, 32), "카카오-러너블 러너스 카드, Runable 접수처럼", 20, INK, "PretBold", align=1)
    text(p, rect(120, 1084, 840, 32), "기록은 참여 경험을 이어주는 장치가 됩니다.", 20, INK, "PretBold", align=1)
    footer(p, "출처: TechM 카카오-러너블 러너스 카드, JTBC 서울마라톤 Runable 접수 안내.", 3)


def card4(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 4, "PLACE")
    title_block(
        p,
        "ROUTE COMMERCE",
        "러너가\n지나는 곳에\n거점이 생긴다",
        "피팅, 측정, 보관, 물·간식, 휴식, 러닝 모임이\n코스 주변 접점으로 붙고 있습니다.",
        w=690,
        title_size=76,
    )
    map_box = rect(70, 670, 940, 420)
    panel(p, map_box, fill=PANEL_2)
    route = [(130, 1005), (240, 820), (420, 890), (560, 740), (720, 850), (930, 710)]
    for a, b in zip(route, route[1:]):
        p.draw_line(a, b, color=c(TAN), width=4)
    nodes = [
        (130, 1005, "피팅"),
        (240, 820, "측정"),
        (420, 890, "보관"),
        (560, 740, "물·간식"),
        (720, 850, "휴식"),
        (930, 710, "러닝 모임"),
    ]
    for x, y, label in nodes:
        p.draw_circle((x, y), 24, fill=c(ORANGE), color=c(TAN), width=1, fill_opacity=0.36)
        pill(p, x - 58, y + 34, label, 116 if len(label) < 5 else 138, fill=BASE, size=15)
    panel(p, rect(70, 1122, 445, 70), fill=BASE)
    panel(p, rect(565, 1122, 445, 70), fill=BASE)
    text(p, rect(92, 1142, 400, 32), "더현대 러닝 클럽·러닝 전문 공간 흐름", 18, TAN, "PretBold", align=1)
    text(p, rect(587, 1142, 400, 32), "CU 한강 러닝 스테이션 컨셉", 18, TAN, "PretBold", align=1)
    footer(p, "출처: 이코노믹리뷰, 한경비즈니스, 어패럴뉴스. 모든 매장에 일반화하지 않았습니다.", 4)


def card5(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 5, "PRODUCT")
    image_panel(p, "running-korea-2026-products.png", rect(622, 140, 400, 370), "AI 생성 이미지 / 제품 플랫레이", opacity=0.08)
    title_block(
        p,
        "PRODUCT MAP",
        "러닝제품은\n전·중·후\n루틴으로\n쪼개진다",
        "러닝화 하나보다 준비, 기록, 보급,\n회복으로 카테고리가 나뉩니다.",
        w=520,
        title_size=70,
    )
    cols = [
        ("Before", "뛰기 전", ["러닝화 피팅", "의류", "양말", "조끼"]),
        ("During", "뛰는 중", ["웨어러블", "기록 앱", "수분 보급", "에너지 간식"]),
        ("After", "뛰고 난 뒤", ["리커버리 슈즈", "회복용품", "발 건강", "보급·영양"]),
    ]
    for i, (head, sub, rows) in enumerate(cols):
        x = 58 + i * 338
        panel(p, rect(x, 625, 302, 480), fill=PANEL_2)
        text(p, rect(x + 22, 652, 258, 40), head, 31, TAN if i != 1 else ORANGE, "PretBlack", align=1)
        text(p, rect(x + 22, 700, 258, 30), sub, 18, MUTED, "PretBold", align=1)
        for j, row in enumerate(rows):
            pill(p, x + 32, 770 + j * 70, row, 238, fill=BASE, color=INK, size=18)
    panel(p, rect(58, 1135, 964, 58), fill=BASE)
    text(p, rect(80, 1150, 920, 28), "핵심은 성능 보장이 아니라 러너가 어느 순간에 무엇을 찾는지 나누는 것입니다.", 18, TAN, "PretBold", align=1)
    footer(p, "특정 제품 효과, 부상 예방, 매출 전망을 보장하지 않습니다. 제품군 세분화 흐름만 반영했습니다.", 5)


def card6(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 6, "CHECKLIST")
    title_block(
        p,
        "SAVE CHECKLIST",
        "숫자보다\n먼저,\n러너 동선을\n보세요",
        "작은 브랜드와 로컬 매장은 러너가 어디서 모이고,\n뛰고, 쉬고, 다시 사는지를 봐야 합니다.",
        w=740,
        title_size=76,
    )
    left = ["크루가 모이는 장소인가", "뛰기 전후 들를 이유가 있는가", "기록·인증과 연결되는가", "작은 반복 구매가 가능한가"]
    right = ["장비 과열을 부추기지 않는가", "부상·안전을 과장하지 않는가", "확인 안 된 숫자를 쓰지 않는가"]
    for x, title, rows, color in [(58, "기회", left, TAN), (562, "주의", right, WARN)]:
        panel(p, rect(x, 650, 460, 430), fill=PANEL_2)
        text(p, rect(x + 28, 682, 390, 42), title, 34, color, "PretBlack")
        for i, row in enumerate(rows):
            y = 760 + i * 74
            p.draw_circle((x + 48, y + 14), 13, fill=c(ORANGE if title == "기회" else WARN), color=None, fill_opacity=0.6)
            text(p, rect(x + 78, y, 340, 36), row, 21, INK, "PretBold")
    pill(p, 362, 1128, "RUNNER ROUTE CHECK", 356, fill=BASE, color=TAN, size=19)
    footer(p, "성과 보장이나 창업 추천이 아니라, 러너 동선 점검 기준입니다.", 6)


def card7(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    p.insert_image(rect(160, 592, 760, 90), filename=str(LOGO), keep_proportion=True)
    text(p, rect(58, 738, 964, 42), "RUNNING TREND CARDNEWS", 18, TAN, "PretBold", align=1)
    text(p, rect(58, 1244, 760, 42), "러너의 동선을 보면 다음 소비 접점이 보입니다.", 14, MUTED, "Pret")
    text(p, rect(930, 1244, 92, 42), "07 / 07", 15, MUTED, "PretBold", align=2)


HTML_CARDS = [
    ("01", "TREND FRAME", "러닝은 무료지만<br>길목엔 시장이 붙는다", "러닝크루, 대회, 앱, 매장, 회복제품이 러너의 하루 동선 안으로 들어옵니다."),
    ("02", "CULTURE", "혼자 뛰던 러닝이<br>모이는 경험이 됐다", "생활체육 참여율 62.9%, 대회 참가 경쟁, 러닝크루가 참여 경험을 키웁니다."),
    ("03", "PLATFORM", "기록은 러너의<br>소속감 카드가 된다", "운동 로그가 접수, 인증, 커뮤니티를 잇는 작은 신분증처럼 쓰입니다."),
    ("04", "PLACE", "러너가 지나는 곳에<br>거점이 생긴다", "피팅, 측정, 보관, 물·간식, 휴식, 러닝 모임이 코스 주변 접점으로 붙습니다."),
    ("05", "PRODUCT", "러닝제품은 전·중·후<br>루틴으로 쪼개진다", "러닝화 하나보다 준비, 기록, 보급, 회복으로 카테고리가 나뉩니다."),
    ("06", "CHECKLIST", "숫자보다 먼저,<br>러너 동선을 보세요", "어디서 모이고, 뛰고, 쉬고, 다시 사는지를 점검하세요."),
    ("07", "EARLYSHINE", "", ""),
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
    .card::before {{ content: ""; position: absolute; width: 760px; height: 760px; border-radius: 50%; background: rgba(217,96,53,.10); left: -320px; top: -220px; }}
    .top {{ position: relative; display: flex; justify-content: space-between; align-items: center; z-index: 2; }}
    .kicker {{ color: {TAN}; font-weight: 800; letter-spacing: .18em; font-size: 16px; }}
    .kicker b {{ display: inline-flex; width: 44px; height: 44px; border: 1px solid {TAN}; border-radius: 50%; align-items: center; justify-content: center; margin-right: 12px; letter-spacing: 0; }}
    .logo {{ width: 262px; height: auto; }}
    .body {{ position: relative; z-index: 2; margin-top: 74px; }}
    .label {{ color: {TAN}; font-size: 15px; font-weight: 800; letter-spacing: .26em; }}
    h1 {{ margin: 48px 0 34px; font-size: 78px; line-height: .98; letter-spacing: -.02em; max-width: 760px; }}
    p {{ color: {MUTED}; font-size: 28px; line-height: 1.35; max-width: 760px; }}
    .photo {{ position: absolute; right: 58px; bottom: 160px; width: 390px; height: 520px; object-fit: cover; border: 1px solid {TAN_DEEP}; filter: saturate(.9) brightness(.9); }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 52px; max-width: 840px; }}
    .chip {{ border: 1px solid {LINE}; background: {PANEL}; padding: 12px 20px; font-size: 20px; font-weight: 800; color: {INK}; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; margin-top: 60px; max-width: 610px; }}
    .box {{ background: {PANEL}; border: 1px solid {LINE}; padding: 28px; min-height: 130px; }}
    .box strong {{ display: block; font-size: 30px; }}
    .box span {{ color: {TAN}; font-weight: 800; font-size: 21px; }}
    .footer {{ position: absolute; left: 58px; right: 58px; bottom: 78px; padding-top: 18px; border-top: 1px solid {LINE}; display: flex; justify-content: space-between; color: {MUTED}; font-size: 14px; z-index: 2; }}
    .ending {{ display: flex; align-items: center; justify-content: center; flex-direction: column; }}
    .ending img {{ width: 760px; }}
    .ending small {{ margin-top: 48px; color: {TAN}; letter-spacing: .24em; font-weight: 800; }}
    @page {{ size: 1080px 1350px; margin: 0; }}
    @media print {{ main {{ padding: 0; gap: 0; }} .card {{ break-after: page; }} }}
    """
    cards = []
    notes = [
        "프레임 카드입니다. 공식 확인이 어려운 러닝 인구·시장 규모 추정치는 제외했습니다.",
        "출처: 정책브리핑 2025 국민생활체육조사, JTBC 서울마라톤, 스포츠Q 대구마라톤 보도.",
        "출처: TechM 카카오-러너블 러너스 카드, JTBC 서울마라톤 Runable 접수 안내.",
        "출처: 이코노믹리뷰, 한경비즈니스, 어패럴뉴스. 모든 매장에 일반화하지 않았습니다.",
        "특정 제품 효과, 부상 예방, 매출 전망을 보장하지 않습니다.",
        "성과 보장이나 창업 추천이 아니라, 러너 동선 점검 기준입니다.",
        "러너의 동선을 보면 다음 소비 접점이 보입니다.",
    ]
    for no, label, title, sub in HTML_CARDS:
        if no == "07":
            body = f"""<section class="card ending"><img src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"><small>RUNNING TREND CARDNEWS</small><div class="footer"><span>{html.escape(notes[6])}</span><span>07 / 07</span></div></section>"""
        else:
            chips = ["러닝크루", "대회", "앱", "매장", "회복제품"] if no == "01" else ["동선", "인증", "거점", "루틴"]
            chip_html = "".join(f"<span class='chip'>{html.escape(ch)}</span>" for ch in chips)
            photo = ""
            if no == "02":
                photo = "<img class='photo' src='photos/running-korea-2026-crew.png' alt='러닝크루 AI 생성 이미지'>"
            if no == "05":
                photo = "<img class='photo' src='photos/running-korea-2026-products.png' alt='러닝제품 AI 생성 이미지'>"
            body = f"""<section class="card"><div class="top"><span class="kicker"><b>{no}</b>{label}</span><img class="logo" src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"></div><div class="body"><span class="label">{label}</span><h1>{title}</h1><p>{html.escape(sub)}</p><div class="chips">{chip_html}</div></div>{photo}<div class="footer"><span>{html.escape(notes[int(no)-1])}</span><span>{no} / 07</span></div></section>"""
        cards.append(body)
    html_text = "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>국내 러닝 트렌드 및 러닝제품 트렌드 2026</title><style>" + css + "</style></head><body><main>" + "\n".join(cards) + "</main></body></html>"
    (OUT / "running-korea-2026-cardnews.html").write_text(html_text, encoding="utf-8")


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for fn in [card1, card2, card3, card4, card5, card6, card7]:
        fn(doc)
    pdf_path = OUT / "running-korea-2026-cardnews.pdf"
    doc.save(pdf_path)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        pix.save(CARDS / f"running-korea-2026-card-{i:02d}.png")
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
        cp.insert_image(thumb, filename=str(CARDS / f"running-korea-2026-card-{idx:02d}.png"))
        text(cp, rect(x, y + 405, 320, 24), f"{idx:02d} / {TOTAL:02d}", 13, TAN, "PretBold", align=1)
    cpix = cp.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    cpix.save(OUT / "running-korea-2026-render-check.png")
    check.close()
    doc.close()
    write_html()
    print(f"wrote {pdf_path}")
    print("wrote 7 PNG cards")
    print("wrote running-korea-2026-cardnews.html")


if __name__ == "__main__":
    main()
