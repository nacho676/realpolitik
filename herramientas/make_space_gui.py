# Generates interface/mdr_space.gui and common/scripted_guis/mdr_space_gui.txt: the space programme menu, built with Millennium Dawn's
# own sprites. A tab inside its Space Programme opens the menu, a window of its own beside the International Systems window.
# Each page is a whole window: pages hanging from a window without a parent were placed relative to the screen.
# The agency's name is typed as in the intelligence agency's window. A mod window cannot read a text field, so the keys are shortcuts of
# buttons kept off screen, which only exist while that window is open.
# Run from the mod folder: python herramientas/make_space_gui.py
import re
import space_program

NAV = {i: "" for i in range(1, 10)}
NAV_ICONS = {1: "summary", 2: "goals", 3: "projects", 4: "staff", 5: "finance", 6: "solar", 7: "decisions", 8: "colonies", 9: "programme"}
# Side bar: groups of pages, in order.
NAV_GROUPS = [("PROGRAMME", (1, 2, 4, 5)), ("EXPLORATION", (6, 8)), ("OPERATIONS", (3, 7)), ("HELP", (9,))]
# As big as Millennium Dawn's satellite orbit window, beside its Space Programme panel. The pages were drawn for a
# 748 x 576 area from (16, 124): they are moved into the area right of the side bar (CONTENT_X, CONTENT_Y).
W, H = 904, 690
# Centred on the screen when it opens; it can be dragged by its frame.
POS_X, POS_Y = -W // 2, -H // 2
SIDE_X, SIDE_W = 10, 126
CONTENT_X, CONTENT_Y = 144, 58
BAR_Y = 642
LOGOS = {"usa": "USA", "sov": "SOV", "chi": "CHI", "fra": "FRA", "eng": "ENG", "raj": "RAJ", "isr": "ISR"}
# mdr_space_logo: 0 the country's own, from 1 these, in this order.
GENERIC_LOGOS = ["any", "space", "rocketry", "orbit", "moon", "landmars", "marsbase", "mars", "asteroid"]
MAX_CHARS = 32
UPPER = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
# A character is stored as its position here, from 1.
CHARS = UPPER + UPPER.lower() + "áéíóú0123456789 -."
CODE = {c: i + 1 for i, c in enumerate(CHARS)}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
OTHER_KEYS = {"space": ("SPACE", " "), "dash": ("-", "-"), "dot": (".", ".")}
OTHER_KEYS.update({f"digit_{n}": (str(n), str(n)) for n in range(10)})
# Real names, written ready in the field when the country starts.
REAL_NAMES = {
    "USA": "NASA", "SOV": "Roscosmos", "CHI": "CNSA", "JAP": "JAXA", "RAJ": "ISRO", "FRA": "CNES", "UKR": "SSAU", "ISR": "ISA",
    "CAN": "CSA", "GER": "DLR", "ITA": "ASI", "ENG": "UK Space Agency", "BRA": "AEB", "ARG": "CONAE", "KOR": "KARI", "PAK": "SUPARCO",
    "IND": "LAPAN", "SPR": "INTA", "HOL": "NSO", "BEL": "BELSPO", "SWE": "SNSA", "SWI": "SSO", "NRY": "NOSA", "DEN": "DTU Space",
    "AUS": "ALR", "FIN": "Business Finland Space", "IRE": "Enterprise Ireland Space", "POR": "Portugal Space", "PER": "ISA Irán",
    "UAE": "UAESA", "TUR": "TUA", "AST": "ASA", "MEX": "AEM", "SAU": "Saudi Space Agency", "EGY": "EgSA", "NIG": "NASRDA",
    "SAF": "SANSA", "MAY": "MYSA", "VEN": "ABAE", "BOL": "ABE", "NZL": "NZSA", "LUX": "LSA", "POL": "POLSA",
    "GRE": "Hellenic Space Center", "KAZ": "Kazcosmos", "AZE": "Azercosmos", "NKO": "NADA", "VIE": "VNSC", "TAI": "NSPO",
}
OPEN = "NOT = { " + " ".join(f"has_country_flag = mdr_{c[0]}_open" for c in space_program.COLONY_KEYS) + " } has_country_flag = mdr_space_open check_variable = { var_open_MD_space_gui = 2 } has_country_flag = open_MD_countrymissilesview"


def text(name, x, y, w, h, font, key, fmt="left", tip=None):
    end = f'pdx_tooltip = "{tip}"' if tip else "alwaystransparent = yes"
    return f'\t\tinstantTextboxType = {{ name = "{name}" position = {{ x = {x} y = {y} }} font = "{font}" borderSize = {{ x = 0 y = 0 }} text = "{key}" maxWidth = {w} maxHeight = {h} format = {fmt} {end} }}\n'


def panel(name, x, y, w, h):
    return f'\t\tcontainerWindowType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tsize = {{ width = {w} height = {h} }}\n\t\t\talwaystransparent = yes\n\t\t\tbackground = {{\n\t\t\t\tname = "Background"\n\t\t\t\tquadTextureSprite = "GFX_mdr_space_panel"\n\t\t\t}}\n\t\t}}\n'


def section(name, x, y, key):
    return text(name, x, y, 460, 20, "hoi_16mbs", key) + picture(name + "_rule", "GFX_mdr_space_rule", x, y + 21)


def button(name, x, y, sprite, key, tip=None):
    tooltip = f' pdx_tooltip = "{tip}"' if tip else ""
    return f'\t\tbuttonType = {{ name = "{name}" position = {{ x = {x} y = {y} }} quadTextureSprite = "{sprite}" buttonText = "{key}" buttonFont = "hoi_16mbs"{tooltip} clicksound = click_default }}\n'


def picture(name, sprite, x, y, scale=None):
    size = f" scale = {scale}" if scale else ""
    return f'\t\ticonType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x = {x} y = {y} }}{size} alwaystransparent = yes }}\n'


def tile(prefix, x, y, w, icon, label, value, tip=None):
    s = panel(prefix + "_tile", x, y, w, 84) + picture(prefix + "_icon", f"GFX_mdr_space_icon_{icon}", x + (w - 28) // 2, y + 6)
    return s + text(prefix + "_value", x, y + 36, w, 22, "hoi_18mbs", value, "center", tip) + text(prefix + "_label", x, y + 60, w, 18, "hoi_16mbs", label, "center", tip)


def shortcut_carrier(name, key):
    return f'\t\tbuttonType = {{ name = "{name}" position = {{ x = -9000 y = -9000 }} quadTextureSprite = "GFX_shield_medium" Orientation = "UPPER_LEFT" shortcut = "{key}" }}\n'


def logo_slot(i):
    return 30 + i % 4 * 78, 88 + i // 4 * 83


def name_window():
    # The intelligence agency's window (name_logo_agency_selection_window), with the same sprites and layout.
    s = '\tcontainerWindowType = {\n\t\tname = "mdr_space_name_window"\n\t\tposition = { x = -175 y = -250 }\n\t\tsize = { width = 380 height = 540 }\n\t\tOrientation = center\n\t\tclipping = no\n\t\tmoveable = yes\n\n\t\tbackground = {\n\t\t\tname = "Background"\n\t\t\tquadTextureSprite = "GFX_tiled_window_insigna"\n\t\t}\n\n'
    s += '\t\tbuttonType = { name = "mdr_space_name_close" position = { x = 342 y = 4 } spriteType = "GFX_NV_btn_close" shortcut = "ESCAPE" clicksound = click_close pdx_tooltip = "CLOSE" }\n'
    s += text("mdr_space_name_title", 18, 0, 320, 20, "hoi_36header", "MDR_SPACE_NAMING_TITLE")
    s += '\t\tcontainerWindowType = {\n\t\t\tname = "mdr_space_name_field"\n\t\t\tposition = { x = 0 y = 41 }\n\t\t\tsize = { width = 350 height = 108 }\n\t\t\tbackground = {\n\t\t\t\tname = "Background"\n\t\t\t\tposition = { x = 55 y = 3 }\n\t\t\t\tquadTextureSprite = "GFX_group_name_bg"\n\t\t\t}\n\t\t}\n'
    s += text("mdr_space_field", 62, 46, 258, 23, "hoi_18", "MDR_SPACE_FIELD", "left", "MDR_SPACE_TIP_FIELD")
    s += '\t\tbuttonType = { name = "mdr_space_cursor_left" position = { x = 30 y = 45 } quadTextureSprite = "GFX_scroll_left_gold" pdx_tooltip = "MDR_SPACE_CURSOR_TT" clicksound = click_default }\n'
    s += '\t\tbuttonType = { name = "mdr_space_cursor_right" position = { x = 325 y = 45 } quadTextureSprite = "GFX_scroll_right_gold" pdx_tooltip = "MDR_SPACE_CURSOR_TT" clicksound = click_default }\n'
    s += '\t\tcontainerWindowType = {\n\t\t\tname = "mdr_space_logo_list"\n\t\t\tposition = { x = 12 y = 73 }\n\t\t\tsize = { width = -12 height = 408 }\n\t\t\tverticalScrollbar = "right_vertical_slider"\n\t\t\tscroll_wheel_factor = 40\n\t\t\tsmooth_scrolling = yes\n\t\t\tmargin = { top = 15 left = 17 bottom = 15 right = 25 }\n\t\t\tbackground = {\n\t\t\t\tname = "Background"\n\t\t\t\tquadTextureSprite = "GFX_tiled_paper_w_frame_bg"\n\t\t\t}\n\t\t}\n'
    names = GENERIC_LOGOS + list(LOGOS)
    for n, name in enumerate(names):
        x, y = logo_slot(min(n, len(GENERIC_LOGOS)))
        s += f'\t\tbuttonType = {{ name = "mdr_space_pick_{name}" position = {{ x = {x} y = {y} }} spriteType = "GFX_mdr_space_logo_{name}" scale = 0.7 clicksound = click_default }}\n'
    for i in range(len(GENERIC_LOGOS) + 1):
        x, y = logo_slot(i)
        s += picture(f"mdr_space_ring_{i}", "GFX_mdr_space_logo_ring", x - 2, y - 2)
    s += '\t\tbuttonType = { name = "mdr_space_create" position = { x = 80 y = -49 } quadTextureSprite = "GFX_button_221x34" Orientation = "LOWER_LEFT" buttonText = "MDR_SPACE_CREATE" buttonFont = "hoi_16mbs" pdx_tooltip = "MDR_SPACE_CREATE_TT" shortcut = "RETURN" clicksound = Spy_Agency_Build_Agency_Confirm }\n'
    for c in LETTERS:
        s += shortcut_carrier(f"mdr_space_key_{c}", c) + shortcut_carrier(f"mdr_space_key_shift_{c}", f"shift+{c}")
    for name, (key, _) in OTHER_KEYS.items():
        s += shortcut_carrier(f"mdr_space_key_{name}", key)
    for name, key in (("back", "BACKSPACE"), ("delete", "DEL"), ("left", "LEFT"), ("right", "RIGHT")):
        s += shortcut_carrier(f"mdr_space_key_{name}", key)
    return s + "\t}\n\n"


def shifted(content, dx, dy):
    # Moves every element of a page by (dx, dy).
    def move(m):
        return f"position = {{ x = {int(m.group(1)) + dx} y = {int(m.group(2)) + dy} }}"
    return re.sub(r"position = \{ x = (-?\d+) y = (-?\d+) \}", move, content)


def header(width):
    s = picture("mdr_space_header", "GFX_mdr_space_header", 5, 5)
    s += text("mdr_space_title", 18, 12, 300, 20, "hoi_24header", "MDR_SPACE_TITLE")
    s += f'\t\tbuttonType = {{\n\t\t\tname = "mdr_space_close"\n\t\t\tposition = {{ x = {width - 40} y = 12 }}\n\t\t\tquadTextureSprite = "GFX_closebutton"\n\t\t\tclicksound = click_close\n\t\t}}\n'
    return s


def page_frame():
    # Figures on top, the side bar of pages, and the next step at the bottom.
    s = ""
    for n, key in enumerate(("TREASURY", "UPKEEP", "SCIENCE", "PRESTIGE")):
        x = 330 + n * 130
        s += panel(f"mdr_space_top_{n}", x, 6, 124, 42) + text(f"mdr_space_top_label_{n}", x + 10, 10, 108, 14, "hoi_16mbs", f"MDR_SPACE_TOP_{key}", "left", f"MDR_SPACE_TOP_{key}_TT")
        s += text(f"mdr_space_top_value_{n}", x + 10, 26, 108, 18, "hoi_18mbs", f"MDR_SPACE_TOP_{key}_V", "left", f"MDR_SPACE_TOP_{key}_TT")
    s += panel("mdr_space_side", SIDE_X, CONTENT_Y, SIDE_W, BAR_Y - CONTENT_Y - 8)
    y = CONTENT_Y + 8
    for group, pages in NAV_GROUPS:
        s += text(f"mdr_space_group_{group.lower()}", SIDE_X + 10, y, SIDE_W - 16, 16, "hoi_16mbs", f"MDR_SPACE_GROUP_{group}")
        y += 20
        for i in pages:
            for state, frame_ in (("off", 1), ("on", 2)):
                s += f'\t\tbuttonType = {{ name = "mdr_space_nav_{i}_{state}" position = {{ x = {SIDE_X + 4} y = {y} }} quadTextureSprite = "GFX_mdr_space_sidetab" frame = {frame_} pdx_tooltip = "MDR_SPACE_NAV_{i}" clicksound = click_checkbox }}\n'
            s += f'\t\ticonType = {{ name = "mdr_space_nav_icon_{i}" spriteType = "GFX_mdr_space_icon_{NAV_ICONS[i]}" position = {{ x = {SIDE_X + 10} y = {y + 3} }} alwaystransparent = yes }}\n'
            s += text(f"mdr_space_nav_label_{i}", SIDE_X + 42, y + 9, SIDE_W - 46, 18, "hoi_16mbs", f"MDR_SPACE_TAB_{i}")
            y += 34
        y += 12
    s += panel("mdr_space_bar", SIDE_X, BAR_Y, W - 2 * SIDE_X, 38)
    s += text("mdr_space_bar_title", SIDE_X + 14, BAR_Y + 11, 120, 18, "hoi_16mbs", "MDR_SPACE_BAR_TITLE")
    s += text("mdr_space_bar_step", CONTENT_X, BAR_Y + 11, 640, 18, "hoi_16mbs", "MDR_SPACE_NEXT_STEP")
    s += button("mdr_space_bar_go", W - SIDE_X - 82, BAR_Y + 6, "GFX_mdr_space_btn_71x26", "MDR_SPACE_GO", "MDR_SPACE_GO_TT")
    return s


def frame_window():
    # One draggable frame with everything the pages share (backdrop, header, side bar, figures, bottom bar): changing
    # page only swaps the content window inside it, so the frame keeps its position.
    s = f'\tcontainerWindowType = {{\n\t\tname = "mdr_space_frame"\n\t\tposition = {{ x = {POS_X} y = {POS_Y} }}\n\t\tsize = {{ width = {W} height = {H} }}\n\t\tOrientation = center\n\t\tmoveable = yes\n\n\t\tbackground = {{\n\t\t\tname = "Background"\n\t\t\tquadTextureSprite = "GFX_mdr_space_window"\n\t\t}}\n\n'
    return s + picture("mdr_space_backdrop", "GFX_mdr_space_backdrop", 2, 2) + header(W) + page_frame() + "\t}\n\n"


def page_window(name, content):
    # Content of one page, inside the frame, over the area right of the side bar.
    content = shifted(content, -16, -124)
    w, h = W - CONTENT_X - SIDE_X, BAR_Y - CONTENT_Y - 8
    return f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = {CONTENT_X} y = {CONTENT_Y} }}\n\t\tsize = {{ width = {w} height = {h} }}\n\t\tclipping = no\n\n' + content + "\t}\n\n"


def window(name, content, nav=True, height=H, width=W):
    if nav:
        return page_window(name, content)
    s = f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = {-width // 2} y = {-height // 2} }}\n\t\tsize = {{ width = {width} height = {height} }}\n\t\tOrientation = center\n\t\tmoveable = yes\n\n\t\tbackground = {{\n\t\t\tname = "Background"\n\t\t\tquadTextureSprite = "GFX_mdr_space_window"\n\t\t}}\n\n'
    s += header(width)
    return s + "\n" + content + "\t}\n\n"


out = "# Generated by herramientas/make_space_gui.py.\nguiTypes = {\n"
# The tab, after Millennium Dawn's four in its Space Programme (x = 10, 92, 174 and 256).
out += '\tcontainerWindowType = {\n\t\tname = "mdr_space_tab_window"\n\t\tposition = { x = 338 y = 15 }\n\t\tsize = { width = 90 height = 53 }\n\n'
for state, frame in (("off", 1), ("on", 2)):
    out += f'\t\tbuttonType = {{\n\t\t\tname = "mdr_space_tab_{state}"\n\t\t\tposition = {{ x = 0 y = 0 }}\n\t\t\tquadTextureSprite = "GFX_missiles_gui_ledger_btn"\n\t\t\tframe = {frame}\n\t\t\tpdx_tooltip = "MDR_SPACE_TAB_TT"\n\t\t\tpdx_tooltip_delayed = "MDR_SPACE_TAB_TT_DELAYED"\n\t\t\tclicksound = click_checkbox\n\t\t}}\n'
out += picture("mdr_space_tab_icon", "GFX_mdr_space_icon_programme", 31, 12)
out += "\t}\n\n"

# Summary.
Y = 124
c = picture("mdr_space_hero", "GFX_mdr_space_hero", 16, Y)
for name in list(LOGOS) + GENERIC_LOGOS:
    c += picture(f"mdr_space_logo_{name}", f"GFX_mdr_space_logo_{name}", 30, Y + 20)
c += text("mdr_space_name", 148, Y + 24, 400, 32, "hoi_24header", "MDR_SPACE_PANEL_NAME") + text("mdr_space_tier", 148, Y + 62, 400, 20, "hoi_18mbs", "MDR_SPACE_PANEL_TIER") + text("mdr_space_country", 148, Y + 88, 400, 20, "hoi_16mbs", "MDR_SPACE_PANEL_COUNTRY", "left", "MDR_SPACE_TIP_PRESTIGE")
c += picture("mdr_space_picture_usa", "GFX_nasa", 610, Y + 12, 0.64) + picture("mdr_space_picture_chi", "GFX_CHI_long_march_launch", 610, Y + 12, 0.64) + picture("mdr_space_picture_sov", "GFX_buran_event_3_SOV", 610, Y + 12, 0.64) + picture("mdr_space_picture_any", "GFX_mars_colony_2", 610, Y + 12, 0.64)
# What to do now is in the bottom bar of every page.
Y = 262
for i, (icon, key, value) in enumerate((("projects", "TECHS", "TECHS"), ("programme", "SITES", "SITES"), ("finance", "PCT", "PCT"), ("atom", "SCIENCE", "SCIENCE"), ("flask", "BONUS", "BONUS"))):
    c += tile(f"mdr_space_stat_{i}", 16 + i * 150, Y, 148, icon, f"MDR_SPACE_LBL_{key}", f"MDR_SPACE_VAL_{value}", f"MDR_SPACE_TIP_{key}")
Y = 354
c += panel("mdr_space_next_panel", 16, Y, 370, 140) + section("mdr_space_next_title", 30, Y + 10, "MDR_SPACE_NEXT_TITLE")
c += text("mdr_space_next_name", 30, Y + 42, 340, 22, "hoi_18mbs", "MDR_SPACE_NEXT_NAME") + text("mdr_space_next_hint", 30, Y + 72, 340, 44, "hoi_16mbs", "MDR_SPACE_NEXT_HINT")
c += panel("mdr_space_state_panel", 394, Y, 370, 140) + section("mdr_space_state_title", 408, Y + 10, "MDR_SPACE_GOAL_TITLE")
c += text("mdr_space_goal_name", 408, Y + 42, 340, 22, "hoi_18mbs", "MDR_SPACE_GOAL_NAME") + text("mdr_space_goal_status", 408, Y + 72, 340, 44, "hoi_16mbs", "MDR_SPACE_GOAL_STATUS")
Y = 502
c += panel("mdr_space_net_panel", 16, Y, 748, 104) + section("mdr_space_net_title", 30, Y + 10, "MDR_SPACE_NET_TITLE")
c += text("mdr_space_lease", 400, Y + 10, 350, 20, "hoi_16mbs", "MDR_SPACE_LEASE", "right")
for i, key in enumerate(("SPEED", "RELIABILITY", "COST", "SCIENCE")):
    x = 30 + i * 182
    c += text(f"mdr_space_net_value_{i}", x, Y + 48, 170, 24, "hoi_18mbs", f"MDR_SPACE_NETVAL_{key}") + text(f"mdr_space_net_label_{i}", x, Y + 78, 170, 36, "hoi_16mbs", f"MDR_SPACE_NET_{key}")
# Shortcuts with pictures, under everything.
Y = 612
CARD_EFFECTS = ""
for i, card in enumerate(space_program.CARDS):
    x = 16 + i * 150
    c += f'\t\tbuttonType = {{ name = "mdr_space_card_{i}" position = {{ x = {x} y = {Y} }} quadTextureSprite = "GFX_mdr_space_card_{i}" clicksound = click_default }}\n'
    c += text(f"mdr_space_card_label_{i}", x + 10, Y + 62, 126, 18, "hoi_16mbs", f"MDR_SPACE_CARD_{i}")
    extra = f"\t\t\t\t{card[2]}\n" if card[2] else ""
    CARD_EFFECTS += f"\t\t\tmdr_space_card_{i}_click = {{\n{extra}\t\t\t\tset_variable = {{ mdr_space_page = {card[1]} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}}\n"
out += window("mdr_space_summary_window", c)

# Finance.
Y = 124
c = picture("mdr_space_hero", "GFX_mdr_space_hero", 16, Y)
c += text("mdr_space_budget_title", 32, Y + 22, 220, 20, "hoi_16mbs", "MDR_SPACE_BUDGET_TITLE") + text("mdr_space_budget_value", 32, Y + 52, 240, 32, "hoi_24header", "MDR_SPACE_BUDGET_VALUE")
c += picture("mdr_space_budget_bar", "GFX_mdr_space_budget_bar", 400, Y + 22)
c += text("mdr_space_bar_min", 400, Y + 42, 30, 16, "hoi_16mbs", "MDR_SPACE_BAR_MIN") + text("mdr_space_bar_mark", 440, Y + 42, 44, 16, "hoi_16mbs", "MDR_SPACE_BAR_MARK", "center") + text("mdr_space_bar_max", 674, Y + 42, 30, 16, "hoi_16mbs", "MDR_SPACE_BAR_MAX", "right")
c += button("mdr_space_budget_minus", 400, Y + 76, "GFX_mdr_space_btn_71x26", "MDR_SPACE_MINUS", "MDR_SPACE_BUDGET_TT") + button("mdr_space_budget_plus", 482, Y + 76, "GFX_mdr_space_btn_71x26", "MDR_SPACE_PLUS", "MDR_SPACE_BUDGET_TT")
c += text("mdr_space_budget_hint", 564, Y + 80, 140, 20, "hoi_16mbs", "MDR_SPACE_BUDGET_HINT", "right")
Y = 262
for i, (icon, key) in enumerate((("summary", "GDP"), ("finance", "YEAR"), ("finance", "WEEK"), ("decisions", "TREASURY"))):
    c += tile(f"mdr_space_money_{i}", 16 + i * 188, Y, 184, icon, f"MDR_SPACE_LBL_{key}", f"MDR_SPACE_VAL_{key}")
# Two columns: what it returns and where the money goes, then the spending chart and the private contracts.
Y = 354
c += panel("mdr_space_return_panel", 16, Y, 370, 150) + section("mdr_space_return_title", 30, Y + 10, "MDR_SPACE_RETURN_TITLE")
for i, key in enumerate(("WEEK", "TOTAL", "RESEARCH", "SITES")):
    c += text(f"mdr_space_return_label_{i}", 30, Y + 42 + i * 26, 250, 20, "hoi_18mbs", f"MDR_SPACE_RET_{key}") + text(f"mdr_space_return_value_{i}", 280, Y + 42 + i * 26, 92, 22, "hoi_18mbs", f"MDR_SPACE_RETVAL_{key}", "right")
c += panel("mdr_space_note_panel", 394, Y, 370, 150) + section("mdr_space_note_title", 408, Y + 10, "MDR_SPACE_NOTE_TITLE")
for i, key in enumerate(("BUDGET", "PAYROLL", "TOTAL")):
    c += text(f"mdr_space_spend_label_{i}", 408, Y + 42 + i * 26, 220, 20, "hoi_18mbs", f"MDR_SPACE_SPEND_{key}", "left", "MDR_SPACE_BUDGET_NOTE") + text(f"mdr_space_spend_value_{i}", 628, Y + 42 + i * 26, 122, 20, "hoi_18mbs", f"MDR_SPACE_SPEND_{key}_V", "right", "MDR_SPACE_BUDGET_NOTE")
c += text("mdr_space_note", 408, Y + 122, 342, 20, "hoi_16mbs", "MDR_SPACE_SPEND_WHERE", "left", "MDR_SPACE_BUDGET_NOTE")
Y = 510
c += panel("mdr_space_chart_panel", 16, Y, 370, 190) + section("mdr_space_chart_title", 30, Y + 10, "MDR_SPACE_CHART_TITLE")
# Oldest year on the left: column 0 shows mdr_space_spend_4, the last one the year running.
for col in range(space_program.CHART_YEARS):
    i = space_program.CHART_YEARS - 1 - col
    x = 26 + col * 70
    c += text(f"mdr_space_chart_value_{i}", x, Y + 38, 70, 18, "hoi_16mbs", f"MDR_SPACE_CHART_V{i}", "center", "MDR_SPACE_CHART_TT")
    c += f'\t\ticonType = {{ name = "mdr_space_chart_bar_{i}" spriteType = "GFX_mdr_space_chart_bar" position = {{ x = {x + 17} y = {Y + 60} }} pdx_tooltip = "MDR_SPACE_CHART_TT" }}\n'
    c += text(f"mdr_space_chart_year_{i}", x, Y + 164, 70, 18, "hoi_16mbs", f"MDR_SPACE_CHART_Y{i}", "center")
c += panel("mdr_space_contracts_panel", 394, Y, 370, 190) + section("mdr_space_contracts_title", 408, Y + 10, "MDR_SPACE_CONTRACTS_TITLE")
c += button("mdr_space_contracts_go", 680, Y + 6, "GFX_mdr_space_btn_71x26", "MDR_SPACE_GO", "MDR_SPACE_CONTRACTS_GO_TT")
# One line per service: the company hired and what it costs.
for i, (n, _, _) in enumerate(space_program.SERVICES):
    N = n.upper()
    row_y = Y + 40 + i * 36
    c += text(f"mdr_space_fin_pc_{n}_service", 408, row_y, 200, 16, "hoi_16mbs", f"MDR_PC_SERVICE_{N}") + text(f"mdr_space_fin_pc_{n}_cost", 598, row_y + 8, 152, 18, "hoi_16mbs", f"MDR_PC_{N}_SIGNED_COST", "right")
    c += text(f"mdr_space_fin_pc_{n}_name", 408, row_y + 16, 190, 20, "hoi_18mbs", f"MDR_PC_{N}_SIGNED_NAME")
out += window("mdr_space_finance_window", c)

# No agency yet: no tabs, as there is nothing behind them.
Y = 56
c = picture("mdr_space_hero", "GFX_mdr_space_hero", 16, Y)
c += picture("mdr_space_none_picture", "GFX_astronauts", 610, Y + 12, 0.64)
c += text("mdr_space_none_title", 32, Y + 24, 560, 32, "hoi_24header", "MDR_SPACE_NONE_TITLE") + text("mdr_space_none_text", 32, Y + 66, 560, 44, "hoi_18mbs", "MDR_SPACE_NONE_TEXT")
Y = 194
c += panel("mdr_space_reqs_panel", 16, Y, 748, 140) + section("mdr_space_reqs_title", 30, Y + 10, "MDR_SPACE_REQS_TITLE")
for i in range(3):
    c += text(f"mdr_space_none_req_{i}", 30, Y + 44 + i * 30, 716, 24, "hoi_18mbs", f"MDR_SPACE_NONE_REQ_{i}")
Y = 340
c += panel("mdr_space_found_panel", 16, Y, 748, 74)
c += button("mdr_space_found", 30, Y + 20, "GFX_mdr_space_btn_123x34", "MDR_SPACE_CREATE", "MDR_SPACE_FOUND_TT")
c += text("mdr_space_none_hint", 170, Y + 16, 580, 44, "hoi_18mbs", "MDR_SPACE_NONE_HINT")
out += window("mdr_space_none_window", c, False, 430, 780)

PROGRAM = space_program.pages(text, panel, picture, button, section, tile, shortcut_carrier)
out += frame_window()
for key, page_data in PROGRAM.items():
    out += window(f"mdr_space_{key}_window", page_data[0])
# Entry of the list of launch bases.
out += '\tcontainerWindowType = {\n\t\tname = "mdr_space_site_entry"\n\t\tposition = { x = 0 y = 0 }\n\t\tsize = { width = 228 height = 22 }\n' + text("mdr_space_site_entry_text", 0, 2, 228, 18, "hoi_16mbs", "MDR_SPACE_SITE_ENTRY") + "\t}\n\n"
# On the map, like the air bases and missile sites: the game shows them from its own code, so this is a state map icon.
out += '\tcontainerWindowType = {\n\t\tname = "mdr_space_site_mapicon"\n\t\tposition = { x = 0 y = 0 }\n\t\tsize = { width = 32 height = 32 }\n\t\torientation = upper_left\n\t\tbuttonType = { name = "mdr_space_site_mapicon_btn" quadTextureSprite = "GFX_mdr_space_site_mapicon" position = { x = -3 y = -3 } pdx_tooltip = "MDR_SPACE_SITE_MAPICON_TT" }\n\t}\n\n'

out += name_window()
out = out.rstrip("\n") + "\n}\n"
with open("interface/mdr_space.gui", "wb") as f:
    f.write(out.encode("utf-8"))

# Logic.
DIRTY = "\t\tcontext_type = player_context\n\t\tdirty = global.international_systems_updated\n"
toggle = "if = { limit = { has_country_flag = mdr_space_open } clr_country_flag = mdr_space_open }\n\t\t\t\telse = {\n\t\t\t\t\tset_country_flag = mdr_space_open\n\t\t\t\t\tif = { limit = { NOT = { check_variable = { mdr_space_page > 0 } } } set_variable = { mdr_space_page = 1 } }\n\t\t\t\t\tif = { limit = { NOT = { has_country_flag = mdr_space_guide_seen } } set_country_flag = mdr_space_guide_seen set_variable = { mdr_space_page = 9 } }\n\t\t\t\t}\n\t\t\t\tmdr_space_refresh = yes"
g = "# Generated by herramientas/make_space_gui.py.\nscripted_gui = {\n"
g += f'\tmdr_space_tab_gui = {{\n\t\twindow_name = "mdr_space_tab_window"\n\t\tparent_window_name = MD_space_program_window_instance\n{DIRTY}\n\t\tvisible = {{ check_variable = {{ var_open_MD_space_gui = 2 }} has_country_flag = open_MD_countrymissilesview }}\n\n\t\teffects = {{\n\t\t\tmdr_space_tab_off_click = {{\n\t\t\t\t{toggle}\n\t\t\t}}\n\t\t\tmdr_space_tab_on_click = {{\n\t\t\t\t{toggle}\n\t\t\t}}\n\t\t}}\n\n\t\ttriggers = {{\n\t\t\tmdr_space_tab_on_visible = {{ has_country_flag = mdr_space_open }}\n\t\t\tmdr_space_tab_off_visible = {{ NOT = {{ has_country_flag = mdr_space_open }} }}\n\t\t}}\n\t}}\n\n'

def type_char(c):
    return f"{{\n\t\t\t\tset_temp_variable = {{ mdr_space_char = {CODE[c]} }}\n\t\t\t\tmdr_space_type_char = yes\n\t\t\t}}\n"


KEY_EFFECTS = ""
for c in LETTERS:
    KEY_EFFECTS += f"\t\t\tmdr_space_key_{c}_click = " + type_char(c) + f"\t\t\tmdr_space_key_shift_{c}_click = " + type_char(c.upper())
for name, (_, c) in OTHER_KEYS.items():
    KEY_EFFECTS += f"\t\t\tmdr_space_key_{name}_click = " + type_char(c)
KEY_EFFECTS += "\t\t\tmdr_space_cursor_left_click = {\n\t\t\t\tmdr_space_caret_left = yes\n\t\t\t}\n\t\t\tmdr_space_cursor_right_click = {\n\t\t\t\tmdr_space_caret_right = yes\n\t\t\t}\n"
KEY_EFFECTS += "".join(f"\t\t\tmdr_space_key_{name}_click = {{\n\t\t\t\t{effect} = yes\n\t\t\t}}\n" for name, effect in (("back", "mdr_space_erase_before"), ("delete", "mdr_space_erase_after"), ("left", "mdr_space_caret_left"), ("right", "mdr_space_caret_right")))
ALL_TAGS = " ".join(f"original_tag = {tag}" for tag in LOGOS.values())
LOGO_TRIGGERS = "".join(f"\t\t\tmdr_space_logo_{name}_visible = {{ original_tag = {tag} check_variable = {{ mdr_space_logo = 0 }} }}\n" for name, tag in LOGOS.items())
LOGO_TRIGGERS += "".join(f"\t\t\tmdr_space_logo_{name}_visible = {{ check_variable = {{ mdr_space_logo = {i + 1} }} }}\n" for i, name in enumerate(GENERIC_LOGOS))
PICK_EFFECTS = "".join(f"\t\t\tmdr_space_pick_{name}_click = {{\n\t\t\t\tset_variable = {{ mdr_space_logo = {i + 1} }}\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n" for i, name in enumerate(GENERIC_LOGOS))
PICK_EFFECTS += "".join(f"\t\t\tmdr_space_pick_{name}_click = {{\n\t\t\t\tset_variable = {{ mdr_space_logo = 0 }}\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n" for name in LOGOS)
PICK_TRIGGERS = "".join(f"\t\t\tmdr_space_pick_{name}_visible = {{ original_tag = {tag} }}\n" for name, tag in LOGOS.items())
PICK_TRIGGERS += "".join(f"\t\t\tmdr_space_ring_{i}_visible = {{ check_variable = {{ mdr_space_logo = {i + 1} }} }}\n" for i in range(len(GENERIC_LOGOS)))
PICK_TRIGGERS += f"\t\t\tmdr_space_ring_{len(GENERIC_LOGOS)}_visible = {{ check_variable = {{ mdr_space_logo = 0 }} }}\n"

def budget_step(name, delta, clamp):
    return f"\t\t\t\tadd_to_variable = {{ mdr_space_budget = {delta} }}\n\t\t\t\t{clamp}\n"


LOW = "if = { limit = { check_variable = { mdr_space_budget < 0 } } set_variable = { mdr_space_budget = 0 } }"
HIGH = "if = { limit = { check_variable = { mdr_space_budget > 500 } } set_variable = { mdr_space_budget = 500 } }"
# Refreshes the figures and Economy, as Millennium Dawn's own economy buttons do.
AFTER_BUDGET = "\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n"
FINANCE_EFFECTS = ""
# Hundredths of a percent: click 0.01%, shift 0.1%, ctrl 1%.
for name, sign, clamp in (("minus", -1, LOW), ("plus", 1, HIGH)):
    for suffix, step in (("", 1), ("_shift", 10), ("_control", 100)):
        FINANCE_EFFECTS += f"\t\t\tmdr_space_budget_{name}{suffix}_click = {{\n" + budget_step(name, sign * step, clamp) + AFTER_BUDGET + "\t\t\t}\n"
FINANCE_EFFECTS += "\t\t\tmdr_space_contracts_go_click = {\n\t\t\t\tset_variable = { mdr_space_page = 4 }\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}\n"
CHART_FRAMES = "".join(f"\t\t\tmdr_space_chart_bar_{i} = {{\n\t\t\t\tframe = mdr_space_spend_frame_{i}\n\t\t\t}}\n" for i in range(space_program.CHART_YEARS))
PAGE_PROPERTIES = {"finance": "\n\t\tproperties = {\n\t\t\tmdr_space_budget_bar = {\n\t\t\t\tframe = mdr_space_budget_frame\n\t\t\t}\n" + CHART_FRAMES + "\t\t}\n"}

# Bottom bar of every page: the Go button takes to where the next step is done.
GO_EFFECT = "\t\t\tmdr_space_bar_go_click = {\n\t\t\t\tset_variable = { mdr_space_page = 3 }\n\t\t\t\tif = { limit = { mdr_space_any_goal_ready = yes } set_variable = { mdr_space_page = 2 } }\n\t\t\t\tif = { limit = { check_variable = { mdr_space_budget < 1 } } set_variable = { mdr_space_page = 5 } }\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}\n"
GO_TRIGGER = "\t\t\tmdr_space_bar_go_visible = { NOT = { check_variable = { mdr_space_sites < 1 } } OR = { check_variable = { mdr_space_budget < 1 } mdr_space_any_goal_ready = yes check_variable = { var = mdr_space_active compare = less_than value = mdr_space_slots } } }\n"
PAGE_EFFECTS = {
    "summary": CARD_EFFECTS,
    "finance": FINANCE_EFFECTS,
    "none": "\t\t\tmdr_space_found_click = {\n\t\t\t\tset_country_flag = mdr_space_naming\n\t\t\t\tadd_to_variable = { global.international_systems_updated = 1 }\n\t\t\t}\n",
}
PAGE_TRIGGERS = {
    "summary": "\t\t\tmdr_space_lease_visible = { check_variable = { mdr_space_leased_levels > 0 } }\n\t\t\tmdr_space_picture_usa_visible = { original_tag = USA }\n\t\t\tmdr_space_picture_chi_visible = { original_tag = CHI }\n\t\t\tmdr_space_picture_sov_visible = { original_tag = SOV }\n\t\t\tmdr_space_picture_any_visible = { NOT = { original_tag = USA original_tag = CHI original_tag = SOV } }\n" + LOGO_TRIGGERS,
    "finance": "".join(f"\t\t\tmdr_space_budget_minus{s}_click_enabled = {{ check_variable = {{ mdr_space_budget > 0 }} }}\n\t\t\tmdr_space_budget_plus{s}_click_enabled = {{ check_variable = {{ mdr_space_budget < 500 }} }}\n" for s in ("", "_shift", "_control")),
    "none": "\t\t\tmdr_space_found_click_enabled = { mdr_space_can_create = yes }\n",
}
PAGE_PROPERTIES.update({key: "\n\t\tproperties = {\n" + data[4] + "\t\t}\n" for key, data in PROGRAM.items() if len(data) > 4})
PAGE_VISIBLE = {
    "summary": "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 1 }",
    "finance": "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 5 }",
    "none": "check_variable = { mdr_space_tier = 0 } NOT = { has_country_flag = mdr_space_naming } NOT = { check_variable = { mdr_space_page = 9 } }",
}
for key, data in PROGRAM.items():
    PAGE_EFFECTS[key], PAGE_TRIGGERS[key], PAGE_VISIBLE[key] = data[1], data[2], data[3]
CLOSE_EFFECT = "\t\t\tmdr_space_close_click = {\n\t\t\t\tclr_country_flag = mdr_space_open\n\t\t\t\tclr_country_flag = mdr_space_naming\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}\n"
# The shared frame: close, side bar and bottom bar. Visible whenever a page of the Programme is (the guide also shows with no agency).
g += f'\tmdr_space_frame_gui = {{\n\t\twindow_name = "mdr_space_frame"\n{DIRTY}\n\t\tvisible = {{ {OPEN} OR = {{ check_variable = {{ mdr_space_tier > 0 }} check_variable = {{ mdr_space_page = 9 }} }} }}\n\n\t\teffects = {{\n{GO_EFFECT}{CLOSE_EFFECT}'
for i in NAV:
    g += f"\t\t\tmdr_space_nav_{i}_off_click = {{\n\t\t\t\tset_variable = {{ mdr_space_page = {i} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}}\n"
g += "\t\t}\n\n\t\ttriggers = {\n"
for i in NAV:
    on = f"check_variable = {{ mdr_space_page = {i} }} check_variable = {{ mdr_space_tier > 0 }}"
    g += f"\t\t\tmdr_space_nav_{i}_on_visible = {{ {on} }}\n\t\t\tmdr_space_nav_{i}_off_visible = {{ NOT = {{ AND = {{ {on} }} }} }}\n\t\t\tmdr_space_nav_{i}_off_click_enabled = {{ OR = {{ check_variable = {{ mdr_space_tier > 0 }} check_variable = {{ mdr_space_page = 9 }} }} }}\n"
g += GO_TRIGGER + "\t\t}\n\t}\n\n"
for name in PAGE_VISIBLE:
    parent = "" if name == "none" else "\t\tparent_window_name = mdr_space_frame\n"
    g += f'\tmdr_space_{name}_gui = {{\n\t\twindow_name = "mdr_space_{name}_window"\n{parent}{DIRTY}\n\t\tvisible = {{ {OPEN} {PAGE_VISIBLE[name]} }}\n{PAGE_PROPERTIES.get(name, "")}\n\t\teffects = {{\n'
    if name == "none":
        g += CLOSE_EFFECT
    g += PAGE_EFFECTS[name] + "\t\t}\n\n\t\ttriggers = {\n"
    g += PAGE_TRIGGERS[name] + "\t\t}\n"
    if name == "agency":
        g += "\n\t\tdynamic_lists = {\n\t\t\tmdr_space_site_list = {\n\t\t\t\tarray = mdr_space_site_states\n\t\t\t\tchange_scope = yes\n\t\t\t\tentry_container = mdr_space_site_entry\n\t\t\t}\n\t\t}\n"
    g += "\t}\n\n"
g += f'\tmdr_space_name_gui = {{\n\t\twindow_name = "mdr_space_name_window"\n{DIRTY}\n\t\tvisible = {{ {OPEN} check_variable = {{ mdr_space_tier = 0 }} has_country_flag = mdr_space_naming }}\n\n\t\teffects = {{\n\t\t\tmdr_space_name_close_click = {{\n\t\t\t\tclr_country_flag = mdr_space_naming\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n\t\t\tmdr_space_create_click = {{\n\t\t\t\tclr_country_flag = mdr_space_naming\n\t\t\t\tmdr_space_create = yes\n\t\t\t}}\n' + PICK_EFFECTS + KEY_EFFECTS + "\t\t}\n\n\t\ttriggers = {\n\t\t\tmdr_space_create_click_enabled = { mdr_space_can_create = yes check_variable = { mdr_space_len > 0 } }\n" + PICK_TRIGGERS + "\t\t}\n\t}\n"
g = g.rstrip("\n") + "\n\n"
# No spaceport map icon: removed at the user's request (a scripted map icon cannot hide by zoom).
g += '}\n'
with open("common/scripted_guis/mdr_space_gui.txt", "wb") as f:
    f.write(g.encode("utf-8"))

# Keyboard: effects.
def chain(condition, action, count, start=0):
    return "".join(f"\t\t{'if' if i == start else 'else_if'} = {{ limit = {{ check_variable = {{ {condition(i)} }} }} {action(i)} }}\n" for i in range(start, count))


LAST_EMPTY = chain(lambda i: f"mdr_space_len = {i + 1}", lambda i: f"set_variable = {{ mdr_space_ch_{i} = 0 }}", MAX_CHARS)
UPDATED = "\t\tadd_to_variable = { global.international_systems_updated = 1 }\n"
e = "# Generated by herramientas/make_space_gui.py. The typed name: mdr_space_ch_0 onwards hold the characters, mdr_space_len how many,\n# mdr_space_caret how many stand before the text cursor.\n\n"
e += "# Temp variable mdr_space_char: the character to add at the cursor.\nmdr_space_type_char = {\n\tif = { limit = { check_variable = { mdr_space_len < " + str(MAX_CHARS) + " } }\n"
for i in range(MAX_CHARS - 2, -1, -1):
    e += f"\t\tif = {{ limit = {{ check_variable = {{ mdr_space_caret < {i + 1} }} check_variable = {{ mdr_space_len > {i} }} }} set_variable = {{ mdr_space_ch_{i + 1} = mdr_space_ch_{i} }} }}\n"
e += chain(lambda i: f"mdr_space_caret = {i}", lambda i: f"set_variable = {{ mdr_space_ch_{i} = mdr_space_char }}", MAX_CHARS)
e += "\t\tadd_to_variable = { mdr_space_len = 1 }\n\t\tadd_to_variable = { mdr_space_caret = 1 }\n" + UPDATED + "\t}\n}\n\n"
e += "mdr_space_erase_before = {\n\tif = { limit = { check_variable = { mdr_space_caret > 0 } }\n"
for i in range(MAX_CHARS - 1):
    e += f"\t\tif = {{ limit = {{ check_variable = {{ mdr_space_caret < {i + 2} }} check_variable = {{ mdr_space_len > {i + 1} }} }} set_variable = {{ mdr_space_ch_{i} = mdr_space_ch_{i + 1} }} }}\n"
e += LAST_EMPTY + "\t\tadd_to_variable = { mdr_space_len = -1 }\n\t\tadd_to_variable = { mdr_space_caret = -1 }\n" + UPDATED + "\t}\n}\n\n"
e += "mdr_space_erase_after = {\n\tif = { limit = { check_variable = { var = mdr_space_caret compare = less_than value = mdr_space_len } }\n"
for i in range(MAX_CHARS - 1):
    e += f"\t\tif = {{ limit = {{ check_variable = {{ mdr_space_caret < {i + 1} }} check_variable = {{ mdr_space_len > {i + 1} }} }} set_variable = {{ mdr_space_ch_{i} = mdr_space_ch_{i + 1} }} }}\n"
e += LAST_EMPTY + "\t\tadd_to_variable = { mdr_space_len = -1 }\n" + UPDATED + "\t}\n}\n\n"
e += "mdr_space_caret_left = {\n\tif = { limit = { check_variable = { mdr_space_caret > 0 } }\n\t\tadd_to_variable = { mdr_space_caret = -1 }\n" + UPDATED + "\t}\n}\n\n"
e += "mdr_space_caret_right = {\n\tif = { limit = { check_variable = { var = mdr_space_caret compare = less_than value = mdr_space_len } }\n\t\tadd_to_variable = { mdr_space_caret = 1 }\n" + UPDATED + "\t}\n}\n\n"
e += "# Country init: the real name and logo, if the country had them.\nmdr_space_load_default_name = {\n\tset_variable = { mdr_space_len = 0 }\n\tset_variable = { mdr_space_logo = 1 }\n\tif = { limit = { OR = { " + " ".join(f"original_tag = {tag}" for tag in LOGOS.values()) + " } } set_variable = { mdr_space_logo = 0 } }\n"
for n, (tag, name) in enumerate(REAL_NAMES.items()):
    word = "if" if n == 0 else "else_if"
    if len(name) > MAX_CHARS or any(ch not in CODE for ch in name):
        raise SystemExit("bad name " + name)
    e += f"\t{word} = {{ limit = {{ original_tag = {tag} }}\n"
    for i, ch in enumerate(name):
        e += f"\t\tset_variable = {{ mdr_space_ch_{i} = {CODE[ch]} }}\n"
    e += f"\t\tset_variable = {{ mdr_space_len = {len(name)} }}\n\t}}\n"
e += "\tset_variable = { mdr_space_caret = mdr_space_len }\n}\n"
with open("common/scripted_effects/mdr_space_keyboard.txt", "wb") as f:
    f.write(e.encode("utf-8"))

# Keyboard: one scripted text per position of the name.
s = "# Generated by herramientas/make_space_gui.py.\ndefined_text = {\n\tname = mdr_space_typed\n\ttext = {\n\t\tlocalization_key = MDR_SPACE_NAME_FIELD\n\t}\n}\n\n"
for i in range(MAX_CHARS + 1):
    s += f"defined_text = {{\n\tname = mdr_space_caret_{i}\n\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_caret = {i} }} }}\n\t\tlocalization_key = MDR_SPACE_CARET\n\t}}\n\ttext = {{\n\t\tlocalization_key = MDR_SPACE_CH_EMPTY\n\t}}\n}}\n\n"
for i in range(MAX_CHARS):
    s += f"defined_text = {{\n\tname = mdr_space_ch_text_{i}\n\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_len < {i + 1} }} }}\n\t\tlocalization_key = MDR_SPACE_CH_EMPTY\n\t}}\n"
    for code in range(1, len(CHARS) + 1):
        s += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_ch_{i} = {code} }} }}\n\t\tlocalization_key = MDR_SPACE_CH_{code}\n\t}}\n"
    s += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_CH_EMPTY\n\t}\n}\n\n"
with open("common/scripted_localisation/mdr_space_keyboard_loc.txt", "wb") as f:
    f.write(s.encode("utf-8"))

# Keyboard: the characters. The same in every language.
typed = "".join(f"[mdr_space_ch_text_{i}]" for i in range(MAX_CHARS))
field = "".join(f"[mdr_space_caret_{i}][mdr_space_ch_text_{i}]" for i in range(MAX_CHARS)) + f"[mdr_space_caret_{MAX_CHARS}]"
for lang in ("spanish", "english"):
    y = f"l_{lang}:\n MDR_SPACE_NAME_TYPED: \"{typed}\"\n MDR_SPACE_NAME_FIELD: \"{field}\"\n MDR_SPACE_CARET: \"|\"\n MDR_SPACE_CH_EMPTY: \"\"\n"
    y += "".join(f" MDR_SPACE_CH_{i + 1}: \"{c}\"\n" for i, c in enumerate(CHARS))
    with open(f"localisation/{lang}/mdr_space_keyboard_l_{lang}.yml", "wb") as f:
        f.write(b"\xef\xbb\xbf" + y.encode("utf-8"))
space_program.write_files()
import space_auto
space_auto.write_all()
import space_colony
space_colony.write_all()
print("ok")
