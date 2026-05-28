import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation


REQUIRED_COLUMNS = {
    'Meter_ID', 'Site_Name', 'Billing_Period_Start',
    'Billing_Period_End', 'Consumption_kWh'
}


def parse_utility_date(date_str):
    """
    Utility exports dates as DD/MM/YYYY.
    Returns a date object or raises ValueError.
    """
    return datetime.strptime(date_str.strip(), '%d/%m/%Y').date()


def parse_utility_decimal(value_str):
    cleaned = value_str.strip().replace(',', '.')
    return Decimal(cleaned)


def check_period_crosses_month(start_date, end_date):
    """
    Billing periods that cross month boundaries are flagged.
    Analysts need to know because carbon reporting is typically monthly.
    """
    return start_date.month != end_date.month or start_date.year != end_date.year


def parse_utility_file(file_content: bytes) -> list[dict]:
    """
    Parses a utility electricity CSV export.

    Unlike SAP, utility CSVs have a clean single-row header.
    Key complications handled:
      - Billing periods not aligned to calendar months
      - Missing unit fields (default to kWh if absent)
      - Zero consumption flagging
      - Duplicate meter + period detection

    Returns same structure as SAP parser:
      [{row_number, status, data, errors, parsed}]
    """
    text = file_content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))

    results = []
    row_number = 0

    # Track meter+period combinations to detect duplicates
    seen_meter_periods = {}

    for raw_row in reader:
        row_number += 1
        errors = []
        flags = []
        parsed = {}
        raw_data = dict(raw_row)

        meter_id = raw_row.get('Meter_ID', '').strip()
        site_name = raw_row.get('Site_Name', '').strip()
        start_str = raw_row.get('Billing_Period_Start', '').strip()
        end_str = raw_row.get('Billing_Period_End', '').strip()
        consumption_str = raw_row.get('Consumption_kWh', '').strip()
        unit_str = raw_row.get('Unit', '').strip()
        account = raw_row.get('Account_Number', '').strip()

        # --- Meter ID ---
        if not meter_id:
            errors.append('Missing Meter_ID')
        else:
            parsed['meter_id'] = meter_id

        # --- Site name ---
        parsed['site_name'] = site_name if site_name else ''

        # --- Billing period start ---
        if not start_str:
            errors.append('Missing Billing_Period_Start')
        else:
            try:
                parsed['period_start'] = parse_utility_date(start_str)
            except ValueError:
                errors.append(f'Invalid start date: {start_str!r} (expected DD/MM/YYYY)')

        # --- Billing period end ---
        if not end_str:
            errors.append('Missing Billing_Period_End')
        else:
            try:
                parsed['period_end'] = parse_utility_date(end_str)
            except ValueError:
                errors.append(f'Invalid end date: {end_str!r} (expected DD/MM/YYYY)')

        # --- Cross-month billing period flag ---
        if 'period_start' in parsed and 'period_end' in parsed:
            if check_period_crosses_month(parsed['period_start'], parsed['period_end']):
                flags.append(
                    f"Billing period crosses month boundary: "
                    f"{parsed['period_start']} to {parsed['period_end']} — "
                    f"may need proration for monthly reporting"
                )
            # Use period_start as the canonical activity_date
            parsed['activity_date'] = parsed['period_start']

        # --- Consumption ---
        if not consumption_str:
            errors.append('Missing Consumption_kWh')
        else:
            try:
                parsed['quantity'] = parse_utility_decimal(consumption_str)
                if parsed['quantity'] == 0:
                    flags.append('Zero consumption — possible missing data or inactive meter')
            except InvalidOperation:
                errors.append(f'Invalid consumption value: {consumption_str!r}')

        # --- Unit --- default to kWh if missing (reasonable assumption, flagged)
        if not unit_str:
            parsed['original_unit'] = 'kWh'
            parsed['normalized_unit'] = 'kWh'
            flags.append('Missing unit field — defaulted to kWh, verify with source')
        else:
            parsed['original_unit'] = unit_str
            parsed['normalized_unit'] = 'kWh'  # All electricity normalized to kWh

        if 'quantity' in parsed:
            parsed['normalized_quantity'] = parsed['quantity']  # kWh → kWh, no conversion needed

        # --- Duplicate meter + period detection ---
        if 'meter_id' in parsed and 'period_start' in parsed and 'period_end' in parsed:
            period_key = (parsed['meter_id'], str(parsed['period_start']), str(parsed['period_end']))
            if period_key in seen_meter_periods:
                flags.append(
                    f"Duplicate meter+period: {parsed['meter_id']} "
                    f"already seen for {parsed['period_start']} to {parsed['period_end']}"
                )
            else:
                seen_meter_periods[period_key] = row_number

        # --- Location and vendor ---
        parsed['location'] = site_name
        parsed['supplier_vendor'] = account
        parsed['scope'] = 'SCOPE_2'
        parsed['category'] = 'Purchased Electricity'

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