
def determine_code_entity_location(asset_conc_str):
    code_start = asset_conc_str.find('\n')
    code_length = len(asset_conc_str[code_start:])
    return code_start, code_length


def parse_pct_input(pct):
    pct = float(pct)
    if pct >= 100:
        raise ValueError('Cannot lose 100% of allocation')
    elif 1 <= pct < 100:
        parsed_pct = pct / 100
    else:
        parsed_pct = pct
    return parsed_pct
