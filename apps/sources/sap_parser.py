import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation


# These are the canonical column names we expect after skipping the header block.
REQUIRED_COLUMNS = {
    'Buchungsdatum', 'Material', 'Menge', 'Einheit', 'Werk', 'Lieferant'
}


def parse_sap_date(date_str):
    """
    SAP exports dates as DD.MM.YYYY.
    Returns a date object or raises ValueError.
    """
    return datetime.strptime(date_str.strip(), '%d.%m.%Y').date()


def parse_sap_decimal(value_str):
    """
    SAP uses comma as decimal separator in German locale configs.
    '500,5' → Decimal('500.5')
    Raises InvalidOperation if unparseable.
    """
    cleaned = value_str.strip().replace(',', '.')
    return Decimal(cleaned)


def _is_header_row(row):
    """
    SAP exports have a metadata block at the top before actual data.
    We detect these by checking if the first meaningful cell starts with
    known header patterns, or if the row is entirely empty.
    """
    values = [v.strip() for v in row.values()]
    non_empty = [v for v in values if v]
    if not non_empty:
        return True
    first = non_empty[0]
    # Header block rows start with 'SAP', 'Plant:', 'Export'
    if any(first.startswith(prefix) for prefix in ('SAP', 'Plant:', 'Export')):
        return True
    return False


def parse_sap_file(file_content: bytes) -> list[dict]:
    text = file_content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text), delimiter=';')

    results = []
    row_number = 0

    for raw_row in reader:
        row_number += 1

        if _is_header_row(raw_row):
            continue

        errors = []
        flags = []
        parsed = {}
        raw_data = dict(raw_row)

        date_str = raw_row.get('Buchungsdatum', '').strip()
        material = raw_row.get('Material', '').strip()
        quantity_str = raw_row.get('Menge', '').strip()
        unit_str = raw_row.get('Einheit', '').strip().upper()
        plant_code = raw_row.get('Werk', '').strip().upper()
        vendor = raw_row.get('Lieferant', '').strip()

        if not date_str:
            errors.append('Missing Buchungsdatum (date)')
        else:
            try:
                parsed['activity_date'] = parse_sap_date(date_str)
            except ValueError:
                errors.append(f'Invalid date format: {date_str!r} (expected DD.MM.YYYY)')

        if not material:
            errors.append('Missing Material code')
        else:
            parsed['material'] = material

        if not quantity_str:
            errors.append('Missing Menge (quantity)')
        else:
            try:
                parsed['quantity'] = parse_sap_decimal(quantity_str)
                if parsed['quantity'] == 0:
                    flags.append('Zero quantity — possible data entry error')
            except InvalidOperation:
                errors.append(f'Invalid quantity: {quantity_str!r}')

        if not unit_str:
            errors.append('Missing Einheit (unit)')
        else:
            from apps.sources.sap_lookups import UNIT_NORMALIZATION, UNIT_CONVERSION_FACTORS
            if unit_str not in UNIT_NORMALIZATION:
                errors.append(f'Unknown unit: {unit_str!r} — cannot normalize')
            else:
                parsed['original_unit'] = unit_str
                parsed['normalized_unit'] = UNIT_NORMALIZATION[unit_str]
                factor = UNIT_CONVERSION_FACTORS[unit_str]
                if 'quantity' in parsed:
                    parsed['normalized_quantity'] = parsed['quantity'] * Decimal(str(factor))

        if not plant_code:
            errors.append('Missing Werk (plant code)')
        else:
            from apps.sources.sap_lookups import PLANT_LOOKUP
            parsed['plant_code'] = plant_code
            if plant_code not in PLANT_LOOKUP:
                flags.append(f'Unknown plant code: {plant_code!r} — not in lookup table')
            else:
                parsed['location'] = PLANT_LOOKUP[plant_code]

        parsed['supplier_vendor'] = vendor if vendor else ''

        if 'material' in parsed:
            from apps.sources.sap_lookups import MATERIAL_SCOPE, MATERIAL_CATEGORY
            parsed['scope'] = MATERIAL_SCOPE.get(material, 'SCOPE_1')
            parsed['category'] = MATERIAL_CATEGORY.get(
                material,
                f'Stationary Combustion - Unknown ({material})'
            )

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