import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, 
                            QGraphicsView, QGraphicsPolygonItem, QGraphicsTextItem,
                            QPushButton, QVBoxLayout, QWidget, QLabel, QGraphicsRectItem)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QBrush, QColor, QFont, QPolygonF, QPen

class StartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("background-color: #333;")
        
        layout = QVBoxLayout()
        
        # Заголовок игры
        title = QLabel("Super Mario Clone")
        title.setStyleSheet("font-size: 40px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        # Кнопка старта
        self.start_btn = QPushButton("Старт")
        self.start_btn.setStyleSheet(
            "QPushButton {"
            "background-color: #4CAF50;"
            "border: none;"
            "color: white;"
            "padding: 15px 32px;"
            "text-align: center;"
            "text-decoration: none;"
            "font-size: 16px;"
            "margin: 4px 2px;"
            "border-radius: 8px;"
            "}"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.start_btn.setFixedSize(200, 50)
        
        # Кнопка настроек
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.setStyleSheet(
            "QPushButton {"
            "background-color: #f39c12;"
            "border: none;"
            "color: white;"
            "padding: 15px 32px;"
            "text-align: center;"
            "text-decoration: none;"
            "font-size: 16px;"
            "margin: 4px 2px;"
            "border-radius: 8px;"
            "}"
            "QPushButton:hover { background-color: #e67e22; }"
        )
        self.settings_btn.setFixedSize(200, 50)
        
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addSpacing(50)
        layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        layout.addWidget(self.settings_btn, 0, Qt.AlignCenter)
        layout.addStretch(1)
        
        self.setLayout(layout)

class MarioGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mario-like Game with PyQt5")
        self.setFixedSize(800, 400)
        
        # Главный виджет и стек
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Начальный экран
        self.start_screen = StartScreen()
        self.start_screen.start_btn.clicked.connect(self.start_game)
        self.start_screen.settings_btn.clicked.connect(self.show_settings)
        
        # Игровой экран
        self.game_view = QGraphicsView()
        self.game_scene = QGraphicsScene()
        self.game_view.setScene(self.game_scene)
        self.game_view.hide()
        
        self.layout.addWidget(self.start_screen)
        self.layout.addWidget(self.game_view)
        
        # Инициализация игры
        self.init_game()
    
    def init_game(self):
        # Настройки игры
        self.gravity = 0.5
        self.jump_strength = -12
        self.move_speed = 5
        self.player_x_vel = 0
        self.player_y_vel = 0
        self.is_jumping = False
        self.score = 0
        self.lives = 3
        
        # Состояние клавиш
        self.keys_pressed = {
            Qt.Key_A: False,
            Qt.Key_D: False,
            Qt.Key_Space: False
        }
        
        # Очищаем сцену
        self.game_scene.clear()
        self.game_scene.setSceneRect(0, 0, 800, 400)
        self.game_scene.setBackgroundBrush(QBrush(QColor(135, 206, 235)))
        
        # Создаем треугольного игрока
        self.create_triangle_player()
        
        # Создаем землю
        self.ground = QGraphicsRectItem(0, 0, 800, 50)
        self.ground.setBrush(QBrush(QColor(139, 69, 19)))
        self.ground.setPos(0, 350)
        self.game_scene.addItem(self.ground)
        
        # Платформы
        self.platforms = []
        self.create_platform(200, 280, 200, 10)
        self.create_platform(500, 250, 200, 10)
        self.create_platform(300, 200, 200, 10)
        
        # Враги
        self.enemies = []
        self.enemy_timer = QTimer(self)
        self.enemy_timer.timeout.connect(self.spawn_enemy)
        
        # Монеты
        self.coins = []
        self.spawn_coins(5)
        
        # Интерфейс
        self.score_text = QGraphicsTextItem(f"Score: {self.score}")
        self.score_text.setFont(QFont("Arial", 14))
        self.score_text.setDefaultTextColor(QColor(255, 255, 255))
        self.score_text.setPos(10, 10)
        self.game_scene.addItem(self.score_text)
        
        self.lives_text = QGraphicsTextItem(f"Lives: {self.lives}")
        self.lives_text.setFont(QFont("Arial", 14))
        self.lives_text.setDefaultTextColor(QColor(255, 255, 255))
        self.lives_text.setPos(700, 10)
        self.game_scene.addItem(self.lives_text)
        
        # Игровой цикл
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_loop)
        
        # Фокус
        self.game_view.setFocus()
        self.game_view.setFocusPolicy(Qt.StrongFocus)
    
    def create_triangle_player(self):
        # Создаем треугольник (указываем три точки)
        triangle = QPolygonF()
        triangle.append(QPointF(15, 0))    # Верхняя точка
        triangle.append(QPointF(0, 30))    # Левая нижняя точка
        triangle.append(QPointF(30, 30))   # Правая нижняя точка
        
        self.player = QGraphicsPolygonItem(triangle)
        self.player.setBrush(QBrush(QColor(255, 182, 193)))  # Розовый цвет
        self.player.setPen(QPen(Qt.black, 1))  # Черная обводка
        self.player.setPos(50, 320)
        self.game_scene.addItem(self.player)
    
    def start_game(self):
        self.start_screen.hide()
        self.game_view.show()
        self.game_view.setFocus()
        self.enemy_timer.start(3000)
        self.game_timer.start(30)
    
    def show_settings(self):
        # Здесь можно добавить логику настроек
        print("Настройки игры")
    
    def create_platform(self, x, y, width, height):
        platform = QGraphicsRectItem(0, 0, width, height)
        platform.setBrush(QBrush(QColor(0, 128, 0)))
        platform.setPos(x, y)
        self.game_scene.addItem(platform)
        self.platforms.append(platform)
    
    def spawn_enemy(self):
        enemy = QGraphicsRectItem(0, 0, 30, 20)
        enemy.setBrush(QBrush(QColor(0, 0, 0)))
        enemy.setPos(800, 330)
        self.game_scene.addItem(enemy)
        self.enemies.append({
            'item': enemy,
            'x_vel': -3,
            'y_vel': 0
        })
    
    def spawn_coins(self, count):
        for _ in range(count):
            coin = QGraphicsRectItem(0, 0, 15, 15)
            coin.setBrush(QBrush(QColor(255, 215, 0)))
            x = random.randint(100, 700)
            y = random.randint(100, 300)
            coin.setPos(x, y)
            self.game_scene.addItem(coin)
            self.coins.append(coin)
    
    def keyPressEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed[event.key()] = True
            self.update_movement()
    
    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed[event.key()] = False
            self.update_movement()
    
    def update_movement(self):
        if self.keys_pressed[Qt.Key_A] and not self.keys_pressed[Qt.Key_D]:
            self.player_x_vel = -self.move_speed
        elif self.keys_pressed[Qt.Key_D] and not self.keys_pressed[Qt.Key_A]:
            self.player_x_vel = self.move_speed
        else:
            self.player_x_vel = 0
        
        if self.keys_pressed[Qt.Key_Space] and not self.is_jumping:
            self.player_y_vel = self.jump_strength
            self.is_jumping = True
    
    def check_collisions(self):
        player_rect = self.player.sceneBoundingRect()
        
        # Столкновение с землей
        if player_rect.bottom() >= 350:
            self.player.setY(350 - player_rect.height())
            self.player_y_vel = 0
            self.is_jumping = False
        
        # Столкновение с платформами
        for platform in self.platforms:
            platform_rect = platform.sceneBoundingRect()
            if (player_rect.right() > platform_rect.left() and 
                player_rect.left() < platform_rect.right() and
                player_rect.bottom() >= platform_rect.top() and 
                player_rect.top() < platform_rect.top()):
                if self.player_y_vel > 0:
                    self.player.setY(platform_rect.top() - player_rect.height())
                    self.player_y_vel = 0
                    self.is_jumping = False
        
        # Столкновение с врагами
        for enemy in self.enemies[:]:
            enemy_rect = enemy['item'].sceneBoundingRect()
            if player_rect.intersects(enemy_rect):
                if self.player_y_vel > 0 and player_rect.top() < enemy_rect.top():
                    self.game_scene.removeItem(enemy['item'])
                    self.enemies.remove(enemy)
                    self.player_y_vel = self.jump_strength / 2
                    self.score += 100
                    self.score_text.setPlainText(f"Score: {self.score}")
                else:
                    self.lives -= 1
                    self.lives_text.setPlainText(f"Lives: {self.lives}")
                    if self.lives <= 0:
                        self.game_over()
                    else:
                        self.player.setPos(50, 320)
                        self.player_y_vel = 0
                        self.is_jumping = False
        
        # Сбор монет
        for coin in self.coins[:]:
            coin_rect = coin.sceneBoundingRect()
            if player_rect.intersects(coin_rect):
                self.game_scene.removeItem(coin)
                self.coins.remove(coin)
                self.score += 50
                self.score_text.setPlainText(f"Score: {self.score}")
                if random.random() < 0.3:
                    self.spawn_coins(1)
    
    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy['item'].moveBy(enemy['x_vel'], enemy['y_vel'])
            if enemy['item'].sceneBoundingRect().right() < 0:
                self.game_scene.removeItem(enemy['item'])
                self.enemies.remove(enemy)
    
    def game_over(self):
        game_over_text = QGraphicsTextItem("GAME OVER")
        game_over_text.setFont(QFont("Arial", 30))
        game_over_text.setDefaultTextColor(QColor(255, 0, 0))
        game_over_text.setPos(300, 180)
        self.game_scene.addItem(game_over_text)
        self.game_timer.stop()
        self.enemy_timer.stop()

    def game_loop(self):
        self.player_y_vel += self.gravity
        self.player.moveBy(self.player_x_vel, self.player_y_vel)
        
        player_rect = self.player.sceneBoundingRect()
        if player_rect.left() < 0:
            self.player.setX(0)
        elif player_rect.right() > 800:
            self.player.setX(800 - player_rect.width())
        
        self.update_enemies()
        self.check_collisions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MarioGame()
    game.show()
    sys.exit(app.exec_())