#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from math import ceil
import argparse


from iaq_dictionaries import (
    CFM_PER_M3H,
    DESIGN_LIMITS,
    get_design_limit_ugm3,
    OUTDOOR_CONCENTRATIONS,
    get_outdoor_concentration_ugm3,
    emission_rates_ug_m2_h,
    get_emission_rates_for_occupancy,
    MOLAR_MASSES,
    MIXTURE_GROUPS, 
    calculate_mixture_exposure,
    VRP_TABLE_6_1,
    get_human_occupant_emission_rates
)


from mass_balance import calc_Voz, calc_Cbz
from air_cleaner   import get_cleaner_efficiency




def main(**p):
    """
    All inputs now come straight from CLI arguments.
    Missing keys fall back to the defaults dict below.
    """
    defaults = {
        "Ef":          0.5,
        "Ez":          1.0,
        "units":       "BOTH",
        "safe_factor": 1.0,
    }

    for k, v in defaults.items():
        p.setdefault(k, v)

    R   = float(p.get("R", 0.0))              
    Ez  = float(p["Ez"])
    Ef_global = float(p["Ef"])  
    
    loc = p.get("loc", "A").strip().upper()
    if loc not in ("A", "B"):
        print("Unrecognized filter_loc; defaulting to A.")
        loc = "A"
        
    units = p.get("units", "both").strip().upper()
    if units not in ("CFM", "CMH", "BOTH"):
        print("Unrecognized units specified; defaulting to BOTH (CMH/CFM).")
        units = "BOTH"

    area_m2 = float(p.get("area_m2", 1))
    area_ft2 = area_m2 * 10.7639
    
    
    if "area_m2" in p:
        area_m2  = float(p["area_m2"])
    elif "area_ft2" in p:
        area_m2  = float(p["area_ft2"]) / 10.7639
    else:
        area_m2  = 90.0   # default
    area_ft2 = area_m2 * 10.7639
    
    
    occupancy = p.get("occupancy", "Classrooms (age 9 plus)")
    safe_factor = float(p.get("safe_factor", 1.0))
    if safe_factor > 1:
        raise ValueError("safe_factor must be <= 1.")


    if "num_people" in p:
        num_people = int(float(p["num_people"]))
    else:
        occ_row = VRP_TABLE_6_1[occupancy]
        density = occ_row.get("Default_Occ_Density_per_1000ft2", 0)
        if not density:
            raise ValueError(f"Default occupant density not available for '{occupancy}'.")
        num_people = ceil(density * area_ft2 / 1000)


    recirc_flow = None                       # m3/h
    if "Recirc_CFM" in p and p["Recirc_CFM"] is not None:
        recirc_flow = float(p["Recirc_CFM"]) / CFM_PER_M3H
    elif "Recirc_CMH" in p and p["Recirc_CMH"] is not None:
        recirc_flow = float(p["Recirc_CMH"])




    # Print the input information
    print("\n--- Scenario Summary ---\n")
    print(f"{'Parameter':<25} | {'Value':>15} | {'Units'}")
    print("-" * 50)
    print(f"{'Occupancy Category':<25} | {occupancy:>15} |")
    print(f"{'Area':<25} | {area_m2:15.2f} | m2")
    print(f"{'Area':<25} | {area_ft2:15.2f} | ft2")
    print(f"{'Number of People':<25} | {num_people:15d} | persons")
    if recirc_flow is None:
        print(f"{'Recirculation (R)':<25} | {R:15.2f} | (fraction)")
    if recirc_flow is not None:
        print(f"{'Recirc airflow':<25} | {recirc_flow*CFM_PER_M3H:15.2f} | CFM")
        print(f"{'Recirc airflow':<25} | {recirc_flow:15.2f} | m3/h")        
    print(f"{'Filter Efficiency (Ef)':<25} | {Ef_global:15.2f} | (fraction)")
    print(f"{'Filter Location':<25} | {loc:>15} |")
    print(f"{'Ez':<25} | {Ez:15.2f} | (zone air dist. eff.)")
    print(f"{'Units':<25} | {units:>15} |")
    print(f"{'Safe Factor':<25} | {safe_factor:15.2f} | (<= 1)")
    print("-" * 50)
    print()





    # Compute emission rates
    try:
        # Area-based emissions
        rates = get_emission_rates_for_occupancy(occupancy, area_m2)
    except Exception as e:
        print(e)
        return

    # Per-person (human) emission rates for relevant compounds
    human_emissions = get_human_occupant_emission_rates(num_people, DESIGN_LIMITS.keys())

    summary = []
    for compound in DESIGN_LIMITS.keys():
        # Start with zero
        N = 0.0

        # Add area-based emissions if present
        for em_comp in rates:
            if em_comp.strip().lower() == compound.strip().lower():
                N = rates[em_comp]
                break

        # Add per-person (human) emissions if present
        for h_comp in human_emissions:
            if h_comp.strip().lower() == compound.strip().lower():
                N += human_emissions[h_comp]
                break

        d_info = DESIGN_LIMITS.get(compound)
        if d_info is None:
            continue
        Cbz, units_out, _ = get_design_limit_ugm3(compound)
        Cbz = Cbz * safe_factor
        Co_c = float('nan')
        try:
            Co_c = get_outdoor_concentration_ugm3(compound)
            
            # choose an efficiency for this compound
            if Ef_global == 0:
                Ef_c = 0.0
            else:
                try:
                    Ef_c = get_cleaner_efficiency(compound)
                except KeyError:
                    Ef_c = Ef_global  # fall back to the global value            
            
            Voz, Vr, Recirc = calc_Voz(N, Co_c, Cbz, R, Ef_c, Ez, loc=loc)
            summary.append({
                "compound": compound,
                "N": N,
                "limit": Cbz,
                "units": units_out,      # always ug/m3
                "Co": Co_c,
                "Voz": Voz,
                "Voz_CFM": Voz * CFM_PER_M3H,
                "Ef": Ef_c,
                "Cbz": Cbz,
            })
        except Exception as e:
            summary.append({
                "compound": compound,
                "N": N,
                "limit": Cbz,
                "units": units_out,
                "Co": Co_c,
                "Voz": None,
                "Voz_CFM": None,
                "Ef": Ef_c,
                "Cbz": Cbz,
                "error": str(e),
            })




    print(f"\n=== Required Airflow by Compound for '{occupancy}' (area = {area_m2} m2) ===\n")
    header = (
        f"{'Compound':<25} | {'N (ug/h)':>10} | "
        f"{'Safe Limit (ug/m3)':>18} | {'Outdoor (ug/m3)':>16} | "
        f"{'Voz (m3/h)':>12} | {'Voz (CFM)':>10}"
    )
    print(header)                          

    print("-" * len(header))
    for r in summary:
        if r["Voz"] is not None:
            print(f"{r['compound']:<25} | {r['N']:10.2f} | {r['limit']:18.2f} | "f"{r['Co']:16.2f} | {r['Voz']:12.2f} | {r['Voz_CFM']:10.2f}")
        else:
            error_message = r.get('error', '')
            explanation = "Outdoor > limit" if "Denominator" in error_message and "<= 0" in error_message else "ERROR"
            print(f"{r['compound']:<25} | {r['N']:10.2f} | {r['limit']:18.2f} | "f"{r['Co']:16.2f} | {explanation:>12} | {explanation:>10}")
    print()



    # Calculate maximum Voz and corresponding Vr
    voz_vals = [r['Voz'] for r in summary if r['Voz'] is not None]
    if not voz_vals:
        print("No valid Voz values found.")
    else:
        
        max_voz = max(voz_vals)

        if recirc_flow is not None and (max_voz + recirc_flow) > 0:
            R = recirc_flow / (max_voz + recirc_flow)

        max_vr = max_voz / (1 - R) if R < 1 else float('inf')        
        
        

        # Now output the Cbz table with colored values
        print(f"\n=== Calculated Breathing Zone Concentration (Cbz) for Each Compound Using Maximum Voz = {max_voz:.2f} m3/h ===\n")

        header = (
            f"{'Compound':<25} | {'N (ug/h)':>10} | {'Outdoor (ug/m3)':>16} | "
            f"{'Cbz (ug/m3)':>14} | {'Design Limit (ug/m3)':>20} | {'% Limit':>8}"
        )
        
        print(header)
        print("-" * len(header))
        for r in summary:
            try:
                cbz = calc_Cbz(
                    N=r['N'],
                    Voz=max_voz,
                    Co=r['Co'],
                    R=R,
                    Ef=r['Ef'],
                    Ez=Ez,
                    Vr=max_vr,
                    loc=loc
                )
                r['Cbz'] = cbz  
                design_limit, _, _ = get_design_limit_ugm3(r['compound'])
                
                cbz_str = f"{cbz:14.2f}"
                
                pct = 100.0 * cbz / design_limit if design_limit > 0 else 0.0
                
                print(
                    f"{r['compound']:<25} | {r['N']:10.2f} | {r['Co']:16.2f} | "
                    f"{cbz_str} | {design_limit:20.2f} | {pct:8.1f}"
                )
 
            except Exception as e:
                r['Cbz'] = float('nan')  # Optionally store NaN if failed
                
                print(
                    f"{r['compound']:<25} | {r['N']:10.2f} | {r['Co']:16.2f} | "
                    f"{'ERROR':>14} | {'ERROR':>20} | {'ERROR':>8}"
                )

        print()


    print("\n=== Mixed Exposure Sum ===")
    mixture_sums = calculate_mixture_exposure(summary)
    for group, value in mixture_sums.items():
        print(f"{group:35} : {value:.3f}")
    print()



    # Find the final Voz used (max of all valid Voz)
    voz_vals = [r['Voz'] for r in summary if r['Voz'] is not None]
    if voz_vals:
        final_voz_cmh = max(voz_vals)
        final_voz_cfm = final_voz_cmh * CFM_PER_M3H
        Vr = final_voz_cmh / (1 - R) if R < 1 else float('inf')
        Recirc = R * Vr
        Total_flow = final_voz_cmh + Recirc
        Recirc_CFM = Recirc * CFM_PER_M3H
        Total_CFM = Total_flow * CFM_PER_M3H

        # Calculate percentage
        pct_outdoor = 100 * final_voz_cmh / Total_flow if Total_flow > 0 else 0

        print("\n=== Final Airflows Used in Zone Calculations ===")
        print(f"{'Parameter':<28} | {'Value (CFM)':>15} | {'Value (m3/h)':>15}")
        print("-" * 62)
        print(f"{'Voz (outdoor airflow)':<28} | {final_voz_cfm:15.2f} | {final_voz_cmh:15.2f}")
        print(f"{'R x Vr (recirc airflow)':<28} | {Recirc_CFM:15.2f} | {Recirc:15.2f}")
        print(f"{'Total to zone (Voz+Recirc)':<28} | {Total_CFM:15.2f} | {Total_flow:15.2f}")
        print(f"{'Outdoor % of Total':<28} | {pct_outdoor:13.1f} % | {pct_outdoor:14.1f} %")
        print("-" * 62)
    else:
        print("\nNo valid Voz values found for summary table.")






#if __name__ == "__main__":
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASHRAE 62.1 IAQP Console Calculator")
    parser.add_argument("-Ez", type=float, help="Zone air distribution effectiveness")
    parser.add_argument("-Ef", type=float, help="Filter efficiency")
    parser.add_argument("-R", type=float, help="Recirculation factor")
    parser.add_argument("-area_m2", type=float, help="Area in square meters")
    parser.add_argument("-area_ft2", type=float, help="Area in square feet")
    parser.add_argument("-occupancy", type=str, help="Occupancy category")
    parser.add_argument("-safe_factor", type=float, help="Safety factor (<=1)")
    parser.add_argument("-num_people", type=int, help="Number of people")
    parser.add_argument("-units", type=str, help="Units (CFM, CMH, BOTH)")
    parser.add_argument("-loc", type=str, help="Filter location (A or B)")
    parser.add_argument("-Recirc_CFM", type=float,   help="Recirculation airflow (CFM)")
    parser.add_argument("-Recirc_CMH", type=float,  help="Recirculation airflow (m3/h)")



    args = parser.parse_args()
    # Build a dict with CLI arguments that are not None
    p = {k: v for k, v in vars(args).items() if v is not None}
    main(**p) 