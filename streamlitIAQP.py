"""
streamlitIAQP.py
=================

This Streamlit application provides an interactive interface to the
Indoor Air Quality Procedure (IAQP) calculator originally implemented
as a console script.  Users can specify building and system
parameters – such as occupancy type, floor area, number of people,
recirculation settings, filter efficiency and location, and zone air
distribution effectiveness – and the app computes:

  * The contaminant generation rates for each design compound
    (ug/h).
  * The minimum outdoor airflow required to meet a given breathing
    zone concentration limit for each compound (m3/h and CFM).
  * The breathing zone concentrations achieved using the worst‑case
    airflow across all compounds and the associated percentage of the
    design limit.
  * Mixture exposure sums for different health effect groups.
  * Summary of the final outdoor and recirculated airflows used in the
    calculations.

The app reproduces the logic of the accompanying console program
(`mainIAQPconsole.py`) but presents the results in neatly formatted
tables and provides input widgets for all adjustable parameters.  It
also includes basic error handling to guide the user when inputs are
invalid (for example, a safety factor greater than 1).

The code is intentionally kept simple and uses only ASCII characters
to avoid encoding issues.  Tables are displayed using Pandas
DataFrames via `st.dataframe` for clarity, and warnings or errors
raised by the underlying calculation functions are surfaced to the
user as `st.warning` or `st.error` messages.
"""

import math
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

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
    get_human_occupant_emission_rates,
)

from mass_balance import calc_Voz, calc_Cbz
from air_cleaner import get_cleaner_efficiency


def compute_summary(
    occupancy: str,
    area_m2: float,
    num_people: Optional[int],
    safe_factor: float,
    recirc_factor: Optional[float],
    recirc_flow_cfm: Optional[float],
    recirc_flow_cmh: Optional[float],
    global_Ef: float,
    loc: str,
    Ez: float,
    units: str,
) -> Dict[str, any]:
    """
    Perform the IAQP calculations and return a dictionary containing
    intermediate tables and results.  If any error is encountered
    during processing (for example, unknown occupancy), an exception
    will be raised to be handled by the caller.

    Parameters
    ----------
    occupancy : str
        The occupancy category (must match keys in VRP_TABLE_6_1 to
        compute default occupant density).
    area_m2 : float
        Area of the zone in square metres.
    num_people : Optional[int]
        If provided and greater than zero, overrides the default
        occupant density and number of people.  If None or zero, the
        default density from VRP_TABLE_6_1 is used.
    safe_factor : float
        Safety factor applied to design limits (must be <= 1.0).
    recirc_factor : Optional[float]
        The recirculation fraction R (0-1).  If recirc_flow_cfm or
        recirc_flow_cmh is provided instead, this argument is ignored.
    recirc_flow_cfm : Optional[float]
        Recirculated airflow specified in CFM (cubic feet per minute).
    recirc_flow_cmh : Optional[float]
        Recirculated airflow specified in m3/h (cubic metres per hour).
    global_Ef : float
        Global filter efficiency (fraction between 0 and 1).
    loc : str
        Filter location ('A' or 'B').
    Ez : float
        Zone air distribution effectiveness.
    units : str
        One of 'CFM', 'CMH' or 'BOTH'.  Determines which columns are
        shown in the final table.

    Returns
    -------
    dict
        A dictionary containing the following keys:
            summary_table : pd.DataFrame
                Required outdoor airflow by compound.
            cbz_table : pd.DataFrame
                Breathing zone concentrations for each compound using
                the maximum Voz.
            mixture_table : pd.DataFrame
                Mixed exposure sums by group.
            final_flows_table : pd.DataFrame
                Final outdoor and recirculated airflows summary.
            scenario_summary : pd.DataFrame
                A simple table summarising the input scenario.
    """

    # Validate safety factor
    if safe_factor > 1.0:
        raise ValueError("Safe factor must be <= 1.0")

    # Normalise filter location and units
    loc = str(loc).strip().upper() or 'A'
    if loc not in ('A', 'B'):
        loc = 'A'

    units = str(units).strip().upper() or 'BOTH'
    if units not in ('CFM', 'CMH', 'BOTH'):
        units = 'BOTH'

    # Convert area from ft2 to m2 if necessary (not needed here since
    # streamlit collects only m2).  Keep area_ft2 for occupant density.
    area_ft2 = area_m2 * 10.7639

    # Determine number of people
    if num_people is not None and num_people > 0:
        num_people_used = int(num_people)
    else:
        occ_row = VRP_TABLE_6_1.get(occupancy)
        if not occ_row:
            raise ValueError(
                f"Default occupant density not available for occupancy '{occupancy}'"
            )
        density = occ_row.get('Default_Occ_Density_per_1000ft2', 0)
        if density <= 0:
            raise ValueError(
                f"Non‑positive occupant density found for occupancy '{occupancy}'"
            )
        num_people_used = int(math.ceil(density * area_ft2 / 1000.0))

    # Compute recirculation flow if provided in CFM or CMH
    recirc_flow_m3h: Optional[float] = None
    if recirc_flow_cfm is not None and recirc_flow_cfm > 0:
        recirc_flow_m3h = recirc_flow_cfm / CFM_PER_M3H
    elif recirc_flow_cmh is not None and recirc_flow_cmh > 0:
        recirc_flow_m3h = recirc_flow_cmh

    # Begin building scenario summary table
    summary_rows = []
    summary_rows.append({
        'Parameter': 'Occupancy category',
        'Value': occupancy,
        'Units': ''
    })
    summary_rows.append({
        'Parameter': 'Area',
        'Value': f"{area_m2:.2f}",
        'Units': 'm2'
    })
    summary_rows.append({
        'Parameter': 'Area',
        'Value': f"{area_ft2:.2f}",
        'Units': 'ft2'
    })
    summary_rows.append({
        'Parameter': 'Number of people',
        'Value': f"{num_people_used}",
        'Units': 'persons'
    })
    if recirc_flow_m3h is None:
        # Show R if recirc flow is not provided
        R_in = recirc_factor or 0.0
        summary_rows.append({
            'Parameter': 'Recirculation (R)',
            'Value': f"{R_in:.2f}",
            'Units': 'fraction'
        })
    else:
        summary_rows.append({
            'Parameter': 'Recirc airflow',
            'Value': f"{recirc_flow_m3h * CFM_PER_M3H:.2f}",
            'Units': 'CFM'
        })
        summary_rows.append({
            'Parameter': 'Recirc airflow',
            'Value': f"{recirc_flow_m3h:.2f}",
            'Units': 'm3/h'
        })
        # In this mode R is unknown until max_voz is computed
    # Indicate whether a global zero efficiency is used or the internal
    # design‑specific values.  When global_Ef == 0.0 we are disabling
    # filtration (Ef=0 for all compounds).  Otherwise the internal
    # efficiencies defined in air_cleaner.py are used.
    if global_Ef == 0.0:
        summary_rows.append({
            'Parameter': 'Filter efficiency',
            'Value': '0 (disabled)',
            'Units': ''
        })
    else:
        summary_rows.append({
            'Parameter': 'Filter efficiency',
            'Value': 'internal values',
            'Units': ''
        })
    summary_rows.append({
        'Parameter': 'Filter location',
        'Value': loc,
        'Units': ''
    })
    summary_rows.append({
        'Parameter': 'Ez',
        'Value': f"{Ez:.2f}",
        'Units': 'zone air dist. eff.'
    })
    # Do not include a units row since the app always shows both CFM and m3/h
    summary_rows.append({
        'Parameter': 'Safe factor',
        'Value': f"{safe_factor:.2f}",
        'Units': '<= 1'
    })
    scenario_summary_df = pd.DataFrame(summary_rows)

    # Compute emission rates for area and per person
    try:
        rates = get_emission_rates_for_occupancy(occupancy, area_m2)
    except Exception as e:
        # Propagate exception for the caller to handle
        raise

    human_emissions = get_human_occupant_emission_rates(num_people_used, DESIGN_LIMITS.keys())

    # Build summary for each compound
    compound_rows: List[Dict[str, any]] = []
    # We'll store intermediate results for later Cbz calculation
    intermediate: List[Dict[str, any]] = []

    for compound in DESIGN_LIMITS.keys():
        # Calculate N (emission rate) as area + human contributions
        N_val = 0.0
        # Area contributions: match case-insensitive
        for em_comp in rates:
            if em_comp.strip().lower() == compound.strip().lower():
                N_val = rates[em_comp]
                break
        # Human contributions
        for h_comp in human_emissions:
            if h_comp.strip().lower() == compound.strip().lower():
                N_val += human_emissions[h_comp]
                break

        # Design limit and units
        Cbz_limit, units_out, _ = get_design_limit_ugm3(compound)
        Cbz_limit_safe = Cbz_limit * safe_factor
        # Outdoor concentration
        Co_val = get_outdoor_concentration_ugm3(compound)

        # Determine compound specific filter efficiency
        if global_Ef == 0.0:
            Ef_val = 0.0
        else:
            try:
                Ef_val = get_cleaner_efficiency(compound)
            except KeyError:
                Ef_val = global_Ef

        # Compute required outdoor airflow
        try:
            Voz_val, Vr_val, Recirc_val = calc_Voz(
                N=N_val,
                Co=Co_val,
                Cbz=Cbz_limit_safe,
                R=recirc_factor or 0.0,
                Ef=Ef_val,
                Ez=Ez,
                loc=loc,
            )
            Voz_cfm_val = Voz_val * CFM_PER_M3H
            row = {
                'Compound': compound,
                'N (ug/h)': N_val,
                'Safe limit (ug/m3)': Cbz_limit_safe,
                'Outdoor (ug/m3)': Co_val,
                'Voz (m3/h)': Voz_val,
                'Voz (CFM)': Voz_cfm_val,
            }
            intermediate.append({
                'compound': compound,
                'N': N_val,
                'limit': Cbz_limit_safe,
                'Co': Co_val,
                'Voz': Voz_val,
                'Ef': Ef_val,
            })
        except Exception as e:
            # Use None to signal an error; recirc factor remains as given
            row = {
                'Compound': compound,
                'N (ug/h)': N_val,
                'Safe limit (ug/m3)': Cbz_limit_safe,
                'Outdoor (ug/m3)': Co_val,
                'Voz (m3/h)': None,
                'Voz (CFM)': None,
            }
            intermediate.append({
                'compound': compound,
                'N': N_val,
                'limit': Cbz_limit_safe,
                'Co': Co_val,
                'Voz': None,
                'Ef': Ef_val,
                'error': str(e),
            })

        compound_rows.append(row)

    # Build DataFrame for required airflow
    summary_df = pd.DataFrame(compound_rows)
    # Display columns according to units selection
    display_columns = ['Compound', 'N (ug/h)', 'Safe limit (ug/m3)', 'Outdoor (ug/m3)']
    if units in ('CMH', 'BOTH'):
        display_columns.append('Voz (m3/h)')
    if units in ('CFM', 'BOTH'):
        display_columns.append('Voz (CFM)')
    summary_df = summary_df[display_columns]

    # Determine maximum Voz among valid entries
    voz_values = [r['Voz'] for r in intermediate if r.get('Voz') is not None]
    if voz_values:
        max_voz = max(voz_values)
    else:
        max_voz = 0.0

    # Compute recirculation factor R from recirc_flow if provided
    R_effective = recirc_factor or 0.0
    if recirc_flow_m3h is not None and max_voz + recirc_flow_m3h > 0:
        R_effective = recirc_flow_m3h / (max_voz + recirc_flow_m3h)

    # Compute Vr and other flows based on R_effective
    if R_effective < 1.0 and max_voz > 0:
        max_vr = max_voz / (1.0 - R_effective)
    else:
        max_vr = float('inf')

    # Now compute Cbz values for each compound using max_voz
    cbz_rows: List[Dict[str, any]] = []
    for r in intermediate:
        comp = r['compound']
        N_val = r['N']
        Co_val = r['Co']
        limit_val = r['limit']
        Ef_val = r['Ef']
        try:
            if max_voz <= 0:
                cbz_val = float('nan')
            else:
                cbz_val = calc_Cbz(
                    N=N_val,
                    Voz=max_voz,
                    Co=Co_val,
                    R=R_effective,
                    Ef=Ef_val,
                    Ez=Ez,
                    Vr=max_vr,
                    loc=loc,
                )
            pct = (cbz_val / limit_val * 100.0) if limit_val > 0 else float('nan')
            cbz_rows.append({
                'Compound': comp,
                'N (ug/h)': N_val,
                'Outdoor (ug/m3)': Co_val,
                'Cbz (ug/m3)': cbz_val,
                'Design limit (ug/m3)': limit_val,
                '% Limit': pct,
            })
        except Exception:
            cbz_rows.append({
                'Compound': comp,
                'N (ug/h)': N_val,
                'Outdoor (ug/m3)': Co_val,
                'Cbz (ug/m3)': None,
                'Design limit (ug/m3)': limit_val,
                '% Limit': None,
            })

    cbz_df = pd.DataFrame(cbz_rows)

    # Compute mixture exposure sums
    mixture_sums = calculate_mixture_exposure([
        {
            'compound': row['Compound'],
            'Cbz': row['Cbz (ug/m3)'],
            'limit': row['Design limit (ug/m3)'],
        }
        for row in cbz_rows
    ])
    mix_rows = []
    for group, value in mixture_sums.items():
        mix_rows.append({
            'Group': group,
            'Exposure sum': value,
        })
    mixture_df = pd.DataFrame(mix_rows)

    # Build final airflows table
    final_rows = []
    # Use final_voz = max_voz; compute Recirc = R_effective * Vr; total flow; percent outdoor
    final_voz_cmh = max_voz
    final_voz_cfm = final_voz_cmh * CFM_PER_M3H
    if R_effective < 1.0 and max_voz > 0:
        Vr_val = max_vr
        Recirc_val = R_effective * Vr_val
    else:
        Vr_val = float('inf')
        Recirc_val = float('inf')
    total_flow_m3h = final_voz_cmh + Recirc_val
    total_flow_cfm = total_flow_m3h * CFM_PER_M3H
    pct_outdoor = (100.0 * final_voz_cmh / total_flow_m3h) if total_flow_m3h > 0 else float('nan')

    final_rows.append({
        'Parameter': 'Voz (outdoor airflow)',
        'Value (CFM)': final_voz_cfm,
        'Value (m3/h)': final_voz_cmh,
    })
    final_rows.append({
        'Parameter': 'R x Vr (recirc airflow)',
        'Value (CFM)': Recirc_val * CFM_PER_M3H if math.isfinite(Recirc_val) else float('nan'),
        'Value (m3/h)': Recirc_val if math.isfinite(Recirc_val) else float('nan'),
    })
    final_rows.append({
        'Parameter': 'Total to zone (Voz+Recirc)',
        'Value (CFM)': total_flow_cfm,
        'Value (m3/h)': total_flow_m3h,
    })
    final_rows.append({
        'Parameter': 'Outdoor % of Total',
        'Value (CFM)': pct_outdoor,
        'Value (m3/h)': pct_outdoor,
    })
    final_flows_df = pd.DataFrame(final_rows)

    return {
        'scenario_summary': scenario_summary_df,
        'summary_table': summary_df,
        'cbz_table': cbz_df,
        'mixture_table': mixture_df,
        'final_flows_table': final_flows_df,
    }


def main():
    """
    Entry point for the Streamlit application.  Builds the user
    interface, collects user inputs, calls the core computation
    function and displays results.
    """
    st.set_page_config(
        page_title="IAQP Calculator",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Indoor Air Quality Procedure Calculator")
    st.markdown(
        "This tool computes the minimum outdoor airflow required to meet \n"
        "design limits for various indoor contaminants using the ASHRAE \n"
        "62.1 IAQP method.  Adjust the parameters below and click the \n"
        "*Calculate* button to see results."
    )

    # Sidebar for inputs
    with st.sidebar:
        st.header("Inputs")
        # Occupancy selection: use keys from VRP_TABLE_6_1 for occupant density
        occupancy_options = sorted(VRP_TABLE_6_1.keys())
        occupancy = st.selectbox(
            "Occupancy category",
            options=occupancy_options,
            index=occupancy_options.index("Classrooms (age 9 plus)")
            if "Classrooms (age 9 plus)" in occupancy_options
            else 0,
        )
        # Area input: allow specification in m2 or ft2.  The user selects
        # the units, enters a numeric value and we convert to m2 for
        # calculations.
        area_unit = st.radio("Area units", options=["m2", "ft2"], index=0, horizontal=True)
        area_input = st.number_input(
            f"Area ({area_unit})", min_value=0.0, value=90.0 if area_unit == "m2" else 968.75, step=1.0, format="%.2f"
        )
        # Optional number of people
        num_people_input = st.number_input(
            "Number of people (leave zero to use default)",
            min_value=0,
            value=0,
            step=1,
        )
        safe_factor = st.number_input(
            "Safety factor (<=1)", min_value=0.0, max_value=1.0, value=1.0, step=0.01
        )
        # Recirculation options: choose to specify R or flow
        recirc_mode = st.radio(
            "Recirculation input mode",
            options=["Use R (fraction)", "Use recirc airflow"],
            index=0,
        )
        recirc_factor = None
        recirc_flow_cfm = None
        recirc_flow_cmh = None
        if recirc_mode == "Use R (fraction)":
            recirc_factor = st.number_input(
                "Recirculation factor R (0-1)", min_value=0.0, max_value=0.99, value=0.0, step=0.01
            )
        else:
            recirc_units = st.radio(
                "Recirculation airflow units", options=["CFM", "m3/h"], index=0
            )
            if recirc_units == "CFM":
                recirc_flow_cfm = st.number_input(
                    "Recirc airflow (CFM)", min_value=0.0, value=0.0, step=1.0
                )
            else:
                recirc_flow_cmh = st.number_input(
                    "Recirc airflow (m3/h)", min_value=0.0, value=0.0, step=1.0
                )
        # Filter efficiency selection: tick box to set Ef to zero for all
        # compounds; otherwise the internal values defined in
        # air_cleaner.py are used.  We do not expose a numeric input
        # because the IAQP specification provides default values.
        ef_zero = st.checkbox(
            "Set Ef to zero (disable filtration)",
            value=False,
            help="If checked, sets the filter efficiency Ef to zero for all compounds.  Otherwise the internal design-specific values are used."
        )
        loc = st.radio(
            "Filter location", options=["A", "B"], index=0, horizontal=True
        )
        Ez = st.number_input(
            "Zone air distribution effectiveness (Ez)", min_value=0.1, max_value=5.0, value=1.0, step=0.05
        )
        # Always display results in both CFM and m3/h; no units selector
        calculate_button = st.button("Calculate")

    # End of sidebar; now proceed in the main page.  If the button was
    # pressed, compute and display results outside of the sidebar so
    # they appear in the main pane.
    if calculate_button:
        # Determine area in m2 regardless of units selected
        if area_unit == "m2":
            area_m2 = area_input
        else:
            area_m2 = area_input / 10.7639  # convert ft2 to m2
        # Determine global filter efficiency: zero if ef_zero is checked,
        # else a non-zero value to trigger use of internal efficiencies.
        global_Ef = 0.0 if ef_zero else 1.0
        try:
            result = compute_summary(
                occupancy=occupancy,
                area_m2=area_m2,
                num_people=num_people_input if num_people_input > 0 else None,
                safe_factor=safe_factor,
                recirc_factor=recirc_factor,
                recirc_flow_cfm=recirc_flow_cfm,
                recirc_flow_cmh=recirc_flow_cmh,
                global_Ef=global_Ef,
                loc=loc,
                Ez=Ez,
                units='BOTH',
            )
        except Exception as e:
            st.error(str(e))
            return

        st.subheader("Scenario summary")
        st.dataframe(result['scenario_summary'], use_container_width=True)

        st.subheader("Required outdoor airflow by compound")
        airflow_df = result['summary_table'].copy()
        for col in airflow_df.columns:
            if col not in ('Compound',):
                airflow_df[col] = airflow_df[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and pd.notna(x) else '')
        st.dataframe(airflow_df, use_container_width=True)

        st.subheader("Breathing zone concentrations using maximum Voz")
        cbz_df = result['cbz_table'].copy()
        def fmt_cbz(row):
            cbz = row['Cbz (ug/m3)']
            limit = row['Design limit (ug/m3)']
            if pd.isna(cbz):
                return ''
            elif cbz <= limit:
                return f"{cbz:.2f}"
            else:
                return f"{cbz:.2f}"
        cbz_df['Cbz (ug/m3)'] = cbz_df.apply(fmt_cbz, axis=1)
        for col in ['N (ug/h)', 'Outdoor (ug/m3)', 'Design limit (ug/m3)', '% Limit']:
            cbz_df[col] = cbz_df[col].apply(
                lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and pd.notna(x) else ''
            )
        st.dataframe(cbz_df, use_container_width=True)

        st.subheader("Mixed exposure sums")
        mixture_df = result['mixture_table'].copy()
        mixture_df['Exposure sum'] = mixture_df['Exposure sum'].apply(
            lambda x: f"{x:.3f}" if isinstance(x, (int, float)) and pd.notna(x) else ''
        )
        st.dataframe(mixture_df, use_container_width=True)

        st.subheader("Final airflows used in zone calculations")
        final_df = result['final_flows_table'].copy()
        for col in ['Value (CFM)', 'Value (m3/h)']:
            final_df[col] = final_df[col].apply(
                lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and pd.notna(x) else ''
            )
        st.dataframe(final_df, use_container_width=True)


if __name__ == "__main__":
    main()