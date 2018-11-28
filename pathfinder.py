from TileClasses import *


def pathfinder(non_traversable,limits, start, end):
    """ Fonction pour trouver son chemin, renvoie une liste de coordonnées """
    # TODO : A améliorer
    open = TileGroup()
    closed = TileGroup()

    open.append(start)

    loop = True
    while loop:
        current = open.get_lowest_f()
        open.remove(current)
        closed.append(current)

        # On vérifie si on a trouvé le chemin
        if current == end:
            path = [current]  # Liste de Tile

            while path[0] != start:
                # TODO : A mettre à jour
                step = closed[path[0] + path[0].get_direction(path[0].direction)]
                if step == start:
                    break
                path.insert(0, step)
            break

        # On continue les recherches
        for neighbour in current.get_neighbours():
            if neighbour in non_traversable or neighbour in closed or neighbour.check_limits(limits) is False:
                # Mur, ou déjà analysé, ou hors-limites
                pass
            # TODO : A mettre à jour
            else:
                direction = neighbour.get_direction(current, True )
                neighbour.calcul_f(start, end, direction)
                if neighbour in open:
                    if neighbour.f < open[neighbour].f:
                        open[neighbour].calcul_f(start, end, direction)
                else:
                    open.append(neighbour)

    return path
