import tkinter as tk
import random
import os
from tkinter import messagebox
import winsound

# Пути к файлам
IMAGE_DIR = "C:\\Mario\\images"
MUSIC_FILE = "C:\\Mario\\sounds\\background.wav"

# Размеры игрового поля
SCREEN_WIDTH = 736
SCREEN_HEIGHT = 414
GROUND_LEVEL = 414 - 50

# Глобальные переменные
obstacles = []
game_active = True
double_jump = False
stop = False
score = 0
world_speed = -1
is_jumping = False
background_music_playing = False
gravity = 0.5
jump_speed = 0

def show_rules():
    messagebox.showinfo("Правила", 
                      "Правила игры:\n"
                      "1. Нажимайте пробел для прыжка\n"
                      "2. Можно прыгнуть дважды\n"
                      "3. Избегайте грибов\n"
                      "4. Чем дольше играете, тем быстрее препятствия")

def load_image(filename):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        return tk.PhotoImage(file=path)
    except:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {filename}")
        raise

def play_background_music():
    global background_music_playing
    if not background_music_playing:
        try:
            if os.path.exists(MUSIC_FILE):
                winsound.PlaySound(MUSIC_FILE, winsound.SND_ASYNC | winsound.SND_LOOP)
                background_music_playing = True
            else:
                messagebox.showwarning("Внимание", f"Файл музыки не найден: {MUSIC_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести музыку: {e}")

def stop_background_music():
    global background_music_playing
    if background_music_playing:
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
            background_music_playing = False
        except Exception as e:
            print(f"Не удалось остановить музыку: {e}")

def save_score(score):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scores_file = os.path.join(current_dir, "scores.txt")
        with open(scores_file, "a", encoding="utf-8") as file:
            file.write(f"{score}\n")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить счет: {str(e)}")

def check_collision():
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
    global game_active, stop, score
    game_active = False
    stop = True
    stop_background_music()
    save_score(score)
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

def jump(event=None):
    global is_jumping, jump_speed, double_jump, game_active
    if not game_active or (is_jumping and double_jump):
        return
        
    if not is_jumping:
        is_jumping = True
        jump_speed = -19
    elif not double_jump:
        double_jump = True
        jump_speed = -5
    
    apply_physics()

def reset_game():
    global obstacles, score, player, game_active, is_jumping, jump_speed, world_speed
    game_active = True
    stop = False
    score = 0
    is_jumping = False
    double_jump = False
    jump_speed = 0
    world_speed = -1
    
    for obstacle in obstacles:
        canvas.delete(obstacle[0])
    obstacles.clear()
    
    canvas.coords(player, 100, GROUND_LEVEL - 80 + 50)
    score_label.config(text="Score: 0")
    
    for x_pos in [300, 500, 700, 900]:
        obstacle = canvas.create_image(x_pos, GROUND_LEVEL, anchor=tk.NW, image=obstacle_image)
        obstacles.append([obstacle, [x_pos, GROUND_LEVEL]])
    
    play_background_music()
    move_background()
    move_obstacles()
    check_collision()
    update_score()

def start_game():
    global canvas, player, background, obstacle_image, score_label
    
    if not os.path.exists(MUSIC_FILE):
        messagebox.showwarning("Внимание", 
                             f"Файл фоновой музыки не найден:\n{MUSIC_FILE}\n"
                             "Игра будет запущена без музыки.")
    
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

    background = canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    player = canvas.create_image(100, GROUND_LEVEL - 80 + 50, anchor=tk.NW, image=player_image)

    score = 0
    score_label = tk.Label(window, text="Score: 0", font=("Arial", 20))
    score_label.place(x=SCREEN_WIDTH/2, y=20, anchor=tk.CENTER)
    
    obstacles.clear()
    for x_pos in [300, 500, 700, 900]:
        obstacle = canvas.create_image(x_pos, GROUND_LEVEL, anchor=tk.NW, image=obstacle_image)
        obstacles.append([obstacle, [x_pos, GROUND_LEVEL]])

    window.bind("<space>", jump)
    
    play_background_music()
    move_background()
    move_obstacles()
    check_collision()
    update_score()
    
    window.mainloop()

if __name__ == "__main__":
    show_rules()
    start_game()