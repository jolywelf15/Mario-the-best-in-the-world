
import os
from random import randint as rand
from time import sleep
from tkinter import Tk, Canvas, Button, Entry, StringVar, PhotoImage

# !---------------------------Global Variables----------------------------
fps = 90  # how frequent game_loop calls itself
canvasWidth = 1280
canvasHeight = 720
maxJump = 255
jumpSpeed = -0.12  # increase abs value to increase
dinoHeight = 80
dinoWidth = 46
rocketWidth = 85
rocketHeight = 50
obstacleHeight = 50
obstacleWidth = 50
obstacleSpeed = -8  # increase abs value to increase
obstacleProbability = 4  # probability /100 of spawning obstacle
cactusProbability = 65  # probability of spawning a mushroom over rocket
difficultyIncrease = 500  # difficulty increases after n iterations
decreaseSpawnDistance = 0
scoreFilename = "scores.txt"
saveFileName = "saveFile.txt"
customFont = ("Arial Bold", 50)


# !-------------------------------Functions-------------------------------
def configure_window():
    """Configure window size, backgorund and title"""

    res = str(canvasWidth) + "x" + str(canvasHeight)
    window.geometry(res)
    window.configure(background='#b3ffff')
    window.title("M A R I O - S A U R")


def clean_window():
    """Destroys unnecessary objects to save space and performance"""

    global dino, canvas, label_pause, score_label, restartGameButton
    global quitButton, stopCanvas, gameOverCanvas, mainMenuCanvas, bossCanvas
    global startButton, saveGameButton, resumeButton
    if startButton is not None:
        startButton.destroy()
    if restartGameButton is not None:
        restartGameButton.destroy()
    if quitButton is not None:
        quitButton.destroy()
    if stopCanvas is not None:
        stopCanvas.destroy()
    if gameOverCanvas is not None:
        gameOverCanvas.destroy()
    if saveGameButton is not None:
        saveGameButton.destroy()
    if resumeButton is not None:
        resumeButton.destroy()
    if mainMenuCanvas is not None:
        mainMenuCanvas.destroy()
    if bossCanvas is not None:
        bossCanvas.destroy()


def keyPressed(event):
    """Called when a key is pressed. That key is stored in event.char"""

    global cheatCollision, cheatInfiniteJump, bossKeyChecked
    global jumpKey, invulnerabilityKey, infiniteJumpKey, pauseKey, bossKey

    if event.char == jumpKey:  # JUMP
        jump()
    elif event.char == invulnerabilityKey:  # INVULNERABILITY
        cheatCollision = -cheatCollision
    elif event.char == infiniteJumpKey:  # INFINITEJUMP
        cheatInfiniteJump = -cheatInfiniteJump
    elif event.char == pauseKey:  # PAUSE
        pause()
    elif event.char == bossKey:  # BOSSKEY
        bossKeyChecked = -bossKeyChecked
        bossKeyCheckedPressed()


def bossKeyCheckedPressed():
    """When boss key is pressed, displays pauses game and show image
       When it is pressed again, go to pause menu"""

    global bossCanvas, paused, bossKeyChecked

    if bossKeyChecked == -1:  # Key is false
        window.after(100, pause)

    elif bossKeyChecked == 1:  # Key is true
        paused = True
        bossCanvas = Canvas(window, width=canvasWidth, height=canvasHeight)
        bossCanvas.grid(column=0, row=0)
        bossCanvas.config(bg="darkblue")
        bossCanvas.create_image(0, 0, anchor="nw", image=bossBackground_img)


def pause():
    """Pauses the game and show the game pause menu.
    Options are: resume, save, return to main menu"""

    global paused, stopCanvas
    global saveGameButton, returnMainMenuButton, resumeButton

    # Pauses the game and prevent game_loop from calling itself
    paused = True

    # Create game pause menu and show the buttons. Show label "pause"
    stopCanvas = Canvas(window, width=canvasWidth, height=canvasHeight)
    stopCanvas.grid(column=0, row=0)
    stopCanvas.config(bg="darkgrey")
    resumeButton = Button(window, text="Resume", command=resume_game,
                          image=button_resume_img, bg="darkgrey")
    saveGameButton = Button(window, text="Save Game", command=save_game,
                            image=button_saveGame_img, bg="darkgrey")
    returnMainMenuButton = Button(window, text="Return to main Menu",
                                  command=main_menu, bg="darkgrey",
                                  image=button_mainMenu_img)
    stopCanvas.create_window(25, 25, anchor="nw",
                             height=100, width=400, window=resumeButton)
    stopCanvas.create_window(25, 150, anchor="nw",
                             height=100, width=400, window=saveGameButton)
    stopCanvas.create_window(25, 275, anchor="nw", height=100,
                             width=400, window=returnMainMenuButton)
    stopCanvas.create_text(710, 170, anchor="nw", fill="white",
                           text="Paused", font=("Impact", 50))


def save_game():
    """Save the game by writing to a file Score, lastGenerated,
    position of Dino, of obstacles"""

    global saveFile, obstacleList, dino, canvas, playerName
    global iterationCounter, lastGenerated, playerNameEntry

    # Save position of obstacles in a list "obstaclePosList"
    # and append their ID
    obstaclePosList = []
    for obs in obstacleList:
        coor = canvas.coords(obs[0])
        id = obs[1]
        obstaclePosList.append([coor, id])
    dinoPos = canvas.coords(dino)

    # Delete the File if it already exists, otherwise do nothing
    try:
        os.remove(saveFileName)
    except:
        pass

    main_menu()

    # Create the File in append mode and write data without brackets
    saveFile = open(saveFileName, "a")
    saveFile.write(playerName + "\n")
    saveFile.write(str(iterationCounter) + "\n")
    saveFile.write(str(lastGenerated) + "\n")
    saveFile.write(str(dinoPos).replace("[", "").replace("]", "") + "\n")
    for item in obstaclePosList:
        saveFile.write(str(item).replace("[", "").replace("]", "") + "\n")
    saveFile.close()


def jump():
    global cheatInfiniteJump, paused
    pos = canvas.coords(dino)

    # If cheat not in place then check that dino is
    # not already flying
    if cheatInfiniteJump == -1:
        if pos[1] != canvasHeight-dinoHeight:
            return

    # Perform a jump, according to jump speed and height
    y = jumpSpeed
    firstJump = False
    while True:
        pos = canvas.coords(dino)
        if pos[1] <= canvasHeight-dinoHeight-maxJump:
            y = -y
        if pos[1] >= canvasHeight-dinoHeight and firstJump is True:
            break
        canvas.move(dino, 0, y)
        window.update()
        firstJump = True


def check_collision(pos1, obs):
    """Returns True if a collision is detected, False otherwise.
       Since dealing with img, only topleft (x,y) are recorded,
       so it appends width and height according to the object"""

    # Append missing coordinates accordin to object
    if obs[1] == 'm':
        pos2 = canvas.coords(obs[0])
        pos2.append(pos2[0]+obstacleHeight)
        pos2.append(pos2[1]+obstacleHeight)
    else:
        pos2 = canvas.coords(obs[0])
        pos2.append(pos2[0]+rocketWidth)
        pos2.append(pos2[1]+rocketHeight)

    pos1.append(pos1[0]+dinoWidth)
    pos1.append(pos1[1]+dinoHeight)

    # Collision check
    if len(pos1) == 4 and len(pos2) == 4:
        if (pos1[0] < pos2[2] and pos1[2] > pos2[0] and
           pos1[1] < pos2[3] and pos1[3] > pos2[1]):
            return True
        return False


def create_obstacle(obstacleList):
    """When This Function is called, it creates an obstacle and
      it appends it to the obstacleList, with an ID, with
      a certain probability. Then it returns the obstaclelist"""

    r = rand(0, 100)
    if r < cactusProbability:
        obsImg = canvas.create_image(canvasWidth-10,
                                     canvasHeight-obstacleHeight,
                                     image=mushroom_img, anchor="nw")
        obs = [obsImg, 'm']
    else:
        obsImg = canvas.create_image(canvasWidth-25,
                                     canvasHeight-dinoHeight-5-rocketHeight,
                                     image=rocket_img, anchor="nw")
        obs = [obsImg, 'r']
    obstacleList.append(obs)
    return obstacleList


def get_best_score(scoreFile):
    """Gets the best score from the score file and return it"""

    best = 0
    lines = scoreFile.readlines()
    allLines = []

    for line in lines:
        allLines.append(line)

    for i in range(len(allLines)):
        tempList = allLines[i].split(",")
        temp = int(tempList[0])
        if temp > best:
            best = temp
    return best


def get_3_best_scores(scoreFile):
    """Gets the 3 best scores from the file and return them"""

    best = 0
    lines = scoreFile.readlines()
    allLines = []
    bestValues = []
    best3 = []
    counter = 0

    for line in lines:
        allLines.append(line)
        counter += 1

    if counter >= 3:  # Check if the file has at least 3 scores
        for j in range(3):
            best = 0
            for i in range(len(allLines)):
                tempList = allLines[i].split(",")
                temp = int(tempList[0])
                if j == 0:
                    if temp > best:
                        best = temp
                        index = i
                else:
                    if temp > best and temp not in bestValues:
                        best = temp
                        index = i
            best3.append(allLines[index])
            splitList = best3[j].split(",")
            bestValues.append(int(splitList[0]))
        return best3
    else:  # File has not at least 3 scores
        for j in range(counter):
            best = 0
            for i in range(len(allLines)):
                tempList = allLines[i].split(",")
                temp = int(tempList[0])
                if j == 0:
                    if temp > best:
                        best = temp
                        index = i
                else:
                    if temp > best and temp not in bestValues:
                        best = temp
                        index = i
            best3.append(allLines[index])
            splitList = best3[j].split(",")
            bestValues.append(int(splitList[0]))
        return best3


def move_obstacles(obstacleList):
    """Loop Through all the obstacles and move them by their speed"""

    for obs in obstacleList:
        pos = canvas.coords(obs[0])
        canvas.move(obs[0], obstacleSpeed, 0)
        if len(pos) == 4:
            if pos[2] <= 0:  # Remove obstacle from list to save space
                obstacleList.remove(obs)

    window.update()


def pause_game_1():
    global canvas, label_pause
    label_pause = canvas.create_text(canvasWidth/2, canvasHeight/2,
                                     fill="purple",
                                     font=("Impact", 80), text="3")


def pause_game_2():
    global canvas, label_pause
    canvas.itemconfig(label_pause, text="2")


def pause_game_3():
    global canvas, label_pause
    canvas.itemconfig(label_pause, text="1")


def pause_game_4():
    global canvas, label_pause
    canvas.itemconfig(label_pause, text="GO!")


def pause_game_5():
    global canvas, label_pause
    canvas.itemconfig(label_pause, text="")


def pause_game_3_sec():
    """When this function gets called, pauses the game for 3 seconds
      and shows a countdown on a label"""

    window.after(300, pause_game_1)
    window.after(600, pause_game_2)
    window.after(900, pause_game_3)
    window.after(1200, pause_game_4)
    window.after(1500, pause_game_5)


def game_over():
    """This function is called when a collision is detected.
    Options are: restart, back to main menu, quit"""

    global gameOverCanvas, restartGameButton, quitButton
    global paused, scoreFile, iterationCounter
    global playerName, gameOverBackground_img, returnMainMenuButton2

    # Stop the Game
    paused = True

    # Show game over menu and buttons
    gameOverCanvas = Canvas(window, width=canvasWidth, height=canvasHeight)
    gameOverCanvas.grid(column=0, row=0)
    gameOverCanvas.config(bg="darkblue")
    gameOverCanvas.create_image(0, 0, image=gameOverBackground_img,
                                anchor="nw")

    # Create buttons
    restartGameButton = Button(window, text="Restart Game", command=start_game,
                               image=button_restartGame_img)
    quitButton = Button(window, text="Quit Game", command=quit,
                        image=button_quit_img)
    returnMainMenuButton2 = Button(window, text="Return to main Menu",
                                   command=main_menu,
                                   image=button_mainMenu_img)

    # Place Buttons
    gameOverCanvas.create_window(25, 25, anchor="nw",
                                 height=100, width=400,
                                 window=restartGameButton)
    gameOverCanvas.create_window(25, 150, anchor="nw",
                                 height=100, width=400,
                                 window=returnMainMenuButton2)
    gameOverCanvas.create_window(25, 275, anchor="nw",
                                 height=100, width=400,
                                 window=quitButton)

    # Open file and print the score
    scoreFile = open(scoreFilename, "a+")
    scoreFile.write(str(iterationCounter) + ", " + playerName + "\n")
    scoreFile.close()

    # Get 3 best scores and write a leaderboard
    scoreFile = open(scoreFilename, "r")
    best3 = get_3_best_scores(scoreFile)
    scoreFile.close()
    best_score_label = gameOverCanvas.create_text(600, 25, text="Leadeboard")
    for i in range(len(best3)):
        score = gameOverCanvas.create_text(1100, 50+50*i,
                                           text=best3[i].strip("\n"),
                                           font=("impact", 30), fill="white")


def resume_game():
    """Called when game is resumed from pause.
      Sets paused to False, destroys unnecessary items
      and calls game_loop after waiting for 3 seconds"""

    global paused, stopCanvas, resumeButton

    # Destroy unnecessary item and pausing
    clean_window()
    paused = False

    # Wait 3 seconds and call game_loop
    pause_game_3_sec()
    window.after(1500, game_loop)


def start_game():
    global dino, canvas, obstacleList, paused, iterationCounter
    global best_score_label, scoreFile, lastGenerated, playerName, start_game
    global textErrorPlayerName, playerNameEntry, dino_pic
    global mainBackground1, mainBackground2, label_pause, score_label

    # Check a valid name has been entered
    if len(playerNameEntry.get()) == 0 or "," in playerNameEntry.get():
        textErrorPlayerName = "Invalid name!"
        main_menu()

    else:
        #  Initialize and reset components
        textErrorPlayerName = ""
        playerName = playerNameEntry.get()
        obstacleList = []
        paused = False
        iterationCounter = 0
        lastGenerated = 0

        # Create main Canvas items
        canvas = Canvas(window, width=canvasWidth, height=canvasHeight)
        canvas.focus_set()
        canvas.grid(column=0, row=0)
        canvas.config(bg="black")
        mainBackground1 = canvas.create_image(0, 0, image=main_background_img,
                                              anchor="nw")
        mainBackground2 = canvas.create_image(canvasWidth, 0,
                                              image=main_background_img,
                                              anchor="nw")
        dino = canvas.create_image(canvasWidth/4, canvasHeight-dinoHeight,
                                   image=mario_img, anchor="nw")

        # Read scoreFile and display best score on screen
        scoreFile = open(scoreFilename, "r")
        bestScore = get_best_score(scoreFile)
        best_score_label = canvas.create_text(canvasWidth/2-30, 10,
                                              fill="white",
                                              font="Times 20 italic bold",
                                              text="Best Score: " +
                                              str(bestScore))
        scoreFile.close()

        # Wait 3 seconds before starting and call game_loop()
        pause_game_3_sec()
        canvas.bind("<Key>", keyPressed)
        score_label = canvas.create_text(canvasWidth-50, 10, fill="white",
                                         font="Times 20 italic bold", text="")
        window.after(1500, game_loop)


def load_game():
    """Loads game status from savefile, places dino, obstacles (accordingly),
       player name, lastIteration, score and updates score label"""

    global dino, canvas, label_pause, score_label, obstacleList, paused
    global best_score_label, scoreFile, lastGenerated, noSaveFileLabel
    global mainBackground1, mainBackground2, iterationCounter, start_game
    global mainMenuCanvas, playerNameEntry, playerName

    obstacleList = []
    obstaclePosList = []
    try:
        saveFile = open(saveFileName, "r")

        # Create main Canvas items
        canvas = Canvas(window, width=canvasWidth, height=canvasHeight)
        canvas.focus_set()
        canvas.grid(column=0, row=0)
        canvas.config(bg="black")
        mainBackground1 = canvas.create_image(0, 0, image=main_background_img,
                                              anchor="nw")
        mainBackground2 = canvas.create_image(canvasWidth, 0,
                                              image=main_background_img,
                                              anchor="nw")

        # Retrieve data and update global variables
        playerName = saveFile.readline()
        playerName = playerName.strip(" ").strip("\n")
        iterationCounter = int(saveFile.readline())
        lastGenerated = int(saveFile.readline())
        dinoPos = saveFile.readline().split(",")
        for remainingLine in saveFile:
            if len(remainingLine.split(",")) == 3:
                temp = remainingLine.split(",")
                if float(temp[1]) >= float(canvasHeight/2):
                    obstaclePosList.append(remainingLine.split(","))

        dino = canvas.create_image(canvasWidth/4, canvasHeight-dinoHeight,
                                   image=mario_img, anchor="nw")
        for obs in obstaclePosList:
            if obs[2].strip(" ").rstrip() == "'m'":
                mushroom = canvas.create_image(int(float(obs[0])),
                                               int(float(obs[1])),
                                               image=mushroom_img,
                                               anchor="nw")
                obstacleList.append([mushroom, 'm'])
            else:
                rocket = canvas.create_image(int(float(obs[0])),
                                             int(float(obs[1])),
                                             image=rocket_img,
                                             anchor="nw")
                obstacleList.append([rocket, 'r'])

        paused = False

        # Read scoreFile and display best score on screen
        scoreFile = open(scoreFilename, "r")
        bestScore = get_best_score(scoreFile)
        best_score_label = canvas.create_text(canvasWidth/2-30, 10,
                                              fill="white",
                                              font="Times 20 italic bold",
                                              text="Best Score: " +
                                              str(bestScore))
        score_label = canvas.create_text(canvasWidth-50, 10,
                                         fill="white",
                                         font="Times 20 italic bold", text="")

        # Wait 3 seconds before starting and call game_loop().
        # Close used files.
        pause_game_3_sec()
        canvas.bind("<Key>", keyPressed)
        saveFile.close()
        scoreFile.close()
        window.after(1800, game_loop)

    except:
        mainMenuCanvas.itemconfig(noSaveFileLabel, text="No games saved!")


def game_loop():
    """Main game loop. This function increases difficulty each N iterations,
      it calls create_obstacle(), move_obstacles(), check_collision() and
      increments iterationCounter. Then it calls itself again
      if the game is not paused"""

    global obstacleList, obstacleProbability, obstacleSpeed, dino
    global iterationCounter, score_label, canvas, playerName
    global lastGenerated, cheatCollision, decreaseSpawnDistance
    global mainBackground1, mainBackground2, label_pause

    # Move backgrounds. When one reaches the left end,
    # restore it to the right end
    canvas.move(mainBackground1, -1, 0)
    canvas.move(mainBackground2, -1, 0)
    allBackgrounds = [mainBackground1, mainBackground2]
    for item in allBackgrounds:
        backPos = canvas.coords(item)
        if backPos[0] <= -canvasWidth:
            canvas.move(item, 2 * canvasWidth, 0)

    # To increase difficulty, every 400 iterations increase
    # obstacle speed and spawning probability
    if iterationCounter % 400 == 0:
        obstacleProbability += 1
        obstacleSpeed -= 1
        decreaseSpawnDistance -= 0.4

    # Check that at least N iterations have been executed
    # before spawning an obstacle
    lastGenerated = lastGenerated
    if iterationCounter - lastGenerated > 20 - decreaseSpawnDistance:
        r = rand(0, 100)
        if r < obstacleProbability:
            obstacleList = create_obstacle(obstacleList)
            lastGenerated = iterationCounter

    # Move all obstacles according to their speed
    move_obstacles(obstacleList)

    # Check collision between dino and each obstacle. If Yes, call game_over()
    if cheatCollision == -1:
        for obs in obstacleList:
            if check_collision(canvas.coords(dino), obs):
                print("GAME OVER")
                game_over()

    # Increment iteration counter (score) and update the score_label
    iterationCounter += 1
    canvas.itemconfig(score_label, text=str(iterationCounter))

    # Call itself again if the game is not paused
    if paused is False:
        window.after(fps, game_loop)


def main_menu():
    global mainMenuCanvas, startButton, loadGameButton, noSaveFileLabel
    global textErrorPlayerName, playerNameEntry, textErrorKeys

    mainMenuCanvas = Canvas(window, width=canvasWidth, height=canvasHeight)
    mainMenuCanvas.grid(column=0, row=0)
    mainMenuCanvas.config(bg="lightblue")
    mainMenuCanvas.create_image(0, 0, image=main_background_img, anchor="nw")
    textErrorKeys = ""  # So it's empty when user reopen define_keys

    # Create Buttons
    startButton = Button(window, text="New Game", command=start_game,
                         image=button_newGame_Img)
    loadGameButton = Button(window, text="Load Game", command=load_game,
                            image=button_load_img)
    defineCommandButton = Button(window, text="Define Commands",
                                 command=define_keys,
                                 image=button_keys_img)

    # Place Buttons and labels
    mainMenuCanvas.create_window(25, 25, anchor="nw", height=100, width=400,
                                 window=startButton)
    mainMenuCanvas.create_window(25, 150, anchor="nw", height=100, width=400,
                                 window=loadGameButton)
    mainMenuCanvas.create_window(25, 275, anchor="nw", height=100, width=400,
                                 window=defineCommandButton)
    noSaveFileLabel = mainMenuCanvas.create_text(650, 430, fill="green",
                                                 font=("Impact", 20), text="")

    insertNameLabel = mainMenuCanvas.create_text(200, 450,
                                                 text="Please enter your name",
                                                 font=("Impact", 27))

    # Create and place entry and related label
    playerNameEntry = Entry(window)
    mainMenuCanvas.create_window(180, 500, width=300, height=40,
                                 window=playerNameEntry)
    errorPlayerNameLabel = mainMenuCanvas.create_text(510, 500,
                                                      font=("Impact", 20),
                                                      fill="purple",
                                                      text=textErrorPlayerName)


def validate_custom_keys(jumpKeyEntry, pauseKeyEntry, invulKeyEntry,
                         infJuKeyEntry, bossKeyEntry):
    """This validates function keys such that they are only 1 character"""

    global invulnerabilityKey, infiniteJumpKey, pauseKey
    global saveKeysButton, jumpKey, bossKey
    global defineCommandCanvas, textErrorKeys, saveKeysButton
    entriesList = []
    done = False
    error = False
    if (len(jumpKeyEntry.get()) == 1 and
            jumpKeyEntry.get().isalnum() is True or
            jumpKeyEntry.get() == " "):
        entriesList.append(jumpKeyEntry.get())
        if (len(pauseKeyEntry.get()) == 1 and
                pauseKeyEntry.get().isalnum() is True or
                pauseKeyEntry.get() == " "):
            entriesList.append(pauseKeyEntry.get())
            if (len(invulKeyEntry.get()) == 1 and
                    invulKeyEntry.get().isalnum() is True or
                    invulKeyEntry.get() == " "):
                entriesList.append(invulKeyEntry.get())
                if (len(infJuKeyEntry.get()) == 1 and
                        infJuKeyEntry.get().isalnum() is True or
                        infJuKeyEntry.get() == " "):
                    entriesList.append(infJuKeyEntry.get())
                    if (len(bossKeyEntry.get()) == 1 and
                            bossKeyEntry.get().isalnum() is True or
                            bossKeyEntry.get() == " "):
                        entriesList.append(bossKeyEntry.get())
                        for i in range(len(entriesList)):
                            for j in range(i+1, len(entriesList)):
                                if entriesList[i] == entriesList[j]:
                                    textErrorKeys = "Error occurred!"
                                    error = True
                                    define_keys()
                        for name in entriesList:
                            if len(name) == 0:
                                error = True

                        if error is False:
                            jumpKey = jumpKeyEntry.get()
                            pauseKey = pauseKeyEntry.get()
                            invulnerabilityKey = invulKeyEntry.get()
                            infiniteJumpKey = infJuKeyEntry.get()
                            bossKey = bossKeyEntry.get()
                            textErrorKeys = "Saved!"
                            error = False
                            done = True
                            define_keys()
    if error is True or done is False:
        textErrorKeys = "Error occurred!"
    define_keys()


def define_keys():
    global defineCommandCanvas, defineCommandButton
    global invulnerabilityKey, infiniteJumpKey, pauseKey, saveKeysButton
    global jumpKey, bossKey, returnMainMenuButton, textErrorKeys

    defineCommandCanvas = Canvas(window, width=canvasWidth,
                                 height=canvasHeight)
    defineCommandCanvas.grid(column=0, row=0)
    defineCommandCanvas.config(bg="lightblue")
    defineCommandCanvas.create_image(0, 0, image=main_background_img,
                                     anchor="nw")

    # Create labels
    defineCommandCanvas.create_text(300, 65, fill="black",
                                    font=("Helvetica", 20),
                                    anchor="e",
                                    text="Jump Key (" + jumpKey + ") :")
    defineCommandCanvas.create_text(300, 95, fill="black",
                                    font=("Helvetica", 20),
                                    anchor="e",
                                    text="Pause Key (" + pauseKey + ") :")
    defineCommandCanvas.create_text(300, 125, fill="black",
                                    font=("Helvetica", 20),
                                    anchor="e",
                                    text="Invulnerability Key (" +
                                    invulnerabilityKey + ") :")
    defineCommandCanvas.create_text(300, 155, fill="black",
                                    font=("Helvetica", 20),
                                    anchor="e",
                                    text="Infinite Jump Key  (" +
                                    infiniteJumpKey + ") :")
    defineCommandCanvas.create_text(300, 185, fill="black",
                                    font=("Helvetica", 20),
                                    anchor="e",
                                    text="Boss Key (" + bossKey + ") :")

    # Create entries
    jumpKeyEntry = Entry(window)
    pauseKeyEntry = Entry(window)
    invulKeyEntry = Entry(window)
    infJuKeyEntry = Entry(window)
    bossKeyEntry = Entry(window)

    # Place entries
    defineCommandCanvas.create_window(380, 65, window=jumpKeyEntry)
    defineCommandCanvas.create_window(380, 95, window=pauseKeyEntry)
    defineCommandCanvas.create_window(380, 125, window=invulKeyEntry)
    defineCommandCanvas.create_window(380, 155, window=infJuKeyEntry)
    defineCommandCanvas.create_window(380, 185, window=bossKeyEntry)

    # Create and place labels and buttons
    tmp_font = ("Impact", 27)
    tmp_string = "Enter command in form of single character. "
    tmp_string2 = "They must be different!"
    instructionLabel = defineCommandCanvas.create_text(500, 20, fill="black",
                                                       font=tmp_font,
                                                       text=tmp_string +
                                                       tmp_string2)
    errorLabelDefine = defineCommandCanvas.create_text(700, 100, fill="purple",
                                                       font=tmp_font,
                                                       text=textErrorKeys)

    saveKeysButton = Button(window, text="Save Commands",
                            command=lambda: validate_custom_keys(jumpKeyEntry,
                                                                 pauseKeyEntry,
                                                                 invulKeyEntry,
                                                                 infJuKeyEntry,
                                                                 bossKeyEntry),
                            image=button_saveKeys_img)
    returnMainMenuButton = Button(window, text="Back to Main Menu",
                                  command=main_menu,
                                  image=button_mainMenu_img)
    defineCommandCanvas.create_window(34, 250, anchor="nw",
                                      height=100, width=400,
                                      window=saveKeysButton)
    defineCommandCanvas.create_window(34, 360, anchor="nw",
                                      height=100, width=400,
                                      window=returnMainMenuButton)

# !------------------------------PROGRAMME START----------------------------
window = Tk()
configure_window()

# Global Variables
mainMenuCanvas = None
playerNameEntry = None
textErrorPlayerName = ""
loadGameButton = None
noSaveFileLabel = None
startButton = None
canvas = None
dino = None
obstacleList = []
iterationCounter = 0
lastGenerated = 0
label_pause = None
score_label = None
best_score_label = None
paused = False
stopCanvas = None
resumeButton = None
gameOverCanvas = None
saveGameButton = None
restartGameButton = None
quitButton = None
scoreFile = None
saveFile = None
returnMainMenuButton = None
returnMainMenuButton2 = None
bossCanvas = None
playerName = None

# Define custom commands variables
defineCommandCanvas = None
defineCommandButton = None
saveKeysButton = None
jumpKey = " "
invulnerabilityKey = "y"
infiniteJumpKey = "q"
pauseKey = "p"
bossKey = "i"
errorLabelDefine = None
textErrorKeys = ""

# Cheats and bosskey tokens
cheatCollision = -1
cheatInfiniteJump = -1
bossKeyChecked = -1

# Images
main_background_img = PhotoImage(file="background.png")
mario_img = PhotoImage(file="mario.png")
mushroom_img = PhotoImage(file="mushroom.png")
rocket_img = PhotoImage(file="rocket.png")
button_resume_img = PhotoImage(file="buttonResumeGameImg.png")
button_load_img = PhotoImage(file="buttonLoadGameImg.png")
button_saveGame_img = PhotoImage(file="buttonSaveGameImg.png")
button_mainMenu_img = PhotoImage(file="buttonMainMenuImg.png")
button_newGame_Img = PhotoImage(file="buttonNewGameImg.png")
button_keys_img = PhotoImage(file="buttonKeysImg.png")
button_restartGame_img = PhotoImage(file="buttonRestartGameImg.png")
button_quit_img = PhotoImage(file="buttonQuitImg.png")
button_saveKeys_img = PhotoImage(file="buttonSaveKeysImg.png")
gameOverBackground_img = PhotoImage(file="game_over_background.png")
bossBackground_img = PhotoImage(file="boss_background.png")

mainBackground1 = None
mainBackground2 = None

dino_pic = None

# If score file does not exist, create it. Otherwise, do nothing
try:
    scoreFile = open(scoreFilename, "x+")
    scoreFile.close()
except:
    pass

# Show main menu
main_menu()

window.mainloop()
