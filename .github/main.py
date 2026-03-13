"""
Quiz Bot — by Dilshod Badriddinov
Android Kivy versiyasi
"""
import random, re, os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock

try:
    from docx import Document as DocxDoc
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

# ─── Ranglar ───
C_BG      = (0.059, 0.067, 0.090, 1)
C_CARD    = (0.102, 0.114, 0.153, 1)
C_OPT     = (0.133, 0.145, 0.227, 1)
C_ACCENT  = (0.424, 0.388, 1.000, 1)
C_SUCCESS = (0.263, 0.851, 0.549, 1)
C_FAIL    = (1.000, 0.341, 0.341, 1)
C_WARN    = (1.000, 0.820, 0.400, 1)
C_TEXT    = (0.910, 0.918, 0.965, 1)
C_DIM     = (0.482, 0.498, 0.620, 1)
C_BORDER  = (0.165, 0.180, 0.243, 1)

# ─── Parser ───
def is_sep(line):
    return bool(re.match(r'^={3,}\s*$', line))

def parse_docx(path):
    if not DOCX_OK: return []
    doc   = DocxDoc(path)
    lines = [p.text.strip() for p in doc.paragraphs]
    qs = []; i = 0
    while i < len(lines) and lines[i] != '+++++': i += 1
    while i < len(lines):
        if lines[i] != '+++++': i += 1; continue
        i += 1
        if i >= len(lines): break
        qt = lines[i].strip(); i += 1
        opts = []; cor = None
        while i < len(lines) and lines[i] != '+++++':
            if is_sep(lines[i]):
                i += 1
                while i < len(lines) and is_sep(lines[i]): i += 1
                if i < len(lines) and lines[i] not in ('+++++',''):
                    o = lines[i].strip()
                    if o.startswith('#'):
                        c = o[1:].strip()
                        if c: opts.append(c); cor = c
                    elif o and not is_sep(o): opts.append(o)
                    i += 1
            else: i += 1
        if qt and len(opts)>=2 and cor:
            qs.append({"q":qt,"options":opts,"answer":cor})
    return qs

DEMO = [
    {"q":"Python dasturlash tilini kim yaratgan?",
     "options":["Guido van Rossum","James Gosling","Linus Torvalds","Dennis Ritchie"],
     "answer":"Guido van Rossum"},
    {"q":"HTML to'liq nomi?",
     "options":["HyperText Markup Language","High Tech Modern Language",
                "Hyper Transfer Markup Link","Home Tool Markup Language"],
     "answer":"HyperText Markup Language"},
    {"q":"Ma'lumotlar bazasi tizimi?",
     "options":["MySQL","Python","HTML","CSS"],"answer":"MySQL"},
    {"q":"Internet brauzer?",
     "options":["Google Chrome","Microsoft Word","Adobe Photoshop","WinRAR"],
     "answer":"Google Chrome"},
    {"q":"CPU nima?",
     "options":["Markaziy protsessor","Markaziy printer",
                "Kompyuter tarmoq kartasi","Video karta"],
     "answer":"Markaziy protsessor"},
]

# ─── Yordamchi ───
def bg_rect(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda w,v: setattr(rect,'pos',v),
                size=lambda w,v: setattr(rect,'size',v))
    return rect

def lbl(text, size=14, color=None, bold=False, halign='left'):
    color = color or C_TEXT
    l = Label(text=text, font_size=dp(size), color=color, bold=bold,
              halign=halign, valign='middle', size_hint_y=None)
    l.bind(texture_size=lambda i,v: setattr(i,'height',v[1]+dp(6)))
    l.bind(width=lambda i,v: setattr(i,'text_size',(v,None)))
    return l

def btn(text, color=None, h=dp(52), fs=15):
    color = color or C_ACCENT
    b = Button(text=text, font_size=dp(fs), size_hint_y=None, height=h,
               background_normal='', background_color=color,
               color=(1,1,1,1), bold=True)
    return b


# ═══════════════════════════════════════════
#  INTERVAL SCREEN
# ═══════════════════════════════════════════
class IntervalScreen(Screen):
    def setup(self, all_qs, source, on_start):
        self.all_qs   = all_qs
        self.source   = source
        self.on_start = on_start   # callback(start, stop)
        self.clear_widgets()
        self._build()

    def _build(self):
        total = len(self.all_qs)
        root  = ScrollView()
        box   = BoxLayout(orientation='vertical', padding=dp(20),
                          spacing=dp(12), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        bg_rect(box, C_BG)

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(60))
        bg_rect(hdr, (0.08,0.09,0.14,1))
        hdr.add_widget(lbl("🎯  Quiz Bot", size=20, bold=True, halign='center'))
        box.add_widget(hdr)

        # Created by
        box.add_widget(lbl("created by  Dilshod Badriddinov",
                           size=11, color=C_ACCENT, halign='center'))

        box.add_widget(Label(size_hint_y=None, height=dp(10)))

        # Info karta
        info = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6),
                         size_hint_y=None, height=dp(160))
        bg_rect(info, C_CARD)
        info.add_widget(lbl("✅  Fayl muvaffaqiyatli yuklandi!", size=13,
                            color=C_SUCCESS, bold=True))
        info.add_widget(lbl(f"📄  {self.source}", size=11, color=C_DIM))
        info.add_widget(lbl(f"📊  Jami savollar soni:  {total} ta",
                            size=16, color=C_WARN, bold=True))
        info.add_widget(lbl("Interval tanlang yoki To'liq bosing:",
                            size=11, color=C_DIM))
        box.add_widget(info)

        box.add_widget(Label(size_hint_y=None, height=dp(8)))
        box.add_widget(lbl("Interval  (masalan: 1 dan 50 gacha)",
                           size=13, bold=True))

        # Dan / Gacha
        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        row.add_widget(lbl("Dan:", size=13, color=C_DIM,
                           halign='right', bold=False))
        self.t_start = TextInput(text="1", multiline=False,
                                  font_size=dp(16), size_hint_x=0.3,
                                  background_color=C_OPT, foreground_color=C_TEXT,
                                  cursor_color=C_TEXT, padding=[dp(10),dp(12)])
        row.add_widget(self.t_start)
        row.add_widget(lbl("Gacha:", size=13, color=C_DIM,
                           halign='right', bold=False))
        self.t_stop = TextInput(text=str(total), multiline=False,
                                 font_size=dp(16), size_hint_x=0.3,
                                 background_color=C_OPT, foreground_color=C_TEXT,
                                 cursor_color=C_TEXT, padding=[dp(10),dp(12)])
        row.add_widget(self.t_stop)
        box.add_widget(row)

        self.err_lbl = lbl("", size=11, color=C_WARN)
        box.add_widget(self.err_lbl)

        box.add_widget(Label(size_hint_y=None, height=dp(6)))

        b1 = btn("▶  Intervalda boshlash", C_ACCENT, h=dp(56), fs=16)
        b1.bind(on_release=self._do_interval)
        box.add_widget(b1)

        b2 = btn("⚡  To'liq boshlash  (barcha savollar)", C_SUCCESS, h=dp(56), fs=16)
        b2.bind(on_release=self._do_full)
        box.add_widget(b2)

        box.add_widget(Label(size_hint_y=None, height=dp(20)))

        root.add_widget(box)
        self.add_widget(root)

    def _do_interval(self, *a):
        total = len(self.all_qs)
        try:
            s = int(self.t_start.text)
            e = int(self.t_stop.text)
        except ValueError:
            self.err_lbl.text = "⚠  Faqat son kiriting!"; return
        if s < 1 or e > total or s > e:
            self.err_lbl.text = f"⚠  1 dan {total} gacha bo'lsin!"; return
        self.on_start(s-1, e)

    def _do_full(self, *a):
        self.on_start(0, len(self.all_qs))


# ═══════════════════════════════════════════
#  QUIZ SCREEN
# ═══════════════════════════════════════════
class QuizScreen(Screen):
    LETTERS = list("ABCDEFGH")

    def setup(self, all_qs, source, start, stop, go_interval):
        self.all_qs      = all_qs
        self.source      = source
        self.go_interval = go_interval  # interval ekraniga qaytish
        base             = all_qs[start:stop]
        self.session     = random.sample(base, len(base))
        self.idx         = 0
        self.score       = 0
        self.ans_total   = 0
        self.answered    = False
        self.clear_widgets()
        self._build_shell()
        self._show_q()

    def _build_shell(self):
        self.root_box = BoxLayout(orientation='vertical', spacing=0)
        bg_rect(self.root_box, C_BG)

        # ── Top bar ──
        top = BoxLayout(size_hint_y=None, height=dp(52),
                        padding=[dp(12),dp(6)], spacing=dp(8))
        bg_rect(top, (0.08,0.09,0.14,1))

        load_b = btn("📂", color=(0.3,0.3,0.5,1), h=dp(40), fs=18)
        load_b.size_hint_x = None
        load_b.width = dp(48)
        load_b.bind(on_release=self._load_file)
        top.add_widget(load_b)

        self.file_lbl = lbl(f"📄 {self.source}", size=9, color=C_DIM)
        top.add_widget(self.file_lbl)
        self.root_box.add_widget(top)

        # Created by
        cb = BoxLayout(size_hint_y=None, height=dp(24), padding=[0,dp(2)])
        bg_rect(cb, (0.075,0.085,0.13,1))
        c1 = lbl("created by  ", size=9, color=C_DIM, halign='right')
        c1.size_hint_x = 0.4
        cb.add_widget(c1)
        c2 = lbl("Dilshod Badriddinov", size=11, color=C_ACCENT, bold=True)
        c2.size_hint_x = 0.6
        cb.add_widget(c2)
        self.root_box.add_widget(cb)

        # ── Stats ──
        sf = BoxLayout(size_hint_y=None, height=dp(72),
                       padding=[dp(8),dp(4)], spacing=dp(6))
        bg_rect(sf, C_BG)
        self._stat_lbls = {}
        for key, ico, val, clr in [
            ("pos","📌","1/0", C_ACCENT),
            ("ok","✅","0",   C_SUCCESS),
            ("bad","❌","0",  C_FAIL),
            ("pct","📊","0%", C_WARN),
        ]:
            card = BoxLayout(orientation='vertical', padding=dp(4))
            bg_rect(card, C_CARD)
            card.add_widget(lbl(ico, size=14, halign='center'))
            vl = lbl(val, size=15, color=clr, bold=True, halign='center')
            card.add_widget(vl)
            sf.add_widget(card)
            self._stat_lbls[key] = vl
        self.root_box.add_widget(sf)

        # ── Scroll area (savol + variantlar) ──
        self.scroll = ScrollView(size_hint=(1,1))
        self.content = BoxLayout(orientation='vertical', padding=dp(12),
                                  spacing=dp(8), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        bg_rect(self.content, C_BG)
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        # ── Bottom ──
        bot = BoxLayout(size_hint_y=None, height=dp(52),
                        padding=[dp(12),dp(6)], spacing=dp(8))
        bg_rect(bot, C_BG)
        self.next_btn = btn("⏭  Keyingi savol", C_ACCENT, h=dp(44), fs=14)
        self.next_btn.bind(on_release=self._next)
        bot.add_widget(self.next_btn)
        restart_b = btn("🔄  Qayta", (0.2,0.22,0.35,1), h=dp(44), fs=14)
        restart_b.size_hint_x = 0.38
        restart_b.bind(on_release=lambda *a: self.go_interval())
        bot.add_widget(restart_b)
        self.root_box.add_widget(bot)

        self.add_widget(self.root_box)

    def _show_q(self):
        self.content.clear_widgets()
        self.answered = False

        if self.idx >= len(self.session):
            self._final(); return

        q     = self.session[self.idx]
        self.cur_q = q
        total = len(self.session)

        # Savol raqami
        self.content.add_widget(
            lbl(f"SAVOL  #{self.idx+1}  •  Jami {total} ta",
                size=10, color=C_ACCENT, bold=True))

        # Savol matni
        qt = lbl(q["q"], size=15, bold=True)
        self.content.add_widget(qt)

        # Variantlar
        opts = q["options"][:]
        random.shuffle(opts)
        self.opt_btns = []
        for i, opt in enumerate(opts):
            letter = self.LETTERS[i] if i < len(self.LETTERS) else str(i+1)
            row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6))
            bg_rect(row, C_OPT)
            badge = btn(letter, C_ACCENT, h=dp(56), fs=15)
            badge.size_hint_x = None
            badge.width = dp(44)
            row.add_widget(badge)
            opt_lbl = lbl(f"  {opt}", size=13)
            row.add_widget(opt_lbl)
            row.bind(on_touch_down=lambda inst, touch, o=opt, r=row:
                     self._check(o, r) if r.collide_point(*touch.pos) and not self.answered else None)
            self.content.add_widget(row)
            self.opt_btns.append((row, opt))

        self.res_lbl = lbl("", size=14, bold=True)
        self.content.add_widget(self.res_lbl)
        self.ans_lbl = lbl("", size=12, color=C_DIM)
        self.content.add_widget(self.ans_lbl)

        self._upd_stats()
        self.scroll.scroll_y = 1

    def _check(self, chosen, tapped_row):
        if self.answered: return
        self.answered  = True
        self.ans_total += 1
        correct = self.cur_q["answer"]

        for row, opt in self.opt_btns:
            if opt == correct:
                self._row_color(row, (0.05,0.24,0.14,1))
            elif opt == chosen and chosen != correct:
                self._row_color(row, (0.24,0.05,0.05,1))

        if chosen == correct:
            self.score += 1
            self.res_lbl.text  = "✅  To'g'ri!  +1 ball"
            self.res_lbl.color = C_SUCCESS
            self.ans_lbl.text  = ""
        else:
            self.res_lbl.text  = "❌  Noto'g'ri!"
            self.res_lbl.color = C_FAIL
            self.ans_lbl.text  = f"✔  To'g'ri javob:  {correct}"
            self.ans_lbl.color = C_SUCCESS

        self._upd_stats()

    def _row_color(self, row, color):
        row.canvas.before.clear()
        with row.canvas.before:
            Color(*color)
            Rectangle(pos=row.pos, size=row.size)
        row.bind(pos=lambda w,v: self._redraw_bg(w,color),
                 size=lambda w,v: self._redraw_bg(w,color))

    def _redraw_bg(self, widget, color):
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(*color)
            Rectangle(pos=widget.pos, size=widget.size)

    def _next(self, *a):
        if not self.answered and self.idx < len(self.session): return
        self.idx += 1
        self._show_q()

    def _final(self):
        self.content.clear_widgets()
        total = len(self.session)
        pct   = round(self.score/total*100) if total else 0
        if   pct>=86: e,m,c="🏆","Ajoyib natija!",     C_WARN
        elif pct>=71: e,m,c="🎉","Yaxshi natija!",      C_SUCCESS
        elif pct>=51: e,m,c="📚","O'rtacha natija",     C_ACCENT
        else:         e,m,c="💪","Ko'proq mashq kerak!",C_FAIL

        self.content.add_widget(Label(size_hint_y=None, height=dp(20)))
        self.content.add_widget(lbl("✦  YAKUNIY NATIJA  ✦", size=14,
                                    color=C_ACCENT, bold=True, halign='center'))
        self.content.add_widget(lbl(f"{e}  {m}", size=22, color=c,
                                    bold=True, halign='center'))
        self.content.add_widget(Label(size_hint_y=None, height=dp(10)))
        self.content.add_widget(lbl(f"To'g'ri:  {self.score}  /  {total}",
                                    size=18, color=C_TEXT, bold=True, halign='center'))
        self.content.add_widget(lbl(f"Natija:  {pct}%",
                                    size=20, color=c, bold=True, halign='center'))
        self.content.add_widget(Label(size_hint_y=None, height=dp(10)))
        self.content.add_widget(lbl(f"{total} ta savoldan {self.score} tasini to'g'ri javob berdingiz.",
                                    size=13, color=C_DIM, halign='center'))
        self.content.add_widget(Label(size_hint_y=None, height=dp(8)))
        self.content.add_widget(lbl("🔄  Qaytadan boshlash uchun pastdagi tugmani bosing.",
                                    size=12, color=C_DIM, halign='center'))
        self.next_btn.background_color = (0.2,0.22,0.35,1)
        self._upd_stats()

    def _upd_stats(self):
        total = len(self.session)
        wrong = self.ans_total - self.score
        pct   = f"{round(self.score/self.ans_total*100)}%" if self.ans_total else "0%"
        self._stat_lbls["pos"].text = f"{min(self.idx+1,total)}/{total}"
        self._stat_lbls["ok" ].text = str(self.score)
        self._stat_lbls["bad"].text = str(wrong)
        self._stat_lbls["pct"].text = pct

    def _load_file(self, *a):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        fc = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=["*.docx","*.DOCX"],
            size_hint_y=None, height=dp(400))
        content.add_widget(fc)
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        ok_b  = btn("✅  Yuklash",  C_SUCCESS, h=dp(44), fs=14)
        can_b = btn("❌  Bekor",    C_FAIL,    h=dp(44), fs=14)
        row.add_widget(ok_b); row.add_widget(can_b)
        content.add_widget(row)
        popup = Popup(title="Fayl tanlang", content=content,
                      size_hint=(0.95,0.85))
        def do_load(*a):
            if not fc.selection: return
            path = fc.selection[0]
            qs   = parse_docx(path)
            popup.dismiss()
            if not qs:
                self._msg("⚠️  Savollar topilmadi!"); return
            self.all_qs = qs
            self.source = os.path.basename(path)
            self.file_lbl.text = f"📄 {self.source} ({len(qs)})"
            self.go_interval()
        ok_b.bind(on_release=do_load)
        can_b.bind(on_release=popup.dismiss)
        popup.open()

    def _msg(self, text):
        p = Popup(title="Xabar",
                  content=lbl(text, size=14, halign='center'),
                  size_hint=(0.8,0.3))
        p.open()
        Clock.schedule_once(lambda *a: p.dismiss(), 3)


# ═══════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════
class QuizBotApp(App):
    def build(self):
        Window.clearcolor = (0.059,0.067,0.090,1)
        self.all_qs = list(DEMO)
        self.source = "Demo savollar"

        self.sm = ScreenManager(transition=SlideTransition())

        self.iv = IntervalScreen(name='interval')
        self.qv = QuizScreen(name='quiz')
        self.sm.add_widget(self.iv)
        self.sm.add_widget(self.qv)

        self._go_interval()
        return self.sm

    def _go_interval(self):
        self.iv.setup(self.all_qs, self.source, self._start_quiz)
        self.sm.current = 'interval'

    def _start_quiz(self, start, stop):
        self.qv.all_qs  = self.all_qs
        self.qv.source  = self.source
        self.qv.setup(self.all_qs, self.source, start, stop, self._go_interval)
        self.sm.current = 'quiz'

if __name__ == '__main__':
    QuizBotApp().run()
