import pygame,sys
from random import randint

#variables constantes
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
Ancho,Largo = 750,750
ventana = pygame.display.set_mode((Ancho,Largo))
pygame.display.set_caption("Space Shooter")
reloj = pygame.time.Clock()
fps = 60
fuente = pygame.font.Font("freesansbold.ttf",45)
blanco = (255,255,255)

#sonidos
ataque_enemigo = pygame.mixer.Sound("Ataque_enemigo.wav")
ataque_jugador = pygame.mixer.Sound("Ataque_jugador.wav")
explosion = pygame.mixer.Sound("explosion.wav")
salud_sound = pygame.mixer.Sound("salud.wav")
vida_menos = pygame.mixer.Sound("warning.wav")
level_up = pygame.mixer.Sound("level-up-sound-effect.wav")
bg_music = pygame.mixer.music.load("x_com.wav")

#Imagenes:

#salud
salud_img = pygame.transform.scale(pygame.image.load("salud.png"),(50,50))

#naves
Nave_Roja = pygame.image.load("pixel_ship_red_small.png")
Nave_Azul = pygame.image.load("pixel_ship_blue_small.png")
Nave_Verde = pygame.image.load("pixel_ship_green_small.png")
Nave_Jugador = pygame.image.load("pixel_ship_yellow.png")

lista_naves = [Nave_Roja,Nave_Azul,Nave_Verde]

#lazers
laser_rojo = pygame.image.load("pixel_laser_red.png")
laser_azul = pygame.image.load("pixel_laser_blue.png")
laser_verde = pygame.image.load("pixel_laser_green.png")
laser_jugador = pygame.image.load("pixel_laser_yellow.png")

lista_lasers = [laser_rojo,laser_azul,laser_verde]

bg = pygame.transform.scale(pygame.image.load("background-black.png"),(Ancho,Largo))

class Nave:
	ValorCooldown = 10

	def __init__(self,x,y,salud = 180):
		self.x = x
		self.y = y
		self.salud = salud
		self.img = None
		self.laser_img = None
		self.lasers = []
		self.cooldownAtaque = 0
		self.vel_laser = 0

	def dibujar(self,ventana):
		ventana.blit(self.img,(self.x,self.y))
		for laser in self.lasers:
			laser.dibujar(ventana)

	def getAncho(self):
		return self.img.get_width()

	def getLargo(self):
		return self.img.get_height()

	def disparar(self):
		if self.cooldownAtaque == 0:
			laser = Laser(self.x,self.y,self.laser_img,self.vel_laser)
			self.lasers.append(laser)
			self.cooldownAtaque = 1

	def cooldown(self):
		if self.cooldownAtaque >= self.ValorCooldown:
			self.cooldownAtaque = 0
		elif self.cooldownAtaque > 0:
			self.cooldownAtaque += 1

	def mover_lasers(self,obj):
		self.cooldown()
		for laser in self.lasers:
			laser.mover()
			if laser.offScreen(Largo):
				self.lasers.remove(laser)
			elif laser.colisionar(obj):
				obj.salud -= 20
				self.lasers.remove(laser)

class Jugador(Nave):
	def __init__(self,x,y,salud = 180):
		super().__init__(x,y,salud)
		self.img = Nave_Jugador
		self.laser_img = laser_jugador
		self.mask = pygame.mask.from_surface(self.img)
		self.vel_laser = -25
		self.salud_max = salud
		self.score = 0

	def mover_lasers(self,objs):
		self.cooldown()
		for laser in self.lasers:
			laser.mover()
			if laser.offScreen(Largo):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.colisionar(obj):
						objs.remove(obj)
						self.score += 25
						pygame.mixer.Sound.play(explosion)
						if laser in self.lasers:
							self.lasers.remove(laser)
	
	def dibujar(self,ventana):
		super().dibujar(ventana)
		self.barraSalud(ventana)
	
	def barraSalud(self,ventana):
		pygame.draw.rect(ventana,(255,0,0),(self.x,self.y + self.img.get_height() + 10,self.img.get_width(),10))
		pygame.draw.rect(ventana,(0,255,0),(self.x,self.y + self.img.get_height() + 10,self.img.get_width() * (self.salud/self.salud_max),10))

	def vidaPerdida(self):
		return self.salud_max - self.salud

class Enemigo(Nave):
	def __init__(self,x,y,salud = 100):
		super().__init__(x,y,salud)
		self.vel = 3
		self.tipo = randint(0,2)
		self.img = lista_naves[self.tipo]
		self.laser_img = lista_lasers[self.tipo]
		self.mask = pygame.mask.from_surface(self.img)
		self.vel_laser = 25

	def movimiento(self):
		self.y += self.vel

	def disparar(self):
		if self.cooldownAtaque == 0:
			if self.tipo == 1:
				laser = Laser(self.x - 25,self.y,self.laser_img,self.vel_laser)
			else:
				laser = Laser(self.x - 15,self.y,self.laser_img,self.vel_laser)
			self.lasers.append(laser)
			self.cooldownAtaque = 1

	def offScreen(self,Largo):
		 return not(self.y <= Largo and self.y >= 0)

class Laser:
	def __init__(self,x,y,img,vel):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)
		self.vel = vel

	def dibujar(self,ventana):
		ventana.blit(self.img,(self.x,self.y))
	
	def mover(self):
		self.y += self.vel

	def colisionar(self,obj):
		return colision(self,obj)

	def offScreen(self,Largo):
		 return not(self.y <= Largo and self.y >= 0)

class KitReparar:
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.img = salud_img
		self.mask = pygame.mask.from_surface(self.img)

	def dibujarKit(self,ventana,Ancho,Largo):
		ventana.blit(self.img,(self.x,self.y))

	def recogerKit(self,obj):
		return colision(self,obj)

	def repararJugador(self,obj,Vidas):
		self.reparar = obj.salud_max/2
		if self.recogerKit(obj):
			if Vidas < 5:
				Vidas += 1
			pygame.mixer.Sound.play(salud_sound)
			if obj.salud + self.reparar <= obj.salud_max:
				obj.salud += self.reparar
			else:
				obj.salud = obj.salud_max
			return False,Vidas
		return True,Vidas


def colision(obj1,obj2):
	vector_y = obj2.y - obj1.y
	vector_x = obj2.x - obj1.x
	return obj1.mask.overlap(obj2.mask,(vector_x,vector_y)) != None


def main():
	juego = True
	nivel = 0
	vidas = 5
	jugador_vel = 15
	derrota = False
	tiempo_actual = 0
	jugador = Jugador(600,500)
	regenerar = 20
	pick_salud = False
	x_salud,y_salud = 0,0
	timer_salud = 0
	tiempoActualSalud = 0
	
	enemigos = []
	oleada = 0
	
	def dibujarPantalla():
		mantenerKit = False
		lives = vidas
		ventana.blit(bg,(0,0))
		if pick_salud:
			kit = KitReparar(x_salud,y_salud)
			kit.dibujarKit(ventana,Ancho,Largo)
			mantenerKit,lives = kit.repararJugador(jugador,vidas)
		jugador.dibujar(ventana)

		for enemigo in enemigos:
			enemigo.dibujar(ventana)

		jugador.mover_lasers(enemigos)
		
		txt = fuente.render("Vidas: " + str(vidas),True,blanco)
		ventana.blit(txt,(20,25))

		txt = fuente.render("Nivel: " + str(nivel),True,blanco)
		ventana.blit(txt,(Ancho - txt.get_width() - 20,25))

		if derrota:
			fuente_derrota = pygame.font.Font("freesansbold.ttf", 60)
			txt = fuente_derrota.render("Perdiste:(",True,blanco)
			ventana.blit(txt,(Ancho/2 - txt.get_width()/2,Largo/2 - txt.get_height()/2))

		pygame.display.update()
		return mantenerKit,lives

	while juego:
		reloj.tick(fps)

		if jugador.salud <= 0:
			pygame.mixer.Sound.play(explosion)

		if vidas <= 0 or jugador.salud <= 0:
			derrota = True
			timer_derrota = pygame.time.get_ticks()

		if not pick_salud and randint(0,1000*fps//((nivel+1)**2 + 8*(jugador.salud_max - jugador.salud))) == 0:
			pick_salud= True
			x_salud,y_salud = randint(150,Ancho - 100),randint(100,Largo - 50)
			timer_salud = pygame.time.get_ticks()

		if pick_salud:
			tiempoActualSalud = pygame.time.get_ticks()
			if tiempoActualSalud - timer_salud >= 7000:
				pick_salud = False
		
		pick_salud,vidas = dibujarPantalla()

		while derrota:
			tiempo_actual = pygame.time.get_ticks()
			for evento in pygame.event.get():
				if evento.type == pygame.QUIT:
					juego = False
					pygame.quit()
					sys.exit()
			if tiempo_actual - timer_derrota >= 3000:
				jugador.score = (jugador.score * nivel + 75 * vidas)//2
				return jugador.score,nivel
			else:
				continue

		if len(enemigos) == 0:
			nivel += 1
			oleada = 3*nivel
			if nivel != 1:
				pygame.mixer.Sound.play(level_up)

			jugador.salud_max += regenerar
			
			if jugador.salud + regenerar < jugador.salud_max:
				jugador.salud += regenerar
			else:
				jugador.salud = jugador.salud_max

			for i in range(oleada):
				enemigo = Enemigo(randint(50,Ancho - 100),randint(-1500,-100))
				enemigos.append(enemigo)

		for evento in pygame.event.get():
			if evento.type == pygame.QUIT:
				juego = False
				pygame.quit()
				sys.exit()
		
		dicc = pygame.key.get_pressed()
		if dicc[pygame.K_UP] and jugador.y - jugador_vel > 0:    #arriba
			jugador.y -= jugador_vel
		if dicc[pygame.K_DOWN] and jugador.y + jugador_vel + jugador.getLargo() + 15 < Largo:   #abajo
			jugador.y += jugador_vel
		if dicc[pygame.K_LEFT] and jugador.x - jugador_vel > 0:    #izquierda
			jugador.x -= jugador_vel
		if dicc[pygame.K_RIGHT] and jugador.x + jugador.getAncho() + jugador_vel < Ancho:  #derecha
			jugador.x += jugador_vel
		if dicc[pygame.K_SPACE]:
			if jugador.cooldownAtaque == 0:
				pygame.mixer.Sound.play(ataque_jugador)
			jugador.disparar()

		for enemigo in enemigos[:]:
			enemigo.movimiento()
			enemigo.mover_lasers(jugador)
			
			if not enemigo.offScreen(Largo):
				if randint(0,3/2*fps) == 60:
					enemigo.disparar()
					pygame.mixer.Sound.play(ataque_enemigo)
			
				if colision(enemigo,jugador):
					pygame.mixer.Sound.play(explosion)
					if jugador.salud - 50 >= 0:
						jugador.salud -= 50
					else:
						jugador.salud = 0
					enemigos.remove(enemigo)
					jugador.score += 50
				
				elif enemigo.y + enemigo.getLargo() >= Largo:
					vidas -= 1
					enemigos.remove(enemigo)
					pygame.mixer.Sound.play(vida_menos)

def menu():
	score = 'no hay score'
	nivel = 'no hay nivel'
	pygame.mixer.music.play(-1)
	fuente_menu = pygame.font.Font("freesansbold.ttf", 50)
	fuente_menu2 = pygame.font.Font("freesansbold.ttf", 20)
	while True:
		ventana.blit(bg,(0,0))

		if score != 'no hay score' and nivel != 'no hay nivel':
			msj = fuente_menu.render("Puntaje: " + str(score),True,blanco)
			ventana.blit(msj,(20,20))

			msj = fuente_menu.render("Nivel: " + str(nivel), True,blanco)
			ventana.blit(msj,(20,100))

		msj1 = fuente_menu.render("Haz click para continuar",True,blanco)
		ventana.blit(msj1,(Ancho/2 - msj1.get_width()/2,Largo/2 - msj1.get_height()/2))
		
		msj2 = fuente_menu2.render("Tu objetivo es defender la Tierra de los invasores",True,blanco)
		ventana.blit(msj2,(Ancho/2 - msj2.get_width()/2,Largo/2 - msj2.get_height()/2 + 150))
		
		msj3 = fuente_menu2.render("Destruye tantas naves como puedas, y no las dejes pasar!",True,blanco)
		ventana.blit(msj3,(Ancho/2 - msj3.get_width()/2,Largo/2 - msj3.get_height()/2 + 200))
		
		pygame.display.update()
		
		for evento in pygame.event.get():
			if evento.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if evento.type == pygame.MOUSEBUTTONDOWN:
				score,nivel = main()
menu()