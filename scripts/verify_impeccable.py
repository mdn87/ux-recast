"""Verify the real Windows npm detector against the evidence helper; installs nothing.

Run from the repository root with an explicitly installed impeccable@4.8.0 under
--tool-root, an existing Chromium --browser, and a fresh --output directory.
Raw output and helper records are retained for inspection. This checks the tool
contract, not whether its design opinions identify actual user-task problems.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import threading

from ux_recast.evidence.impeccable_detect import DetectError, detect


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-root', type=Path, required=True)
    parser.add_argument('--browser', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tool = args.tool_root.resolve()
    output = args.output.resolve()
    browser = args.browser.resolve()
    assert os.name == 'nt', 'This verification recipe targets the Windows npm launcher'
    assert browser.is_file(), 'Supply an existing Chromium executable'
    package = tool / 'node_modules/impeccable'
    engine_package = tool / 'node_modules/@impeccable/cli-windows-x64'
    engine = engine_package / 'bin/impeccable.exe'
    metadata = json.loads((package / 'package.json').read_text())
    engine_metadata = json.loads((engine_package / 'package.json').read_text())
    assert metadata['version'] == '4.8.0'
    assert engine_metadata['version'] == '0.1.18'
    checksum = sha256(engine)
    manifest = (package / 'skill/scripts/engine-checksums.txt').read_text()
    assert f'0.1.18 impeccable-windows-x64.exe {checksum}' in manifest
    output.mkdir(parents=True, exist_ok=False)
    # The complete engine is present; keep any tool-owned state inside this run.
    os.environ['IMPECCABLE_BIN'] = str(engine)
    os.environ['IMPECCABLE_HOME'] = str(output / 'tool-home')
    os.environ['IMPECCABLE_BROWSER'] = str(browser)
    os.environ['PATH'] = str(tool / 'node_modules/.bin') + os.pathsep + os.environ['PATH']
    fixture = root / 'fixtures/contact-request'
    hashes = {name: sha256(fixture / name) for name in ('index.before.html', 'index.html')}
    clean = output / 'clean.css'
    clean.write_text('body { color: #222; background: #fff; }\n', encoding='utf-8')
    cases = []

    def save(name, value):
        (output / f'{name}.json').write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

    def check(name, target, expected_exit, viewport=None):
        arguments = ['detect', '--json', *(['--viewport', viewport] if viewport else []), str(target)]
        # Direct Node invocation is independent of the helper's Windows batch quoting.
        raw = subprocess.run([shutil.which('node'), str(package / 'cli/bin/cli.js'), *arguments],
                             capture_output=True, text=True, encoding='utf-8', timeout=120)
        save(name + '-raw', {'arguments': arguments, 'exit_code': raw.returncode,
                            'stdout': raw.stdout, 'stderr': raw.stderr})
        assert raw.returncode == expected_exit, (name, raw.returncode, raw.stderr)
        if expected_exit == 1:
            try:
                detect(target, viewport=viewport)
            except DetectError as error:
                save(name + '-helper', {'error': str(error)})
                assert 'exited 1' in str(error)
            else:
                raise AssertionError('Operational error was not raised')
            cases.append({'case': name, 'exit_code': 1, 'result': 'error propagated'})
            return
        record = detect(target, viewport=viewport)
        save(name + '-helper', record)
        hits = json.loads(raw.stdout)
        assert record['status'] == ('findings' if expected_exit == 2 else 'clean')
        assert record['provenance']['version'] == '4.8.0'
        assert record['provenance']['exit_code'] == expected_exit
        assert record['provenance']['arguments'] == arguments
        assert len(record['findings']) == len(hits)
        for mapped, hit in zip(record['findings'], hits):
            for dest, source in [('rule_id', 'antipattern'), ('rule_name', 'name'),
                                 ('description', 'description'), ('observed', 'snippet'),
                                 ('file', 'file'), ('line', 'line'),
                                 ('tool_severity', 'severity'), ('tool_category', 'category')]:
                assert mapped[dest] == hit.get(source), (name, dest)
            assert mapped['kind'] == 'implementation'
            assert mapped['category'] == 'heuristic concern'
            assert mapped['advisory'] == (hit.get('advisory') is True)
        cases.append({'case': name, 'exit_code': expected_exit, 'result': record['status'],
                      'rules': [hit['antipattern'] for hit in hits]})

    check('static-before', fixture / 'index.before.html', 2)
    check('static-after', fixture / 'index.html', 2)
    check('static-clean', clean, 0)
    check('missing-target', output / 'does-not-exist.html', 1)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(fixture)))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        # Ampersand also exercises the actual npm batch launcher's URL argument handling.
        check('rendered-mobile', f'http://127.0.0.1:{server.server_port}/index.html?scenario=success&probe=1',
              2, viewport='390x844')
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
    assert hashes == {name: sha256(fixture / name) for name in hashes}
    save('summary', {'ran_at': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
                     'python': platform.python_version(), 'npm_package': metadata['version'],
                     'engine_package': engine_metadata['version'], 'engine_sha256': checksum,
                     'browser': str(browser), 'browser_sha256': sha256(browser),
                     'fixture_sha256': hashes, 'cases': cases})
    print(json.dumps({'status': 'passed', 'cases': len(cases), 'output': str(output)}))


if __name__ == '__main__':
    main()
