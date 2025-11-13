import aiohttp
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

class MLPrediction(BaseModel):
    prediction: int  # 0 or 1
    confidence: float
    signal: str  # 'BUY' | 'SELL' | 'HOLD'
    timestamp: str

class MLService:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.is_available = False
        logger.info(f'ML Service initialized: {base_url}')

    async def check_health(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.base_url}/health', timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.is_available = data.get('status') == 'ok' and data.get('model_loaded', False)
                        if self.is_available:
                            logger.info('✅ ML Service is available and model is loaded')
                        else:
                            logger.warning('⚠️ ML Service is available but model is not loaded')
                        return self.is_available
                    else:
                        logger.warning(f'⚠️ ML Service health check failed with status {response.status}')
                        self.is_available = False
                        return False
        except Exception as error:
            logger.warning(f'⚠️ ML Service is not available: {error}')
            self.is_available = False
            return False

    async def get_prediction(self, market_data: Dict[str, Any]) -> Optional[MLPrediction]:
        if not self.is_available:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/predict',
                    json=market_data,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return MLPrediction(**data)
                    else:
                        logger.error(f'ML prediction failed with status {response.status}')
                        return None
        except Exception as error:
            logger.error(f'Failed to get ML prediction: {error}')
            return None

    async def get_model_info(self) -> Optional[Dict[str, Any]]:
        if not self.is_available:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.base_url}/model/info', timeout=self.timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f'Failed to get model info with status {response.status}')
                        return None
        except Exception as error:
            logger.error(f'Failed to get model info: {error}')
            return None