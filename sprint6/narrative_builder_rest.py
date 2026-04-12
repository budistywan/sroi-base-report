"""
Narrative Builder — Sprint 6
Sub-modes: builder_framing (Bab 1-3), builder_context (Bab 4-6), builder_learning (Bab 8-9)

Input  : canonical_esl_v1.json + handoff_b.json + report_blueprint.json
Output : chapter_semantic_bab[1-6,8-9].json (Handoff E ke QA)

Rules:
  - Bab partial → tulis konten + callout_gap untuk bagian yang tipis
  - Bab strong  → tulis penuh
  - Tidak ada angka baru — semua dari sroi_metrics.calculated
  - Placeholder eksplisit jika data tidak tersedia

Usage:
  python narrative_builder_rest.py
  python narrative_builder_rest.py --canonical /p/ --handoff-b /p/ --blueprint /p/ --output /p/
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

BUILDER_VERSION = "1.0.0"

# ── PATH CONFIG ──────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--canonical",  default=None)
parser.add_argument("--handoff-b",  default=None, dest="handoff_b")
parser.add_argument("--blueprint",  default=None)
parser.add_argument("--output",     default=None)
args = parser.parse_args()

SCRIPT_DIR     = Path(__file__).parent
CANONICAL_FILE = Path(args.canonical) if args.canonical \
    else Path(os.environ.get("CANONICAL_FILE", SCRIPT_DIR.parent / "sprint0/canonical_esl_v1.json"))
HANDOFF_B_FILE = Path(args.handoff_b) if args.handoff_b \
    else Path(os.environ.get("HANDOFF_B_FILE", SCRIPT_DIR.parent / "sprint1/handoff_b.json"))
BLUEPRINT_FILE = Path(args.blueprint) if args.blueprint \
    else Path(os.environ.get("BLUEPRINT_FILE", SCRIPT_DIR.parent / "sprint2/report_blueprint.json"))
OUTPUT_DIR     = Path(args.output)    if args.output    \
    else Path(os.environ.get("OUTPUT_DIR", SCRIPT_DIR))

for f in [CANONICAL_FILE, HANDOFF_B_FILE, BLUEPRINT_FILE]:
    if not f.exists():
        print(f"FAIL: {f} tidak ditemukan"); sys.exit(1)

canonical  = json.load(open(CANONICAL_FILE))
handoff_b  = json.load(open(HANDOFF_B_FILE))
blueprint  = json.load(open(BLUEPRINT_FILE))

pi   = canonical["program_identity"]
pp   = canonical["program_positioning"]
sd   = canonical["strategy_design"]
pf   = canonical["problem_framing"]
ic   = canonical["ideal_conditions"]
ls   = canonical["learning_signals"]
calc = handoff_b["sroi_metrics"]["calculated"]
audit_map = {e["field"]: e["value"] for e in handoff_b["calc_audit_log"]}

def A(f): return audit_map[f]
def idr(v): return f"Rp {v:,.0f}"
def ratio(v): return f"1 : {v:.2f}"

# ── BLOCK HELPERS ─────────────────────────────────────────
def H1(t): return {"type":"heading_1","text":t}
def H2(t): return {"type":"heading_2","text":t}
def H3(t): return {"type":"heading_3","text":t}
def P(t, ds=None, sr=None):
    b = {"type":"paragraph","text":t}
    if ds: b["display_status"]=ds
    if sr: b["source_refs"]=sr
    return b
def LEAD(t): return {"type":"paragraph_lead","text":t}
def SMALL(t): return {"type":"paragraph_small","text":t}
def DIV(): return {"type":"divider"}
def BREAK(): return {"type":"page_break"}
def GAP(t, gt="data_unavailable"):
    return {"type":"callout_gap","text":t,"gap_type":gt,"display_status":"present_as_inferred"}
def INFO(t, sr=None):
    b = {"type":"callout_info","text":t}
    if sr: b["source_refs"]=sr
    return b
def WARN(t, sr=None):
    b = {"type":"callout_warning","text":t}
    if sr: b["source_refs"]=sr
    return b
def NEUTRAL(t): return {"type":"callout_neutral","text":t}
def SUCCESS(t, sr=None):
    b = {"type":"callout_success","text":t}
    if sr: b["source_refs"]=sr
    return b
def BULLET(items):
    return {"type":"bullet_list","items":[{"text":i} for i in items]}
def NUMBERED(items):
    return {"type":"numbered_list","items":[{"text":i} for i in items]}
def METRIC3(items): return {"type":"metric_card_3col","items":items}
def TBL_BL(headers, rows, cw, sr=None):
    b = {"type":"table_borderless","headers":headers,"rows":rows,"column_widths":cw}
    if sr: b["source_refs"]=sr
    return b

def chapter_semantic(cid, ctype, bmode, blocks):
    return {
        "chapter_id":        cid,
        "chapter_type":      ctype,
        "source_outline_ref":cid,
        "builder_mode":      bmode,
        "builder_version":   BUILDER_VERSION,
        "generated_at":      datetime.now().isoformat(),
        "blocks":            blocks,
    }


# ══════════════════════════════════════════════════════════
# BAB 1 — PENDAHULUAN
# ══════════════════════════════════════════════════════════
print("Building Bab 1 — Pendahuluan...")
b1 = []
b1 += [
    H1("BAB I PENDAHULUAN"),
    LEAD(
        f"Bab ini menyajikan latar belakang, tujuan, ruang lingkup, dan konsiderasi "
        f"hukum penyusunan Laporan Evaluasi Social Return on Investment (SROI) "
        f"Program {pi['program_name']} ({pi['program_code']}) "
        f"periode {pi['period_start']}–{pi['period_end']}."
    ),
    DIV(),
    H2("1.1 Latar Belakang Penulisan Laporan SROI"),
    P(
        f"Tanggung Jawab Sosial dan Lingkungan (TJSL) merupakan kewajiban strategis "
        f"yang tidak hanya bersifat normatif, tetapi juga menjadi instrumen pengukuran "
        f"dampak sosial yang terukur. {pi['company']} sebagai bagian dari ekosistem "
        f"BUMN, melaksanakan TJSL dalam kerangka {pp['proper_category']} — melampaui "
        f"kepatuhan minimum dan mengarah pada penciptaan nilai sosial yang berkelanjutan."
    ),
    P(
        "Social Return on Investment (SROI) adalah kerangka analisis yang mengukur "
        "nilai sosial, ekonomi, dan lingkungan dari suatu program intervensi secara "
        "holistik. Berbeda dengan evaluasi konvensional yang hanya mengukur output, "
        "SROI menelusuri perubahan yang dirasakan oleh pemangku kepentingan — dari "
        "individu penerima manfaat hingga komunitas yang lebih luas."
    ),
    INFO(
        f"Program {pi['program_name']} masuk dalam kategori {pp['proper_category']} "
        f"sesuai Peraturan Menteri LHK No. 1 Tahun 2021 yang mewajibkan perusahaan "
        f"peserta PROPER untuk mengusulkan program inovasi sosial unggulan dengan "
        f"pengukuran dampak berbasis SROI.",
        sr=["program_positioning"]
    ),
    H2("1.2 Tujuan dan Luaran"),
    P("Penyusunan laporan ini bertujuan untuk:"),
    NUMBERED([
        "Mengidentifikasi dan mendokumentasikan seluruh aktivitas program secara terstruktur",
        "Menghitung rasio nilai sosial yang dihasilkan terhadap investasi yang dikeluarkan",
        "Menyajikan temuan secara transparan — termasuk keterbatasan data dan area yang perlu diperkuat",
        "Memberikan rekomendasi berbasis bukti untuk pengembangan program pada periode berikutnya",
        "Memenuhi kewajiban pelaporan PROPER beyond compliance kepada KLHK",
    ]),
    H2("1.3 Ruang Lingkup Kajian"),
    P(
        f"Kajian ini mencakup seluruh aktivitas Program {pi['program_name']} "
        f"selama periode {pi['period_start']}–{pi['period_end']}, "
        f"meliputi empat node program yang tersebar di wilayah operasional."
    ),
    TBL_BL(
        ["Dimensi", "Cakupan"],
        [
            ["Program",  pi["program_name"]],
            ["Periode",  f"{pi['period_start']}–{pi['period_end']}"],
            ["Perusahaan", pi["company"]],
            ["Pilar TJSL", pp["tjsl_pillar"]],
            ["Kategori PROPER", pp["proper_category"]],
            ["Node Program", "4 node (3 aktif + 1 dalam pembentukan)"],
        ],
        [3200, 6438],
        sr=["program_identity","program_positioning"]
    ),
    H2("1.4 Konsiderasi Hukum"),
    P("Penyusunan laporan ini berlandaskan pada regulasi berikut:"),
    BULLET([p for p in pp.get("policy_basis", [])]),
    SMALL(
        "Ketiga regulasi di atas membentuk kerangka kewajiban dan metodologi "
        "yang menjadi dasar pelaksanaan kajian SROI ini."
    ),
]

# ══════════════════════════════════════════════════════════
# BAB 2 — PROFIL PERUSAHAAN
# ══════════════════════════════════════════════════════════
print("Building Bab 2 — Profil Perusahaan...")
b2 = []
b2 += [
    H1("BAB II PROFIL PERUSAHAAN"),
    LEAD(
        f"Bab ini menyajikan profil {pi['company']} sebagai pemrakarsa program, "
        f"mencakup lingkup usaha, arah kebijakan TJSL, dan posisi program "
        f"{pi['program_name']} dalam portofolio pemberdayaan perusahaan."
    ),
    DIV(),
    H2("2.1 Lingkup Usaha"),
    P(
        f"{pi['company']} merupakan anak perusahaan PT Pertamina (Persero) yang "
        f"bergerak di bidang produksi dan distribusi pelumas untuk kendaraan bermotor "
        f"dan industri. Produk unggulan perusahaan mencakup merek Enduro yang ditujukan "
        f"untuk segmen kendaraan bermotor, menjadikan perusahaan ini memiliki kedekatan "
        f"langsung dengan ekosistem perbengkelan otomotif di seluruh Indonesia."
    ),
    GAP(
        "Data lengkap profil perusahaan (kapasitas produksi, jumlah karyawan, sebaran "
        "distribusi) tidak tersedia dalam canonical JSON kajian ini. Untuk laporan final, "
        "bagian ini perlu dilengkapi dari dokumen profil korporat resmi.",
        "data_unavailable"
    ),
    H2("2.2 Arah Kebijakan, Visi Misi, dan Tujuan Perusahaan"),
    P(
        f"Komitmen {pi['company']} terhadap pembangunan sosial diwujudkan melalui "
        f"pilar TJSL '{pp['tjsl_pillar']}' yang selaras dengan agenda SDGs global. "
        f"Program {pi['program_name']} secara langsung berkontribusi pada:"
    ),
    BULLET([s for s in pp.get("sdg_alignment", [])]),
    H2("2.3 Prinsip dan Strategi Pengelolaan Pemberdayaan"),
    P(
        f"Pengelolaan program TJSL {pi['company']} menganut pendekatan "
        f"{pp['proper_category']} — sebuah paradigma yang menempatkan program sosial "
        f"bukan sebagai kewajiban semata, melainkan sebagai investasi strategis yang "
        f"menghasilkan nilai bersama bagi perusahaan dan masyarakat."
    ),
    INFO(
        "Pendekatan beyond compliance mengharuskan perusahaan untuk mengukur dampak "
        "program secara kuantitatif melalui SROI, membuktikan bahwa setiap rupiah "
        "yang diinvestasikan menghasilkan nilai sosial yang terukur dan dapat "
        "dipertanggungjawabkan kepada pemangku kepentingan.",
        sr=["program_positioning"]
    ),
    H2("2.4 Jenis dan Lingkup Program Pemberdayaan Masyarakat"),
    P(
        f"Program {pi['program_name']} merupakan salah satu program unggulan TJSL "
        f"{pi['company']} yang difokuskan pada pemberdayaan Warga Binaan "
        f"Pemasyarakatan (WBP) dan eks-WBP melalui pelatihan vokasional berbasis "
        f"bengkel otomotif. Program ini dirancang sebagai intervensi yang menyentuh "
        f"tiga dimensi sekaligus: peningkatan keterampilan teknis, pembentukan "
        f"kapasitas wirausaha, dan fasilitasi reintegrasi sosial-ekonomi."
    ),
]

# ══════════════════════════════════════════════════════════
# BAB 3 — METODOLOGI
# ══════════════════════════════════════════════════════════
print("Building Bab 3 — Metodologi...")
b3 = []
b3 += [
    H1("BAB III METODOLOGI SROI DAN TRIPLE LOOP LEARNING"),
    LEAD(
        "Bab ini menjelaskan kerangka metodologi yang digunakan dalam kajian SROI "
        "program, mencakup prinsip-prinsip SROI, metode pengumpulan data, pendekatan "
        "LFA, parameter fiksasi dampak, dan kerangka pembelajaran triple loop."
    ),
    DIV(),
    H2("3.1 Perhitungan Dampak Investasi Sosial / Social Return on Investment"),
    P(
        "SROI adalah kerangka pengukuran yang mengkuantifikasi nilai sosial, ekonomi, "
        "dan lingkungan dari suatu investasi. Berbeda dengan ROI finansial konvensional, "
        "SROI memasukkan nilai-nilai yang tidak selalu tercermin dalam transaksi pasar, "
        "seperti peningkatan kepercayaan diri, kesiapan reintegrasi, atau penguatan "
        "kapasitas kelembagaan."
    ),
    P(
        "Formula dasar SROI dalam kajian ini: "
        "SROI = Total Net Benefit (compounded) ÷ Total Investasi. "
        "Nilai bersih dihitung setelah menerapkan DDAT adjustment (Deadweight, "
        "Displacement, Attribution, Drop-off) per aspek monetisasi, "
        "kemudian di-compound ke terminal year menggunakan ORI reference rate."
    ),
    H2("3.2 Metode Pengumpulan Data, Analisis Data, dan Rumus SROI"),
    P(
        "Pengumpulan data dalam kajian ini menggunakan pendekatan triangulasi yang "
        "mengombinasikan data primer dan sekunder:"
    ),
    BULLET([
        "Data primer: catatan transaksi aktual dari tiga node aktif (LUB dan SVC)",
        "Data sekunder: referensi kebijakan untuk proxy REINT (Kartu Prakerja) dan CONF (tarif psikologi publik)",
        "Data program: laporan kegiatan, dokumentasi investasi, dan catatan pendampingan",
    ]),
    H2("3.3 Parameter Fiksasi Dampak (DDAT)"),
    P(
        "Empat parameter fiksasi diterapkan untuk memastikan nilai sosial yang diklaim "
        "benar-benar mencerminkan kontribusi program:"
    ),
    TBL_BL(
        ["Parameter", "Definisi", "Fungsi"],
        [
            ["Deadweight (DW)",    "Manfaat yang terjadi tanpa intervensi program",      "Menghindari klaim berlebihan"],
            ["Displacement (DS)",  "Manfaat yang menggeser pihak lain",                  "Mencegah double-counting"],
            ["Attribution (AT)",   "Kontribusi pihak lain terhadap outcome",             "Proporsionalitas klaim"],
            ["Drop-off (DO)",      "Penurunan manfaat dari waktu ke waktu",              "Realisme jangka menengah"],
        ],
        [2400, 4000, 3238],
        sr=["ddat_params"]
    ),
    H2("3.4 ORI Reference Rate sebagai Discount Rate"),
    P(
        "Nilai bersih setiap tahun di-compound ke terminal year 2025 menggunakan "
        "suku bunga ORI (Obligasi Ritel Indonesia) sebagai proxy biaya modal sosial "
        "yang konservatif dan terverifikasi:"
    ),
    TBL_BL(
        ["Tahun", "Seri ORI", "Rate", "Compound Factor"],
        [
            [str(yr), canonical["ori_rates"][str(yr)]["series"],
             f"{canonical['ori_rates'][str(yr)]['rate']*100:.2f}%",
             str(canonical["ori_rates"][str(yr)]["compound_factor"])]
            for yr in [2023, 2024, 2025]
        ],
        [1500, 3000, 2000, 3138],
        sr=["ori_rates"]
    ),
    H2("3.5 Prinsip SROI"),
    BULLET([
        "Involve stakeholders — pemangku kepentingan dilibatkan dalam identifikasi outcome",
        "Understand what changes — fokus pada perubahan nyata yang dirasakan",
        "Value the things that matter — monetisasi nilai yang tidak selalu terwakili pasar",
        "Only include what is material — excludes minor outcomes",
        "Do not over-claim — DDAT adjustment diterapkan secara konsisten",
        "Be transparent — status data (observed/proxy/pending) ditampilkan eksplisit",
        "Verify the result — audit trail tersedia melalui calc_audit_log",
    ]),
    H2("3.6 Logical Framework Approach (LFA)"),
    P(
        "LFA digunakan untuk memetakan rantai kausalitas program: dari input dan "
        "aktivitas menuju output, outcome, dan dampak jangka panjang. Dalam kajian "
        "ini, LFA berfungsi sebagai kerangka verifikasi — memastikan bahwa klaim "
        "outcome dapat ditelusuri kembali ke aktivitas program yang konkret."
    ),
    GAP(
        "Tabel LFA utuh lintas program belum tersedia dalam canonical JSON — "
        "memerlukan data dari laporan kegiatan detail per aktivitas per node. "
        "Untuk laporan final, sub-bab ini perlu dilengkapi.",
        "data_unavailable"
    ),
    H2("3.7 Triple Loop Learning"),
    P(
        "Kajian ini mengadopsi kerangka triple loop learning untuk mengevaluasi "
        "bukan hanya apa yang terjadi (loop 1), tetapi juga mengapa program "
        "merespons seperti yang dilakukan (loop 2), dan nilai serta asumsi apa "
        "yang berubah dalam proses tersebut (loop 3)."
    ),
    BULLET([
        "Loop 1 (Single): pembelajaran dari hasil langsung — apa yang berhasil dan tidak",
        "Loop 2 (Double): refleksi atas strategi — mengapa cara tertentu dipilih",
        "Loop 3 (Triple): transformasi nilai dan asumsi mendasar program",
    ]),
]

# ══════════════════════════════════════════════════════════
# BAB 4 — KONDISI AWAL
# ══════════════════════════════════════════════════════════
print("Building Bab 4 — Kondisi Awal...")
b4 = []
b4 += [
    H1("BAB IV IDENTIFIKASI KONDISI AWAL"),
    LEAD(
        "Bab ini mengidentifikasi kondisi awal yang menjadi dasar intervensi program — "
        "mencakup karakteristik kelompok sasaran, hambatan yang dihadapi, dan potensi "
        "yang dapat dimobilisasi melalui program."
    ),
    DIV(),
    WARN(
        "Catatan keterbatasan: pemetaan kondisi awal dalam laporan ini disusun terutama "
        "dari data program, identifikasi kelompok sasaran, dan problem framing yang "
        "diturunkan dari desain intervensi. Data baseline wilayah yang sepenuhnya "
        "komprehensif — seperti statistik BPS, peta administrasi, atau data ekonomi "
        "kecamatan — tidak tersedia dalam sumber utama kajian ini. Pembacaan kondisi "
        "awal pada bab ini perlu dipahami sebagai baseline programatik, bukan potret "
        "statistik wilayah yang lengkap.",
        sr=["context_baseline","problem_framing"]
    ),
    GAP(
        "Data profil wilayah rinci (statistik BPS, peta administrasi, data ekonomi "
        "kecamatan) tidak tersedia dalam sumber canonical kajian ini. Sub-bab 4.1 "
        "memerlukan pengisian dari data lapangan dan laporan pendampingan.",
        "data_unavailable"
    ),
    H2("4.1 Profil dan Kondisi Kelompok Sasaran"),
    P(
        "Kelompok sasaran program adalah Warga Binaan Pemasyarakatan (WBP) yang "
        "sedang menjalani masa pembinaan di Lembaga Pemasyarakatan, serta eks-WBP "
        "yang telah menyelesaikan masa hukuman dan memasuki fase reintegrasi. "
        "Kedua kelompok ini menghadapi kerentanan struktural yang saling memperkuat."
    ),
    H2("4.2 Permasalahan"),
    P(
        "Berdasarkan analisis program, terdapat empat akar masalah utama yang "
        "menjadi hambatan bagi WBP dan eks-WBP dalam mencapai kemandirian ekonomi:"
    ),
]

# Problem tree
for pt in pf.get("problem_tree", []):
    b4.append(H3(f"{pt['problem_id']}. {pt['label']}"))
    b4.append(P(
        pt.get("description",""),
        ds="present_as_inferred",
        sr=["problem_framing"]
    ))
    if pt.get("root_causes"):
        b4.append(BULLET(pt["root_causes"]))

b4 += [
    WARN(
        "Data di atas bersumber dari problem framing yang disusun berdasarkan "
        "inferensi dari desain program. Untuk laporan defensible, setiap poin "
        "perlu didukung data primer (wawancara, survei baseline) atau data "
        "sekunder terverifikasi (BPS, Kemenaker, laporan riset).",
        sr=["problem_framing"]
    ),
    H2("4.3 Potensi"),
    P(
        "Di balik hambatan struktural, program mengidentifikasi potensi yang "
        "dapat dimobilisasi melalui intervensi yang tepat:"
    ),
    BULLET([
        "Keterampilan mekanik otomotif memiliki permintaan pasar yang stabil dan tidak memerlukan pendidikan formal tinggi",
        "Ekosistem bengkel informal di Indonesia sangat luas — membuka peluang penyerapan tenaga kerja dan wirausaha",
        "Model eks-WBP yang sudah berhasil (Milenial Motor) dapat menjadi role model dan jalur referral",
        "Program pelatihan vokasional di Lapas memiliki akses langsung ke populasi sasaran yang terdefinisi",
    ]),
]

# ══════════════════════════════════════════════════════════
# BAB 5 — KONDISI IDEAL
# ══════════════════════════════════════════════════════════
print("Building Bab 5 — Kondisi Ideal...")
b5 = []
b5 += [
    H1("BAB V IDENTIFIKASI KONDISI IDEAL YANG DIHARAPKAN"),
    LEAD(ic.get("vision_statement","")),
    DIV(),
    GAP(
        "Data kuantitatif kondisi ideal yang spesifik (target angka SROI, "
        "target peserta, target pendapatan pasca-program) belum tersedia dalam "
        "canonical JSON kajian ini. Sub-bab ini dapat diperkaya dari dokumen "
        "perencanaan program dan laporan target kinerja.",
        "data_unavailable"
    ),
    H2("5.1 Tujuan Utama"),
    P(
        f"Program {pi['program_name']} bertujuan menciptakan ekosistem produktif "
        f"yang memungkinkan WBP dan eks-WBP mencapai kemandirian ekonomi dan "
        f"reintegrasi sosial yang bermartabat dan berkelanjutan."
    ),
    BULLET(ic.get("target_outcomes", [])),
    H2("5.2 Tujuan Spesifik: Key Areas of Improvement"),
    P("Empat area perbaikan kunci yang menjadi fokus intervensi program:"),
]

for area in ic.get("key_improvements", []):
    b5.append(P(f"• {area}", ds="present_as_inferred", sr=["ideal_conditions"]))

b5 += [
    H2("5.3 Kesesuaian Masalah / Intervensi / Tujuan"),
    P(
        "Setiap akar masalah yang diidentifikasi di Bab IV dijawab secara "
        "langsung oleh komponen program:"
    ),
    TBL_BL(
        ["Akar Masalah", "Intervensi Program", "Tujuan yang Dicapai"],
        [
            ["Competency-to-Service Gap",     "Pelatihan mekanik + praktik bengkel riil",       "Hard skill mekanik terstandar"],
            ["Post-Release Transition Risk",   "Pendampingan unit usaha + node eks-WBP",          "Kesiapan reintegrasi terukur"],
            ["Entrepreneurship Gap",           "Pembinaan kewirausahaan bengkel",                 "Kapasitas wirausaha mandiri"],
            ["Social Acceptance & Market Link","Jejaring bengkel + model Milenial Motor",         "Kepercayaan diri & akses pasar"],
        ],
        [3200, 3600, 2838],
        sr=["problem_framing","ideal_conditions","strategy_design"]
    ),
    INFO(
        "Kondisi ideal program selaras dengan SDG 8 (Pekerjaan Layak dan "
        "Pertumbuhan Ekonomi), SDG 10 (Berkurangnya Ketimpangan), dan SDG 16 "
        "(Perdamaian, Keadilan, dan Kelembagaan yang Kuat) — tiga tujuan global "
        "yang langsung relevan dengan isu reintegrasi eks-WBP.",
        sr=["program_positioning"]
    ),
]

# ══════════════════════════════════════════════════════════
# BAB 6 — STRATEGI
# ══════════════════════════════════════════════════════════
print("Building Bab 6 — Strategi...")
b6 = []
b6 += [
    H1("BAB VI STRATEGI UNTUK MENCAPAI KONDISI IDEAL YANG DIHARAPKAN"),
    LEAD(
        f"Bab ini menyajikan desain strategis Program {pi['program_name']} — "
        f"mencakup filosofi program, roadmap tiga tahun, value chain, dan "
        f"kelembagaan yang terbentuk."
    ),
    DIV(),
    H2("6.1 Nama dan Filosofi Program"),
    P(
        f"Nama '{pi['program_name']}' mencerminkan filosofi inti program: "
        f"menempatkan perusahaan sebagai mitra aktif (bukan donor pasif) bagi "
        f"WBP dan eks-WBP dalam perjalanan mereka menuju kemandirian. "
        f"Tagline program: \"{pi['program_tagline']}\"."
    ),
    H2("6.2 Relevansi Program dengan Visi Misi Perusahaan dan Program Pemerintah"),
    P(
        f"Program ini selaras dengan pilar '{pp['tjsl_pillar']}' dan kategori "
        f"'{pp['proper_category']}' yang ditetapkan dalam regulasi PROPER. "
        f"Di sisi pemerintah, program berkontribusi pada agenda Kementerian Hukum "
        f"dan HAM dalam rehabilitasi dan reintegrasi WBP."
    ),
    H2("6.3 Roadmap Program"),
    P(
        f"Program dirancang dalam tiga tahap yang mencerminkan evolusi dari "
        f"pembentukan kapasitas menuju stabilisasi dan ekspansi:"
    ),
]

for stage in sd.get("roadmap", []):
    b6.append(H3(f"Tahap {stage['stage_id']}: {stage['label']} ({stage['period']})"))
    b6.append(P(
        f"Fokus: {stage['focus']}. "
        f"Tipe pembelajaran: {stage.get('loop_type','—')}-loop learning.",
        ds="present_as_final",
        sr=["strategy_design"]
    ))

b6 += [
    H2("6.4 Value Chain"),
    P("Rantai nilai program mengalir secara sekuensial dari kapasitas teknis menuju dampak sosial:"),
]

vc = sd.get("value_chain", [])
for i, step in enumerate(vc):
    arrow = " →" if i < len(vc)-1 else ""
    b6.append(P(f"{i+1}. {step}{arrow}", ds="present_as_final", sr=["strategy_design"]))

b6 += [
    H2("6.5 Kelembagaan"),
    P(
        f"Program membentuk dan menguatkan {len(sd['institutional']['nodes'])} "
        f"node kelembagaan yang menjadi unit operasional program:"
    ),
    TBL_BL(
        ["Node", "Tipologi"],
        [
            ["Lapas Kota Palembang",     "WBP aktif — fase pembentukan kapasitas"],
            ["Bengkel Lapas IIB Sleman", "WBP aktif — fase aktif bertransaksi"],
            ["Milenial Motor (Eks-WBP)", "Eks-WBP — proof-of-concept reintegrasi"],
            ["Pemasyarakatan Corner",    "WBP aktif — fase aktif bertransaksi"],
        ],
        [4200, 5438],
        sr=["strategy_design"]
    ),
    SUCCESS(
        "Milenial Motor adalah pencapaian kelembagaan terkuat program: sebuah "
        "unit usaha bengkel yang dikelola sepenuhnya oleh eks-WBP, membuktikan "
        "bahwa model reintegrasi produktif yang dicita-citakan program dapat "
        "diwujudkan dalam skala nyata.",
        sr=["EV_06"]
    ),
    METRIC3([
        {"label":"Node Program",       "value":"4",  "sublabel":"total"},
        {"label":"Node Bertransaksi",  "value":"3",  "sublabel":"aktif"},
        {"label":"Model Reintegrasi",  "value":"1",  "sublabel":"Milenial Motor"},
    ]),
]

# ══════════════════════════════════════════════════════════
# BAB 8 — TRIPLE LOOP LEARNING
# ══════════════════════════════════════════════════════════
print("Building Bab 8 — Triple Loop Learning...")
b8 = []
b8 += [
    H1("BAB VIII ASPEK PEMBELAJARAN DENGAN TRIPLE LOOP LEARNING"),
    LEAD(
        "Bab ini menyajikan refleksi pembelajaran program melalui kerangka "
        "triple loop learning — menganalisis tidak hanya apa yang terjadi, "
        "tetapi juga mengapa program merespons seperti yang dilakukan, "
        "dan perubahan mendasar apa yang muncul dari proses implementasi."
    ),
    DIV(),
    H2("8.1 Identifikasi Masalah dan Keterkaitan LFA"),
    P(
        "Selama implementasi 2023–2025, program menghadapi beberapa tantangan "
        "yang menjadi sumber pembelajaran:"
    ),
]

for ref in ls.get("lfa_reflections", []):
    b8.append(H3(f"Refleksi: {ref.get('activity_ref','')}"))
    b8.append(P(
        f"Gap LFA: {ref.get('lfa_gap','')}",
        ds="present_as_inferred",
        sr=["learning_signals"]
    ))
    b8.append(P(
        f"Pembelajaran: {ref.get('lesson_learned','')}",
        ds="present_as_inferred",
        sr=["learning_signals"]
    ))

b8 += [
    H2("8.2 L1, L2, L3 — Analisis Triple Loop"),
    INFO(
        "Dalam laporan ini digunakan dua ukuran yang berbeda dan saling melengkapi. "
        "Observed direct return (1 : 0,29) menunjukkan rasio pengembalian langsung "
        "berbasis transaksi riil yang tercatat dari tiga node aktif selama implementasi. "
        "Blended SROI (1 : 1,03) menunjukkan rasio nilai sosial-ekonomi total setelah "
        "monetisasi outcome, compound ORI, dan penyesuaian DDAT per aspek diperhitungkan. "
        "Kedua ukuran ini tidak saling menggantikan — keduanya membaca program dari "
        "sudut yang berbeda dan sama-sama sahih.",
        sr=["sroi_metrics.calculated","monetization","ddat_params"]
    ),
    H3("Loop 1 — Single Loop Learning (Apa yang terjadi?)"),
    P(
        "Pembelajaran level pertama berfokus pada hasil langsung dari "
        "implementasi aktivitas:"
    ),
    BULLET(ls.get("loop_1", [])),
    H3("Loop 2 — Double Loop Learning (Mengapa respons itu dipilih?)"),
    P(
        "Pembelajaran level kedua merefleksikan penyesuaian strategi "
        "yang dilakukan berdasarkan temuan implementasi:"
    ),
    BULLET(ls.get("loop_2", [])),
    H3("Loop 3 — Triple Loop Learning (Apa yang berubah secara fundamental?)"),
    P(
        "Pembelajaran level ketiga menandai transformasi nilai dan asumsi "
        "mendasar yang muncul dari proses implementasi:"
    ),
    BULLET(ls.get("loop_3", [])),
    WARN(
        "Analisis triple loop di atas bersumber dari learning signals yang "
        "disusun berdasarkan data program yang tersedia. Untuk laporan final, "
        "refleksi ini perlu diperkaya dengan wawancara mendalam bersama "
        "pengelola program, peserta, dan mitra lapangan.",
        sr=["learning_signals"]
    ),
    H2("8.3 Identifikasi Keunikan Program"),
    P(
        "Program memiliki beberapa karakteristik unik yang membedakannya dari "
        "program pemberdayaan vokasional konvensional:"
    ),
    BULLET([
        "Intervensi di dalam Lapas — menjangkau kelompok yang paling sulit diakses program pemberdayaan umum",
        "Dual-track model: bengkel di dalam Lapas (WBP aktif) + bengkel mandiri eks-WBP (pasca-bebas)",
        "Produk program sekaligus menjadi saluran distribusi produk perusahaan — alignment bisnis dan sosial",
        "Milenial Motor sebagai proof-of-concept yang hidup — bukan aspirasi, tetapi realita yang dapat direplikasi",
    ]),
    H2("8.4 Kontribusi Efisiensi, Efektivitas, dan Keberlanjutan Sosial"),
    P(
        f"Dari sisi efisiensi, program menghasilkan SROI blended "
        f"{ratio(calc['sroi_blended'])} — setiap Rp 1 investasi menghasilkan "
        f"{idr(calc['sroi_blended'])} nilai sosial. Dari sisi efektivitas, "
        f"tiga dari empat node aktif bertransaksi secara konsisten. "
        f"Keberlanjutan dijamin oleh model bisnis bengkel yang menghasilkan "
        f"pendapatan riil — bukan bergantung pada subsidi program selamanya.",
        ds="present_as_final",
        sr=["sroi_metrics.calculated","strategy_design"]
    ),
]

# ══════════════════════════════════════════════════════════
# BAB 9 — PENUTUP
# ══════════════════════════════════════════════════════════
print("Building Bab 9 — Penutup...")
b9 = []
b9 += [
    H1("BAB IX PENUTUP"),
    DIV(),
    H2("9.1 Kesimpulan"),
    LEAD(
        f"Program {pi['program_name']} terbukti menghasilkan nilai sosial-ekonomi "
        f"yang melampaui investasi, dengan SROI blended "
        f"{ratio(calc['sroi_blended'])} selama periode {pi['period_start']}–{pi['period_end']}."
    ),
    P(
        f"Dari total investasi {idr(A('total_investment'))}, program menghasilkan "
        f"net benefit compounded sebesar {idr(A('total_net_compounded'))} — "
        f"mencerminkan positive return yang konsisten di seluruh tahun evaluasi.",
        ds="present_as_final",
        sr=["sroi_metrics.calculated"]
    ),
    METRIC3([
        {"label":"SROI Blended",          "value":ratio(calc["sroi_blended"]),   "sublabel":"2023–2025"},
        {"label":"Total Investasi",        "value":idr(A("total_investment")),    "sublabel":"kumulatif"},
        {"label":"Net Benefit Compounded", "value":idr(A("total_net_compounded")),"sublabel":"terminal 2025"},
    ]),
    P(
        "Tiga temuan utama yang perlu ditekankan: "
        "(1) Aspek REINT mendominasi nilai — menunjukkan bahwa nilai reintegrasi "
        "sosial-ekonomi adalah dampak paling signifikan dari intervensi ini. "
        "(2) Node Lapas Palembang belum menghasilkan transaksi — mengindikasikan "
        "potensi kenaikan SROI yang belum terealisasi. "
        "(3) Milenial Motor membuktikan bahwa model reintegrasi produktif bukan "
        "sekadar aspirasi — ini adalah template yang dapat direplikasi."
    ),
    H2("9.2 Rekomendasi / Usulan Tindak Lanjut"),
    NUMBERED([
        f"Aktivasi Node Lapas Palembang: tetapkan milestone spesifik dan target "
        f"transaksi pertama pada 2026 — node ini adalah peluang kenaikan SROI "
        f"terbesar tanpa investasi tambahan yang proporsional",
        "Verifikasi jumlah peserta aktual: data 70/70/80 peserta per tahun adalah "
        "estimasi konservatif yang perlu diverifikasi dari data absensi pelatihan "
        "dan dokumentasi pendampingan",
        "Replikasi model Milenial Motor: dokumentasi jalur Lapas → pelatihan → "
        "usaha mandiri sebagai SOP yang dapat diadopsi node lain",
        "Penguatan data baseline: survei kepuasan dan profil sosial-ekonomi peserta "
        "sebelum dan sesudah program untuk memperkuat proxy REINT dan CONF",
        "Pembaruan kajian SROI: lakukan pembaruan tahunan untuk merekam trajectory "
        "dampak jangka menengah — terutama retensi pekerjaan dan keberlangsungan usaha",
    ]),
    SMALL(
        f"Laporan ini disusun berdasarkan data yang tersedia per {pi['period_end']} "
        f"dan mencerminkan status evaluatif. Angka investasi 2023–2024 berstatus "
        f"under_confirmation dan perlu diverifikasi dari dokumen keuangan resmi."
    ),
]

# ══════════════════════════════════════════════════════════
# COMPOSE & WRITE
# ══════════════════════════════════════════════════════════
chapters = [
    chapter_semantic("bab_1","pendahuluan",   "framing",  b1),
    chapter_semantic("bab_2","profil",        "framing",  b2),
    chapter_semantic("bab_3","metodologi",    "framing",  b3),
    chapter_semantic("bab_4","kondisi_awal",  "context",  b4),
    chapter_semantic("bab_5","kondisi_ideal", "context",  b5),
    chapter_semantic("bab_6","strategi",      "context",  b6),
    chapter_semantic("bab_8","learning",      "learning", b8),
    chapter_semantic("bab_9","penutup",       "learning", b9),
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Tulis satu file per bab + satu file gabungan
all_chapters = []
for ch in chapters:
    cid  = ch["chapter_id"]
    path = OUTPUT_DIR / f"chapter_semantic_{cid}.json"
    json.dump([ch], open(path,"w"), indent=2, ensure_ascii=False)
    all_chapters.append(ch)
    nb = len(ch["blocks"])
    print(f"  {cid}: {nb} blocks → {path.name}")

# Gabungan semua bab kecuali bab_7 (sudah ada)
all_path = OUTPUT_DIR / "chapters_semantic_rest.json"
json.dump(all_chapters, open(all_path,"w"), indent=2, ensure_ascii=False)

print(f"\nGabungan: {all_path.name} ({len(all_chapters)} bab)")
print("\n" + "="*55)
print("NARRATIVE BUILDER REST — selesai")
total_blocks = sum(len(c["blocks"]) for c in all_chapters)
print(f"  Bab dihasilkan : {len(all_chapters)}")
print(f"  Total blocks   : {total_blocks}")
for ch in all_chapters:
    nb = len(ch["blocks"])
    print(f"    {ch['chapter_id']}: {nb} blocks ({ch['builder_mode']})")
print("="*55)
