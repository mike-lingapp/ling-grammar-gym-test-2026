/*
 * Grammar Gym prototype runtime (standalone hosting).
 * Renders the canvas's .dc.html components outside Claude: reads each file's template,
 * styles and Component class, and draws them with Preact. The component files are used
 * as they are, so updating the site = replacing files in /components.
 *
 * Usage (see a/index.html):  GymRuntime.start({ root: 'GymFlow', langs: ['sr', ...], mount: '#phone' })
 */
(function () {
  const { h, render, Component: PComponent, Fragment } = window.preact;
  const me = document.currentScript;
  const BASE = new URL('.', me.src).href;
  const registry = {};
  const sources = {};
  const injected = new Set();

  // ---------- expressions: {{ path.to.value }}, {{ true }}, {{ 3 }}, {{ 'text' }} ----------
  function evalExpr(expr, scope) {
    const e = expr.trim();
    if (e === 'true') return true;
    if (e === 'false') return false;
    if (e === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(e)) return Number(e);
    if (/^'.*'$|^".*"$/.test(e)) return e.slice(1, -1);
    const parts = e.split('.');
    let v;
    for (let i = scope.length - 1; i >= 0; i--) {
      if (scope[i] && Object.prototype.hasOwnProperty.call(scope[i], parts[0])) { v = scope[i][parts[0]]; break; }
    }
    for (let k = 1; k < parts.length; k++) v = v == null ? undefined : v[parts[k]];
    return v;
  }
  const HOLE = /\{\{([\s\S]*?)\}\}/g;
  function parseParts(str) {
    const out = [];
    let last = 0, m;
    HOLE.lastIndex = 0;
    while ((m = HOLE.exec(str))) {
      if (m.index > last) out.push({ lit: str.slice(last, m.index) });
      out.push({ expr: m[1] });
      last = m.index + m[0].length;
    }
    if (last < str.length) out.push({ lit: str.slice(last) });
    return out;
  }
  function evalParts(parts, scope, raw) {
    if (raw && parts.length === 1 && parts[0].expr !== undefined) return evalExpr(parts[0].expr, scope);
    let s = '';
    for (const p of parts) {
      if (p.lit !== undefined) s += p.lit;
      else { const v = evalExpr(p.expr, scope); s += v == null || v === false ? (v === false ? 'false' : '') : String(v); }
    }
    return s;
  }
  const camel = (n) => n.replace(/-([a-z])/g, (_, c) => c.toUpperCase());

  // ---------- template compiler: DOM -> descriptor tree ----------
  function compileNodes(nodes) {
    const out = [];
    for (const n of nodes) {
      if (n.nodeType === 3) {
        if (!n.nodeValue) continue;
        out.push({ t: 'text', parts: parseParts(n.nodeValue) });
      } else if (n.nodeType === 1) {
        const tag = n.localName;
        if (tag === 'helmet') continue;
        const attrs = [];
        for (const a of Array.from(n.attributes)) {
          if (a.name.startsWith('hint-')) continue;
          attrs.push({ name: a.name, parts: parseParts(a.value) });
        }
        const children = compileNodes(Array.from(n.childNodes));
        if (tag === 'sc-for') {
          const list = attrs.find((a) => a.name === 'list');
          const as = attrs.find((a) => a.name === 'as');
          out.push({ t: 'for', list: list ? list.parts : [], as: as ? evalParts(as.parts, [{}]) : 'item', children });
        } else if (tag === 'sc-if') {
          const val = attrs.find((a) => a.name === 'value');
          out.push({ t: 'if', value: val ? val.parts : [], children });
        } else if (tag === 'dc-import') {
          const name = attrs.find((a) => a.name === 'name');
          out.push({ t: 'import', name: name ? evalParts(name.parts, [{}]) : '', attrs: attrs.filter((a) => a.name !== 'name'), children });
        } else {
          out.push({ t: 'el', tag, attrs, children });
        }
      }
    }
    return out;
  }
  function renderNodes(nodes, scope) {
    const out = [];
    for (const n of nodes) {
      if (n.t === 'text') {
        const v = evalParts(n.parts, scope, false);
        if (v !== '') out.push(v);
      } else if (n.t === 'for') {
        const list = evalParts(n.list, scope, true);
        if (Array.isArray(list)) list.forEach((item, i) => out.push(...renderNodes(n.children, scope.concat([{ [n.as]: item, $index: i }]))));
      } else if (n.t === 'if') {
        if (evalParts(n.value, scope, true)) out.push(...renderNodes(n.children, scope));
      } else if (n.t === 'import') {
        const C = registry[n.name];
        if (!C) { out.push(h('div', { style: 'color:#D31212;font:12px monospace' }, 'Missing component ' + n.name)); continue; }
        const props = {};
        for (const a of n.attrs) props[camel(a.name)] = evalParts(a.parts, scope, true);
        out.push(h(C, props));
      } else {
        const props = {};
        for (const a of n.attrs) {
          const v = evalParts(a.parts, scope, true);
          if (v === undefined || v === null) continue;
          props[a.name] = v;
        }
        out.push(h(n.tag, props, ...renderNodes(n.children, scope)));
      }
    }
    return out;
  }

  // ---------- component files ----------
  function fixUrls(text) {
    return text.replace(/\/_blob\/([0-9a-f]{32})/g, BASE + 'assets/$1.svg');
  }
  async function fetchSource(name) {
    if (sources[name]) return sources[name];
    const res = await fetch(BASE + 'components/' + name + '.dc.html', { cache: 'no-cache' });
    if (!res.ok) throw new Error('Could not load component ' + name);
    const text = fixUrls(await res.text());
    sources[name] = text;
    const deps = Array.from(text.matchAll(/<dc-import\s+name="([^"]+)"/g)).map((m) => m[1]);
    await Promise.all(deps.filter((d) => !sources[d]).map(fetchSource));
    return text;
  }
  function injectHelmet(helmet) {
    if (!helmet) return;
    for (const node of Array.from(helmet.children)) {
      const key = node.outerHTML;
      if (injected.has(key)) continue;
      injected.add(key);
      document.head.appendChild(node.cloneNode(true));
    }
  }
  function define(name) {
    if (registry[name]) return registry[name];
    const doc = new DOMParser().parseFromString(sources[name], 'text/html');
    const xdc = doc.querySelector('x-dc');
    injectHelmet(xdc && xdc.querySelector('helmet'));
    const tree = compileNodes(xdc ? Array.from(xdc.childNodes) : []);
    const scriptEl = doc.querySelector('script[data-dc-script]');
    let defaults = {};
    try {
      const meta = JSON.parse((scriptEl && scriptEl.getAttribute('data-props')) || '{}');
      for (const k of Object.keys(meta)) if (k[0] !== '$' && meta[k] && meta[k].default !== undefined) defaults[k] = meta[k].default;
    } catch (e) { /* no defaults */ }
    class DCLogic extends PComponent {
      render() {
        const vals = this.renderVals ? this.renderVals() : {};
        return h(Fragment, null, ...renderNodes(tree, [vals]));
      }
    }
    const code = scriptEl ? scriptEl.textContent : 'class Component extends DCLogic { renderVals() { return {}; } }';
    const Cls = new Function('DCLogic', code + '\n;return Component;')(DCLogic);
    Cls.defaultProps = defaults;
    Cls.displayName = name;
    registry[name] = Cls;
    return Cls;
  }

  // ---------- screen names in the URL hash, for Useberry's URL-based task success ----------
  function screenName(step, games) {
    if (step === 'tab') return 'learn-tab';
    if (step === 'lang') return 'language-picker';
    if (step === 'review') return 'review-tab';
    if (step === 'list') return 'grammar-exercises';
    if (step === 'learn') return 'learn-the-rule';
    if (step === 0) return 'start';
    if (typeof step === 'number' && step >= 1 && step <= games) return 'game-' + step;
    if (step === games + 1) return 'results';
    if (step === games + 2) return 'complete';
    return String(step);
  }

  async function start(opts) {
    const mount = document.querySelector(opts.mount || '#phone');
    try {
      await fetchSource(opts.root);
      Object.keys(sources).forEach(define);
    } catch (e) {
      mount.innerHTML = '<p style="padding:24px;font:16px sans-serif;color:#A40E0E">Could not load the prototype: ' + e.message + '</p>';
      return;
    }
    const params = new URLSearchParams(location.search);
    const langs = opts.langs || ['sr'];
    const lang = langs.includes(params.get('lang')) ? params.get('lang') : langs[0];
    const Base = registry[opts.root];
    const games = opts.games || 4;
    class Root extends Base {
      constructor(props) {
        super(props);
        // Course language from the link (?lang=cz); the in-app flag can still switch it.
        this.state = { ...(this.state || {}), lang };
      }
      componentDidUpdate(prevProps, prevState) {
        if (super.componentDidUpdate) super.componentDidUpdate(prevProps, prevState);
        const name = screenName(this.state.step, games);
        if (location.hash !== '#' + name) location.hash = name;
      }
      componentDidMount() {
        if (super.componentDidMount) super.componentDidMount();
        location.hash = screenName(this.state.step, games);
      }
    }
    render(h(Root, {}), mount);
  }

  window.GymRuntime = { start };
})();
