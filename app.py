from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import tempfile
import openpyxl
import pandas as pd
import streamlit as st

from currency_conv import convert_currency
from energy_power_conv import convert_energy_power
from length_conv import convert_length
from misc_conv import convert_misc
from pressure_force_area_conv import convert_pressure_force_area
from temp_conv import convert_temp
from time_conv import convert_time
from volume_conv import convert_volume
from weight_conv import convert_weight

st.set_page_config(
    page_title="Unit Conversion & Offset Calculator",
    page_icon="\u2696\ufe0f",
    layout="wide",
)


ALL_CONVERTERS = [
    convert_length,
    convert_weight,
    convert_temp,
    convert_currency,
    convert_time,
    convert_volume,
    convert_energy_power,
    convert_pressure_force_area,
    convert_misc,
]

DEFAULT_COMPOUND_OVERRIDES = {
    ("%", "\u2030"): (0.1, 0.0),
    ("N/m", "kN.m/m2"): (1000.0, 0.0),
    ("N", "kN.m/m"): (1000.0, 0.0),
    ("1/(N/m2)", "1/MPa"): (1e-6, 0.0),
    ("mm4", "in4"): (25.4**4, 0.0),
    ("m(1/3)/s", "ft(1/3)/s"): (0.3048 ** (1 / 3), 0.0),
    ("m/kg(1/3)", "ft/lb(1/3)"): (0.3048 / (0.45359237 ** (1 / 3)), 0.0),
    ("W/m2", "BTU/(h.ft2)"): (0.29307107 / (0.3048**2), 0.0),
    ("W/(m.K)", "BTU/(h.ft.\u00b0F)"): (
        1055.05585262 / (3600 * 0.3048 * (5 / 9)),
        0.0,
    ),
    ("N/m", "kip.ft/ft2"): (4448.2216152605 / 0.3048, 0.0),
    ("N", "kip.ft/ft"): (4448.2216152605, 0.0),
    ("1/(N/m2)", "1/ksi"): (1 / 6894757.293168361, 0.0),
    ("N/mm^(3/2)", "ksi.in(1/2)"): (
        6894757.293168361 * (0.0254**0.5) / (1000**1.5),
        0.0,
    ),
    ("m.s", "h.ft"): (3600 * 0.3048, 0.0),
    ("m2.s", "h.ft2"): (3600 * 0.3048**2, 0.0),
    ("m2.s.\u00b0C", "h.ft2.\u00b0F"): (3600 * 0.3048**2 * (5 / 9), 0.0),
    ("m.s.\u00b0C", "h.ft.\u00b0F"): (3600 * 0.3048 * (5 / 9), 0.0),
    ("m", "J/kN"): (0.001, 0.0),
    ("W", "J/h"): (1 / 3600, 0.0),
    ("lx", "lm/ft2"): (1 / 0.09290304, 0.0),
    ("cm2/m", "m2/m"): (1 / 10000.0, 0.0),
    ("mm2/m", "m2/m"): (1 / 1000000.0, 0.0),
}

for key, default_val in [
    ("custom_pair_rules", {}),
    ("custom_base_units", {}),
]:
  if key not in st.session_state:
    st.session_state[key] = default_val


def strip_outer_parentheses(unit_str: str) -> str:
  unit_str = unit_str.strip()
  while unit_str.startswith("(") and unit_str.endswith(")"):
    depth = 0
    for idx, ch in enumerate(unit_str):
      if ch == "(":
        depth += 1
      elif ch == ")":
        depth -= 1
        if depth == 0 and idx != len(unit_str) - 1:
          return unit_str
    if depth != 0:
      return unit_str
    unit_str = unit_str[1:-1].strip()
  return unit_str


def split_ratio(unit_str: str):
  depth = 0
  separators = []
  for idx, ch in enumerate(unit_str):
    if ch == "(":
      depth += 1
    elif ch == ")":
      depth -= 1
    elif ch == "/" and depth == 0:
      separators.append(idx)
  if separators:
    idx = separators[-1]
    return (
        strip_outer_parentheses(unit_str[:idx]),
        strip_outer_parentheses(unit_str[idx + 1 :]),
    )
  return unit_str, None


def resolve_conversion(to_u: str, from_u: str):
  to_u = str(to_u).strip()
  from_u = str(from_u).strip()

  if to_u == from_u:
    return 1.0, 0.0, "Matched (Identical)"

  if (to_u, from_u) in st.session_state.custom_pair_rules:
    f, o = st.session_state.custom_pair_rules[(to_u, from_u)]
    return f, o, "Custom Pair Rule"

  base_map = st.session_state.custom_base_units
  if to_u in base_map and from_u in base_map:
    dim_to, mult_to = base_map[to_u]
    dim_from, mult_from = base_map[from_u]
    if dim_to == dim_from and mult_to != 0:
      return mult_from / mult_to, 0.0, f"Custom Base Unit ({dim_to})"

  if (to_u, from_u) in DEFAULT_COMPOUND_OVERRIDES:
    f, o = DEFAULT_COMPOUND_OVERRIDES[(to_u, from_u)]
    return f, o, "Matched (Override)"

  for converter in ALL_CONVERTERS:
    factor, offset = converter(to_u, from_u)
    if factor is not None:
      return factor, offset, f"Matched ({converter.__name__})"

  if "/" in to_u and "/" in from_u:
    num_to, den_to = split_ratio(to_u)
    num_from, den_from = split_ratio(from_u)
    if den_to and den_from:
      num_f, _, _ = resolve_conversion(num_to, num_from)
      den_f, _, _ = resolve_conversion(den_to, den_from)
      if num_f is not None and den_f is not None and den_f != 0:
        return num_f / den_f, 0.0, "Matched (Compound Ratio)"

  if "." in to_u and "." in from_u:
    p_to, p_from = to_u.split("."), from_u.split(".")
    if len(p_to) == len(p_from) and len(p_to) >= 2:
      product = 1.0
      for a, b in zip(p_to, p_from):
        part_f, _, _ = resolve_conversion(a, b)
        if part_f is None:
          product = None
          break
        product *= part_f
      if product is not None:
        return product, 0.0, "Matched (Compound Product)"

  if to_u.startswith("1/") and from_u.startswith("1/"):
    b_f, _, _ = resolve_conversion(to_u[2:], from_u[2:])
    if b_f is not None and b_f != 0:
      return 1.0 / b_f, 0.0, "Matched (Reciprocal)"

  return None, None, "Unmatched"


def _find_col_index(ws, target_name: str, fallback_idx: int) -> int:
  for col_idx in range(1, ws.max_column + 1):
    val = ws.cell(row=1, column=col_idx).value
    if val is not None and str(val).strip() == target_name:
      return col_idx
  return fallback_idx


def build_output_excel(uploaded_bytes: bytes, results_df: pd.DataFrame) -> bytes:
  wb = openpyxl.load_workbook(BytesIO(uploaded_bytes))
  ws = wb.active
  fac_col = _find_col_index(ws, "conversionFactor", 2)
  off_col = _find_col_index(ws, "conversionOffset", 3)

  lookup = {
      int(row["excel_row"]): (row["conversionFactor"], row["conversionOffset"])
      for _, row in results_df.iterrows()
  }
  for row_idx in range(2, ws.max_row + 1):
    if row_idx in lookup:
      fac, off = lookup[row_idx]
      ws.cell(row=row_idx, column=fac_col).value = (
          float(fac) if pd.notna(fac) else float("nan")
      )
      ws.cell(row=row_idx, column=off_col).value = (
          float(off) if pd.notna(off) else float("nan")
      )
  out_stream = BytesIO()
  wb.save(out_stream)
  out_stream.seek(0)
  return out_stream.getvalue()


def build_manual_rules_template(unmatched_pairs_df: pd.DataFrame) -> bytes:
  if unmatched_pairs_df.empty:
    template_df = pd.DataFrame(
        columns=[
            "to_unit",
            "from_unit",
            "to_unit_desig",
            "from_unit_desig",
            "conversionFactor",
            "conversionOffset",
        ]
    )
  else:
    template_df = unmatched_pairs_df.copy()
    template_df["conversionFactor"] = float("nan")
    template_df["conversionOffset"] = 0.0

  out_stream = BytesIO()
  with pd.ExcelWriter(out_stream, engine="openpyxl") as writer:
    template_df.to_excel(writer, index=False, sheet_name="manual_rules")
  out_stream.seek(0)
  return out_stream.getvalue()


def parse_manual_rules_excel(excel_bytes: bytes) -> tuple[dict, list[str]]:
  rules_df = pd.read_excel(BytesIO(excel_bytes))
  required_cols = {"to_unit", "from_unit", "conversionFactor"}
  if not required_cols.issubset(set(rules_df.columns)):
    raise ValueError(
        "Manual rules Excel must contain `to_unit`, `from_unit`, and"
        " `conversionFactor` columns (optional `conversionOffset`)."
    )

  imported_rules = {}
  skipped_notes = []
  has_offset = "conversionOffset" in rules_df.columns

  for idx, row in rules_df.iterrows():
    to_u = "" if pd.isna(row["to_unit"]) else str(row["to_unit"]).strip()
    from_u = "" if pd.isna(row["from_unit"]) else str(row["from_unit"]).strip()
    if not to_u or not from_u:
      continue

    fac_raw = row["conversionFactor"]
    if pd.isna(fac_raw) or str(fac_raw).strip() == "":
      skipped_notes.append(f"Row {idx + 2}: blank `conversionFactor` skipped.")
      continue
    try:
      fac_val = float(fac_raw)
    except (TypeError, ValueError):
      skipped_notes.append(
          f"Row {idx + 2}: invalid `conversionFactor` ({fac_raw!r}) skipped."
      )
      continue

    off_val = 0.0
    if has_offset and pd.notna(row["conversionOffset"]) and str(
        row["conversionOffset"]
    ).strip() != "":
      try:
        off_val = float(row["conversionOffset"])
      except (TypeError, ValueError):
        skipped_notes.append(
            f"Row {idx + 2}: invalid `conversionOffset` defaulted to 0.0."
        )
        off_val = 0.0

    imported_rules[(to_u, from_u)] = (fac_val, off_val)

  return imported_rules, skipped_notes


DOCUMENTATION_TEX = r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{hyperref}

\title{Unit Conversion \& Offset Factor Generator\\\large User Documentation}
\date{}

\begin{document}
\maketitle

\section{Purpose}
This web application fills in the columns \texttt{conversionFactor} and
\texttt{conversionOffset} of an Excel file that lists pairs of units. For
every pair it finds the numbers needed to convert a value from one unit to
another, and lets you define the pairs it cannot resolve on its own.

\section{Conversion Formula}
Every conversion follows the same linear relation:
\begin{equation}
  v_{\text{to}} = v_{\text{from}} \cdot f + o
\end{equation}
where $f$ is the \texttt{conversionFactor} and $o$ is the
\texttt{conversionOffset}. For most units $o = 0$. A non-zero offset occurs,
for example, between temperature scales:
\begin{equation}
  T_{^\circ\mathrm{C}} = T_{\mathrm{K}} \cdot 1 + (-273.15)
\end{equation}

\section{Input File}
Upload an \texttt{.xlsx} file with at least these columns:
\begin{center}
\begin{tabular}{@{}ll@{}}
\toprule
Column & Meaning \\
\midrule
\texttt{to\_unit} & Target unit \\
\texttt{from\_unit} & Source unit \\
\texttt{to\_unit\_desig}, \texttt{from\_unit\_desig} & Optional descriptions \\
\texttt{id} & Optional row identifier \\
\texttt{conversionFactor}, \texttt{conversionOffset} & Filled in by the app \\
\bottomrule
\end{tabular}
\end{center}

\section{How a Pair Is Resolved}
For each row the app tries the following steps in order and stops at the
first match:
\begin{enumerate}[nosep]
  \item \textbf{Identical units}: factor $1$, offset $0$.
  \item \textbf{Custom pair rule} defined by the user.
  \item \textbf{Custom base units} of the same dimension group, where
        $f = m_{\text{from}} / m_{\text{to}}$ and $m$ is the multiplier to
        the base unit.
  \item \textbf{Built-in overrides} for special compound units.
  \item \textbf{Built-in converters}: length, weight, temperature, currency,
        time, volume, energy and power, pressure/force/area, and
        miscellaneous.
  \item \textbf{Compound ratio} such as \texttt{m/s}: numerator and
        denominator are converted separately and $f = f_{\text{num}} /
        f_{\text{den}}$.
  \item \textbf{Compound product} such as \texttt{kN.m}: the factors of the
        parts are multiplied.
  \item \textbf{Reciprocal} such as \texttt{1/MPa}: $f = 1 / f_{\text{base}}$.
\end{enumerate}
If none of these succeeds, the row is marked \texttt{Unmatched}. The
\texttt{status} column in the preview shows which step produced each result.

\section{Using the App}
\begin{enumerate}[nosep]
  \item Upload the Excel file in the sidebar.
  \item Check the summary figures (total rows, matched, unmatched, custom
        rules).
  \item In the tab \emph{Output Preview \& Download}, filter the rows and
        inspect the results.
  \item In the tab \emph{Define Unmatched Units}, resolve the unmatched rows
        with one of the options below.
  \item Download the populated Excel file.
\end{enumerate}

\subsection*{Option 1: Do It Manually}
Select an unmatched pair, enter its factor and offset, and save it as a
custom pair rule. You can also define a reusable base unit by giving a
dimension group, a symbol and a multiplier to the base unit. Units of the same
group are then converted automatically.

\subsection*{Option 2: Upload Manual Rules Excel}
Download the template (it lists the current unmatched pairs), fill in
\texttt{conversionFactor} and, if needed, \texttt{conversionOffset}, and upload
it again. Rows with a blank or invalid factor are skipped, and an invalid
offset defaults to $0$.

\section{Output}
The downloaded file is a copy of the uploaded one in which the columns
\texttt{conversionFactor} and \texttt{conversionOffset} have been filled in.
Unmatched rows contain \texttt{NaN}.

\section{Notes}
\begin{itemize}[nosep]
  \item Custom rules are kept only for the current browser session. Reloading
        the page clears them, so download your results before closing.
  \item Custom rules take priority over all built-in conversions.
  \item Always check generated factors for critical applications.
\end{itemize}

\end{document}
'''


@st.cache_data(show_spinner=False)
def build_documentation_pdf(tex_source: str) -> bytes | None:
  """Compiles the LaTeX documentation to PDF.

  1. If `pdflatex` is installed (TeX Live / MiKTeX), compile it on the fly.
  2. Otherwise use `unit_conversion_documentation.pdf` placed next to app.py.
  3. Otherwise return None (no documentation button content is shown).
  """
  exe = shutil.which("pdflatex")
  if exe:
    try:
      with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "doc.tex").write_text(tex_source, encoding="utf-8")
        subprocess.run(
            [exe, "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
            cwd=tmp,
            capture_output=True,
            timeout=120,
            check=True,
        )
        return (Path(tmp) / "doc.pdf").read_bytes()
    except Exception:
      pass
  bundled = Path(__file__).with_name("unit_conversion_documentation.pdf")
  if bundled.exists():
    return bundled.read_bytes()
  return None


st.title("\u2696\ufe0f Unit Conversion & Offset Factor Generator")
st.markdown(
    "Upload your Excel file (`units_conversion_to_add.xlsx`), inspect the"
    " output preview, and define unmatched units manually or via Excel."
)

with st.sidebar:
  st.header("1. Upload Excel File")
  uploaded_file = st.file_uploader("Choose an `.xlsx` file", type=["xlsx"])
  st.divider()
  st.header("Documentation")
  doc_pdf = build_documentation_pdf(DOCUMENTATION_TEX)
  if doc_pdf:
    st.download_button(
        label="\U0001f4c4 Download Documentation (PDF)",
        data=doc_pdf,
        file_name="unit_conversion_documentation.pdf",
        mime="application/pdf",
    )
  else:
    st.caption("Documentation is currently unavailable.")

if uploaded_file is None:
  st.info("\U0001f448 Upload an `.xlsx` file in the sidebar to begin.")
  st.stop()

file_bytes = uploaded_file.getvalue()
raw_df = pd.read_excel(BytesIO(file_bytes))

if not {"to_unit", "from_unit"}.issubset(set(raw_df.columns)):
  st.error("Excel file must contain `to_unit` and `from_unit` columns.")
  st.stop()

nan_val = float("nan")
processed_records = []
for idx, row in raw_df.iterrows():
  to_u = "" if pd.isna(row["to_unit"]) else str(row["to_unit"]).strip()
  from_u = "" if pd.isna(row["from_unit"]) else str(row["from_unit"]).strip()
  factor, offset, status = resolve_conversion(to_u, from_u)
  processed_records.append({
      "excel_row": idx + 2,
      "id": row.get("id", idx + 1),
      "to_unit": to_u,
      "from_unit": from_u,
      "to_unit_desig": row.get("to_unit_desig", ""),
      "from_unit_desig": row.get("from_unit_desig", ""),
      "conversionFactor": factor if factor is not None else nan_val,
      "conversionOffset": offset if offset is not None else nan_val,
      "status": status,
  })

results_df = pd.DataFrame(processed_records)
unmatched_df = results_df[results_df["status"] == "Unmatched"].copy()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Rows", len(results_df))
k2.metric("Matched Automatically", len(results_df) - len(unmatched_df))
k3.metric("Unmatched Units", len(unmatched_df))
k4.metric(
    "Custom Rules Defined",
    len(st.session_state.custom_pair_rules)
    + len(st.session_state.custom_base_units),
)

tab_preview, tab_define = st.tabs([
    "\U0001f4ca Output Preview & Download",
    "\U0001f6e0\ufe0f Define Unmatched Units",
])

with tab_preview:
  st.subheader("Conversion Results Preview")
  filter_choice = st.radio(
      "Filter rows:",
      [
          "All Rows",
          "Unmatched Only",
          "Non-Zero Offset Only",
          "Custom Rules Only",
      ],
      horizontal=True,
  )
  preview_df = results_df.copy()
  if filter_choice == "Unmatched Only":
    preview_df = preview_df[preview_df["status"] == "Unmatched"]
  elif filter_choice == "Non-Zero Offset Only":
    preview_df = preview_df[preview_df["conversionOffset"].fillna(0.0) != 0.0]
  elif filter_choice == "Custom Rules Only":
    preview_df = preview_df[preview_df["status"].str.startswith("Custom")]

  st.dataframe(
      preview_df[[
          "id",
          "conversionFactor",
          "conversionOffset",
          "to_unit",
          "from_unit",
          "to_unit_desig",
          "from_unit_desig",
          "status",
      ]],
      use_container_width=True,
      height=450,
  )

  st.download_button(
      label="\u2b07\ufe0f Download Populated Excel File",
      data=build_output_excel(file_bytes, results_df),
      file_name="units_conversion_modular_output.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
      type="primary",
  )

with tab_define:
  st.subheader("Define Unmatched Units")
  mode = st.radio(
      "Choose an option:",
      [
          "Option 1: Do It Manually",
          "Option 2: Upload Manual Rules Excel",
      ],
      horizontal=True,
  )

  if mode == "Option 1: Do It Manually":
    left_col, right_col = st.columns([1.2, 1])
    with left_col:
      st.markdown("### Define a Specific Pair (`to_unit` \u2190 `from_unit`)")
      if not unmatched_df.empty:
        unmatched_pairs = unmatched_df[
            ["to_unit", "from_unit", "to_unit_desig", "from_unit_desig"]
        ].drop_duplicates()
        pair_options = [
            f"{r['to_unit']}  \u2190  {r['from_unit']}   ({r['to_unit_desig']}"
            f" from {r['from_unit_desig']})"
            for _, r in unmatched_pairs.iterrows()
        ]
        sel_idx = st.selectbox(
            "Select an unmatched pair:",
            range(len(pair_options)),
            format_func=lambda i: pair_options[i],
        )
        sel_to = unmatched_pairs.iloc[sel_idx]["to_unit"]
        sel_from = unmatched_pairs.iloc[sel_idx]["from_unit"]
      else:
        st.success("No unmatched pairs remaining!")
        sel_to, sel_from = "", ""

      with st.form("manual_pair_form"):
        c1, c2 = st.columns(2)
        in_to = c1.text_input("Target Unit (`to_unit`)", value=sel_to)
        in_from = c2.text_input("Source Unit (`from_unit`)", value=sel_from)
        c3, c4 = st.columns(2)
        in_factor = c3.number_input(
            "Conversion Factor", value=1.0, format="%.10g"
        )
        in_offset = c4.number_input(
            "Conversion Offset", value=0.0, format="%.10g"
        )
        if st.form_submit_button("Save Manual Pair Rule"):
          if in_to.strip() and in_from.strip():
            st.session_state.custom_pair_rules[
                (in_to.strip(), in_from.strip())
            ] = (float(in_factor), float(in_offset))
            st.rerun()

    with right_col:
      st.markdown("### Define a Reusable Base Unit")
      with st.form("manual_base_form"):
        b_dim = st.text_input(
            "Dimension Group", placeholder="e.g., Population, Length"
        )
        b_sym = st.text_input("Unit Symbol", placeholder="e.g., k_hab")
        b_mult = st.number_input(
            "Multiplier to Base Unit", value=1.0, format="%.10g"
        )
        if st.form_submit_button("Save Base Unit"):
          if b_dim.strip() and b_sym.strip() and b_mult != 0:
            st.session_state.custom_base_units[b_sym.strip()] = (
                b_dim.strip(),
                float(b_mult),
            )
            st.rerun()

  else:
    st.markdown("### Upload Manual Conversion Values via Excel")
    st.caption(
        "Upload an `.xlsx` file containing `to_unit`, `from_unit`, and"
        " `conversionFactor` (plus optional `conversionOffset`, defaulting to"
        " `0.0`)."
    )

    unmatched_pairs_for_tpl = (
        unmatched_df[
            ["to_unit", "from_unit", "to_unit_desig", "from_unit_desig"]
        ].drop_duplicates()
        if not unmatched_df.empty
        else pd.DataFrame(
            columns=["to_unit", "from_unit", "to_unit_desig", "from_unit_desig"]
        )
    )
    st.download_button(
        label="\U0001f4e5 Download Manual Rules Excel Template",
        data=build_manual_rules_template(unmatched_pairs_for_tpl),
        file_name="manual_unmatched_rules_template.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )

    manual_rules_file = st.file_uploader(
        "Upload filled manual rules `.xlsx` file",
        type=["xlsx"],
        key="manual_rules_uploader",
    )
    if manual_rules_file is not None:
      try:
        imported_rules, notes = parse_manual_rules_excel(
            manual_rules_file.getvalue()
        )
        st.write(
            f"Ready to import **{len(imported_rules)}** manual pair rule(s)."
        )
        for note in notes:
          st.caption(note)
        if st.button(
            "\u2705 Apply Uploaded Excel Rules",
            type="primary",
            disabled=not imported_rules,
        ):
          st.session_state.custom_pair_rules.update(imported_rules)
          st.success(f"Applied {len(imported_rules)} manual rule(s) from Excel.")
          st.rerun()
      except Exception as exc:
        st.error(str(exc))

  if (
      st.session_state.custom_pair_rules
      or st.session_state.custom_base_units
  ):
    st.divider()
    st.markdown("### Active Custom Rules")
    if st.session_state.custom_pair_rules:
      st.dataframe(
          pd.DataFrame([
              {
                  "to_unit": k[0],
                  "from_unit": k[1],
                  "conversionFactor": v[0],
                  "conversionOffset": v[1],
              }
              for k, v in st.session_state.custom_pair_rules.items()
          ]),
          use_container_width=True,
      )
    if st.session_state.custom_base_units:
      st.dataframe(
          pd.DataFrame([
              {
                  "unit_symbol": k,
                  "dimension_category": v[0],
                  "base_multiplier": v[1],
              }
              for k, v in st.session_state.custom_base_units.items()
          ]),
          use_container_width=True,
      )
    if st.button("\U0001f5d1\ufe0f Clear All Custom Rules"):
      st.session_state.custom_pair_rules.clear()
      st.session_state.custom_base_units.clear()
      st.rerun()
