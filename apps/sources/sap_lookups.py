# Plant codes from SAP that we know about.
# IN03 and anything else is intentionally absent — triggers a flag.
PLANT_LOOKUP = {
    'IN01': 'Mumbai Plant',
    'IN02': 'Pune Plant',
}

# Normalize SAP unit codes to canonical units we store.
# Anything not in this map is a parse failure.
UNIT_NORMALIZATION = {
    'L':  'L',    # Litres — keep as-is
    'M3': 'M3',   # Cubic metres — keep as-is
    'KG': 'KG',   # Kilograms — keep as-is
    'TO': 'KG',   # SAP tonnes → store as KG (1 TO = 1000 KG)
}

UNIT_CONVERSION_FACTORS = {
    'L':  1.0,
    'M3': 1.0,
    'KG': 1.0,
    'TO': 1000.0,  # Convert tonnes to KG
}

# GHG Protocol scope assignment by material type.
# All fuel combustion = Scope 1.
MATERIAL_SCOPE = {
    'MAT-DIESEL-001': 'SCOPE_1',
    'MAT-PNG-002':    'SCOPE_1',
    'MAT-HFO-003':    'SCOPE_1',
    'MAT-LPG-004':    'SCOPE_1',
    'MAT-COAL-005':   'SCOPE_1',
}

MATERIAL_CATEGORY = {
    'MAT-DIESEL-001': 'Stationary Combustion - Diesel',
    'MAT-PNG-002':    'Stationary Combustion - Natural Gas',
    'MAT-HFO-003':    'Stationary Combustion - Heavy Fuel Oil',
    'MAT-LPG-004':    'Stationary Combustion - LPG',
    'MAT-COAL-005':   'Stationary Combustion - Coal',
}