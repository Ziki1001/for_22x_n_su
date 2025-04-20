import sys
import random
import os
import pygame

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QPushButton, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer, QMargins, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QFont, QCursor

# 这是从 pet_1.ui 生成的 Python 文件，类名通常是 Ui_MainWindow
from Ui_pet_1 import Ui_MainWindow


def resource_path(relative_path):
    """获取资源文件路径，兼容 PyInstaller 打包路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class PetApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # -----------------------------
        # 1. 使用 Ui_MainWindow 的 setupUi
        # -----------------------------
        self.setupUi(self)

        # -----------------------------
        # 2. 窗口外观和特性
        # -----------------------------
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("没想好叫什么名字")
        # -----------------------------
        # 3. Mouse Tracking（用于拖动和悬浮检查）
        # -----------------------------
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)
        # 这些按钮也要纳入悬浮显示逻辑，所以开启 mouseTracking
        self.hover_button.setMouseTracking(True)
        self.icecream_button.setMouseTracking(True)
        self.egg_button.setMouseTracking(True)
        self.timer_button.setMouseTracking(True)

        # -----------------------------
        # 4. 作者信息
        # -----------------------------
        self.author_label = QLabel(self)
        self.setup_author_label()

        # -----------------------------
        # 5. 初始化播放器与属性
        # -----------------------------
        pygame.mixer.init()
        # 用于记录拖动时的全局鼠标位置（原代码使用 self.old_pos）
        self.old_pos = QPoint(0, 0)

        # 在这里保存**当前音频相关**的所有定时器
        self.current_timers = []

        # 标记资源路径
        self.songs = [
            resource_path("song1.mp3"),
            resource_path("song2.mp3"),
            resource_path("song3.mp3"),
            resource_path("song4.mp3"),
            resource_path("song5.mp3"),
            resource_path("song6.mp3"),
            resource_path("song7.mp3"),
        ]
        # 每首歌的播放时长(毫秒)
        self.song_play_time_dict = {
            self.songs[0]: 26000,
            self.songs[1]: 229000,
            self.songs[2]: 14000,
            self.songs[3]: 37000,
            self.songs[4]: 12000,
            self.songs[5]: 137500,
            self.songs[6]: 51000
        }

        # 麦克风调度表
        self.song_mic_schedules = {
            0: [
                (0,    "gg"),
                (13000, "cc"),
                (20000, "ggcc"),
                (25000, "none")
            ],
            1: [
                (7000,"gg"),
                (58000, "cc"),
                (100000, "ggcc"),
                (102000, "gg"),
                (120000, "cc"),
                (130000, "gg"),
                (132000, "ggcc"),
                (148000, "gg"),
                (162000, "ggcc"),
                (165000, "gg"),
                (172000, "cc"),
                (193000, "ggcc"),
                (198000, "cc"),
                (203000, "ggcc"),
                (208000, "cc"),
                (214000, "none"),
            ],
            2: [
                (0,"cc"),
                (3000, "gg"),
                (6500, "cc"),
                (8500, "gg"),
                (10000, "ggcc"),
                (13000, "none")
            ],
            3: [
                (0,"cc"),
                (12500, "gg"),
                (23000, "none"),
                (25000, "gg"),
                (30000, "cc"),
                (37000, "none")
            ],
            4: [
                (0,"cc"),
                (2000, "gg"),
                (4800, "cc"),
                (7000, "ggcc"),
                (9500, "none"),
                (10000, "cc"),
                (12000,"none")
            ],
            5: [
                (0,"cc"),
                (41000, "gg"),
                (102000, "cc"),
                (137500, "none")
            ],
            6: [
                (0,"gg"),
                (10000, "none"),
                (11000, "cc"),
                (20000, "ggcc"),
                (21000, "gg"),
                (23500,"cc"),
                (39000, "ggcc"),
                (51000, "none")
            ]
        }

        # 其它音频
        self.letter_cc = resource_path("letter_cc.mp3")
        self.icecream_sound = resource_path("icecream.mp3")
        self.egg_sound = resource_path("egg.mp3")
        self.letter_gg = resource_path("letter_gg.mp3")#时长设置在触发的函数里了
        # 给非歌曲音频一个大致的播放时长(示例值)
        self.other_sounds_duration = {
            self.letter_cc: 152000,     # 示例：假设信封音频25s
            self.icecream_sound: 8000    # 示例：假设icecream音频5s
        }

        # 为两个角色分别准备一个“麦克风”QLabel
        self.gg_mic_label = QLabel(self)
        self.cc_mic_label = QLabel(self)

        pixmap_mic = QPixmap(resource_path("mic_show.png"))
        self.gg_mic_label.setPixmap(pixmap_mic)
        self.cc_mic_label.setPixmap(pixmap_mic)

        # 放在合适位置（示例：分别放在 gg_body, cc_body 附近）
        self.gg_mic_label.setGeometry(99, 313, 57, 22)   # 根据需要微调坐标
        self.cc_mic_label.setGeometry(355, 310, 57,22)   # 根据需要微调坐标
        self.gg_mic_label.setScaledContents(True)
        self.cc_mic_label.setScaledContents(True)

        self.gg_mic_label.setVisible(False)
        self.cc_mic_label.setVisible(False)

        # -----------------------------
        # 初始化角色图片、按钮功能
        # -----------------------------
        self.init_images_and_buttons()

        # 2. Pause 按钮（默认隐藏）
        self.set_button_image(self.pause_button, resource_path("end_music.png"), self.pause_button_clicked)
        self.pause_button.setVisible(False)  # 默认不显示

        # 3. Timer 功能相关
        self.set_button_image(self.timer_button, resource_path("timer_button.png"), self.timer_button_clicked)
        # 输入框和“开始”按钮
        self.set_button_image(self.timer_start_button, resource_path("start_timer.png"), self.timer_start_button_clicked)
        # 暂停、结束按钮
        self.set_button_image(self.timer_pause_button, resource_path("pause_button.png"), self.timer_pause_button_clicked)
        self.set_button_image(self.timer_end_button, resource_path("end_button.png"), self.timer_end_button_clicked)

        # Timer 输入框、Label、Finish Label 都需要先隐藏
        self.timer_input.setVisible(False)
        self.timer_start_button.setVisible(False)
        self.timer_label.setVisible(False)
        self.timer_pause_button.setVisible(False)
        self.timer_end_button.setVisible(False)

        # 倒计时定时器
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)  # 每秒触发一次
        self.countdown_timer.timeout.connect(self.update_timer)

        # 剩余秒数
        self.remaining_seconds = 0
        # 计时器当前是否在暂停状态
        self.timer_is_paused = False

        # -----------------------------
        # 悬浮按钮逻辑
        # -----------------------------
        self.hover_trigger_button = self.hover_button
        self.hover_target_buttons = [
            self.icecream_button,
            self.egg_button,
            self.letter_button_gg,
            self.letter_button,
            self.timer_button
        ]
        for btn in self.hover_target_buttons:
            btn.setVisible(False)

        # 用一个定时器定期检查悬浮区域
        self.hover_timer = QTimer(self)
        self.hover_timer.setInterval(150)  # 每 150 ms 检查一次
        self.hover_timer.timeout.connect(self.check_hover_area)
        self.hover_timer.start()

        # -----------------------------
        # 事件过滤器：安装到主窗口及所有子控件上，实现统一的拖动处理
        # -----------------------------
        self.installEventFilter(self)
        for child in self.findChildren(QWidget):
            child.installEventFilter(self)

    # -----------------------------
    # 添加事件过滤器方法（仅增加，不改变其它代码）
    # -----------------------------
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # 记录鼠标全局位置，用于计算拖动偏移
            self.old_pos = event.globalPos()
            # 返回 True 表示此事件已被处理（阻止后续调用 mousePressEvent 等）
            return True
        elif event.type() == QEvent.MouseMove and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            return True
        return super().eventFilter(obj, event)

    # ============================================================
    # ============   封装统一的 音频播放/停止/覆盖 逻辑   ==========
    # ============================================================
    def stop_current_audio(self):
        """
        停止当前所有正在播放的音频，并清理所有相关的定时器与UI。
        无论是点击 pause_button、音频自然结束，或播放新的音频前，都应调用它。
        """
        # 1. 停止音乐
        pygame.mixer.music.stop()

        # 2. 停止/清理所有 QTimer
        for t in self.current_timers:
            t.stop()
        self.current_timers.clear()

        # 3. 恢复 UI - 隐藏麦克风、泪水等
        self.gg_mic_label.setVisible(False)
        self.cc_mic_label.setVisible(False)
        self.l_tear.setVisible(False)
        self.flush_1.setVisible(False) 
        self.flush_2.setVisible(False)
        # 如果你还有别的UI要复原，也在这里做

        # 4. 隐藏 pause_button
        self.pause_button.setVisible(False)

    def start_new_audio(self, file_path: str, total_duration: int, mic_schedule=None):
        """
        统一的开始播放新音频方法。
        :param file_path: 音频文件路径
        :param total_duration: 音频总时长(毫秒)
        :param mic_schedule: 若是歌曲，需要麦克风时间表(列表[(ms, who), ...])；否则 None
        """
        # 1. 先停止旧的音频和定时器，避免冲突
        self.stop_current_audio()

        # 2. 播放新音频
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # 3. 显示 pause_button
        self.pause_button.setVisible(True)

        # 4. 如果有麦克风时间表，就安排其显示/隐藏
        if mic_schedule is not None:
            for (time_ms, who) in mic_schedule:
                timer = QTimer(self)
                timer.setSingleShot(True)
                # 用lambda捕获 who 的值
                timer.timeout.connect(lambda checked=False, w=who: self.set_mic_visibility(w))
                timer.start(time_ms)
                self.current_timers.append(timer)

        # 5. 设置一个“音频自然播放结束”的定时器
        end_timer = QTimer(self)
        end_timer.setSingleShot(True)
        end_timer.timeout.connect(self.stop_current_audio)
        end_timer.start(total_duration)
        self.current_timers.append(end_timer)

    # ============================================================
    # ============   作者信息、角色图片与按钮初始化    ============
    # ============================================================
    def setup_author_label(self):
        self.author_label.setText(
            "开发 @Shrybdjak\n"
            "人物 @只等明日一秒\n"
            "all for ZZX&SXH"
        )
        # 设置字体和样式
        self.author_label.setFont(QFont("Arial", 6, QFont.Bold))
        self.author_label.setStyleSheet("""
            color: rgba(255, 255, 255, 200);  /* 半透明白色文字 */
        """)
        self.author_label.setGeometry(95, 330, 400, 150)
        self.author_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.author_label.setVisible(True)

        # 如果需要自动隐藏作者信息，可以解开下面这行注释
        QTimer.singleShot(4000, lambda: self.author_label.setVisible(False))

    def init_images_and_buttons(self):
        """模拟原先 init_ui() 中对角色、按钮的配置。"""
        # 角色图
        self.gg_images = [
            resource_path("gg1.png"),
            resource_path("gg2.png"),
            resource_path("gg3.png"),
            resource_path("gg4.png")
        ]
        self.cc_images = [
            resource_path("cc1.png"),
            resource_path("cc2.png"),
            resource_path("cc3.png"),
            resource_path("cc4.png")
        ]

        # 默认图
        gg_pixmap = QPixmap(self.gg_images[3])
        cc_pixmap = QPixmap(self.cc_images[3])

        self.gg_body.setPixmap(gg_pixmap)
        self.gg_body.setScaledContents(True)
        self.cc_body.setPixmap(cc_pixmap)
        self.cc_body.setScaledContents(True)

        # 角色切换
        self.gg_body.mousePressEvent = self.change_gg_image
        self.cc_body.mousePressEvent = self.change_cc_image

        # 按钮设置
        self.set_button_image(self.letter_button, resource_path("letter.webp"), self.letter_button_clicked)
        self.set_button_image(self.egg_button, resource_path("egg.png"), self.egg_button_clicked)
        self.set_button_image(self.rabbit_button, resource_path("rabbit_button.png"), self.rabbit_button_clicked)
        self.set_button_image(self.letter_button_gg, resource_path("letter.webp"), self.letter_button_gg_clicked)
        self.set_button_image(self.icecream_button, resource_path("icecream_button.webp"), self.icecream_button_clicked)
        self.set_button_image(self.trex_button, resource_path("trex_button.png"), self.trex_button_clicked)
        self.set_button_image(self.mic_button, resource_path("mic_click.png"), self.mic_button_clicked)
        self.set_button_image(self.hover_button, resource_path("hover_button.png"), lambda: None)

        # mic_button 右键菜单
        self.mic_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mic_button.customContextMenuRequested.connect(self.show_mic_menu)

        # 其他控件（信封、眼泪、兔子、trex等）
        self.trex_ac_images = resource_path("trex_ac.png")
        pixmap_trex_ac = QPixmap(self.trex_ac_images)
        self.trex_ac.setPixmap(pixmap_trex_ac)
        self.trex_ac.setScaledContents(True)

        self.rabbit_ac_images = resource_path("rabbit_ac.png")
        pixmap_rabbit_ac = QPixmap(self.rabbit_ac_images)
        self.rabbit_ac.setPixmap(pixmap_rabbit_ac)
        self.rabbit_ac.setScaledContents(True)
        
        self.l_tear_images = resource_path("tear.webp")
        pixmap_tear = QPixmap(self.l_tear_images)
        self.l_tear.setPixmap(pixmap_tear)
        self.l_tear.setScaledContents(True)
        
        self.flush_images = resource_path("flush.png")
        pixmap_flush_1 = QPixmap(self.flush_images)
        self.flush_1.setPixmap(pixmap_flush_1)
        self.flush_1.setScaledContents(True)
        self.flush_2.setPixmap(pixmap_flush_1)
        self.flush_2.setScaledContents(True)
 
        self.l_my_old_friend_22x.setVisible(False)
        self.l_tear.setVisible(False)
        self.trex_ac.setVisible(False)
        self.rabbit_ac.setVisible(False)
        self.flush_1.setVisible(False)
        self.flush_2.setVisible(False)

    def set_button_image(self, button: QPushButton, image_path: str, callback):
        """给按钮设置图标和点击回调"""
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"无法加载图片: {image_path}")
            return
        button.setText("")
        icon = QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(button.size())
        button.clicked.connect(callback)

    # ============================================================
    # ============          角色点击切换逻辑           ============
    # ============================================================
    def change_gg_image(self, event):
        new_image = random.choice(self.gg_images)
        self.gg_body.setPixmap(QPixmap(new_image))

    def change_cc_image(self, event):
        new_image = random.choice(self.cc_images)
        self.cc_body.setPixmap(QPixmap(new_image))

    # ============================================================
    # ============       pause按钮：停止当前音频       ============
    # ============================================================
    def pause_button_clicked(self):
        """
        点击pause按钮，就停止当前音频并恢复UI
        """
        self.stop_current_audio()

    # ============================================================
    # ============       mic按钮（点/右键菜单）        ============
    # ============================================================
    def mic_button_clicked(self):
        """
        单击 mic_button 时，随机播放一首歌。
        """
        song_index = random.randint(0, len(self.songs) - 1)
        self.play_song(song_index)

    def show_mic_menu(self, pos):
        menu = QMenu(self)
        menu.setFont(QFont("Microsoft YaHei", 12))
        menu.setStyleSheet("QMenu { background-color: lightgray; color: black; }"
                           "QMenu::item { padding: 5px 20px; }"
                           "QMenu::item:selected { background-color: gray; color: white; }")
        action1 = menu.addAction("Complete me")
        action2 = menu.addAction("返老还童")
        action3 = menu.addAction("好想大声说爱你")
        action4 = menu.addAction("海芋恋")
        action5 = menu.addAction("RingRingRing")
        action6 = menu.addAction("日日夜夜")
        action7 = menu.addAction("when you come around")
        action1.triggered.connect(lambda: self.play_song(0))
        action2.triggered.connect(lambda: self.play_song(1))
        action3.triggered.connect(lambda: self.play_song(2))
        action4.triggered.connect(lambda: self.play_song(3))
        action5.triggered.connect(lambda: self.play_song(4))
        action6.triggered.connect(lambda: self.play_song(5))
        action7.triggered.connect(lambda: self.play_song(6))
        menu.exec_(self.mic_button.mapToGlobal(pos))

    def play_song(self, song_index: int):
        """
        根据 song_index 播放 self.songs[song_index]，
        并安排对应的麦克风显示调度。
        """
        if not (0 <= song_index < len(self.songs)):
            return

        file_path = self.songs[song_index]
        total_duration = self.song_play_time_dict[file_path]
        mic_schedule = self.song_mic_schedules.get(song_index, [])
        # 调用统一方法开始新的音频
        self.start_new_audio(file_path, total_duration, mic_schedule)

    # ============================================================
    # ============  麦克风显示（由 start_new_audio 调度）  ============
    # ============================================================
    def set_mic_visibility(self, who: str):
        """
        who 可以是 "gg" / "cc" / "ggcc" / "none"
        分别表示只显示 gg 的麦克风、只显示 cc 的麦克风、都显示、都隐藏。
        """
        if who == "gg":
            self.gg_mic_label.setVisible(True)
            self.cc_mic_label.setVisible(False)
        elif who == "cc":
            self.gg_mic_label.setVisible(False)
            self.cc_mic_label.setVisible(True)
        elif who == "ggcc":
            self.gg_mic_label.setVisible(True)
            self.cc_mic_label.setVisible(True)
        else:  # "none" 或其他
            self.gg_mic_label.setVisible(False)
            self.cc_mic_label.setVisible(False)

    # ============================================================
    # ============       其它音频：信封、冰激凌等      ============
    # ============================================================
    def letter_button_clicked(self):
        """
        点击信封按钮 -> 播放 letter_cc.mp3 并在2s时显示泪水，22s时隐藏泪水
        """
        # 先计算播放时长(示例值 25000ms，如果实际音频不同可自行调整)
        duration = self.other_sounds_duration.get(self.letter_cc, 145200)

        self.start_new_audio(self.letter_cc, duration, None)

        # 安排泪水出现/隐藏
        t1 = QTimer(self)
        t1.setSingleShot(True)
        t1.timeout.connect(self.show_l_label)
        t1.start(2000)
        self.current_timers.append(t1)

        t2 = QTimer(self)
        t2.setSingleShot(True)
        t2.timeout.connect(self.hide_l_tear)
        t2.start(152000)
        self.current_timers.append(t2)

    def show_l_label(self):
        self.l_tear.setVisible(True)


    def hide_l_tear(self):
        self.l_tear.setVisible(False)

    def icecream_button_clicked(self):
        """
        播放 icecream_sound.mp3
        """
        duration = self.other_sounds_duration.get(self.icecream_sound, 8000)
        self.start_new_audio(self.icecream_sound, duration, None)

    def egg_button_clicked(self):
        # 假设 egg.mp3 也想做同样逻辑，可以这样写：
        self.start_new_audio(resource_path("egg.mp3"), 5600, None)
                # 安排泪水出现/隐藏
        t1 = QTimer(self)
        t1.setSingleShot(True)
        t1.timeout.connect(self.show_flush)
        t1.start(1000)
        self.current_timers.append(t1)

        t2 = QTimer(self)
        t2.setSingleShot(True)
        t2.timeout.connect(self.hide_flush)
        t2.start(5000)
        self.current_timers.append(t2)

    def show_flush(self):
        self.flush_1.setVisible(True)
        self.flush_2.setVisible(True)

    def hide_flush(self):
        self.flush_1.setVisible(False)
        self.flush_2.setVisible(False)

    def letter_button_gg_clicked(self):
        duration = self.other_sounds_duration.get(self.letter_gg, 96000)

        self.start_new_audio(self.letter_gg, duration, None)

    def rabbit_button_clicked(self):
        self.rabbit_ac.setVisible(not self.rabbit_ac.isVisible())

    def trex_button_clicked(self):
        self.trex_ac.setVisible(not self.trex_ac.isVisible())

    # ============================================================
    # ============           Timer 功能相关           ============
    # ============================================================
    def timer_button_clicked(self):
        """点击 Timer 按钮后，显示输入框和“开始”按钮"""
        self.timer_input.setVisible(True)
        self.timer_start_button.setVisible(True)

    def timer_start_button_clicked(self):
        """
        点击“开始”按钮，读取输入框的分钟数，开始倒计时。
        隐藏输入框与“开始”按钮，显示倒计时 Label 与 pause/end 按钮。
        """
        text = self.timer_input.text().strip()
        if not text.isdigit():
            print("请输入有效的分钟数!")
            return

        minutes = int(text)
        self.remaining_seconds = minutes * 60
        if self.remaining_seconds <= 0:
            print("请输入大于0的时长")
            return

        # 隐藏输入框和开始按钮
        self.timer_input.setVisible(False)
        self.timer_start_button.setVisible(False)

        # 重置定时器状态
        self.timer_is_paused = False
        # 显示倒计时 label，并更新一次文字
        self.timer_label.setVisible(True)
        self.update_timer_label()  # 立即显示一次

        # 显示暂停、结束按钮
        self.timer_pause_button.setVisible(True)
        self.timer_end_button.setVisible(True)

        # 启动 1s 间隔倒计时
        self.countdown_timer.start()

    def timer_pause_button_clicked(self):
        """
        暂停或继续倒计时。如果正在倒计时，则暂停；如果已经暂停，则继续。
        """
        if not self.timer_is_paused:
            # 暂停
            self.timer_is_paused = True
            self.countdown_timer.stop()
            print("倒计时已暂停")
        else:
            # 继续
            self.timer_is_paused = False
            self.countdown_timer.start()
            print("倒计时已继续")

    def timer_end_button_clicked(self):
        """
        结束倒计时。隐藏 label，复位状态，停止 QTimer。
        """
        self.countdown_timer.stop()
        self.remaining_seconds = 0
        self.timer_is_paused = False
        self.timer_label.setVisible(False)
        self.timer_pause_button.setVisible(False)
        self.timer_end_button.setVisible(False)
        print("倒计时已结束")

    def update_timer(self):
        """每秒触发一次，更新剩余时间，并刷新 label。"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_label()
            if self.remaining_seconds <= 0:
                # 倒计时结束
                self.countdown_timer.stop()
                self.timer_label.setVisible(False)
                self.timer_pause_button.setVisible(False)
                self.timer_end_button.setVisible(False)
        else:
            # 理论上不会跑到这里，因为剩余时间<=0 时已经 stop
            pass

    def update_timer_label(self):
        """把剩余秒数格式化成 MM:SS 显示在 timer_label 上。"""
        mm = self.remaining_seconds // 60
        ss = self.remaining_seconds % 60
        text = f"{mm:02d}:{ss:02d}"
        self.timer_label.setText(text)

    # ============================================================
    # ============     窗口拖动、悬浮按钮等逻辑       ============
    # ============================================================
    # 原来的鼠标拖动方法（现已由事件过滤器统一处理，下列方法保留但不启用）
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.old_pos = event.globalPos()
    #     # super().mousePressEvent(event)
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.LeftButton:
    #         # 拖动窗口
    #         delta = QPoint(event.globalPos() - self.old_pos)
    #         self.move(self.x() + delta.x(), self.y() + delta.y())
    #         self.old_pos = event.globalPos()
    #     # super().mouseMoveEvent(event)

    def check_hover_area(self):
        """
        定时器定期调用。若鼠标在 hover_button + 目标按钮 所组成的 union 区域内，
        则显示 hover_target_buttons；否则隐藏。
        """
        # mousePos：相对于本窗体 (self) 的坐标
        mousePos = self.mapFromGlobal(QCursor.pos())

        # 计算 union 区域
        rect_union = self.hover_trigger_button.geometry()
        for btn in self.hover_target_buttons:
            rect_union = rect_union.united(btn.geometry())

        # 加一些 margin
        margin = 10
        rect_union = rect_union.marginsAdded(QMargins(margin, margin, margin, margin))

        # 判断是否包含鼠标
        if rect_union.contains(mousePos):
            for btn in self.hover_target_buttons:
                btn.setVisible(True)
        else:
            for btn in self.hover_target_buttons:
                btn.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet_app = PetApp()
    pet_app.show()
    sys.exit(app.exec_())
