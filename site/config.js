// ============================================================
//  САЙТ БАПТАУЛАРЫ — барлық деректерді осы жерден өзгертіңіз
//  НАСТРОЙКИ САЙТА — меняйте все данные здесь
// ============================================================

window.SITE = {
  brand: "FitLine KZ",                 // Бренд атауы
  phone: "+7 700 000 00 00",           // Көрсетілетін телефон
  whatsapp: "77000000000",             // WhatsApp нөмірі (тек цифрлар, + белгісіз)
  instagram: "https://instagram.com/", // Instagram сілтемесі
  email: "info@example.kz",
  address: {
    ru: "г. Алматы, пр. Абая, 1 (пример адреса)",
    kz: "Алматы қ., Абай даңғ., 1 (мекенжай мысалы)"
  },
  hours: {
    ru: "Ежедневно 10:00–20:00",
    kz: "Күн сайын 10:00–20:00"
  },
  currency: "₸"
};

// Санаттар / Категории
window.CATEGORIES = [
  { id: "treadmill", icon: "treadmill", ru: "Беговые дорожки", kz: "Жүгіру жолдары" },
  { id: "bike",      icon: "bike",      ru: "Велотренажёры",   kz: "Велотренажерлер" },
  { id: "elliptical",icon: "elliptical",ru: "Эллипсоиды",      kz: "Эллипс тренажерлер" },
  { id: "strength",  icon: "strength",  ru: "Силовое оборудование", kz: "Күш жабдықтары" },
  { id: "accessory", icon: "accessory", ru: "Аксессуары",      kz: "Аксессуарлар" }
];

// Тауарлар / Товары  (price, oldPrice — теңгемен; oldPrice: null болса, жеңілдік көрсетілмейді)
window.PRODUCTS = [
  { id: 1, cat: "treadmill", price: 289000, oldPrice: 349000, badge: "hit",
    ru: { name: "Беговая дорожка Runner 300", specs: ["До 120 кг", "1–14 км/ч", "Складная"] },
    kz: { name: "Жүгіру жолы Runner 300",     specs: ["120 кг дейін", "1–14 км/сағ", "Жиналмалы"] } },
  { id: 2, cat: "treadmill", price: 459000, oldPrice: 529000, badge: "sale",
    ru: { name: "Беговая дорожка Runner 500 Pro", specs: ["До 150 кг", "1–18 км/ч", "Наклон 15%"] },
    kz: { name: "Жүгіру жолы Runner 500 Pro",     specs: ["150 кг дейін", "1–18 км/сағ", "Еңіс 15%"] } },
  { id: 3, cat: "treadmill", price: 189000, oldPrice: null, badge: "new",
    ru: { name: "Беговая дорожка Walk Slim", specs: ["До 110 кг", "1–8 км/ч", "Под диван"] },
    kz: { name: "Жүгіру жолы Walk Slim",     specs: ["110 кг дейін", "1–8 км/сағ", "Диван астына сыяды"] } },
  { id: 4, cat: "bike", price: 139000, oldPrice: 169000, badge: "sale",
    ru: { name: "Велотренажёр Cycle 200", specs: ["До 120 кг", "8 уровней", "Магнитный"] },
    kz: { name: "Велотренажер Cycle 200", specs: ["120 кг дейін", "8 деңгей", "Магниттік"] } },
  { id: 5, cat: "bike", price: 219000, oldPrice: null, badge: "hit",
    ru: { name: "Спин-байк Sprint X", specs: ["До 130 кг", "Маховик 18 кг", "Bluetooth"] },
    kz: { name: "Спин-байк Sprint X", specs: ["130 кг дейін", "Маховик 18 кг", "Bluetooth"] } },
  { id: 6, cat: "elliptical", price: 249000, oldPrice: 299000, badge: "sale",
    ru: { name: "Эллипсоид Orbit 400", specs: ["До 130 кг", "16 уровней", "Шаг 40 см"] },
    kz: { name: "Эллипс тренажер Orbit 400", specs: ["130 кг дейін", "16 деңгей", "Қадам 40 см"] } },
  { id: 7, cat: "strength", price: 329000, oldPrice: null, badge: null,
    ru: { name: "Силовая станция Home Gym", specs: ["Стек 70 кг", "20+ упражнений", "Компактная"] },
    kz: { name: "Күш станциясы Home Gym",   specs: ["Стек 70 кг", "20+ жаттығу", "Ықшам"] } },
  { id: 8, cat: "strength", price: 79000, oldPrice: 95000, badge: "sale",
    ru: { name: "Скамья регулируемая Bench 2", specs: ["До 250 кг", "7 положений", "Сталь"] },
    kz: { name: "Реттелетін орындық Bench 2",  specs: ["250 кг дейін", "7 қалып", "Болат"] } },
  { id: 9, cat: "accessory", price: 59000, oldPrice: null, badge: "new",
    ru: { name: "Гантели наборные 2×20 кг", specs: ["Хром", "Быстрая смена", "Кейс"] },
    kz: { name: "Жиналмалы гантельдер 2×20 кг", specs: ["Хром", "Тез ауыстыру", "Кейс"] } },
  { id: 10, cat: "accessory", price: 9900, oldPrice: 12900, badge: "sale",
    ru: { name: "Коврик для тренажёра", specs: ["200×100 см", "6 мм", "Защита пола"] },
    kz: { name: "Тренажер астына төсеніш", specs: ["200×100 см", "6 мм", "Еденді қорғайды"] } }
];
