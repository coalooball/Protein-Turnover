"""Generate some SQL statements."""

PROTEIN_TURNOVER = "protein_turnover"


def add_prefix_for_table_name(func):
    def inner(table_name):
        full_name = PROTEIN_TURNOVER + "_" + table_name
        res = func(full_name)
        return res

    return inner


@add_prefix_for_table_name
def make_pepxml_create_table_sql(table_name: str) -> str:
    return f"""CREATE TABLE default.{table_name}
(
    `spectrum` String,
    `precursor_neutral_mass` Nullable(Float64),
    `assumed_charge` Nullable(Int64),
    `retention_time_sec` Nullable(Float64),
    `start_scan` Nullable(Int64),
    `end_scan` Nullable(Int64),
    `index` Nullable(Int64),
    `protein` Array(String),
    `protein_descr` Array(String),
    `peptide_next_aa` Array(String),
    `peptide_prev_aa` Array(String),
    `num_tol_term` Array(UInt8),
    `ionscore` Nullable(Float64),
    `identityscore` Nullable(Float64),
    `star` Nullable(Float64),
    `homologyscore` Nullable(Float64),
    `expect` Nullable(Float64),
    `modifications` Array(String),
    `hit_rank` Nullable(Int64),
    `peptide` String,
    `num_tot_proteins` Nullable(Int64),
    `num_matched_ions` Nullable(Int64),
    `tot_num_ions` Nullable(Int64),
    `num_missed_cleavages` Nullable(Int64),
    `calc_neutral_pep_mass` Nullable(Float64),
    `massdiff` Nullable(Float64),
    `is_rejected` Nullable(UInt8),
    `modified_peptide` String,
    `fval` Nullable(Float64),
    `ntt` Nullable(Float64),
    `nmc` Nullable(Float64),
    `AccMass` Nullable(Float64),
    `isomassd` Nullable(Float64),
    `peptideprophet_probability` Nullable(Float64),
    `peptideprophet_ntt_prob` Array(Nullable(Float64))
)
ENGINE = MergeTree
ORDER BY spectrum
SETTINGS index_granularity = 8192
"""


@add_prefix_for_table_name
def make_mzml_create_table_sql(table_name: str) -> str:
    return f"""CREATE TABLE default.{table_name}
(
    `RT` Float64,
    `mzarray` Array(Float64),
    `intarray` Array(Float64)
)
ENGINE = MergeTree
ORDER BY RT
SETTINGS index_granularity = 8192
"""


@add_prefix_for_table_name
def make_find_table_in_system_table(table_name: str) -> str:
    return f"""select name from `system`.`tables` where `database` = 'default' and name = '{table_name}'"""


@add_prefix_for_table_name
def get_full_table_name(table_name: str) -> str:
    return table_name


def make_get_all_pepxml_table_names() -> str:
    return r"select name from `system`.`tables` where `database` = 'default' and name like 'protein_turnover%xml'"

def make_get_all_mzml_table_names() -> str:
    return r"select name from `system`.`tables` where `database` = 'default' and name like 'protein_turnover%mzml'"

def make_history_dirs_ddl() -> str:
    return f"""CREATE TABLE {get_full_table_name('history_dirs')} (
    dirs String
) ENGINE = MergeTree()
ORDER BY dirs;
"""

def make_get_all_history_dirs() -> str:
    return f"select distinct(dirs) from {get_full_table_name('history_dirs')}"
