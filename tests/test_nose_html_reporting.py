from __future__ import print_function

from process_tests import dump_on_error
from process_tests import TestProcess
from process_tests import wait_for_strings

import re
import os.path

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../src/nose_html_reporting/templates')
TEMPLATE = 'report.html'

TIMEOUT = 10


def test_sample():
    test_detail = {
        'test_sample': {
            'fail': 1,
            'skip': 1,
            'error': 1,
            'success': 1,
            'total': 4
        },
        'test_sample.TestMainCase': {
            'fail': 2,
            'skip': 0,
            'error': 0,
            'success': 1,
            'total': 3
        },
        'test_sample.TestFailedSetupCase': {
            'fail': 0,
            'skip': 0,
            'error': 1,
            'success': 0,
            'total': 1
        },
        'test_sample.TestSecondCase': {
            'fail': 1,
            'skip': 0,
            'error': 0,
            'success': 1,
            'total': 2
        }
    }

    test_summary = {
        'fail': sum([v.get('fail') for v in test_detail.values()]),
        'skip': sum([v.get('skip') for v in test_detail.values()]),
        'error': sum([v.get('error') for v in test_detail.values()]),
        'success': sum([v.get('success') for v in test_detail.values()]),
        'total': sum([v.get('total') for v in test_detail.values()])
    }

    test_count = test_summary.get('total')

    with TestProcess(
        'coverage', 'run', 'tests/nosetests.py',
        '--verbose',
        '--with-html',
        '--html-report=sample.html',
        '--html-report-template=%s' % os.path.join(TEMPLATE_DIR, TEMPLATE),
        'tests/test_sample.py'
    ) as proc:
        with dump_on_error(proc.read):
            wait_for_strings(proc.read, TIMEOUT, 'Ran %d tests in' % test_count)

    output = open('sample.html').read()

    map(lambda key: test_detail.get(key).update({'name': key}), test_detail.keys())
    for test_item in test_detail.values():
        assert """<tr>
                    <td>{name}</td>
                    <td>{fail}</td>
                    <td>{skip}</td>
                    <td>{success}</td>
                    <td>{total}</td>
                </tr>""".format(**test_item) in output

    assert """<tr>
                <td><strong>Total</strong></td>
                <td>{fail}</td>
                <td>{skip}</td>
                <td>{success}</td>
                <td>{total}</td>
            </tr>""".format(**test_summary) in output

    test = 'test_sample.TestMainCase'
    assert '<h2>{name} ({fail} failures, {error} errors)</h2>'.format(**test_detail.get(test)) in output
    assert '<section id="{}:test_Mb">'.format(test) in output
    assert '<h3>test_b: <strong>' in output
    assert '<li><a class="failed" href="#{}:test_Mb">test_Mb</a></li>'.format(test) in output

    test = 'test_sample'
    assert '<h2>{name} ({fail} failures, {error} errors)</h2>'.format(**test_detail.get(test)) in output
    assert '<section id="{}:test_b">'.format(test) in output
    assert '<h3>test_b: <strong>' in output
    assert '<li><a class="failed" href="#{}:test_b">test_b</a></li>'.format(test) in output
    assert '<li><a class="success">test_a</a></li>' in output
    assert '<li><a class="success">test_a</a></li>' in output

    test = 'test_sample.TestFailedSetupCase'
    assert "<h2>{name} ({fail} failures, {error} errors)</h2>".format(**test_detail.get(test)) in output

    title_pattern = r'<h1>TEST REPORT.*</h1>'
    assert re.search(title_pattern, output)

    timestamp_pattern = r'<h1>.* \| [0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2} UTC.*</h1>'
    assert re.search(timestamp_pattern, output)

    elapsed_time_pattern = r'<h1>.* \| Elapsed time: .*[0-9]+m [0-9]+s.*</h1>'
    assert re.search(elapsed_time_pattern, output)
