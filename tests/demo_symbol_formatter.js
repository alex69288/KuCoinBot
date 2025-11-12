#!/usr/bin/env node

/**
 * Демонстрация форматирования торговых пар
 * Показывает различие между старым и новым форматом
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

const pairs = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 'BNB/USDT', 'LINK/USDT'];

console.log('\n' + '='.repeat(80));
console.log('🔄 СРАВНЕНИЕ: Старый формат vs Новый формат');
console.log('='.repeat(80) + '\n');

pairs.forEach((pair, index) => {
  const formatted = formatSymbol(pair);
  console.log(`${index + 1}. Пара: ${pair}`);
  console.log(`   ❌ Старо: ${pair}`);
  console.log(`   ✅ Ново: ${formatted}\n`);
});

console.log('='.repeat(80));
console.log('✨ Нововведения:');
console.log('  • Добавлены символы криптовалют (₿, Ξ, ✕, ₳, ◎, ●, ₮, Ⓒ, ⧉, ⛓)');
console.log('  • Добавлены названия криптовалют на русском (Bitcoin, Ethereum и т.д.)');
console.log('  • Полная информация в одной строке для удобства пользователя');
console.log('='.repeat(80) + '\n');
