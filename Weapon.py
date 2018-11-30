# Types d'armes {Acronyme : (Nom complet, Efficacité distance)}

weapon_type = {'PA': ('Pistolet automatique', [1.3, 1, 0.5]),
               'FA': ('Fusil automatique', [0.9, 1.3, 1]),
               'FP': ('Fusil de précision', [0.3, 1, 1.5]),
               'RE': ('Revolver', [1.3, 1, 0.5])}

distance_range = [range(0,300), range(300, 1000), range(1000, 4000)]

weapon_modes = {'NOR': 'Normal',
                'PRE': 'Tir de précision',
                'COV': 'Tir de couverture',
                'RAF': 'Rafale'}


class Weapon:
    def __init__(self, name, type, accuracy, damage, cooldown, reload_time, magazine, modes):
        """ Premet de créer les armes
        :param name: Le nom de l'arme
        :param type: Le type de la l'arme ('PA', 'FA', 'FP')
        :param damage: Les dégâts qu'inflige l'arme
        :param cooldown: Le temps entre deux tirs
        :param reload_time: Le temps de recharge
        :param magazine: La taille du chargeur
        :param modes: Les modes de tir disponibles ('NOR', 'PRE', 'COV', 'RAF')
        """

        # Informations générales
        self.name = name
        self.type = type

        # Dégâts
        self.damage = damage
        self.accuracy = accuracy

        # Cooldowns
        self.cooldown = cooldown
        self.reload_time = reload_time
        self.magazine = magazine

        # Modes de tir
        self.modes = modes

    def __repr__(self):
        return "Weapon:%s" % self.name


default_weapons = {'PAMAS': Weapon('PAMAS', 'PA', 0.8, 20, 100, 80, 8, ['NOR', 'PRE', 'COV']),
                   'Pétoire': Weapon('Pétoire', 'RE', 0.5, 25, 200, 200, 6, ['NOR', 'PRE'])}