from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.models import RawLog, NormalizedLog
from src.normalization.parser import LogParser  
from src.storage.elastic_client import es_service 
from src.detection.rule_engine import rule_engine
from datetime import datetime

router = APIRouter()

def process_log_background(normalized_data: NormalizedLog):
    """Logu analiz et ve veritabanına yaz (Arka plan görevi)"""
    
    # Stage 1: Detection
    alert = rule_engine.check_rules(normalized_data)
    
    if alert:
        print(f"\033[91m🚨 [ALERT TRIGGERED] {alert}\033[0m")
    
    # Stage 2: Storage
    doc = normalized_data.dict()
    today = datetime.utcnow().strftime("%Y.%m.%d")
    index_name = f"siem-logs-{today}"
    
    result = es_service.save_log(index_name, doc)
    
    if not alert:
        print(f"[STORAGE] ✅ Log -> {index_name} | ID: {normalized_data.id}")


@router.post("/v1/ingest", status_code=202)
async def ingest_log(log: RawLog, background_tasks: BackgroundTasks):
    try:
        normalized_log = LogParser.normalize(log)
        
        # Non-blocking
        background_tasks.add_task(process_log_background, normalized_log)
        
        return {
            "status": "accepted", 
            "log_id": normalized_log.id,
            "processed_severity": normalized_log.severity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))