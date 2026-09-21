// ==============================================================================
// GROUP: 03_Reference
// Purpose: Lookup tables for declarative standardization and translation
// Load Setting: Enable Load = FALSE for all queries in this group
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY: ref_currency_mapping
// ------------------------------------------------------------------------------
let
    Source = Table.FromRows({
        {"EGP", "EGP", "Egyptian Pound", "جنيه مصري", 1.0},
        {"EGP ", "EGP", "Egyptian Pound", "جنيه مصري", 1.0},
        {"جنيه", "EGP", "Egyptian Pound", "جنيه مصري", 1.0},
        {"جنيه مصري", "EGP", "Egyptian Pound", "جنيه مصري", 1.0},
        {"USD", "USD", "US Dollar", "دولار أمريكي", 30.90},
        {"EUR", "EUR", "Euro", "يورو", 33.50}
    }, {"RawCurrency", "NormalizedCurrency", "CurrencyName_EN", "CurrencyName_AR", "BaseExchangeRateToEGP"}),
    Typed = Table.TransformColumnTypes(Source, {
        {"RawCurrency", type text},
        {"NormalizedCurrency", type text},
        {"CurrencyName_EN", type text},
        {"CurrencyName_AR", type text},
        {"BaseExchangeRateToEGP", type number}
    })
in
    Typed


// ------------------------------------------------------------------------------
// QUERY: ref_status_mapping
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// QUERY: ref_governorate_mapping
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// QUERY: ref_channel_mapping
// ------------------------------------------------------------------------------
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


// ------------------------------------------------------------------------------
// QUERY: ref_payment_mapping
// ------------------------------------------------------------------------------
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
