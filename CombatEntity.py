import pygame
from TileClasses import *
from Member import *

orientations = {'nw': 5, 'no': 4, 'ne': 3, 'ea': 2, 'se': 1, 'so': 0, 'sw': 7, 'we': 6}


class CombatEntity:
    def __init__(self, entity, coord, weapon):
        """ Gère le soldat au combat """
        # On vérifie les paramètres
        if type(coord) != Tile:
            coord = Tile(coord)

        if type(entity) != Member:
            self.mob = True
        else:
            self.mob = False

        # Informations générales
        self.id = entity.id
        self.name = entity.name

        # Equipement
        self.weapon = weapon
        self.magazine = [weapon.magazine, weapon.magazine]

        # Compétences d'armes
        if type(entity) == Member:
            self.skills = entity.skills
            self.cooldown = [0, weapon.cooldown * self.skills.get_modifier(weapon.type)]
            self.reload_time = [0, weapon.reload_time * self.skills.get_modifier(weapon.type)]
        else:
            self.cooldown = [0, weapon.cooldown]
            self.reload_time = [0, weapon.cooldown]

        # Information de jeu
        self.exp = entity.exp
        self.health = [entity.health, entity.health]
        self.aim = [entity.aim, entity.aim]
        self.mobility = [entity.mobility, entity.mobility]
        self.will = [1000, 1000]
        self.will_reload = entity.will

        self.port = entity.port

        # Information de statut
        self.status = "idle"
        self.cover_bonus = 0
        self.hit_chance = 0

        # Informations graphiques
        self.orientation = 'ea'
        self.tile = coord
        # TODO : self.pos
        self.pos = [self.tile.abs_pos('x'), self.tile.abs_pos('y') - 28]
        self.frame = [0, orientations[self.orientation]]
        self.hitbox = pygame.Rect(self.tile.abs_pos('x') + 5, self.tile.abs_pos('y') - 18, 22, 44)

        # Sélection
        self.selected = False
        self.target = False
        self.fire_at = False

        # Pathfinder
        self.destination = self.tile.copy()
        self.path = []
        self.path_timer = 0

        # IA
        self.ia_activated = False
        self.going_to_cover = False

    def is_ko(self):
        """ Renvoie True si la vie du soldat tombe à 0 """
        return self.health[0] == 0

    def get_shot_at(self):
        # TODO : Ce qu'il se passe quand on se fait tirer dessus
        self.ia_activated = True
        self.will[0] -= 80
        if self.will[0] < 0:
            self.will[0] = 0

    def get_damage(self, damage, log):
        """ Ce qu'il se passe quand l'entité prend des dégâts"""
        self.health[0] -= damage
        self.will[0] -= 50
        if self.will[0] < 0:
            self.will[0] = 0
        if self.will[0] / self.will[1] * 100 < 25:
            log.append('Combat', "%s panique !" % self)
        if self.health[0] <= 0:
            log.append('Combat', "%s est KO !" % self)
            self.health[0] = 0

    def calcul_hit_chance(self, target):
        w_accuracy = self.weapon.accuracy
        if self.mob:
            skill_modifier = 1
        else:
            skill_modifier = self.skills.get_modifier(self.weapon.type)
        distance = self.tile.get_distance(target.tile)
        for dist in distance_range:
            if distance in dist:
                dist_indice = distance_range.index(dist)
        dist_modifier = weapon_type[self.weapon.type][1][dist_indice]
        cover_bonus = self.target.cover_bonus

        self.hit_chance = self.aim[0] * w_accuracy * skill_modifier * dist_modifier - cover_bonus

    def set_target(self, target):
        """ Indique la cible et calcule les chances de toucher """
        self.target = target
        self.calcul_hit_chance(target)

    def update(self, map,walls, log, limits):
        """ MàJ des infos du soldat à chaque tick """
        self.fire_at = False
        # On vérifie s'il est à couvert
        self.cover_bonus = 0
        for neighbour in self.tile.get_neighbours(True):
            # TODO : Vérifier que le soldat n'est pas contourné
            if neighbour in walls and neighbour.check_limits(limits):
                self.cover_bonus = 20

        # Recharge du cooldown
        if self.cooldown[0] < self.cooldown[1]:
            self.cooldown[0] += 1

        # Recharge de la volonté
        if self.will[0] < self.will[1]:
            self.will[0] += self.will_reload
        else:
            self.will[0] = self.will[1]

        # Vérifier la panique
        if self.will[0] / self.will[1] * 100 < 25:
            self._panick()

        elif self.destination != self.tile:
            self.cooldown[0] = 0
            self.status = "moving"
            self._move()
        elif self.magazine[0] == 0:
            self.status = 'reloading'
            self._reload()

        elif self.target is not False:
            self.calcul_hit_chance(self.target)
            if self.target.is_ko():
                self.target = False
                self.status = 'idle'
            elif self.magazine[0] > 0:
                self.status = "firing"
                self._fire(self.target, log)
            else:
                self.staus = 'reloading'

        # MàJ Graphique
        if self.status == "firing":
            sprite_x = 1
        else:
            sprite_x = 0

        self.frame = [sprite_x, orientations[self.orientation]]

    def _reload(self):
        self.cooldown[0] = 0
        self.reload_time[0] += 1
        if self.reload_time[0] == self.reload_time[1]:
            self.magazine[0] = self.magazine[1]
            self.reload_time[0] = 0

    def _panick(self):
        self.status = 'panick'
        self.cooldown[0] = 0

    def _fire(self, target, log):
        """ Boucle de tir """
        if self.cooldown[0] == self.cooldown[1]:
            if target.is_ko():
                self.target = False
            else:
                target.get_shot_at()
                self.fire_at = target
                if randrange(0,100) < self.hit_chance:
                    target.get_damage(self.weapon.damage, log)
                    log.append('Combat', "%s inflige %s dégâts à %s" % (self.name, self.weapon.damage, target))
                else:
                    log.append('Combat', "%s tire sur %s mais le rate" % (self.name, target))

                self.cooldown[0] = 0
                self.magazine[0] -= 1
                if self.magazine[0] == 0:
                    self.status == 'reload'

    def _move(self):
        """ Déplacement du soldat """
        # TODO : Rendre le déplacement fluide
        # TODO : Gérer l'animation du gaillard
        # On vérifie si le chemin est vide
        if len(self.path) > 0:
            # Incrémentation du timer
            self.path_timer += 1
            if self.path_timer > 10:
                # Nouvelle position
                new_tile = self.path[0].copy()
                self.path.remove(self.path[0])
                azimut = new_tile.get_direction(self.tile, True, True)
                self.tile = new_tile.copy()

                # MàJ graphique
                self.pos = [self.tile.abs_pos('x'), self.tile.abs_pos('y') - 28]
                self.hitbox = pygame.Rect(self.tile.abs_pos('x') + 5, self.tile.abs_pos('y') - 18, 22, 44)
                self.orientation = azimut

                # Réinitialisation du timer
                self.path_timer = 0

    def get_pos(self, dead=False):
        """ Retourne la position absolue pour l'affichage """
        if dead:
            return self.pos[0], self.pos[1] + 28
        else:
            return self.pos[0], self.pos[1]

    def get_sprite(self):
        """ Renvoie le tuple d'affichage de la frame"""
        return self.frame[0] * 30, self.frame[1] * 60, 30, 60

    def __repr__(self):
        """ Fonction de représentation """
        return self.name


class CombatEntityGroup:
    def __init__(self):
        """ Gestion et manipulation de groupes de soldats"""
        self._id = []
        self._member = []

    def unselect_all(self):
        """ Déselectionner tous les membres """
        for member in self._member:
            member.selected = False

    def select(self, select_member):
        """ Sélectionne un membre, déselectionne les autres"""
        if type(select_member) == int:
            sel = self._member[select_member]
        else:
            sel = select_member
        for member in self._member:
            if member == sel:
                member.selected = True
            else:
                member.selected = False

    def append(self, new_member):
        """ Ajoute le membre au groupe """
        if type(new_member) == CombatEntity:
            self._id.append(new_member.id)
            self._member.append(new_member)
        else:
            raise TypeError("Impossible d'ajouter %s (type:%s)" % (new_member, type(new_member)))

    def __getitem__(self, indice):
        """ Méthode de récupération """
        return self._member[indice]

    def __iter__(self):
        """ Méthode d'itération """
        return iter(self._member)

    def __getattr__(self, item_member):
        # TODO : Différence avec __getitem__ ?
        if type(item_member) == CombatEntity:
            indice = item_member.id
        elif type(item_member) == int:
            indice = item_member
        else:
            raise TypeError("%s (type=%s) n'est pas possible comme type")

        if indice in self._id:
            return self.member[0]
        else:
            raise KeyError("ID%s n'est pas dans la liste" % indice)

    def __repr__(self):
        return "CombatEntityGroup(%s)" % self._member

