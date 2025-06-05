import tkinter as tk
import random
from tkinter import messagebox
from PIL import Image, ImageTk  # Для работы с изображениями

# Глобальные переменные
obstacles = []
world_speed = -1
stop = False
on_cactus = False
stand_cactus = None
double_jump = False
score = 0
jump_tick = 0
# Загрузка изображений
def load_images():
    global background_img, player_img, obstacle_img
    
    try:
        # Фон
        bg = Image.open("background.png")
        bg = bg.resize((800, 422), Image.LANCZOS)
        background_img = ImageTk.PhotoImage(bg)
        
        # Игрок
        pl = Image.open("player.png")
        pl = pl.resize((30, 50), Image.LANCZOS)
        player_img = ImageTk.PhotoImage(pl)
        
        # Препятствие
        obs = Image.open("obstacle.png")
        obs = obs.resize((40, 50), Image.LANCZOS)
        obstacle_img = ImageTk.PhotoImage(obs)
        
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображения: {e}")
        return False

def move_obstacles():
    global obstacles, world_speed
    for obstacle in obstacles:
        canvas.move(obstacle[0], world_speed, 0)
        obstacle[1][0] += world_speed
        x = canvas.coords(obstacle[0])[0]
        if x < -100:
            new_x = random.randint(800, 900)
            canvas.move(obstacle[0], new_x - x, 0)
            obstacle[1][0] = new_x
        check_player_collision(obstacle)
    canvas.after(10, move_obstacles)

def check_player_collision(obstacle):
    global player, stop, score
    
    player_coords = canvas.coords(player)
    obstacle_coords = canvas.coords(obstacle[0])
    
    # Простая проверка столкновения
    if (player_coords[0] < obstacle_coords[0] + 40 and
        player_coords[0] + 30 > obstacle_coords[0] and
        player_coords[1] < obstacle_coords[1] + 50 and
        player_coords[1] + 50 > obstacle_coords[1]):
        
        stop = True
        messagebox.showinfo("Game Over", f"Ваш счет: {score}")
        reset_game()
        stop = False

def update_score():
    global score, score_label, world_speed
    score += 1
    score_label.config(text=f"Score: {score}")
    
    # Увеличиваем сложность
    if score > 1000:
        world_speed = -4
    elif score > 500:
        world_speed = -3
    elif score > 200:
        world_speed = -2

def move_background():
    global background, world_speed
    if not stop:
        canvas.move(background, world_speed, 0)
        x = canvas.coords(background)[0]
        if x < -700:
            canvas.move(background, 800, 0)
        update_score()
    canvas.after(10, move_background)

def jump_animation():
    global jump_tick, player
    canvas.move(player, 0, -12)
    jump_tick += 1
    if jump_tick >= 10:
        jump_tick = 0
        canvas.after(10, fall)
    else:
        canvas.after(20, jump_animation)

def jump(event=None):
    global double_jump
    if not double_jump:
        double_jump = True
        jump_animation()

def fall():
    global double_jump, player
    canvas.move(player, 0, 8)
    y = canvas.coords(player)[1]
    if y < 350:  # Высота земли
        canvas.after(10, fall)
    else:
        double_jump = False

def reset_game():
    global obstacles, score, player
    
    score = 0
    score_label.config(text="Score: 0")
    
    # Сброс позиции игрока
    canvas.coords(player, 100, 300)
    
    # Сброс препятствий
    for i, obstacle in enumerate(obstacles):
        new_x = 300 + i * 200
        canvas.coords(obstacle[0], new_x, 350)
        obstacle[1][0] = new_x
    
    world_speed = -1
    canvas.after(1000, lambda: move_obstacles())

def show_rules():
    messagebox.showinfo("Правила", 
        "Управление:\nПробел - прыжок\n\nЦель:\nИзбегайте препятствий и наберите как можно больше очков!")

def start_game():
    global canvas, player, background, score_label
    
    if not load_images():
        return
    
    window = tk.Tk()
    window.title("Dino Game")
    window.resizable(False, False)
    
    canvas = tk.Canvas(window, width=800, height=422)
    canvas.pack()
    
    # Создание фона
    background = canvas.create_image(0, 0, anchor=tk.NW, image=background_img)
    canvas.create_image(800, 0, anchor=tk.NW, image=background_img)  # Второй фон для бесшовного скролла
    
    # Создание игрока
    player = canvas.create_image(100, 350, anchor=tk.NW, image=player_img)
    
    # Создание препятствий
    for x in [300, 500, 700, 900]:
        obstacle = canvas.create_image(x, 350, anchor=tk.NW, image=obstacle_img)
        obstacles.append([obstacle, [x, 350]])
    
    # Счет
    score_label = tk.Label(window, text="Score: 0", font=("Arial", 20), bg="white")
    score_label.place(x=400, y=20)
    
    # Управление
    window.bind("<space>", jump)
    window.bind("<Up>", jump)
    
    # Запуск игрового цикла
    move_background()
    move_obstacles()
    
    show_rules()
    window.mainloop()

# Запуск игры
start_game()