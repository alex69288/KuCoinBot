#!/usr/bin/env node

/**
 * Тест функции форматирования символов криптовалют
 * Проверяет, что символы выводятся в формате: ₿ BTC/USDT (Bitcoin)
 */

const cryptoData = {
    'BTC': { emoji: '₿', name: 'Bitcoin' },
    'ETH': { emoji: 'Ξ', name: 'Ethereum' },
    'XRP': { emoji: '✕', name: 'Ripple' },
    'ADA': { emoji: '₳', name: 'Cardano' },
    'SOL': { emoji: '◎', name: 'Solana' },
    'DOT': { emoji: '●', name: 'Polkadot' },
    'USDT': { emoji: '₮', name: 'Tether' },
    'USDC': { emoji: 'Ⓒ', name: 'USD Coin' },
    'BNB': { emoji: '⧉', name: 'Binance Coin' },
    'LINK': { emoji: '⛓', name: 'Chainlink' }
};

function formatSymbol(symbol) {
    if (!symbol) return symbol;
    
    const parts = symbol.split('/');
    if (parts.length !== 2) return symbol;
    
    const [baseCrypto, quoteCrypto] = parts;
    const baseData = cryptoData[baseCrypto];
    
    if (baseData) {
        return `${baseData.emoji} ${symbol} (${baseData.name})`;
    }
    
    return symbol;
}

// Тестовые случаи
const testCases = [
    { input: 'BTC/USDT', expected: '₿ BTC/USDT (Bitcoin)' },
    { input: 'ETH/USDT', expected: 'Ξ ETH/USDT (Ethereum)' },
    { input: 'XRP/USDT', expected: '✕ XRP/USDT (Ripple)' },
    { input: 'ADA/USDT', expected: '₳ ADA/USDT (Cardano)' },
    { input: 'SOL/USDT', expected: '◎ SOL/USDT (Solana)' },
    { input: 'UNKNOWN/USDT', expected: 'UNKNOWN/USDT' },
    { input: '', expected: '' },
];

console.log('\n🧪 Тестирование функции formatSymbol\n');
console.log('='.repeat(80));

let passCount = 0;
let failCount = 0;

testCases.forEach((testCase, index) => {
    const result = formatSymbol(testCase.input);
    const passed = result === testCase.expected;
    
    if (passed) {
        passCount++;
        console.log(`\n✅ Тест ${index + 1}: PASSED`);
    } else {
        failCount++;
        console.log(`\n❌ Тест ${index + 1}: FAILED`);
    }
    
    console.log(`   Вход:      "${testCase.input}"`);
    console.log(`   Ожидалось: "${testCase.expected}"`);
    console.log(`   Получено:  "${result}"`);
});

console.log('\n' + '='.repeat(80));
console.log(`\n📊 Результаты: ${passCount} пройдено, ${failCount} не пройдено из ${passCount + failCount}\n`);

if (failCount === 0) {
    console.log('✅ Все тесты пройдены успешно!\n');
    process.exit(0);
} else {
    console.log('❌ Некоторые тесты не пройдены!\n');
    process.exit(1);
}
