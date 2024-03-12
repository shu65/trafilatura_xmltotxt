from trafilatura.utils import normalize_unicode
from trafilatura.xml import replace_element_text, NEWLINE_ELEMS, HI_FORMATTING, SPECIAL_FORMATTING, sanitize
from html import unescape
import copy
import logging

LOGGER = logging.getLogger(__name__)

def replace_element_text(element, include_formatting):
    '''Determine element text based on text and tail'''
    # handle formatting: convert to markdown
    if include_formatting is True and element.text is not None:
        if element.tag in ('del', 'head'):
            if element.tag == 'head':
                try:
                    number = int(element.get('rend')[1])
                except (TypeError, ValueError):
                    number = 2
                element.text = f'{"#" * number} {element.text}'
            elif element.tag == 'del':
                element.text = f'~~{element.text}~~'
        elif element.tag == 'hi':
            rend = element.get('rend')
            if rend in HI_FORMATTING:
                element.text = f'{HI_FORMATTING[rend]}{element.text}{HI_FORMATTING[rend]}'
        elif element.tag == 'code':
            if '\n' in element.text:
                element.text = f'```\n{element.text}\n```'
            else:
                element.text = f'`{element.text}`'
    # handle links
    if element.tag == 'ref':
        if element.text is not None:
            link_text = f'[{element.text}]'
            if element.get('target') is not None:
                element.text = f"{link_text}({element.get('target')})"
            else:
                LOGGER.warning('missing link attribute: %s %s', element.text, element.attrib)
                element.text = link_text
        else:
            LOGGER.warning('empty link: %s %s', element.text, element.attrib)
    # handle text
    return (element.text or '') + (element.tail or '')

def tablecelltotxt(cell_xml, include_formatting):
  new_block = []
  new_raw_block = []
  last_element = None
  for element in cell_xml.iter('*'):
    last_element = element
    if element.text is None and element.tail is None:
        if element.tag == 'graphic':
            # add source, default to ''
            text = f'{element.get("title", "")} {element.get("alt", "")}'
            new_block.extend(['![', text.strip(), ']', '(', element.get('src', ''), ')'])
        #if element.tag in ('graphic', 'row', 'table'):
        #    new_block.append('\n')
        continue
    else:
      textelement = replace_element_text(element, include_formatting)
      if element.tag == "cell":
        new_block.extend([textelement, ' '])
        new_raw_block.extend([textelement, ' '])
      elif element.tag in NEWLINE_ELEMS:
          new_block.extend([NEWLINE_ELEMS[element.tag], textelement, ' '])
          new_raw_block.extend([textelement, ' '])
      else:
          if element.tag not in SPECIAL_FORMATTING:
              LOGGER.debug('unprocessed element in output: %s', element.tag)
          new_block.extend([textelement, ' '])
          new_raw_block.extend([textelement, ' '])
  new_text = sanitize(''.join(new_block))
  new_raw_text = sanitize(''.join(new_raw_block))
  return new_text, new_raw_text, last_element

def tabelrowtotxt(row_xml, include_formatting):
  n_cell = 0
  last_element = None
  new_block = []
  new_raw_block = []
  for element in row_xml:
    if element.tag != "cell":
      continue
    else:
      n_cell += 1
      cell_text, new_raw_text, last_element = tablecelltotxt(element, include_formatting)
      new_block.extend(["|", cell_text])
      new_raw_block.append(new_raw_text + "\n")
  new_block.append("|")
  new_text = ''.join(new_block)
  new_raw_text = ''.join(new_raw_block)
  return new_text, new_raw_text, last_element, n_cell

def tabletotxt(table_xml, include_formatting, table_formatting):
  n_cells_first_row = None
  valid_table = True
  last_element = None
  table_block = []
  raw_text_block = []
  for i, element in enumerate(table_xml):
    if element.tag != "row":
      continue
    else:
      new_text, new_raw_text, last_element, n_cell = tabelrowtotxt(element, include_formatting)
      #print("n_cells_first_row", n_cells_first_row, "n_cell", n_cell)
      if n_cells_first_row is None:
        n_cells_first_row = n_cell
      elif n_cells_first_row != n_cell:
        valid_table = False
      table_block.append(new_text)
      raw_text_block.append(new_raw_text)
      if i < (len(table_xml) - 1):
        table_block.append("\n")
        raw_text_block.append("\n")

  ret = ''.join(raw_text_block)
  if valid_table and include_formatting and table_formatting:
    ret = ''.join(table_block)
  return ret, last_element


def xmltotxt(xmloutput, include_formatting, table_formatting=False):
    '''Convert to plain text format and optionally preserve formatting as markdown.'''
    return_blocks = []
    new_block = []
    last_table_element = None
    for element in xmloutput.iter('*'):
        if last_table_element is not None:
          if last_table_element == element:
            last_table_element = None
            continue
          else:
            # skip table element
            continue
        if element.text is None and element.tail is None:
            if element.tag == 'graphic':
                # add source, default to ''
                text = f'{element.get("title", "")} {element.get("alt", "")}'
                new_block.extend(['![', text.strip(), ']', '(', element.get('src', ''), ')'])
            # newlines for textless elements
            if element.tag == 'graphic':
              new_block.append('\n')
            elif element.tag == 'table':
              if len(new_block) > 0:
                new_text = sanitize(''.join(new_block))
                return_blocks.append(new_text + '\n')
              table_block, last_table_element = tabletotxt(element, include_formatting=include_formatting, table_formatting=table_formatting)
              return_blocks.append(''.join(table_block) + '\n')
              new_block = []
            elif element.tag in ('graphic', 'row', 'table'):
                new_block.append('\n')
            continue
        else:
          # process text
          textelement = replace_element_text(element, include_formatting)
          if element.tag == "code":
            if '\n' in textelement:
              if len(new_block) > 0:
                new_text = sanitize(''.join(new_block))
                return_blocks.append(new_text + '\n')
              new_text = sanitize(textelement, preserve_space=True)
              return_blocks.append(new_text + '\n')
              new_block = []
            else:
              new_block.extend([" ", textelement, ' '])
          elif element.tag in NEWLINE_ELEMS:
              new_block.extend([NEWLINE_ELEMS[element.tag], textelement, '\n'])
          elif element.tag == 'comments':
              new_block.append('\n\n')
          else:
              if element.tag not in SPECIAL_FORMATTING:
                  LOGGER.debug('unprocessed element in output: %s', element.tag)
              new_block.extend([textelement, ' '])
    if len(new_block) > 0:
      new_text = sanitize(''.join(new_block))
      return_blocks.append(new_text)
    ret = unescape(''.join(return_blocks))
    ret = normalize_unicode(ret)
    return ret


#v = normalize_unicode(xmltotxt(copy.deepcopy(html_xml.body), include_formatting=True))
#print(normalize_unicode(xmltotxt(copy.deepcopy(html_xml.body), include_formatting=True)))
#print(xmltotxt(copy.deepcopy(html_xml.body), include_formatting=True))
#xmltotxt(copy.deepcopy(html_xml.body), include_formatting=True)