"""REST API server for analyzer."""
import json
import logging
import os
from logging.config import dictConfig
from pathlib import Path
from typing import Optional, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_analyzer.analyzer_request import AnalyzerRequest

DEFAULT_PORT = "3000"

LOGGING_CONF_FILE = "logging.json"

WELCOME_MESSAGE = r"""
 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)
"""


class Server:
    """HTTP Server for calling Presidio Analyzer."""

    def __init__(self):
        with open(Path(Path(__file__).parent, LOGGING_CONF_FILE)) as logging_file:
            logging_config = json.load(logging_file)
            dictConfig(logging_config)

        self.logger = logging.getLogger("presidio-analyzer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = FastAPI()
        self.logger.info("Starting analyzer engine")
        self.engine = AnalyzerEngine()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.get("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Analyzer service is up"

        @self.app.post("/analyze")
        def analyze(req_data: AnalyzerRequest) -> Tuple[str, int]:
            """Execute the analyzer function."""
            # Parse the request params
            try:
                recognizer_result_list = self.engine.analyze(
                    text=req_data.text,
                    language=req_data.language,
                    correlation_id=req_data.correlation_id,
                    score_threshold=req_data.score_threshold,
                    entities=req_data.entities,
                    return_decision_process=req_data.return_decision_process,
                    ad_hoc_recognizers=req_data.ad_hoc_recognizers,
                    context=req_data.context,
                )

                return PlainTextResponse(content=
                    json.dumps(
                        recognizer_result_list,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    ),
                    media_type='application/json'
                )
            except TypeError as te:
                error_msg = (
                    f"Failed to parse /analyze request "
                    f"for AnalyzerEngine.analyze(). {te.args[0]}"
                )
                self.logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)

            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                raise HTTPException(status_code=500, detail=e.args[0])

        @self.app.get("/recognizers")
        def recognizers(language: str) -> Tuple[str, int]:
            """Return a list of supported recognizers."""
            try:
                recognizers_list = self.engine.get_recognizers(language)
                names = [o.name for o in recognizers_list]
                return names
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.get_recognizers(). {e}"
                )
                raise HTTPException(status_code=500, detail=e.args[0])

        @self.app.get("/supportedentities")
        def supported_entities(language: Optional[str] = None) -> Tuple[str, int]:
            """Return a list of supported entities."""
            try:
                entities_list = self.engine.get_supported_entities(language)
                return PlainTextResponse(content=
                    json.dumps(
                        entities_list,
                        sort_keys=True,
                    ),
                    media_type='application/json'
            )
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.supported_entities(). {e}"
                )
                raise HTTPException(status_code=500, detail=e.args[0])


server = Server()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    uvicorn.run(
        "app:server.app",
        host="0.0.0.0",
        port=port,
        # ssl_keyfile="./localhost+4-key.pem",
        # ssl_certfile="./localhost+4.pem",
        reload=False
    )
