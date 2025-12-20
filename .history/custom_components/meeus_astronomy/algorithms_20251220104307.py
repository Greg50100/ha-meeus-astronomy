import math
import time
from datetime import datetime, timezone

# ==============================================================================
# BIBLIOTHÈQUE D'ALGORITHMES ASTRONOMIQUES
# Basé sur "Astronomical Algorithms" de Jean Meeus (2ème Édition)
# Chapitre 7 : Julian Day
# ==============================================================================

def is_leap_year(year: int) -> bool:
    """
    Détermine si une année est bissextile selon le calendrier Grégorien.
    Nécessaire pour le calcul du Jour de l'Année.
    """
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    return False

def gregorian_to_jd(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
    """
    Convertit une date Grégorienne en Jour Julien (JD).
    
    RÉFÉRENCE : Page 60-61, Formule 7.1
    
    FORMULES DU LIVRE :
    Si M > 2, alors Y et M restent inchangés.
    Si M = 1 ou 2, alors Y = Y - 1 et M = M + 12.
    
    Dans le calendrier Grégorien :
    A = INT(Y / 100)
    B = 2 - A + INT(A / 4)
    
    JD = INT(365.25(Y + 4716)) + INT(30.6001(M + 1)) + D + B - 1524.5
    
    Args:
        year (Y): Année (ex: 2024)
        month (M): Mois (1-12)
        day (D): Jour du mois (avec décimales pour inclure l'heure)
    """
    # 1. Gestion des mois Janvier/Février (Page 61)
    if month <= 2:
        year -= 1
        month += 12
    
    # 2. Calcul de A et B pour le calendrier Grégorien (Page 61)
    # Note: INT correspond à la partie entière (int() en Python)
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    
    # 3. Ajout de la fraction du jour (Heure) au jour D
    # Le jour 'D' dans la formule inclut la fraction temporelle
    day_fraction = day + (hour + minute / 60 + second / 3600) / 24.0
    
    # 4. Formule 7.1
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day_fraction + B - 1524.5
    
    return jd

def jd_to_gregorian(jd: float):
    """
    Convertit un Jour Julien (JD) en date Grégorienne.
    
    RÉFÉRENCE : Page 63, Algorithme inverse
    
    FORMULES DU LIVRE :
    JD = JD + 0.5
    Z = Partie entière de JD
    F = Partie fractionnaire de JD
    
    Si Z < 2299161, A = Z
    Sinon :
        alpha = INT((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - INT(alpha / 4)
        
    B = A + 1524
    C = INT((B - 122.1) / 365.25)
    D = INT(365.25 * C)
    E = INT((B - D) / 30.6001)
    
    Jour du mois (avec décimales) = B - D - INT(30.6001 * E) + F
    Mois = E - 1 (si E < 14) ou E - 13 (si E=14 ou 15)
    Année = C - 4716 (si Mois > 2) ou C - 4715 (si Mois = 1 ou 2)
    """
    jd_adjusted = jd + 0.5
    Z = int(jd_adjusted)
    F = jd_adjusted - Z
    
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
        
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    
    # Calcul du jour avec sa fraction
    day_with_fraction = B - D - int(30.6001 * E) + F
    day = int(day_with_fraction)
    
    if E < 14:
        month = E - 1
    else:
        month = E - 13
        
    if month > 2:
        year = C - 4716
    else:
        year = C - 4715
        
    # Conversion de la fraction de jour en H:M:S
    fractional_day = day_with_fraction - day
    total_seconds = fractional_day * 86400
    
    hour = int(total_seconds // 3600)
    total_seconds %= 3600
    minute = int(total_seconds // 60)
    second = round(total_seconds % 60, 4) # Arrondi à 4 décimales
    
    return year, month, day, hour, minute, second

def jd_to_mjd(jd: float) -> float:
    """
    Calcule le Jour Julien Modifié (MJD).
    
    RÉFÉRENCE : Page 63
    
    FORMULE :
    MJD = JD - 2400000.5
    
    Note : Alors que le JD commence à midi (12h UTC), 
    le MJD commence à minuit (0h UTC).
    """
    return jd - 2400000.5

def mjd_to_jd(mjd: float) -> float:
    """
    Convertit un MJD en JD.
    """
    return mjd + 2400000.5

def day_of_week(jd: float) -> str:
    """
    Calcule le jour de la semaine.
    
    RÉFÉRENCE : Page 65
    
    FORMULE :
    Le jour de la semaine est obtenu par : (JD + 1.5) modulo 7
    Le résultat est 0 pour Dimanche, 1 pour Lundi, ... 6 pour Samedi.
    
    Note: On utilise le JD à 0h UTC pour obtenir le jour civil correct.
    """
    # On ajoute 1.5 au JD, on prend la partie entière, puis modulo 7
    # Note: Utiliser le JD correspondant à midi de la date donnée donne aussi le bon résultat
    # car la formule est conçue pour absorber le décalage de 0.5.
    
    wd = int(jd + 1.5) % 7
    days = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    return days[wd]

def day_of_year(year: int, month: int, day: int) -> int:
    """
    Calcule le numéro du jour dans l'année (DoY).
    
    RÉFÉRENCE : Page 65
    
    FORMULE :
    N = INT(275 * M / 9) - K * INT((M + 9) / 12) + D - 30
    
    Où K = 1 si bissextile, K = 2 si année commune.
    """
    if is_leap_year(year):
        K = 1
    else:
        K = 2
        
    N = int((275 * month) / 9) - K * int((month + 9) / 12) + day - 30
    return N

def time_interval(jd1: float, jd2: float) -> float:
    """
    Calcule l'intervalle de temps en jours entre deux dates.
    
    RÉFÉRENCE : Page 66
    
    FORMULE :
    Intervalle = JD2 - JD1
    """
    return abs(jd2 - jd1)

# ==============================================================================
# AFFICHAGE DES "SENSORS" (Zone de Test et d'Utilisation)
# ==============================================================================

if __name__ == "__main__":
    print("=== ASTRONOMICAL ALGORITHMS (CHAPITRE 7) ===\n")
    
    # 1. Récupération de la date actuelle (UTC est préférable pour l'astronomie)
    now = datetime.now(timezone.utc)
    y, m, d = now.year, now.month, now.day
    h, mn, s = now.hour, now.minute, now.second + now.microsecond/1000000.0
    
    print(f"Date actuelle (UTC) : {d}/{m}/{y} à {h}:{mn}:{s:.2f}")
    
    # --- CALCUL DES SENSORS ---
    
    # Sensor 1: Julian Day
    current_jd = gregorian_to_jd(y, m, d, h, mn, s)
    
    # Sensor 2: Modified Julian Day
    current_mjd = jd_to_mjd(current_jd)
    
    # Sensor 3: Day of Week
    current_dow = day_of_week(current_jd)
    
    # Sensor 4: Day of Year (DoY)
    current_doy = day_of_year(y, m, d)
    
    print("\n--- SENSORS ACTUELS ---")
    print(f"[Sensor] Julian Day (JD)          : {current_jd:.6f}")
    print(f"[Sensor] Modified Julian Day (MJD): {current_mjd:.6f}")
    print(f"[Sensor] Jour de la semaine       : {current_dow}")
    print(f"[Sensor] Jour de l'année (DoY)    : {current_doy}")
    
    
    # --- VERIFICATION MANUELLE (EXEMPLES DU LIVRE) ---
    print("\n--- VÉRIFICATION MANUELLE (Exemples du Livre) ---")
    
    # Exemple 7.a (Page 61) : 4 Octobre 1957 (Lancement Spoutnik)
    # JD attendu : 2436116.31 (Si on prend l'heure 19:26:24 UT du lancement)
    # Ici calculons pour 0h UTC comme dans l'exemple standard du livre
    jd_sputnik = gregorian_to_jd(1957, 10, 4.81) # 4.81 = le 4 octobre à 19.44h
    print(f"Test Spoutnik (4 Oct 1957, ~19h) -> JD: {jd_sputnik:.2f} (Attendu ~2436116.31)")
    
    # Exemple Page 62 : 27 Janvier 333 (année 333) à 12h
    jd_333 = gregorian_to_jd(333, 1, 27, 12, 0, 0)
    print(f"Test An 333 (27 Jan 12h)         -> JD: {jd_333:.1f} (Attendu 1842713.0)")
    
    # Test Intervalle (Page 66) : Comète de Halley
    # Passage 1 : 1910 Avril 20.0
    # Passage 2 : 1986 Février 9.0
    jd_halley_1 = gregorian_to_jd(1910, 4, 20)
    jd_halley_2 = gregorian_to_jd(1986, 2, 9)
    interval = time_interval(jd_halley_1, jd_halley_2)
    print(f"Intervalle Comète Halley         -> {interval:.1f} jours (Attendu 27689.0)")

    # Test Inverse
    print("\n--- TEST INVERSE (JD -> Grégorien) ---")
    calc_y, calc_m, calc_d, calc_h, calc_mn, calc_s = jd_to_gregorian(current_jd)
    print(f"Entrée JD : {current_jd}")
    print(f"Sortie    : {calc_d}/{calc_m}/{calc_y} à {calc_h}:{calc_mn}:{calc_s:.2f}")