"""
Mass balance calculation functions for IAQP.
"""
def calc_Voz(N, Co, Cbz, R, Ef, Ez, loc='A', Fr=1.0):
    """
    Wrapper for Case-A or Case-B outdoor-airflow (Voz) calculations.

    Inputs:
        N     : contaminant generation rate      [ug/h]
        Co    : outdoor concentration            [ug/m3]
        Cbz   : breathing-zone design limit      [ug/m3]
        R     : recirculation flow factor        (fraction)
        Ef    : filter efficiency                (fraction)
        Ez    : zone air distribution effectiveness (fraction)
        loc   : 'A' or 'B' (filter position, defaults to 'A' if unclear)
        Fr    : design flow-reduction fraction   (fraction, 1.0 = constant volume)

    Returns:
        Voz    : required outdoor airflow        [m3/h]
        Vr     : supply/return airflow now       [m3/h]
        Recirc : recirculated airflow now        [m3/h]
    """
    loc_in = loc
    loc    = str(loc).strip().upper() if loc is not None else 'A'

    if loc == 'B':
        return calc_Voz_caseB(N, Co, Cbz, R, Ef, Ez, Fr=Fr)
    elif loc == 'A':
        return calc_Voz_caseA(N, Co, Cbz, R, Ef, Ez, Fr=Fr)
    else:
        print(f"Note: unknown filter location '{loc_in}', defaulting to 'A'.")
        return calc_Voz_caseA(N, Co, Cbz, R, Ef, Ez, Fr=Fr)


def calc_Cbz(N, Voz, Co, R, Ef, Ez, Vr, loc='A', Fr=1.0):
    """
    Wrapper for Case-A or Case-B breathing-zone concentration (Cbz) calculations.

    Inputs:
        N     : contaminant generation rate      [ug/h]
        Voz   : outdoor airflow used for compound [m3/h]
        Co    : outdoor concentration            [ug/m3]
        R     : recirculation flow factor        (fraction)
        Ef    : filter efficiency                (fraction)
        Ez    : zone air distribution effectiveness (fraction)
        Vr    : return (supply) airflow          [m3/h]
        loc   : 'A' or 'B' (filter position, defaults to 'A' if unclear)
        Fr    : design flow-reduction fraction   (fraction, 1.0 = constant volume)

    Returns:
        Cbz : breathing-zone concentration       [ug/m3]
    """
    loc_in = loc
    loc    = str(loc).strip().upper() if loc is not None else 'A'

    if loc == 'B':
        return calc_Cbz_caseB(N, Voz, Co, R, Ef, Ez, Vr, Fr=Fr)
    elif loc == 'A':
        return calc_Cbz_caseA(N, Voz, Co, R, Ef, Ez, Vr, Fr=Fr)
    else:
        print(f"Note: unknown filter location '{loc_in}', defaulting to 'A'.")
        return calc_Cbz_caseA(N, Voz, Co, R, Ef, Ez, Vr, Fr=Fr)


def calc_Voz_caseA(N, Co, Cbz, R, Ef, Ez, Fr=1.0):
    """
    ASHRAE 62.1 Table F-1 Case A (filter at Position A).

    System types handled:
        - Constant outdoor air, constant volume (Fr = 1, R >= 0)
        - Constant outdoor air, VAV          (0 < Fr < 1, R > 0)
        - 100 % outdoor air, VAV             (0 < Fr < 1, R = 0)

    Inputs:
        N   : contaminant generation rate      [ug/h]
        Co  : outdoor concentration            [ug/m3]
        Cbz : breathing-zone design limit      [ug/m3]
        R   : recirculation flow factor        (fraction)
        Ef  : filter efficiency                (fraction)
        Ez  : zone air distribution effectiveness (fraction)
        Fr  : design flow-reduction fraction   (fraction, 1.0 = constant volume)

    Returns:
        Voz    : required outdoor airflow      [m3/h]
        Vr     : supply/return airflow now     [m3/h]
        Recirc : recirculated airflow now      [m3/h]
    """
    if R == 0.0:  # 100 % OA VAV (Table F-1 "None VAV 100 %") :contentReference[oaicite:5]{index=5}
        denom = Ez * Fr * (Cbz - Co)
    else:         # OA held constant (A Constant/Constant or A VAV/Constant) :contentReference[oaicite:6]{index=6}
        denom = Ez * (Cbz - Co + (Fr * R * Ef * Cbz) / (1 - R))

    if denom <= 0:
        print(f"Warning: Denominator <= 0 in calc_Voz_caseA for N={N}, Co={Co}, "
              f"Cbz={Cbz}, R={R}, Ef={Ef}, Ez={Ez}, Fr={Fr}. Returning zero airflow.")
        return 0.0, 0.0, 0.0

    Voz = N / denom

    if R == 0.0:
        Vr = Voz            # supply = outdoor (100 % OA)
        Recirc = 0.0
    else:
        Vr = Voz * Fr / (1 - R)  # current supply/return flow
        Recirc = R * Vr          # current recirculation flow

    return Voz, Vr, Recirc


def calc_Cbz_caseA(N, Voz, Co, R, Ef, Ez, Vr, Fr=1.0):
    """
    Steady-state breathing-zone concentration (Cbz) - ASHRAE 62.1 Table F-1, Case A.

    System types handled:
        - Constant outdoor air, constant volume (Fr = 1, R >= 0)
        - Constant outdoor air, VAV          (0 < Fr < 1, R > 0)
        - 100 % outdoor air, VAV             (0 < Fr < 1, R = 0)

    Parameters:
        N   : contaminant generation rate [ug/h]
        Voz : outdoor airflow used for this compound [m3/h]
        Co  : outdoor concentration [ug/m3]
        R   : recirculation flow factor (fraction)
        Ef  : filter efficiency (fraction)
        Ez  : zone air distribution effectiveness (fraction)
        Vr  : return (supply) airflow [m3/h]
        Fr  : design flow-reduction fraction (1.0 = constant volume)

    Returns:
        Cbz : breathing-zone concentration [ug/m3]
    """
    if R == 0.0:  # 100 % outdoor air (no recirculation) — Table F-1 “None VAV 100 %”
        denominator = Ez * Fr * Voz
        if denominator == 0:
            raise ZeroDivisionError("Denominator is zero in Cbz calculation.")
        return Co + N / denominator

    # Recirculation present (A Constant/Constant or A VAV/Constant)
    numerator   = N + Ez * Voz * Co
    denominator = Ez * (Voz + Fr * R * Vr * Ef)

    if denominator == 0:
        raise ZeroDivisionError("Denominator is zero in Cbz calculation.")
    return numerator / denominator


def calc_Voz_caseB(N, Co, Cbz, R, Ef, Ez, Fr=1.0):
    """
    ASHRAE 62.1 Table F-1 Case B (filter at Position B).

    System types handled:
        • Constant outdoor air, constant volume (Fr = 1, R ≥ 0)
        • Constant outdoor air, VAV          (0 < Fr < 1, R > 0)
        • 100 % outdoor air, VAV             (0 < Fr < 1, R = 0)

    Inputs:
        N   : contaminant generation rate      [ug/h]
        Co  : outdoor concentration            [ug/m3]
        Cbz : breathing-zone design limit      [ug/m3]
        R   : recirculation flow factor        (fraction)
        Ef  : filter efficiency                (fraction)
        Ez  : zone air distribution effectiveness (fraction)
        Fr  : design flow-reduction fraction   (fraction, 1.0 = constant volume)

    Returns:
        Voz    : required outdoor airflow      [m3/h]
        Vr     : supply/return airflow now     [m3/h]
        Recirc : recirculated airflow now      [m3/h]
    """
    if R == 0.0:  # 100 % OA VAV (Table F-1 “B VAV 100 %”) :contentReference[oaicite:3]{index=3}
        denom = Ez * Fr * (Cbz - (1 - Ef) * Co)
    else:         # OA held constant (Constant/Constant or VAV/Constant) :contentReference[oaicite:4]{index=4}
        denom = Ez * (Cbz - (1 - Ef) * Co + (Fr * R * Ef * Cbz) / (1 - R))

    if denom <= 0:
        print(f"Warning: Denominator <= 0 in calc_Voz_caseB for N={N}, Co={Co}, "
              f"Cbz={Cbz}, R={R}, Ef={Ef}, Ez={Ez}, Fr={Fr}. Returning zero airflow.")
        return 0.0, 0.0, 0.0

    Voz = N / denom

    if R == 0.0:
        Vr = Voz            # supply = outdoor (100 % OA)
        Recirc = 0.0
    else:
        Vr = Voz * Fr / (1 - R)  # current supply/return flow
        Recirc = R * Vr          # current recirculation flow

    return Voz, Vr, Recirc


def calc_Cbz_caseB(N, Voz, Co, R, Ef, Ez, Vr, Fr=1.0):
    """
    Steady-state breathing-zone concentration (Cbz) - ASHRAE 62.1 Table F-1, Case B.

    System types handled:
        - Constant outdoor air, constant volume (Fr = 1, R >= 0)
        - Constant outdoor air, VAV          (0 < Fr < 1, R > 0)
        - 100 % outdoor air, VAV             (0 < Fr < 1, R = 0)

    Parameters:
        N   : contaminant generation rate [ug/h]
        Voz : outdoor airflow used for this compound [m3/h]
        Co  : outdoor concentration [ug/m3]
        R   : recirculation flow factor (fraction)
        Ef  : filter efficiency (fraction)
        Ez  : zone air distribution effectiveness (fraction)
        Vr  : return (supply) airflow [m3/h]
        Fr  : design flow-reduction fraction (1.0 = constant volume)

    Returns:
        Cbz : breathing-zone concentration [ug/m3]
    """
    numerator = N + Ez * Voz * (1 - Ef) * Co

    if R == 0.0:  # 100 % outdoor air (no recirculation)
        numerator   = N + Ez * Fr * Voz * (1 - Ef) * Co  # add Fr for B VAV 100 %
        denominator = Ez * Fr * Voz
    else:         # outdoor air held constant (recirculation present)
        denominator = Ez * (Voz + Fr * R * Vr * Ef)

    if denominator == 0:
        raise ZeroDivisionError("Denominator is zero in Cbz calculation.")
    return numerator / denominator

