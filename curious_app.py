"""
Veritas Curious — unified backend for Veritas Protocol ecosystem.
Aggregates Veritas Protocol (witness) and Veritas Foresight into one API.

Architecture:
    /api/witness   — proxy to veritas-protocol
    /api/foresight — proxy to veritas-foresight
    /api/curious   — unified: text → witness analysis + foresight resonance
"""

import os
import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Service URLs ───────────────────────────────────────────────────────────────
PROTOCOL_URL = os.environ.get(
    'PROTOCOL_URL',
    'https://veritas-protocol.onrender.com'
).rstrip('/')

FORESIGHT_URL = os.environ.get(
    'FORESIGHT_URL',
    'https://veritas-foresight.onrender.com'
).rstrip('/')

TIMEOUT = int(os.environ.get('SERVICE_TIMEOUT', '30'))


# ── HTTP helpers ───────────────────────────────────────────────────────────────
def _post(url: str, body: dict, timeout: int = TIMEOUT) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _get(url: str, timeout: int = TIMEOUT) -> dict:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


# ── Frontend ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return open('curious_index.html', encoding='utf-8').read()


# ── Health ─────────────────────────────────────────────────────────────────────
@app.route('/api/health')
def health():
    services = {}

    try:
        _get(f'{PROTOCOL_URL}/api/health', timeout=8)
        services['protocol'] = 'ok'
    except Exception as e:
        services['protocol'] = f'error: {str(e)[:60]}'

    try:
        _get(f'{FORESIGHT_URL}/api/health', timeout=8)
        services['foresight'] = 'ok'
    except Exception as e:
        services['foresight'] = f'error: {str(e)[:60]}'

    overall = 'ok' if all(v == 'ok' for v in services.values()) else 'degraded'
    return jsonify({
        'status': overall,
        'services': services,
        'protocol_url': PROTOCOL_URL,
        'foresight_url': FORESIGHT_URL,
    })


# ── Witness proxy ──────────────────────────────────────────────────────────────
@app.route('/api/witness', methods=['POST'])
def witness():
    """
    Proxy to Veritas Protocol witness analysis.
    Body: { text, url? }
    """
    try:
        data = request.get_json(force=True) or {}
        text = data.get('text', '').strip()
        url = data.get('url', '').strip()

        if not text and not url:
            return jsonify({'error': 'text or url required'}), 400

        payload = {}
        if text:
            payload['text'] = text
        if url:
            payload['url'] = url

        result = _post(f'{PROTOCOL_URL}/api/analyze', payload)
        return jsonify(result)

    except urllib.error.URLError as e:
        return jsonify({'error': f'Protocol service unavailable: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Foresight proxy ────────────────────────────────────────────────────────────
@app.route('/api/foresight/simulate', methods=['POST'])
def foresight_simulate():
    """Proxy to Foresight simulate endpoint."""
    try:
        data = request.get_json(force=True) or {}
        result = _post(f'{FORESIGHT_URL}/api/simulate', data)
        return jsonify(result)
    except urllib.error.URLError as e:
        return jsonify({'error': f'Foresight service unavailable: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/foresight/battle', methods=['POST'])
def foresight_battle():
    """Proxy to Foresight battle endpoint."""
    try:
        data = request.get_json(force=True) or {}
        result = _post(f'{FORESIGHT_URL}/api/battle', data)
        return jsonify(result)
    except urllib.error.URLError as e:
        return jsonify({'error': f'Foresight service unavailable: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/foresight/field')
def foresight_field():
    """Proxy to Foresight field endpoint."""
    try:
        result = _get(f'{FORESIGHT_URL}/api/field')
        return jsonify(result)
    except urllib.error.URLError as e:
        return jsonify({'error': f'Foresight service unavailable: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Curious — unified analysis ─────────────────────────────────────────────────
@app.route('/api/curious', methods=['POST'])
def curious():
    """
    Unified analysis: text → witness + foresight in one call.

    Flow:
        1. Witness analyzes text for manipulation/integrity
        2. Foresight simulates where this text pushes the field
        3. Return combined result with synthesis

    Body: {
        text: str,
        steps: int (foresight steps, default 5),
        use_field: bool (use live RSS context, default true)
    }
    """
    try:
        data = request.get_json(force=True) or {}
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'text is required'}), 400

        steps = max(1, min(int(data.get('steps', 5)), 10))
        use_field = data.get('use_field', True)

        # Run both in sequence (could parallelize but keep simple)
        witness_result = None
        foresight_result = None
        witness_error = None
        foresight_error = None

        # 1. Witness analysis
        try:
            witness_result = _post(f'{PROTOCOL_URL}/api/analyze', {'text': text})
        except Exception as e:
            witness_error = str(e)[:120]

        # 2. Foresight simulation — use text as argument
        try:
            foresight_result = _post(f'{FORESIGHT_URL}/api/simulate', {
                'argument': text,
                'steps': steps,
                'use_field': use_field,
            })
        except Exception as e:
            foresight_error = str(e)[:120]

        # 3. Synthesize
        synthesis = _synthesize(witness_result, foresight_result)

        # 4. Haiku interpretation (non-blocking — skip if slow)
        lang = data.get('lang', 'uk')
        interpretation = _haiku_interpret(text, synthesis, lang=lang)

        return jsonify({
            'text': text,
            'witness': witness_result,
            'foresight': foresight_result,
            'synthesis': synthesis,
            'interpretation': interpretation,
            'errors': {
                k: v for k, v in {
                    'witness': witness_error,
                    'foresight': foresight_error,
                }.items() if v
            },
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


DARK_FUTURES = {
    'Nuclear-Escalation', 'AI-Control-Instrument',
    'Control-Consolidation', 'Russia-Collapse', 'Climate-Tipping',
}
LIGHT_FUTURES = {
    'Ukraine-Victory', 'Green-Symbiosis',
    'Resilient-Adaptation', 'Post-Scarcity',
}


def _synthesize(witness: dict, foresight: dict) -> dict:
    """
    Build synthesis from witness + foresight results.

    Logic:
        MANIPULATIVE_NARRATIVE — witness found manipulation (regardless of foresight)
        DARK_ATTRACTOR         — text is clean but resonates with dangerous futures
        CONSTRUCTIVE_ATTRACTOR — text resonates with positive futures
        NEUTRAL_SIGNAL         — clean text, uncertain or neutral future
    """
    if not witness and not foresight:
        return {'verdict': 'NO_DATA', 'dominant_future': None, 'insights': []}

    insights = []
    dominant = ''
    is_manipulative = False

    # Witness signals
    if witness:
        w_verdict = witness.get('verdict') or witness.get('preservation_verdict', '')
        w_score = witness.get('score', witness.get('preservation_score', 0))
        clean_verdicts = ('CLEAN', 'STRUCTURAL_INTEGRITY', 'STRUCTURAL_INTEGRITY ')

        if w_verdict and w_verdict.strip() not in clean_verdicts:
            is_manipulative = True
            insights.append(f'Witness: {w_verdict.strip()} (score {w_score:.2f})')
        else:
            insights.append(f'Witness: структурна цілісність (score {w_score:.2f})')

    # Foresight signals
    if foresight:
        fs = foresight.get('final_state', {})
        dominant = fs.get('dominant', '')
        entropy = fs.get('entropy', 0)

        if dominant:
            insights.append(f'Резонує з: {dominant}')

        if entropy < 0.5:
            insights.append('Поле конвергує — траєкторія визначена')
        elif entropy > 1.5:
            insights.append('Висока невизначеність — багато рівноймовірних майбутніх')

    # Combined verdict — witness takes priority
    if is_manipulative:
        combined = 'MANIPULATIVE_NARRATIVE'
    elif dominant in DARK_FUTURES:
        combined = 'DARK_ATTRACTOR'
    elif dominant in LIGHT_FUTURES:
        combined = 'CONSTRUCTIVE_ATTRACTOR'
    else:
        combined = 'NEUTRAL_SIGNAL'

    return {
        'verdict': combined,
        'dominant_future': dominant or None,
        'insights': insights,
    }


def _haiku_interpret(text: str, synthesis: dict, lang: str = 'uk') -> str:
    """
    Use Claude Haiku to generate human-readable interpretation of the synthesis.
    Returns plain text explanation. Falls back to empty string on error.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return ''

    verdict = synthesis.get('verdict', '')
    dominant = synthesis.get('dominant_future', '')
    insights = synthesis.get('insights', [])

    if lang == 'uk':
        prompt = f"""Ти пояснювач результатів системи Veritas Curious.

ВАЖЛИВО: Твоя задача — пояснити що ВИМІРЯЛА система, а не робити власні висновки.
Не додавай власний аналіз маніпуляцій якщо Свідок їх не знайшов.
Не використовуй markdown. Без заголовків. Просто текст 3-4 речення.

Що виміряла система:
- Свідок: {insights[0] if insights else 'немає даних'}
- Foresight домінантне майбутнє: {dominant}
- Загальний вердикт: {verdict}

Поясни просто: що означає цей вердикт і чому саме ці ключові слова тексту резонують з майбутнім "{dominant}".
Говори про вимірювання системи — не про зміст тексту."""
    else:
        prompt = f"""You are an explainer for Veritas Curious system results.

IMPORTANT: Your task is to explain what the system MEASURED, not to add your own analysis.
Do not identify manipulation if Witness did not find it.
No markdown. No headers. Plain text, 3-4 sentences only.

What the system measured:
- Witness: {insights[0] if insights else 'no data'}
- Foresight dominant future: {dominant}
- Synthesis verdict: {verdict}

Explain simply: what this verdict means and why the keywords in this text resonate with the future "{dominant}".
Talk about the system measurements — not about the content itself."""

    try:
        payload = {
            'model': 'claude-haiku-4-5-20251001',
            'max_tokens': 400,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=data,
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result['content'][0]['text'].strip()
    except Exception as e:
        print(f'[curious] haiku interpret error: {e}')
        return 


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10002))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
