// Telegram Web App API
const tg = window.Telegram.WebApp;

// Инициализация Web App
tg.ready();
tg.expand();

// Состояние приложения
let appState = {
    status: 'disconnected',
    data: null
};

// Элементы DOM
const elements = {
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    statusDot: document.querySelector('.status-dot'),
    currentPair: document.getElementById('currentPair'),
    currentPrice: document.getElementById('currentPrice'),
    positionStatus: document.getElementById('positionStatus'),
    strategy: document.getElementById('strategy'),
    balanceUSDT: document.getElementById('balanceUSDT'),
    balanceBTC: document.getElementById('balanceBTC'),
    totalTrades: document.getElementById('totalTrades'),
    winRate: document.getElementById('winRate'),
    totalProfit: document.getElementById('totalProfit'),
    toggleTrading: document.getElementById('toggleTrading'),
    tradingStatus: document.getElementById('tradingStatus'),
    refreshData: document.getElementById('refreshData'),
    openSettings: document.getElementById('openSettings'),
    dashboard: document.getElementById('dashboard'),
    settings: document.getElementById('settings'),
    backToDashboard: document.getElementById('backToDashboard'),
    saveSettings: document.getElementById('saveSettings')
};

// Инициализация
function init() {
    // Настройка кнопок
    setupButtons();
    
    // Загрузка данных
    loadData();
    
    // Автообновление каждые 30 секунд
    setInterval(loadData, 30000);
    
    // Обновление статуса
    updateStatus('connected');
}

// Настройка обработчиков кнопок
function setupButtons() {
    elements.toggleTrading.addEventListener('click', () => {
        toggleTrading();
    });
    
    elements.refreshData.addEventListener('click', () => {
        loadData();
        tg.HapticFeedback.notificationOccurred('success');
    });
    
    elements.openSettings.addEventListener('click', () => {
        showSettings();
    });
    
    elements.backToDashboard.addEventListener('click', () => {
        showDashboard();
    });
    
    elements.saveSettings.addEventListener('click', () => {
        saveSettings();
    });
}

// Загрузка данных (заглушка - нужно подключить к API бота)
async function loadData() {
    updateStatus('loading');
    
    try {
        // Здесь должен быть запрос к API вашего бота
        // Пример: const response = await fetch('http://your-bot-api:8080/api/status');
        // const data = await response.json();
        
        // Заглушка для демонстрации
        const mockData = {
            pair: 'BTC/USDT',
            price: 43250.50,
            position: 'Ожидание',
            strategy: 'EMA + ML',
            balance: {
                usdt: 1000.00,
                btc: 0.023
            },
            stats: {
                trades: 15,
                winRate: 73.3,
                profit: 5.2
            },
            trading: false
        };
        
        updateUI(mockData);
        updateStatus('connected');
        
        // Реальный код:
        // const data = await fetchBotData();
        // updateUI(data);
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        updateStatus('error');
        tg.showAlert('Ошибка загрузки данных');
    }
}

// Обновление UI
function updateUI(data) {
    elements.currentPair.textContent = data.pair || '-';
    elements.currentPrice.textContent = data.price ? `$${data.price.toFixed(2)}` : '-';
    elements.positionStatus.textContent = data.position || '-';
    elements.strategy.textContent = data.strategy || '-';
    elements.balanceUSDT.textContent = data.balance?.usdt ? `$${data.balance.usdt.toFixed(2)}` : '-';
    elements.balanceBTC.textContent = data.balance?.btc ? `${data.balance.btc.toFixed(6)} BTC` : '-';
    elements.totalTrades.textContent = data.stats?.trades || 0;
    elements.winRate.textContent = data.stats?.winRate ? `${data.stats.winRate}%` : '0%';
    elements.totalProfit.textContent = data.stats?.profit ? `${data.stats.profit}%` : '0%';
    
    if (data.trading !== undefined) {
        elements.tradingStatus.textContent = data.trading ? 'ВКЛ' : 'ВЫКЛ';
        elements.toggleTrading.style.opacity = data.trading ? '1' : '0.7';
    }
}

// Обновление статуса подключения
function updateStatus(status) {
    appState.status = status;
    
    const statusMap = {
        'connected': { text: 'Подключено', class: 'connected' },
        'loading': { text: 'Загрузка...', class: '' },
        'error': { text: 'Ошибка', class: '' },
        'disconnected': { text: 'Отключено', class: '' }
    };
    
    const statusInfo = statusMap[status] || statusMap.disconnected;
    elements.statusText.textContent = statusInfo.text;
    elements.statusDot.className = 'status-dot ' + statusInfo.class;
}

// Переключение торговли
async function toggleTrading() {
    tg.HapticFeedback.impactOccurred('medium');
    
    // Здесь должен быть запрос к API бота
    // await fetch('http://your-bot-api:8080/api/toggle-trading', { method: 'POST' });
    
    const currentStatus = elements.tradingStatus.textContent;
    const newStatus = currentStatus === 'ВКЛ' ? 'ВЫКЛ' : 'ВКЛ';
    elements.tradingStatus.textContent = newStatus;
    
    tg.showAlert(`Торговля ${newStatus === 'ВКЛ' ? 'включена' : 'выключена'}`);
}

// Показать настройки
function showSettings() {
    elements.dashboard.style.display = 'none';
    elements.settings.style.display = 'block';
    tg.HapticFeedback.impactOccurred('light');
}

// Показать дашборд
function showDashboard() {
    elements.settings.style.display = 'none';
    elements.dashboard.style.display = 'block';
    tg.HapticFeedback.impactOccurred('light');
}

// Сохранение настроек
async function saveSettings() {
    tg.HapticFeedback.impactOccurred('medium');
    
    const settings = {
        pair: elements.tradingPair.value,
        strategy: elements.strategySelect.value,
        tradeAmount: parseFloat(elements.tradeAmount.value),
        takeProfit: parseFloat(elements.takeProfit.value)
    };
    
    // Здесь должен быть запрос к API бота
    // await fetch('http://your-bot-api:8080/api/settings', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(settings)
    // });
    
    tg.showAlert('Настройки сохранены');
    showDashboard();
    loadData();
}

// Запуск приложения
init();

