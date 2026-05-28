from datetime import datetime
from decimal import Decimal
from apps.sources.travel_lookups import (
    AIRPORT_DISTANCES, TRAVEL_CATEGORY, TRAVEL_SCOPE, TRAVEL_UNITS
)


def parse_travel_date(date_str):
    return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()


def get_flight_distance(origin, destination):
    """
    Look up great-circle distance from static table.
    Returns (distance_km, was_estimated) tuple.
    was_estimated=True means we used the lookup, not source data.
    """
    key = (origin.upper(), destination.upper())
    distance = AIRPORT_DISTANCES.get(key)
    if distance:
        return Decimal(str(distance)), True
    return None, False


def parse_travel_file(file_content: bytes) -> list[dict]:
    """
    Parses a Concur-style JSON travel export.

    Key complications handled:
      - Flights without distance — estimated from airport code lookup
      - Unknown airport codes — flagged, no distance computed
      - Hotels — quantity is nights, not distance
      - Ground transport — uses distance_km if present, else flagged
      - Missing employee ID — flagged
      - Business vs economy class — different category labels

    Returns same structure as SAP and utility parsers.
    """
    import json
    data = json.loads(file_content.decode('utf-8'))
    trips = data.get('trips', [])

    results = []

    for row_number, trip in enumerate(trips, start=1):
        errors = []
        flags = []
        parsed = {}
        raw_data = dict(trip)

        trip_id = trip.get('trip_id', '').strip()
        employee_id = trip.get('employee_id')
        travel_date_str = trip.get('travel_date', '').strip()
        category = trip.get('category', '').strip().lower()
        origin = (trip.get('origin') or '').strip().upper()
        destination = (trip.get('destination') or '').strip().upper()
        ticket_class = (trip.get('ticket_class') or '').strip().lower()
        distance_km = trip.get('distance_km')
        vendor = (trip.get('vendor') or '').strip()
        nights = trip.get('nights')

        # --- Employee ID ---
        if not employee_id:
            flags.append(f'Missing employee_id on trip {trip_id}')
        else:
            parsed['employee_id'] = employee_id

        # --- Date ---
        if not travel_date_str:
            errors.append('Missing travel_date')
        else:
            try:
                parsed['activity_date'] = parse_travel_date(travel_date_str)
            except ValueError:
                errors.append(f'Invalid travel_date: {travel_date_str!r}')

        # --- Category routing ---
        if category not in ('flight', 'hotel', 'ground_transport'):
            errors.append(f'Unknown category: {category!r}')
        else:
            parsed['travel_category'] = category

            if category == 'flight':
                class_key = f'flight_{ticket_class}' if ticket_class in ('economy', 'business') else 'flight_unknown'
                parsed['category'] = TRAVEL_CATEGORY[class_key]
                parsed['original_unit'] = 'km'
                parsed['normalized_unit'] = 'km'

                # Try source distance first, then lookup, then flag
                if distance_km is not None:
                    parsed['quantity'] = Decimal(str(distance_km))
                    parsed['normalized_quantity'] = parsed['quantity']
                elif origin and destination:
                    dist, estimated = get_flight_distance(origin, destination)
                    if dist:
                        parsed['quantity'] = dist
                        parsed['normalized_quantity'] = dist
                        flags.append(
                            f'Distance estimated from airport lookup: '
                            f'{origin}→{destination} = {dist}km'
                        )
                    else:
                        flags.append(
                            f'Unknown airport pair: {origin}→{destination} — '
                            f'distance could not be determined'
                        )
                        parsed['quantity'] = Decimal('0')
                        parsed['normalized_quantity'] = Decimal('0')
                else:
                    errors.append('Flight missing both distance_km and airport codes')

                parsed['location'] = f'{origin}→{destination}' if origin and destination else ''

            elif category == 'hotel':
                parsed['category'] = TRAVEL_CATEGORY['hotel']
                parsed['original_unit'] = 'nights'
                parsed['normalized_unit'] = 'nights'

                if not destination:
                    flags.append('Hotel stay missing destination/city')
                    parsed['location'] = 'Unknown'
                else:
                    parsed['location'] = destination

                if nights is not None:
                    parsed['quantity'] = Decimal(str(nights))
                    parsed['normalized_quantity'] = parsed['quantity']
                else:
                    flags.append('Hotel stay missing nights count — defaulted to 1')
                    parsed['quantity'] = Decimal('1')
                    parsed['normalized_quantity'] = Decimal('1')

            elif category == 'ground_transport':
                parsed['category'] = TRAVEL_CATEGORY['ground_transport']
                parsed['original_unit'] = 'km'
                parsed['normalized_unit'] = 'km'
                parsed['location'] = origin or destination or 'Unknown'

                if distance_km is not None:
                    parsed['quantity'] = Decimal(str(distance_km))
                    parsed['normalized_quantity'] = parsed['quantity']
                else:
                    flags.append(
                        'Ground transport missing distance_km — '
                        'cannot compute activity quantity'
                    )
                    parsed['quantity'] = Decimal('0')
                    parsed['normalized_quantity'] = Decimal('0')

        # --- Scope (always Scope 3 for travel) ---
        parsed['scope'] = TRAVEL_SCOPE
        parsed['supplier_vendor'] = vendor
        parsed['description'] = f"{trip_id} — {vendor}"

        # --- Final status ---
        if errors:
            status = 'FAILED'
            parsed = None
        elif flags:
            status = 'FLAGGED'
            parsed['flags'] = flags
        else:
            status = 'OK'

        results.append({
            'row_number': row_number,
            'status': status,
            'data': raw_data,
            'errors': errors,
            'parsed': parsed,
        })

    return results