#!/usr/bin/env python3
"""
INCO site builder.

Generates the static pages from one source so EN and ES never drift apart:
  /index.html          English home
  /es/index.html       Spanish home
  /legal/index.html    English legal notice, privacy & cookies
  /es/legal/index.html Spanish legal notice, privacy & cookies

Run:  python3 build.py
Edit content in this file (CONTENT, PROJECTS, STATIONS, TIMELINE…), then rebuild.
"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).parent

# ------------------------------------------------------------------ config
SITE_URL = "https://marcosdagama.github.io/inco-metal/"
# Prototype: keep the site out of search engines. Set to False at launch.
NOINDEX = True
# Free contact form via Web3Forms (https://web3forms.com, 250 submissions/month free).
# Paste the access key here; empty = form shows a "prototype" notice instead of sending.
WEB3FORMS_KEY = ""

COMPANY = {
    "brand": "INCO",
    "legal_name": "S.A. de Ingeniería y Construcción Mecánica",
    "nif": None,  # pending
    "registry": None,  # Registro Mercantil de Barcelona, tomo/folio/hoja — pending
    "address": "Calle Tuset, 20-24, 08006 Barcelona, España",
    "address_en": "Calle Tuset 20-24, 08006 Barcelona, Spain",
    "phone": "+34 932 387 960",
    "phone_href": "+34932387960",
    "email": "inco@saincome.es",
    "since": 1980,
}

# Placeholder images (most are temporary). Replace with INCO's own photography,
# ideally stored in /assets/img/. The duotone CSS treatment keeps any photo on-brand.
IMG = {
    "hero": "https://www.meadmetals.com/hubfs/230823_MEAD-CAMP_Blog4Images_1200x628_2.jpg",
    "about": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
}

# Certifications shown as duotone seals in the footer.
# PENDING CONFIRMATION — replace with INCO's actual certificates (and official logo files if desired).
CERTS = [
    {"code": "ISO 9001", "en": "Quality management", "es": "Gestión de calidad", "kind": "iso"},
    {"code": "ISO 14001", "en": "Environmental management", "es": "Gestión ambiental", "kind": "iso"},
    {"code": "ISO 45001", "en": "Health & safety", "es": "Seguridad y salud", "kind": "iso"},
    {"code": "CE", "en": "Machinery Directive", "es": "Directiva de Máquinas", "kind": "ce"},
]

# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(str(s), quote=True)

PENDING = {"en": "pending", "es": "pendiente"}

def pend(lang, what):
    return f'<span class="pending">[{esc(what)} — {PENDING[lang]}]</span>'

ICON = {
    "arrow": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1 8h13M9 3l5 5-5 5"/></svg>',
    "coil": '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="11" cy="22" r="7"/><circle cx="11" cy="22" r="2.5"/><path d="M11 15h22M33 15v14M18 29h15"/><circle cx="33" cy="22" r="7"/></svg>',
    "mill": '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="11" r="6"/><circle cx="20" cy="29" r="6"/><path d="M2 20h36"/><path d="M8 4v32M32 4v32"/></svg>',
    "cast": '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M6 6h14l-3 10H9z"/><path d="M13 16v6"/><path d="M8 22h10v4H8z"/><path d="M18 24h18M18 30h18"/><circle cx="24" cy="27" r="3"/></svg>',
    "eng": '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M6 34L34 6"/><path d="M6 34h28V6"/><path d="M14 34v-4M22 34v-4M30 34v-4M34 14h-4M34 22h-4"/><circle cx="16" cy="16" r="5"/></svg>',
    "turnkey": '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M4 34h32"/><path d="M8 34V18l8-6v6l8-6v6l8-6v22"/><path d="M14 26h4v8h-4zM24 24h4v4h-4z"/></svg>',
    "support": '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="13"/><circle cx="20" cy="20" r="5"/><path d="M20 7v8M20 25v8M7 20h8M25 20h8"/></svg>',
    "check": '<svg viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12"/><path d="M8.5 14.5l3.5 3.5 7.5-8"/></svg>',
    "close": '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M1 1l12 12M13 1L1 13"/></svg>',
    "prev": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg>',
    "next": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg>',
}

def seal(cert):
    """Duotone certification seal drawn in currentColor (no third-party logos)."""
    if cert["kind"] == "ce":
        inner = ('<text x="24" y="29.5" text-anchor="middle" font-family="Newsreader, Georgia, serif" '
                 'font-size="17" font-weight="400" fill="currentColor" letter-spacing="1">CE</text>')
    else:
        num = cert["code"].split()[-1]
        inner = ('<text x="24" y="21" text-anchor="middle" font-family="Plex Mono, monospace" font-size="6.5" '
                 'fill="currentColor" letter-spacing="1.2">ISO</text>'
                 f'<text x="24" y="31" text-anchor="middle" font-family="Plex, sans-serif" font-size="{10 if len(num) <= 4 else 8.4}" '
                 f'font-weight="500" fill="currentColor">{num}</text>')
    return ('<svg viewBox="0 0 48 48" aria-hidden="true">'
            '<circle cx="24" cy="24" r="22.5" fill="none" stroke="currentColor" stroke-width=".8"/>'
            '<circle cx="24" cy="24" r="18.5" fill="none" stroke="#E5485C" stroke-width=".8" stroke-dasharray="1.5 2"/>'
            f'{inner}</svg>')

# ------------------------------------------------------------------ content
T = {
  "en": {
    "title": "INCO — Metallurgical Process Engineering",
    "desc": "INCO engineers and builds custom lines for ferrous and non-ferrous metals: coil processing, rolling, casting and continuous casting. Barcelona · Geneva.",
    "og_locale": "en_GB",
    "brand_sub": "Engineering · Since 1980",
    "logo_sub": "Engineering &amp;<br>Mechanical Construction",
    "nav": [("#company", "Company"), ("#capabilities", "Capabilities"), ("#process", "Process"), ("#projects", "Projects"), ("#contact", "Contact")],
    "menu": "Menu",
    "skip": "Skip to content",
    "hero_eyebrow": "Metallurgical process engineering",
    "hero_h1": "Lines built <em>around</em> metal.",
    "hero_lede": "We design, manufacture and commission custom process lines for steel, aluminium and copper — from coil processing to continuous casting, engineered to each client's production targets.",
    "cta1": "See reference projects",
    "cta2": "Discuss a project",
    "fig_cap": ("Coil processing line", "Fig. 01"),
    "stats": [("40+", "years of process engineering"), ("10", "product lines"), ("2", "offices — Barcelona & Geneva"), ("100%", "custom-engineered")],
    "co_eyebrow": "Company",
    "co_h2": "Specialists in metallurgical <em>process</em> engineering.",
    "co_p": [
        "INCO is a group of companies that engineers and manufactures equipment for metallurgical processes, ferrous and non-ferrous.",
        "Our core is flat-product (coil) transformation lines, along with casting and continuous casting for non-ferrous metals such as aluminium and copper. Years of close collaboration with clients have produced processes and machinery that exist nowhere else — and a multidisciplinary Technical Office that starts every project from the client's production targets.",
    ],
    "principles": [
        "Every proposal is technically and economically viable in a competitive global market.",
        "Machinery matched precisely to the process requirements and output targets.",
        "Process value-add that delivers a solid, measurable return on investment.",
    ],
    "quality_h": "Quality policy",
    "quality_p": "Quality is built into every stage, from concept to commissioning. Each project goes through multidisciplinary review to secure technical excellence and long-term equipment reliability.",
    "cap_eyebrow": "Capabilities",
    "cap_h2": "The full lifecycle of a <em>process line</em>.",
    "cap_lede": "From the first feasibility study to operator training, one engineering team carries the project through.",
    "caps": [
        ("coil", "Coil processing lines", "Painting, pickling, annealing, levelling and tension-levelling lines for aluminium, steel and copper coils — for architecture, appliances and electronics."),
        ("mill", "Rolling mills", "Reversible cold mills, mini-mills and skin-pass mills for steel, aluminium, copper and special alloys. Widths up to 1,800 mm, speeds up to 1,500 m/min."),
        ("cast", "Casting & continuous casting", "Melting, casting and continuous-casting sections for aluminium and copper, including hot-rolling tandems and billet plants."),
        ("eng", "Custom engineering", "Our Technical Office designs bespoke processes and machinery that give clients a lasting strategic edge."),
        ("turnkey", "Turnkey installation", "Project management from manufacturing to on-site assembly, testing and commissioning, with our engineers present throughout."),
        ("support", "Training & after-sales", "Operator and maintenance training from day one, ongoing technical support and guaranteed spare-parts availability."),
    ],
    "pr_eyebrow": "How a line works",
    "pr_h2": "Anatomy of a <em>coil coating</em> line.",
    "pr_lede": "A continuous line takes a bare coil to a painted, cured and rewound coil in one pass. Select a station to see what it does.",
    "pr_note": "Schematic · 2-coat, 2-bake (2C2B) configuration · not to scale",
    "pr_legend": ("Strip path", "Heated section"),
    "pr_prev": "Previous station", "pr_next": "Next station",
    "tl_eyebrow": "Service",
    "tl_h2": "From first study to <em>full production</em>.",
    "tl_lede": "One team, accountable from the initial assessment to the line running at nominal speed.",
    "pj_eyebrow": "Reference work",
    "pj_h2": "Selected <em>projects</em>.",
    "pj_lede": "Filter by process and metal. Open any project for its technical specification.",
    "f_process": "Process", "f_metal": "Metal", "f_all": "All",
    "showing": "Showing {n} of {t} projects", "showingOne": "Showing 1 of {t} projects",
    "reset": "Clear filters", "empty": "No projects match this combination.",
    "m_cta": "Enquire about a similar line", "close": "Close",
    "ct_eyebrow": "Contact",
    "ct_h2": "Tell us about your <em>process</em>.",
    "ct_lede": "Share your requirements and our engineers will reply with an initial technical assessment.",
    "ct_labels": {"phone": "Phone", "email": "Email", "bcn": "Barcelona · Head office", "gva": "Geneva · European office"},
    "gva_addr": "26 Boulevard des Philosophes, 1205 Geneva, Switzerland",
    "form": {
        "name": "Name", "company": "Company", "email": "Email", "country": "Country",
        "process": "Process", "metal": "Metal", "select": "Select…",
        "tech": "Optional · technical parameters",
        "width": "Strip width (mm)", "thick": "Thickness (mm)", "cap": "Capacity (t/year)",
        "msg": "Project description",
        "consent": 'I agree that INCO processes my data to answer this enquiry, as described in the <a href="{legal}#privacy">privacy policy</a>.',
        "send": "Send enquiry", "req": "required",
        "other": "Other",
    },
    "formProto": "Prototype: the form is not connected yet. Your message was not sent.",
    "formSending": "Sending…",
    "formOk": "Thank you. Your enquiry has been sent — our engineers will be in touch shortly.",
    "formErr": "Something went wrong. Please try again or write to " + COMPANY["email"] + ".",
    "ft_tag": "Metallurgical process engineering since 1980.",
    "ft_nav": "Site", "ft_contact": "Contact", "ft_offices": "Offices",
    "ft_certs": "Certifications",
    "ft_legal": [("legal", "Legal notice"), ("privacy", "Privacy"), ("cookies", "Cookies")],
    "rights": "All rights reserved.",
    "lang_name": "English",
    "legal_title": "Legal notice, privacy & cookies",
    "legal_desc": "Legal notice, privacy policy and cookie policy of INCO — S.A. de Ingeniería y Construcción Mecánica.",
    "back": "Back to home",
  },
  "es": {
    "title": "INCO — Ingeniería de procesos metalúrgicos",
    "desc": "INCO diseña y fabrica líneas a medida para metales férricos y no férricos: procesado de bobinas, laminación, fundición y colada continua. Barcelona · Ginebra.",
    "og_locale": "es_ES",
    "brand_sub": "Ingeniería · Desde 1980",
    "logo_sub": "Ingeniería y<br>Construcción Mecánica",
    "nav": [("#company", "Empresa"), ("#capabilities", "Capacidades"), ("#process", "Proceso"), ("#projects", "Proyectos"), ("#contact", "Contacto")],
    "menu": "Menú",
    "skip": "Saltar al contenido",
    "hero_eyebrow": "Ingeniería de procesos metalúrgicos",
    "hero_h1": "Líneas pensadas <em>desde</em> el metal.",
    "hero_lede": "Diseñamos, fabricamos y ponemos en marcha líneas de proceso a medida para acero, aluminio y cobre — del procesado de bobinas a la colada continua, según los objetivos de producción de cada cliente.",
    "cta1": "Ver proyectos de referencia",
    "cta2": "Hablemos de su proyecto",
    "fig_cap": ("Línea de procesado de bobinas", "Fig. 01"),
    "stats": [("40+", "años de ingeniería de procesos"), ("10", "líneas de producto"), ("2", "oficinas — Barcelona y Ginebra"), ("100%", "ingeniería a medida")],
    "co_eyebrow": "Empresa",
    "co_h2": "Especialistas en ingeniería de <em>procesos</em> metalúrgicos.",
    "co_p": [
        "INCO es un grupo de empresas que diseña y fabrica equipos para procesos metalúrgicos, férricos y no férricos.",
        "Nuestra especialidad son las líneas de transformación de productos planos (bobinas), junto con la fundición y la colada continua de metales no férricos como el aluminio y el cobre. Años de colaboración estrecha con nuestros clientes han dado lugar a procesos y maquinaria únicos, y a una Oficina Técnica multidisciplinar que parte siempre de los objetivos de producción de cada cliente.",
    ],
    "principles": [
        "Cada propuesta es técnica y económicamente viable en un mercado global competitivo.",
        "Maquinaria ajustada con precisión a los requisitos del proceso y a los objetivos de producción.",
        "Un valor añadido de proceso que garantiza un retorno de la inversión sólido y medible.",
    ],
    "quality_h": "Política de calidad",
    "quality_p": "La calidad está integrada en cada etapa, del concepto a la puesta en marcha. Cada proyecto pasa por una revisión multidisciplinar que asegura la excelencia técnica y la fiabilidad del equipo a largo plazo.",
    "cap_eyebrow": "Capacidades",
    "cap_h2": "El ciclo completo de una <em>línea de proceso</em>.",
    "cap_lede": "Del primer estudio de viabilidad a la formación de operarios, un mismo equipo de ingeniería lleva el proyecto.",
    "caps": [
        ("coil", "Líneas de procesado de bobinas", "Líneas de pintura, decapado, recocido, aplanado y aplanado bajo tensión para bobinas de aluminio, acero y cobre — para arquitectura, electrodomésticos y electrónica."),
        ("mill", "Laminadores", "Laminadores reversibles en frío, minilaminadores y skin-pass para acero, aluminio, cobre y aleaciones especiales. Anchos hasta 1.800 mm y velocidades hasta 1.500 m/min."),
        ("cast", "Fundición y colada continua", "Secciones de fusión, colada y colada continua para aluminio y cobre, incluidos trenes de laminación en caliente y plantas de palanquillas."),
        ("eng", "Ingeniería a medida", "Nuestra Oficina Técnica diseña procesos y maquinaria a medida que otorgan al cliente una ventaja estratégica duradera."),
        ("turnkey", "Instalación llave en mano", "Gestión del proyecto desde la fabricación hasta el montaje, las pruebas y la puesta en marcha, con nuestros ingenieros presentes en todo momento."),
        ("support", "Formación y postventa", "Formación de operarios y mantenimiento desde el primer día, soporte técnico continuo y disponibilidad garantizada de repuestos."),
    ],
    "pr_eyebrow": "Cómo funciona una línea",
    "pr_h2": "Anatomía de una línea de <em>pintado de bobinas</em>.",
    "pr_lede": "Una línea continua transforma una bobina desnuda en una bobina pintada, curada y rebobinada en una sola pasada. Seleccione una estación para ver su función.",
    "pr_note": "Esquema · configuración de 2 capas y 2 hornos (2C2B) · sin escala",
    "pr_legend": ("Recorrido de la banda", "Sección térmica"),
    "pr_prev": "Estación anterior", "pr_next": "Estación siguiente",
    "tl_eyebrow": "Servicio",
    "tl_h2": "Del primer estudio a la <em>plena producción</em>.",
    "tl_lede": "Un solo equipo, responsable desde la evaluación inicial hasta que la línea trabaja a velocidad nominal.",
    "pj_eyebrow": "Trabajos de referencia",
    "pj_h2": "Proyectos <em>seleccionados</em>.",
    "pj_lede": "Filtre por proceso y por metal. Abra cualquier proyecto para ver su especificación técnica.",
    "f_process": "Proceso", "f_metal": "Metal", "f_all": "Todos",
    "showing": "Mostrando {n} de {t} proyectos", "showingOne": "Mostrando 1 de {t} proyectos",
    "reset": "Quitar filtros", "empty": "Ningún proyecto coincide con esta combinación.",
    "m_cta": "Consultar por una línea similar", "close": "Cerrar",
    "ct_eyebrow": "Contacto",
    "ct_h2": "Cuéntenos su <em>proceso</em>.",
    "ct_lede": "Comparta sus requisitos y nuestros ingenieros le responderán con una evaluación técnica inicial.",
    "ct_labels": {"phone": "Teléfono", "email": "Email", "bcn": "Barcelona · Sede central", "gva": "Ginebra · Oficina europea"},
    "gva_addr": "26 Boulevard des Philosophes, 1205 Ginebra, Suiza",
    "form": {
        "name": "Nombre", "company": "Empresa", "email": "Email", "country": "País",
        "process": "Proceso", "metal": "Metal", "select": "Seleccione…",
        "tech": "Opcional · parámetros técnicos",
        "width": "Ancho de banda (mm)", "thick": "Espesor (mm)", "cap": "Capacidad (t/año)",
        "msg": "Descripción del proyecto",
        "consent": 'Acepto que INCO trate mis datos para responder a esta consulta, según la <a href="{legal}#privacy">política de privacidad</a>.',
        "send": "Enviar consulta", "req": "obligatorio",
        "other": "Otro",
    },
    "formProto": "Prototipo: el formulario aún no está conectado. Su mensaje no se ha enviado.",
    "formSending": "Enviando…",
    "formOk": "Gracias. Su consulta se ha enviado — nuestros ingenieros contactarán con usted en breve.",
    "formErr": "Se ha producido un error. Inténtelo de nuevo o escriba a " + COMPANY["email"] + ".",
    "ft_tag": "Ingeniería de procesos metalúrgicos desde 1980.",
    "ft_nav": "Web", "ft_contact": "Contacto", "ft_offices": "Oficinas",
    "ft_certs": "Certificaciones",
    "ft_legal": [("legal", "Aviso legal"), ("privacy", "Privacidad"), ("cookies", "Cookies")],
    "rights": "Todos los derechos reservados.",
    "lang_name": "Español",
    "legal_title": "Aviso legal, privacidad y cookies",
    "legal_desc": "Aviso legal, política de privacidad y política de cookies de INCO — S.A. de Ingeniería y Construcción Mecánica.",
    "back": "Volver al inicio",
  },
}

# Process & metal taxonomy for the project filters
PROCESSES = [
    ("painting", "Coil coating", "Pintado de bobinas"),
    ("levelling", "Tension levelling", "Aplanado bajo tensión"),
    ("pickling", "Pickling", "Decapado"),
    ("annealing", "Annealing", "Recocido"),
    ("casting", "Casting & rolling", "Colada y laminación"),
    ("recycling", "Recycling", "Reciclaje"),
    ("service", "Service centre", "Centro de servicio"),
]
METALS = [
    ("steel", "Steel", "Acero"),
    ("aluminium", "Aluminium", "Aluminio"),
    ("copper", "Copper", "Cobre"),
]

def _p(id, process, metals, img, en, es, specs_en, specs_es):
    return {"id": id, "process": process, "metals": metals, "img": img, "en": en, "es": es,
            "specs_en": specs_en, "specs_es": specs_es}

PROJECTS = [
    _p("p01", "levelling", ["aluminium"],
       "https://www.intocast.de/wp-content/uploads/2023/03/into-products-refractories-aluminium.png",
       {"title": "Tension levelling line for architectural aluminium", "sector": "Architecture",
        "desc": "Custom tension levelling line for aluminium coils destined for architectural cladding, reaching the flatness tolerances demanded by high-end façade systems. Delivered turnkey: decoiler, entry loop, multi-roll leveller, exit loop and recoiler."},
       {"title": "Línea de aplanado bajo tensión para aluminio arquitectónico", "sector": "Arquitectura",
        "desc": "Línea de aplanado bajo tensión a medida para bobinas de aluminio destinadas a revestimiento arquitectónico, con las tolerancias de planitud que exigen los sistemas de fachada de alta gama. Entregada llave en mano: desbobinador, lazo de entrada, aplanadora multirrodillo, lazo de salida y rebobinador."},
       [("Strip width", "up to 1,600 mm"), ("Thickness", "0.3–4.0 mm"), ("Speed", "60–120 m/min"), ("Alloys", "1xxx, 3xxx, 5xxx"), ("Applications", "Cladding, façades, roofing"), ("Supply", "Full turnkey, PLC automation")],
       [("Ancho de banda", "hasta 1.600 mm"), ("Espesor", "0,3–4,0 mm"), ("Velocidad", "60–120 m/min"), ("Aleaciones", "1xxx, 3xxx, 5xxx"), ("Aplicaciones", "Revestimiento, fachadas, cubiertas"), ("Suministro", "Llave en mano, automatización PLC")]),
    _p("p02", "painting", ["steel", "aluminium"],
       "https://cdn.shortpixel.ai/spai/q_lossy+w_1200+to_webp+ret_img/alucoatuniversal.com/wp-content/uploads/2025/03/Types-of-aluminum-coil-coating.jpg",
       {"title": "Coil paint line for architecture and appliances", "sector": "Architecture · Appliances",
        "desc": "High-speed coil paint line for galvanised steel and aluminium strip. Handles polyester, PVDF and plastisol systems with rapid colour change and convection/IR oven sections. Full turnkey supply."},
       {"title": "Línea de pintura para arquitectura y electrodomésticos", "sector": "Arquitectura · Electrodomésticos",
        "desc": "Línea de pintura de alta velocidad para banda de acero galvanizado y aluminio. Trabaja con sistemas de poliéster, PVDF y plastisol, con cambio rápido de color y hornos de convección e IR. Suministro llave en mano."},
       [("Strip width", "up to 2,400 mm"), ("Speed", "20–180 m/min"), ("Materials", "Galvanised, Galvalume, aluminium"), ("Paints", "Polyester, PVDF, plastisol, epoxy"), ("Ovens", "Convection + IR")],
       [("Ancho de banda", "hasta 2.400 mm"), ("Velocidad", "20–180 m/min"), ("Materiales", "Galvanizado, Galvalume, aluminio"), ("Pinturas", "Poliéster, PVDF, plastisol, epoxi"), ("Hornos", "Convección + IR")]),
    _p("p03", "levelling", ["copper"],
       "https://almetals.com/getfile/d6492474-c916-4ee2-87ee-db33a0c7d203/Copper.aspx",
       {"title": "Tension levelling for copper electronic components", "sector": "Electronics",
        "desc": "Precision tension levelling line for thin copper and copper-alloy strip used in connectors, lead frames and PCB components, where flatness and surface quality are critical."},
       {"title": "Aplanado bajo tensión de cobre para componentes electrónicos", "sector": "Electrónica",
        "desc": "Línea de aplanado bajo tensión de precisión para banda fina de cobre y aleaciones de cobre destinada a conectores, lead frames y componentes de PCB, donde la planitud y la calidad superficial son críticas."},
       [("Strip width", "100–650 mm"), ("Thickness", "0.10–2.0 mm"), ("Speed", "30–100 m/min"), ("Materials", "Copper, brass, bronze"), ("Applications", "PCB, connectors, lead frames")],
       [("Ancho de banda", "100–650 mm"), ("Espesor", "0,10–2,0 mm"), ("Velocidad", "30–100 m/min"), ("Materiales", "Cobre, latón, bronce"), ("Aplicaciones", "PCB, conectores, lead frames")]),
    _p("p04", "painting", ["aluminium"],
       "https://www.sa-inco.com/en_US/media/b920b3982726a905c67471fb184bdf6e.cms_1_1024_1_1024__/line-paint-galvanized-steel-coil,-aluminum-aluzinc.JPG",
       {"title": "Paint line for aluminium coils", "sector": "Architecture",
        "desc": "Dedicated aluminium coil coating line with integrated pre-treatment and quick colour change, configurable as one-coat/one-bake or two-coat/two-bake."},
       {"title": "Línea de pintura para bobinas de aluminio", "sector": "Arquitectura",
        "desc": "Línea de pintado específica para bobinas de aluminio, con pretratamiento integrado y cambio rápido de color, configurable como una capa y un horno o dos capas y dos hornos."},
       [("Strip width", "up to 1,650 mm"), ("Speed", "40–120 m/min"), ("Paints", "Polyester, PVDF, acrylic"), ("Configuration", "1C1B or 2C2B"), ("Pre-treatment", "Included")],
       [("Ancho de banda", "hasta 1.650 mm"), ("Velocidad", "40–120 m/min"), ("Pinturas", "Poliéster, PVDF, acrílica"), ("Configuración", "1C1B o 2C2B"), ("Pretratamiento", "Incluido")]),
    _p("p05", "pickling", ["steel"],
       "https://www.clecim.com/wp-content/uploads/2025/08/clecim-lines-stainless-annealing-picking-lines-3.jpg",
       {"title": "Pickling line for narrow carbon-steel coils", "sector": "Steel processing",
        "desc": "Hydrochloric-acid pickling line for narrow hot-rolled carbon-steel strip, removing scale ahead of cold rolling, with acid regeneration included."},
       {"title": "Línea de decapado para bobinas estrechas de acero al carbono", "sector": "Transformación del acero",
        "desc": "Línea de decapado con ácido clorhídrico para banda estrecha de acero al carbono laminada en caliente, que elimina la cascarilla antes de la laminación en frío. Incluye regeneración de ácido."},
       [("Strip width", "100–700 mm"), ("Entry thickness", "1.5–6 mm"), ("Acid", "HCl, with regeneration"), ("Speed", "30–120 m/min")],
       [("Ancho de banda", "100–700 mm"), ("Espesor de entrada", "1,5–6 mm"), ("Ácido", "HCl, con regeneración"), ("Velocidad", "30–120 m/min")]),
    _p("p06", "annealing", ["steel"],
       "assets/img/bell-annealing.jpg",
       {"title": "Bell annealing section for a cold-rolling plant", "sector": "Steel processing",
        "desc": "Controlled-atmosphere (HNX) bell annealing integrated within a cold-rolling complex for carbon-steel strip, with programmable heating and cooling cycles for flexible multi-grade production."},
       {"title": "Sección de recocido en campana para planta de laminación en frío", "sector": "Transformación del acero",
        "desc": "Recocido en campana con atmósfera controlada (HNX) integrado en un complejo de laminación en frío para banda de acero al carbono, con ciclos programables de calentamiento y enfriamiento para producir varias calidades con flexibilidad."},
       [("Furnace type", "Bell annealing (HNX)"), ("Coil weight", "up to 32 t"), ("Grades", "CQ, DQ, DDQ, EDDQ"), ("Cooling", "Controlled forced convection")],
       [("Tipo de horno", "Recocido en campana (HNX)"), ("Peso de bobina", "hasta 32 t"), ("Calidades", "CQ, DQ, DDQ, EDDQ"), ("Enfriamiento", "Convección forzada controlada")]),
    _p("p07", "painting", ["steel", "aluminium"],
       "https://www.sa-inco.com/en_US/media/b920b3982726a905c67471fb184bdf6e.cms_1_1024_1_1024__/line-paint-galvanized-steel-coil,-aluminum-aluzinc.JPG",
       {"title": "Paint line for galvanised, Aluzinc and aluminium", "sector": "Construction",
        "desc": "Multi-substrate coil coating line with horizontal two-roll coaters, sized for galvanised steel, Aluzinc and aluminium strip."},
       {"title": "Línea de pintura para galvanizado, Aluzinc y aluminio", "sector": "Construcción",
        "desc": "Línea de pintado multisustrato con recubridores horizontales de dos rodillos, dimensionada para banda de acero galvanizado, Aluzinc y aluminio."},
       [("Materials", "Galvanised, Galvalume, aluminium"), ("Width", "up to 1,800 mm"), ("Speed", "30–120 m/min"), ("Coater", "Horizontal 2-roll"), ("Paints", "Polyester, SMP, PVDF")],
       [("Materiales", "Galvanizado, Galvalume, aluminio"), ("Ancho", "hasta 1.800 mm"), ("Velocidad", "30–120 m/min"), ("Recubridor", "Horizontal de 2 rodillos"), ("Pinturas", "Poliéster, SMP, PVDF")]),
    _p("p08", "casting", ["aluminium"],
       "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1000&q=80&fit=crop",
       {"title": "Melting and continuous casting — aluminium billet plant", "sector": "Primary aluminium",
        "desc": "Complete melting and continuous-casting plant for aluminium billets, with rotary degassing and ceramic-foam filtration for consistent metal quality."},
       {"title": "Fusión y colada continua — planta de palanquillas de aluminio", "sector": "Aluminio primario",
        "desc": "Planta completa de fusión y colada continua de palanquillas de aluminio, con desgasificación rotativa y filtración por espuma cerámica para una calidad de metal constante."},
       [("Capacity", "up to 30 t/h"), ("Alloys", "1xxx, 3xxx, 5xxx, 6xxx, 8xxx"), ("Billet diameter", "75–400 mm"), ("Degassing", "Rotary"), ("Filtration", "Ceramic foam")],
       [("Capacidad", "hasta 30 t/h"), ("Aleaciones", "1xxx, 3xxx, 5xxx, 6xxx, 8xxx"), ("Diámetro de palanquilla", "75–400 mm"), ("Desgasificación", "Rotativa"), ("Filtración", "Espuma cerámica")]),
    _p("p09", "casting", ["aluminium", "copper"],
       "https://www.intocast.de/wp-content/uploads/2023/03/into-products-refractories-aluminium.png",
       {"title": "Continuous casting + 3-stand hot rolling tandem", "sector": "Non-ferrous rolling",
        "desc": "Integrated continuous casting and hot rolling for non-ferrous metals: a twin-roll or belt caster feeding an inline 3-stand, 4-high hot tandem — coils or sheets in a single energy-efficient flow."},
       {"title": "Colada continua + tren de laminación en caliente de 3 cajas", "sector": "Laminación de no férricos",
        "desc": "Colada continua y laminación en caliente integradas para metales no férricos: una coladora de doble rodillo o de banda alimenta un tren en caliente en línea de 3 cajas cuarto — bobinas o chapas en un único flujo eficiente."},
       [("Casting speed", "up to 8 m/min"), ("Hot mill", "3-stand tandem, 4-high"), ("Entry gauge", "8–25 mm"), ("Exit gauge", "2–8 mm"), ("Width", "up to 1,400 mm")],
       [("Velocidad de colada", "hasta 8 m/min"), ("Tren en caliente", "Tándem de 3 cajas, cuarto"), ("Espesor de entrada", "8–25 mm"), ("Espesor de salida", "2–8 mm"), ("Ancho", "hasta 1.400 mm")]),
    _p("p10", "service", ["aluminium"],
       "https://cdn.shortpixel.ai/spai/q_lossy+w_1200+to_webp+ret_img/alucoatuniversal.com/wp-content/uploads/2025/03/Types-of-aluminum-coil-coating.jpg",
       {"title": "Aluminium disc blanking line", "sector": "Cookware · Packaging",
        "desc": "High-output blanking line producing aluminium discs from coil, with electrostatic oiling and automatic stacking."},
       {"title": "Línea de corte de discos de aluminio", "sector": "Menaje · Envase",
        "desc": "Línea de corte de alta producción que obtiene discos de aluminio a partir de bobina, con aceitado electrostático y apilado automático."},
       [("Disc diameter", "80–600 mm"), ("Thickness", "0.4–4.0 mm"), ("Alloys", "1xxx, 3xxx, 5xxx"), ("Output", "up to 200 discs/min")],
       [("Diámetro de disco", "80–600 mm"), ("Espesor", "0,4–4,0 mm"), ("Aleaciones", "1xxx, 3xxx, 5xxx"), ("Producción", "hasta 200 discos/min")]),
    _p("p11", "recycling", ["aluminium"],
       "https://www.meadmetals.com/hubfs/230823_MEAD-CAMP_Blog4Images_1200x628_2.jpg",
       {"title": "Aluminium recycling plant", "sector": "Secondary aluminium",
        "desc": "Recycling plant for mixed scrap, used beverage cans and process scrap, with rotary-drum and reverberatory furnaces, dross treatment and emission control."},
       {"title": "Planta de reciclaje de aluminio", "sector": "Aluminio secundario",
        "desc": "Planta de reciclaje para chatarra mixta, latas usadas y recortes de proceso, con hornos rotativos y de reverbero, tratamiento de escorias y control de emisiones."},
       [("Capacity", "up to 20 t/h"), ("Input", "Mixed scrap, UBC, process scrap"), ("Furnaces", "Rotary drum + reverberatory"), ("Dross treatment", "Included")],
       [("Capacidad", "hasta 20 t/h"), ("Entrada", "Chatarra mixta, UBC, recortes"), ("Hornos", "Rotativo + reverbero"), ("Tratamiento de escorias", "Incluido")]),
    _p("p12", "service", ["steel", "aluminium"],
       "https://www.clecim.com/wp-content/uploads/2025/08/clecim-lines-stainless-annealing-picking-lines-3.jpg",
       {"title": "Service-centre lines — steel and aluminium", "sector": "Service centres",
        "desc": "Slitting and cut-to-length lines for steel and aluminium service centres, from mild steel to advanced high-strength grades."},
       {"title": "Líneas para centros de servicio — acero y aluminio", "sector": "Centros de servicio",
        "desc": "Líneas de corte longitudinal y transversal para centros de servicio de acero y aluminio, desde acero dulce hasta aceros avanzados de alta resistencia."},
       [("Slitting", "up to 1,800 mm wide, 0.3–8 mm"), ("Cut-to-length tolerance", "±0.5 mm"), ("Speed", "up to 200 m/min"), ("Materials", "Mild steel, AHSS, aluminium")],
       [("Corte longitudinal", "hasta 1.800 mm de ancho, 0,3–8 mm"), ("Tolerancia de corte", "±0,5 mm"), ("Velocidad", "hasta 200 m/min"), ("Materiales", "Acero dulce, AHSS, aluminio")]),
]

# Coil coating line stations (schema)
STATIONS = [
    ("Decoilers", "Desbobinadoras",
     "Two mandrels let the next coil be prepared while the current one runs, so coil changes never stop the line.",
     "Dos mandriles permiten preparar la siguiente bobina mientras corre la actual, de modo que el cambio de bobina no detiene la línea."),
    ("Shear & stitcher", "Cizalla y unión",
     "The tail of one coil is trimmed and joined to the head of the next, creating an endless strip.",
     "La cola de una bobina se recorta y se une a la cabeza de la siguiente, creando una banda continua."),
    ("Entry accumulator", "Acumulador de entrada",
     "A vertical strip store fills while the line runs and empties during coil changes, keeping process speed constant.",
     "Un almacén vertical de banda se llena durante la marcha y se vacía en los cambios de bobina, manteniendo constante la velocidad de proceso."),
    ("Cleaning & pre-treatment", "Limpieza y pretratamiento",
     "Alkaline degreasing, rinsing and a chemical conversion coat prepare the surface for paint adhesion and corrosion resistance.",
     "Desengrase alcalino, aclarado y capa de conversión química preparan la superficie para la adherencia de la pintura y la resistencia a la corrosión."),
    ("Primer coater", "Recubridor de imprimación",
     "Roll coaters apply primer to the top face and backer to the reverse in a controlled film thickness.",
     "Los recubridores de rodillos aplican imprimación en la cara superior y backer en el reverso, con espesor de película controlado."),
    ("Primer oven & quench", "Horno de imprimación y enfriamiento",
     "Convection zones cure the primer to a precise peak metal temperature; a water quench then cools the strip.",
     "Las zonas de convección curan la imprimación hasta una temperatura de metal precisa; después, un enfriamiento por agua baja la temperatura de la banda."),
    ("Finish coater", "Recubridor de acabado",
     "The top coat is applied, with fast colour-change capability to minimise downtime between orders.",
     "Se aplica la capa de acabado, con cambio rápido de color para reducir las paradas entre pedidos."),
    ("Finish oven & quench", "Horno de acabado y enfriamiento",
     "Final cure, quench and drying. Fume incineration recovers energy back into the ovens.",
     "Curado final, enfriamiento y secado. La incineración de humos recupera energía para los hornos."),
    ("Exit accumulator & inspection", "Acumulador de salida e inspección",
     "Buffers the strip during coil cut-off, with surface inspection and optional protective-film lamination.",
     "Amortigua la banda durante el corte de bobina, con inspección superficial y laminado opcional de film protector."),
    ("Recoiler", "Rebobinadora",
     "The strip is cut to the ordered coil weight and rewound, ready for packing and dispatch.",
     "La banda se corta al peso de bobina pedido y se rebobina, lista para embalaje y expedición."),
]

PHASE = {"en": "Phase", "es": "Fase"}

SHORT = {
    "en": ["Decoilers", "Shear", "Entry accum.", "Pre-treatment", "Primer coat", "Primer oven", "Finish coat", "Finish oven", "Exit accum.", "Recoiler"],
    "es": ["Desbobinado", "Cizalla", "Acum. entrada", "Pretratamiento", "Imprimación", "Horno imprim.", "Acabado", "Horno acabado", "Acum. salida", "Rebobinado"],
}

TIMELINE = [
    ("Feasibility", "Viabilidad", "Process study", "Estudio de proceso",
     "Analysis of the product, targets and site; layout and a technical-economic proposal.",
     "Análisis del producto, los objetivos y la planta; layout y propuesta técnico-económica.",
     "Proposal & layout", "Propuesta y layout"),
    ("Engineering", "Ingeniería", "Basic & detailed", "Básica y de detalle",
     "Process, mechanical, electrical and automation engineering by our Technical Office.",
     "Ingeniería de proceso, mecánica, eléctrica y de automatización por nuestra Oficina Técnica.",
     "Design approval", "Aprobación del diseño"),
    ("Manufacturing", "Fabricación", "Build & test", "Fabricación y pruebas",
     "Fabrication and machining with supplier quality control and factory acceptance tests.",
     "Fabricación y mecanizado con control de calidad de proveedores y pruebas de aceptación en taller.",
     "FAT", "FAT"),
    ("Installation", "Montaje", "On site", "En planta",
     "Assembly at the client's plant, led and supervised by INCO engineers.",
     "Montaje en la planta del cliente, dirigido y supervisado por ingenieros de INCO.",
     "Mechanical completion", "Fin de montaje"),
    ("Commissioning", "Puesta en marcha", "Ramp-up", "Arranque",
     "Cold and hot tests, ramp-up to nominal speed and performance verification.",
     "Pruebas en frío y en caliente, subida a velocidad nominal y verificación de prestaciones.",
     "SAT · acceptance", "SAT · recepción"),
    ("Training & support", "Formación y soporte", "Lifetime", "Toda la vida útil",
     "Operator and maintenance training, spare parts, remote and on-site support.",
     "Formación de operarios y mantenimiento, repuestos, soporte remoto y en planta.",
     "Continuous", "Continuo"),
]

# ------------------------------------------------------------------ schema svg
def schema_svg(lang):
    """Coil coating line, drawn programmatically. Stations are focusable groups."""
    W, H, Y = 1200, 340, 150
    g = []
    g.append(f'<svg class="schema" viewBox="0 0 {W} {H}" role="group" aria-label="{esc(T[lang]["pr_h2"].replace("<em>","").replace("</em>",""))}">')
    # faint grid
    for x in range(0, W + 1, 40):
        g.append(f'<line class="grid" x1="{x}" y1="20" x2="{x}" y2="250"/>')
    # strip path (continuous), built piecewise
    def festoon(x0, x1, top, bot, n):
        pts = []
        step = (x1 - x0) / (n * 2)
        x = x0
        for i in range(n):
            pts += [f"L{x + step * 0.5:.1f},{top}", f"L{x + step * 1.5:.1f},{bot}"]
            x += step * 2
        return " ".join(pts)
    path = (f"M88,{Y - 30} L150,{Y} L222,{Y} "
            + festoon(232, 312, 62, 222, 3) +
            f" L322,{Y} L1000,{Y} " + festoon(1010, 1080, 62, 222, 3) +
            f" L1090,{Y} L1150,{Y - 30}")
    g.append(f'<path class="strip" d="{path}"/>')
    g.append(f'<path class="strip flow" d="{path}" stroke="#F3F1EC" stroke-opacity=".55" stroke-width="1.2"/>')

    def station(i, x0, x1, body):
        name_en, name_es, d_en, d_es = STATIONS[i]
        name = name_en if lang == "en" else name_es
        desc = d_en if lang == "en" else d_es
        cx = (x0 + x1) / 2
        short = SHORT[lang][i]
        ly = 306 if i % 2 == 0 else 324
        g.append(f'<g class="st" tabindex="0" role="button" aria-pressed="false" '
                 f'data-name="{esc(name)}" data-desc="{esc(desc)}" aria-label="{i + 1:02d}. {esc(name)}">')
        g.append(f'<rect class="hit" x="{x0}" y="20" width="{x1 - x0}" height="315"/>')
        g.append(body)
        g.append(f'<line class="tick" x1="{cx}" y1="256" x2="{cx}" y2="{ly - 26}"/>')
        g.append(f'<text class="lbl-n" x="{cx}" y="{ly - 14}" text-anchor="middle">{i + 1:02d}</text>')
        g.append(f'<text class="lbl" x="{cx}" y="{ly}" text-anchor="middle">{esc(short)}</text>')
        g.append('</g>')

    # 1 decoilers
    station(0, 20, 130,
            f'<circle class="mach fill" cx="70" cy="{Y - 52}" r="26"/><circle class="mach" cx="70" cy="{Y - 52}" r="6"/>'
            f'<circle class="mach" cx="70" cy="{Y + 40}" r="20" stroke-dasharray="3 3"/><circle class="mach" cx="70" cy="{Y + 40}" r="5"/>'
            f'<path class="mach" d="M50,{Y + 85} h40 M70,{Y - 26} v6"/>')
    # 2 shear & stitcher
    station(1, 130, 220,
            f'<rect class="mach fill" x="152" y="{Y - 22}" width="22" height="16"/><rect class="mach fill" x="152" y="{Y + 6}" width="22" height="16"/>'
            f'<path class="mach" d="M163,{Y - 34} v12 M163,{Y + 22} v12"/>'
            f'<rect class="mach" x="188" y="{Y - 14}" width="18" height="28"/><path class="mach" d="M192,{Y} h10"/>')
    # 3 entry accumulator
    rollers = "".join(f'<circle class="mach fill" cx="{x}" cy="62" r="7"/>' for x in (245, 272, 299)) + \
              "".join(f'<circle class="mach fill" cx="{x}" cy="222" r="7"/>' for x in (258, 285, 312))
    station(2, 220, 330,
            f'<rect class="mach" x="230" y="40" width="94" height="200" stroke-dasharray="2 4"/>{rollers}')
    # 4 cleaning & pre-treatment
    tanks = ""
    for k, x in enumerate(range(344, 476, 33)):
        tanks += f'<rect class="mach fill" x="{x}" y="{Y + 10}" width="27" height="40"/>'
        tanks += f'<path class="mach" d="M{x + 5},{Y - 14} l4,8 M{x + 13},{Y - 16} v10 M{x + 21},{Y - 14} l-4,8"/>'
    station(3, 330, 480, f'<rect class="mach" x="336" y="{Y - 30}" width="138" height="88" stroke-dasharray="2 4"/>{tanks}')
    # 5 primer coater
    station(4, 480, 548,
            f'<circle class="mach fill" cx="506" cy="{Y - 12}" r="11"/><circle class="mach" cx="522" cy="{Y - 34}" r="9"/>'
            f'<circle class="mach fill" cx="506" cy="{Y + 12}" r="11"/><circle class="mach" cx="522" cy="{Y + 34}" r="9"/>'
            f'<path class="mach" d="M488,{Y + 60} h44"/>')
    # 6 primer oven & quench
    station(5, 548, 720,
            f'<rect class="heat" x="556" y="{Y - 30}" width="128" height="60"/>'
            + "".join(f'<path class="mach" d="M{x},{Y - 30} v60" stroke-dasharray="2 3"/>' for x in (588, 620, 652)) +
            f'<rect class="mach fill" x="692" y="{Y - 22}" width="20" height="44"/>'
            f'<path class="mach" d="M697,{Y - 32} l3,6 M707,{Y - 32} l-3,6"/>'
            f'<path class="mach" d="M600,{Y - 30} v-28 h12 v28" />')
    # 7 finish coater
    station(6, 720, 788,
            f'<circle class="mach fill" cx="746" cy="{Y - 12}" r="11"/><circle class="mach" cx="762" cy="{Y - 34}" r="9"/>'
            f'<circle class="mach fill" cx="746" cy="{Y + 12}" r="11"/><circle class="mach" cx="762" cy="{Y + 34}" r="9"/>'
            f'<path class="mach" d="M728,{Y + 60} h44"/>')
    # 8 finish oven & quench
    station(7, 788, 1000,
            f'<rect class="heat" x="796" y="{Y - 30}" width="150" height="60"/>'
            + "".join(f'<path class="mach" d="M{x},{Y - 30} v60" stroke-dasharray="2 3"/>' for x in (834, 872, 910)) +
            f'<rect class="mach fill" x="956" y="{Y - 22}" width="20" height="44"/>'
            f'<path class="mach" d="M961,{Y - 32} l3,6 M971,{Y - 32} l-3,6"/>'
            f'<path class="mach" d="M846,{Y - 30} v-28 h12 v28" /><path class="mach" d="M852,{Y - 58} v-14" stroke-dasharray="2 2"/>')
    # 9 exit accumulator & inspection
    rollers2 = "".join(f'<circle class="mach fill" cx="{x}" cy="62" r="7"/>' for x in (1022, 1045, 1068)) + \
               "".join(f'<circle class="mach fill" cx="{x}" cy="222" r="7"/>' for x in (1034, 1057, 1080))
    station(8, 1000, 1098,
            f'<rect class="mach" x="1006" y="40" width="86" height="200" stroke-dasharray="2 4"/>{rollers2}')
    # 10 recoiler
    station(9, 1098, 1190,
            f'<path class="mach" d="M1104,{Y - 10} l8,10 l-8,10"/>'
            f'<circle class="mach fill" cx="1150" cy="{Y - 52}" r="24"/><circle class="mach" cx="1150" cy="{Y - 52}" r="6"/>'
            f'<path class="mach" d="M1128,{Y + 6} h44 M1150,{Y - 28} v34"/>')
    g.append("</svg>")
    return "\n".join(g)

# ------------------------------------------------------------------ page parts
def head(lang, title, desc, prefix, path_en, path_es, extra=""):
    t = T[lang]
    robots = '<meta name="robots" content="noindex, nofollow, noarchive">' if NOINDEX else '<meta name="robots" content="index, follow">'
    url = SITE_URL + (path_en if lang == "en" else path_es)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<meta name="theme-color" content="#F3F1EC">
<meta name="author" content="{esc(COMPANY['legal_name'])}">
<link rel="alternate" hreflang="en" href="{SITE_URL}{path_en}">
<link rel="alternate" hreflang="es" href="{SITE_URL}{path_es}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}{path_en}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="INCO">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{t['og_locale']}">
<meta property="og:locale:alternate" content="{T['es' if lang == 'en' else 'en']['og_locale']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{prefix}assets/fonts/playfair-display-latin-900-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/fonts/newsreader-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/css/site.css">
{extra}</head>
"""

def header(lang, prefix, home, alt_href, on_home=True):
    t = T[lang]
    nav = "".join(f'<li><a href="{"" if on_home else home}{h}">{esc(n)}</a></li>' for h, n in t["nav"])
    en_href = alt_href if lang == "es" else "#"
    es_href = alt_href if lang == "en" else "#"
    def l(code, href):
        cur = ' aria-current="true"' if code == lang else ""
        return f'<a href="{href}" hreflang="{code}" lang="{code}" data-setlang="{code}"{cur}>{code.upper()}</a>'
    return f"""<a class="sr" href="#main">{esc(t['skip'])}</a>
<header class="hdr">
  <div class="wrap">
    <a class="brand" href="{home}" aria-label="INCO — home"><b>INCO</b><i aria-hidden="true"></i><span>{t['logo_sub']}</span></a>
    <ul class="nav">{nav}</ul>
    <div class="lang" role="group" aria-label="Language">{l('en', en_href)}{l('es', es_href)}</div>
    <button class="menu-btn" aria-expanded="false" aria-label="{esc(t['menu'])}"><i></i></button>
  </div>
</header>
"""

def footer(lang, prefix, home, legal, on_home=True):
    t = T[lang]
    navl = "".join(f'<li><a href="{"" if on_home else home}{h}">{esc(n)}</a></li>' for h, n in t["nav"])
    certs = "".join(
        f'<div class="seal" title="{esc(c["code"])}">{seal(c)}<span><b>{esc(c["code"])}</b>{esc(c[lang])}</span></div>'
        for c in CERTS)
    legal_links = "".join(f'<a href="{legal}#{a}">{esc(n)}</a>' for a, n in t["ft_legal"])
    addr = COMPANY["address_en"] if lang == "en" else COMPANY["address"]
    return f"""<footer class="ftr">
  <div class="wrap">
    <div class="ftop">
      <div>
        <a class="brand" href="{home}" aria-label="INCO"><b>INCO</b><i aria-hidden="true"></i><span>{t['logo_sub']}</span></a>
        <p class="ftag">{esc(t['ft_tag'])}</p>
      </div>
      <div><h4>{esc(t['ft_nav'])}</h4><ul>{navl}</ul></div>
      <div><h4>{esc(t['ft_contact'])}</h4><ul>
        <li><a href="tel:{COMPANY['phone_href']}">{esc(COMPANY['phone'])}</a></li>
        <li><a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></li>
      </ul></div>
      <div><h4>{esc(t['ft_offices'])}</h4>
        <address><b>Barcelona</b>{esc(addr)}</address>
        <address><b>{'Geneva' if lang == 'en' else 'Ginebra'}</b>{esc(t['gva_addr'])}</address>
      </div>
    </div>
    <!-- Certification seals: PENDING CONFIRMATION of INCO's actual certificates -->
    <div class="certs"><span class="ct">{esc(t['ft_certs'])}</span>{certs}</div>
    <div class="fbot">
      <span>© {COMPANY_YEAR} INCO — {esc(COMPANY['legal_name'])}. {esc(t['rights'])}</span>
      <nav aria-label="Legal">{legal_links}</nav>
    </div>
  </div>
</footer>
"""

COMPANY_YEAR = 2026

def src(img, prefix):
    return img if img.startswith("http") else prefix + img

def i18n_script(lang, prefix=""):
    t = T[lang]
    keys = ["showing", "showingOne", "formProto", "formSending", "formOk", "formErr"]
    data = {k: t[k] for k in keys}
    projects = []
    proc_names = {k: (en if lang == "en" else es) for k, en, es in PROCESSES}
    metal_names = {k: (en if lang == "en" else es) for k, en, es in METALS}
    for p in PROJECTS:
        c = p[lang]
        projects.append({
            "id": p["id"], "img": src(p["img"], prefix), "title": c["title"], "desc": c["desc"],
            "tag": proc_names[p["process"]] + " · " + " / ".join(metal_names[m] for m in p["metals"]) + " · " + c["sector"],
            "specs": p["specs_" + lang], "formProcess": p["process"],
        })
    return (f"<script>window.INCO_I18N={json.dumps(data, ensure_ascii=False)};"
            f"window.INCO_PROJECTS={json.dumps(projects, ensure_ascii=False)};</script>")

# ------------------------------------------------------------------ home page
def home_page(lang):
    t = T[lang]
    prefix = "" if lang == "en" else "../"
    home = "index.html"
    alt = "es/index.html" if lang == "en" else "../index.html"
    legal = "legal/index.html"
    proc_names = {k: (en if lang == "en" else es) for k, en, es in PROCESSES}
    metal_names = {k: (en if lang == "en" else es) for k, en, es in METALS}

    # first-visit language detection (root page only): Spanish browsers go to /es/
    detect = ""
    if lang == "en":
        detect = ("<script>(function(){try{var s=localStorage.getItem('inco-lang');"
                  "var n=(navigator.languages&&navigator.languages[0])||navigator.language||'';"
                  "if(s==='es'||(!s&&/^(es|ca|gl|eu)\\b/i.test(n))){location.replace('es/index.html'+location.search+location.hash);}"
                  "}catch(e){}})();</script>\n")

    out = [head(lang, t["title"], t["desc"], prefix, "", "es/", detect)]
    out.append("<body>")
    out.append(header(lang, prefix, home, alt))
    out.append('<main id="main">')

    # hero
    stats = "".join(f'<div class="stat"><b>{esc(n)}</b><span>{esc(l)}</span></div>' for n, l in t["stats"])
    out.append(f"""
<section class="hero" id="top">
  <div class="wrap">
    <div class="hero-grid">
      <div class="rv">
        <p class="eyebrow">{esc(t['hero_eyebrow'])}</p>
        <h1>{t['hero_h1']}</h1>
        <p class="lede">{esc(t['hero_lede'])}</p>
        <div class="cta">
          <a class="btn btn-dark" href="#projects">{esc(t['cta1'])} {ICON['arrow']}</a>
          <a class="btn btn-line" href="#contact">{esc(t['cta2'])}</a>
        </div>
      </div>
      <figure class="hero-fig rv">
        <div class="duo"><img src="{IMG['hero']}" alt="{esc(t['fig_cap'][0])}" fetchpriority="high"></div>
        <figcaption class="fig-cap"><span>{esc(t['fig_cap'][0])}</span><span>{esc(t['fig_cap'][1])}</span></figcaption>
      </figure>
    </div>
    <div class="stats rv">{stats}</div>
  </div>
</section>""")

    # company
    principles = "".join(f'<li><span>0{i + 1}</span>{esc(p)}</li>' for i, p in enumerate(t["principles"]))
    paras = "".join(f"<p>{esc(p)}</p>" for p in t["co_p"])
    out.append(f"""
<section id="company">
  <div class="wrap">
    <div class="about">
      <div class="rv">
        <p class="eyebrow"><span class="n">01</span> {esc(t['co_eyebrow'])}</p>
        <h2 style="margin:22px 0 40px">{t['co_h2']}</h2>
        <div class="duo"><img src="{IMG['about']}" alt="" loading="lazy"></div>
      </div>
      <div class="about-txt rv">
        {paras}
        <ul class="principles">{principles}</ul>
        <div class="quality">{ICON['check']}<div><h3>{esc(t['quality_h'])}</h3><p>{esc(t['quality_p'])}</p></div></div>
      </div>
    </div>
  </div>
</section>""")

    # capabilities
    caps = "".join(
        f'<article class="cap rv"><span class="num">0{i + 1}</span>{ICON[ic]}<h3>{esc(h)}</h3><p>{esc(p)}</p></article>'
        for i, (ic, h, p) in enumerate(t["caps"]))
    out.append(f"""
<section id="capabilities" class="alt">
  <div class="wrap">
    <div class="sec-head rv">
      <div><p class="eyebrow"><span class="n">02</span> {esc(t['cap_eyebrow'])}</p><h2>{t['cap_h2']}</h2></div>
      <p class="lede">{esc(t['cap_lede'])}</p>
    </div>
    <div class="caps">{caps}</div>
  </div>
</section>""")

    # process schema
    first = STATIONS[0]
    out.append(f"""
<section id="process" class="dark">
  <div class="wrap">
    <div class="sec-head rv">
      <div><p class="eyebrow"><span class="n">03</span> {esc(t['pr_eyebrow'])}</p><h2>{t['pr_h2']}</h2></div>
      <p class="lede">{esc(t['pr_lede'])}</p>
    </div>
    <div class="schema-wrap rv">
      <div class="schema-scroll">
{schema_svg(lang)}
      </div>
      <div class="schema-panel" aria-live="polite">
        <div class="pn">01</div>
        <div><h3>{esc(first[0] if lang == 'en' else first[1])}</h3><p>{esc(first[2] if lang == 'en' else first[3])}</p></div>
        <div class="schema-nav">
          <button type="button" data-schema="prev" aria-label="{esc(t['pr_prev'])}">{ICON['prev']}</button>
          <button type="button" data-schema="next" aria-label="{esc(t['pr_next'])}">{ICON['next']}</button>
        </div>
      </div>
    </div>
    <div class="schema-note"><span>{esc(t['pr_note'])}</span>
      <span class="legend"><span><i></i>{esc(t['pr_legend'][0])}</span><span><i class="h"></i>{esc(t['pr_legend'][1])}</span></span></div>
  </div>
</section>""")

    # timeline
    tl = ""
    for i, row in enumerate(TIMELINE):
        en_n, es_n, en_s, es_s, en_d, es_d, en_o, es_o = row
        n, s, d, o = (en_n, en_s, en_d, en_o) if lang == "en" else (es_n, es_s, es_d, es_o)
        tl += (f'<li><span class="ph">{PHASE[lang]} {i + 1:02d}</span><h3>{esc(n)}</h3>'
               f'<p>{esc(d)}</p><span class="out">→ {esc(o)}</span></li>')
    out.append(f"""
<section id="service">
  <div class="wrap">
    <div class="sec-head rv">
      <div><p class="eyebrow"><span class="n">04</span> {esc(t['tl_eyebrow'])}</p><h2>{t['tl_h2']}</h2></div>
      <p class="lede">{esc(t['tl_lede'])}</p>
    </div>
    <ol class="timeline">{tl}</ol>
  </div>
</section>""")

    # projects
    def chips(key, items):
        b = [f'<button type="button" class="chip" data-key="{key}" data-val="all" aria-pressed="true">{esc(t["f_all"])} <sup></sup></button>']
        for k, en, es in items:
            b.append(f'<button type="button" class="chip" data-key="{key}" data-val="{k}" aria-pressed="false">{esc(en if lang == "en" else es)} <sup></sup></button>')
        return "".join(b)
    cards = ""
    for p in PROJECTS:
        c = p[lang]
        key_specs = p["specs_" + lang][:2]
        key = "".join(f"<span>{esc(v)}</span>" for _, v in key_specs)
        metals = " / ".join(metal_names[m] for m in p["metals"])
        cards += (f'<button type="button" class="pc" data-id="{p["id"]}" data-process="{p["process"]}" data-metal="{" ".join(p["metals"])}">'
                  f'<div class="duo"><img src="{src(p["img"], prefix)}" alt="" loading="lazy"></div>'
                  f'<div class="meta"><span class="pr">{esc(proc_names[p["process"]])}</span><span>{esc(metals)}</span></div>'
                  f'<h3>{esc(c["title"])}</h3><div class="key">{key}</div></button>')
    out.append(f"""
<section id="projects" class="alt">
  <div class="wrap">
    <div class="sec-head rv">
      <div><p class="eyebrow"><span class="n">05</span> {esc(t['pj_eyebrow'])}</p><h2>{t['pj_h2']}</h2></div>
      <p class="lede">{esc(t['pj_lede'])}</p>
    </div>
    <div class="filters" role="group" aria-label="Filters">
      <div class="frow-f"><span class="flab">{esc(t['f_process'])}</span><div class="chips">{chips('process', PROCESSES)}</div></div>
      <div class="frow-f"><span class="flab">{esc(t['f_metal'])}</span><div class="chips">{chips('metal', METALS)}</div></div>
    </div>
    <div class="fstatus"><span id="fcount" aria-live="polite"></span><button type="button" id="freset" hidden>{esc(t['reset'])}</button></div>
    <div class="pgrid" id="pgrid">{cards}<p class="empty" id="fempty" hidden>{esc(t['empty'])}</p></div>
  </div>
</section>""")

    # contact
    f = t["form"]
    proc_opts = "".join(f'<option value="{k}">{esc(proc_names[k])}</option>' for k, _, _ in PROCESSES)
    proc_opts += f'<option value="rolling">{"Rolling mill" if lang == "en" else "Laminador"}</option><option value="other">{esc(f["other"])}</option>'
    metal_opts = "".join(f'<option value="{k}">{esc(metal_names[k])}</option>' for k, _, _ in METALS)
    metal_opts += f'<option value="other">{esc(f["other"])}</option>'
    cl = t["ct_labels"]
    addr = COMPANY["address_en"] if lang == "en" else COMPANY["address"]
    req = f' <i aria-hidden="true">*</i>'
    out.append(f"""
<section id="contact">
  <div class="wrap">
    <div class="contact">
      <div class="cinfo rv">
        <p class="eyebrow"><span class="n">06</span> {esc(t['ct_eyebrow'])}</p>
        <h2 style="margin:22px 0 24px">{t['ct_h2']}</h2>
        <p class="lede">{esc(t['ct_lede'])}</p>
        <dl>
          <div><dt>{esc(cl['phone'])}</dt><dd><a href="tel:{COMPANY['phone_href']}">{esc(COMPANY['phone'])}</a></dd></div>
          <div><dt>{esc(cl['email'])}</dt><dd><a href="mailto:{COMPANY['email']}">{esc(COMPANY['email'])}</a></dd></div>
          <div><dt>{esc(cl['bcn'])}</dt><dd>{esc(addr)}</dd></div>
          <div><dt>{esc(cl['gva'])}</dt><dd>{esc(t['gva_addr'])}</dd></div>
        </dl>
      </div>
      <form class="form rv" id="enquiry" data-key="{esc(WEB3FORMS_KEY)}" novalidate>
        <input type="hidden" name="subject" value="{'New enquiry — INCO website' if lang == 'en' else 'Nueva consulta — web INCO'}">
        <input type="hidden" name="from_name" value="INCO website">
        <input type="hidden" name="language" value="{lang}">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="fld"><label for="f-name">{esc(f['name'])}{req}</label><input id="f-name" name="name" required autocomplete="name"></div>
        <div class="fld"><label for="f-company">{esc(f['company'])}{req}</label><input id="f-company" name="company" required autocomplete="organization"></div>
        <div class="fld"><label for="f-email">{esc(f['email'])}{req}</label><input id="f-email" type="email" name="email" required autocomplete="email"></div>
        <div class="fld"><label for="f-country">{esc(f['country'])}</label><input id="f-country" name="country" autocomplete="country-name"></div>
        <div class="fld"><label for="f-process">{esc(f['process'])}</label><select id="f-process" name="process"><option value="">{esc(f['select'])}</option>{proc_opts}</select></div>
        <div class="fld"><label for="f-metal">{esc(f['metal'])}</label><select id="f-metal" name="metal"><option value="">{esc(f['select'])}</option>{metal_opts}</select></div>
        <div class="tech">
          <span class="tl">{esc(f['tech'])}</span>
          <div class="fld"><label for="f-width">{esc(f['width'])}</label><input id="f-width" name="strip_width_mm" inputmode="decimal"></div>
          <div class="fld"><label for="f-thick">{esc(f['thick'])}</label><input id="f-thick" name="thickness_mm" inputmode="decimal"></div>
          <div class="fld"><label for="f-cap">{esc(f['cap'])}</label><input id="f-cap" name="capacity_t_year" inputmode="decimal"></div>
        </div>
        <div class="fld full"><label for="f-msg">{esc(f['msg'])}{req}</label><textarea id="f-msg" name="message" required></textarea></div>
        <label class="consent"><input type="checkbox" name="privacy_consent" value="yes" required> <span>{f['consent'].format(legal=legal)}</span></label>
        <div class="fsend"><button class="btn btn-dark" type="submit">{esc(f['send'])} {ICON['arrow']}</button><p class="fmsg" role="status"></p></div>
      </form>
    </div>
  </div>
</section>""")

    out.append("</main>")
    out.append(footer(lang, prefix, home, legal))

    # modal
    out.append(f"""
<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="m-title">
  <div class="mbox">
    <div class="duo"><img src="" alt=""></div>
    <div class="mbody">
      <button type="button" class="mclose" aria-label="{esc(t['close'])}">{ICON['close']}</button>
      <p class="meta"></p>
      <h3 id="m-title"></h3>
      <p class="mdesc"></p>
      <table class="specs"><tbody></tbody></table>
      <a class="btn btn-dark mcta" href="#contact">{esc(t['m_cta'])} {ICON['arrow']}</a>
    </div>
  </div>
</div>""")
    out.append(i18n_script(lang, prefix))
    out.append(f'<script src="{prefix}assets/js/site.js" defer></script>')
    out.append("</body>\n</html>\n")
    return "\n".join(out)

# ------------------------------------------------------------------ legal page
def legal_page(lang):
    t = T[lang]
    prefix = "../" if lang == "en" else "../../"
    home = "../index.html"
    alt = "../es/legal/index.html" if lang == "en" else "../../legal/index.html"
    c = COMPANY
    nif = c["nif"] or pend(lang, "NIF" if lang == "es" else "Tax ID (NIF)")
    reg = c["registry"] or pend(lang, "Registro Mercantil de Barcelona, tomo, folio, hoja" if lang == "es" else "Barcelona Commercial Register, volume, folio, sheet")
    addr = c["address"] if lang == "es" else c["address_en"]
    updated = "Última actualización: noviembre de 2026" if lang == "es" else "Last updated: November 2026"

    if lang == "es":
        toc = [("legal", "Aviso legal"), ("privacy", "Política de privacidad"), ("cookies", "Política de cookies")]
        body = f"""
<h2 id="legal">Aviso legal</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de los datos identificativos del titular de este sitio web:</p>
<dl>
  <dt>Titular</dt><dd>{esc(c['legal_name'])} (INCO)</dd>
  <dt>NIF</dt><dd>{nif}</dd>
  <dt>Domicilio social</dt><dd>{esc(addr)}</dd>
  <dt>Datos registrales</dt><dd>{reg}</dd>
  <dt>Teléfono</dt><dd>{esc(c['phone'])}</dd>
  <dt>Email</dt><dd><a href="mailto:{c['email']}">{esc(c['email'])}</a></dd>
</dl>
<h3>Condiciones de uso</h3>
<p>El acceso a este sitio web es gratuito y atribuye la condición de usuario, que acepta estas condiciones. El usuario se compromete a hacer un uso adecuado de los contenidos y a no emplearlos para actividades ilícitas o contrarias a la buena fe.</p>
<h3>Propiedad intelectual e industrial</h3>
<p>Los contenidos de este sitio (textos, imágenes, diseño gráfico, esquemas, logotipos y código) son titularidad de {esc(c['legal_name'])} o de terceros que han autorizado su uso. Queda prohibida su reproducción, distribución o transformación sin autorización expresa. Los datos técnicos de los proyectos son orientativos y no constituyen una oferta vinculante.</p>
<h3>Responsabilidad</h3>
<p>INCO no se hace responsable de los daños derivados del uso de la información de este sitio, ni de interrupciones del servicio, ni de los contenidos de sitios de terceros enlazados desde él.</p>
<h3>Legislación aplicable</h3>
<p>Estas condiciones se rigen por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales de Barcelona, salvo que la normativa aplicable disponga otra cosa.</p>

<h2 id="privacy">Política de privacidad</h2>
<p>Esta política explica cómo se tratan los datos personales recogidos a través de este sitio, conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD).</p>
<h3>Responsable del tratamiento</h3>
<p>{esc(c['legal_name'])}, {nif}, {esc(addr)}. Contacto: <a href="mailto:{c['email']}">{esc(c['email'])}</a>.</p>
<h3>Datos que tratamos y finalidad</h3>
<p>A través del formulario de contacto recogemos nombre, empresa, email, país y la información técnica que nos facilite, con la única finalidad de atender su consulta y, en su caso, preparar una propuesta. No elaboramos perfiles ni tomamos decisiones automatizadas.</p>
<h3>Base jurídica</h3>
<p>Su consentimiento, otorgado al enviar el formulario (art. 6.1.a RGPD), y la aplicación de medidas precontractuales a petición suya (art. 6.1.b RGPD).</p>
<h3>Conservación</h3>
<p>Conservamos los datos el tiempo necesario para atender la consulta y, después, durante los plazos legales que puedan derivarse de la relación. Si no se inicia una relación comercial, se suprimen en un plazo máximo de 12 meses.</p>
<h3>Destinatarios y encargados del tratamiento</h3>
<ul>
  <li><strong>Web3Forms</strong> — servicio que transmite el formulario por email.</li>
  <li><strong>GitHub, Inc.</strong> — alojamiento del sitio web; puede registrar datos técnicos de conexión (como la dirección IP) por motivos de seguridad.</li>
</ul>
<p>Algunos de estos proveedores pueden tratar datos fuera del Espacio Económico Europeo; en ese caso, las transferencias se amparan en el Marco de Privacidad de Datos UE-EE. UU. o en cláusulas contractuales tipo aprobadas por la Comisión Europea. No cedemos datos a terceros salvo obligación legal.</p>
<h3>Sus derechos</h3>
<p>Puede ejercer sus derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad, así como retirar su consentimiento, escribiendo a <a href="mailto:{c['email']}">{esc(c['email'])}</a>. Si considera que sus derechos no han sido atendidos, puede presentar una reclamación ante la Agencia Española de Protección de Datos (aepd.es).</p>

<h2 id="cookies">Política de cookies</h2>
<p>Este sitio <strong>no utiliza cookies</strong> de análisis, publicidad ni de terceros, y las tipografías se sirven desde el propio servidor.</p>
<p>Únicamente se guarda en el almacenamiento local de su navegador su preferencia de idioma (clave <span class="mono">inco-lang</span>), cuando la elige expresamente. Es un dato técnico necesario para prestar el servicio solicitado y está exento de consentimiento conforme al artículo 22.2 de la LSSI-CE. Puede borrarlo en cualquier momento desde la configuración de su navegador.</p>
<p>Si en el futuro se incorporan herramientas de analítica u otras cookies no necesarias, se solicitará su consentimiento previo y se actualizará esta política.</p>
"""
    else:
        toc = [("legal", "Legal notice"), ("privacy", "Privacy policy"), ("cookies", "Cookie policy")]
        body = f"""
<h2 id="legal">Legal notice</h2>
<p>In accordance with article 10 of Spanish Law 34/2002 on Information Society Services and Electronic Commerce (LSSI-CE), the owner of this website is identified as follows:</p>
<dl>
  <dt>Owner</dt><dd>{esc(c['legal_name'])} (INCO)</dd>
  <dt>Tax ID (NIF)</dt><dd>{nif}</dd>
  <dt>Registered office</dt><dd>{esc(addr)}</dd>
  <dt>Registry details</dt><dd>{reg}</dd>
  <dt>Phone</dt><dd>{esc(c['phone'])}</dd>
  <dt>Email</dt><dd><a href="mailto:{c['email']}">{esc(c['email'])}</a></dd>
</dl>
<h3>Terms of use</h3>
<p>Access to this website is free of charge and makes you a user who accepts these terms. Users agree to use the content appropriately and not for unlawful purposes or in bad faith.</p>
<h3>Intellectual and industrial property</h3>
<p>The content of this site (text, images, graphic design, diagrams, logos and code) belongs to {esc(c['legal_name'])} or to third parties who have authorised its use. Reproduction, distribution or modification without express permission is prohibited. Project technical data is indicative and does not constitute a binding offer.</p>
<h3>Liability</h3>
<p>INCO accepts no liability for damage arising from the use of information on this site, for service interruptions, or for the content of third-party sites linked from it.</p>
<h3>Governing law</h3>
<p>These terms are governed by Spanish law. Any dispute shall be submitted to the courts of Barcelona, unless applicable law provides otherwise.</p>

<h2 id="privacy">Privacy policy</h2>
<p>This policy explains how personal data collected through this site is processed, in accordance with Regulation (EU) 2016/679 (GDPR) and Spanish Organic Law 3/2018 (LOPDGDD).</p>
<h3>Data controller</h3>
<p>{esc(c['legal_name'])}, {nif}, {esc(addr)}. Contact: <a href="mailto:{c['email']}">{esc(c['email'])}</a>.</p>
<h3>Data we process and why</h3>
<p>Through the contact form we collect your name, company, email, country and any technical information you provide, solely to answer your enquiry and, where relevant, prepare a proposal. We do not profile users or make automated decisions.</p>
<h3>Legal basis</h3>
<p>Your consent, given when you submit the form (art. 6.1.a GDPR), and steps taken at your request prior to entering into a contract (art. 6.1.b GDPR).</p>
<h3>Retention</h3>
<p>We keep the data for as long as needed to handle the enquiry and then for any legally required periods. If no business relationship follows, the data is deleted within 12 months at the latest.</p>
<h3>Recipients and processors</h3>
<ul>
  <li><strong>Web3Forms</strong> — service that relays the form by email.</li>
  <li><strong>GitHub, Inc.</strong> — website hosting; may log technical connection data (such as IP addresses) for security purposes.</li>
</ul>
<p>Some of these providers may process data outside the European Economic Area; such transfers rely on the EU-US Data Privacy Framework or on standard contractual clauses approved by the European Commission. We do not share data with third parties unless legally required.</p>
<h3>Your rights</h3>
<p>You may exercise your rights of access, rectification, erasure, objection, restriction and portability, and withdraw consent, by writing to <a href="mailto:{c['email']}">{esc(c['email'])}</a>. You may also lodge a complaint with the Spanish Data Protection Agency (aepd.es).</p>

<h2 id="cookies">Cookie policy</h2>
<p>This site <strong>does not use cookies</strong> for analytics, advertising or third parties, and fonts are served from our own server.</p>
<p>Only your language preference (key <span class="mono">inco-lang</span>) is stored in your browser's local storage, when you choose it explicitly. This is technical data needed to provide the service you requested and is exempt from consent under article 22.2 LSSI-CE. You can delete it at any time in your browser settings.</p>
<p>Should analytics or other non-essential cookies be added in future, your prior consent will be requested and this policy updated.</p>
"""
    tocl = "".join(f'<li><a href="#{a}">{esc(n)}</a></li>' for a, n in toc)
    out = [head(lang, t["legal_title"] + " — INCO", t["legal_desc"], prefix, "legal/", "es/legal/")]
    out.append("<body>")
    out.append(header(lang, prefix, home, alt, on_home=False))
    out.append(f"""<main id="main" class="legal">
  <div class="wrap">
    <!-- Recommended legal text (LSSI-CE / GDPR). To be reviewed by INCO's legal advisor before launch. -->
    <p class="eyebrow">INCO</p>
    <h1>{esc(t['legal_title'])}</h1>
    <p class="upd">{updated}</p>
    <div class="legal-grid">
      <ul class="toc">{tocl}<li><a href="{home}">← {esc(t['back'])}</a></li></ul>
      <article>{body}</article>
    </div>
  </div>
</main>""")
    out.append(footer(lang, prefix, home, "index.html", on_home=False))
    out.append(f'<script src="{prefix}assets/js/site.js" defer></script>')
    out.append("</body>\n</html>\n")
    return "\n".join(out)

# ------------------------------------------------------------------ build
def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("  wrote", rel)

def main():
    print("Building INCO site…")
    write("index.html", home_page("en"))
    write("es/index.html", home_page("es"))
    write("legal/index.html", legal_page("en"))
    write("es/legal/index.html", legal_page("es"))
    print("Done.")

if __name__ == "__main__":
    main()
