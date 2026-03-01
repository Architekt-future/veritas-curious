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

        return jsonify({
            'text': text,
            'witness': witness_result,
            'foresight': foresight_result,
            'synthesis': synthesis,
            'errors': {
                k: v for k, v in {
                    'witness': witness_error,
                    'foresight': foresight_error,
                }.items() if v
            },
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _synthesize(witness: dict, foresight: dict) -> dict:
    """
    Build synthesis from witness + foresight results.
    Returns a unified verdict and key insights.
    """
    if not witness and not foresight:
        return {'verdict': 'NO_DATA', 'insight': 'Both services unavailable.'}

    verdict_parts = []
    insights = []

    # Witness signals
    if witness:
        w_verdict = witness.get('verdict') or witness.get('preservation_verdict', '')
        w_score = witness.get('score', witness.get('preservation_score', 0))

        if w_verdict and w_verdict not in ('CLEAN', 'STRUCTURAL_INTEGRITY'):
            verdict_parts.append('MANIPULATIVE')
            insights.append(f'Witness: {w_verdict} (score {w_score:.2f})')
        else:
            verdict_parts.append('CLEAN')

    # Foresight signals
    if foresight:
        fs = foresight.get('final_state', {})
        dominant = fs.get('dominant', '')
        entropy = fs.get('entropy', 0)

        if dominant:
            insights.append(f'Resonates with: {dominant}')

        if entropy < 0.3:
            insights.append('Field strongly converged — high certainty trajectory')
        elif entropy > 0.7:
            insights.append('Field highly uncertain — multiple futures equally possible')

    # Combined verdict
    if 'MANIPULATIVE' in verdict_parts:
        combined = 'MANIPULATIVE_NARRATIVE'
    elif dominant in ('Nuclear-Escalation', 'AI-Control-Instrument', 'Control-Consolidation'):
        combined = 'DARK_ATTRACTOR'
    elif dominant in ('Ukraine-Victory', 'Green-Symbiosis', 'Resilient-Adaptation'):
        combined = 'CONSTRUCTIVE_ATTRACTOR'
    else:
        combined = 'NEUTRAL_SIGNAL'

    return {
        'verdict': combined,
        'dominant_future': dominant if foresight else None,
        'insights': insights,
    }


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10002))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
