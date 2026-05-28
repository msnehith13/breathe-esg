# Great-circle distances between common Indian airport pairs (km).
# In production this would be an API call (e.g. Aviation Edge, OAG).
# We use a static lookup for prototype scope — documented in DECISIONS.md.
AIRPORT_DISTANCES = {
    ('BOM', 'DEL'): 1148,
    ('DEL', 'BOM'): 1148,
    ('DEL', 'BLR'): 1740,
    ('BLR', 'DEL'): 1740,
    ('MAA', 'BOM'): 1031,
    ('BOM', 'MAA'): 1031,
    ('HYD', 'BOM'): 711,
    ('BOM', 'HYD'): 711,
    ('BOM', 'CCU'): 1654,
    ('CCU', 'BOM'): 1654,
    ('HYD', 'DEL'): 1253,
    ('DEL', 'HYD'): 1253,
}

# Scope 3 category mapping by travel type and class.
TRAVEL_CATEGORY = {
    'flight_economy':         'Business Travel - Flight (Economy)',
    'flight_business':        'Business Travel - Flight (Business Class)',
    'flight_unknown':         'Business Travel - Flight (Class Unknown)',
    'hotel':                  'Business Travel - Hotel Stay',
    'ground_transport':       'Business Travel - Ground Transport',
}

# All corporate travel = Scope 3
TRAVEL_SCOPE = 'SCOPE_3'

# Quantity units per category
# Flights: km traveled
# Hotel: nights
# Ground transport: km (if known) else cost as proxy
TRAVEL_UNITS = {
    'flight':          'km',
    'hotel':           'nights',
    'ground_transport': 'km',
}