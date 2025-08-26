from django.core.management.base import BaseCommand
from django.db import transaction
from markets.models import Market, Stock
from markets.utils import get_tasi_companies, get_global_markets_data
import yfinance as yf

class Command(BaseCommand):
    help = 'Populate initial market and stock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing data',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Populating DEBT Trading Platform with market data...')
        )
        
        with transaction.atomic():
            # Create Markets
            self.create_markets()
            
            # Create TASI Stocks
            self.create_tasi_stocks()
            
            # Create Global Stocks
            self.create_global_stocks()
            
        self.stdout.write(
            self.style.SUCCESS('✅ Successfully populated market data!')
        )

    def create_markets(self):
        """Create market entries"""
        markets_data = [
            {
                'name': 'Saudi Stock Exchange (TASI)',
                'code': 'TASI',
                'market_type': 'TASI',
                'country': 'Saudi Arabia',
                'currency': 'SAR',
                'timezone': 'Asia/Riyadh',
            },
            {
                'name': 'New York Stock Exchange',
                'code': 'NYSE',
                'market_type': 'NYSE',
                'country': 'United States',
                'currency': 'USD',
                'timezone': 'America/New_York',
            },
            {
                'name': 'NASDAQ',
                'code': 'NASDAQ',
                'market_type': 'NASDAQ',
                'country': 'United States',
                'currency': 'USD',
                'timezone': 'America/New_York',
            },
            {
                'name': 'London Stock Exchange',
                'code': 'LSE',
                'market_type': 'LSE',
                'country': 'United Kingdom',
                'currency': 'GBP',
                'timezone': 'Europe/London',
            },
            {
                'name': 'Cryptocurrency Markets',
                'code': 'CRYPTO',
                'market_type': 'CRYPTO',
                'country': 'Global',
                'currency': 'USD',
                'timezone': 'UTC',
            },
            {
                'name': 'Precious Metals',
                'code': 'PRECIOUS',
                'market_type': 'PRECIOUS',
                'country': 'Global',
                'currency': 'USD',
                'timezone': 'UTC',
            },
        ]
        
        for market_data in markets_data:
            market, created = Market.objects.get_or_create(
                code=market_data['code'],
                defaults=market_data
            )
            if created:
                self.stdout.write(f"  ✅ Created market: {market.name}")
            else:
                self.stdout.write(f"  ⚡ Market exists: {market.name}")

    def create_tasi_stocks(self):
        """Create TASI stocks"""
        tasi_market = Market.objects.get(code='TASI')
        tasi_companies = get_tasi_companies()
        
        self.stdout.write("📊 Creating TASI stocks...")
        
        for company in tasi_companies:
            try:
                # Try to get additional info from yfinance
                ticker = yf.Ticker(company['symbol'])
                info = ticker.info
                
                stock_data = {
                    'market': tasi_market,
                    'symbol': company['symbol'],
                    'name': info.get('longName', company['name']),
                    'sector': info.get('sector', company.get('sector', '')),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap'),
                    'is_sharia_compliant': True,  # Assume TASI stocks are Sharia compliant
                }
                
                stock, created = Stock.objects.get_or_create(
                    market=tasi_market,
                    symbol=company['symbol'],
                    defaults=stock_data
                )
                
                if created:
                    self.stdout.write(f"    ✅ Created TASI stock: {stock.name} ({stock.symbol})")
                else:
                    self.stdout.write(f"    ⚡ TASI stock exists: {stock.name} ({stock.symbol})")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"    ⚠️  Failed to create {company['symbol']}: {str(e)}")
                )

    def create_global_stocks(self):
        """Create global market stocks"""
        global_data = get_global_markets_data()
        
        # US Stocks
        self.create_stocks_for_market('NASDAQ', global_data['USA']['stocks'])
        
        # Crypto
        self.create_crypto_stocks(global_data['CRYPTO']['major'] + global_data['CRYPTO']['altcoins'])
        
        # Precious Metals
        self.create_precious_metals_stocks(global_data['PRECIOUS_METALS']['futures'])

    def create_stocks_for_market(self, market_code, symbols):
        """Create stocks for a specific market"""
        try:
            market = Market.objects.get(code=market_code)
            self.stdout.write(f"📈 Creating {market_code} stocks...")
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    stock_data = {
                        'market': market,
                        'symbol': symbol,
                        'name': info.get('longName', info.get('shortName', symbol)),
                        'sector': info.get('sector', ''),
                        'industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap'),
                    }
                    
                    stock, created = Stock.objects.get_or_create(
                        market=market,
                        symbol=symbol,
                        defaults=stock_data
                    )
                    
                    if created:
                        self.stdout.write(f"    ✅ Created {market_code} stock: {stock.name} ({stock.symbol})")
                    else:
                        self.stdout.write(f"    ⚡ {market_code} stock exists: {stock.name} ({stock.symbol})")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Failed to create {symbol}: {str(e)}")
                    )
                    
        except Market.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Market {market_code} not found")
            )

    def create_crypto_stocks(self, symbols):
        """Create cryptocurrency entries"""
        try:
            crypto_market = Market.objects.get(code='CRYPTO')
            self.stdout.write("💰 Creating crypto assets...")
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    stock_data = {
                        'market': crypto_market,
                        'symbol': symbol,
                        'name': info.get('longName', info.get('shortName', symbol)),
                        'sector': 'Cryptocurrency',
                        'industry': 'Digital Currency',
                        'market_cap': info.get('marketCap'),
                    }
                    
                    stock, created = Stock.objects.get_or_create(
                        market=crypto_market,
                        symbol=symbol,
                        defaults=stock_data
                    )
                    
                    if created:
                        self.stdout.write(f"    ✅ Created crypto: {stock.name} ({stock.symbol})")
                    else:
                        self.stdout.write(f"    ⚡ Crypto exists: {stock.name} ({stock.symbol})")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Failed to create {symbol}: {str(e)}")
                    )
                    
        except Market.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Crypto market not found")
            )

    def create_precious_metals_stocks(self, symbols):
        """Create precious metals entries"""
        try:
            precious_market = Market.objects.get(code='PRECIOUS')
            self.stdout.write("🥇 Creating precious metals...")
            
            metal_names = {
                'GC=F': 'Gold Futures',
                'SI=F': 'Silver Futures',
                'PL=F': 'Platinum Futures',
                'PA=F': 'Palladium Futures',
            }
            
            for symbol in symbols:
                try:
                    stock_data = {
                        'market': precious_market,
                        'symbol': symbol,
                        'name': metal_names.get(symbol, symbol),
                        'sector': 'Precious Metals',
                        'industry': 'Commodities',
                    }
                    
                    stock, created = Stock.objects.get_or_create(
                        market=precious_market,
                        symbol=symbol,
                        defaults=stock_data
                    )
                    
                    if created:
                        self.stdout.write(f"    ✅ Created precious metal: {stock.name} ({stock.symbol})")
                    else:
                        self.stdout.write(f"    ⚡ Precious metal exists: {stock.name} ({stock.symbol})")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"    ⚠️  Failed to create {symbol}: {str(e)}")
                    )
                    
        except Market.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Precious metals market not found")
            )