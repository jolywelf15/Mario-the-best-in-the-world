import tkinter as tk
import random
import os
from tkinter import messagebox

# Путь к папке с изображениями
IMAGE_DIR = "C:\\Mario\\images"

# Размеры игрового поля
SCREEN_WIDTH = 736
SCREEN_HEIGHT = 414
GROUND_LEVEL = 414 - 50  # Уровень земли (50px высота объектов)

# Глобальные переменные
obstacles = []
speed_mod = 0
game_active = True
jump_tick = 0
double_jump = False
stop = False
score = 0
world_speed = -1
jump_height = 150  # Максимальная высота прыжка в пикселях
jump_speed = 0.12  # Текущая скорость прыжка
gravity = 0.5  # Сила гравитации
is_jumping = False  # Флаг прыжка

def load_image(filename):
    """Загрузка изображения из папки images"""
    try:
        path = os.path.join(IMAGE_DIR, filename)
        return tk.PhotoImage(file=path)
    except:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {filename}")
        raise

def save_score(score):
    """Сохранение счета в файл"""
    try:
        # Получаем путь к рабочей директории
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scores_file = os.path.join(current_dir, "scores.txt")
        
        # Открываем файл в режиме добавления (создаст, если не существует)
        with open(scores_file, "a", encoding="utf-8") as file:
            file.write(f"{score}\n")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить счет: {str(e)}")
        # Показываем полный путь к файлу для отладки
        messagebox.showinfo("Отладочная информация", 
                          f"Пытаемся сохранить в: {scores_file}\n"
                          f"Текущая директория: {current_dir}")

def check_collision():
    """Проверка столкновения игрока с препятствиями"""
    global game_active
    
    if not game_active:
        return
        
    player_coords = canvas.coords(player)
    player_left = player_coords[0]
    player_right = player_coords[0] + 46
    player_top = player_coords[1]
    player_bottom = player_coords[1] + 80
    
    for obstacle in obstacles:
        obs_coords = canvas.coords(obstacle[0])
        obs_left = obs_coords[0]
        obs_right = obs_coords[0] + 50
        obs_top = obs_coords[1]
        obs_bottom = obs_coords[1] + 50
        
        if (player_right > obs_left and 
            player_left < obs_right and 
            player_bottom > obs_top and 
            player_top < obs_bottom):
            game_over()
            return
    
    canvas.after(50, check_collision)

def game_over():
    """Обработка завершения игры"""
    global game_active, stop, score
    game_active = False
    stop = True
    save_score(score)  # Сохраняем счет перед показом сообщения
    messagebox.showinfo("Игра окончена", f"Ваш счет: {score}")
    reset_game()

def move_obstacles():
    global obstacles, canvas, world_speed, game_active
    
    if not game_active:
        return
        
    for obstacle in obstacles:
        canvas.move(obstacle[0], world_speed, 0)
        obstacle[1][0] += world_speed
        x = canvas.coords(obstacle[0])[0]
        if x < -50:
            new_x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 200)
            canvas.coords(obstacle[0], new_x, GROUND_LEVEL)
            obstacle[1][0] = new_x
    
    if game_active:
        canvas.after(10, move_obstacles)

def update_score():
    global score, score_label, world_speed, game_active
    
    if game_active:
        score += 1
        score_label.config(text=f"Score: {score}")
        
        if score > 10000:
            world_speed = -4
        elif score > 5000:
            world_speed = -3
        elif score > 1000:
            world_speed = -2
        else:
            world_speed = -1
    
    canvas.after(100, update_score)

def move_background():
    global world_speed, stop, game_active
    
    if not game_active or stop:
        return
        
    canvas.move(background, world_speed, 0)
    x1, y1, x2, y2 = canvas.bbox(background)
    
    if x2 <= SCREEN_WIDTH:
        canvas.move(background, x2 - x1, 0)
    
    if game_active:
        canvas.after(10, move_background)

def jump():
    global is_jumping, jump_speed, double_jump, game_active
    
    if not game_active or (is_jumping and double_jump):
        return
        
    if not is_jumping:
        is_jumping = True
        jump_speed = -19  # Начальная скорость прыжка
    elif not double_jump:
        double_jump = True
        jump_speed = -5  # Скорость двойного прыжка
    
    apply_physics()

def apply_physics():
    global is_jumping, jump_speed, double_jump
    
    if not is_jumping:
        return
        
    jump_speed += gravity
    canvas.move(player, 0, jump_speed)
    
    y = canvas.coords(player)[1]
    if y >= GROUND_LEVEL - 80 + 50:
        canvas.coords(player, canvas.coords(player)[0], GROUND_LEVEL - 80 + 50)
        is_jumping = False
        double_jump = False
        jump_speed = 0
    else:
        canvas.after(20, apply_physics)

def reset_game():
    global obstacles, score, player, stand_cactus, on_cactus, double_jump, game_active, is_jumping, jump_speed, world_speed
    
    # Полный сброс всех параметров
    game_active = True
    stop = False
    score = 0
    is_jumping = False
    double_jump = False
    jump_speed = 0
    world_speed = -1
    
    # Удаляем все препятствия
    for obstacle in obstacles:
        canvas.delete(obstacle[0])
    obstacles.clear()
    
    # Сбрасываем позицию игрока
    canvas.coords(player, 100, GROUND_LEVEL - 80 + 50)
    
    # Обновляем счет
    score_label.config(text="Score: 0")
    
    # Создаем новые препятствия
    for x_pos in [300, 500, 700, 900]:
        obstacle = canvas.create_image(x_pos, GROUND_LEVEL, anchor=tk.NW, image=obstacle_image)
        obstacles.append([obstacle, [x_pos, GROUND_LEVEL]])
    
    # Перезапускаем игровые процессы
    move_background()
    move_obstacles()
    check_collision()

def show_rules():
    messagebox.showinfo("Правила", "Правила игры:\n1. Нажимайте пробел для прыжка\n2. Можно прыгнуть дважды\n3. Избегайте грибов\n4. Чем дольше играете, тем быстрее препятствия")

def start_game():
    global screen_width, stop, stand_cactus, on_cactus, screen_height
    global canvas, player, background, obstacle_image, score_label
    
    # Инициализация игры
    double_jump = False
    stand_cactus = None
    on_cactus = False
    stop = False
    
    window = tk.Tk()
    window.title("Mario Game")
    
    canvas = tk.Canvas(window, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    window.resizable(False, False)
    canvas.pack()

    try:
        background_image = load_image("background.png")
        player_image = load_image("player.png")
        obstacle_image = load_image("obstacle.png")
    except:
        return

    # Создание игровых объектов
    background = canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    player = canvas.create_image(100, GROUND_LEVEL - 80 + 50, anchor=tk.NW, image=player_image)

    # Счет
    score = 0
    score_label = tk.Label(window, text="Score: 0", font=("Arial", 20))
    score_label.place(x=SCREEN_WIDTH/2, y=20, anchor=tk.CENTER)
    
    # Создание препятствий
    obstacles.clear()
    for x_pos in [300, 500, 700, 900]:
        obstacle = canvas.create_image(x_pos, GROUND_LEVEL, anchor=tk.NW, image=obstacle_image)
        obstacles.append([obstacle, [x_pos, GROUND_LEVEL]])

    # Управление
    window.bind("<space>", lambda event: jump())
    
    # Запуск игровых процессов
    move_background()
    move_obstacles()
    check_collision()
    update_score()
    
    window.mainloop()

if __name__ == "__main__":
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scores_file = os.path.join(current_dir, "scores.txt")
        if not os.path.exists(scores_file):
            with open(scores_file, "w", encoding="utf-8") as file:
                file.write("")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать файл scores.txt: {str(e)}")
    
    show_rules()
    start_game()