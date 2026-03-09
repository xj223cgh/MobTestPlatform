# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import sys

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_para_text(el):
    out = []
    for t in el.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            out.append(t.text)
        if t.tail and t.tail.strip():
            out.append(t.tail)
    return ''.join(out)

def main():
    path = r'd:\PycharmProjects\MobTestPlatform\docs\论文\信计223陈国慧-本科毕业论文.docx'
    with zipfile.ZipFile(path, 'r') as z:
        xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    paras = []
    for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        t = get_para_text(p)
        if t.strip():
            paras.append(t)
    text = '\n'.join(paras)
    out_path = r'd:\PycharmProjects\MobTestPlatform\docs\论文\论文正文提取.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('OK', len(text), 'chars', file=sys.stderr)

if __name__ == '__main__':
    main()
