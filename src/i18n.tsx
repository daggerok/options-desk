import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

export type Language = 'en' | 'ru';
export const DEFAULT_LANGUAGE: Language = 'en';
export const LANGUAGES: Language[] = ['en', 'ru'];

const translations: Record<Language, Record<string, string>> = {
    en: {
        'app.brand': 'Option Desk',
        'app.title': 'Options Desk',

        'topBar.api': 'API',
        'topBar.settings': 'Settings',
        'topBar.language': 'Language',

        'language.en': 'English',
        'language.ru': 'Русский',
        'language.icon': '🌐',

        'theme.light': 'Light',
        'theme.system': 'System',
        'theme.dark': 'Dark',

        'settings.title': 'Settings',
        'settings.provider': 'Data provider',
        'settings.providerHint': 'Also available in the heading for quick access.',
        'settings.theme': 'Theme',
        'settings.themeHint': 'Also available in the heading for quick access.',
        'settings.language': 'Language',
        'settings.languageHint': 'Also available in the heading for quick access.',
        'settings.apiKey': 'API key',
        'settings.apiSecret': 'API secret',
        'settings.getKey': 'Get a free key',
        'settings.keyHint': 'Stored only in your browser (localStorage).',
        'settings.proxyBase': 'Proxy base URL',
        'settings.proxyBaseHint': 'Run bun ./scripts/yahoo-proxy.ts locally, or deploy scripts/cloudflare-worker.js.',
        'settings.proxyBasePlaceholder': 'http://localhost:8787 or https://name.you.workers.dev',
        'settings.corsProxy': 'CORS proxy',
        'settings.corsProxyHint': 'Public proxies can be flaky — switch if one fails, or use your own Worker.',
        'settings.workerUrl': 'Worker URL',
        'settings.workerUrlPlaceholder': 'https://name.you.workers.dev',

        'settings.deskColumns': 'Desk columns',
        'settings.deskColumns.calls': 'Calls',
        'settings.deskColumns.puts': 'Puts',
        'settings.deskColumns.openInterest': 'Open interest',
        'settings.deskColumns.volume': 'Volume',
        'settings.deskColumns.iv': 'IV',
        'settings.deskColumns.delta': 'Delta Δ',
        'settings.deskColumns.gamma': 'Gamma Γ',
        'settings.deskColumns.theta': 'Theta Θ',
        'settings.deskColumns.vega': 'Vega',
        'settings.deskColumns.rho': 'Rho ρ',
        'settings.deskColumns.lambda': 'Lambda λ',
        'settings.deskColumns.vanna': 'Vanna',
        'settings.deskColumns.vomma': 'Vomma',
        'settings.deskColumns.charm': 'Charm',
        'settings.deskColumns.speed': 'Speed',
        'settings.deskColumns.zomma': 'Zomma',
        'settings.deskColumns.color': 'Color',
        'settings.deskColumns.note': 'Bid / Mid / Ask and Strike stay visible. Rho is disabled by default.',

        'settings.cache': 'Cache',
        'settings.cache.records': 'Data records',
        'settings.cache.dataSize': 'Data size',
        'settings.cache.settingsSize': 'Settings size',
        'settings.cache.oldest': 'Oldest record',
        'settings.cache.newest': 'Newest record',
        'settings.cache.clearData': 'Clear data',
        'settings.cache.clearDataHint': 'Downloaded query results only',
        'settings.cache.clearSettings': 'Clear settings',
        'settings.cache.clearSettingsHint': 'Provider / theme / language / keys / proxy / columns',
        'settings.cache.clearAll': 'Clear everything',
        'settings.cache.clearAllHint': 'Data + settings (full reset)',
        'settings.cache.confirm': 'Confirm?',
        'settings.cache.confirmHelp': 'Click “Confirm?” again to proceed, or click away to cancel.',

        'setupBadge.noSetup': 'No setup',
        'setupBadge.freeKey': 'Free key',
        'setupBadge.keySet': 'Key set',
        'setupBadge.needsProxy': 'Needs proxy',

        'providerDescription.static':
            'Local static cache — same-origin data/{TICKER}.json (GitHub Action + yfinance + CBOE/BS greeks). ' +
            'No proxy, no keys. Best default on GitHub Pages. Only cached tickers are listed.',
        'providerDescription.yahoo':
            'Yahoo Finance via proxy (/api/options) — crumb/cookie handled by scripts/yahoo-proxy.ts or Cloudflare Worker. ' +
            'Lazy per-expiration. No provider greeks; client Black-Scholes fills them when IV is present.',
        'providerDescription.nasdaq':
            'NASDAQ option chain via proxy (/api/nasdaq) — full chain one call (bid/ask/last/volume/OI). ' +
            'No IV/greeks in feed (higher-order stay empty). Needs Proxy base URL.',
        'providerDescription.cboe':
            'CBOE delayed options via proxy (/api/cboe) — equities & indices, greeks/IV/OI + spot. ' +
            'Default on localhost when proxy is available. Needs Proxy base URL.',

        'onboarding.title': 'One quick step: add your free {{provider}} {{keys}}',
        'onboarding.description': '{{hint}}',
        'onboarding.getKey': 'Get a free key',
        'onboarding.save': 'Save {{keys}} & load',
        'onboarding.saved': 'Credentials already saved — just search a ticker above.',
        'onboarding.keys': 'keys',
        'onboarding.key': 'key',
        'onboarding.previewDemo': 'or get {{symbol}}’s dates now (no key needed)',
        'onboarding.previewCache': 'or switch to CACHE (AAPL static data)',

        'controls.tickerPlaceholder': 'Ticker or company (e.g. AAPL, Tesla, SPX)',
        'controls.expirations': 'Expirations',
        'controls.loading': 'Loading…',
        'controls.load': 'Load',
        'controls.loadCount': 'Load ({{count}})',
        'controls.all': 'All',
        'controls.none': 'None',
        'controls.cancel': 'Cancel',
        'controls.searching': 'Searching tickers…',

        'chain.expirations': 'expiration',
        'chain.expirationsPlural': 'expirations',
        'chain.collapseAll': 'Collapse all',
        'chain.expandAll': 'Expand all',
        'chain.calls': 'Calls',
        'chain.puts': 'Puts',
        'chain.strike': 'Strike',
        'chain.strikeSymbol': '$',
        'chain.strikes': '{{count}} strikes',

        'spot.label': 'Spot',
        'spot.estimated': '(est.)',
        'spot.delayed': '· delayed · {{provider}}',

        'loading.expirations': 'Fetching expirations…',
        'loading.chain': 'Loading chain…',

        'notice.cancelled': 'Request cancelled.',
        'notice.noOptions': '“{{symbol}}” is a valid ticker, but the latest local index marks it as (no options).',
        'notice.noContracts': 'No contracts returned for the selected expiration(s).',
        'notice.start': 'Enter a ticker and press {{expirations}} to begin.',
        'notice.select': 'Pick one or more expirations and press {{load}} to fetch the chain.',

        'error.enterTicker': 'Enter a ticker symbol.',
        'error.noContracts': 'No option contracts found for “{{symbol}}”.',
        'error.providerBulk': 'Provider misconfigured (bulk without fetchAll).',
        'error.providerLazy': 'Provider misconfigured (lazy without fetchMeta).',
        'error.friendly.networkProxy':
            'Could not reach the proxy. To fix this:\n\n' +
            '1. Clone the repo: git clone https://github.com/daggerok/options-desk.git\n' +
            '2. Install dependencies: bun install -E\n' +
            '3. Run the proxy: bun ./scripts/yahoo-proxy.ts\n' +
            '4. Set Proxy base URL in Settings to http://localhost:8787\n\n' +
            'Or deploy scripts/cloudflare-worker.js and set the Worker URL instead.\n\n' +
            'See docs/README.en.md for detailed instructions.',
        'error.friendly.networkCors':
            'Network/CORS error reaching the proxy. Try a different CORS proxy in Settings, or use CACHE (static data).',
        'error.friendly.networkGeneric':
            'Network error — could not reach the data provider. Check your connection and try again.',
        'error.friendly.unexpectedJson':
            'The provider returned an unexpected (non-JSON) response — often a proxy error page. Switch the proxy or provider in Settings.',
        'error.friendly.generic': 'Something went wrong while loading option data.',

        'retry': 'Retry',
        'expired': 'expired',
        'noOptions': '(no options)',
        'tickerFromIndex': 'Ticker from local index',
        'validTickerFromIndex': 'Valid ticker from local index',
    },
    ru: {
        'app.brand': 'Option Desk',
        'app.title': 'Options Desk',

        'topBar.api': 'API',
        'topBar.settings': 'Настройки',
        'topBar.language': 'Язык',

        'language.en': 'English',
        'language.ru': 'Русский',
        'language.icon': '🌐',

        'theme.light': 'Светлая',
        'theme.system': 'Системная',
        'theme.dark': 'Тёмная',

        'settings.title': 'Настройки',
        'settings.provider': 'Провайдер данных',
        'settings.providerHint': 'Также доступен в шапке для быстрого доступа.',
        'settings.theme': 'Тема',
        'settings.themeHint': 'Также доступна в шапке для быстрого доступа.',
        'settings.language': 'Язык',
        'settings.languageHint': 'Также доступен в шапке для быстрого доступа.',
        'settings.apiKey': 'API ключ',
        'settings.apiSecret': 'API секрет',
        'settings.getKey': 'Получить бесплатный ключ',
        'settings.keyHint': 'Хранится только в браузере (localStorage).',
        'settings.proxyBase': 'Базовый URL прокси',
        'settings.proxyBaseHint': 'Запусти bun ./scripts/yahoo-proxy.ts локально или задеплой scripts/cloudflare-worker.js.',
        'settings.proxyBasePlaceholder': 'http://localhost:8787 или https://name.you.workers.dev',
        'settings.corsProxy': 'CORS прокси',
        'settings.corsProxyHint': 'Публичные прокси могут быть нестабильны — переключайся при сбоях или используй свой Worker.',
        'settings.workerUrl': 'URL Worker',
        'settings.workerUrlPlaceholder': 'https://name.you.workers.dev',

        'settings.deskColumns': 'Колонки доски',
        'settings.deskColumns.calls': 'Calls',
        'settings.deskColumns.puts': 'Puts',
        'settings.deskColumns.openInterest': 'OI',
        'settings.deskColumns.volume': 'Объём',
        'settings.deskColumns.iv': 'IV',
        'settings.deskColumns.delta': 'Delta Δ',
        'settings.deskColumns.gamma': 'Gamma Γ',
        'settings.deskColumns.theta': 'Theta Θ',
        'settings.deskColumns.vega': 'Vega',
        'settings.deskColumns.rho': 'Rho ρ',
        'settings.deskColumns.lambda': 'Lambda λ',
        'settings.deskColumns.vanna': 'Vanna',
        'settings.deskColumns.vomma': 'Vomma',
        'settings.deskColumns.charm': 'Charm',
        'settings.deskColumns.speed': 'Speed',
        'settings.deskColumns.zomma': 'Zomma',
        'settings.deskColumns.color': 'Color',
        'settings.deskColumns.note': 'Bid / Mid / Ask и Strike всегда видны. Rho отключён по умолчанию.',

        'settings.cache': 'Кэш',
        'settings.cache.records': 'Записей данных',
        'settings.cache.dataSize': 'Размер данных',
        'settings.cache.settingsSize': 'Размер настроек',
        'settings.cache.oldest': 'Самая старая запись',
        'settings.cache.newest': 'Самая новая запись',
        'settings.cache.clearData': 'Очистить данные',
        'settings.cache.clearDataHint': 'Только загруженные результаты запросов',
        'settings.cache.clearSettings': 'Очистить настройки',
        'settings.cache.clearSettingsHint': 'Провайдер / тема / язык / ключи / прокси / колонки',
        'settings.cache.clearAll': 'Очистить всё',
        'settings.cache.clearAllHint': 'Данные + настройки (полный сброс)',
        'settings.cache.confirm': 'Подтвердить?',
        'settings.cache.confirmHelp': 'Нажми «Подтвердить?» ещё раз, чтобы продолжить, или клни вне кнопки для отмены.',

        'setupBadge.noSetup': 'Без настройки',
        'setupBadge.freeKey': 'Бесплатный ключ',
        'setupBadge.keySet': 'Ключ задан',
        'setupBadge.needsProxy': 'Нужен прокси',

        'providerDescription.static':
            'Локальный статический кэш — same-origin data/{TICKER}.json (GitHub Action + yfinance + CBOE/BS греки). ' +
            'Без прокси и ключей. Лучший default для GitHub Pages. Показываются только закэшированные тикеры.',
        'providerDescription.yahoo':
            'Yahoo Finance через прокси (/api/options) — crumb/cookie обрабатывают scripts/yahoo-proxy.ts или Cloudflare Worker. ' +
            'Lazy по expiration. Нет провайдерских греков; клиентский Black-Scholes считает их при наличии IV.',
        'providerDescription.nasdaq':
            'Цепочка NASDAQ через прокси (/api/nasdaq) — полная цепочка за один запрос (bid/ask/last/volume/OI). ' +
            'Нет IV/греков в фиде (higher-order остаются пустыми). Нужен Proxy base URL.',
        'providerDescription.cboe':
            'CBOE delayed options через прокси (/api/cboe) — акции и индексы, греки/IV/OI + spot. ' +
            'Default на localhost, если прокси доступен. Нужен Proxy base URL.',

        'onboarding.title': 'Один простой шаг: добавь бесплатный {{keys}} для {{provider}}',
        'onboarding.description': '{{hint}}',
        'onboarding.getKey': 'Получить бесплатный ключ',
        'onboarding.save': 'Сохранить {{keys}} и загрузить',
        'onboarding.saved': 'Ключи уже сохранены — просто введи тикер выше.',
        'onboarding.keys': 'ключи',
        'onboarding.key': 'ключ',
        'onboarding.previewDemo': 'или получить даты для {{symbol}} прямо сейчас (без ключа)',
        'onboarding.previewCache': 'или переключиться на CACHE (статичные данные AAPL)',

        'controls.tickerPlaceholder': 'Тикер или компания (например, AAPL, Tesla, SPX)',
        'controls.expirations': 'Экспирации',
        'controls.loading': 'Загрузка…',
        'controls.load': 'Загрузить',
        'controls.loadCount': 'Загрузить ({{count}})',
        'controls.all': 'Все',
        'controls.none': 'Нет',
        'controls.cancel': 'Отмена',
        'controls.searching': 'Ищем тикеры…',

        'chain.expirations': 'экспирация',
        'chain.expirationsPlural': 'экспираций',
        'chain.collapseAll': 'Свернуть все',
        'chain.expandAll': 'Развернуть все',
        'chain.calls': 'Calls',
        'chain.puts': 'Puts',
        'chain.strike': 'Strike',
        'chain.strikeSymbol': '$',
        'chain.strikes': '{{count}} страйков',

        'spot.label': 'Спот',
        'spot.estimated': '(оценка)',
        'spot.delayed': '· с задержкой · {{provider}}',

        'loading.expirations': 'Загружаем экспирации…',
        'loading.chain': 'Загружаем цепочку…',

        'notice.cancelled': 'Запрос отменён.',
        'notice.noOptions': '«{{symbol}}» — валидный тикер, но последний локальный индекс помечает его как (no options).',
        'notice.noContracts': 'По выбранным экспирациям не вернулось контрактов.',
        'notice.start': 'Введи тикер и нажми {{expirations}}, чтобы начать.',
        'notice.select': 'Выбери одну или несколько экспираций и нажми {{load}}, чтобы загрузить цепочку.',

        'error.enterTicker': 'Введи тикер.',
        'error.noContracts': 'Для «{{symbol}}» не найдено опционных контрактов.',
        'error.providerBulk': 'Провайдер настроен неверно (bulk без fetchAll).',
        'error.providerLazy': 'Провайдер настроен неверно (lazy без fetchMeta).',
        'error.friendly.networkProxy':
            'Не удалось достучаться до прокси. Чтобы исправить:\n\n' +
            '1. Клонируй репозиторий: git clone https://github.com/daggerok/options-desk.git\n' +
            '2. Установи зависимости: bun install -E\n' +
            '3. Запусти прокси: bun ./scripts/yahoo-proxy.ts\n' +
            '4. Укажи Proxy base URL в настройках: http://localhost:8787\n\n' +
            'Или задеплой scripts/cloudflare-worker.js и укажи URL Worker.\n\n' +
            'Подробности — в docs/README.en.md.',
        'error.friendly.networkCors':
            'Ошибка сети/CORS при обращении к прокси. Попробуй другой CORS-прокси в настройках или используй CACHE (статичные данные).',
        'error.friendly.networkGeneric':
            'Сетевая ошибка — не удалось достучаться до провайдера данных. Проверь соединение и попробуй снова.',
        'error.friendly.unexpectedJson':
            'Провайдер вернул неожиданный (не-JSON) ответ — часто это страница ошибки прокси. Переключи прокси или провайдера в настройках.',
        'error.friendly.generic': 'Что-то пошло не так при загрузке данных об опционах.',

        'retry': 'Повторить',
        'expired': 'истёк',
        'noOptions': '(no options)',
        'tickerFromIndex': 'Тикер из локального индекса',
        'validTickerFromIndex': 'Валидный тикер из локального индекса',
    },
};

export function translate(key: string, lang: Language, params?: Record<string, string | number>): string {
    const dict = translations[lang] ?? translations[DEFAULT_LANGUAGE];
    let text = dict[key] ?? translations[DEFAULT_LANGUAGE][key] ?? key;
    if (params) {
        Object.entries(params).forEach(([k, v]) => {
            text = text.split(`{{${k}}}`).join(String(v));
        });
    }
    return text;
}

export function providerDescription(providerId: string, lang: Language): string {
    return translate(`providerDescription.${providerId}`, lang);
}

interface I18nContextValue {
    lang: Language;
    t: (key: string, params?: Record<string, string | number>) => string;
    setLang: (lang: Language) => void;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

export const I18nProvider: React.FC<{ initial: Language; children: React.ReactNode }> = ({ initial, children }) => {
    const [lang, setLang] = useState<Language>(LANGUAGES.includes(initial) ? initial : DEFAULT_LANGUAGE);
    useEffect(() => {
        document.documentElement.lang = lang;
        document.documentElement.dir = 'ltr';
    }, [lang]);

    const t = useCallback(
        (key: string, params?: Record<string, string | number>) => translate(key, lang, params),
        [lang],
    );

    return <I18nContext.Provider value={{ lang, t, setLang }}>{children}</I18nContext.Provider>;
};

export function useI18n(): I18nContextValue {
    const ctx = useContext(I18nContext);
    if (!ctx) throw new Error('useI18n must be used inside I18nProvider');
    return ctx;
}
