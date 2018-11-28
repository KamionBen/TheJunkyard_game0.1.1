class Mob:
    id = 0

    def __init__(self, intel=1, health=70, aim=45, mobility=100, will=1):
        """
        Classe miroir de Member, mais pour les mobs
        :param name: Le nom du mob
        :param intel: L'intelligence
        :param health: La santé
        :param aim: La précision
        :param mobility: La vitesse de déplacement
        :param will: La vitesse de rechargement de la volonté
        :param port: La capacité de portage
        :param temper: False par défaut : Mettre une liste de type ['A', 'B', 'D'] pour mettre un temper personnalisé
        """

        # Identifiant unique
        self.id = Mob.id
        Mob.id += 1

        # Informations générales
        self.name = 'Mob%s' % self.id
        self.intel = intel

        # Pas de tempérament pour les mobs, mais on mets quand même la variable
        self.temper = False
        # Pas non plus de relations
        self.relations = {}

        # Information de jeu
        self.exp = 0
        self.health = health
        self.aim = aim
        self.mobility = mobility
        self.will = will
        self.port = 0

    def details(self):
        """ Renvoie les informations détaillées """
        general = "Name : %s" % self.name
        game = "H : %s | A : %s | M : %s | W : %s" % (self.health, self.aim, self.mobility, self.will)
        return "%s\n%s\n" % (general, game)

    def __repr__(self):
        return self.name
