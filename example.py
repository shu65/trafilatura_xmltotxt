import trafilatura
import trafilatura_xmltotxt

downloaded = trafilatura.fetch_url('https://www.mattari-benkyo-note.com/2023/01/29/cuda-reduction2023/')

html_xml = trafilatura.bare_extraction(downloaded, include_formatting=True, as_dict=False, output_format="txt")
print(trafilatura_xmltotxt.xmltotxt(html_xml.body, include_formatting=True))