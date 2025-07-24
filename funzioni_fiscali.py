
"""
Module funzioni_fiscali.py

Contiene funzioni equivalenti alle LAMBDA di Excel per calcoli fiscali.
"""

def add_reg(reddito):
    """Calcola l'addizionale regionale IRPEF"""
    if reddito <= 15000:
        return reddito * 0.0123
    elif reddito <= 28000:
        return reddito * 0.0318
    elif reddito <= 50000:
        return reddito * 0.0323
    else:
        return reddito * 0.0333


def bonus_redditi(reddito):
    """Attribuisce un bonus fiscale basato sul reddito"""
    if reddito < 15000:
        return reddito * 0.053
    elif reddito <= 20000:
        return reddito * 0.048
    else:
        return 0


def contr_inps(reddito, aliquota):
    """Calcola i contributi INPS con maggiorazione sopra i 55.000€"""
    base = reddito * aliquota
    if reddito > 55000:
        return base + (reddito - 55000) * 0.01
    return base


def detr_lav_dip(reddito, giorni, mese):
    """Detrazioni per lavoro dipendente semplificate"""
    # Calcolo base (può essere aggiustato in base alla normativa)
    return max(0, reddito * 0.2) + (giorni / 365.0 * mese)


def ex_bonus_renzi(reddito):
    """Bonus Renzi per i redditi inferiori a 15.000€"""
    return 1200 if reddito < 15000 else 0


def irpef(reddito):
    """Calcola l'IRPEF progressiva"""
    if reddito <= 15000:
        return reddito * 0.23
    elif reddito <= 28000:
        return (15000 * 0.23) + ((reddito - 15000) * 0.27)
    elif reddito <= 55000:
        return (15000 * 0.23) + (13000 * 0.27) + ((reddito - 28000) * 0.38)
    else:
        return (15000 * 0.23) + (13000 * 0.27) + (27000 * 0.38) + ((reddito - 55000) * 0.41)


def irpef_mensile(reddito):
    """Calcola l'IRPEF mensile"""
    return irpef(reddito) / 12


def irpef_con_addiz(reddito):
    """Calcola l'IRPEF con le addizionali regionali incluse"""
    return irpef(reddito) + add_reg(reddito)


def taglio_cun_fisc(reddito, lavoratore_dipendente):
    """Calcola il taglio del cuneo fiscale"""
    # esempio semplificato: applica 10% di taglio se dipendente
    return reddito * 0.1 if lavoratore_dipendente else 0

# Sezione di test (può essere rimossa per il deployment)
if __name__ == "__main__":
    # Esempi di utilizzo delle funzioni
    print("Add_reg per reddito 30000:", add_reg(30000))
    print("Bonus redditi per reddito 16000:", bonus_redditi(16000))
    print("Contr INPS per reddito 60000 e aliquota 0.1:", contr_inps(60000, 0.1))
    print("Detr Lav Dip:", detr_lav_dip(30000, 21, 30))
    print("Ex bonus Renzi per reddito 12000:", ex_bonus_renzi(12000))
    print("IRPEF per reddito 30000:", irpef(30000))
    print("IRPEF mensile per reddito 30000:", irpef_mensile(30000))
    print("IRPEF con addiz per reddito 30000:", irpef_con_addiz(30000))
    print("Taglio cun fisc per dipendente:", taglio_cun_fisc(30000, True))
