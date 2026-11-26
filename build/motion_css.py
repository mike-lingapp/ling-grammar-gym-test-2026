"""Convert Figma get_motion_context JSON into scoped CSS.
Usage: python3 motion_css.py <motion.json> <prefix>  -> prints CSS
Each animated node is targeted by [data-m="<fallbackNodeId>"] inside .slide-<prefix>.
Keyframe names are prefixed to avoid collisions across slides."""
import json, re, sys

def split_blocks(css):
    props, kfs, decl = [], [], []
    i = 0
    while i < len(css):
        if css.startswith('@property', i) or css.startswith('@keyframes', i):
            j = css.index('{', i); depth = 0; k = j
            while True:
                if css[k] == '{': depth += 1
                elif css[k] == '}':
                    depth -= 1
                    if depth == 0: break
                k += 1
            (props if css.startswith('@property', i) else kfs).append(css[i:k+1])
            i = k + 1
        else:
            decl.append(css[i]); i += 1
    return props, kfs, ''.join(decl).strip()

def convert(path, prefix, scope=None):
    j = json.load(open(path))
    scope = scope or f'.slide-{prefix}'
    out, seen_props = [], set()
    for n in j['nodes']:
        css = n['codeSnippets'].get('css', '')
        if not css: continue
        css = re.sub(r'\bkf_', f'kf_{prefix}_', css)
        props, kfs, decl = split_blocks(css)
        for p in props:
            name = p.split('{')[0]
            if name not in seen_props:
                seen_props.add(name); out.append(p)
        out.append(f'{scope} [data-m="{n["fallbackNodeId"]}"] {{ {decl} }}')
        out.extend(kfs)
    return '\n'.join(out)

if __name__ == '__main__':
    print(convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
