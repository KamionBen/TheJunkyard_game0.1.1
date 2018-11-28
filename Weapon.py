weapon_type = ['Pistolet automatique', 'Fusil automatique', 'Fusil de précision']


class Weapon:
    def __init__(self, type, damage, cooldown):
        """ Premet de créer les armes """
        # TODO : Nom, type, taille du chargeur, cooldown et toutes les fonctions
        self.type = type
        self.damage = damage
        self.cooldown = cooldown