import math
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
TOTAL_CARDS = 7

BASE = "#0F0E0C"
PANEL = "#16140F"
INK = "#F3EDDE"
MUTED = "#9F927A"
TAN = "#D4B896"
TAN_DEEP = "#B79A6E"
ACCENT = "#D96035"
CREAM = "#EEE6D7"
LINE = "#514533"

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


def draw_bg(page):
    page.draw_rect(rect(0, 0, W, H), fill=c(BASE), color=None)
    for radius, opacity, x, y in [
        (390, 0.13, 100, 130),
        (520, 0.07, 980, 1140),
    ]:
        page.draw_circle((x, y), radius, fill=c(ACCENT), color=None, fill_opacity=opacity)
    page.draw_line((58, 1225), (1022, 1225), color=c(LINE), width=1)


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


def top(page, no, label="20S FASHION 2026"):
    page.draw_circle((78, 76), 22, color=c(TAN), width=1)
    text(page, rect(62, 59, 32, 34), no, 15, TAN, "PretBlack", align=1)
    text(page, rect(112, 59, 460, 36), label, 16, TAN, "PretBold")
    page.insert_image(rect(750, 57, 272, 32), filename=str(LOGO), keep_proportion=True)


def footer(page, note, no):
    text(page, rect(58, 1244, 760, 42), note, 14, MUTED, "Pret")
    text(page, rect(930, 1244, 92, 42), f"{no} / {TOTAL_CARDS:02d}", 15, MUTED, "PretBold", align=2)


def panel(page, r, fill=PANEL, stroke=LINE):
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=1)


def pill(page, x, y, label, width=None, fill=PANEL, color=INK, stroke=LINE, size=18):
    w = width or max(92, len(label) * 18 + 28)
    r = rect(x, y, w, 38)
    page.draw_rect(r, fill=c(fill), color=c(stroke), width=1)
    text(page, rect(x, y + 7, w, 28), label, size, color, "PretBold", align=1)


def image_panel(page, filename, r, label, keep=False):
    page.draw_rect(r, fill=c(PANEL), color=c(TAN_DEEP), width=1)
    page.insert_image(r, filename=str(PHOTOS / filename), keep_proportion=keep)
    page.draw_rect(r, color=c(BASE), width=0, fill=c(BASE), fill_opacity=0.08)
    lab = rect(r.x0 + 18, r.y1 - 56, 288, 38)
    page.draw_rect(lab, fill=c(BASE), color=c(LINE), width=1, fill_opacity=0.88)
    text(page, lab + (0, 8, 0, 0), label, 14, TAN, "PretBold", align=1)


def card1(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "01")
    text(p, rect(58, 144, 430, 36), "TREND FRAME", 15, TAN, "PretBold")
    text(p, rect(58, 205, 500, 385), "2026,\n20대는\n유행템보다\n룩을 편집한다", 72, INK, "PretBlack", lineheight=0.96)
    text(p, rect(58, 620, 455, 90), "새 옷을 더 사기보다,\n내 생활에 반복되는 조합을 만든다.", 27, MUTED, "Pret", lineheight=1.22)
    panel(p, rect(58, 835, 460, 250))
    text(p, rect(84, 858, 408, 70), "핵심은 뭐가 떴나가 아니라\n어떻게 내 스타일로 조합하나", 25, INK, "PretBold", lineheight=1.18)
    chips = ["스포츠코어", "빈티지", "모던 유니폼", "컬러 한 점", "실착 신발"]
    x, y = 84, 958
    for ch in chips:
        w = 118 if len(ch) <= 4 else 152
        if x + w > 490:
            x, y = 84, y + 50
        pill(p, x, y, ch, w, size=17)
        x += w + 10
    image_panel(p, "fashion-20s-2026-street.png", rect(552, 150, 470, 934), "AI 생성 이미지 / 한국 20대 스타일")
    footer(p, "공개 리포트와 패션 매체 보도 기반. 국내 20대 정량 수치는 확인 필요로 제외했습니다.", "01")


def card2(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "02")
    text(p, rect(58, 144, 430, 36), "TREND MAP", 15, TAN, "PretBold")
    text(p, rect(58, 204, 760, 310), "선호는\n5개 축으로\n갈라진다", 70, INK, "PretBlack", lineheight=0.98)
    text(p, rect(58, 475, 620, 70), "더 많은 옷장이 아니라,\n더 선명한 선택 기준.", 28, MUTED, "Pret", lineheight=1.2)
    p.draw_circle((918, 274), 92, fill=c(PANEL), color=c(TAN_DEEP), width=1)
    text_at(p, 894, 286, "5", 64, TAN, "PretBlack")
    text(p, rect(842, 300, 152, 32), "STYLE AXES", 17, MUTED, "PretBold", align=1)
    axes = [
        ("01", "스포츠\n로맨스", "저지와 트랙을\n일상복처럼"),
        ("02", "모던\n유니폼", "반복 가능한\n셔츠·재킷·팬츠"),
        ("03", "네오\n노스탤지어", "2000s·2010s를\n현재식으로"),
        ("04", "리셀\n가치", "새것보다\n발견감과 희소성"),
        ("05", "디테일\n팝", "무채색 위\n컬러·소품 한 점"),
    ]
    start_x = 58
    for i, (num, title, desc) in enumerate(axes):
        x = start_x + i * 194
        y = 620 + (40 if i % 2 else 0)
        r = rect(x, y, 178, 438)
        panel(p, r)
        p.draw_circle((x + 38, y + 42), 23, fill=c(ACCENT), color=c(TAN_DEEP), width=1, fill_opacity=0.25)
        text(p, rect(x + 24, y + 27, 28, 32), num, 14, TAN, "PretBlack", align=1)
        text(p, rect(x + 20, y + 108, 138, 150), title, 25, INK, "PretBlack", lineheight=1.08)
        text(p, rect(x + 20, y + 300, 138, 88), desc, 18, MUTED, "Pret", lineheight=1.25)
    pill(p, 58, 1128, "아이템보다 조합", 250, size=20)
    pill(p, 330, 1128, "유행보다 맥락", 250, size=20)
    pill(p, 602, 1128, "과시보다 실착", 250, size=20)
    footer(p, "Depop 2026 Trend Forecast, Pinterest Palette 2026, Vogue/GQ 보도 흐름 종합.", "02")


def card3(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "03")
    text(p, rect(58, 144, 430, 36), "SPORT SIGNAL", 15, TAN, "PretBold")
    text(p, rect(58, 204, 900, 265), "월드컵은\n경기장 밖 패션을\n키운다", 70, INK, "PretBlack", lineheight=0.98)
    text(p, rect(58, 480, 720, 70), "저지는 응원복에서 끝나지 않고,\n스커트·로퍼·셔츠와 섞인다.", 27, MUTED, "Pret", lineheight=1.22)
    board = rect(58, 610, 964, 490)
    panel(p, board)
    bars = [("+276%", "baddie tracksuit outfit", "트랙수트도 꾸미는 옷", 220), ("+840%", "World Cup jerseys", "저지는 2026의 강한 신호", 420)]
    for i, (big, small, lab, bh) in enumerate(bars):
        x = 122 + i * 455
        bar = rect(x, 610 + 450 - bh, 330, bh)
        p.draw_rect(bar, fill=c(TAN if i == 0 else CREAM), color=None)
        text(p, rect(x + 12, bar.y0 + 34, 306, 90), big, 72, BASE, "PretBlack", align=1)
        text(p, rect(x + 28, bar.y0 + 126, 274, 48), small, 22, BASE, "PretBold", align=1)
        text(p, rect(x, 1068, 330, 40), lab, 25, TAN, "PretBlack", align=1)
    pill(p, 75, 1140, "저지와 스커트", 280, size=20)
    pill(p, 400, 1140, "트랙 재킷과 로퍼", 280, size=20)
    pill(p, 725, 1140, "스포티와 포멀", 250, size=20)
    footer(p, "ELLE, Pinterest Summer Trend Report 인용 수치. 지역·계정별 실제 관심도는 다를 수 있습니다.", "03")


def card4(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "04")
    image_panel(p, "fashion-20s-2026-vintage.png", rect(58, 154, 430, 930), "AI 생성 이미지 / 빈티지 탐색")
    text(p, rect(526, 144, 420, 36), "RESALE VALUE", 15, TAN, "PretBold")
    text(p, rect(526, 204, 496, 300), "새것보다\n내가 발견한 옷이\n더 세다", 67, INK, "PretBlack", lineheight=0.98)
    text(p, rect(526, 535, 488, 92), "리셀과 빈티지는 가격보다\n희소성, 맥락, 자기표현의 언어가 된다.", 25, MUTED, "Pret", lineheight=1.22)
    stats = [("289B", "2026 글로벌 중고 의류 시장 전망"), ("70", "Gen Z·밀레니얼 성장 기여 전망")]
    for i, (big, desc) in enumerate(stats):
        x = 526 + i * 248
        panel(p, rect(x, 670, 232, 150))
        if big == "70":
            text_at(p, x + 16, 736, "70", 48, TAN, "PretBlack")
            text_at(p, x + 92, 730, "퍼센트", 18, TAN, "PretBold")
        else:
            text_at(p, x + 16, 736, big, 48, TAN, "PretBlack")
        text(p, rect(x + 16, 756, 200, 42), desc, 17, MUTED, "Pret", lineheight=1.16)
    reasons = ["남들과 덜 겹치는 희소성", "예산 안에서 좋은 소재 찾기", "옷에 이야기를 붙이는 재미"]
    for i, rtext in enumerate(reasons):
        y = 850 + i * 80
        panel(p, rect(526, y, 496, 64))
        p.draw_circle((556, y + 32), 22, fill=c(ACCENT), color=c(TAN_DEEP), width=1, fill_opacity=0.25)
        text(p, rect(544, y + 19, 24, 28), f"{i+1}", 15, TAN, "PretBlack", align=1)
        text(p, rect(588, y + 18, 390, 32), rtext, 23, INK, "PretBold")
    footer(p, "The Guardian, ThredUp/GlobalData 인용. 리셀 시장 전망은 보장 수치가 아닌 예측입니다.", "04")


def card5(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "05")
    text(p, rect(58, 144, 430, 36), "CLOSET SHIFT", 15, TAN, "PretBold")
    text(p, rect(58, 204, 530, 250), "옷장은 작아지고\n조합은\n선명해진다", 73, INK, "PretBlack", lineheight=0.98)
    text(p, rect(58, 488, 498, 78), "반복 가능한 셔츠, 재킷, 팬츠,\n신발이 20대의 새 기본값이 된다.", 25, MUTED, "Pret", lineheight=1.22)
    for x, head, items in [
        (58, "BEFORE", ["마이크로트렌드 쌓기", "하이프 스니커 모으기", "로고로 보여주기", "착장마다 새로 사기"]),
        (350, "AFTER", ["반복 실루엣 만들기", "실착 러너·로퍼", "컬러·소품 한 점", "출근-약속 겸용"]),
    ]:
        panel(p, rect(x, 640, 246, 420))
        text(p, rect(x + 20, 668, 200, 32), head, 24, TAN, "PretBlack")
        for i, item in enumerate(items):
            pill(p, x + 20, 730 + i * 76, item, 206, size=17)
    text(p, rect(306, 820, 44, 60), "TO", 24, TAN, "PretBlack", align=1)
    image_panel(p, "fashion-20s-2026-uniform.png", rect(638, 154, 384, 906), "AI 생성 이미지 / 모던 유니폼")
    panel(p, rect(638, 1082, 384, 88))
    text(p, rect(660, 1098, 340, 68), "트렌드는 빨라져도,\n실제로 입는 옷은 더 오래 반복됩니다.", 21, INK, "PretBold", lineheight=1.16)
    footer(p, "Depop Modern Uniforms, GQ Sneaker Survey의 실착성·개인화 흐름 참고.", "05")


def card6(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    top(p, "06")
    text(p, rect(58, 144, 430, 36), "SAVE CHECKLIST", 15, TAN, "PretBold")
    text(p, rect(58, 204, 760, 250), "20대가 반응하는\n패션 콘텐츠\n6가지", 77, INK, "PretBlack", lineheight=0.98)
    text(p, rect(58, 488, 650, 70), "상품보다 입는 공식을 보여줄 때 저장된다.", 28, MUTED, "Pret", lineheight=1.2)
    panel(p, rect(786, 455, 236, 46))
    text(p, rect(786, 464, 236, 38), "SAVE THIS", 18, TAN, "PretBlack", align=1)
    items = [
        ("저지와 스커트 공식", "스포츠 아이템을 포멀하게 섞기"),
        ("3가지 스타일링", "한 상품을 출근·약속·주말로 확장"),
        ("빈티지 발견감", "새것보다 고른 이유를 보여주기"),
        ("컬러 한 점", "무채색 베이스에 wasabi·persimmon"),
        ("실착 신발", "러너, 로퍼, 낮은 실루엣 중심"),
        ("반복 가능한 룩", "유행템보다 저장되는 조합"),
    ]
    for i, (head, desc) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 58 + col * 490
        y = 635 + row * 178
        panel(p, rect(x, y, 474, 152))
        p.draw_circle((x + 42, y + 76), 27, fill=c(ACCENT), color=c(TAN_DEEP), width=1, fill_opacity=0.25)
        text(p, rect(x + 28, y + 59, 28, 34), str(i + 1), 18, TAN, "PretBlack", align=1)
        text(p, rect(x + 86, y + 42, 350, 40), head, 28, INK, "PretBlack")
        text(p, rect(x + 86, y + 84, 350, 44), desc, 18, MUTED, "Pret", lineheight=1.18)
    footer(p, "출처: ELLE, Depop, Vogue Business, The Guardian, GQ, Pinterest Palette 2026.", "06")


def card7(doc):
    p = doc.new_page(width=W, height=H)
    install_fonts(p)
    draw_bg(p)
    p.insert_image(rect(160, 592, 760, 90), filename=str(LOGO), keep_proportion=True)
    text(p, rect(58, 738, 964, 42), "TREND CARDNEWS BY EARLYSHINE", 18, TAN, "PretBold", align=1)
    text(p, rect(58, 1244, 760, 42), "다음 카드뉴스에서도 바로 써먹을 수 있는 트렌드만 압축해 전합니다.", 14, MUTED, "Pret")
    text(p, rect(930, 1244, 92, 42), f"07 / {TOTAL_CARDS:02d}", 15, MUTED, "PretBold", align=2)


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for fn in [card1, card2, card3, card4, card5, card6, card7]:
        fn(doc)
    pdf_path = OUT / "fashion-20s-2026-cardnews.pdf"
    doc.save(pdf_path)
    zoom = 1
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        pix.save(CARDS / f"fashion-20s-2026-card-{i:02d}.png")
    first = doc[0].get_pixmap(matrix=fitz.Matrix(0.5, 0.5), alpha=False)
    first.save(OUT / "fashion-20s-2026-render-check.png")
    doc.close()
    print(f"wrote {pdf_path}")
    print(f"wrote {TOTAL_CARDS} PNG cards")


if __name__ == "__main__":
    main()
