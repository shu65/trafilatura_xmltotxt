from lxml import html
from trafilatura.settings import DEFAULT_CONFIG
import trafilatura
import trafilatura_xmltotxt


ZERO_CONFIG = DEFAULT_CONFIG
ZERO_CONFIG['DEFAULT']['MIN_OUTPUT_SIZE'] = '0'
ZERO_CONFIG['DEFAULT']['MIN_EXTRACTED_SIZE'] = '0'

def test_tabel():
    my_document = html.fromstring('<html><body><p>table 1</p><table><tr><th>cell title 0</th><th>cell title 1</th></tr><tr><td>cell 0</td><td>cell 1</td></tr></table><p>table end</p></body></html>')
    my_xml = trafilatura.bare_extraction(my_document, output_format='txt', include_formatting=True, config=ZERO_CONFIG, as_dict=False)
    my_result = trafilatura_xmltotxt.xmltotxt(my_xml.body, include_formatting=True, table_formatting=True)
    assert my_result == 'table 1\n|cell title 0|cell title 1|\n|cell 0|cell 1|\ntable end'

def test_invalid_tabel():
    my_document = html.fromstring('<html><body><p>table 1</p><table><th>cell title 1</th></tr><tr><td>cell 0</td><td>cell 1</td></tr></table><p>table end</p></body></html>')
    my_xml = trafilatura.bare_extraction(my_document, output_format='txt', include_formatting=True, config=ZERO_CONFIG, as_dict=False)
    my_result = trafilatura_xmltotxt.xmltotxt(my_xml.body, include_formatting=True, table_formatting=True)
    assert my_result == 'table 1\ncell title 1\n\ncell 0\ncell 1\n\ntable end'

def test_raw_tabel():
    my_document = html.fromstring('<html><body><p>table 1</p><table><tr><th>cell title 0</th><th>cell title 1</th></tr><tr><td>cell 0</td><td>cell 1</td></tr></table><p>table end</p></body></html>')
    my_xml = trafilatura.bare_extraction(my_document, output_format='txt', include_formatting=True, config=ZERO_CONFIG, as_dict=False)
    my_result = trafilatura_xmltotxt.xmltotxt(my_xml.body, include_formatting=True, table_formatting=False)
    assert my_result == 'table 1\ncell title 0\ncell title 1\n\ncell 0\ncell 1\n\ntable end'