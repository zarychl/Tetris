import random
import ustawienia as u
import pygame
import pygame_menu

pygame.init()

hitSound = pygame.mixer.Sound("sounds/hit.mp3")
rotateSound = pygame.mixer.Sound('sounds/block_rotate.mp3')
moveSound = pygame.mixer.Sound('sounds/move.mp3')
lineClearS = pygame.mixer.Sound('sounds/lineclear.mp3')

hitSound.set_volume(0.5)
rotateSound.set_volume(0.5)
moveSound.set_volume(0.5)
lineClearS.set_volume(0.5)


#Wszystkie możliwe kolory klocków w postaci RGB
koloryKlockow = [
    (227, 227, 227),
    (255, 156, 43),
    (214, 219, 68),
    (68, 138, 219),
    (219, 68, 151),
    (143, 68, 46),
    (71, 158, 65)
]
class Klocek:
    #[0][1][2][3]
    #[4][5][6][7]
    #[8][9][10][11]
    #[12][13][14][15]

    #klocki i ich obroty
    ksztalty = [
        [[4, 5, 6, 7], [1, 5, 9, 13]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 4, 5], [1, 5, 6, 10]],
        [[1, 2, 5, 6]]
    ]
    #pozycja
    x = 0
    y = 0

    #konstruktor
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.obrot = 0
        self.kolor = random.randint(1, len(koloryKlockow) - 1)
        self.ksztalt = random.randint(0, len(self.ksztalty) - 1)

    def obroc(self):
        self.obrot = (self.obrot + 1) % len(self.ksztalty[self.ksztalt])

    def getKlocek(self):
        return self.ksztalty[self.ksztalt][self.obrot]

class Gra:
    stanGry = 0 #0 - normalna rozgrywka; 1 - pauza; 2 - koniec gry
    wynik = 0 #wynik który zdobył gracz do tej pory
    poleGry = [] #informacja o wszystkich figurach na planszy
    figura = None #figura która obecnie "spada"
    figuraNext = None #następna figura (do wyświetlenia obok)
    hs = [] #tablica rekordów
    imie = "imie"
    czyRekord = False
    czyPauza = False

    def __init__(self):
        for x in range(u.POLE_H):
            poleWiersz = [] #tworzymy nowy wiersz pola gry...
            for y in range(u.POLE_W):
                poleWiersz.append(0)#...i wypełniamy go zerami (czyli brak klocków)
            self.poleGry.append(poleWiersz)#dodajemy go do pola gry
        self.wczytajRekordy()

    def zmienImie(self, imieNew):
        self.imie = imieNew

    def nowyKlocek(self):
        if (self.figura == None):
            self.figura = Klocek(3, 0)
        else:
            self.figura = self.figuraNext
        self.figuraNext = Klocek(3, 0)

    def usunPelnyWiersz(self):
        pelneWiersze = 0
        for x in range(u.POLE_H):
            pusteKomorki = 0
            for y in range(u.POLE_W):
                if(self.poleGry[x][y] == 0): # Sprawdzamy czy w danej lini znajdują się puste komórki
                    pusteKomorki = 1 # jeśli tak to pomijamy ten wiersz
            if(pusteKomorki != 1): # a jeśli cały wiersz jest wypełniony
                pelneWiersze = pelneWiersze + 1#to zliczamy ich ilosc
                for xa in range(x, 1, -1): #a pozostałe klocki przesuwany z góry na dół
                    for y in range(u.POLE_W):
                        self.poleGry[xa][y] = self.poleGry[xa - 1][y]
        self.wynik += pow(pelneWiersze, 2)
        if(pelneWiersze > 0):
            playSound(3)

    def wczytajRekordy(self):
        f = open("hs.txt", "r").read().split('\n')
        i=0
        for line in f:
            rekord = line.split(";")
            rekord[1] = int(rekord[1])
            self.hs.append(rekord)
            i=i+1

    def zapiszRekordy(self):
        f = open("hs.txt", "w")
        for i in range(len(self.hs)):
            if(i==4):
                f.write(self.hs[i][0]+';'+str(self.hs[i][1]))
            else:
                f.write(self.hs[i][0]+';'+str(self.hs[i][1])+'\n')

    def getRekord(self):
        return self.hs[0][1]

    def checkHS(self):
        for i in range(len(self.hs)):
            if(self.hs[i][1] < self.wynik):
                self.hs.insert(i,[self.imie,self.wynik])
                self.hs.pop(len(self.hs)-1)
                self.zapiszRekordy()
                return 1

    def zatrzymaj(self):
        for x in range(4):
            for y in range(4):
                if(x * 4 + y in self.figura.getKlocek()):
                    self.poleGry[x + self.figura.y][y + self.figura.x] = self.figura.kolor
        self.usunPelnyWiersz()
        self.nowyKlocek()
        if self.czyKolizja():
            self.stanGry = 2
            self.checkHS()

    def czyKolizja(self):
        kolizja = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figura.getKlocek():
                    if i + self.figura.y > u.POLE_H - 1 or \
                            j + self.figura.x > u.POLE_W - 1 or \
                            j + self.figura.x < 0 or \
                            self.poleGry[i + self.figura.y][j + self.figura.x] > 0:
                        kolizja = True
        return kolizja

    def ruchBok(self, d):
        if self.czyPauza is True:
            return
        xOld = self.figura.x
        self.figura.x = self.figura.x + d;
        if(self.czyKolizja()):
            self.figura.x = xOld;
        else:
            playSound(2)

    def obroc(self):
        if self.czyPauza is True:
            return
        rOld = self.figura.obrot
        self.figura.obroc()
        if(self.czyKolizja()):
            self.figura.obrot = rOld

    def spadek(self):
        self.figura.y = self.figura.y + 1
        if(self.czyKolizja() == True):
            self.figura.y = self.figura.y -1
            playSound(1)
            self.zatrzymaj()
    def togglePause(self):
        if(self.czyPauza is True):
            self.czyPauza = False
        else:
            self.czyPauza = True

def rozpocznij():
    czasGry = pygame.time.Clock()
    ticks = 0
    szybko = False
    czyPauza = 0

    while 1:
        if tetris.figura is None:
            tetris.nowyKlocek()
        ticks += 1
        if ticks > 100000:
            ticks = 0

        if ticks % (100 // u.SZYBKOSC_GRY ) == 0 or szybko:
            if tetris.stanGry == 0 and tetris.czyPauza is False:
                tetris.spadek()

        #obsługa sterowania
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                zakoncz()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    tetris.obroc()
                    playSound(0)
                if event.key == pygame.K_DOWN:
                    szybko = True
                if event.key == pygame.K_LEFT:
                    tetris.ruchBok(-1)
                if event.key == pygame.K_RIGHT:
                    tetris.ruchBok(1)
                if event.key == pygame.K_p:
                        tetris.togglePause()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    szybko = False

        screen.fill(u.CZARNY)

        for i in range(u.POLE_H):
            for j in range(u.POLE_W):
                pygame.draw.rect(screen, u.SZARY, [u.START_X + u.ZOOM_OKNA * j, u.START_Y + u.ZOOM_OKNA * i, u.ZOOM_OKNA, u.ZOOM_OKNA],
                                 1)
                if tetris.poleGry[i][j] > 0:
                    pygame.draw.rect(screen, koloryKlockow[tetris.poleGry[i][j]],
                                     [u.START_X + u.ZOOM_OKNA * j + 1, u.START_Y + u.ZOOM_OKNA * i + 1, u.ZOOM_OKNA - 2,
                                      u.ZOOM_OKNA - 1])

        if tetris.figura is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.figura.getKlocek():
                        pygame.draw.rect(screen, koloryKlockow[tetris.figura.kolor],
                                         [u.START_X + u.ZOOM_OKNA * (j + tetris.figura.x) + 1,
                                          u.START_Y + u.ZOOM_OKNA * (i + tetris.figura.y) + 1,
                                          u.ZOOM_OKNA - 2, u.ZOOM_OKNA - 2])

        if tetris.figuraNext is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in tetris.figuraNext.getKlocek():
                        pygame.draw.rect(screen, koloryKlockow[tetris.figuraNext.kolor],
                                         [210 + u.ZOOM_OKNA * (j + tetris.figuraNext.x) + 1,
                                          80 + u.ZOOM_OKNA * (i + tetris.figuraNext.y) + 1,
                                          u.ZOOM_OKNA - 2, u.ZOOM_OKNA - 2])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        textWynik = font.render("Wynik: " + str(tetris.wynik), True, u.BIALY)
        textRekord = font.render(" | Rekord: " + str(tetris.getRekord()), True, u.BIALY)
        textNextKlocek = font.render("Następny:", True, u.SZARY)
        textKoniec = font1.render("Koniec gry :( ", True, (255, 0, 0))
        textPauza = font1.render("||", True, (255, 0, 0))

        screen.blit(textWynik, [20, 470])
        screen.blit(textRekord, [160, 470])
        screen.blit(textNextKlocek, [260, 20])
        if tetris.stanGry == 2:
            screen.blit(textKoniec, [30, 200])
        #if tetris.czyPauza is True:
            #screen.blit(textPauza, [140,200])

        pygame.display.flip()
        czasGry.tick(u.SZYBKOSC_GRY)

    pygame.quit()

def zakoncz():
    pygame.quit()

def playSound(numer):
    if numer == 0:
        rotateSound.play()
    if numer == 1:
        hitSound.play()
    if numer == 2:
        moveSound.play()
    if numer == 3:
        lineClearS.play()



def dispMenu():
    while 1:
        menu = pygame_menu.Menu('Tetris',300, 400, theme=pygame_menu.themes.THEME_GREEN)
        menu.add.text_input('Imię:', default='', onchange=tetris.zmienImie)
        menu.add.button('Graj', rozpocznij)
        menu.add.button('Najlepsze wyniki', wyniki)
        menu.add.button('Wyjście', pygame_menu.events.EXIT)
        menu.mainloop(screen)

def wyniki():
    while 1:
        wynikiMenu = pygame_menu.Menu('Wyniki', 300, 400, theme=pygame_menu.themes.THEME_GREEN)
        for i in range(5):
            wynikiMenu.add.label(str(i+1)+". " + tetris.hs[i][0] + ", " + str(tetris.hs[i][1]) + " p.")
        wynikiMenu.add.button("Powrót", dispMenu)
        wynikiMenu.mainloop(screen)

rozmiarOkna = (400, 500)
screen = pygame.display.set_mode(rozmiarOkna)
pygame.display.set_caption("Tetris")
tetris = Gra()
dispMenu()