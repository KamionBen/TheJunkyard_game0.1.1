import pygame
from pygame.locals import *
from constants import *
from pathfinder import *
from Member import *
from CombatEntity import *
from Mob import *
from Weapon import *
from TileClasses import *
import os
import sys

if getattr(sys, 'frozen', False):
    path = sys._MEIPASS
else:
    path = os.path.dirname(os.path.abspath(__file__))

VERSION = '0.1.0'
TITLE = "The Junkyard - Tutorial - Version %s" % VERSION

WIDTH, HEIGHT = 1280, 720

# Chargement des ressources
gravel = os.path.join(path, 'img/gravel.png')
crate = os.path.join(path, 'img/crate.png')
soldier_sprite_30 = os.path.join(path, 'img/soldier_sprite_30.png')
overlay = os.path.join(path, 'img/overlay.png')
tile_hl = os.path.join(path, 'img/tile_hl.png')
dead = os.path.join(path, 'img/dead.png')
PressStart2P = os.path.join(path, 'fonts/PressStart2P.ttf')
map = os.path.join(path, 'maps/tutorial')
bullet = os.path.join(path, 'img/bullet.png')
help_file = os.path.join(path, 'img/help.png')


class CombatLog:
    id = 0

    def __init__(self):
        """ Gère le journal de combat """
        self._id = []
        self._type = []  # Peut être Combat, Système, Social, etc ...
        self._message = []  # Le message en lui-même

    def append(self, type, message):
        """ Ajout d'un message """
        self._id.append(CombatLog.id)
        CombatLog.id += 1
        self._type.append(type)
        self._message.append(message)

    def __iter__(self):
        """ Méthode d'itération """
        return iter(self._id)

    def __getitem__(self, id):
        """ Méthode de récupération """
        if id in self._id:
            return "[%s] %s" % (self._type[self._id.index(id)], self._message[self._id.index(id)])
        else:
            raise IndexError("Le journal ne contient aucune entré à l'indice %s" % id)

    def __len__(self):
        """ Renvoie la taille du log """
        return len(self._id)


class Tutorial:
    def __init__(self, level):
        """ Classe principale, affiche la map et le menu, gère l'IA"""
        # Map infos
        self.map = TileGroup()
        self.walls = TileGroup()
        self.covers = TileGroup()
        self.map_name = 'Default'
        self.map_width, self.map_height = 0, 0

        # Groupes de combat
        self.members = CombatEntityGroup()
        self.mobs = CombatEntityGroup()

        # Images
        self.gravel = pygame.image.load(gravel).convert()
        self.crate = pygame.image.load(crate).convert()
        self.spriteset = pygame.image.load(soldier_sprite_30).convert_alpha()
        self.hl_img = pygame.image.load(overlay).convert_alpha()
        self.tile_hl = pygame.image.load(tile_hl).convert_alpha()
        self.dead = pygame.image.load(dead).convert_alpha()
        self.help_img = pygame.image.load(help_file).convert_alpha()
        # Variables
        self.hl = False
        self.frame_list = {}
        self.pause = True
        self.help = True

        # Log
        self.log = CombatLog()

        # Générations
        self.generate(level)
        self.generate_sold_mobs()

        # Variables IA
        self.ia_are_activated = True

    """ Gestion de évènements"""
    def left_click(self, pos):
        """ Ce qu'il se passe en cas de clic gauche """
        self.members.unselect_all()

        # Recherche des hitbox
        for member in self.members:
            if member.hitbox.collidepoint(pos):
                self.members.select(member)

        # Recherche dans le menu
        for key, rect in self.frame_list.items():
            if rect.collidepoint(pos):
                self.members.select(key)

    def right_click(self, pos):
        """ Ce qu'il se passe en cas de clic droit """
        # On cherche un soldat selectionné
        for member in self.members:
            if member.selected:
                # On vérifie si on a cliqué sur un ennemi
                for mob in self.mobs:
                    if mob.hitbox.collidepoint(pos):
                        member.set_target(mob)

                    else:
                        # C'est un clic droit de déplacement
                        locked = TileGroup()

                        # On cherche les positions des alliés et des ennemis

                        for ally in self.members:
                            locked.append(ally.tile.copy())
                        for mob in self.mobs:
                            locked.append(mob.tile.copy())

                        new_tile = Tile([int(pos[0] / 32), int(pos[1] / 32)])
                        if new_tile not in locked and new_tile not in self.walls:
                            member.path = pathfinder(self.walls, [self.map_width, self.map_height], member.tile, new_tile)
                            member.destination = new_tile

    def spacebar(self):
        """ Ce qu'il se passe quand on appuye sur espace """
        if self.pause:
            self.pause = False
        else:
            self.pause = True

        self.help = False

    def shortcut(self, key):
        """ Les raccourcis claviers """
        # TODO : Ne marchera sûrement pas sur d'autres plateforme
        if key == K_AMPERSAND:
            self.members.select(0)
        if key == 160:
            self.members.select(1)
        if key == 34:
            self.members.select(2)

    def t_help(self):
        """ Affichage de l'aide """
        if self.help:
            self.help = False
        else:
            self.pause = True
            self.help = True

    """ Affichage principal"""
    def display(self, window):
        """ On affiche tout à l'écran"""
        """ Affichage de la carte """
        # Tuiles
        for tile in self.map:
            if tile in self.walls:
                # On affiche le mur
                window.blit(self.crate, (tile.abs_pos('x'), tile.abs_pos('y') - 12))
            else:
                # On affiche du gravier
                window.blit(self.gravel, tile.abs_pos())
            if self.hl:
                # Si l'overlay est activé
                window.blit(self.hl_img, tile.abs_pos())

        # Destination : Si le soldat bouge, on indique sa destination
        for member in self.members:
            if member.tile != member.destination:
                window.blit(self.tile_hl, member.destination.abs_pos())

        # Alliés
        for member in self.members:
            if self.hl:
                # Si l'overlay est activé, on affiche la hitbox
                pygame.draw.rect(window, BLUE, member.hitbox)
            if member.selected:
                # Fond vert si le soldat est activé
                # TODO : Essaye de faire un truc plus joli
                pygame.draw.rect(window, GREEN, member.hitbox)

            if member.fire_at is not False:
                pygame.draw.line(window, WHITE, member.tile.abs_pos(), member.fire_at.tile.abs_pos())

            window.blit(self.spriteset, member.get_pos(), (member.frame[0] * 30, member.frame[1] * 60, 30, 60))

        # Ennemis
        for mob in self.mobs:
            if self.hl:
                # Si l'overlay est activé, on affiche la hitbox
                pygame.draw.rect(window, RED, mob.hitbox)
            if mob.is_ko():
                window.blit(self.dead, mob.get_pos(True))
            else:
                window.blit(self.spriteset, mob.get_pos(), (mob.frame[0] * 30, mob.frame[1] * 60, 30, 60))

            if mob.fire_at is not False:
                pygame.draw.line(window, WHITE, mob.tile.abs_pos(), mob.fire_at.tile.abs_pos())

        # Si l'overlay est activé, on affiche les couverts
        if self.hl:
            for tile in self.covers:
                pygame.draw.rect(window, GREEN, (tile.abs_pos('x') + 14, tile.abs_pos('y') + 14, 4, 4))

        # Nom de la map
        title = FONT8.render(self.map_name, 1, WHITE)
        window.blit(title, (10, 10))

        """ Affichage de menu """
        # Détails
        pygame.draw.rect(window, GREY50, (0, 578, 320, 144))
        for member in self.members:
            if member.selected:
                name = FONT28.render(member.name, 1, WHITE)
                tile = FONT8.render(str(member.tile), 1, WHITE)
                status = FONT8.render("Status : %s" % member.status, 1, WHITE)
                cover = FONT8.render("Cover bonus : +%s" % member.cover_bonus, 1, WHITE)
                hitchance = FONT8.render("HitChance : {}%".format(member.hit_chance), 1, WHITE)
                target = FONT8.render("Target : %s" % member.target, 1, WHITE)

                window.blit(name, (10, 588))
                window.blit(tile, (10, 620))
                window.blit(status, (10, 630))
                window.blit(cover, (10, 640))
                window.blit(hitchance, (10, 650))
                window.blit(target, (10, 660))

        # Alliés
        pygame.draw.rect(window, GREY75, (320, 578, 320, 144))
        i = 0

        frames_list = {}  # Générations des boutons

        for member in self.members:
            posx, posy = 325 + i * 53, 583
            width, height = 48, 48

            if member.selected:
                color = GREEN
            else:
                color = GREY25

            frames_list[member.id] = pygame.Rect(posx, posy, width, height)

            # Fond
            pygame.draw.rect(window, color, (posx, posy, width, height))
            # Portrait
            pygame.draw.rect(window, GREY75, (posx + 2, posy + 2, width - 4, height - 4))
            # Barre de vie
            pygame.draw.rect(window, GREY50, (posx, posy + height, width, 4))
            pygame.draw.rect(window, RED, (posx, posy + height, member.health[0] / member.health[1] * width, 4))

            # Barre de volonté
            pygame.draw.rect(window, GREY50, (posx, posy + height + 4, width, 4))
            pygame.draw.rect(window, GREEN, (posx, posy + height + 4, member.will[0] / member.will[1] * width, 4))

            # Barre d'action
            pygame.draw.rect(window, GREY50, (posx, posy + height + 8, width, 4))
            pygame.draw.rect(window, BLUE, (posx, posy + height + 8, member.cooldown[0] / member.cooldown[1] * width, 4))

            i += 1

        self.frame_list = frames_list

        # Liste des ennemis
        pygame.draw.rect(window, GREY50, (640, 578, 160, 144))
        i = 0
        for mob in self.mobs:
            posx, posy = 645 + i * 53, 583
            width, height = 48, 48

            if mob.ia_activated:
                color = RED
            else:
                color = GREY25

            # Fond
            pygame.draw.rect(window, color, (posx, posy, width, height))
            # Portrait
            pygame.draw.rect(window, GREY75, (posx + 2, posy + 2, width - 4, height - 4))
            # Barre de vie
            if mob.health == 0:
                life_ratio = 0
            else:
                life_ratio = mob.health[0] / mob.health[1] * width

            pygame.draw.rect(window, GREY50, (posx, posy + height, width, 4))
            pygame.draw.rect(window, RED, (posx, posy + height, life_ratio, 4))

            # Barre de volonté
            pygame.draw.rect(window, GREY50, (posx, posy + height + 4, width, 4))
            pygame.draw.rect(window, GREEN, (posx, posy + height + 4, mob.will[0] / mob.will[1] * width, 4))

            # Barre d'action
            pygame.draw.rect(window, GREY50, (posx, posy + height + 8, width, 4))
            pygame.draw.rect(window, BLUE,
                             (posx, posy + height + 8, mob.cooldown[0] / mob.cooldown[1] * width, 4))

            i += 1

        # Journal de combat
        pygame.draw.rect(window, GREY75, (800, 578, 480, 144))
        log_list = []
        for entry in self.log:
            log_list.append(self.log[entry])

        if len(log_list) > 13:
            aff_log_list = log_list[len(log_list) - 13:]
        else:
            aff_log_list = log_list

        i = 0
        for entry in aff_log_list:
            txt = FONT8.render(entry, 1, BLACK)
            window.blit(txt, (805, 583 + i * 10))
            i += 1

        # Pause et aide
        if self.pause:
            pause_txt = FONT28.render("PAUSE", 1, WHITE)
            restart_txt = FONT8.render("Appuyer sur 'R' pour recommencer", 1, WHITE)
            window.blit(pause_txt, (640 - pause_txt.get_rect().width / 2, 520))
            window.blit(restart_txt, (640 - restart_txt.get_rect().width / 2, 560))
        if self.help:
            window.blit(self.help_img, (0,0))

    """ Fonctions de mise à jour des bonhommes """
    def update_ia(self, mob):
        """ Gère l'intelligence artificielle des mobs """
        # On met à jour le mob
        mob.update(self.map, self.walls, self.log, [self.map_width, self.map_height])

        # On vérifie si le mob est à couvert
        if mob.tile in self.covers:
            mob.going_to_cover = False
            # Le mob est à couvert, on vérifie s'il a une cible
            for member in self.members:
                if member.is_ko():
                    pass
                elif mob.target is False:
                    mob.set_target(member)
                else:
                    if mob.tile.get_distance(member.tile) < mob.tile.get_distance(mob.target.tile):
                        # Le mob tire sur le joueur le plus proche
                        mob.set_target(member)
        # Le mob est à découvert, on vérifie s'il n'est pas déjà entrain de bouger
        elif mob.going_to_cover is False:
            # TODO : Verrouiller les positions déjà occupées
            # On cherche la position à couvert la plus proche
            best_cover = False
            for cover in self.covers:
                if best_cover is False:
                    best_cover = cover
                elif mob.tile.get_distance(cover) < mob.tile.get_distance(best_cover):
                    best_cover = cover

            """ Couvert trouvé """

            mob.destination = best_cover
            mob.path = pathfinder(self.walls, [self.map_width, self.map_height], mob.tile.copy(), best_cover)
            mob.going_to_cover = True

    def update(self):
        """ Mets à jour les membres et les mobs encore en état """
        for member in self.members:
            if member.is_ko() is False:
                member.update(self.map, self.walls, self.log, [self.map_width, self.map_height])

        for mob in self.mobs:
            if mob.is_ko() is False and self.ia_are_activated:
                self.update_ia(mob)

    """ Fonctions de génération """
    def generate_sold_mobs(self):
        """ Génère les soldats et les mobs """
        # TODO : Permettre de changer les paramètres
        soldiers = [Member('Michel', 6, 100, 55, 100, 4, 6, ['A', 'B']),
                    Member('Bob', 5, 100, 55, 100, 3, 6, ['B', 'C']),
                    Member('Arthur', 7, 100, 55, 100, 4, 6, ['A', 'C', 'B'])]

        # On fait se rencontrer les soldats
        for member in soldiers:
            for oth_member in soldiers:
                if oth_member != member:
                    member.meet(oth_member)

        # Zone de spawn allié
        spawns = [[4, 4], [4, 7], [4, 12]]
        for member in soldiers:
            self.members.append(CombatEntity(member, spawns.pop(0), Weapon('Pistolet automatique', 20, 80)))

        # On génère les mobs
        mobs = [Mob(), Mob()]
        mob_spawn = [[35, 8], [35, 14]]
        for mob in mobs:
            self.mobs.append(CombatEntity(mob, mob_spawn.pop(0), Weapon('Pistolet automatique', 15, 100)))

    def generate(self, level):
        """ Génère le niveau """
        with open(level, 'r') as file:
            t_y = 0
            for line in file:
                if line[0] in ['#', '\n']:
                    pass
                elif line[0] == '@':
                    name = line[1:]
                    name = name[:-1]
                    self.map_name = name
                else:

                    t_x = 0
                    for char in line:
                        if char == 'x':
                            self.map.append(Tile([t_x, t_y]))
                            self.walls.append(Tile([t_x, t_y]))
                        else:
                            self.map.append(Tile([t_x, t_y]))
                        t_x += 1
                    t_y += 1

            self.map_width, self.map_height = t_x, t_y

        for tile in self.walls:
            for neighbour in tile.get_neighbours(True):  # Cherche les voisins directs
                if neighbour not in self.walls and neighbour not in self.covers and neighbour.check_limits([self.map_width, self.map_height]):
                    self.covers.append(neighbour)

        self.log.append('Système', 'Chargement du tutoriel')


pygame.init()
window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption(TITLE)
FONT8 = pygame.font.Font(PressStart2P, 8)
FONT28 = pygame.font.Font(PressStart2P, 28)

tuto = Tutorial(map)

pause = True
continuer = 1
while continuer:
    pygame.time.Clock().tick(60)
    for event in pygame.event.get():
        # Quitter
        if event.type == QUIT:
            continuer = 0

        # Espace : pause
        if event.type == KEYUP and event.key == K_SPACE:
            tuto.spacebar()

        # Clic gauche
        if event.type == MOUSEBUTTONUP and event.button == 1:
            tuto.left_click(event.pos)
        # Clic droit
        if event.type == MOUSEBUTTONUP and event.button == 3:
            tuto.right_click(event.pos)

        # Raccourcis de sélection
        if event.type == KEYUP and event.key in [K_AMPERSAND, 160, 34]:
            tuto.shortcut(event.key)

        # Shift Gauche : HL
        if event.type == KEYDOWN and event.key == K_LSHIFT:
            tuto.hl = True
        if event.type == KEYUP and event.key == K_LSHIFT:
            tuto.hl = False

        # Restart
        if event.type == KEYUP and event.key == K_r:
            tuto = Tutorial(map)

        # Help
        if event.type == KEYUP and event.key == K_h:
            tuto.t_help()

    tuto.display(window)
    if tuto.pause is False:
        tuto.update()

    pygame.display.flip()
