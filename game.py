from os import path
from random import randint
from time import time

import pygame

from tile import Tile

FOND = pygame.Color(150, 150, 150)

# Merci Microsoft
couleurs_chiffres = {
		1: pygame.Color(0, 0, 255),
		2: pygame.Color(0, 128, 0),
		3: pygame.Color(255, 0, 0),
		4: pygame.Color(0, 0, 128),
		5: pygame.Color(128, 0, 0),
		6: pygame.Color(0, 128, 128),
		7: pygame.Color(0, 0, 0),
		8: pygame.Color(128, 128, 128)
}


class Game:
	def __init__(self, horiz_tiles: int, vert_tiles: int, num_bombs: int = 50):
		assert horiz_tiles > 0
		assert vert_tiles > 0
		pygame.init()
		self.hidden_bombs = 0
		self.num_bombs = num_bombs
		self.flagged = 0
		self.horiz_tiles = horiz_tiles
		self.vert_tiles = vert_tiles
		self.tilesize = 25
		self.width = self.horiz_tiles * self.tilesize
		self.height = self.vert_tiles * self.tilesize
		self.num_tiles = horiz_tiles * vert_tiles

		self.Font = pygame.font.SysFont("segoe-ui-symbol.ttf", int(self.tilesize * .6))
		# TODO : meilleures images...
		self.flag_image = pygame.transform.smoothscale(
				pygame.image.load(path.join("resources", "drapeau.png")),
				(self.tilesize, self.tilesize))
		self.tile_image = pygame.transform.smoothscale(
				pygame.image.load(path.join("resources", "case.png")),
				(self.tilesize, self.tilesize))
		self.bomb_image = pygame.transform.smoothscale(
				pygame.image.load(path.join("resources", "bombe.png")),
				(self.tilesize, self.tilesize))

		self.running = True
		self.lost = False
		self.tiles: list[Tile] = []

		# Les cases sont vides pour l'instant
		# On ne peut pas les initialiser avant le premier clic du joueur 
		for x in range(self.horiz_tiles):
			for y in range(self.vert_tiles):
				self.tiles.append(Tile(x, y))
		self.generated = False

		self.surface = pygame.Surface((self.width, self.height))
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.mouse.set_cursor(pygame.cursors.arrow)

	def run(self) -> None:
		debut = time()
		temps = 0.
		# Boucle principale
		while self.running:
			# On s'occupe du titre de la fenètre
			if self.lost:
				# TODO : mécanisme pour recommencer une nouvelle partie
				pygame.display.set_caption(
						f"Perdu, il restait {str(self.hidden_bombs)} bombes, temps de jeu : {temps}s")
			else:
				pygame.display.set_caption(
						f"Il reste {str(self.num_bombs - self.flagged)} bombes, temps de jeu : {int(time() - debut)}s")

			# TODO : mécanisme pour recommencer une nouvelle partie
			# Si on a gagné
			if self.generated and self.hidden_bombs == 0:
				self.win(debut)

			# On traite les événements qui nous intéressent
			for event in pygame.event.get():
				# Quitter le jeu
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					self.running = False

				# Technique secrète pour aller vite
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL) and not self.lost:
						for tile in self.tiles:
							if tile.is_bomb:
								tile.revealed = True

				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_s and not self.lost:
						for tile in self.tiles:
							if tile.is_bomb:
								tile.revealed = False

				# Clic de souris
				if event.type == pygame.MOUSEBUTTONDOWN and not self.lost:
					x, y = event.pos[0] // self.tilesize, event.pos[1] // self.tilesize
					clicked_tile = self.tiles[x * self.vert_tiles + y]

					# Clic gauche, on veut révéler une ou des cases
					if event.button == pygame.BUTTON_LEFT:
						# On ne peut pas révéler une case drapeau
						if clicked_tile.flagged: continue
						if not self.generated:
							self.generate(x, y)

						# Si la case est déjà révélée et a autant de drapeaux autour d'elle que de bombes,
						# on peut cliquer dessus pour révéler toutes les cases adjacentes qui n'ont pas de drapeau
						# (si un drapeau a été mal placé, on perd la partie)
						if clicked_tile.revealed:
							num_flagged = sum(neighbour.flagged for neighbour in clicked_tile.neighbours)
							if num_flagged == clicked_tile.bomb_neighbours_count:
								for neighbour in clicked_tile.neighbours:
									if not neighbour.flagged and not neighbour.revealed:
										neighbour.floodfill()
										if neighbour.is_bomb:
											temps = self.lose(debut)

						# On a cliqué sur une bombe cachée
						if clicked_tile.is_bomb:
							temps = self.lose(debut)

						# Sinon on révèle simplement la case cliquée
						else:
							clicked_tile.floodfill()

					# Clic droit, on marque une case d'un drapeau
					elif event.button == pygame.BUTTON_RIGHT and not clicked_tile.revealed:
						# Si la case était déjà marquée, on rajoute la bombe cachée qui avait été enlevée du compte
						if clicked_tile.flagged:
							if clicked_tile.is_bomb:
								self.hidden_bombs += 1
							self.flagged -= 1

						# Sinon, si c'est une bombe on l'enlève du compte des bombes cachées
						else:
							if clicked_tile.is_bomb:
								self.hidden_bombs -= 1
							self.flagged += 1

						clicked_tile.flagged = not clicked_tile.flagged
				
			# Affichage
			self.display()

	def display(self) -> None:
		for tile in self.tiles:
			if tile.revealed:
				if tile.is_bomb:
					# On dessine l'image self.bomb_image sur self.surface aux coordonnées précisées.
					self.surface.blit(self.bomb_image,
										 (tile.x * self.tilesize, tile.y * self.tilesize))
				else:
					# On affiche le fond et l'éventuel nombre de bombes voisines
					pygame.draw.rect(self.surface, FOND,
									 pygame.Rect(tile.x * self.tilesize, tile.y * self.tilesize,
												 self.tilesize, self.tilesize))
					if tile.bomb_neighbours_count > 0:
						# Si on a des voisins bombes, on utilise self.Font.render pour créer une image qui contient 
						# le nombre de voisins bombes, de la bonne couleur.
						text = self.Font.render(str(tile.bomb_neighbours_count), True,
												couleurs_chiffres[tile.bomb_neighbours_count])
						text_rect = text.get_rect()
						# On centre le texte sur la case
						text_rect.center = (tile.x * self.tilesize + self.tilesize // 2,
											tile.y * self.tilesize + self.tilesize // 2)
						self.surface.blit(text, text_rect)
			
			if tile.flagged:
				if not tile.revealed:
					self.surface.blit(self.tile_image,
										 (tile.x * self.tilesize, tile.y * self.tilesize))
				self.surface.blit(self.flag_image,
									 (tile.x * self.tilesize, tile.y * self.tilesize))
			# On affiche juste le fond
			if not (tile.flagged or tile.revealed):
				self.surface.blit(self.tile_image,
									 (tile.x * self.tilesize, tile.y * self.tilesize))

		# On affiche la surface de dessin sur l'écran
		self.screen.blit(self.surface, self.surface.get_rect())
		# Et on met à jour l'affichage avec le nouveau contenu de l'écran
		pygame.display.update()

	def win(self, debut):
		self.running = False
		temps = time() - debut
		print(f"Bravo, réussi en {int(temps)}s")

	def lose(self, debut: float) -> int:
		"""
		Affiche toutes les bombes et termine la partie, et renvoit le temps de jeu.

		:param debut: Le temps de début
		:return: Le temps total de jeu
		"""
		for tile in self.tiles:
			if tile.is_bomb:
				tile.revealed = True
		self.lost = True
		return int(time() - debut)

	def voisins(self, x: int, y: int) -> list[int]:
		"""
		La liste des voisins d'une case sélectionnée. Les voisins sont exprimés en termes d'indices dans le tableau des cases.

		:param x: La coordonnée horizontale.
		:param y: La coordonnée verticale.
		:return: La liste des voisins.
		"""
		v = []
		for i in range(- 1, 2):
			for j in range(- 1, 2):
				# On ne compte pas une case dans ses voisins
				if i == j == 0: continue
				if 0 <= x + i < self.horiz_tiles and 0 <= y + j < self.vert_tiles:
					v.append((x + i) * self.vert_tiles + y + j)
		return v

	def generate(self, x: int, y: int) -> None:
		"""
		Génère la liste des bombes et initialise chaque case avec ses voisins.

		:param x: La coordonnée horizontale.
		:param y: La coordonnée verticale.
		"""
		selected_tile_number = x * self.vert_tiles + y
		voisins = self.voisins(x, y)

		# On ajoute toutes les bombes
		while self.hidden_bombs < self.num_bombs:
			i = randint(0, self.num_tiles - 1)

			# On veut que la première case cliquée n'ait aucune bombe parmis ses voisins
			while self.tiles[i].is_bomb or i == selected_tile_number or i in voisins:
				i = randint(0, self.num_tiles - 1)
			self.tiles[i].is_bomb = True
			self.hidden_bombs += 1

		# On calcule la liste des voisins de chaque case
		for i, tile in enumerate(self.tiles):
			if i - self.vert_tiles >= 0:
				tile.neighbours.append(self.tiles[i - self.vert_tiles])
				if i % self.vert_tiles > 0:
					tile.neighbours.append(self.tiles[i - self.vert_tiles - 1])
				if i % self.vert_tiles < self.vert_tiles - 1:
					tile.neighbours.append(self.tiles[i - self.vert_tiles + 1])

			if i + self.vert_tiles < self.num_tiles:
				tile.neighbours.append(self.tiles[i + self.vert_tiles])
				if i % self.vert_tiles < self.vert_tiles - 1:
					tile.neighbours.append(self.tiles[i + self.vert_tiles + 1])
				if i % self.vert_tiles > 0:
					tile.neighbours.append(self.tiles[i + self.vert_tiles - 1])

			if i % self.vert_tiles > 0:
				tile.neighbours.append(self.tiles[i - 1])

			if i % self.vert_tiles < self.vert_tiles - 1:
				tile.neighbours.append(self.tiles[i + 1])

		for tile in self.tiles:
			tile.count_neighbour_bombs()

		self.generated = True
