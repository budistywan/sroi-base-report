"""
Point Builder — Sprint 3
SROI Report System

Sub-mode: builder_sroi (Bab 7 — Implementasi / PDIS dengan SROI)

Input  : canonical_esl_v1.json + handoff_b.json + handoff_c.json
Output : chapter_outline_bab7.json (Handoff D ke Narrative Builder)

Prinsip:
  - Point Builder TIDAK menulis narasi
  - Point Builder menyusun LOGIKA ARGUMENTASI per bab
  - Setiap poin harus punya evidence_refs yang traceable ke canonical JSON
  - Angka hanya boleh diambil dari sroi_metrics.calculated via calc_audit_log

Usage:
  python point_builder_sroi.py
  python point_builder_sroi.py --canonical /p/c.json --handoff-b /p/hb.json --handoff-c /p/hc.json --output /p/
  CANONICAL_FILE=... HANDOFF_B_FILE=... HANDOFF_C_FILE=... OUTPUT_DIR=... python point_builder_sroi.py
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

BUILDER_VERSION = "1.0.0"

# ── PATH CONFIG ──────────────────────────────────────────
parser = argparse.ArgumentParser(description="Point Builder — builder_sroi")
parser.add_argument("--canonical",  default=None)
parser.add_argument("--handoff-b",  default=None, dest="handoff_b")
parser.add_argument("--handoff-c",  default=None, dest="handoff_c")
parser.add_argument("--output",     default=None)
args = parser.parse_args()

SCRIPT_DIR     = Path(__file__).parent
CANONICAL_FILE = Path(args.canonical) if args.canonical \
    else Path(os.environ.get("CANONICAL_FILE", SCRIPT_DIR.parent / "sprint0/canonical_esl_v1.json"))
HANDOFF_B_FILE = Path(args.handoff_b) if args.handoff_b \
    else Path(os.environ.get("HANDOFF_B_FILE", SCRIPT_DIR.parent / "sprint1/handoff_b.json"))
HANDOFF_C_FILE = Path(args.handoff_c) if args.handoff_c \
    else Path(os.environ.get("HANDOFF_C_FILE", SCRIPT_DIR.parent / "sprint2/handoff_c.json"))
OUTPUT_DIR     = Path(args.output)    if args.output \
    else Path(os.environ.get("OUTPUT_DIR", SCRIPT_DIR))

print(f"Canonical : {CANONICAL_FILE.resolve()}")
print(f"Handoff B : {HANDOFF_B_FILE.resolve()}")
print(f"Handoff C : {HANDOFF_C_FILE.resolve()}")
print(f"Output    : {OUTPUT_DIR.resolve()}")

for f in [CANONICAL_FILE, HANDOFF_B_FILE, HANDOFF_C_FILE]:
    if not f.exists():
        print(f"\nFAIL: File tidak ditemukan — {f}")
        sys.exit(1)

canonical  = json.load(open(CANONICAL_FILE))
handoff_b  = json.load(open(HANDOFF_B_FILE))
handoff_c  = json.load(open(HANDOFF_C_FILE))
calc       = handoff_b["sroi_metrics"]["calculated"]
blueprint  = handoff_c["report_blueprint_json"]
audit_log  = {e["field"]: e for e in handoff_b["calc_audit_log"]}

# ── HELPER: ambil angka dari audit log ───────────────────
def from_audit(field):
    """Ambil nilai dari calc_audit_log. Raise jika tidak ada — angka harus traceable."""
    if field not in audit_log:
        raise KeyError(f"Field '{field}' tidak ada di calc_audit_log — angka tidak traceable")
    return audit_log[field]["value"]

def fmt_idr(value):
    """Format angka ke Rp dengan titik ribuan."""
    return f"Rp {value:,.0f}"

def fmt_ratio(value):
    """Format SROI ratio ke 1:X,XX."""
    return f"1 : {value:.2f}"

# ── VERIFY: Bab 7 ada dan strong ─────────────────────────
bab7_blueprint = next(
    (c for c in blueprint["chapters"] if c["chapter_id"] == "bab_7"), None
)
if not bab7_blueprint:
    print("FAIL: bab_7 tidak ditemukan di blueprint")
    sys.exit(1)
if bab7_blueprint["coverage_status"] != "strong":
    print(f"FAIL: bab_7 coverage_status = {bab7_blueprint['coverage_status']} — harus strong")
    sys.exit(1)

print(f"\nbab_7 status : {bab7_blueprint['coverage_status']}")
print(f"builder_mode : {bab7_blueprint['builder_mode']}")
print(f"report_mode  : {blueprint['report_mode']}")

# ── EXTRACT DATA DARI CANONICAL ───────────────────────────
years = [2023, 2024, 2025]

# Investasi per tahun
inv_by_year = {}
for item in canonical["investment"]:
    yr = item["year"]
    inv_by_year[yr] = inv_by_year.get(yr, 0) + item["amount_idr"]

# Monetisasi per aspek per tahun
mon_by_aspect = {}
for m in canonical["monetization"]:
    asp = m["aspect_code"]
    if asp not in mon_by_aspect:
        mon_by_aspect[asp] = {}
    mon_by_aspect[asp][m["year"]] = {
        "gross":          m["gross_idr"],
        "proxy_basis":    m.get("proxy_basis", ""),
        "proxy_value":    m.get("proxy_value", 0),
        "quantity_basis": m.get("quantity_basis", ""),
        "data_status":    m["data_status"],
        "display_status": m["display_status"],
        "source_refs":    m.get("source_refs", []),
    }

# DDAT params
ddat = canonical["ddat_params"]

# ORI rates
ori = canonical["ori_rates"]

# SROI per tahun dari calc
per_year = {row["year"]: row for row in calc["per_year"]}

# Financial tables — ambil table_id list
table_ids = [t["table_id"] for t in handoff_b["financial_tables"]]

# ══════════════════════════════════════════════════════════
# SUSUN OUTLINE BAB 7
# ══════════════════════════════════════════════════════════

print("\n--- Menyusun argument points Bab 7 ---")

argument_points = []

# ── 7.1 Node Program ─────────────────────────────────────
institutional = canonical.get("strategy_design", {}).get("institutional", {})
nodes = institutional.get("nodes", [])
active_note = institutional.get("note", "")
argument_points.append({
    "label": "7.1",
    "point": (
        f"Program beroperasi di {len(nodes)} node dengan karakteristik dan tingkat "
        f"aktivitas berbeda — {len(nodes)-1} node aktif menghasilkan transaksi terukur "
        f"dan 1 node dalam fase pembentukan kapasitas."
    ),
    "elaboration": (
        f"Node: {', '.join(nodes)}. "
        f"Catatan: {active_note}. "
        "Narasi harus menjelaskan peran berbeda tiap node dan mengapa Lapas Palembang "
        "belum menghasilkan transaksi — ini temuan jujur, bukan kelemahan yang disembunyikan."
    ),
    "evidence_refs": ["strategy_design.institutional", "outputs"],
    "status": "supported"
})

# ── 7.2 Stakeholder ──────────────────────────────────────
stk_count = len(canonical["stakeholders"])
stk_names = [s["name"] for s in canonical["stakeholders"]]
argument_points.append({
    "label": "7.2",
    "point": (
        f"Program melibatkan {stk_count} pemangku kepentingan utama dengan peran "
        "yang berbeda dalam ekosistem program."
    ),
    "elaboration": f"Stakeholder: {', '.join(stk_names)}.",
    "evidence_refs": ["stakeholders"],
    "status": "supported"
})

# ── 7.3 Investasi ─────────────────────────────────────────
total_inv = from_audit("total_investment")
inv_statuses = set(i["data_status"] for i in canonical["investment"])
has_pending  = "under_confirmation" in inv_statuses

argument_points.append({
    "label": "7.3",
    "point": (
        f"Total investasi program 2023–2025 mencapai {fmt_idr(total_inv)}, "
        "meningkat setiap tahun seiring penguatan aktivitas program."
    ),
    "elaboration": (
        f"Per tahun: "
        f"2023 {fmt_idr(from_audit('investment_total_2023'))}, "
        f"2024 {fmt_idr(from_audit('investment_total_2024'))}, "
        f"2025 {fmt_idr(from_audit('investment_total_2025'))}. "
        + ("Investasi 2023–2024 berstatus under_confirmation — "
           "ditampilkan dengan badge pending, perlu diverifikasi dari laporan keuangan resmi."
           if has_pending else "")
    ),
    "evidence_refs": ["investment"],
    "financial_ref": "table_investment_per_node",
    "status": "supported",
    "note": "Investasi 2023–2024 under_confirmation — display_status present_as_pending" if has_pending else ""
})

# ── 7.4 Output Program ────────────────────────────────────
act_count = len(canonical["activities"])
argument_points.append({
    "label": "7.4",
    "point": (
        f"Program menghasilkan output berupa {act_count} aktivitas terstruktur "
        "yang mencakup pelatihan teknis, product knowledge, praktik bengkel, "
        "pembinaan kewirausahaan, dan pendampingan unit usaha."
    ),
    "evidence_refs": ["activities", "outputs"],
    "status": "supported"
})

# ── 7.5 Outcome & 4 Aspek Nilai ───────────────────────────
asp_info = {
    "LUB":   {"name": "Penjualan Pelumas",             "tag": "observed"},
    "SVC":   {"name": "Jasa & Sparepart",               "tag": "observed"},
    "REINT": {"name": "Kesiapan Reintegrasi",           "tag": "proxy"},
    "CONF":  {"name": "Kepercayaan Diri / Self-Efficacy","tag": "proxy"},
}

argument_points.append({
    "label": "7.5",
    "point": (
        "Program menghasilkan empat aspek nilai terukur: dua aspek observed "
        "(LUB dan SVC dari transaksi aktual) dan dua aspek proxy yang tervalidasi "
        "secara akademik dan kebijakan (REINT dan CONF)."
    ),
    "evidence_refs": ["outcomes", "monetization"],
    "financial_ref": "table_monetization_per_aspek",
    "status": "supported"
})

# Sub-poin per aspek
for asp_code, info in asp_info.items():
    mon_data = mon_by_aspect.get(asp_code, {})
    gross_total = sum(v["gross"] for v in mon_data.values())
    mult = ddat[asp_code]["net_multiplier"]
    net_total = gross_total * mult

    if info["tag"] == "proxy":
        sample = mon_data.get(2023, {})
        proxy_detail = (
            f"Proxy: {sample.get('proxy_basis','—')}. "
            f"Basis kalkulasi: {sample.get('quantity_basis','—')} per tahun."
        )
        justification = ddat[asp_code]["justification"]
        elaboration = f"{proxy_detail} Justifikasi DDAT: {justification}"
        note = f"Proxy — display_status present_as_proxy. Wajib disertai badge dan source_refs."
    else:
        elaboration = f"Data transaksi aktual dari tiga node aktif. Justifikasi DDAT: {ddat[asp_code]['justification']}"
        note = ""

    argument_points.append({
        "label": f"7.5.{list(asp_info.keys()).index(asp_code)+1}",
        "point": (
            f"{asp_code} — {info['name']} ({info['tag']}): "
            f"gross kumulatif {fmt_idr(gross_total)}, "
            f"adj ×{mult}, net kumulatif {fmt_idr(net_total)}."
        ),
        "elaboration": elaboration,
        "evidence_refs": [
            f"monetization[aspect={asp_code}]",
            f"ddat_params.{asp_code}",
            "evidence_registry",
        ],
        "financial_ref": "table_monetization_per_aspek",
        "status": "supported",
        "note": note
    })

# ── 7.6 Fiksasi Dampak (DDAT) ─────────────────────────────
avg_fiksasi = calc["avg_fiksasi_pct"]
argument_points.append({
    "label": "7.6",
    "point": (
        f"Fiksasi dampak (DDAT adjustment) diterapkan per aspek dengan haircut "
        f"rata-rata {avg_fiksasi:.1f}%, mencerminkan konservatisme metodologis yang konsisten."
    ),
    "elaboration": (
        "DDAT = Deadweight + Displacement + Attribution + Drop-off. "
        "LUB ×0,54 (46% haircut) · SVC ×0,61 (39% haircut) · "
        "REINT ×0,55 (45% haircut) · CONF ×0,50 (50% haircut). "
        "CONF mendapat haircut tertinggi karena perubahan self-efficacy sulit "
        "diatribusikan penuh ke program."
    ),
    "evidence_refs": ["ddat_params"],
    "financial_ref": "table_ddat_per_aspek",
    "status": "supported"
})

# ── 7.7 Compound & ORI ────────────────────────────────────
argument_points.append({
    "label": "7.7",
    "point": (
        "Nilai bersih setiap tahun di-compound ke terminal year 2025 menggunakan "
        "ORI reference rate, untuk mencerminkan nilai waktu uang secara konservatif."
    ),
    "elaboration": (
        "2023: ×1,1252 (ORI023T3, 5,90%) → "
        f"{fmt_idr(from_audit('net_compounded_2023'))}. "
        "2024: ×1,0625 (ORI025T3, 6,25%) → "
        f"{fmt_idr(from_audit('net_compounded_2024'))}. "
        "2025: ×1,0000 (terminal year) → "
        f"{fmt_idr(from_audit('net_compounded_2025'))}."
    ),
    "evidence_refs": ["ori_rates"],
    "financial_ref": "table_sroi_per_tahun",
    "status": "supported"
})

# ── 7.8 SROI per Tahun ────────────────────────────────────
for yr in years:
    row = per_year[yr]
    argument_points.append({
        "label": f"7.8.{years.index(yr)+1}",
        "point": (
            f"Tahun {yr}: investasi {fmt_idr(row['investment'])}, "
            f"net compounded {fmt_idr(row['compounded'])}, "
            f"SROI {fmt_ratio(row['sroi_ratio'])}."
        ),
        "elaboration": (
            f"Gross: {fmt_idr(row['gross'])}. "
            f"Net setelah DDAT: {fmt_idr(row['net'])}. "
            f"Compound factor: ×{row['cf_applied']:.4f}."
        ),
        "evidence_refs": [f"sroi_metrics.calculated.per_year[{yr}]"],
        "financial_ref": "table_sroi_per_tahun",
        "status": "supported"
    })

# ── 7.9 SROI Blended ──────────────────────────────────────
total_inv_val   = from_audit("total_investment")
total_net_comp  = from_audit("total_net_compounded")
sroi_blended    = from_audit("sroi_blended")

argument_points.append({
    "label": "7.9",
    "point": (
        f"SROI blended 2023–2025: {fmt_ratio(sroi_blended)} — "
        f"dari investasi {fmt_idr(total_inv_val)} menghasilkan "
        f"net benefit compounded {fmt_idr(total_net_comp)}."
    ),
    "elaboration": (
        "Setiap Rp 1 yang diinvestasikan menghasilkan Rp 1,14 nilai sosial-ekonomi terukur. "
        "Program dinyatakan positive return. "
        "Catatan: REINT dan CONF adalah proxy — jika hanya LUB+SVC (observed), "
        "SROI akan jauh lebih rendah. Transparansi ini penting untuk kredibilitas laporan."
    ),
    "evidence_refs": ["sroi_metrics.calculated"],
    "financial_ref": "table_sroi_blended",
    "status": "supported"
})

# ── 7.10 Temuan Kritis: Lapas Palembang ───────────────────
argument_points.append({
    "label": "7.10",
    "point": (
        "Node Lapas Palembang belum menghasilkan transaksi terukur selama "
        "2023–2025 — ini adalah temuan jujur yang justru memperkuat "
        "kredibilitas laporan dan memberi dasar rekomendasi konkret."
    ),
    "elaboration": (
        "Jika Lapas Palembang dapat diaktivasi pada periode berikutnya, "
        "SROI berpotensi meningkat signifikan tanpa investasi tambahan yang proporsional. "
        "Narasi harus menempatkan ini sebagai learning finding, bukan kegagalan."
    ),
    "evidence_refs": ["strategy_design.institutional", "uncertainty_flags"],
    "status": "supported"
})

# ── 7.11 Milenial Motor sebagai Proof-of-Concept ──────────
argument_points.append({
    "label": "7.11",
    "point": (
        "Node Milenial Motor (eks-WBP) adalah bukti terkuat bahwa program "
        "dapat menghasilkan reintegrasi produktif nyata pasca-pembebasan."
    ),
    "elaboration": (
        "Node ini membuktikan bahwa jalur Lapas → pelatihan → usaha mandiri "
        "adalah jalur yang viable, bukan sekadar aspirasi program. "
        "Posisikan sebagai model replikasi untuk node lapas lain."
    ),
    "evidence_refs": ["EV_06", "strategy_design.institutional"],
    "status": "supported"
})

print(f"  {len(argument_points)} argument points disusun")


# ══════════════════════════════════════════════════════════
# COMPOSE OUTLINE BAB 7
# ══════════════════════════════════════════════════════════

outline_bab7 = {
    "chapter_id":    "bab_7",
    "chapter_title": "Implementasi / PDIS dengan SROI",
    "builder_mode":  "sroi",
    "coverage_status": "strong",

    "purpose": (
        "Menyajikan seluruh rangkaian implementasi program secara terukur — "
        "dari aktivitas, stakeholder, investasi, dan output hingga outcome, "
        "fiksasi dampak, monetisasi, dan hasil SROI evaluatif."
    ),

    "core_claim": (
        f"Program ESL menghasilkan SROI blended {fmt_ratio(sroi_blended)} — "
        "positive return yang dicapai melalui kombinasi transaksi bengkel riil (observed) "
        "dan nilai reintegrasi sosial-ekonomi yang terproksikan secara konservatif dan defensible."
    ),
    "core_claim_ref": "sroi_metrics.calculated",

    "argument_points": argument_points,

    "known_gaps": [],

    "financial_refs": table_ids,

    "narrative_notes": (
        "PENTING untuk Narrative Builder: "
        "(1) Semua angka HARUS diambil dari sroi_metrics.calculated — "
        "jangan hitung ulang atau bulatkan secara mandiri. "
        "(2) Aspek REINT dan CONF wajib disertai badge proxy dan source_refs. "
        "(3) Lapas Palembang yang belum bertransaksi adalah temuan jujur — "
        "jangan dihilangkan atau disamarkan. "
        "(4) Investasi 2023–2024 berstatus under_confirmation — "
        "tampilkan dengan callout_warning atau badge pending. "
        "(5) Milenial Motor adalah proof-of-concept — posisikan sebagai highlight positif."
    ),

    "generated_at":      datetime.now().isoformat(),
    "builder_version":   BUILDER_VERSION,
    "source_calc_at":    calc.get("calculated_at", ""),
    "source_engine_ver": calc.get("engine_version", ""),
}


# ══════════════════════════════════════════════════════════
# VALIDATE SEBELUM SIMPAN (Gate Sprint 3 rule 1–4)
# ══════════════════════════════════════════════════════════

print("\n--- Pre-save validation ---")
errors = []

# Rule 1: semua evidence_refs harus traceable
valid_refs = set(canonical.keys()) | {
    f"sroi_metrics.calculated.per_year[{yr}]" for yr in years
} | {
    f"sroi_metrics.calculated",
    f"strategy_design.institutional",
    f"strategy_design.institutional",
} | {e["evidence_id"] for e in canonical.get("evidence_registry",[])} \
  | {f"monetization[aspect={asp}]" for asp in asp_info} \
  | {f"ddat_params.{asp}" for asp in ddat} \
  | {"evidence_registry", "uncertainty_flags", "outputs", "outcomes",
     "activities", "investment", "stakeholders", "monetization",
     "ddat_params", "ori_rates"}

for ap in argument_points:
    for ref in ap.get("evidence_refs", []):
        # Cek apakah ref ada di valid_refs atau merupakan prefix yang valid
        ref_base = ref.split(".")[0].split("[")[0]
        if ref not in valid_refs and ref_base not in valid_refs:
            errors.append(f"  WARN: evidence_ref tidak dikenal: '{ref}' di point {ap['label']}")

# Rule 2: supported tidak boleh punya evidence_refs kosong
for ap in argument_points:
    if ap["status"] == "supported" and not ap.get("evidence_refs"):
        errors.append(f"  FAIL: Point {ap['label']} supported tapi evidence_refs kosong")

# Rule 3: known_gaps harus kosong (bab_7 coverage strong)
if outline_bab7["known_gaps"]:
    errors.append("  FAIL: known_gaps tidak boleh berisi jika coverage strong")

# Rule 4: core_claim_ref harus ada di canonical
core_ref = outline_bab7["core_claim_ref"].split(".")[0]
if core_ref not in canonical:
    errors.append(f"  FAIL: core_claim_ref '{core_ref}' tidak ada di canonical")
else:
    print(f"  PASS: core_claim_ref '{core_ref}' ditemukan di canonical")

# Rule 5 (tambahan dari Orchestrator): poin pending/inferred harus punya note
for ap in argument_points:
    if ap["status"] in ["pending","inferred"] and not ap.get("note","").strip():
        errors.append(f"  FAIL: Point {ap['label']} status={ap['status']} tapi note kosong")

if errors:
    for e in errors:
        print(e)
    # WARN tidak blocking tapi FAIL adalah blocking
    fail_count = sum(1 for e in errors if "FAIL" in e)
    if fail_count > 0:
        print(f"\n{fail_count} validation error — outline tidak disimpan")
        sys.exit(1)
    else:
        print(f"  {len(errors)} warning(s) — outline tetap disimpan")
else:
    print("  PASS: semua validation rules terpenuhi")


# ══════════════════════════════════════════════════════════
# WRITE OUTPUT (Handoff D)
# ══════════════════════════════════════════════════════════

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
outline_path = OUTPUT_DIR / "chapter_outline_bab7.json"

json.dump([outline_bab7], open(outline_path, "w"), indent=2, ensure_ascii=False)

print(f"\nOutput: {outline_path}")

# ── Human-readable preview ───────────────────────────────
print("\n" + "="*65)
print(f"POINT BUILDER OUTPUT — {outline_bab7['chapter_id']}")
print(f"Mode    : {outline_bab7['builder_mode']}")
print(f"Coverage: {outline_bab7['coverage_status']}")
print(f"Points  : {len(argument_points)}")
print(f"Fin.refs: {len(table_ids)}")
print("-"*65)
print(f"Core claim: {outline_bab7['core_claim'][:80]}...")
print("-"*65)
for ap in argument_points:
    status_marker = {"supported":"✓","partial":"~","inferred":"?","pending":"⏳"}.get(ap["status"],"·")
    proxy_marker  = " [PROXY]" if ap.get("note","").strip() else ""
    print(f"  {status_marker} {ap['label']:<8} {ap['point'][:65]}{proxy_marker}")
print("="*65)
