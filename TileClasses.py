NEIGHBOURS = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]  # Tuiles voisine
DIRECTIONS = ['nw', 'no', 'ne', 'ea', 'se', 'so', 'sw', 'we']  # Azimuts


class Tile:
    def __init__(self, coord):
        """ Classe qui permet de gérer et de manipuler les tuiles """
        # Coordonnées
        self.x, self.y = coord[0], coord[1]

        # Informations PathFinder
        self.g = 0  # Distance depuis le départ
        self.h = 0  # Distance depuis la fin
        self.f = self.g + self.h
        self.direction = False

    def check_limits(self, limits):
        """ Renvoie True si la tuile est dans les limites données """
        # On convertit en Tile si besoin
        if type(limits) != Tile:
            limits = Tile(limits)

        limit_x = self.x > 0 or self.x <= limits.x
        limit_y = self.y > 0 or self.y <= limits.y

        return limit_x and limit_y


    def calcul_f(self, start, end, direction):
        """ Calcule la valeur de f et indique la direction """
        # Convertit 'start' et 'end' si besoin
        if type(start) != Tile:
            start = Tile(start)
        if type(end) != Tile:
            end = Tile(end)

        self.g = self.get_distance(start)
        self.h = self.get_distance(end)
        self.f = self.g + self.h
        self.direction = direction

    def get_direction(self, tile, azimut=False, opposite=False):
        """ Prend une tuile voisine en paramètre et renvoie la direction sous forme [x,y] ou 'azimut'"""
        if opposite:
            opp = - 4
        else:
            opp = 0

        if type(tile) == str:
            if tile in DIRECTIONS:
                indice = DIRECTIONS.index(tile)
                return NEIGHBOURS[indice + opp]

        else:
            if type(tile) != Tile:
                tile = Tile(tile)

            difference = tile - self
            if difference in NEIGHBOURS:
                if azimut:
                    return DIRECTIONS[NEIGHBOURS.index(difference) + opp]
                else:
                    return NEIGHBOURS[NEIGHBOURS.index(difference) + opp]
            else:
                raise IndexError("La tuile doit être voisine. %s ne convient pas." % tile)

    def get_distance(self, dist_tile):
        """ Renvoie la distance par rapport à une tuile """
        # On convertit en Tile si besoin
        if type(dist_tile) != Tile:
            dist_tile = Tile(dist_tile)

        difference = [abs(self.x - dist_tile.x), abs(self.y - dist_tile.y)]
        distance = min(difference) * 45 + (max(difference) - min(difference)) * 32

        return distance

    def get_neighbours(self, direct=False):
        """ Renvoie une liste des tuiles voisines
        Si direct est Vrai, on n'inclut pas les tuiles diagonales """
        tile_list = []
        for n_tile in NEIGHBOURS:
            if direct:
                if n_tile[0] == 0 or n_tile[1] == 0:
                    tile_list.append(self + n_tile)
            else:
                tile_list.append(self + n_tile)

        return tile_list

    def abs_pos(self, xy='both'):
        """ Renvoie la position absolue (x32) """
        """ Prends xy en paramètre si on veut seulement x, ou seulement y """
        if xy in ['x', 0]:
            return self.x * 32
        elif xy in ['y', 1]:
            return self.y * 32
        elif xy == 'both':
            pos = (self.x * 32, self.y * 32)
            return pos
        else:
            raise TypeError("Paramètre non valide pour trouver la position absolue. param:%s type:%s" % (xy, type(xy)))

    def copy(self):
        """ Copie l'objet """
        return Tile(self.get())

    def get(self):
        """ Renvoie la position sous la forme [x,y] """
        return [self.x, self.y]

    # Remplacement des méthodes existantes

    def __iadd__(self, iadd_tile):
        """ Méthode pour i_additionner les coordonnées """
        # TODO : A voir si cette fonction est utile ou pas
        # On vérifie le type de add_tile
        if type(iadd_tile) == Tile:
            self.x += iadd_tile.x
            self.y += iadd_tile.y
            return self
        elif type(iadd_tile) == list or type(iadd_tile) == tuple:
            self.x += iadd_tile[0]
            self.y += iadd_tile[1]
            return self
        else:
            raise TypeError("Impossible d'i_additionner %s avec %s (type:%s)" % self, iadd_tile, type(iadd_tile))

    def __add__(self, add_tile):
        """ Méthode pour additionner les coordonnées """
        # On vérifie le type de add_tile
        if type(add_tile) == Tile:
            return Tile([self.x + add_tile.x, self.y + add_tile.y])
        elif type(add_tile) == list or type(add_tile) == tuple:
            return Tile([self.x + add_tile[0], self.y + add_tile[1]])
        else:
            raise TypeError("Impossible d'additionner %s avec %s (type:%s)" % self, add_tile, type(add_tile))

    def __sub__(self, sub_tile):
        """ Méthode pour soustraire les coordonnées """
        # TODO Faire __isub__ ?
        # On vérifie le type de sub_tile
        if type(sub_tile) == Tile:
            return Tile([self.x - sub_tile.x, self.y - sub_tile.y])
        elif type(sub_tile) == list or type(sub_tile) == tuple:
            return Tile([self.x - sub_tile[0], self.y - sub_tile[1]])
        else:
            raise TypeError("Impossible de soustraire %s avec %s (type:%s)" % self, sub_tile, type(sub_tile))

    def __eq__(self, eq_tile):
        """ Méthode pour vérifier l'égalité """
        # On vérifie le type de eq_tile
        if type(eq_tile) == Tile:
            return self.x == eq_tile.x and self.y == eq_tile.y
        elif type(eq_tile) == list or type(eq_tile) == tuple:
            return self.x == eq_tile[0] and self.y == eq_tile[1]
        else:
            raise TypeError("Impossible de comparer %s avec %s (type:%s)" % (self, eq_tile, type(eq_tile)))

    def __repr__(self):
        """ Méthode de réprésentation """
        return "[%s|%s]" % (self.x, self.y)


class TileGroup:
    def __init__(self):
        # TODO : Faire un groupe déjà rempli, ou bien concaténer les groupes
        """ Permet de gérer et de manipuler des groupes de tuiles """
        self._keys = []  # Clés, au format Coord
        self._tiles = []  # Valeurs, au format Tile

    def append(self, add_tile):
        """ Ajoute une tuile dans le groupe """
        # On convertit la tuile s'il le faut
        if type(add_tile) != Tile:
            add_tile = Tile(add_tile)

        self._keys.append(add_tile.get())
        self._tiles.append(add_tile)

    def remove(self, remove_tile):
        """ Retire une tuile spécifique """
        if remove_tile in self._keys:
            indice = self._keys.index(remove_tile)
        elif remove_tile in self._tiles:
            indice =self._tiles.index(remove_tile)
        else:
            raise IndexError("%s (type:%s) n'est pas dans le groupe" % (remove_tile, type(remove_tile)))

        del self._keys[indice]
        del self._tiles[indice]

    def get_lowest_f(self):
        """ Renvoie la tuile ayant le plus bas f. En cas d'égalité, choisit le h le plus bas """
        if len(self._tiles) > 0:
            lowest_f = self._tiles[0]
            for tile in self._tiles:
                if tile.f < lowest_f.f:
                    lowest_f = tile
                elif tile.f == lowest_f.f:
                    if tile.h < lowest_f.h:
                        lowest_f = tile
        else:
            raise IndexError("get_lowest_f Erreur : Le groupe de tuiles est vide !")

        return lowest_f

    def __contains__(self, contains_tile):
        """ Vérifie si la tuile est dans le groupe """
        if contains_tile in self._keys or contains_tile in self._tiles:
            return True
        else:
            return False

    def __iter__(self):
        """ Méthode d'itération """
        return iter(self._tiles)

    def __getitem__(self, item_tile):
        """ Méthode de récupération """
        # On convertit en Tile s'il le faut
        if type(item_tile) != Tile:
            item_tile = Tile(item_tile)

        if item_tile in self._tiles:
            return self._tiles[self._tiles.index(item_tile)]
        else:
            raise IndexError("%s n'est pas dans le groupe" % item_tile)

    def __repr__(self):
        """ Méthode de représention """
        return "TileGroup : %s" % self._tiles
