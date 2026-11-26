#!/usr/bin/env python3
"""Render entry.png: one image summing up 25 November 2026 world news.

Canvas 1024x1024, PIL + DejaVu. Structure: masthead with the date, one
lead story (tariffs + the Wall Street plunge and rebound, with a small
intraday chart), a 2x2 grid of four stories, a briefs strip, and a
sources footer. Text is wrapped to fixed boxes and the script raises
on overflow, so a bad fit fails loudly instead of clipping silently.
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (250, 246, 239)
INK = (22, 22, 22)
GREY = (92, 88, 82)
ACCENT = (163, 51, 39)
RULE = (181, 175, 165)
CARD = (255, 253, 248)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap_lines(draw, text, fnt, max_w):
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if not cur:
                raise ValueError("single word wider than box: %r" % word)
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(draw, text, fnt, x, y, max_w, max_lines, leading, fill=INK):
    lines = wrap_lines(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        raise ValueError("needs %d lines, max %d: %r" % (len(lines), max_lines, text[:50]))
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 44
    cw = W - 2 * mx

    # Masthead (right-hand tag marks this as the full-day final edition)
    d.text((mx, 30), "THE WORLD IN ONE IMAGE", font=F(F_SANS_B, 20), fill=ACCENT)
    tag = "FINAL EDITION"
    tw = d.textlength(tag, font=F(F_SANS_B, 20))
    d.text((W - mx - tw, 30), tag, font=F(F_SANS_B, 20), fill=GREY)
    d.text((mx, 56), "WEDNESDAY · 25 NOVEMBER 2026", font=F(F_SERIF_B, 44), fill=INK)
    d.line([(mx, 124), (W - mx, 124)], fill=INK, width=3)

    # Lead: tariffs and the market swing
    ly = 142
    d.text((mx, ly), "TRADE  ·  MARKETS", font=F(F_SANS_B, 20), fill=ACCENT)
    d.text((mx, ly + 27), "TARIFF SHOCK, THEN", font=F(F_SERIF_B, 47), fill=INK)
    d.text((mx, ly + 82), "A WALL ST REBOUND", font=F(F_SERIF_B, 47), fill=INK)
    lead = ("The US proposes tariffs of up to 20% on 14 partners — China "
            "20%, the EU 15%. The Nasdaq plunges 4.6% intraday and "
            "Nvidia falls 3.9%, then buyers step in before Thanksgiving.")
    para(d, lead, F(F_SANS, 22), mx, ly + 140, 600, 4, 27)
    # Right block: intraday chart (plunge and recovery) + figures,
    # kept compact so its captions clear the rule above the grid.
    cx0, cy0, cx1, cy1 = 690, ly + 140, 966, ly + 204
    d.rectangle([cx0, cy0, cx1, cy1], outline=RULE, width=1)
    pts = [(cx0 + 10, cy0 + 10), (cx0 + 60, cy0 + 22), (cx0 + 110, cy0 + 44),
           (cx0 + 150, cy0 + 54), (cx0 + 195, cy0 + 30), (cx0 + 240, cy0 + 18),
           (cx1 - 10, cy0 + 15)]
    d.line(pts, fill=ACCENT, width=4)
    cap = "Nasdaq: -4.6% low, -0.6% close"
    if d.textlength(cap, font=F(F_SANS, 16)) > cx1 - cx0:
        raise ValueError("chart caption too wide")
    d.text((cx0, cy1 + 7), cap, font=F(F_SANS, 16), fill=GREY)
    d.text((cx0, cy1 + 29), "S&P -0.25%  ·  Dow +0.33%",
           font=F(F_SANS_B, 18), fill=INK)
    d.line([(mx, 398), (W - mx, 398)], fill=RULE, width=1)

    # Grid 2x2
    cards = [
        ("TANKERS HIT MINES IN HORMUZ",
         "Iran says two tankers struck mines and caught fire in the "
         "Strait of Hormuz. The Houthis claim an attack on Saudi "
         "Arabia's Ras Tanura refinery; Brent jumps 3.5%."),
        ("FIRST FOREIGN ASTRONAUT AT TIANGONG",
         "Shenzhou-24 lifts off from Jiuquan: Pakistan's Muhammad "
         "Zeeshan Ali, 40, becomes the first foreign astronaut aboard "
         "China's space station, docking in 3.5 hours."),
        ("HUAWEI CONVICTED IN THE US",
         "A New York jury finds Huawei guilty on 10 of 12 counts — bank "
         "fraud and stealing trade secrets — and not guilty of "
         "racketeering. China condemns the verdict."),
        ("UKRAINE HITS RUSSIAN AIR BASE",
         "Ukraine says a strike on the Savasleyka air base, east of "
         "Moscow, damaged five jets: three MiG-31s and two Su-34s. "
         "Russia steps up attacks on power and heat."),
    ]
    gx, gy = mx, 416
    cell_w, cell_h, gut = 458, 198, 20
    for i, (kick, body) in enumerate(cards):
        x = gx + (i % 2) * (cell_w + gut)
        y = gy + (i // 2) * (cell_h + gut)
        d.rectangle([x, y, x + cell_w, y + cell_h], fill=CARD, outline=RULE, width=1)
        d.text((x + 18, y + 13), kick, font=F(F_SANS_B, 17), fill=ACCENT)
        d.line([(x + 18, y + 42), (x + cell_w - 18, y + 42)], fill=RULE, width=1)
        para(d, body, F(F_SANS, 20), x + 18, y + 56, cell_w - 36, 5, 27)

    # Briefs
    by = 850
    d.text((mx, by), "ALSO TODAY", font=F(F_SANS_B, 18), fill=ACCENT)
    d.line([(mx + 128, by + 10), (W - mx, by + 10)], fill=RULE, width=1)
    briefs = [
        "Solomon Islands signs treaty with Australia: no foreign bases, A$740m over 10 years.",
        "Sudan: RSF drone strikes kill 19 civilians in Blue Nile state, rights group says.",
        "Gaza: Israeli strike kills Hamas security chief Abuelouf and his family in Shati camp.",
        "Pope Leo XIV laments COP31's failure to reach a climate agreement.",
        "Bangladesh raises garment workers' minimum wage 36% to 17,000 taka ($136).",
    ]
    bf = F(F_SANS, 19)
    y = by + 25
    for b in briefs:
        if d.textlength("•  " + b, font=bf) > cw:
            raise ValueError("brief too long for one line: %r" % b)
        d.text((mx, y), "•  " + b, font=bf, fill=INK)
        y += 23

    # Footer
    d.line([(mx, 988), (W - mx, 988)], fill=RULE, width=1)
    foot = "Sources: Reuters · AP · Bloomberg · Al Jazeera · CNN · Xinhua"
    ff = F(F_SANS, 15)
    if d.textlength(foot, font=ff) > cw:
        raise ValueError("footer too wide")
    d.text((mx, 994), foot, font=ff, fill=GREY)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    build()
