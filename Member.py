from random import choice, randrange
from Weapon import *

class Member:
    id = 0

    def __init__(self, name, intel, health, aim, mobility, will, port, temper=False):
        """
        :param name: Le nom du membre
        :param intel: L'intelligence
        :param health: La santé
        :param aim: La précision
        :param mobility: La vitesse de déplacement
        :param will: La vitesse de rechargement de la volonté
        :param port: La capacité de portage
        :param temper: False par défaut : Mettre une liste de type ['A', 'B', 'D'] pour mettre un temper personnalisé
        """

        # Identifiant unique
        self.id = Member.id
        Member.id += 1

        # Informations générales
        self.name = name
        self.intel = intel

        # Tempérament
        if temper is False:
            self.temper = Temper(self.intel)
        else:
            # TODO : Vérifier que temper est valide
            self.temper = Temper(self.intel, temper)

        # Compétences d'armes
        self.skills = Skills()  # Au hasard pour l'instant

        # Relations
        self.relations = {}

        # Information de jeu
        self.exp = 0
        self.health = health
        self.aim = aim
        self.mobility = mobility
        self.will = will
        self.port = port

    def meet(self, other_member):
        """ Les deux membres se rencontrent, on compare leur tempérament """
        if other_member.id not in self.relations.keys():
            result = self.temper._compare(other_member.temper)
            self.relations[other_member] = result
            other_member.relations[self] = result

    def details(self):
        """ Renvoie les informations détaillées """
        general = "ID : %s | Name : %s | Intelligence : %s" % (self.id, self.name, self.intel)
        temper = self.temper
        game = "H : %s | A : %s | M : %s | W : %s | P : %s" % (self.health, self.aim, self.mobility, self.will, self.port)
        relations = "Relations : %s" % self.relations
        return "%s\n%s\n%s\n%s" % (general, temper, game, relations)

    def __repr__(self):
        return self.name


class Temper:
    def __init__(self, intel, temper=False):
        """
        :param intel: L'intelligence du membre
        """
        self.intel = intel

        self.main_temper = []
        self.side_temper = []

        self.temper_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        self._gen_temper(intel, temper)

    def _compare(self, other_temper):
        result = 0

        # Principal
        for m_temper in self.main_temper:
            if m_temper in other_temper.main_temper:
                # Le temper principal correspond
                result += int(100 / self.intel)
            if self.temper_list[self.temper_list.index(m_temper) - 4] in other_temper.main_temper:
                # Le temper principal est opposé
                result -= int(100 / self.intel)

            if m_temper in other_temper.side_temper:
                # Le temper principal correspond à un temper secondaire
                result += int(75 / self.intel)
            if self.temper_list[self.temper_list.index(m_temper) - 4] in other_temper.side_temper:
                # Le temper principal est opposé à un temper secondaire
                result -= int(75 / self.intel)

        # Secondaire
        for s_temper in self.side_temper:
            if s_temper in other_temper.side_temper:
                # Le temper secondaire correspond
                result += int(50 / self.intel)
            if self.temper_list[self.temper_list.index(s_temper) - 4] in other_temper.side_temper:
                # Le temper secondaire est opposé
                result -= int(50 / self.intel)

            if s_temper in other_temper.main_temper:
                # Le temper secondaire correspond à un temper principal
                result += int(75 / self.intel)
            if self.temper_list[self.temper_list.index(s_temper) - 4] in other_temper.main_temper:
                # Le temper secondaire est opposé à un temper principal
                result -= int(75 / self.intel)

        return result

    def _gen_temper(self, intel, temper):
        """ Génère le tempérament du membre """
        if temper is False:
            number = int(intel / 3)

            # Si number n'est pas un multiple de 3, on a 50% de chance d'avoir un temper de plus
            if number % 3 > 0:
                if randrange(0,100) < 50:
                    number += 1

            proxy_temper_list = self.temper_list.copy()
            # On génère le tempérament principal
            while number > 0:
                # On choisit un temper au hasard et on l'enlève de la liste
                self.main_temper.append(proxy_temper_list.pop(proxy_temper_list.index(choice(proxy_temper_list))))
                number -= 1
        else:
            self.main_temper = temper
        # On trie la liste
        self.main_temper.sort()

        # On génère le tempérament secondaire
        for main_temp in self.main_temper:
            left = self.temper_list[self.temper_list.index(main_temp) - 1]
            right = self.temper_list[self.temper_list.index(main_temp) - 7]

            if left in self.main_temper or left in self.side_temper:
                # Le temper est déjà quelque part, on pass
                pass
            else:
                self.side_temper.append(left)

            # On fait pareil pour la droite
            if right in self.main_temper or right in self.side_temper:
                # Le temper est déjà quelque part, on pass
                pass
            else:
                self.side_temper.append(right)

        # On trie la liste secondaire
        self.side_temper.sort()

    def __repr__(self):
        temper = self.main_temper + self.side_temper
        temper.sort()
        for s_t in temper:
            if s_t in self.side_temper:
                temper[temper.index(s_t)] = s_t.lower()

        return "Temper(%s)" % temper


class Skills:
    def __init__(self, preset=None):
        """ Classe permettant de gérer les compétences d'armes """
        # TODO : Permettre de pré remplir les compétences

        self.skills = {}

        if preset is None:
            for type in weapon_type.keys():
                self.skills[type] = randrange(0, 30)

        self.note = {range(0, 10): ('F', 0.6),
                     range(10, 20): ('E', 0.8),
                     range(20, 30): ('D', 1),
                     range(30, 40): ('C', 1.2),
                     range(40, 50): ('B', 1.3),
                     range(50, 60): ('B+', 1.4),
                     range(60, 70): ('A', 1.5),
                     range(70, 80): ('A+', 1.6),
                     range(80, 90): ('S', 1.8),
                     range(90, 100): ('S+', 2)}

    def get_modifier(self, weapon_type):
        """ Renvoie le modificateur en fonction du type d'arme """
        level = self.skills[weapon_type]
        for n_range, note in self.note.items():
            if level in n_range:
                return note[1]

    def get_note(self, weapon_type):
        """ Renvoie la note en fonction du type d'arme """
        level = self.skills[weapon_type]
        for n_range, note in self.note.items():
            if level in n_range:
                return note[0]

    def __repr__(self):
        """ Méthode de représentation """
        renvoi = ""
        for type, level in self.skills.items():
            renvoi += "%s : %s\n" % (type, self.get_note(type))
        return renvoi
