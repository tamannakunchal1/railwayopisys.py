import pygame
import heapq
import math
import random
import time

W, H = 1300, 680
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Railway Optimizing System")
clock = pygame.time.Clock()

def load_font(size, bold=False):
    for name in ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except: pass
    return pygame.font.Font(None, size)

F10   = load_font(10)
F12   = load_font(12)
F13   = load_font(13)
F14   = load_font(14)
F15   = load_font(15)
F18   = load_font(18, bold=True)
FMONO = pygame.font.SysFont("Consolas", 12) or load_font(12)

BG        = (240, 243, 250)
PANEL     = (250, 251, 255)
CARD      = (255, 255, 255)
CARD2     = (235, 242, 255)
BORDER    = (210, 218, 235)
BORDER2   = (180, 196, 220)
TEXT      = ( 30,  40,  65)
TEXT2     = ( 80,  96, 130)
TEXT3     = (140, 155, 185)
ACCENT    = ( 99, 144, 234)
ACCENT2   = ( 72, 187, 145)
WARN      = (240, 170,  70)
DANGER    = (230, 100, 100)
PURPLE    = (160, 120, 220)
TRACK_CLR = (200, 210, 228)
TRAIN_CLR = (255, 195,  60)
WHITE     = (255, 255, 255)

ALGO_COLORS = {"A*": ACCENT2, "Dijkstra": ACCENT, "BFS": WARN, "DFS": PURPLE}
ALGO_NAMES  = ["A*", "Dijkstra", "BFS", "DFS"]

LEFT_W  = 240
RIGHT_W = 285
MAP_X   = LEFT_W
MAP_W   = W - LEFT_W - RIGHT_W

ALGO_BTN_X  = 12
ALGO_BTN_Y0 = 112
ALGO_BTN_W  = LEFT_W - 24
ALGO_BTN_H  = 32
ALGO_BTN_GAP= 40

SLIDER_X = 20
SLIDER_Y = 448
SLIDER_W = LEFT_W - 40
SLIDER_H = 8

def algo_btn_rect(i):
    return pygame.Rect(ALGO_BTN_X, ALGO_BTN_Y0 + i * ALGO_BTN_GAP, ALGO_BTN_W, ALGO_BTN_H)

def slider_hit_rect():
    return pygame.Rect(SLIDER_X, SLIDER_Y - 8, SLIDER_W, SLIDER_H + 16)

_POS = {
    "Delhi":   (0.12, 0.20), "Jaipur":  (0.26, 0.43), "Agra":    (0.30, 0.12),
    "Lucknow": (0.50, 0.17), "Kanpur":  (0.50, 0.44), "Bhopal":  (0.65, 0.57),
    "Indore":  (0.70, 0.76), "Nagpur":  (0.83, 0.50), "Patna":   (0.65, 0.08),
    "Mumbai":  (0.87, 0.82),
}

def node_pos(name):
    rx, ry = _POS[name]
    return (int(MAP_X + rx * MAP_W), int(ry * H))

GRAPH = {
    "Delhi":   [("Jaipur",280), ("Agra",230)],
    "Jaipur":  [("Delhi",280),  ("Bhopal",600)],
    "Agra":    [("Delhi",230),  ("Lucknow",330)],
    "Lucknow": [("Agra",330),   ("Kanpur",90),  ("Patna",400)],
    "Kanpur":  [("Lucknow",90), ("Bhopal",500)],
    "Bhopal":  [("Kanpur",500), ("Jaipur",600), ("Mumbai",770), ("Indore",200)],
    "Indore":  [("Bhopal",200), ("Nagpur",300)],
    "Nagpur":  [("Indore",300), ("Mumbai",700)],
    "Patna":   [("Lucknow",400)],
    "Mumbai":  [("Bhopal",770), ("Nagpur",700)],
}

def rand_delay(): return random.randint(0, 28)
delays = {n: rand_delay() for n in _POS}

def euclidean(a, b):
    ax, ay = node_pos(a); bx, by = node_pos(b)
    return math.hypot(bx-ax, by-ay)

def bfs(s, g):
    q = [(s,[s])]; v = set()
    while q:
        n, p = q.pop(0)
        if n==g: return p
        if n not in v:
            v.add(n)
            for nb,_ in GRAPH[n]: q.append((nb, p+[nb]))
    return []

def dfs(s, g):
    st = [(s,[s])]; v = set()
    while st:
        n, p = st.pop()
        if n==g: return p
        if n not in v:
            v.add(n)
            for nb,_ in GRAPH[n]: st.append((nb, p+[nb]))
    return []

def astar(s, g):
    pq = [(0,0,s,[s])]; v = set(); c = 0
    while pq:
        f, gc, n, p = heapq.heappop(pq)
        if n==g: return p
        if n not in v:
            v.add(n)
            for nb,d in GRAPH[n]:
                ng = gc+d+delays[nb]; c+=1
                heapq.heappush(pq, (ng+euclidean(nb,g), ng, nb, p+[nb]))
    return []

def dijkstra(s, g):
    pq = [(0,0,s,[s])]; v = set(); c = 0
    while pq:
        cost, _, n, p = heapq.heappop(pq)
        if n==g: return p
        if n not in v:
            v.add(n)
            for nb,d in GRAPH[n]:
                c+=1; heapq.heappush(pq, (cost+d, c, nb, p+[nb]))
    return []

ALGOS = {"A*": astar, "Dijkstra": dijkstra, "BFS": bfs, "DFS": dfs}

def drect(surf, color, rect, radius=0, alpha=None):
    if alpha is not None:
        s = pygame.Surface((max(1,rect[2]), max(1,rect[3])), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), (0,0,rect[2],rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)

def brect(surf, color, rect, w=1, r=0):
    pygame.draw.rect(surf, color, rect, w, border_radius=r)

def txt(surf, s, font, color, x, y, anchor="topleft"):
    rendered = font.render(str(s), True, color)
    r = rendered.get_rect(**{anchor: (x, y)})
    surf.blit(rendered, r)
    return r

def lerp_pt(a, b, t):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)

def delay_color(d):
    return ACCENT2 if d<=8 else WARN if d<=18 else DANGER

def delay_bg(d):
    return (210,245,232) if d<=8 else (253,237,195) if d<=18 else (252,220,220)

log_lines = []
def log(msg, color=TEXT3):
    ts = time.strftime("%H:%M:%S")
    log_lines.append((ts, msg, color))
    if len(log_lines) > 60: log_lines.pop(0)

log("System ready", ACCENT2)
log("10 stations loaded", TEXT2)
log("Click a station to begin", TEXT3)

state = {
    "start": None, "goal": None, "path": [],
    "algo": "A*", "compare": {}, "stats": {},
    "train_edge": 0, "train_t": 0.0, "animating": False,
    "train_speed": 0.008, "hover_node": None, "pulse": 0.0,
}

def advance_train():
    if not state["animating"] or len(state["path"]) < 2: return
    state["train_t"] += state["train_speed"]
    if state["train_t"] >= 1.0:
        state["train_t"] = 0.0
        state["train_edge"] += 1
        if state["train_edge"] >= len(state["path"]) - 1:
            state["train_edge"] = 0
            log(f"Arrived at {state['goal']}", ACCENT2)

def train_screen_pos():
    if len(state["path"]) < 2 or state["train_edge"] >= len(state["path"])-1:
        return None
    a = node_pos(state["path"][state["train_edge"]])
    b = node_pos(state["path"][state["train_edge"]+1])
    return lerp_pt(a, b, state["train_t"])

def run_search():
    if not state["start"] or not state["goal"]: return
    fn = ALGOS[state["algo"]]
    t0 = time.perf_counter()
    p  = fn(state["start"], state["goal"])
    ms = (time.perf_counter()-t0)*1000
    state["path"] = p
    state["train_edge"] = 0
    state["train_t"] = 0.0
    state["animating"] = bool(p)
    compare = {}
    for name, fn2 in ALGOS.items():
        cp = fn2(state["start"], state["goal"])
        d  = sum(next(w for nb,w in GRAPH[cp[i]] if nb==cp[i+1])
                 for i in range(len(cp)-1)) if len(cp)>1 else 0
        compare[name] = {"stops": len(cp), "dist": d}
    state["compare"] = compare
    if p:
        td = sum(next(w for nb,w in GRAPH[p[i]] if nb==p[i+1]) for i in range(len(p)-1))
        tdelay = sum(delays[n] for n in p)
        state["stats"] = {"stops":len(p), "dist":td, "delay":tdelay, "time_ms":round(ms,2)}
        log(f"{state['algo']}: {' → '.join(p)}", ACCENT)
        log(f"{td} km · +{tdelay} min delay", ACCENT2)
    else:
        state["stats"] = {}
        log(f"No path: {state['start']} → {state['goal']}", DANGER)

def hit_node(mx, my, r=20):
    if mx < MAP_X or mx > W-RIGHT_W: return None
    for name in _POS:
        nx, ny = node_pos(name)
        if math.hypot(mx-nx, my-ny) <= r: return name
    return None

def hit_algo_btn(mx, my):
    if mx > LEFT_W: return None
    for i, name in enumerate(ALGO_NAMES):
        if algo_btn_rect(i).collidepoint(mx, my): return name
    return None

def reshuffle():
    for n in delays: delays[n] = rand_delay()
    log("Delays reshuffled", WARN)
    if state["start"] and state["goal"]: run_search()

def draw_left_panel():
    drect(screen, PANEL, (0, 0, LEFT_W, H))
    pygame.draw.line(screen, BORDER, (LEFT_W-1, 0), (LEFT_W-1, H), 1)
    drect(screen, CARD, (0, 0, LEFT_W, 76))
    pygame.draw.line(screen, BORDER, (0, 76), (LEFT_W, 76), 1)
    drect(screen, ACCENT, (14, 14, 38, 38), radius=10)
    pygame.draw.rect(screen, WHITE, (20, 24, 26, 16), border_radius=3)
    pygame.draw.circle(screen, ACCENT, (26, 41), 4)
    pygame.draw.circle(screen, ACCENT, (39, 41), 4)
    pygame.draw.circle(screen, (220,235,255), (26, 41), 2)
    pygame.draw.circle(screen, (220,235,255), (39, 41), 2)
    txt(screen, "RailAI", F18, TEXT, 60, 18)
    txt(screen, "India Network  v2.0", F12, TEXT3, 60, 40)

    txt(screen, "ALGORITHM", F10, TEXT3, 14, 88)
    pygame.draw.line(screen, BORDER, (14, 102), (LEFT_W-14, 102), 1)

    for i, name in enumerate(ALGO_NAMES):
        r    = algo_btn_rect(i)
        active = (name == state["algo"])
        clr  = ALGO_COLORS[name]
        drect(screen, CARD2 if active else CARD, r, radius=8)
        brect(screen, clr if active else BORDER, r, w=2 if active else 1, r=8)
        dot_c = clr if active else BORDER2
        pygame.draw.circle(screen, dot_c, (r.x+18, r.y+16), 6)
        if active:
            pygame.draw.circle(screen, WHITE, (r.x+18, r.y+16), 3)
        txt(screen, name, F14, TEXT if active else TEXT2, r.x+34, r.y+9)
        if active:
            pygame.draw.circle(screen, clr, (r.right-14, r.y+16), 4)

    sy_label = SLIDER_Y - 22
    txt(screen, "TRAIN SPEED", F10, TEXT3, 14, sy_label-14)
    pygame.draw.line(screen, BORDER, (14, sy_label), (LEFT_W-14, sy_label), 1)
    drect(screen, BORDER, (SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H), radius=4)
    t2 = (state["train_speed"]-0.003)/0.017
    fw = max(0, int(SLIDER_W*t2))
    if fw > 0: drect(screen, ACCENT, (SLIDER_X, SLIDER_Y, fw, SLIDER_H), radius=4)
    tx2 = SLIDER_X+fw
    pygame.draw.circle(screen, WHITE,  (tx2, SLIDER_Y+4), 9)
    pygame.draw.circle(screen, ACCENT, (tx2, SLIDER_Y+4), 7)
    txt(screen, "Slow", F12, TEXT3, SLIDER_X, SLIDER_Y+14)
    txt(screen, "Fast", F12, TEXT3, SLIDER_X+SLIDER_W, SLIDER_Y+14, anchor="topright")

    sy2 = SLIDER_Y+50
    txt(screen, "ROUTE STATS", F10, TEXT3, 14, sy2)
    pygame.draw.line(screen, BORDER, (14, sy2+14), (LEFT_W-14, sy2+14), 1)
    stats = state["stats"]
    cards = [
        ("Stops",    str(stats.get("stops","—")),        TEXT),
        ("Distance", f"{stats.get('dist','—')} km",      ACCENT),
        ("Delay",    f"{stats.get('delay','—')} min",    WARN),
        ("Computed", f"{stats.get('time_ms','—')} ms",   TEXT3),
    ]
    cw = (LEFT_W-28)//2
    for i, (lbl, val, vc) in enumerate(cards):
        cx2 = 12+(i%2)*(cw+4)
        cy2 = sy2+22+(i//2)*60
        drect(screen, CARD, (cx2, cy2, cw, 52), radius=8)
        brect(screen, BORDER, (cx2, cy2, cw, 52), r=8)
        txt(screen, lbl, F10, TEXT3, cx2+8, cy2+8)
        txt(screen, val, F14, vc,    cx2+8, cy2+26)

    py_s = sy2+162
    txt(screen, "ACTIVE PATH", F10, TEXT3, 14, py_s)
    pygame.draw.line(screen, BORDER, (14, py_s+14), (LEFT_W-14, py_s+14), 1)
    p = state["path"]
    if not p:
        txt(screen, "No route selected", F12, TEXT3, 14, py_s+22)
    else:
        px2, py2 = 14, py_s+22
        for i, node in enumerate(p):
            if i > 0:
                txt(screen, "›", F12, TEXT3, px2, py2+1)
                px2 += 10
            if px2 > LEFT_W-55:
                py2 += 16; px2 = 14
            nc = ACCENT2 if node==state["start"] else DANGER if node==state["goal"] else ACCENT
            txt(screen, node, F12, nc, px2, py2)
            px2 += F12.size(node)[0]+2

    txt(screen, "Keys: 1-4 algo  R reshuffle  ESC reset", F10, TEXT3, 8, H-18)

def draw_right_panel():
    rx = W-RIGHT_W
    drect(screen, PANEL, (rx, 0, RIGHT_W, H))
    pygame.draw.line(screen, BORDER, (rx, 0), (rx, H), 1)
    drect(screen, CARD, (rx, 0, RIGHT_W, 76))
    pygame.draw.line(screen, BORDER, (rx, 76), (W, 76), 1)
    txt(screen, "Station Monitor", F18, TEXT, rx+14, 18)
    txt(screen, "Live delay · India Rail", F12, TEXT3, rx+14, 40)

    y = 90
    txt(screen, "STATION DELAYS", F10, TEXT3, rx+14, y)
    pygame.draw.line(screen, BORDER, (rx+14, y+14), (W-14, y+14), 1)
    for i, (name, d) in enumerate(sorted(delays.items(), key=lambda x: -x[1])):
        iy = y+22+i*36
        onpath = name in state["path"]
        bg = (230,243,255) if onpath else CARD
        drect(screen, bg, (rx+12, iy, RIGHT_W-24, 28), radius=7)
        dc = delay_color(d)
        brect(screen, dc if onpath else BORDER, (rx+12, iy, RIGHT_W-24, 28), r=7)
        pygame.draw.circle(screen, dc, (rx+26, iy+14), 5)
        txt(screen, name, F13, TEXT if onpath else TEXT2, rx+38, iy+7)
        badge = f"+{d}m"
        bw = FMONO.size(badge)[0]+12
        bx2 = rx+RIGHT_W-14-bw
        drect(screen, delay_bg(d), (bx2, iy+5, bw, 18), radius=4)
        pygame.draw.rect(screen, dc, (bx2, iy+5, bw, 18), 1, border_radius=4)
        txt(screen, badge, FMONO, dc, bx2+6, iy+7)

    y2 = 466
    txt(screen, "ALGORITHM COMPARISON", F10, TEXT3, rx+14, y2)
    pygame.draw.line(screen, BORDER, (rx+14, y2+14), (W-14, y2+14), 1)
    cmp = state["compare"]
    if cmp:
        max_dist = max(v["dist"] for v in cmp.values()) or 1
        for i, name in enumerate(ALGO_NAMES):
            vy = y2+22+i*46
            data = cmp.get(name, {"stops":0,"dist":0})
            clr  = ALGO_COLORS[name]
            txt(screen, name, F13, TEXT, rx+14, vy)
            txt(screen, f"{data['stops']} stops · {data['dist']} km", FMONO, TEXT3, rx+14, vy+14)
            bw2 = RIGHT_W-28
            fill = int(bw2*data["dist"]/max_dist)
            drect(screen, BORDER, (rx+14, vy+30, bw2, 6), radius=3)
            if fill > 0: drect(screen, clr, (rx+14, vy+30, fill, 6), radius=3)
    else:
        txt(screen, "Select a route to compare", F12, TEXT3, rx+14, y2+22)

    y3 = 668
    txt(screen, "ACTIVITY LOG", F10, TEXT3, rx+14, y3)
    pygame.draw.line(screen, BORDER, (rx+14, y3+14), (W-14, y3+14), 1)
    log_h = H-y3-28
    drect(screen, CARD, (rx+12, y3+20, RIGHT_W-24, log_h), radius=7)
    brect(screen, BORDER, (rx+12, y3+20, RIGHT_W-24, log_h), r=7)
    visible = log_lines[-(log_h//18):]
    for i, (ts, msg, clr) in enumerate(visible):
        ly = y3+28+i*18
        txt(screen, ts,  FMONO, TEXT3, rx+20, ly)
        txt(screen, msg, FMONO, clr,   rx+80, ly)

def draw_map():
    for gx in range(MAP_X, MAP_X+MAP_W, 40):
        for gy in range(0, H, 40):
            pygame.draw.circle(screen, BORDER, (gx, gy), 1)

    drawn = set()
    for a in GRAPH:
        for b, dist_km in GRAPH[a]:
            key = tuple(sorted([a,b]))
            if key in drawn: continue
            drawn.add(key)
            pa, pb = node_pos(a), node_pos(b)
            on_path = (len(state["path"])>1 and
                any((state["path"][i]==a and state["path"][i+1]==b) or
                    (state["path"][i]==b and state["path"][i+1]==a)
                    for i in range(len(state["path"])-1)))
            if on_path:
                glow = pygame.Surface((W, H), pygame.SRCALPHA)
                pygame.draw.line(glow, (*ACCENT, 45), pa, pb, 10)
                screen.blit(glow, (0,0))
                pygame.draw.line(screen, ACCENT, pa, pb, 3)
            else:
                dx, dy = pb[0]-pa[0], pb[1]-pa[1]
                length = math.hypot(dx, dy)
                if length == 0: continue
                ux, uy = dx/length, dy/length
                pos = 0
                while pos < length:
                    x1 = pa[0]+ux*pos; y1 = pa[1]+uy*pos
                    x2 = pa[0]+ux*min(pos+10,length); y2 = pa[1]+uy*min(pos+10,length)
                    pygame.draw.line(screen, TRACK_CLR, (int(x1),int(y1)), (int(x2),int(y2)), 2)
                    pos += 16
            mx2, my2 = (pa[0]+pb[0])//2, (pa[1]+pb[1])//2
            lbl = str(dist_km)
            lw2 = FMONO.size(lbl)[0]+10
            drect(screen, WHITE, (mx2-lw2//2, my2-9, lw2, 18), radius=4, alpha=210)
            txt(screen, lbl, FMONO, TEXT3, mx2, my2-2, anchor="midtop")

    pulse = abs(math.sin(state["pulse"]))*0.5+0.5
    for name in _POS:
        p = node_pos(name)
        is_start = name==state["start"]
        is_goal  = name==state["goal"]
        on_path  = name in state["path"]
        is_hover = name==state["hover_node"]

        if is_start or is_goal:
            ring_r = int(22+pulse*6)
            ring_c = ACCENT2 if is_start else DANGER
            s2 = pygame.Surface((ring_r*2+6, ring_r*2+6), pygame.SRCALPHA)
            pygame.draw.circle(s2, (*ring_c, int(70*pulse)), (ring_r+3, ring_r+3), ring_r, 3)
            screen.blit(s2, (p[0]-ring_r-3, p[1]-ring_r-3))

        outer_r = 17
        if is_start:
            outer_c, fill_c, dot_c = ACCENT2, (220,248,238), ACCENT2
        elif is_goal:
            outer_c, fill_c, dot_c = DANGER,  (252,228,228), DANGER
        elif on_path:
            outer_c, fill_c, dot_c = ACCENT,  (228,238,255), ACCENT
        else:
            outer_c, fill_c, dot_c = BORDER2, WHITE,         TEXT3

        pygame.draw.circle(screen, fill_c,  p, outer_r)
        pygame.draw.circle(screen, outer_c, p, outer_r, 2)
        pygame.draw.circle(screen, dot_c,   p, 7)
        pygame.draw.circle(screen, WHITE,   p, 3)
        if is_hover and not (is_start or is_goal):
            pygame.draw.circle(screen, WARN, p, outer_r+2, 2)

        lbl = name
        lw2 = F14.size(lbl)[0]+14
        lbl_y = p[1]-32
        drect(screen, WHITE, (p[0]-lw2//2, lbl_y, lw2, 20), radius=5, alpha=220)
        pygame.draw.rect(screen, BORDER, (p[0]-lw2//2, lbl_y, lw2, 20), 1, border_radius=5)
        txt(screen, lbl, F14, TEXT if on_path else TEXT2, p[0], lbl_y+2, anchor="midtop")

        d = delays[name]
        dc = delay_color(d)
        badge = f"+{d}m"
        bw2 = FMONO.size(badge)[0]+8
        bx2 = p[0]-bw2//2
        by2 = p[1]+20
        drect(screen, delay_bg(d), (bx2, by2, bw2, 16), radius=4)
        pygame.draw.rect(screen, dc, (bx2, by2, bw2, 16), 1, border_radius=4)
        txt(screen, badge, FMONO, dc, p[0], by2+1, anchor="midtop")

    tp = train_screen_pos()
    if tp:
        tx, ty = int(tp[0]), int(tp[1])
        glow2 = pygame.Surface((36,36), pygame.SRCALPHA)
        pygame.draw.circle(glow2, (*TRAIN_CLR, 80), (18,18), 16)
        screen.blit(glow2, (tx-18, ty-18))
        pygame.draw.circle(screen, TRAIN_CLR, (tx,ty), 9)
        pygame.draw.circle(screen, WHITE,     (tx,ty), 4)
        if state["train_edge"] < len(state["path"])-1:
            ap = node_pos(state["path"][state["train_edge"]])
            bp = node_pos(state["path"][state["train_edge"]+1])
            dx, dy = bp[0]-ap[0], bp[1]-ap[1]
            length = math.hypot(dx,dy) or 1
            ux, uy = dx/length, dy/length
            pygame.draw.line(screen, TRAIN_CLR, (tx,ty), (int(tx+ux*16),int(ty+uy*16)), 2)

    lx, ly = MAP_X+12, H-76
    drect(screen, WHITE, (lx, ly, 270, 62), radius=10, alpha=230)
    pygame.draw.rect(screen, BORDER, (lx, ly, 270, 62), 1, border_radius=10)
    items = [(ACCENT2,"Origin"),(DANGER,"Destination"),(ACCENT,"Route"),(TRAIN_CLR,"Train")]
    for i, (clr, lbl) in enumerate(items):
        ix = lx+12+(i%2)*126
        iy = ly+10+(i//2)*28
        pygame.draw.circle(screen, clr, (ix+6, iy+7), 5)
        txt(screen, lbl, F12, TEXT2, ix+16, iy)

    if not state["start"]:
        hint = "Click any station to set origin"
    elif not state["goal"]:
        hint = f"Origin: {state['start']}  ·  Now click destination"
    else:
        hint = f"{state['start']} → {state['goal']}  ·  Click a station to restart"
    hw = F14.size(hint)[0]+24
    hx = MAP_X+(MAP_W-hw)//2
    drect(screen, WHITE, (hx, H-24, hw, 20), radius=10, alpha=210)
    txt(screen, hint, F14, TEXT3, hx+12, H-22)

def draw_topbar():
    drect(screen, CARD, (MAP_X, 0, MAP_W, 46))
    pygame.draw.line(screen, BORDER, (MAP_X, 46), (MAP_X+MAP_W, 46), 1)
    txt(screen, "India Railway Network", F18, TEXT, MAP_X+16, 12)
    txt(screen, "10 stations · 13 routes", F12, TEXT3, MAP_X+220, 18)
    clr = ALGO_COLORS[state["algo"]]
    lbl = f"  {state['algo']}  "
    s2 = F13.render(lbl, True, WHITE)
    pw, ph = s2.get_width()+16, s2.get_height()+6
    px2 = W-RIGHT_W-pw-16
    drect(screen, clr, (px2, 14, pw, ph), radius=ph//2)
    screen.blit(s2, (px2+8, 17))

running = True
dragging_speed = False

while running:
    clock.tick(60)
    state["pulse"] += 0.05
    mx, my = pygame.mouse.get_pos()
    state["hover_node"] = hit_node(mx, my)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state.update(start=None, goal=None, path=[], stats={}, compare={}, animating=False)
                log("Selection cleared", TEXT3)
            elif event.key == pygame.K_r:
                reshuffle()
            elif event.key == pygame.K_1:
                state["algo"] = "A*"
                if state["start"] and state["goal"]: run_search()
            elif event.key == pygame.K_2:
                state["algo"] = "Dijkstra"
                if state["start"] and state["goal"]: run_search()
            elif event.key == pygame.K_3:
                state["algo"] = "BFS"
                if state["start"] and state["goal"]: run_search()
            elif event.key == pygame.K_4:
                state["algo"] = "DFS"
                if state["start"] and state["goal"]: run_search()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if slider_hit_rect().collidepoint(mx, my):
                dragging_speed = True

            elif mx < LEFT_W:
                algo = hit_algo_btn(mx, my)
                if algo:
                    state["algo"] = algo
                    log(f"Algorithm changed to {algo}", TEXT2)
                    if state["start"] and state["goal"]:
                        run_search()

            elif MAP_X <= mx <= W - RIGHT_W:
                node = hit_node(mx, my)
                if node:
                    if not state["start"] or (state["start"] and state["goal"]):
                        state.update(start=node, goal=None, path=[], stats={},
                                     compare={}, animating=False)
                        log(f"Origin: {node}", ACCENT2)
                    elif node != state["start"]:
                        state["goal"] = node
                        log(f"Destination: {node}", DANGER)
                        reshuffle()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging_speed = False

        elif event.type == pygame.MOUSEMOTION and dragging_speed:
            t2 = max(0.0, min(1.0, (mx-SLIDER_X)/SLIDER_W))
            state["train_speed"] = 0.003 + t2*0.017

    advance_train()

    screen.fill(BG)
    draw_map()
    draw_left_panel()
    draw_right_panel()
    draw_topbar()
    pygame.display.flip()

pygame.quit()