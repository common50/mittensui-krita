# MITTENS UI ASODAOSDJASJHASK
# yes ofc i named it after my cat
# this took me so long but i like the end result

# only works on win for now imma expand it though

# there also was a whole longer "normal" boot my friend made thing but i removed it because it was corny asl
# but i commented it out so you can always put it back or remove it entirely for mem
# i did keep like a part of it as "compact boot" to recognize his effort

# k i'll be honest when this was first "done" it was messy asl so i lowkey let claude clean it up
# especially cus i was tryna fix a bug which was actually somehow in the qss file :sob:
# but then he somehow messed up everything cus he doesnt understand krita api or basic math
# so then i like had to re rewrite all this and is such a mess and i didnt dare to ask him to clean it up again
# so if there are any volunteers... (especially with the math idk i kinda did it on intuition but i took some from forums)

# so if you encounter some weird stuff / code structure its prolly cus of that

# hmu if something is wrong ill can fix it for you and sorry about any informalities. this was originally a
# personal project and usually late at night i tend to think that i am the funniest person
# ever even though i am absolutely not so i keep whatever i write down as a reminder of how "funny" i truly am

""" 
btw im going to put comments in this format cus its lowkey cleaner 
and im not doing inline comments because they clutter the code too much
"""

# IMPORTANT!!!!! if i put an _ before a function or whatever its FOR INTERNAL USE (PRIVATE)!!!
# id expect people to know this but last time someone really messed up (their copy of) the code 
# and i do NOT want to fix these kinds of things again
# i also not too long ago came to the conclusion that people dont know what i mean with internal use:
# only use these functions in their own class, dont let other code rely on it cus it will break

# -common50

#-------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------#

import os
import sys
import ctypes
import random
from krita import Extension

from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QRectF, QSize, QEvent, QObject
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QDockWidget, QWidget,
    QToolButton, QAbstractButton, QLabel, QVBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QColor, QPen, QPainterPath, QCursor, QPainter


# yess lerp ily
def lerp(a, b, t):
    return a * (1.0 - t) + b * t

# you can use my ascii cat for your own use i hereby license it under CC0 or whatever
_CAT_ASCII = [
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#=*%%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%+#%%%%%%%%%%%%%%%- ..%%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%=  .*%%%%%%%%%%%#. .. #%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%-... -#%%%%#%%*+. ... *%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%- ...  .:-::::    .. .#%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%+. ..    ....    .. ..*%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%% .                ...#%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%...          .... .. *%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%- ......      .......+%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%-....::-.   .-==:.:..*%%",
    "  %%%%%%%%@@@@@@@@%%%%%%%%%%%%+....=++:   :-+=....:%%%",
    "  %%%%%%%%@<<<<<<@%%%%%%%%%%%%%:....::. . ..:.....=%%%",
    "  %%%%%%%%@ MEOW @%%%%%%%%%%%%%=........::........*%%%",
    "  %%%%%%%%@>>>>>>@%%%%%%%%%%%%%+:. ..............:#%%%",
    "  %%%%%%%%@@@@@@@@%%%%%%%%%%%%#=..  ...    ...  ..+%%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%%%+:.                .:#%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%%#=:..                ..+%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%%*:....                ..=%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%%*:.....                ..+%%",
    "  %%%%%%%%%%%%%%%%%%%%%%%*:.......               ..*%%",
    "  %%%%%%%%%%%%%%%%%%%%%%#-.........              .:#%%",
    "  %%%%%%%%%%%%%%%%%%%%%%=.........               .-%%%",
    "  %%%%%%%%%%%%%%%%%%%%%*:....   ..               .*%%%",
    "  %%%%%%%%%%%%%%%%%%%%+.                         :#%%%",
    "  %%%%%%%%%%%%%%%%%%%*:      .....              .:%%%%",
    "  %%%%%%%%%%%%%%%%%%%-.      .....               :%%%%",
    "  %%%%%%%%%%%%%%%%%%*:       .....              .:%%%%",
    "  %%%%%%%%%%%%%%%%%%#:.       ....       ..      -%%%%",
    "  %%%%%%%%%%%%%%%%%%#:.       ....   .  ...     .=%%%%",
    "  %%%%%%%%%%%%%%%%%%#:..       ..    .          .+%%%%",
    "  %%%%%%%%%%%%%%%%%%*....      ...              .+%%%%",
    "  %%%%%%%%%%%%%%%%%%#-....     ...    .        ..#%%%%",
    "  %%%%%%%%%%%%%%%%%%%-...       ...   .        ..%%%%%",
    "  %%%%#+=--------::.....        ...   .        ..*%%%%",
    "  %%#-....                       .              .-%%%%",
]

# i got the krita ascii from the web i forgot from where though :( ill credit when i find out
_KRITA_ASCII = [
    "  ██╗  ██╗██████╗ ██╗███████╗ █████╗ ",
    "  ██║ ██╔╝██╔══██╗██║╚══██╔══██╔══██╗",
    "  █████╔╝ ██████╔╝██║   ██║   ███████║",
    "  ██╔═██╗ ██╔══██╗██║   ██║   ██╔══██║",
    "  ██║  ██╗██║  ██║██║   ██║   ██║  ██║",
    "  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝",
]


def _splash_lines(p):
    art = _CAT_ASCII if random.random() < 0.20 else _KRITA_ASCII
    return [("ASCII", row, p(30)) for row in art]


class InertialDock(QObject):
    """
    this does the bouncy stuff for like when you are dragging a docker quickly and then suddenly
    stop moving your curser so it bounces a bit.

    for some reason it makes dockers really exicted when you hold them but thats ok i get excited too sometimes
    """
    k      = 0.18
    damp   = 0.70
    drag   = 0.88
    thresh = 0.3
    tick   = 11

    def __init__(self, dock):
        super().__init__(dock)
        self._dock         = dock
        self._enabled      = True
        self._mouseIsDown  = False
        self._grab_offset  = QPoint()
        # self._sx = self._sy = 0.0
        self._currentX = self._currentY = 0.0
        self._vel_x = self._vel_y = 0.0
        self._physTimer = QTimer(self)
        self._physTimer.setInterval(self.tick)
        self._physTimer.timeout.connect(self._step)
        dock.installEventFilter(self)

    def set_active(self, v):
        self._enabled = v
        if not v:
            self._physTimer.stop()
            self._mouseIsDown = False

    def _is_on_titlebar(self, gpos):
        w = self._dock.widget()
        if w is None:
            return True
        tl = w.mapToGlobal(QPoint(0, 0))
        return not QRect(tl, w.size()).contains(gpos)

    def eventFilter(self, obj, ev):
        """
        im pretty sure (looking at my code at least) this part makes the dockers slide across the screen
        when you like throw them which i think is really cool but i dont remember why i called it
        eventfilter (or calling it that in the first place) so thats why im kinda unsure wether this is
        even actually that part so hmu if you know
        """
        if ev.type() == QEvent.MouseButtonPress and self._enabled:
            if ev.button() == Qt.LeftButton and self._dock.isFloating():
                if not self._is_on_titlebar(ev.globalPos()):
                    return False
                p = self._dock.pos()
                self._grab_offset = ev.globalPos() - p
                self._currentX, self._currentY = float(p.x()), float(p.y())
                self._vel_x = self._vel_y = 0.0
                self._mouseIsDown = True
                self._physTimer.start()
        if ev.type() == QEvent.MouseButtonRelease:
            if ev.button() == Qt.LeftButton and self._mouseIsDown:
                self._mouseIsDown = False
        return False

    def _step(self):
        if not self._dock.isFloating():
            self._physTimer.stop(); self._mouseIsDown = False; return
        if self._mouseIsDown and not (QApplication.mouseButtons() & Qt.LeftButton):
            self._mouseIsDown = False
        if self._mouseIsDown:
            cur = QCursor.pos()
            targetX = float(cur.x() - self._grab_offset.x())
            targetY = float(cur.y() - self._grab_offset.y())
            # was trying to add acceleration multiplier here but it made everything explode
            # accelX = (targetX - self._currentX) * self._accel
            # accelY = (targetY - self._currentY) * self._accel
            # self._vel_x = (self._vel_x + accelX) * self.damp
            # self._vel_y = (self._vel_y + accelY) * self.damp
            # self._vel_x = (self._vel_x + (targetX - self._currentX) * self.k) * self.damp
            errX = targetX - self._currentX
            errY = targetY - self._currentY
            self._vel_x = self._vel_x + errX * self.k
            self._vel_x = self._vel_x * self.damp
            self._vel_y = self._vel_y + errY * self.k
            self._vel_y = self._vel_y * self.damp
            self._currentX += self._vel_x; self._currentY += self._vel_y
            # print(f"[InertialDock] held pos=({self._currentX:.1f},{self._currentY:.1f}) vel=({self._vel_x:.2f},{self._vel_y:.2f})")
            self._dock.move(int(self._currentX), int(self._currentY))
        else:
            coastingSpeed = abs(self._vel_x) + abs(self._vel_y)
            # print(f"[InertialDock] coasting coastingSpeed={coastingSpeed:.3f}")
            if coastingSpeed < self.thresh:
                self._vel_x = self._vel_y = 0.0; self._physTimer.stop(); return
            self._currentX += self._vel_x; self._currentY += self._vel_y
            self._vel_x *= self.drag; self._vel_y *= self.drag
            self._dock.move(int(self._currentX), int(self._currentY))


class Pill(QWidget):
    """
    idk where the term Pill comes from but thats what this is called ig
    
    its basically a lil green rect that follows your mouse when you are hovering above buttons
    (some of the button stuff is in a different spot in the code)

    i did get the pill appearance from some random forum (was allowed) 
    and the pill itself looks vibecoded asl tho i changed the code itself up a lil
    but hey it works so its not a problem

    also i did a lot of debugging to this part cus of things that werent even connected to this so
    it might look / work weird but if it works it works ✌️😂 (i had to copy the emojis in cus i
    """
    tick   = 16
    speed  = 0.22
    fill   = QColor(0, 255, 148,  38)
    border = QColor(0, 255, 148, 140)
    glow   = QColor(0, 255, 148,  16)

    def __init__(self, bar):
        super().__init__(bar)
        self._toolbar      = bar
        self._on       = True
        self._alive    = False
        # self._cx = self._cy = self._cw = self._ch = 0.0
        self._drawX = self._drawY = self._drawW = self._drawH = 0.0
        self._wantedX = self._wantedY = self._wantedW = self._wantedH = 0.0
        self._moveTimer = QTimer(self)
        self._moveTimer.setInterval(self.tick)
        self._moveTimer.timeout.connect(self._animStep)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._fit()
        self._registerBtns()
        bar.installEventFilter(self)
        self.raise_(); self.show()

    def set_active(self, v):
        self._on = v
        if not v:
            self._alive = False; self._moveTimer.stop(); self.update()

    def reset(self):
        self._alive = False; self._moveTimer.stop()
        self._drawW = self._drawH = 0.0; self.update(); self._fit()

    def _fit(self):
        self.setGeometry(0, 0, self._toolbar.width(), self._toolbar.height())
        self.raise_()

    @staticmethod
    def _ok(btn):
        from PyQt5.QtWidgets import QAbstractSpinBox, QComboBox, QScrollBar, QSlider
        if not isinstance(btn, QAbstractButton):
            return False
        p = btn.parent()
        while p:
            if isinstance(p, (QAbstractSpinBox, QComboBox, QScrollBar, QSlider)):
                return False
            p = p.parent()
        return True

    def _registerBtns(self):
        for btn in self._toolbar.findChildren((QToolButton, QAbstractButton)):
            if self._ok(btn):
                btn.installEventFilter(self)

    def _get_button_rect(self, btn):
        return QRect(btn.mapTo(self._toolbar, QPoint(0, 0)), btn.size())

    def _onHoverEnter(self, btn):
        r = self._get_button_rect(btn)
        self._wantedX, self._wantedY = float(r.x()), float(r.y())
        self._wantedW, self._wantedH = float(r.width()), float(r.height())
        if not self._alive:
            # self._drawX = self._wantedX; self._drawY = self._wantedY
            self._drawX = self._wantedX + self._wantedW * 0.5
            self._drawY = self._wantedY + self._wantedH * 0.5
            self._drawW = self._drawH = 0.0
            self._alive = True
            # print(f"[Pill] spawn at ({self._drawX:.0f},{self._drawY:.0f})")
        self._moveTimer.start()

    def _onHoverLeave(self):
        QTimer.singleShot(80, self._checkShouldHide)

    def _checkShouldHide(self):
        if not self._alive or not self._on: return
        pos = self._toolbar.mapFromGlobal(QCursor.pos())
        for btn in self._toolbar.findChildren((QToolButton, QAbstractButton)):
            if self._ok(btn) and btn.isVisible() and btn.geometry().contains(pos):
                return
        self._wantedW = self._wantedH = 0.0
        self._moveTimer.start()

    def _animStep(self):
        self._drawX = lerp(self._drawX, self._wantedX, self.speed)
        self._drawY = lerp(self._drawY, self._wantedY, self.speed)
        self._drawW = lerp(self._drawW, self._wantedW, self.speed)
        self._drawH = lerp(self._drawH, self._wantedH, self.speed)
        self.raise_(); self.update()
        xDone = abs(self._drawX - self._wantedX) < 0.4
        yDone = abs(self._drawY - self._wantedY) < 0.4
        wDone = abs(self._drawW - self._wantedW) < 0.4
        hDone = abs(self._drawH - self._wantedH) < 0.4
        if xDone and yDone and wDone and hDone:
            self._drawX, self._drawY = self._wantedX, self._wantedY
            self._drawW, self._drawH = self._wantedW, self._wantedH
            if self._drawW < 1.0: self._alive = False
            self._moveTimer.stop()
            # print(f"[Pill] converged -> alive={self._alive} curW={self._drawW:.2f}")
            # if not self._alive:
            #     print(f"[Pill] pill died, bar={self._toolbar.windowTitle()!r}")
            #     self._drawX = self._drawY = 0.0

    def eventFilter(self, obj, ev):
        """
        to do: add comment
        """
        if obj is self._toolbar:
            if ev.type() == QEvent.Resize: self._fit()
            elif ev.type() == QEvent.ChildAdded:
                QTimer.singleShot(100, self._registerBtns)
            return False
        if isinstance(obj, (QToolButton, QAbstractButton)):
            if ev.type() == QEvent.HoverEnter and self._on: self._onHoverEnter(obj)
            elif ev.type() == QEvent.HoverLeave: self._onHoverLeave()
        return False

    def paintEvent(self, _):
        if not self._alive or not self._on or self._drawW < 2 or self._drawH < 2: return
        pad = 3.0
        # rx = self._drawX + pad; ry = self._drawY + pad
        rx = self._drawX + pad
        ry = self._drawY + pad
        rw, rh = self._drawW - (pad + pad), self._drawH - (pad + pad)
        if rw < 1 or rh < 1: return
        # if rw < 1 or rh < 1:
        #     print(f"[Pill] paintEvent bail: rw={rw:.1f} rh={rh:.1f}")
        #     return
        rad = 5.0
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gp = QPainterPath()
        glowExpand = 4
        gp.addRoundedRect(QRectF(rx - glowExpand, ry - glowExpand, rw + glowExpand * 2, rh + glowExpand * 2), rad + glowExpand, rad + glowExpand)
        painter.setPen(Qt.NoPen); painter.setBrush(self.glow); painter.drawPath(gp)
        fp = QPainterPath()
        fp.addRoundedRect(QRectF(rx, ry, rw, rh), rad, rad)
        painter.setBrush(self.fill); painter.drawPath(fp)
        outlinePen = QPen(self.border); outlinePen.setWidthF(1.2)
        painter.setPen(outlinePen); painter.setBrush(Qt.NoBrush); painter.drawPath(fp)
        painter.end()


class IdleFade(QObject):
    """
    so what this one does is if the users cursor is not close to a FLOATING dock for a set amount of time,
    the dock decreases its opacity so they can see whats behind it
    """
    idle_ms  = 3000
    dim      = 0.25
    fade_ms  = 30
    step     = 0.04

    def __init__(self, dock):
        super().__init__(dock)
        self._dock      = dock
        self._currentOpacity   = 1.0
        self._wanted_opacity  = 1.0
        self._on        = True
        dock.installEventFilter(self)
        dock.topLevelChanged.connect(self._dockFloatStateChanged)
        self._countdownTimer = QTimer(self)
        self._countdownTimer.setSingleShot(True)
        self._countdownTimer.setInterval(self.idle_ms)
        self._countdownTimer.timeout.connect(self._beginFadeOut)
        self._opacityStepTimer = QTimer(self)
        self._opacityStepTimer.setInterval(self.fade_ms)
        self._opacityStepTimer.timeout.connect(self._opacityStep)

    def _dockFloatStateChanged(self, floating):
        self._countdownTimer.stop(); self._opacityStepTimer.stop()
        self._currentOpacity = self._wanted_opacity = 1.0
        self._dock.setWindowOpacity(1.0)
        if floating and self._on:
            self._countdownTimer.start()

    def set_active(self, v):
        self._on = v
        if not v:
            self._countdownTimer.stop(); self._opacityStepTimer.stop()
            self._currentOpacity = self._wanted_opacity = 1.0
            if self._dock.isFloating():
                self._dock.setWindowOpacity(1.0)

    def _cancelFade(self):
        if not self._on or not self._dock.isFloating(): return
        self._countdownTimer.start()
        if self._currentOpacity < 1.0:
            self._wanted_opacity = 1.0; self._opacityStepTimer.start()

    def _beginFadeOut(self):
        if not self._on or not self._dock.isFloating(): return
        self._wanted_opacity = self.dim; self._opacityStepTimer.start()

    def _opacityStep(self):
        if self._currentOpacity < self._wanted_opacity:
            self._currentOpacity = self._currentOpacity + self.step
            if self._currentOpacity > self._wanted_opacity:
                self._currentOpacity = self._wanted_opacity
        else:
            self._currentOpacity = self._currentOpacity - self.step
            if self._currentOpacity < self._wanted_opacity:
                self._currentOpacity = self._wanted_opacity
        if self._dock.isFloating():
            self._dock.setWindowOpacity(self._currentOpacity)
        diff = abs(self._currentOpacity - self._wanted_opacity)
        # print(f"[IdleFade] opacity={self._currentOpacity:.3f} target={self._wanted_opacity:.3f} diff={diff:.4f}")
        if diff < 0.001:
            self._currentOpacity = self._wanted_opacity; self._opacityStepTimer.stop()

    def eventFilter(self, obj, ev):
        if ev.type() in (QEvent.Enter, QEvent.MouseButtonPress,
                         QEvent.MouseButtonRelease, QEvent.KeyPress):
            self._cancelFade()
        return False

    def peek(self):
        if not self._on or not self._dock.isFloating() or self._wanted_opacity >= 1.0: return
        if self._currentOpacity < 0.4:
            self._wanted_opacity = 0.4; self._opacityStepTimer.start()

    def unpeek(self):
        if not self._on or not self._dock.isFloating() or self._wanted_opacity >= 1.0: return
        self._wanted_opacity = self.dim; self._opacityStepTimer.start()


class DockPeek(QObject):
    """
    this one lets the user peek the docker by moving the cursor not completely onto the docker but close by
    which makes the opacity increase but not fully
    (applies to the idlefade dockers ofc)
    """
    radius  = 100
    poll_ms = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registered_docks = []
        self._peekingSet = set()
        self._cursorPollTimer = QTimer(self)
        self._cursorPollTimer.setInterval(self.poll_ms)
        self._cursorPollTimer.timeout.connect(self._poll)
        self._cursorPollTimer.start()

    def register(self, dock, fader):
        self._registered_docks.append((dock, fader))

    def _poll(self):
        cur  = QCursor.pos()
        dead = []
        for entry in list(self._registered_docks):
            dock, fader = entry
            try:
                if not dock.isVisible(): continue
                tl = dock.mapToGlobal(QPoint(0, 0))
                gr = QRect(tl, dock.size())
            except RuntimeError:
                dead.append(entry); self._peekingSet.discard(id(fader)); continue
            except Exception:
                continue
            r      = self.radius
            inside = gr.contains(cur)
            # expandedRect = gr.adjusted(-r, -r, r, r)
            expandedRect = gr.adjusted(-r, -r, r, r)
            near   = expandedRect.contains(cur) and not inside
            fid    = id(fader)
            # if inside or near:
            #     print(f"[DockPeek] dock={dock.windowTitle()!r} inside={inside} near={near} fid={fid}")
            if inside:
                self._peekingSet.discard(fid); fader._cancelFade()
            elif near and fid not in self._peekingSet:
                self._peekingSet.add(fid); fader.peek()
            elif not near and fid in self._peekingSet:
                self._peekingSet.discard(fid); fader.unpeek()
        for d in dead: self._registered_docks.remove(d)


class ShardDissolve(QWidget):
    """
    super nonchalant exit transition from the boot to krita itself

    it makes like rects appear at the end and it messes with its color and then
    it makes the rects disappear by flickering

    this works by grabbing a 'picture' of the end terminal, then putting that ontop of krita
    and moving the boot terminal to the back which then reveals the terminal pic ontop of krita.
    the transition is then applied to the terminal pic which reveals krita itself
    """
    tick   = 16
    colors = [
        QColor(255,   0, 128), QColor(255,  60,   0), QColor(255, 220,   0),
        QColor(  0, 255, 148), QColor(  0, 220, 255), QColor(180,   0, 255),
        QColor(255, 255, 255), QColor(255, 100,   0), QColor(  0, 255,  80),
        QColor(255,   0, 255),
    ]

    def __init__(self, pixmap, main_win, on_close=None):
        super().__init__(main_win)
        self._done_callback   = on_close
        self._pixmap     = pixmap
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        sg    = QApplication.primaryScreen().geometry()
        local = main_win.mapFromGlobal(sg.topLeft())
        self.setGeometry(local.x(), local.y(), sg.width(), sg.height())
        self.raise_(); self.show()
        pixmapWidth, pixmapHeight = pixmap.width(), pixmap.height()

        def cuts(total, n):
            pts = sorted(
                random.randint(
                    (total * k) // (n + 1),
                    (total * (k + 1)) // (n + 1)
                )
                for k in range(1, n)
            )
            return [0] + pts + [total]

        xs = cuts(pixmapWidth, random.randint(4, 8))
        ys = cuts(pixmapHeight, random.randint(4, 7))
        self._shards    = []
        self._remaining = 0
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                self._shards.append({
                    "src":   QRect(xs[i], ys[j], xs[i+1]-xs[i], ys[j+1]-ys[j]),
                    "jitter": 0,
                    "shake":  random.randint(4, 18),
                    "color":  random.choice(self.colors),
                    "flash":  0.0,
                    "die":    random.randint(150, 650),
                    "delay":  random.randint(0, 500),
                    "alive":  True,
                    "going":  False,
                })
                self._remaining += 1
        self._time_ms = 0
        self._dissolveTimer = QTimer(self)
        self._dissolveTimer.setInterval(self.tick)
        self._dissolveTimer.timeout.connect(self._animStep)
        self._dissolveTimer.start()

    def _animStep(self):
        self._time_ms += self.tick
        # print(f"[ShardDissolve] t={self._time_ms} remaining={self._remaining}")
        for s in self._shards:
            if not s["alive"]: continue
            if not s["going"]:
                if self._time_ms < s["delay"]: continue
                s["going"] = True; s["die"] += self._time_ms
            s["jitter"] = random.randint(-s["shake"], s["shake"])
            s["flash"]  = random.uniform(0.3, 0.95)
            s["color"]  = random.choice(self.colors)
            if self._time_ms >= s["die"]:
                s["alive"] = False; self._remaining -= 1
        self.update()
        if self._remaining <= 0:
            self._dissolveTimer.stop()
            if self._done_callback: QTimer.singleShot(60, self._done_callback)
            QTimer.singleShot(120, self.close)

    def paintEvent(self, _):
        p = QPainter(self)
        for s in self._shards:
            if not s["alive"]: continue
            dx = s["src"].x() + s["jitter"]
            dy = s["src"].y() + s["jitter"]
            # dx, dy = s["src"].x() + s["jitter"], s["src"].y() + s["jitter"]
            p.drawPixmap(dx, dy, self._pixmap,
                         s["src"].x(), s["src"].y(), s["src"].width(), s["src"].height())
            if s["flash"] > 0.01:
                flashColor = QColor(s["color"]); flashColor.setAlphaF(s["flash"])
                p.fillRect(dx, dy, s["src"].width(), s["src"].height(), flashColor)
        p.end()


def _boot_lines(mode="normal"):
    """
    this is just the lines for the boot animation thingy its quite elementaru
    its like the most unfunny stuff ever but my friends said that thats what makes it funny so i wont touch it

    based on linux
    """
    random.seed()
    quips = [
        ("sudo apt install furry-femboys",           "gang. WHAT are you installing",                      True),
        ("sudo apt install mittens",                 "already installed (obviously)",                      False),
        ("sudo rm -fr",                              "fym -fr?? did you even try spelling it correctly?",  False),
        ("sudo apt install second-monitor",          "E: insufficient funds\nE: have you tried a job",     True),
        ("git push origin main --force",             "fatal: you absolute moron",                          True),
        ("sudo apt install working-drivers",         "i wish bro 😭 ",                                     True),
        ("pip install motivation",                   "ERROR: could not find a version that satisfies motivation", False),
        ("sudo apt-get fix everything",              "E: invalid operation 'fix everything'\nE: have you tried crying", True),
        ("sudo renice -20 krita",                    "renice: permission denied\nrenice: maybe ask nicely", True),
        ("ffmpeg -i timelapse.mp4 -vf 'setpts=0.5*PTS' out.mp4",
         "ffmpeg: no such file 'timelapse.mp4'\nffmpeg: did you forget to record again",                   False),
        ("chmod +x bitcoin.sh && ./bitcoin_gen.sh",      "bash: bitcoin_gen.sh: no such file or directory",        True),
        ("find / -name 'motivation' 2>/dev/null",    "find: no results\nfind: checked everywhere",         False),
    ]
    chosenCmd, chosenResp, do_freak = random.choice(quips)
    speedMult = 0.65 if mode == "compact" else 1.0
    def p(ms): return max(20, int(ms * speedMult))

    if mode == "compact":
        lines = [
            ("SYS",      "mittens_ui :: kernel interface v15.0.0",                   0),
            ("PAUSE",    "",                                                          p(180)),
            ("INIT",     "Qt5 + PyQt5... ok",                                        p(40)),
            ("MEM",      "dock pool [32mb]... ok",                                   p(40)),
            ("GPU",      "OpenGL compositor... mesa 23.1.4  |  shader cache 847",    p(40)),
            ("FONT",     "JetBrains Mono... ok",                                     p(40)),
            ("QSS",      "mittens_theme.qss... 312 rules",                           p(40)),
            ("PAUSE",    "",                                                          p(120)),
            ("DOCK",     "Layers / Brushes / Color / Tools / Overview / Adv.Color... ok", p(50)),
            ("PAUSE",    "",                                                          p(300)),
            ("PHYS",     "spring physics... ok",                                     p(30)),
            ("PILL",     "hover indicators... ok",                                   p(30)),
            ("FADE",     "idle fade... ok",                                          p(30)),
            ("PEEK",     "cursor tracker... ok",                                     p(30)),
            ("PAUSE",    "",                                                          p(500)),
            ("SYS",      "─" * 52,                                                   0),
            ("PROMPT",   "root@mittens:~# ",                                         0),
            ("PAUSE",    "",                                                          random.randint(p(800), p(1200))),
            ("TYPE",     chosenCmd,                                                   p(180)),
            ("PAUSE",    "",                                                          p(600)),
            *[("RESPONSE", f"  > {l}", p(120)) for l in chosenResp.split("\n")],
            ("PAUSE",    "",                                                          p(800)),
            ("RESPONSE", "  > whatever. launching krita",                            p(150)),
            ("PAUSE",    "",                                                          p(600)),
            ("SYS",      "launching krita...",                                       p(120)),
            ("PAUSE",    "",                                                          p(300)),
            *_splash_lines(p),
            ("PAUSE",    "",                                                          p(2000)),
            ("BLANK",    "",                                                          p(250)),
        ]
        return lines

    # lines = [
    #     ("SYS",   "mittens_ui :: kernel interface v15.0.0",               25),
    #     ("PAUSE", "",                                                      p(350)),
    #     ("INIT",  "loading Qt5 display server... ok",                     p(400)),
    #     ("INIT",  "binding PyQt5 event loop... ok",                       p(220)),
    #     ("MEM",   "allocating dock widget pool [32mb]... ok",             p(460)),
    #     ("INIT",  "initialising krita extension bus... ok",               p(300)),
    #     ("PAUSE", "",                                                      p(180)),
    #     ("GPU",   "detecting OpenGL compositor... mesa 23.1.4",           p(560)),
    #     ("GPU",   "shader cache warm... 847 entries",                     p(25)),
    #     ("FONT",  "loading JetBrains Mono [400 500 700]... ok",           p(280)),
    #     ("QSS",   "parsing mittens_theme.qss... 312 rules",               p(400)),
    #     ("QSS",   "scoping stylesheet to qwindow()... ok",                p(25)),
    #     ("PAUSE", "",                                                      p(180)),
    #     ("DOCK",  "scanning QDockWidget tree...",                          0),
    #     ("PAUSE", "",                                                      p(260)),
    #     ("DOCK",  "  found: Layers              [attached]",              p(35)),
    #     ("DOCK",  "  found: Brushes             [attached]",              p(35)),
    #     ("DOCK",  "  found: Color               [attached]",              p(35)),
    #     ("DOCK",  "  found: Tool Options        [attached]",              p(35)),
    #     ("DOCK",  "  found: Overview            [attached]",              p(35)),
    #     ("DOCK",  "  found: Advanced Color Sel  [attached]",              p(35)),
    #     ("PAUSE", "",                                                      p(220)),
    #     ("PHYS",  "spring physics (k=0.18 damp=0.70)... ok",              p(30)),
    #     ("PILL",  "hover indicators... ok",                               p(30)),
    #     ("FADE",  "idle fade (3s → 25%)... ok",                           p(30)),
    #     ("PEEK",  "proximity tracker (r=100px)... ok",                    p(30)),
    #     ("PAUSE", "",                                                      p(260)),
    #     ("SYS",   "─" * 52,                                               0),
    #     ("PROMPT","root@mittens:~# ",                                      0),
    #     ("PAUSE", "",                                                      random.randint(p(1600), p(2200))),
    #     ("TYPE",  chosenCmd,                                               p(220)),
    #     ("PAUSE", "",                                                      p(160)),
    #     *[("RESPONSE", f"  > {l}", p(180)) for l in chosenResp.split("\n")],
    # ]
    # lines = [
    # ("SYS",      "mittens_ui :: kernel interface v15.0.0",               0),
    # ("PAUSE",    "",                                                      p(260)),
    # ("SYS",      "─" * 52,                                               0),
    # ("PROMPT",   "root@mittens:~# ",                                      0),
    # ("PAUSE",    "",                                                      random.randint(p(1600), p(2200))),
    # ("TYPE",     chosenCmd,                                               p(220)),
    # ("PAUSE",    "",                                                      p(160)),
    # *[("RESPONSE", f"  > {l}", p(180)) for l in chosenResp.split("\n")],
    # ]

    # if do_freak:
    # lines += [
    # ("PAUSE",    "",                                                              p(200)),
    # ("RESPONSE", "  > you know what fine i'll do it myself",                     p(300)),
    # ("PAUSE",    "",                                                              p(150)),
    # ("SYS",      "root@mittens:~# sudo rm -rf / --no-preserve-root",             p(120)),
    # ("PAUSE",    "",                                                              p(80)),
    # ("RESPONSE", "  > removing /bin/bash...",                                    p(60)),
    # ("RESPONSE", "  > removing /usr/bin/python3...",                             p(60)),
    # ("RESPONSE", "  > removing /usr/lib/libQt5Core.so.5...",                     p(60)),
    # ("PAUSE",    "",                                                              p(120)),
    # ("PROMPT",   "root@mittens:~# ",                                             0),
    # ("PAUSE",    "",                                                              p(200)),
    # ("TYPE",     "^C",                                                            p(120)),
    # ("PAUSE",    "",                                                              p(80)),
    # ("RESPONSE", "  > i dont think that worked",                                  p(80)),
    # ("PAUSE",    "",                                                              p(60)),
    # ("RESPONSE", "  > removing /etc/hosts...",                                   p(60)),
    # ("RESPONSE", "  > removing /home/user/art-wip-FINAL-v3-USE-THIS-ONE.kra...", p(100)),
    # ("RESPONSE", "  > removing /home/user/ref images/do not delete/...",         p(80)),
    # ("PAUSE",    "",                                                              p(120)),
    # ("PROMPT",   "root@mittens:~# ",                                             0),
    # ("PAUSE",    "",                                                              p(100)),
    # ("TYPE",     "^C^C^C^C",                                                     p(120)),
    # ("PAUSE",    "",                                                              p(80)),
    # ("RESPONSE", "  > bro",                                                      p(80)),
    # ("PAUSE",    "",                                                              p(60)),
    # ("RESPONSE", "  > removing /proc/cats...",                                   p(60)),
    # ("RESPONSE", "  > removing /var/lib/krita/brushes/...",                      p(80)),
    # ("RESPONSE", "  > removing /var/lib/krita/palettes/...",                     p(80)),
    # ("PAUSE",    "",                                                              p(150)),
    # ("PROMPT",   "root@mittens:~# ",                                             0),
    # ("PAUSE",    "",                                                              p(250)),
    # ("TYPE",     "sudo kill -9 -1",                                              p(180)),
    # ("PAUSE",    "",                                                              p(120)),
    # ("RESPONSE", "  > wont work, but at least you gave it a shot",                p(100)),
    # ("PAUSE",    "",                                                              p(120)),
    # ("RESPONSE", "  > ████████████████████████████ 100%",                        p(200)),
    # ]
    # else:
    # lines += [
    # ("PAUSE",    "",                                                        p(120)),
    # ("RESPONSE", "  > shocking. have you tried turning it off and on again", p(100)),
    # ("PAUSE",    "",                                                        p(80)),
    # ("RESPONSE", "  > no? okay. doing it myself then",                     p(200)),
    # ]

    # def _addr():
    # return f"0x{random.randint(0x7f0000000000, 0x7fffffffffff):012x}"

    # def _hex_row():
    # addr = _addr()
    # hx   = " ".join(f"{random.randint(0,255):02x}" for _ in range(16))
    # ch   = "".join(
    # chr(b) if 32 <= b < 127 else "."
    # for b in [random.randint(0, 255) for _ in range(16)]
    # )
    # return f"  {addr}:  {hx}  |{ch}|"

    # frames = [
    # f"  #0  {_addr()} in mittens_ui::BootTerminal::_begin_fade()",
    # f"  #1  {_addr()} in PyQt5.QtCore.QTimer.timeout()",
    # f"  #2  {_addr()} in mittens_ui::MittensUI::setup()",
    # f"  #3  {_addr()} in krita::Extension::setup()",
    # f"  #4  {_addr()} in PyQt5.QtWidgets.QApplication.exec_()",
    # ]
    # numHexRegions = random.randint(2, 4)
    # numFrames     = random.randint(3, 5)
    # lines += [("PAUSE", "", p(200)), ("GLITCH", f"  memory dump  [{numHexRegions} regions]  [{numFrames} frames]", p(80)), ("PAUSE", "", p(100))]
    # for _ in range(numHexRegions):
    # lines.append(("GLITCH", _hex_row(), p(70)))
    # lines += [("PAUSE", "", p(120)), ("GLITCH", "  Traceback (most recent call last):", p(70))]
    # for f in frames[:numFrames]:
    # lines.append(("GLITCH", f, p(60)))
    # lines += [
    # ("PAUSE",    "",                                                               p(400)),
    # ("RESPONSE", "  > segfault",                                                  p(120)),
    # ("PAUSE",    "",                                                               random.randint(p(1400), p(2000))),
    # ("RESPONSE", "  > jk lol everything is fine",                                 p(100)),
    # ("PAUSE",    "",                                                               p(120)),
    # ("RESPONSE", "  > okay it was unfunny asl but no one will actually read this", p(120)),
    # ("PAUSE",    "",                                                               p(250)),
    # ("SYS",      "mittens_ui ready",                                              p(120)),
    # ("PAUSE",    "",                                                               p(120)),
    # ("SYS",      "launching krita...",                                            p(200)),
    # ("PAUSE",    "",                                                               p(150)),
    # *_splash_lines(p),
    # ("PAUSE",    "",                                                               p(2000)),
    # ("BLANK",    "",                                                               p(250)),
    # ]
    # return lines


class BootTerminal(QWidget):
    """
    so this one basically does the boot sequence itself from the stuff above
    it also does some hesitation and typo stuff so that it looks more organic
    then it lets sharddissolve or wtv i named it do the transition
    """
    fg      = "#00FF94"
    dim     = "#1a4a35"
    tag_bg  = "#005533"
    bg      = "#000000"
    font_sz = "18px"
    font    = "'JetBrains Mono','Consolas','Courier New'"
    _fast_pairs = {
        "th","he","in","er","an","re","on","at","en","nd",
        "ti","es","or","te","of","ed","is","it","al","ar",
    }
    _slow_chars = set(r"/\-_.@#$%^&*()[]{};<>?!")

    def __init__(self, main_win, mode="normal"):
        super().__init__(None)
        self._main_win   = main_win
        self._mode       = mode
        self._bootScript  = _boot_lines(mode)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(f"background: {self.bg};")
        self.setGeometry(QApplication.primaryScreen().geometry())
        self._visibleLabels = []
        self._scriptPos    = 0
        self._currentCmd   = ""
        self._charIndex     = 0
        self._promptText  = ""
        self._activeLabel        = None
        self._postTypeDelay  = 0
        self._unprintedPrompt = None
        self._keystrokeTimer = QTimer(self)
        self._keystrokeTimer.setSingleShot(True)
        self._keystrokeTimer.timeout.connect(self._handle_keystroke)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        bar = QWidget(self)
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background: #080808; border-bottom: 1px solid {self.dim};")
        bar_lay = QVBoxLayout(bar)
        bar_lay.setContentsMargins(24, 6, 0, 6)
        titleLbl = QLabel("MITTENS  ::  Modular Interaction Toolkit for Transitional Effects, Navigation & Surfaces  ::  BOOT SEQUENCE", bar)
        titleLbl.setStyleSheet(
            f"color: {self.fg}; font-family: {self.font};"
            f" font-size: 13px; letter-spacing: 3px; background: transparent;"
        )
        bar_lay.addWidget(titleLbl)
        outer.addWidget(bar)
        self._scrollArea = QWidget(self)
        self._scrollArea.setStyleSheet(f"background: {self.bg};")
        self._scrollAreaLayout = QVBoxLayout(self._scrollArea)
        self._scrollAreaLayout.setContentsMargins(60, 30, 60, 30)
        self._scrollAreaLayout.setSpacing(6)
        self._scrollAreaLayout.setAlignment(Qt.AlignTop)
        outer.addWidget(self._scrollArea, 1)

        screenH = QApplication.primaryScreen().availableGeometry().height()
        self._max_lines = max(6, (screenH - 36 - 60) // 28)
        self._nextLineTimer = QTimer(self)
        self._nextLineTimer.setSingleShot(True)
        self._nextLineTimer.timeout.connect(self._process_line)
        self._queue_next(80)

    def _queue_next(self, ms=80):
        self._nextLineTimer.start(max(1, ms))

    def _process_line(self):
        """
        still need to add explanation. hmu if i forgot
        """
        if self._scriptPos >= len(self._bootScript):
            QTimer.singleShot(600, self._startTransition); return
        kind, text, post = self._bootScript[self._scriptPos]
        self._scriptPos += 1
        # print(f"[BootTerminal] _next kind={kind!r} post={post}")
        if kind == "PAUSE":
            self._queue_next(post); return
        if kind == "PROMPT":
            lbl = self._appendLine(kind, "")
            lbl.setProperty("prompt", text)
            self._refreshLabel(lbl, "")
            self._unprintedPrompt = lbl
            self._queue_next(post); return
        if kind == "TYPE":
            if self._unprintedPrompt is not None:
                lbl = self._unprintedPrompt; self._unprintedPrompt = None
                promptStr = lbl.property("prompt") or ""
                cmdStr    = text
            else:
                PROMPT    = "root@mittens:~# "
                promptStr = PROMPT if text.startswith(PROMPT) else ""
                cmdStr    = text[len(promptStr):]
                lbl       = self._appendLine("TYPE", "")
                lbl.setProperty("prompt", promptStr)
                self._refreshLabel(lbl, "")
            self._currentCmd   = cmdStr
            self._promptText  = promptStr
            self._charIndex     = 0
            self._activeLabel        = lbl
            self._postTypeDelay  = post
            self._keystrokeTimer.start(random.randint(80, 160)); return
        self._appendLine(kind, text)
        self._queue_next(post)

    def _keystroke_delay(self, text, pos):
        """
        hesitation part
        """
        ch   = text[pos]
        prev = text[pos - 1] if pos > 0 else ""
        pair = (prev + ch).lower()
        if pair in self._fast_pairs:  base = random.randint(35, 70)
        elif ch in self._slow_chars:  base = random.randint(90, 160)
        elif ch == " ":               base = random.randint(50, 100)
        else:                         base = random.randint(55, 120)
        if prev == " ": base = base + random.randint(0, 60)
        if random.random() < 0.15:
            pauseMs = random.randint(120, 350)
            base = base + pauseMs
        return base

    def _doBackspace(self):
        self._charIndex -= 1
        self._refreshLabel(self._activeLabel, self._currentCmd[:self._charIndex])
        self._keystrokeTimer.start(random.randint(60, 150))

    def _handle_keystroke(self):
        """
        misspell part. it can either accidentally click the same key twice or click a neighbouring key
	inspired by watching myself script
        """
        if self._charIndex >= len(self._currentCmd):
            if self._activeLabel:
                promptStr = self._activeLabel.property("prompt") or ""
                self._activeLabel.setText(
                    f'<span style="color:{self.fg}; font-weight:bold;">{promptStr}</span>'
                    f'<span style="color:#ffffff; font-weight:bold;">{self._currentCmd}</span>'
                )
            self._activeLabel = None
            self._queue_next(self._postTypeDelay); return
        ch = self._currentCmd[self._charIndex]
        prob_double = 0.05 if self._mode == "compact" else 0.10
        prob_typo   = 0.05 if self._mode == "compact" else 0.13
        if ch.isalpha() and random.random() < prob_double and self._charIndex < len(self._currentCmd) - 1:
            self._charIndex += 1
            self._refreshLabel(self._activeLabel, self._currentCmd[:self._charIndex] + ch)
            # print(f"[BootTerminal] double-key at pos={self._charIndex} ch={ch!r}")
            QTimer.singleShot(random.randint(80, 180), self._doBackspace); return
        if ch.isalpha() and random.random() < prob_typo and self._charIndex < len(self._currentCmd) - 1:
            nb = "qwertyuiopasdfghjklzxcvbnm"
            missedKey = random.choice([c for c in nb if c != ch.lower()])
            if ch.isupper(): missedKey = missedKey.upper()
            self._charIndex += 1
            # print(f"[BootTerminal] typo: {ch!r} -> {missedKey!r}")
            self._refreshLabel(self._activeLabel, self._currentCmd[:self._charIndex - 1] + missedKey)
            QTimer.singleShot(random.randint(120, 280), self._doBackspace); return
        self._charIndex += 1
        self._refreshLabel(self._activeLabel, self._currentCmd[:self._charIndex])
        self._keystrokeTimer.start(self._keystroke_delay(self._currentCmd, self._charIndex - 1))

    def _refreshLabel(self, lbl, text):
        if not lbl: return
        promptStr = lbl.property("prompt") or ""
        lbl.setText(
            f'<span style="color:{self.fg}; font-weight:bold;">{promptStr}</span>'
            f'<span style="color:#ffffff; font-weight:bold;">{text}</span>'
            f'<span style="color:{self.fg};">▮</span>'
        )

    def _appendLine(self, kind, text):
        lbl = self._buildLabel(kind, text)
        self._visibleLabels.append(lbl)
        while len(self._visibleLabels) > self._max_lines:
            old = self._visibleLabels.pop(0)
            self._scrollAreaLayout.removeWidget(old); old.deleteLater()
        return lbl

    def _buildLabel(self, kind, text):
        """
        this does the label stuff like [INIT] or [SYS] at the beginning of all the lines
        """
        f, sz = self.font, self.font_sz
        if kind == "BLANK":
            lbl = QLabel(" ", self._scrollArea)
            lbl.setStyleSheet(f"font-size: {sz}; background: transparent;")
        elif kind == "ASCII":
            lbl = QLabel(text, self._scrollArea)
            lbl.setStyleSheet(f"color: {self.fg}; font-family: {f}; font-size: {sz}; background: transparent;")
        elif kind == "GLITCH":
            errColor = random.choice(["#cc3333", "#bb4400", "#cc2222", "#aa3300"])
            lbl = QLabel(text, self._scrollArea)
            lbl.setStyleSheet(f"color: {errColor}; font-family: {f}; font-size: {sz}; background: transparent;")
        elif kind == "TYPE":
            lbl = QLabel("", self._scrollArea)
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(f"font-family: {f}; font-size: {sz}; background: transparent;")
        elif kind == "RESPONSE":
            lbl = QLabel(text, self._scrollArea)
            lbl.setStyleSheet(f"color: #ffcc00; font-family: {f}; font-size: {sz}; background: transparent;")
        else:
            # did the colors based on intuition by just bumping up green and adding a lil blue while keeping red 0
            tag_cols = {
                "SYS":  self.fg,    "INIT": "#00cc77", "MEM":  "#00aa66",
                "GPU":  "#00bb77",  "FONT": "#009955", "QSS":  "#00FF94",
                "DOCK": "#00dd88",  "PHYS": "#00FF94", "PILL": "#00FF94",
                "FADE": "#00cc77",  "PEEK": "#00bb77",
            }
            labelColor = tag_cols.get(kind, self.fg)
            prefix = (
                f'<span style="color:{self.tag_bg};">[</span>'
                f'<span style="color:{labelColor}; font-weight:600;">{kind:<4}</span>'
                f'<span style="color:{self.tag_bg};">]</span> '
            )
            lbl = QLabel(prefix + f'<span style="color:{self.fg};">{text}</span>', self._scrollArea)
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(f"font-family: {f}; font-size: {sz}; background: transparent;")
        lbl.setWordWrap(False)
        self._scrollAreaLayout.addWidget(lbl)
        return lbl

    def _startTransition(self):
        px = self.grab()
        self.hide()
        transitionOverlay = ShardDissolve(px, self._main_win, on_close=self.close)
        QApplication.instance()._shard_dissolve = transitionOverlay


class FrameTimerHUD(QWidget):
    """
    floating draggable hud that tracks how long youve been working this session,
    how many frames youve touched, and your average time per frame

    logs to a txt file next to your krita file so you build up data over time
    its per-document so switching files resets it (but saves first)

    avg/frame only counts frames you actually spent time on (>= MIN_FRAME_SECS),
    so quickly scrubbing past frames doesnt tank the number.
    also hides itself when theres no document open.
    """
    tick_ms        = 1000
    bg             = QColor(8, 8, 8, 210)
    fg             = "#00FF94"
    dim            = "#1a4a35"
    MIN_FRAME_SECS = 20  # frames visited for less than this are ignored in the avg

    def __init__(self, win):
        super().__init__(win, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._win              = win
        self._session_secs     = 0
        self._frames_done      = 0
        self._counted_secs     = 0   # total secs across frames that passed the threshold
        self._running          = False
        self._dragging         = False
        self._drag_offset      = QPoint()
        self._doc_path         = None
        self._last_frame       = None
        self._frame_secs       = 0   # how long we've been on the current frame

        self._tick = QTimer(self)
        self._tick.setInterval(self.tick_ms)
        self._tick.timeout.connect(self._on_tick)

        self._pollTimer = QTimer(self)
        self._pollTimer.setInterval(500)
        self._pollTimer.timeout.connect(self._poll_krita)
        self._pollTimer.start()

        self.setFixedSize(220, 90)
        self.move(win.width() - 240, win.height() - 120)
        # start hidden, _poll_krita will show us once a doc is open
        self.hide()

    def _poll_krita(self):
        """
        checks the active document and current frame so we know when the user
        switches docs or moves to a new frame.
        hides the hud if no document is open.
        """
        from krita import Krita
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            self._stop()
            if self.isVisible(): self.hide()
            return
        if not self.isVisible(): self.show()
        docPath = doc.fileName()
        if docPath != self._doc_path:
            self._save_log()
            self._doc_path     = docPath
            self._session_secs = 0
            self._frames_done  = 0
            self._counted_secs = 0
            self._last_frame   = None
            self._frame_secs   = 0
        curFrame = None
        try:
            w = app.activeWindow()
            if w: curFrame = w.activeView().document().currentTime()
        except Exception:
            pass
        if curFrame is not None and curFrame != self._last_frame:
            if self._last_frame is not None:
                # only count this frame toward the avg if we spent enough time on it
                if self._frame_secs >= self.MIN_FRAME_SECS:
                    self._frames_done  += 1
                    self._counted_secs += self._frame_secs
            self._last_frame = curFrame
            self._frame_secs = 0
            if not self._running: self._start()
        self.update()

    def _start(self):
        self._running = True
        self._tick.start()

    def _stop(self):
        self._running = False
        self._tick.stop()

    def _on_tick(self):
        if self._running:
            self._session_secs += 1
            self._frame_secs   += 1
        self.update()

    def _fmt_time(self, secs):
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if h > 0: return f"{h}h {m:02d}m {s:02d}s"
        return f"{m:02d}m {s:02d}s"

    def _avg(self):
        if self._frames_done == 0: return "—"
        avg = self._counted_secs / self._frames_done
        if avg >= 60:
            return f"{avg / 60:.1f}m"
        return f"{avg:.0f}s"

    def _log_path(self):
        if not self._doc_path: return None
        return os.path.splitext(self._doc_path)[0] + "_frametimes.txt"

    def _save_log(self):
        p = self._log_path()
        if not p or self._session_secs == 0: return
        try:
            import datetime
            with open(p, "a", encoding="utf-8") as f:
                stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                f.write(f"{stamp}  |  session={self._fmt_time(self._session_secs)}"
                        f"  frames={self._frames_done}  avg={self._avg()}\n")
        except Exception as e:
            print(f"[Mittens] frametimer log error: {e}")

    def _qfont(self, size):
        from PyQt5.QtGui import QFont
        f = QFont("JetBrains Mono"); f.setPixelSize(size); return f

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        painter.fillPath(path, self.bg)
        painter.setPen(QPen(QColor(self.dim), 1))
        painter.drawPath(path)

        def row(y, label, val):
            painter.setFont(self._qfont(10))
            painter.setPen(QColor(self.dim))
            painter.drawText(14, y, label)
            painter.setPen(QColor(self.fg))
            painter.drawText(110, y, val)

        painter.setPen(QColor(self.fg))
        painter.setFont(self._qfont(9))
        painter.drawText(14, 18, "FRAME  TIMER")
        row(36, "session",   self._fmt_time(self._session_secs))
        row(52, "frames",    str(self._frames_done))
        row(68, "avg/frame", self._avg())

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.fg) if self._running else QColor(self.dim))
        painter.drawEllipse(200, 8, 7, 7)
        painter.end()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._dragging = True; self._drag_offset = ev.globalPos() - self.pos()

    def mouseMoveEvent(self, ev):
        if self._dragging: self.move(ev.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton: self._dragging = False

    def closeEvent(self, ev):
        self._save_log(); super().closeEvent(ev)


class SceneMarkerBar(QWidget):
    """
    floating bar that attaches on top of kritas timeline docker
    left-click to drop a named marker at that frame, right-click to remove
    markers are color coded, saved next to your krita file so they persist

    toggleable via tools > scripts
    """
    bar_h       = 22
    bg          = QColor(5, 5, 5, 230)
    marker_cols = [
        "#00FF94", "#ff6b6b", "#ffd93d", "#6bcbff",
        "#ff9fff", "#ff9f43", "#a29bfe", "#fd79a8",
    ]

    def __init__(self, win):
        super().__init__(win, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._win          = win
        self._markers      = []
        self._doc_path     = None
        self._total_frames = 100
        self._col_idx      = 0

        self._pollTimer = QTimer(self)
        self._pollTimer.setInterval(600)
        self._pollTimer.timeout.connect(self._poll_krita)
        self._pollTimer.start()

        self._attachTimer = QTimer(self)
        self._attachTimer.setInterval(800)
        self._attachTimer.timeout.connect(self._try_attach)
        self._attachTimer.start()

        self.setCursor(Qt.CrossCursor)
        self.setToolTip("left-click: add scene marker  |  right-click: remove")
        self.show()

    def _try_attach(self):
        """
        finds kritas timeline docker and sits on top of it
        keeps trying cus dockers can move / be closed and reopened
        """
        timelineDock = None
        for dock in self._win.findChildren(QDockWidget):
            if "timeline" in dock.windowTitle().lower():
                timelineDock = dock; break
        if timelineDock is None: return
        self._attachTimer.setInterval(2000)
        dockWidget = timelineDock.widget()
        if dockWidget is None: return
        tl = dockWidget.mapTo(self._win, QPoint(0, 0))
        self.setGeometry(tl.x(), tl.y(), dockWidget.width(), self.bar_h)
        self.raise_()

    def _poll_krita(self):
        from krita import Krita
        doc = Krita.instance().activeDocument()
        if doc is None: return
        docPath = doc.fileName()
        if docPath != self._doc_path:
            self._save_markers()
            self._doc_path = docPath
            self._markers  = []
            self._load_markers()
        try:
            self._total_frames = max(1, doc.animationLength())
        except Exception:
            pass
        self.update()

    def _frame_to_x(self, frame):
        return int((frame / max(1, self._total_frames - 1)) * (self.width() - 1))

    def _x_to_frame(self, x):
        return int((x / max(1, self.width() - 1)) * (self._total_frames - 1))

    def mousePressEvent(self, ev):
        frame = self._x_to_frame(ev.x())
        if ev.button() == Qt.RightButton:
            self._markers = [m for m in self._markers if abs(m["frame"] - frame) > 2]
            self._save_markers(); self.update(); return
        if ev.button() == Qt.LeftButton:
            if any(abs(m["frame"] - frame) <= 2 for m in self._markers): return
            col = self.marker_cols[self._col_idx % len(self.marker_cols)]
            self._col_idx += 1
            self._markers.append({"frame": frame, "name": f"scene {len(self._markers) + 1}", "color": col})
            self._markers.sort(key=lambda m: m["frame"])
            self._save_markers(); self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.bg)
        for m in self._markers:
            x   = self._frame_to_x(m["frame"])
            col = QColor(m["color"])
            tickCol = QColor(col); tickCol.setAlpha(200)
            painter.setPen(QPen(tickCol, 2))
            painter.drawLine(x, 0, x, self.bar_h)
            fm  = painter.fontMetrics()
            tw  = fm.horizontalAdvance(m["name"]) + 8
            lx  = min(x + 3, self.width() - tw - 2)
            labelBg = QColor(col); labelBg.setAlpha(40)
            painter.fillRect(lx, 3, tw, self.bar_h - 6, labelBg)
            painter.setPen(col)
            painter.drawText(lx + 4, self.bar_h - 6, m["name"])
        painter.setPen(QColor(self.marker_cols[0]))
        painter.setOpacity(0.15)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.end()

    def _markers_path(self):
        if not self._doc_path: return None
        return os.path.splitext(self._doc_path)[0] + "_markers.txt"

    def _save_markers(self):
        p = self._markers_path()
        if not p: return
        try:
            with open(p, "w", encoding="utf-8") as f:
                for m in self._markers:
                    f.write(f"{m['frame']}|{m['name']}|{m['color']}\n")
        except Exception as e:
            print(f"[Mittens] marker save error: {e}")

    def _load_markers(self):
        p = self._markers_path()
        if not p: return
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        self._markers.append({
                            "frame": int(parts[0]),
                            "name":  parts[1],
                            "color": parts[2],
                        })
        except Exception:
            pass


class MittensUI(Extension):
    BACKRONYM = "Modular Interaction Toolkit for Transitional Effects, Navigation & Surfaces"
    # yes ofc its a backronym dont tell any1 tho
    _HIDE_BARS = {"Zoom", "Help", "Navigation"}

    def __init__(self, parent):
        super().__init__(parent)
        self._physics_on   = True
        self._boot_mode    = "compact"
        self._dock_springs  = []
        self._all_pills    = []
        self._opacity_faders   = []
        self._proximityWatcher  = DockPeek()
        self._frame_timer   = None
        self._marker_bar    = None
        self._load_cfg()

    def setup(self):
        QTimer.singleShot(800,  self._launch_boot_screen)
        QTimer.singleShot(1200, self._ready)

    def _launch_boot_screen(self):
        if self._boot_mode == "skip": return
        for w in QApplication.instance().topLevelWidgets():
            if isinstance(w, QMainWindow):
                term = BootTerminal(w, self._boot_mode)
                self._boot_term = term
                term.showFullScreen(); term.raise_(); term.activateWindow()
                try:
                    HWND_TOPMOST = -1
                    SWP_NOMOVE   = 0x0002
                    SWP_NOSIZE   = 0x0001
                    hwnd = int(term.winId())
                    ctypes.windll.user32.SetWindowPos(
                        hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
                    )
                except Exception:
                    pass
                return
        QTimer.singleShot(200, self._launch_boot_screen)

    def createActions(self, window):
        """
        this registers and puts all the stuff under tools > scripts, a friend of mine helped me with this cus idk how
        to do these kinds of things so shoutout to him
        """
        a1 = window.createAction("mittens_toggle_theme",   "Mittens: Toggle Theme",   "tools/scripts")
        a1.setCheckable(True); a1.setChecked(True)
        a1.triggered.connect(self._toggle_theme)

        a2 = window.createAction("mittens_toggle_physics", "Mittens: Toggle Physics", "tools/scripts")
        a2.setCheckable(True); a2.setChecked(True)
        a2.triggered.connect(self._toggle_physics)

        a3 = window.createAction("mittens_toggle_frametimer", "Mittens: Toggle Frame Timer", "tools/scripts")
        a3.setCheckable(True); a3.setChecked(True)
        a3.triggered.connect(self._toggle_frame_timer)

        # a4 = window.createAction("mittens_toggle_markerbar", "Mittens: Toggle Scene Markers", "tools/scripts")
        # a4.setCheckable(True); a4.setChecked(True)
        # a4.triggered.connect(self._toggle_marker_bar)

        # self._a_normal  = window.createAction("mittens_boot_normal",  "Mittens: Boot Normal",  "tools/scripts")
        self._a_compact = window.createAction("mittens_boot_compact", "Mittens: Boot Compact", "tools/scripts")
        self._a_skip    = window.createAction("mittens_boot_skip",    "Mittens: Boot Skip",    "tools/scripts")
        for a, m in [(self._a_compact, "compact"), (self._a_skip, "skip")]:
            a.setCheckable(True); a.setChecked(self._boot_mode == m)
            a.triggered.connect(lambda checked, mode=m: self._set_boot_mode(mode))

    def _cfg_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "mittens_config.txt")

    def _load_cfg(self):
        try:
            with open(self._cfg_path()) as f:
                for line in f:
                    k, _, v = line.strip().partition("=")
                    if k == "boot_mode" and v in ("compact", "skip"):
                        self._boot_mode = v
        except Exception:
            pass

    def _save_cfg(self):
        try:
            with open(self._cfg_path(), "w") as f:
                f.write(f"boot_mode={self._boot_mode}\n")
        except Exception as e:
            print(f"[Mittens] config save error: {e}")

    def _set_boot_mode(self, mode):
        self._boot_mode = mode
        # self._a_normal.setChecked(mode == "normal")
        self._a_compact.setChecked(mode == "compact")
        self._a_skip.setChecked(mode == "skip")
        self._save_cfg()

    def _ready(self):
        self._apply_theme()
        QTimer.singleShot(500, self._do_layout)
        win = self._get_main_window()
        if win:
            self._frame_timer = FrameTimerHUD(win)
            # self._marker_bar  = SceneMarkerBar(win)

    def _qss(self):
        p = os.path.join(os.path.dirname(__file__), "mittens_theme.qss")
        try:
            with open(p, encoding="utf-8") as f: return f.read()
        except Exception as e:
            print(f"[Mittens] QSS error: {e}"); return ""

    def _apply_theme(self):
        """
        loads the qss stuff

        there is some weird things going on cus of scuffed debugging (i had to binary search the whole extention btw :sob:)
        but honestly just ignore that, you probably wont even have to edit this, just edit the qss file
        """
        from krita import Krita
        win = Krita.instance().activeWindow()
        if not win: return
        the_qss = self._qss()
        # print(f"[MittensUI] qss loaded, length={len(the_qss)}")
        if not the_qss: return
        qwin = win.qwindow()
        qwin.setStyleSheet(the_qss)
        centralW = qwin.centralWidget()
        if centralW:
            centralW.setStyleSheet(self._tab_qss())
            centralW.resize(centralW.sizeHint())

    def _tab_qss(self):
        return """
            QTabBar::tab {
                background: #0a0a0a; color: #383838; border: none;
                padding: 4px 14px; height: 20px;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #080808; color: #e0e0e0; border-bottom: 2px solid #00FF94; }
            QTabBar::tab:hover { color: #c0c0c0; }
            QTabBar { background: #0a0a0a; border: none; qproperty-drawBase: 0; }
        """

    def _remove_theme(self):
        from krita import Krita
        win = Krita.instance().activeWindow()
        if win: win.qwindow().setStyleSheet("")

    def _toggle_theme(self, on):
        self._apply_theme() if on else self._remove_theme()

    def _toggle_physics(self, on):
        self._physics_on = on
        for x in self._dock_springs + self._all_pills + self._opacity_faders:
            x.set_active(on)

    def _toggle_frame_timer(self, on):
        if self._frame_timer is None: return
        self._frame_timer.setVisible(on)

    def _toggle_marker_bar(self, on):
        if self._marker_bar is None: return
        self._marker_bar.setVisible(on)

    def _get_main_window(self):
        for w in QApplication.instance().topLevelWidgets():
            if isinstance(w, QMainWindow): return w
        return None

    def _do_layout(self):
        win = self._get_main_window()
        if not win: return
        self._init_toolbars(win)
        self._init_dock_widgets(win)
        self._stamp_branding(win)

    # i just wanted to make sure my name was on there dont judge, its literally open source so you cant complain
    def _stamp_branding(self, win):
        from PyQt5.QtWidgets import QStatusBar
        existingTitle = win.windowTitle()
        if "MITTENS" not in existingTitle:
            win.setWindowTitle(f"{existingTitle}  ::  MITTENS: {self.BACKRONYM}" if existingTitle else f"MITTENS: {self.BACKRONYM}")
        sb = win.statusBar() or QStatusBar(win)
        win.setStatusBar(sb)
        footerLabel = QLabel(f"MITTENS  ·  {self.BACKRONYM}")
        footerLabel.setStyleSheet(
            "color: #1e5c40; font-family: 'JetBrains Mono','Consolas','Courier New';"
            "font-size: 10px; letter-spacing: 1px; padding-right: 8px; background: transparent;"
        )
        footerLabel.setToolTip("yes it's also my cat's name")
        sb.addPermanentWidget(footerLabel)

    def _init_toolbars(self, win):
        for tb in win.findChildren(QToolBar):
            if tb.windowTitle() in self._HIDE_BARS:
                tb.setVisible(False); continue
            tb.setIconSize(QSize(22, 22))
            tb.setMovable(True); tb.setFloatable(True)
            tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
            newPill = Pill(tb)
            newPill.set_active(self._physics_on)
            self._all_pills.append(newPill)
            tb.topLevelChanged.connect(lambda _, s=newPill: s.reset())

    def _init_dock_widgets(self, win):
        for dock in win.findChildren(QDockWidget):
            # print(f"[MittensUI] attaching to dock: {dock.windowTitle()!r}")
            dockPhysics = InertialDock(dock)
            dockPhysics.set_active(self._physics_on)
            self._dock_springs.append(dockPhysics)
            dockFader = IdleFade(dock)
            dockFader.set_active(self._physics_on)
            self._opacity_faders.append(dockFader)
            self._proximityWatcher.register(dock, dockFader)
        QTimer.singleShot(800, lambda: self._attach_pills_to_everything(win))

    def _attach_pills_to_everything(self, win):
        """
        This part was added becuase the original "pill" would only go on the toolbar and i had to add more places
        I understand that its a bit confusing that i put it all here except the toolbar but i am too lazy to change it
        """
        from PyQt5.QtWidgets import QAbstractSpinBox, QComboBox, QScrollBar, QSlider
        alreadyHasPill = set()
        widgetsToIgnore  = (QAbstractSpinBox, QComboBox, QScrollBar, QSlider)
        for tb in win.findChildren(QToolBar):
            alreadyHasPill.add(id(tb))
        for btn in win.findChildren(QAbstractButton):
            if not self._button_is_eligible(btn): continue
            containerWidget = None
            p = btn.parent()
            while p and not isinstance(p, (QToolBar, QDockWidget, QMainWindow)):
                if isinstance(p, widgetsToIgnore): break
                buttonKids = [c for c in p.children()
                            if isinstance(c, QAbstractButton) and self._button_is_eligible(c)]
                if len(buttonKids) >= 1:
                    containerWidget = p
                p = p.parent()
            if containerWidget is None or id(containerWidget) in alreadyHasPill: continue
            # print(f"[MittensUI] pill_everywhere adding pill to {containerWidget.__class__.__name__}")
            alreadyHasPill.add(id(containerWidget))
            newPill = Pill(containerWidget)
            newPill.set_active(self._physics_on)
            self._all_pills.append(newPill)

    @staticmethod
    def _button_is_eligible(btn):
        from PyQt5.QtWidgets import QAbstractSpinBox, QComboBox, QScrollBar, QSlider
        p = btn.parent()
        while p:
            if isinstance(p, (QAbstractSpinBox, QComboBox, QScrollBar, QSlider)): return False
            p = p.parent()
        return True


# lil critter (DONT DELETE)
#
#                                               .-+*#######**++=-:
#                      -+.                   :=#####################+=.
#                     :###:               :=############################=.
#                     *####         .-=+*#################################*:
#                    +#####-   :=*##########################################*:
#                 .-**##*###.=################################################+
#              -*####*######=*##################################################:
#            =######*########-###################################################=
#  *#*==---+########*########*=#############################***###################+
#  :####*###########*#########=########################****########################*
#   :###***###############*####+####################*+*#############################+
#    :######*##########**#####%=#*#################+*################################-
#     .*##############*#######*=*#################+*##################################
#       +###################***+##**##############+###################################
#        ######***###########*-**################*####################################
#        =###**#######+*#####*-***###############*###########################+########
#         *#########++*+###**:#############################################*-#########
#         .=****#####*-****+=#############################################==#########*
#         :=*****####***+==*###################%####%##################+==###########.
#     .-*#######*+**+++*#####################+*+****+++++++*******+====*###########*.
#  .+#########++###########################*+############%##**+++**############*=:.
# -#########*+#######################%#*=-..##################################-

# its a cat if you couldnt tell. quite a big critter actually.
# the cat is here cus it kills all the bugs in the code
# (just joking i need the project to be at least 1.6k lines else i wont reach quota and they wont check this anyway lmao)

# made in windows notepad (yes notepad not notepad++ i forgot that existed)
