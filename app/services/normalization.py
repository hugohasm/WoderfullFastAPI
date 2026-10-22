import re
import unicodedata


def normalize_text(value: str | None, *, keep_spaces: bool = True) -> str:
    if value is None:
        return ''
    text = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().strip()
    if keep_spaces:
        text = re.sub(r'\s+', ' ', text)
    else:
        text = re.sub(r'\s+', '', text)
    text = text.replace('&', ' and ')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return text.strip()


def build_full_name(first_name: str | None, last_name: str | None) -> str:
    parts = [part for part in [first_name, last_name] if part and str(part).strip()]
    return ' '.join(parts).strip()


def build_record_key(record: dict) -> str:
    seed = [
        str(record.get('first_name') or '').strip(),
        str(record.get('last_name') or '').strip(),
        str(record.get('clinic_name') or '').strip(),
        str(record.get('location') or '').strip(),
        str(record.get('speciality') or '').strip(),
        str(record.get('address') or '').strip(),
        str(record.get('email') or '').strip(),
        str(record.get('phone') or '').strip(),
    ]
    return '|'.join(seed)


def apply_spanish_b_v_correction(value: str | None) -> str:
    if not value:
        return ''
    text = normalize_text(value)
    text = text.replace('v', 'b')
    return text
