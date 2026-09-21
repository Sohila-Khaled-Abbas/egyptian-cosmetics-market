# Playbook 06: Reference-Driven Mapping & Standardization

## 1. Objective & Scope

A hallmark of amateur Power Query code is the proliferation of deep, repetitive nested `if ... then ... else` expressions scattered across multiple queries to map aliases, currencies, and statuses. 

This playbook details:
1. Creating 5 centralized **Reference Mapping Queries** in group **`03_Reference`** (`ref_currency_mapping`, `ref_status_mapping`, `ref_governorate_mapping`, `ref_channel_mapping`, `ref_payment_mapping`).
2. Why reference-driven architecture is superior to hardcoded conditional logic.
3. How to perform high-speed lookups and merges in Power Query using buffered record and table lookups.

All queries in `03_Reference` have **`Enable Load = False`**.

---

## 2. Advantages of Reference-Driven Mapping Over Nested IFs

| Criterion | Nested `if` Statements | Reference-Driven Mapping Table |
| :--- | :--- | :--- |
| **Maintainability** | Terrible. Adding a new alias (e.g., `"EGP."`) requires modifying M expressions across multiple queries. | Exceptional. Add a new row to the mapping table; all dependent downstream queries immediately inherit the update. |
| **Auditability** | Poor. Business stakeholders cannot easily review embedded procedural code. | Transparent. Mapping tables can be reviewed directly by business users or synchronized from master data. |
| **Performance** | Degrading. Deep nested conditionals are evaluated interpretively row-by-row on every column evaluation. | High. Power Query optimizes dictionary-based record lookups and hash joins against buffered reference tables. |
| **Code Redundancy**| High. The exact same status or currency logic is duplicated across Orders, Products, and Financial queries. | Zero. Single source of truth. |

---

## 3. Step-by-Step Implementation of Reference Tables

All queries below are created in Power Query Editor via **Home** $\rightarrow$ **New Source** $\rightarrow$ **Blank Query** $\rightarrow$ **Advanced Editor**, and stored in group **`03_Reference`**.

### 3.1: `ref_currency_mapping`
Standardizes all Egyptian currency variants to standard ISO code `"EGP"`, and documents exchange rate anchors.

```powerquery
let
    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WctQ11DU01DWwMjC0MjVUitWJVnLTNTIGcozgHCc9Y2MwxxjIdgSyLYGsWAA=", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [RawCurrency = _t, NormalizedCurrency = _t, CurrencyName_EN = _t, CurrencyName_AR = _t]),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawCurrency", type text},
        {"NormalizedCurrency", type text},
        {"CurrencyName_EN", type text},
        {"CurrencyName_AR", type text}
    })
in
    Typed
```
*Equivalent Table Contents:*
- `"EGP"` $\rightarrow$ `"EGP"` (`Egyptian Pound`, `جنيه مصري`)
- `"EGP "` $\rightarrow$ `"EGP"` (`Egyptian Pound`, `جنيه مصري`)
- `"جنيه"` $\rightarrow$ `"EGP"` (`Egyptian Pound`, `جنيه مصري`)
- `"جنيه مصري"` $\rightarrow$ `"EGP"` (`Egyptian Pound`, `جنيه مصري`)
- `"USD"` $\rightarrow$ `"USD"` (`US Dollar`, `دولار أمريكي`)
- `"EUR"` $\rightarrow$ `"EUR"` (`Euro`, `يورو`)

---

### 3.2: `ref_status_mapping`
Maps order status casing and linguistic variations to canonical business states.

```powerquery
let
    Source = Table.FromRows({
        {"Completed", "Completed", "مكتمل", true},
        {"completed", "Completed", "مكتمل", true},
        {"Complete",  "Completed", "مكتمل", true},
        {"Pending",   "Pending",   "قيد التنفيذ", false},
        {"Cancelled", "Cancelled", "ملغي", false},
        {"Returned",  "Returned",  "مرتجع", false}
    }, {"RawStatus", "NormalizedStatus", "Status_AR", "IsRevenueRecognized"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawStatus", type text},
        {"NormalizedStatus", type text},
        {"Status_AR", type text},
        {"IsRevenueRecognized", type logical}
    })
in
    Typed
```
*Business Value:* Explicitly defines `IsRevenueRecognized` flag, separating orders that generate recognized net revenue (`Completed`) from non-recognized states (`Cancelled`, `Returned`, `Pending`).

---

### 3.3: `ref_governorate_mapping`
Standardizes the 22 Egyptian governorates, maps them to official Egyptian economic regions (Cairo, Delta, Canal, Upper Egypt), and provides official Arabic names.

```powerquery
let
    Source = Table.FromRows({
        {"Cairo", "Cairo", "القاهرة", "Cairo Region", "Cairo Hub"},
        {"cairo", "Cairo", "القاهرة", "Cairo Region", "Cairo Hub"},
        {"Giza", "Giza", "الجيزة", "Cairo Region", "Delta Hub"},
        {"giza", "Giza", "الجيزة", "Cairo Region", "Delta Hub"},
        {"Alexandria", "Alexandria", "الإسكندرية", "Alexandria Region", "Delta Hub"},
        {"Dakahlia", "Dakahlia", "الدقهلية", "Delta Region", "Canal Hub"},
        {"Gharbia", "Gharbia", "الغربية", "Delta Region", "Cairo Hub"},
        {"Sharqia", "Sharqia", "الشرقية", "Delta Region", "Cairo Hub"},
        {"Qalyubia", "Qalyubia", "القليوبية", "Cairo Region", "Upper Egypt Hub"},
        {"Damietta", "Damietta", "دمياط", "Delta Region", "Canal Hub"},
        {"Beheira", "Beheira", "البحيرة", "Delta Region", "Delta Hub"},
        {"Ismailia", "Ismailia", "الإسماعيلية", "Canal Region", "Canal Hub"},
        {"Suez", "Suez", "السويس", "Canal Region", "Canal Hub"},
        {"Port Said", "Port Said", "بورسعيد", "Canal Region", "Canal Hub"},
        {"Fayoum", "Fayoum", "الفيوم", "Northern Upper Egypt", "Upper Egypt Hub"},
        {"Minya", "Minya", "المنيا", "Northern Upper Egypt", "Upper Egypt Hub"},
        {"Assiut", "Assiut", "أسيوط", "Central Upper Egypt", "Upper Egypt Hub"},
        {"Sohag", "Sohag", "سوهاج", "Southern Upper Egypt", "Upper Egypt Hub"},
        {"sohag", "Sohag", "سوهاج", "Southern Upper Egypt", "Upper Egypt Hub"},
        {"Qena", "Qena", "قنا", "Southern Upper Egypt", "Upper Egypt Hub"},
        {"Luxor", "Luxor", "الأقصر", "Southern Upper Egypt", "Upper Egypt Hub"},
        {"Aswan", "Aswan", "أسوان", "Southern Upper Egypt", "Upper Egypt Hub"},
        {"Red Sea", "Red Sea", "البحر الأحمر", "Frontier Region", "Upper Egypt Hub"},
        {"North Sinai", "North Sinai", "شمال سيناء", "Frontier Region", "Canal Hub"},
        {"South Sinai", "South Sinai", "جنوب سيناء", "Frontier Region", "Delta Hub"}
    }, {"RawGovernorate", "NormalizedGovernorate", "Governorate_AR", "EconomicRegion", "DefaultHub"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawGovernorate", type text},
        {"NormalizedGovernorate", type text},
        {"Governorate_AR", type text},
        {"EconomicRegion", type text},
        {"DefaultHub", type text}
    })
in
    Typed
```

---

### 3.4: `ref_channel_mapping`
Maps retail and digital touchpoints to high-level Channel Groups (Digital Direct, Marketplace, Physical Retail).

```powerquery
let
    Source = Table.FromRows({
        {"Website", "Website", "الموقع الإلكتروني", "Digital Direct"},
        {"Instagram", "Instagram", "إنستجرام", "Social Commerce"},
        {"Facebook", "Facebook", "فيسبوك", "Social Commerce"},
        {"TikTok", "TikTok", "تيك توك", "Social Commerce"},
        {"Jumia", "Jumia", "جوميا", "Marketplace"},
        {"Amazon Egypt", "Amazon Egypt", "أمازون مصر", "Marketplace"},
        {"Noon", "Noon", "نون", "Marketplace"},
        {"Retail Store", "Retail Store", "فرع", "Physical Retail"},
        {"Pharmacy", "Pharmacy", "صيدلية", "Physical Retail"},
        {"Marketplace", "Marketplace", "ماركت بليس", "Marketplace"}
    }, {"RawChannel", "NormalizedChannel", "Channel_AR", "ChannelGroup"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawChannel", type text},
        {"NormalizedChannel", type text},
        {"Channel_AR", type text},
        {"ChannelGroup", type text}
    })
in
    Typed
```

---

### 3.5: `ref_payment_mapping`
Maps payment methods to payment categories (Digital Fintech, Card, Cash).

```powerquery
let
    Source = Table.FromRows({
        {"Cash on Delivery", "Cash on Delivery", "الدفع عند الاستلام", "Cash", false},
        {"Vodafone Cash", "Vodafone Cash", "فودافون كاش", "Mobile Wallet", true},
        {"InstaPay", "InstaPay", "إنستاباي", "Instant Banking", true},
        {"Credit Card", "Credit Card", "بطاقة ائتمان", "Card", true},
        {"Debit Card", "Debit Card", "بطاقة خصم", "Card", true},
        {"Meeza", "Meeza", "ميزة", "National Card", true}
    }, {"RawPayment", "NormalizedPayment", "Payment_AR", "PaymentCategory", "IsDigitalPayment"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawPayment", type text},
        {"NormalizedPayment", type text},
        {"Payment_AR", type text},
        {"PaymentCategory", type text},
        {"IsDigitalPayment", type logical}
    })
in
    Typed
```

---

## 4. How to Consume Reference Tables via Merges

Rather than hardcoded conditionals, downstream queries join these tables using `Table.NestedJoin`:

```powerquery
// Example: Merging ref_status_mapping into cln_orders
MergedStatus = Table.NestedJoin(
    Source, {"order_status"}, 
    ref_status_mapping, {"RawStatus"}, 
    "StatusRef", 
    JoinKind.LeftOuter
),
ExpandedStatus = Table.ExpandTableColumn(
    MergedStatus, 
    "StatusRef", 
    {"NormalizedStatus", "Status_AR", "IsRevenueRecognized"}, 
    {"order_status_clean", "order_status_ar", "is_revenue_recognized"}
)
```

---

## 5. Summary & Best Practices

1. All reference mapping tables are decoupled and centralized in `03_Reference`.
2. Any new commercial promotion, regional boundary shift, or payment gateway (e.g. Telda, Orange Money) is configured simply by inserting one row in the reference table.
3. Every mapping table carries both Arabic and English designations, directly supporting the bilingual reporting requirement.
