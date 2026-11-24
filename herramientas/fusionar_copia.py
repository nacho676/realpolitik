# Merges a copy of a Millennium Dawn file with the new MD version, without an old MD baseline.
# Run it from the folder that holds both mods (.../Hearts of Iron IV/mod), after changing MD below if the folder name changed.
#   python MD_Realismo/herramientas/fusionar_copia.py show interface/topbar.gui        lists every difference, numbered
#   python MD_Realismo/herramientas/fusionar_copia.py apply interface/topbar.gui 0,2,5  keeps OUR side only for those numbers
#   ... apply <file> ins   keeps our side for every pure insertion (good for "rare_earths = N" lines); ... all   keeps ours everywhere
# Everything not listed takes MD's new text. A difference that only we have is ours; one that only MD has is MD's update.
# Back the file up first: apply overwrites the copy in MD_Realismo.
import sys,difflib,os,json
MD='Millennium-Dawn-2.0.3/'; MY='MD_Realismo/'
def rd(p):
    b=open(p,'rb').read(); bom=b.startswith(b'\xef\xbb\xbf'); crlf=b'\r\n' in b
    return b.decode('utf-8-sig').replace('\r\n','\n').split('\n'),bom,crlf
def ops(path):
    n,_,_=rd(MD+path); o,_,_=rd(MY+path)
    sm=difflib.SequenceMatcher(None,n,o,autojunk=False)
    return n,o,[t for t in sm.get_opcodes() if t[0]!='equal']
def show(path):
    n,o,ps=ops(path)
    for i,(t,a,b,c,d) in enumerate(ps):
        print(f'--[{i}] {t} new[{a+1}:{b}] ours[{c+1}:{d}]')
        for l in n[a:b]: print('  MD  :',l[:150])
        for l in o[c:d]: print('  OURS:',l[:150])
def apply(path,take,keep_md=()):
    """take: set of op indices (or 'inserts') whose OURS side replaces/inserts; others keep MD."""
    n,o,ps=ops(path); _,bom,crlf=rd(MD+path)
    out=[];pos=0
    for i,(t,a,b,c,d) in enumerate(ps):
        out+=n[pos:a]; pos=b
        if (take=='all' or (take=='ins' and t=='insert') or (isinstance(take,set) and i in take)): out+=o[c:d]
        else: out+=n[a:b]
    out+=n[pos:]
    s='\n'.join(out)
    if crlf: s=s.replace('\n','\r\n')
    d=s.encode('utf-8')
    if bom: d=b'\xef\xbb\xbf'+d
    open(MY+path,'wb').write(d)
if __name__=='__main__':
    cmd=sys.argv[1]; p=sys.argv[2]
    if cmd=='show': show(p)
    else:
        t=sys.argv[3]; take='ins' if t=='ins' else 'all' if t=='all' else set(int(x) for x in t.split(',') if x!='')
        apply(p,take)
