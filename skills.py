from myslg import Skill, Passive_skill  # Adjust imports to match your project structure

def fireball():
    skill = Skill("Fire Ball", 50, 3, "attack", 3)
    return skill

def slash():
    skill = Skill("Slash", 35, 1, "attack", 2)
    return skill

def iceSpear():
    skill = Skill("Ice Spear", 35, 5, "attack", 2)
    return skill

def thunder():
    skill = Skill("Thunder", 70, 3, "attack", 6)
    return skill

# for buff skills, the 'damage' is the # of buff in buffs list.
def warCry():
    skill = Skill("War Bless", 1, 2, "buff", 4)
    return skill

def heal():
    skill = Skill("Heal", 30, 2, "heal", 3)
    return skill