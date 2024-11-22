from myslg import Buff  # Adjust imports to match your project structure

def atk_up1():
    buff = Buff('buff', "atk_up", 20, 3, f"increase 20 %% attack for 3 turns.")
    return buff

def atk_up2():
    buff = Buff('buff', "atk_up", 50, 1, f"increase 50 %% attack for 1 turn.")
    return buff

def atk_down1():
    buff = Buff('debuff', "atk_down", 20, 3, f"decrease 20 %% attack for 3 turn.")
    return buff

def atk_up3():
    buff = Buff('buff', "atk_up", 40, 3, f"increase 40 %% attack for 3 turn.")
    return buff