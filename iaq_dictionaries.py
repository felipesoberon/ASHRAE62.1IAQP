CFM_PER_M3H = 0.589


# Dictionary with compound names (case-insensitive), authority, value, and units
DESIGN_LIMITS = {
    "acetaldehyde":          {"authority": "Cal EPA CREL (June 2016)",        "limit": 140,   "units": "ug/m3"},
    "acetone":               {"authority": "AgBB LCI",                        "limit": 1200,  "units": "ug/m3"},
    "benzene":               {"authority": "Cal EPA CREL (June 2016)",        "limit": 3,     "units": "ug/m3"},
    "dichloromethane":       {"authority": "Cal EPA CREL (June 2016)",        "limit": 400,   "units": "ug/m3"},
    "formaldehyde":          {"authority": "Cal EPA 8-hour CREL (2004)",      "limit": 33,    "units": "ug/m3"},
    "naphthalene":           {"authority": "Cal EPA CREL (June 2016)",        "limit": 9,     "units": "ug/m3"},
    "phenol":                {"authority": "AgBB LCI",                        "limit": 70,    "units": "ug/m3"}, #changed from 10 ug/m3 in addendum q (31 Oct 2024)
    "tetrachloroethylene":   {"authority": "Cal EPA CREL (June 2016)",        "limit": 35,    "units": "ug/m3"},
    "toluene":               {"authority": "Cal EPA CREL (June 2016)",        "limit": 300,   "units": "ug/m3"},
   #"1,1,1-trichloroethane": {"authority": "Cal EPA CREL (June 2016)",        "limit": 1000,  "units": "ug/m3"}, removed in addendum q (31 Oct 2024)
    "xylene, total":         {"authority": "AgBB LCI",                        "limit": 500,   "units": "ug/m3"},
    "carbon monoxide":       {"authority": "U.S. EPA NAAQS",                  "limit": 9,     "units": "ppm"},    # ~10310 ug/m3 @25C,1 atm
    "pm2.5":                 {"authority": "U.S. EPA NAAQS (annual mean)",    "limit": 12,    "units": "ug/m3"},
    "ozone":                 {"authority": "U.S. EPA NAAQS",                  "limit": 70,    "units": "ppb"},    # ~137 ug/m3 @25C,1 atm
    "ammonia":               {"authority": "Cal EPA CREL (June 2016)",        "limit": 200,   "units": "ug/m3"},
}


def get_design_limit_ugm3(compound):
    """
    Returns the design limit for a compound in ug/m3, 
    converting from ppm or ppb if needed.
    """
    key = compound.strip().lower()
    info = DESIGN_LIMITS.get(key)
    if info is None:
        raise ValueError(f"No design limit found for '{compound}'.")
    limit = info["limit"]
    units = info["units"]
    authority = info["authority"]

    if units == "ug/m3":
        return limit, "ug/m3", authority
    elif units == "ppm":
        molar_mass = MOLAR_MASSES.get(key)
        if molar_mass is None:
            raise ValueError(f"Molar mass not found for '{compound}' (ppm to ug/m3)")
        # ug/m3 = ppm × (molar_mass / 24.45) × 1000
        limit_ugm3 = limit * (molar_mass / 24.45) * 1000
        return limit_ugm3, "ug/m3", authority
    elif units == "ppb":
        molar_mass = MOLAR_MASSES.get(key)
        if molar_mass is None:
            raise ValueError(f"Molar mass not found for '{compound}' (ppb to ug/m3)")
        # ug/m3 = ppb × (molar_mass / 24.45)
        limit_ugm3 = limit * (molar_mass / 24.45)
        return limit_ugm3, "ug/m3", authority
    else:
        raise ValueError(f"Unknown units '{units}' for design limit of '{compound}'")


OUTDOOR_CONCENTRATIONS = {
    "acetaldehyde":         (0.0, "ug/m3"),
    "acetone":              (0.0, "ug/m3"),
    "benzene":              (0.0, "ug/m3"),
    "dichloromethane":      (0.0, "ug/m3"),
    "formaldehyde":         (0.0, "ug/m3"),
    "naphthalene":          (0.0, "ug/m3"),
    "phenol":               (0.0, "ug/m3"),
    "tetrachloroethylene":  (0.0, "ug/m3"),
    "toluene":              (0.0, "ug/m3"),
    "1,1,1-trichloroethane":(0.0, "ug/m3"),
    "xylene, total":        (0.0, "ug/m3"),
    "carbon monoxide":      (1, "ppm"),      # convert to ug/m3 if needed
    "pm2.5":                (10, "ug/m3"),
    "ozone":                (50, "ppb"),     # convert to ug/m3 if needed
    "ammonia":              (0.0, "ug/m3"),
}



# Molar masses (g/mol) for each compound needing conversion
MOLAR_MASSES = {
    "carbon monoxide": 28.01,
    "ozone": 48.00,
    # Add more if you expect others in ppm/ppb
}

def get_outdoor_concentration_ugm3(compound, temp_C=25, pressure_atm=1.0):
    """
    Retrieve the outdoor concentration for a compound in ug/m3,
    converting from ppm or ppb if needed (at standard conditions).
    """
    compound_lc = compound.strip().lower()
    if compound_lc not in OUTDOOR_CONCENTRATIONS:
        raise ValueError(f"Outdoor concentration not defined for '{compound}'")
    val, units = OUTDOOR_CONCENTRATIONS[compound_lc]

    if units == "ug/m3":
        return val
    elif units == "ppm":
        # ug/m3 = ppm × (molar_mass / 24.45) × 1000
        molar_mass = MOLAR_MASSES.get(compound_lc)
        if molar_mass is None:
            raise ValueError(f"Molar mass not found for conversion of '{compound}' (ppm to ug/m3)")
        return val * (molar_mass / 24.45) * 1000
    elif units == "ppb":
        # ug/m3 = ppb × (molar_mass / 24.45)
        molar_mass = MOLAR_MASSES.get(compound_lc)
        if molar_mass is None:
            raise ValueError(f"Molar mass not found for conversion of '{compound}' (ppb to ug/m3)")
        return val * (molar_mass / 24.45)
    else:
        raise ValueError(f"Unknown units '{units}' for outdoor concentration of '{compound}'")




emission_rates_ug_m2_h = {
    "Art classroom": {
        "Acetaldehyde": 16.5,
        "Acetone": 37.70,
        "Benzene": 0.21,
        "Dichloromethane": 1.18,
        "Formaldehyde": 59.2,
        "Naphthalene": 0.38,
        "Phenol": 6.25,
        "Tetrachloroethylene": 0.14,
        "Toluene": 3.84,
        "1,1,1-trichloroethane": 0.12,
        "Xylene, total": 3.13
    },
    "Bars, cocktail lounges": {
        "Acetaldehyde": 260.0,
        "Acetone": 57.20,
        "Benzene": 3.14,
        "Dichloromethane": 2.95,
        "Formaldehyde": 65.1,
        "Naphthalene": 0.24,
        "Phenol": 4.32,
        "Tetrachloroethylene": 0.24,
        "Toluene": 10.20,
        "1,1,1-trichloroethane": 0.11,
        "Xylene, total": 3.72
    },
    "Cafeteria/fast-food dining": {
        "Acetaldehyde": 260.0,
        "Acetone": 57.20,
        "Benzene": 3.14,
        "Dichloromethane": 2.95,
        "Formaldehyde": 65.1,
        "Naphthalene": 0.24,
        "Phenol": 4.32,
        "Tetrachloroethylene": 0.24,
        "Toluene": 10.20,
        "1,1,1-trichloroethane": 0.11,
        "Xylene, total": 3.72
    },
    "Classrooms (age 9 plus)": {
        "Acetaldehyde": 16.5,
        "Acetone": 37.70,
        "Benzene": 0.21,
        "Dichloromethane": 1.18,
        "Formaldehyde": 59.2,
        "Naphthalene": 0.38,
        "Phenol": 6.25,
        "Tetrachloroethylene": 0.14,
        "Toluene": 3.84,
        "1,1,1-trichloroethane": 0.12,
        "Xylene, total": 3.13
    },
    "Classrooms (ages 5–8)": {
        "Acetaldehyde": 16.5,
        "Acetone": 37.70,
        "Benzene": 0.21,
        "Dichloromethane": 1.18,
        "Formaldehyde": 59.2,
        "Naphthalene": 0.38,
        "Phenol": 6.25,
        "Tetrachloroethylene": 0.14,
        "Toluene": 3.84,
        "1,1,1-trichloroethane": 0.12,
        "Xylene, total": 3.13
    },
    "Dental operatory": {
        "Acetaldehyde": 25.90,
        "Acetone": 433.00,
        "Benzene": 0.51,
        "Dichloromethane": 0.51,
        "Formaldehyde": 54.90,
        "Naphthalene": 0.46,
        "Phenol": 6.21,
        "Tetrachloroethylene": 1.82,
        "Toluene": 7.63,
        "1,1,1-trichloroethane": 0.18,
        "Xylene, total": 12.80
    },
    "General examination room": {
        "Acetaldehyde": 25.90,
        "Acetone": 433.00,
        "Benzene": 0.51,
        "Dichloromethane": 0.51,
        "Formaldehyde": 54.90,
        "Naphthalene": 0.46,
        "Phenol": 6.21,
        "Tetrachloroethylene": 1.82,
        "Toluene": 7.63,
        "1,1,1-trichloroethane": 0.18,
        "Xylene, total": 12.80
    },
    "Health club/aerobics room": {
        "Acetaldehyde": 14.10,
        "Acetone": 75.60,
        "Benzene": 1.59,
        "Dichloromethane": 0.99,
        "Formaldehyde": 60.80,
        "Naphthalene": 0.46,
        "Phenol": 1.44,
        "Tetrachloroethylene": 0.27,
        "Toluene": 8.55,
        "1,1,1-trichloroethane": 0.00,
        "Xylene, total": 4.43
    },
    "Health club/weight rooms": {
        "Acetaldehyde": 14.10,
        "Acetone": 75.60,
        "Benzene": 1.59,
        "Dichloromethane": 0.99,
        "Formaldehyde": 60.80,
        "Naphthalene": 0.46,
        "Phenol": 1.44,
        "Tetrachloroethylene": 0.27,
        "Toluene": 8.55,
        "1,1,1-trichloroethane": 0.00,
        "Xylene, total": 4.43
    },
    "Office space": {
        "Acetaldehyde": 22.10,
        "Acetone": 37.70,
        "Benzene": 0.21,
        "Dichloromethane": 1.18,
        "Formaldehyde": 37.50,
        "Naphthalene": 0.38,
        "Phenol": 6.25,
        "Tetrachloroethylene": 0.14,
        "Toluene": 3.84,
        "1,1,1-trichloroethane": 0.12,
        "Xylene, total": 3.13
    },
    "Reception areas": {
        "Acetaldehyde": 57.20,
        "Acetone": 3.14,
        "Benzene": 2.95,
        "Dichloromethane": 65.1,
        "Formaldehyde": 0.24,
        "Naphthalene": 4.32,
        "Phenol": 0.24,
        "Tetrachloroethylene": 10.20,
        "Toluene": 0.11,
        "1,1,1-trichloroethane": 3.72
    },
    "Restaurant dining rooms": {
        "Acetaldehyde": 260.00,
        "Acetone": 57.20,
        "Benzene": 3.14,
        "Dichloromethane": 2.95,
        "Formaldehyde": 65.10,
        "Naphthalene": 0.24,
        "Phenol": 4.32,
        "Tetrachloroethylene": 0.24,
        "Toluene": 10.20,
        "1,1,1-trichloroethane": 0.11,
        "Xylene, total": 3.72
    },
    "Sales (except as below)": {
        "Acetaldehyde": 14.80,
        "Acetone": 50.9,
        "Benzene": 0.41,
        "Dichloromethane": 0.66,
        "Formaldehyde": 83.2,
        "Naphthalene": 1.06,
        "Phenol": 3.40,
        "Tetrachloroethylene": 1.40,
        "Toluene": 32.70,
        "1,1,1-trichloroethane": 0.28,
        "Xylene, total": 11.14
    }
    # Add more as needed...
}






def get_emission_rates_for_occupancy(occupancy, area_m2):
    """
    Returns {compound: emission_rate_ug_per_hour} for given occupancy and area.
    If occupancy not found, returns all compounds as zero and prints a warning.
    """
    rates = emission_rates_ug_m2_h.get(occupancy)
    if not rates:
        print(f"Warning: Occupancy '{occupancy}' not found in area emission rates dictionary. Setting all area emission rates to zero.")
        return {comp: 0.0 for comp in DESIGN_LIMITS.keys()}
    # Multiply each per-m2 rate by the area
    return {comp: rate * area_m2 for comp, rate in rates.items()}










MIXTURE_GROUPS = {
    "Upper Respiratory Tract Irritation": [
        "acetaldehyde", "acetone", "xylene, total", "ozone"
    ],
    "Eye Irritation": [
        "acetaldehyde", "acetone", "formaldehyde", "xylene, total", "ozone"
    ],
    "Central Nervous System": [
        "acetone", "dichloromethane", "xylene, total", "1,1,1-trichloroethane", "toluene"
    ]
}


def calculate_mixture_exposure(summary):
    """
    Calculates the mixed exposure sum for each group in MIXTURE_GROUPS.

    Parameters:
        summary: list of dicts, each with at least:
            'compound', 'Cbz', 'limit' (all normalized to ug/m3).

    Returns:
        dict: {group_name: mixed_exposure_sum}
    """
    # Quick lookup for Cbz and limit by normalized compound name
    cbz_dict = {row['compound'].strip().lower(): row['Cbz'] for row in summary}
    limit_dict = {row['compound'].strip().lower(): row['limit'] for row in summary}

    results = {}
    for group, compounds in MIXTURE_GROUPS.items():
        cbz_sum = 0.0
        limit_sum = 0.0
        for compound in compounds:
            cname = compound.strip().lower()
            cbz = cbz_dict.get(cname)
            limit = limit_dict.get(cname)
            if cbz is not None and limit is not None:
                cbz_sum += cbz
                limit_sum += limit
        if limit_sum > 0:
            results[group] = cbz_sum / limit_sum
        else:
            results[group] = float('nan')
    return results


human_occupant_emission_rates = {
    "Acetaldehyde": {"CAS": "75-07-0", "emission_rate_ug_hr_person": 114},
    "Acetone": {"CAS": "67-64-1", "emission_rate_ug_hr_person": 1060},
    "Toluene": {"CAS": "108-88-3", "emission_rate_ug_hr_person": 7.7},
    "Carbon monoxide": {"CAS": "630-08-0", "emission_rate_ug_hr_person": 560},
    "Ammonia": {"CAS": "7664-41-7", "emission_rate_ug_hr_person": 1342},

    #The compounds below are not in the design compounds of the IAQP 62.1 2022
    "Carbon dioxide": {"CAS": "124-38-9", "emission_rate_ug_hr_person": 32_800_000},
    "Hydrogen sulfide": {"CAS": "7783-06-4", "emission_rate_ug_hr_person": 119},
    "Decamethylcyclopentasiloxane (D5)": {"CAS": "541-02-6", "emission_rate_ug_hr_person": 3350},
    "Acetic acid": {"CAS": "64-19-7", "emission_rate_ug_hr_person": 329},
    "Isoprene": {"CAS": "78-79-5", "emission_rate_ug_hr_person": 162},
    "Methanol": {"CAS": "67-56-1", "emission_rate_ug_hr_person": 156},
    "Dodecamethylcyclohexasiloxane (D6)": {"CAS": "540-97-6", "emission_rate_ug_hr_person": 105},
    "6-Methyl-5-hepten-2-one": {"CAS": "110-93-0", "emission_rate_ug_hr_person": 99.3},
    "Ethanol": {"CAS": "64-17-5", "emission_rate_ug_hr_person": 94.9},
    "Formic acid": {"CAS": "64-18-6", "emission_rate_ug_hr_person": 48.5},
    "Propionic acid/hydroxyacetone": {"CAS": "79-09-4 / 116-09-6", "emission_rate_ug_hr_person": 40.4},
    "4-oxopentanal": {"CAS": "626-96-0", "emission_rate_ug_hr_person": 36.9},
    "Octamethylcyclotetrasiloxane (D4)": {"CAS": "556-67-2", "emission_rate_ug_hr_person": 21}
}


def get_human_occupant_emission_rates(num_people, compounds=None):
    """
    Returns a dict of {compound: emission_rate_ug_per_hour} for given number of people.
    If compounds is provided, limits output to those compounds (case-insensitive).
    """
    out = {}
    # Normalize for case-insensitive matching
    keys_needed = [k.lower() for k in compounds] if compounds else None

    for name, data in human_occupant_emission_rates.items():
        if (not compounds) or (name.lower() in keys_needed):
            out[name] = data["emission_rate_ug_hr_person"] * num_people
    return out


VRP_TABLE_6_1 = {
    # Animal Facilities
    "Animal exam room (veterinary office)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal imaging (MRI/CT/PET)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal operating rooms": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal postoperative recovery room": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal preparation rooms": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal procedure room": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Animal surgery scrub": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Large-animal holding room": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Necropsy": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Small-animal-cage room (static cages)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Small-animal-cage room (ventilated cages)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },

    # Correctional Facilities
    "Booking/waiting": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 50, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": None
    },
    "Cell": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Dayroom": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 30, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": None
    },
    "Guard stations": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 15, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": None
    },

    # Educational Facilities
    "Art classroom": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Classrooms (ages 5–8)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Classrooms (age 9 plus)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 35, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": None
    },
    "Computer lab": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": None
    },
    "Daycare sickroom": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Daycare (through age 4)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Lecture classroom": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 65, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Lecture hall (fixed seats)": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 150, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Libraries": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": None
    },
    "Media center": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": None
    },
    "Multiuse assembly": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 100, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Music/theater/dance": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 35, "DeltaC_ppm": 2100, "Occupied_Standby_Allowed": "YES"
    },
    "Science laboratories": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "University/college laboratories": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Wood/metal shop": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Corridors (ages 5 plus)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },

    # Food and Beverage Service
    "Bars, cocktail lounges": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 100, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": None
    },
    "Cafeteria/fast-food dining": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 100, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Kitchen (cooking)": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Restaurant dining rooms": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 70, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": None
    },

    # General
    "Break rooms (General)": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Coffee stations": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Conference/meeting": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 50, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Corridors": {
        "Rp_cfm_per": 0, "Rp_Lps_per": 0, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": None, "Occupied_Standby_Allowed": "YES"
    },
    "Occupiable storage rooms for liquids or gels": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 2, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },

    # Hotels, Motels, Resorts, Dormitories
    "Barracks sleeping areas": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": "YES"
    },
    "Bedroom/living room": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": "YES"
    },
    "Laundry rooms, central": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Laundry rooms within dwelling units": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Lobbies/prefunction": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 30, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Multipurpose assembly": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 120, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },

    # Miscellaneous Spaces
    "Banks or bank lobbies": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 15, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": "YES"
    },
    "Bank vaults/safe deposit": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 5, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": "YES"
    },
    "Computer (not printing)": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 4, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": "YES"
    },
    "Freezer and refrigerated spaces (<50°F [10°C])": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0, "Ra_Lps_m2": 0, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Manufacturing where hazardous materials are not used": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 7, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": None
    },
    "Manufacturing where hazardous materials are used (excludes heavy industrial and chemical processes)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 7, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Pharmacy (prep. area)": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Photo studios": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Shipping/receiving": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 2, "DeltaC_ppm": 700, "Occupied_Standby_Allowed": None
    },
    "Sorting, packing, light assembly": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 7, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Telephone closets": {
        "Rp_cfm_per": 0, "Rp_Lps_per": 0, "Ra_cfm_ft2": 0, "Ra_Lps_m2": 0, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": 700, "Occupied_Standby_Allowed": None
    },
    "Transportation waiting": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 100, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },
    "Warehouses": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": 700, "Occupied_Standby_Allowed": None
    },

    # Office Buildings
    "Main entry lobbies": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": "YES"
    },
    "Occupiable storage rooms for dry materials": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 2, "DeltaC_ppm": 700, "Occupied_Standby_Allowed": None
    },
    "Office space": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 5, "DeltaC_ppm": 600, "Occupied_Standby_Allowed": "YES"
    },
    "Reception areas": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 30, "DeltaC_ppm": 2100, "Occupied_Standby_Allowed": "YES"
    },
    "Telephone/data entry": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 60, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },

    # Public Assembly Spaces
    "Auditorium seating area": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 150, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },
    "Courtrooms": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 70, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Legislative chambers": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 50, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },
    "Lobbies": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 150, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },
    "Museums (children’s)": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 40, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": None
    },
    "Museums/galleries": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 40, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Places of religious worship": {
        "Rp_cfm_per": 5, "Rp_Lps_per": 2.5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 120, "DeltaC_ppm": 1800, "Occupied_Standby_Allowed": "YES"
    },

    # Residential
    "Common corridors": {
        "Rp_cfm_per": 0, "Rp_Lps_per": 0, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": None, "Occupied_Standby_Allowed": "YES"
    },

    # Retail
    "Sales (except as below)": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 15, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Barbershop": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": "YES"
    },
    "Beauty and nail salons": {
        "Rp_cfm_per": 20, "Rp_Lps_per": 10, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 25, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Coin-operated laundries": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Mall common areas": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 40, "DeltaC_ppm": 2100, "Occupied_Standby_Allowed": "YES"
    },
    "Pet shops (animal areas)": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },
    "Supermarket": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 8, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Bowling alley (seating)": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.12, "Ra_Lps_m2": 0.6, "Default_Occ_Density_per_1000ft2": 40, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },

    # Sports and Entertainment
    "Disco/dance floors": {
        "Rp_cfm_per": 20, "Rp_Lps_per": 10, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 100, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Gambling casinos": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 120, "DeltaC_ppm": 1200, "Occupied_Standby_Allowed": None
    },
    "Game arcades": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 20, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Gym, sports arena (play area)": {
        "Rp_cfm_per": 20, "Rp_Lps_per": 10, "Ra_cfm_ft2": 0.18, "Ra_Lps_m2": 0.9, "Default_Occ_Density_per_1000ft2": 7, "DeltaC_ppm": 900, "Occupied_Standby_Allowed": None
    },
    "Health club/aerobics room": {
        "Rp_cfm_per": 20, "Rp_Lps_per": 10, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 40, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": None
    },
    "Health club/weight rooms": {
        "Rp_cfm_per": 20, "Rp_Lps_per": 10, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 10, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": None
    },
    "Spectator areas": {
        "Rp_cfm_per": 7.5, "Rp_Lps_per": 3.8, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 150, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Stages, studios": {
        "Rp_cfm_per": 10, "Rp_Lps_per": 5, "Ra_cfm_ft2": 0.06, "Ra_Lps_m2": 0.3, "Default_Occ_Density_per_1000ft2": 70, "DeltaC_ppm": 1500, "Occupied_Standby_Allowed": "YES"
    },
    "Swimming (pool & deck)": {
        "Rp_cfm_per": 0, "Rp_Lps_per": 0, "Ra_cfm_ft2": 0.48, "Ra_Lps_m2": 2.4, "Default_Occ_Density_per_1000ft2": 0, "DeltaC_ppm": None, "Occupied_Standby_Allowed": None
    },

    
    # Outpatient Health Care Facilities (ASHRAE 62.1 Table P-1)
    "Birthing room": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.18,
        "Default_Occ_Density_per_1000ft2": 15,
        "Notes": "Outpatient health care"
    },
    "Class 1 imaging rooms": {
        "Rp_cfm_per": 7.5,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 5,
        "Notes": "Outpatient health care"
    },
    "Dental operatory": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.18,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "General examination room": {
        "Rp_cfm_per": 7.5,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Other dental treatment areas": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 5,
        "Notes": "Outpatient health care"
    },
    "Physical therapy exercise area": {
        "Rp_cfm_per": 20.0,
        "Ra_cfm_ft2": 0.18,
        "Default_Occ_Density_per_1000ft2": 7,
        "Notes": "Outpatient health care"
    },
    "Physical therapy individual room": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Physical therapeutic pool area": {
        "Rp_cfm_per": None,   # not given
        "Ra_cfm_ft2": 0.48,
        "Default_Occ_Density_per_1000ft2": None,
        "Notes": "Outpatient health care"
    },
    "Prosthetics and orthotics room": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.18,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Psychiatric consultation room": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Psychiatric examination room": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Psychiatric group room": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 50,
        "Notes": "Outpatient health care"
    },
    "Psychiatric seclusion room": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 5,
        "Notes": "Outpatient health care"
    },
    "Speech therapy room": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Urgent care examination room": {
        "Rp_cfm_per": 7.5,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Urgent care observation room": {
        "Rp_cfm_per": 5.0,
        "Ra_cfm_ft2": 0.06,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Urgent care treatment room": {
        "Rp_cfm_per": 7.5,
        "Ra_cfm_ft2": 0.12,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    },
    "Urgent care triage room": {
        "Rp_cfm_per": 10.0,
        "Ra_cfm_ft2": 0.18,
        "Default_Occ_Density_per_1000ft2": 20,
        "Notes": "Outpatient health care"
    }
        
} # -- End of VRP_TABLE_6_1 --
