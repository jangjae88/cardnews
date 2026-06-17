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
    # Subtle vertical gradient only. No decorative circles/orbs/blobs.
    bands = 18
    for i in range(bands):
        y0 = H * i / bands
        y1 = H * (i + 1) / bands
        t = i / (bands - 1)
        color = mix("#12100D", "#0F0E0C", min(t * 1.4, 1)) if t < 0.72 else mix("#0F0E0C", "#11100D", (t - 0.72) / 0.28)
        page.draw_rect(fitz.Rect(0, y0, W, y1 + 1), fill=color, color=None)
    for y in [330, 650, 970]:
        page.draw_line((58, y), (1022, y - 90), color=c(LINE), width=0.8, stroke_opacity=0.24)
    page.draw_line((58, 1225), (1022, 1225), color=c(LINE), width=1)


def top(page, no, label):
    page.draw_rect(rect(56, 54, 44, 44), color=c(TAN), width=1)
    text(page, rect(56, 64, 44, 28), f"{no:02d}", 15, TAN, "PretBlack", align=1)
    text(page, rect(112, 59, 530, 34), label, 16, TAN, "PretBold")
    page.insert_image(rect(760, 57, 262, 32), filename=str(LOGO), keep_proportion=True)


def footer(page, note, no):
    text(page, rect(58, 1242, 765, 48), note, 13.5, MUTED, "Pret", lineheight=1.12)
    text(page, rect(928, 1244, 94, 42), f"{no:02d} / {TOTAL:02d}", 15, MUTED, "PretBold", align=2)


def panel(page, r, fill=PANEL, stroke=LINE, width=1, opacity=1):
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=width, fill_opacity=opacity)


def pill(page, x, y, label, width, fill=PANEL, color=INK, stroke=LINE, size=18):
    r = rect(x, y, width, 42)
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=1)
    text(page, rect(x, y + 8, width, 30), label, size, color, "PretBold", align=1)


def image_panel(page, filename, r, label="", opacity=0.16):
    page.draw_rect(r, fill=c(PANEL), color=c(TAN_DEEP), width=1)
    page.insert_image(r, filename=str(PHOTOS / filename), keep_proportion=False)
    page.draw_rect(r, fill=c(BASE), color=None, fill_opacity=opacity)
    if label:
        lab = rect(r.x0 + 18, r.y1 - 56, 310, 38)
        page.draw_rect(lab, fill=c(BASE), color=c(LINE), width=1, fill_opacity=0.9)
        text(page, rect(lab.x0, lab.y0 + 8, lab.width, 28), label, 14, TAN, "PretBold", align=1)


def title_block(page, kicker, title, sub, x=58, y=145, w=720, title_size=74):
    text(page, rect(x, y, 520, 36), kicker, 15, TAN, "PretBold")
    cursor = y + 126
    for line in title.split("\n"):
        text_at(page, x, cursor, line, title_size, INK, "PretBlack")
        cursor += title_size * 0.94
    text(page, rect(x, cursor + 28, w, 112), sub, 26, MUTED, "Pret", lineheight=1.24)


def arrow(page, start, end, color=TAN, width=2.5):
    page.draw_line(start, end, color=c(color), width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    left = (end[0] - ux * 20 - uy * 9, end[1] - uy * 20 + ux * 9)
    right = (end[0] - ux * 20 + uy * 9, end[1] - uy * 20 - ux * 9)
    page.draw_polyline([left, end, right], color=c(color), width=width)


def card1(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    image_panel(p, "glp1-2026-clinic-consult.png", rect(0, 0, W, H), opacity=0.52)
    p.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None, fill_opacity=0.1)
    top(p, 1, "GLP1 MARKET 2026")
    title_block(
        p,
        "TREND FRAME",
        "위고비 열풍,\n진짜 변화는\n약국 밖에서\n시작된다",
        "고객의 장바구니, 식사량, 자기관리 루틴이 다시 짜이는 신호입니다.",
        w=690,
        title_size=74,
    )
    center = (540, 844)
    panel(p, rect(470, 814, 140, 60), fill=BASE, stroke=TAN, width=1.5, opacity=0.9)
    text(p, rect(470, 832, 140, 30), "처방 관심", 21, TAN, "PretBlack", align=1)
    items = [
        (250, 720, "식품"),
        (480, 660, "외식"),
        (736, 720, "헬스"),
        (260, 980, "뷰티"),
        (545, 1040, "패션"),
        (790, 980, "광고"),
    ]
    for x, y, label in items:
        arrow(p, center, (x + 70, y + 20), color=TAN, width=2.4)
        pill(p, x, y, label, 140, fill=PANEL_2, color=INK, stroke=TAN_DEEP, size=20)
    panel(p, rect(180, 1110, 720, 68), fill=BASE, stroke=TAN_DEEP, opacity=0.9)
    text(p, rect(210, 1128, 660, 32), "약 이야기를 넘어, 고객 행동 변화로 보기", 21, TAN, "PretBlack", align=1)
    footer(p, "의약품 복용, 처방, 구매 안내가 아닌 시장 트렌드 해설입니다.", 1)


def card2(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 2, "MARKET SHIFT")
    title_block(
        p,
        "MARKET SHIFT",
        "살 빠지는 약으로만\n보면 진짜 시장을\n놓친다",
        "GLP1/GIP 계열은 관심 이슈에서 거대한 건강관리 카테고리로 넓어지고 있습니다.",
        w=810,
        title_size=69,
    )
    rows = [
        ("틈새 관심", "메가 카테고리", "기업 실적 확대"),
        ("주사 중심", "알약 흐름", "경구제 승인 흐름"),
        ("체중관리", "동반질환 관리", "적응증 확장"),
    ]
    for i, (left, right, chip) in enumerate(rows):
        y = 688 + i * 156
        panel(p, rect(72, y, 378, 108), fill=PANEL_2)
        panel(p, rect(630, y, 378, 108), fill=PANEL_2)
        text(p, rect(100, y + 30, 320, 42), left, 29, MUTED, "PretBlack", align=1)
        text(p, rect(658, y + 30, 320, 42), right, 29, INK, "PretBlack", align=1)
        arrow(p, (474, y + 54), (606, y + 54), color=ORANGE, width=3)
        pill(p, 392, y + 112, chip, 296, fill=BASE, color=TAN, stroke=LINE, size=17)
    footer(p, "시장 성장 신호는 의약품 사용 권유와 다릅니다. 한국 경구제 출시는 확인 필요입니다.", 2)


def card3(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 3, "KOREA")
    title_block(
        p,
        "KOREA MAP",
        "한국에서도\n관심은 커졌지만,\n가드레일이 먼저다",
        "위고비와 마운자로가 알려졌지만, 비급여와 처방, 대상자 확인이 핵심입니다.",
        w=760,
        title_size=72,
    )
    panel(p, rect(58, 660, 456, 460), fill=PANEL_2)
    panel(p, rect(566, 660, 456, 460), fill=PANEL_2, stroke=TAN_DEEP, width=1.4)
    text(p, rect(86, 696, 390, 42), "관심 증가", 34, TAN, "PretBlack")
    text(p, rect(594, 696, 390, 42), "가드레일", 34, WARN, "PretBlack")
    left = ["위고비 2024 국내 출시", "마운자로 2025 국내 출시", "성인 3명 중 1명 이상 비만"]
    right = ["비급여", "대상자 확인", "의료진 판단", "부작용 설명", "생활습관 병행"]
    for i, item in enumerate(left):
        pill(p, 86, 776 + i * 78, item, 374, fill=BASE, color=INK, size=19)
    for i, item in enumerate(right):
        pill(p, 594, 764 + i * 62, item, 374, fill=BASE, color=INK, stroke=WARN if i == 0 else LINE, size=19)
    panel(p, rect(190, 1144, 700, 52), fill=BASE)
    text(p, rect(220, 1158, 640, 30), "관심보다 먼저 확인해야 할 것은 대상자와 안전성입니다.", 18, TAN, "PretBold", align=1)
    footer(p, "가격 비교, 구매처, 처방받는 법은 다루지 않습니다. 허가사항과 의료진 판단이 전제입니다.", 3)


def card4(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, 4, "GUARDRAIL")
    title_block(
        p,
        "COMMUNICATION RISK",
        "건강 이슈는\n말하는 방식이\n리스크가 된다",
        "전문의약품 이름을 마케팅 언어처럼 쓰는 순간, 신뢰와 안전 문제가 생깁니다.",
        w=760,
        title_size=76,
    )
    bads = ["누구나 가능", "부작용 없음", "쉽게 처방", "빠른 감량 보장"]
    for i, label in enumerate(bads):
        x = 82 + (i % 2) * 476
        y = 660 + (i // 2) * 156
        panel(p, rect(x, y, 440, 118), fill=PANEL_2, stroke=WARN, width=1.4)
        p.draw_rect(rect(x + 28, y + 34, 40, 50), fill=c(WARN), color=None, fill_opacity=0.55)
        text(p, rect(x + 28, y + 48, 40, 30), "!", 22, INK, "PretBlack", align=1)
        text(p, rect(x + 92, y + 37, 310, 44), label, 31, INK, "PretBlack")
    text(p, rect(58, 995, 964, 32), "대신 이렇게 말하세요", 19, TAN, "PretBlack", align=1)
    safe = ["의료진 판단", "허가사항", "안전성", "생활습관 병행"]
    for i, label in enumerate(safe):
        pill(p, 132 + i * 210, 1048, label, 172, fill=BASE, color=TAN, stroke=TAN_DEEP, size=18)
    footer(p, "FDA는 미승인 조제 GLP1 제품의 이상사례와 투약 오류 가능성을 경고합니다.", 4)


def card5(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    image_panel(p, "glp1-2026-small-portion.png", rect(632, 142, 390, 360), "AI 생성 이미지 / 소용량 메뉴", opacity=0.08)
    top(p, 5, "CONSUMPTION")
    title_block(
        p,
        "CONSUMPTION",
        "많이 먹기보다\n적게 먹어도\n만족을 찾는다",
        "해외에서는 소용량, 고단백, 저당, 작은 포션 같은 소비 신호가 관찰됩니다.",
        w=560,
        title_size=65,
    )
    panel(p, rect(58, 620, 456, 478), fill=PANEL_2)
    panel(p, rect(566, 620, 456, 478), fill=PANEL_2, stroke=TAN_DEEP, width=1.4)
    text(p, rect(86, 654, 390, 40), "Before", 32, MUTED, "PretBlack")
    text(p, rect(594, 654, 390, 40), "After", 32, TAN, "PretBlack")
    before = ["큰 양", "강한 자극", "달고 짠 간식", "주류 중심"]
    after = ["소용량", "높은 만족", "고단백·저당", "가벼운 한 끼"]
    for i, item in enumerate(before):
        pill(p, 86, 730 + i * 76, item, 374, fill=BASE, color=INK, size=21)
    for i, item in enumerate(after):
        pill(p, 594, 730 + i * 76, item, 374, fill=BASE, color=INK, stroke=TAN_DEEP, size=21)
    panel(p, rect(320, 1128, 440, 58), fill=BASE, stroke=ORANGE)
    text(p, rect(340, 1144, 400, 30), "국내 적용은 확인 필요", 19, ORANGE, "PretBlack", align=1)
    footer(p, "해외 사례를 한국 매출 변화로 단정하지 않습니다. 의약품명 상품 표현도 피합니다.", 5)


def card6(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    image_panel(p, "glp1-2026-fit-routine.png", rect(0, 0, W, H), opacity=0.72)
    p.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None, fill_opacity=0.1)
    top(p, 6, "CHECKLIST")
    title_block(
        p,
        "SAVE CHECKLIST",
        "약을 말하지 말고,\n바뀐 루틴을\n읽어라",
        "작은 브랜드는 고객의 식사량, 만족 기준, 자기관리 고민이 바뀌는지 봐야 합니다.",
        w=760,
        title_size=78,
    )
    panel(p, rect(58, 646, 462, 456), fill=PANEL_2, stroke=TAN_DEEP, opacity=0.94)
    panel(p, rect(560, 646, 462, 456), fill=PANEL_2, stroke=WARN, opacity=0.94)
    text(p, rect(88, 680, 390, 40), "실험 질문", 31, TAN, "PretBlack")
    text(p, rect(590, 680, 390, 40), "표현 주의", 31, WARN, "PretBlack")
    left = ["소용량 옵션이 있는가", "고단백·저당 선택지가 있는가", "가벼운 한 끼 언어를 쓰는가", "핏과 루틴 고민을 읽는가"]
    right = ["효과 보장을 피했는가", "처방·구매 안내를 피했는가", "해외 데이터를 일반화하지 않았는가"]
    for i, item in enumerate(left):
        y = 758 + i * 74
        p.draw_rect(rect(80, y + 4, 24, 24), fill=c(ORANGE), color=None, fill_opacity=0.6)
        text(p, rect(122, y, 360, 42), item, 21, INK, "PretBold")
    for i, item in enumerate(right):
        y = 774 + i * 82
        p.draw_rect(rect(582, y + 4, 24, 24), fill=c(WARN), color=None, fill_opacity=0.62)
        text(p, rect(624, y, 348, 54), item, 21, INK, "PretBold", lineheight=1.08)
    pill(p, 388, 1132, "SAVE THIS", 304, fill=BASE, color=TAN, stroke=TAN_DEEP, size=19)
    footer(p, "의학적 조언이 아닙니다. 전문의약품은 허가사항과 의료진 판단이 필요합니다.", 6)


def card7(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    p.insert_image(center_rect(760, 90, 592), filename=str(LOGO), keep_proportion=True)
    text(p, rect(58, 738, 964, 42), "MARKET TREND CARDNEWS", 18, TAN, "PretBold", align=1)
    text(p, rect(58, 1244, 760, 42), "시장을 볼 때는 제품보다 바뀐 행동을 먼저 봅니다.", 14, MUTED, "Pret")
    text(p, rect(930, 1244, 92, 42), "07 / 07", 15, MUTED, "PretBold", align=2)


HTML_CARDS = [
    ("01", "GLP1 MARKET 2026", "위고비 열풍,<br>진짜 변화는<br>약국 밖에서 시작된다", "고객의 장바구니, 식사량, 자기관리 루틴이 다시 짜이는 신호입니다."),
    ("02", "MARKET SHIFT", "살 빠지는 약으로만 보면<br>진짜 시장을 놓친다", "GLP1/GIP 계열은 관심 이슈에서 거대한 건강관리 카테고리로 넓어지고 있습니다."),
    ("03", "KOREA", "한국에서도 관심은 커졌지만,<br>가드레일이 먼저다", "위고비와 마운자로가 알려졌지만, 비급여와 처방, 대상자 확인이 핵심입니다."),
    ("04", "GUARDRAIL", "건강 이슈는<br>말하는 방식이 리스크가 된다", "전문의약품 이름을 마케팅 언어처럼 쓰는 순간, 신뢰와 안전 문제가 생깁니다."),
    ("05", "CONSUMPTION", "많이 먹기보다<br>적게 먹어도 만족을 찾는다", "해외에서는 소용량, 고단백, 저당, 작은 포션 같은 소비 신호가 관찰됩니다."),
    ("06", "CHECKLIST", "약을 말하지 말고,<br>바뀐 루틴을 읽어라", "고객의 식사량, 만족 기준, 자기관리 고민이 바뀌는지 봐야 합니다."),
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
    .card {{ position: relative; width: 1080px; height: 1350px; overflow: hidden; background: linear-gradient(180deg, #12100D 0%, {BASE} 56%, #11100D 100%); padding: 58px; }}
    .photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .35; filter: saturate(.85) brightness(.72); }}
    .top {{ position: relative; display: flex; justify-content: space-between; align-items: center; z-index: 2; }}
    .kicker {{ color: {TAN}; font-weight: 800; letter-spacing: .18em; font-size: 16px; }}
    .kicker b {{ display: inline-flex; width: 44px; height: 44px; border: 1px solid {TAN}; align-items: center; justify-content: center; margin-right: 12px; letter-spacing: 0; }}
    .logo {{ width: 262px; height: auto; }}
    .body {{ position: relative; z-index: 2; margin-top: 74px; }}
    .label {{ color: {TAN}; font-size: 15px; font-weight: 800; letter-spacing: .26em; }}
    h1 {{ margin: 48px 0 34px; font-size: 74px; line-height: .98; letter-spacing: 0; max-width: 850px; }}
    p {{ color: {MUTED}; font-size: 27px; line-height: 1.35; max-width: 760px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 52px; max-width: 880px; }}
    .chip {{ border: 1px solid {LINE}; background: {PANEL}; padding: 12px 20px; font-size: 20px; font-weight: 800; color: {INK}; }}
    .footer {{ position: absolute; left: 58px; right: 58px; bottom: 78px; padding-top: 18px; border-top: 1px solid {LINE}; display: flex; justify-content: space-between; color: {MUTED}; font-size: 14px; z-index: 2; }}
    .ending {{ display: flex; align-items: center; justify-content: center; flex-direction: column; }}
    .ending img {{ width: 760px; }}
    .ending small {{ margin-top: 48px; color: {TAN}; letter-spacing: .24em; font-weight: 800; }}
    @page {{ size: 1080px 1350px; margin: 0; }}
    @media print {{ main {{ padding: 0; gap: 0; }} .card {{ break-after: page; }} }}
    """
    notes = [
        "의약품 복용, 처방, 구매 안내가 아닌 시장 트렌드 해설입니다.",
        "시장 성장 신호는 의약품 사용 권유와 다릅니다. 한국 경구제 출시는 확인 필요입니다.",
        "가격 비교, 구매처, 처방받는 법은 다루지 않습니다.",
        "FDA는 미승인 조제 GLP1 제품의 이상사례와 투약 오류 가능성을 경고합니다.",
        "해외 사례를 한국 매출 변화로 단정하지 않습니다.",
        "의학적 조언이 아닙니다. 전문의약품은 의료진 판단이 필요합니다.",
        "시장을 볼 때는 제품보다 바뀐 행동을 먼저 봅니다.",
    ]
    chip_sets = [
        ["식품", "외식", "헬스", "뷰티", "패션", "광고"],
        ["틈새 관심 -> 메가 카테고리", "주사 중심 -> 알약 흐름", "체중관리 -> 동반질환 관리"],
        ["비급여", "대상자 확인", "의료진 판단", "생활습관 병행"],
        ["누구나 가능 금지", "부작용 없음 금지", "쉽게 처방 금지", "빠른 감량 보장 금지"],
        ["소용량", "고단백·저당", "가벼운 한 끼", "국내 적용 확인 필요"],
        ["소용량 옵션", "효과 보장 금지", "처방·구매 안내 금지"],
    ]
    photos = {
        "01": "photos/glp1-2026-clinic-consult.png",
        "05": "photos/glp1-2026-small-portion.png",
        "06": "photos/glp1-2026-fit-routine.png",
    }
    cards = []
    for idx, (no, label, title, sub) in enumerate(HTML_CARDS):
        if no == "07":
            body = f"""<section class="card ending"><img src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"><small>MARKET TREND CARDNEWS</small><div class="footer"><span>{html.escape(notes[6])}</span><span>07 / 07</span></div></section>"""
        else:
            photo = f"<img class='photo' src='{photos[no]}' alt='카드 이미지'>" if no in photos else ""
            chips = "".join(f"<span class='chip'>{html.escape(ch)}</span>" for ch in chip_sets[idx])
            body = f"""<section class="card">{photo}<div class="top"><span class="kicker"><b>{no}</b>{label}</span><img class="logo" src="../assets/logo/main_a_transparent.png" alt="EARLYSHINE"></div><div class="body"><span class="label">{label}</span><h1>{title}</h1><p>{html.escape(sub)}</p><div class="chips">{chips}</div></div><div class="footer"><span>{html.escape(notes[idx])}</span><span>{no} / 07</span></div></section>"""
        cards.append(body)
    html_text = "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>GLP-1 비만치료제 트렌드와 시장 영향 2026</title><style>" + css + "</style></head><body><main>" + "\n".join(cards) + "</main></body></html>"
    (OUT / "glp1-diet-drugs-2026-cardnews.html").write_text(html_text, encoding="utf-8")


def write_summary():
    summary = """# Packaging Summary: GLP-1/GIP 비만치료제 트렌드와 시장 영향 2026ver

결론:
1. 인스타 업로드용 1080x1350 PNG 7장, HTML, PDF를 생성했다.
2. 1~6장은 시장 확산, 글로벌 전환, 한국 가드레일, 위험 표현, 소비 변화, 체크리스트로 구성했고 7장은 EARLYSHINE 로고 엔딩으로 마감했다.
3. 모든 본문 카드 우상단과 엔딩 카드 중앙에 실제 EARLYSHINE 로고 이미지 `assets/logo/main_a_transparent.png`를 삽입했다.

에이전트 진행:
- research(자료조사): 완료, `output/research-glp1-diet-drugs-2026.md`
- analysis(기획분석): 완료, `output/analysis-glp1-diet-drugs-2026.md`
- writing-outline(카드구성): 완료, `output/writing-outline-glp1-diet-drugs-2026.md`
- design(디자인설계): 팀장 방에서 작성, `output/design-glp1-diet-drugs-2026.md`
- writing(최종문구): 팀장 방에서 작성, `output/writing-glp1-diet-drugs-2026.md`
- image(이미지제작): 팀장 방에서 imagegen으로 생성 후 `output/image-glp1-diet-drugs-2026.md`에 정리
- packaging(출력패키징): 팀장 방에서 구현 및 QA

산출물:
- HTML: `output/glp1-diet-drugs-2026-cardnews.html`
- PDF: `output/glp1-diet-drugs-2026-cardnews.pdf`
- PNG: `output/cards/glp1-diet-drugs-2026-card-01.png` ~ `output/cards/glp1-diet-drugs-2026-card-07.png`
- 렌더 확인 이미지: `output/glp1-diet-drugs-2026-render-check.png`

QA:
- 처방받는 법, 구매처, 가격 비교, 효과 보장, 전후 몸 사진을 넣지 않았다.
- 해외 소비 데이터는 한국 매출 변화로 단정하지 않고 `국내 적용은 확인 필요`로 낮춰 표현했다.
- 실제 의약품명/로고 대신 추상 상담, 소용량 식품, 핏 루틴 이미지만 사용했다.
- 배경용 원형 장식, 둥근 오브, 블롭을 제거하고 단색에 가까운 미세 세로 그라데이션으로 수정했다.
- 중앙 요소는 1080px 캔버스 중심선 기준으로 박스 좌표를 맞췄다.
- PNG/PDF는 같은 PyMuPDF 렌더 소스에서 생성했다.
"""
    (OUT / "packaging-summary-glp1-diet-drugs-2026.md").write_text(summary, encoding="utf-8")


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for fn in [card1, card2, card3, card4, card5, card6, card7]:
        fn(doc)
    pdf_path = OUT / "glp1-diet-drugs-2026-cardnews.pdf"
    doc.save(pdf_path)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        pix.save(CARDS / f"glp1-diet-drugs-2026-card-{i:02d}.png")
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
        cp.insert_image(thumb, filename=str(CARDS / f"glp1-diet-drugs-2026-card-{idx:02d}.png"))
        text(cp, rect(x, y + 405, 320, 24), f"{idx:02d} / {TOTAL:02d}", 13, TAN, "PretBold", align=1)
    cpix = cp.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    cpix.save(OUT / "glp1-diet-drugs-2026-render-check.png")
    check.close()
    doc.close()
    write_html()
    write_summary()
    print(f"wrote {pdf_path}")
    print("wrote 7 PNG cards")
    print("wrote glp1-diet-drugs-2026-cardnews.html")
    print("wrote packaging-summary-glp1-diet-drugs-2026.md")


if __name__ == "__main__":
    main()
