import time
import logging

logger = logging.getLogger(__name__)


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Iniciar o cronômetro quando uma solicitação for recebida
        start_time = time.time()

        # Processar a solicitação e obter a resposta
        response = self.get_response(request)

        # Calcular o tempo necessário para processar a solicitação
        duration = time.time() - start_time

        # Registre o tempo gasto
        logger.info(f"Request to {request.path} took {duration:.2f} seconds.")

        return response
